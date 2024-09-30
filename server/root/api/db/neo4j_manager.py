import os
from neo4j import AsyncGraphDatabase
from dotenv import load_dotenv
from quart import g
import logging


class AsyncSessionManager:

    def __init__(self):
        self.logger = logging.getLogger('quart_app.db.neo4j_manager')
        if not hasattr(self, "_initialized"):
            self.logger.debug("::__init__:: Initializing AsyncSessionManager.")
            load_dotenv()
            self._uri = os.getenv('NEO4J_URI')
            self._user = os.getenv('NEO4J_USER')
            self._password = os.getenv('NEO4J_PASSWORD')
            missing_configs = [var for var in ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD'] if not os.getenv(var)]
            if missing_configs:
                self.logger.critical(f"::__init__:: Missing connection details in .env file: {', '.join(missing_configs)}")
                raise EnvironmentError(f"Missing connection details in .env file: {', '.join(missing_configs)}")

            try:
                self._driver = AsyncGraphDatabase.driver(
                    self._uri,
                    auth=(self._user, self._password),
                    max_connection_pool_size=50
                )
                self.logger.info("::__init__:: Neo4j driver successfully created.")
            except Exception as e:
                self.logger.critical(f"::__init__:: Unexpected error occurred while initializing Neo4j driver: {e}")
            self._initialized = True

    async def get_session(self):
        self.logger.debug("::get_session:: Attempting to obtain Neo4j session.")
        try:
            if not hasattr(g, 'neo4j_session'):
                self.logger.debug("::get_session:: No existing Neo4j session found, creating a new session.")
                g.neo4j_session = self._create_session()
            else:
                self.logger.debug("::get_session:: Reusing existing Neo4j session.")
            return g.neo4j_session
        except Exception as e:
            self.logger.error(f"::get_session:: Error occurred while getting Neo4j session: {e}")

    def _create_session(self):
        self.logger.info("::_create_session:: Creating a new Neo4j session.")
        try:
            session = self._driver.session()
            self.logger.debug("::_create_session:: Neo4j session created successfully.")
            return session
        except Exception as e:
            self.logger.error(f"::_create_session:: Error occurred while creating Neo4j session: {e}")

    async def close(self):
        self.logger.debug("::close:: Attempting to close Neo4j session and driver.")
        try:
            await self._close_session()
            await self._driver.close()
            self.logger.info("::close:: Neo4j driver successfully closed.")
        except Exception as e:
            self.logger.critical(f"::close:: Error occurred while closing Neo4j driver: {e}")

    async def _close_session(self):
        self.logger.debug("::_close_session:: Attempting to close the current Neo4j session.")
        try:
            if hasattr(g, 'neo4j_session'):
                await g.neo4j_session.close()
                del g.neo4j_session
                self.logger.info("::_close_session:: Neo4j session successfully closed.")
            else:
                self.logger.debug("::_close_session:: No active Neo4j session found to close.")
        except Exception as e:
            self.logger.error(f"::_close_session:: Error occurred while closing Neo4j session: {e}")

    async def execute_query(self, query, parameters=None):
        self.logger.debug(f"::execute_query:: Executing query: {query} | Parameters: {parameters}")
        try:
            session = await self.get_session()
            self.logger.debug("::execute_query:: Session obtained successfully.")
            tx = await session.begin_transaction()
            self.logger.debug("::execute_query:: Transaction started successfully.")
            async with tx:
                result = await tx.run(query, parameters or {})
                self.logger.debug("::execute_query:: Query executed successfully.")
                records = [record.data() async for record in result]
                self.logger.info(f"::execute_query:: Query returned {len(records)} records.")
                return records
        except Exception as e:
            self.logger.critical(f"::execute_query:: An unexpected error occurred: {e}")
