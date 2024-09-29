import os
from neo4j import AsyncGraphDatabase
from dotenv import load_dotenv
from neo4j import AsyncSession
from quart import g, abort
import asyncio
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger('quart_app.db.neo4j_manager')


class AsyncSessionManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures that only one instance of AsyncSessionManager exists (Singleton pattern).

        :return: The singleton instance of AsyncSessionManager.
        """
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            logger.debug("Creating a new AsyncSessionManager instance.")
        return cls._instance

    def __init__(self):
        """
        Initializes the AsyncSessionManager with Neo4j database connection details from the .env file.

        :raises EnvironmentError: If any of the required Neo4j connection details are missing in the .env file.
        :raises HTTPException: If the Neo4j driver fails to initialize.
        """
        if not hasattr(self, "initialized"):
            logger.debug("Initializing AsyncSessionManager.")
            load_dotenv()
            self.uri = os.getenv('NEO4J_URI')
            self.user = os.getenv('NEO4J_USER')
            self.password = os.getenv('NEO4J_PASSWORD')

            missing_configs = [var for var in ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD'] if not os.getenv(var)]
            if missing_configs:
                logger.error(f"Missing connection details in .env file: {', '.join(missing_configs)}")
                raise EnvironmentError(f"Missing connection details in .env file: {', '.join(missing_configs)}")

            try:
                # Create the asynchronous Neo4j driver
                self.driver = AsyncGraphDatabase.driver(
                    self.uri,
                    auth=(self.user, self.password),
                    max_connection_pool_size=1000
                )
                logger.info("Neo4j driver successfully created.")
            except Exception as e:
                logger.error(f"Error occurred while creating Neo4j driver: {e}", exc_info=True)
                abort(500, description="Failed to establish database connection.")

            self.initialized = True

    async def get_session(self) -> AsyncSession:
        """
        Asynchronously retrieves a Neo4j session. If a session is not already open, it creates a new one.

        :return: The active Neo4j session.
        :rtype: AsyncSession

        :raises HTTPException: If unable to retrieve or create a Neo4j session.
        """
        try:
            if not hasattr(g, 'neo4j_session'):
                logger.debug("No existing Neo4j session found, creating a new session.")
                g.neo4j_session = await self.create_session()
            else:
                logger.debug("Reusing existing Neo4j session.")
            return g.neo4j_session
        except Exception as e:
            logger.error(f"Error occurred while getting Neo4j session: {e}", exc_info=True)
            abort(500, description="Failed to retrieve database session.")

    async def create_session(self) -> AsyncSession:
        """
        Asynchronously creates a new Neo4j session.

        :return: The newly created Neo4j session.
        :rtype: AsyncSession

        :raises HTTPException: If unable to create a Neo4j session.
        """
        try:
            logger.info("Creating a new Neo4j session.")
            return self.driver.session()
        except Exception as e:
            logger.error(f"Error occurred while creating Neo4j session: {e}", exc_info=True)
            abort(500, description="Failed to create Neo4j session.")

    async def close(self):
        """
        Asynchronously closes the current Neo4j session and the driver when they are no longer needed.

        :raises HTTPException: If unable to close the Neo4j session or driver.
        """
        try:
            logger.debug("Closing Neo4j session and driver.")
            await self.close_session()
            await self.driver.close()
            logger.info("Neo4j driver successfully closed.")
        except Exception as e:
            logger.error(f"Error occurred while closing Neo4j driver: {e}", exc_info=True)
            abort(500, description="Failed to close database connection.")

    async def close_session(self):
        """
        Asynchronously closes the current Neo4j session if it's active.

        :raises HTTPException: If unable to close the Neo4j session.
        """
        try:
            if hasattr(g, 'neo4j_session'):
                logger.debug("Closing the current Neo4j session.")
                close_method = g.neo4j_session.close
                if asyncio.iscoroutinefunction(close_method):
                    await close_method()
                else:
                    close_method()
                del g.neo4j_session
                logger.info("Neo4j session successfully closed.")
            else:
                logger.debug("No active Neo4j session found to close.")
        except Exception as e:
            logger.error(f"Error occurred while closing Neo4j session: {e}", exc_info=True)
            abort(500, description="Failed to close Neo4j session.")

    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Asynchronously executes a Cypher query in the Neo4j database.

        :param query: The Cypher query to execute.
        :type query: str
        :param parameters: A dictionary of parameters for the query, optional.
        :type parameters: Dict[str, Any], optional
        :return: A list of results from the query.
        :rtype: List[Dict[str, Any]]

        :raises HTTPException: If the query execution fails or an unexpected error occurs.
        """
        logger.debug(f"Executing query: {query} | Parameters: {parameters}")
        try:
            session = await self.get_session()
            result = await session.run(query, parameters or {})
            logger.debug("Query executed successfully.")
            return [record.data() async for record in result]
        except Exception as e:
            logger.error(f"Neo4j query failed: {e}", exc_info=True)
            abort(500, description="Database query execution failed.")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            abort(500, description="An unexpected server error occurred.")
