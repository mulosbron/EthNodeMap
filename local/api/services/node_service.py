import logging
from utils.node_helper import NodeHelper
from db.neo4j_manager import AsyncSessionManager

logger = logging.getLogger('quart_app.services.node_service')


class NodeService:
    def __init__(self):
        """Initializes the NodeService class, setting up the database manager and helper."""
        self.db_manager = AsyncSessionManager()
        self.helper = NodeHelper()

    async def fetch_nodes(self):
        """
        Fetches all nodes from the database.

        :return: A list of dictionaries representing nodes with details such as NodeId, Host, Port, etc.
        :raises: Exception if there is an error during database execution.
        """
        logger.info("Fetching all nodes...")
        query = """
        MATCH (n:Node)
        RETURN n.id AS NodeId, n.host AS Host, n.port AS Port, n.client AS Client, n.os AS OS, n.status AS Status,
        n.latitude AS Latitude, n.longitude AS Longitude, n.isp AS ISP, n.country_name AS Country, n.created_at AS CreatedAt
        """
        try:
            result = await self.db_manager.execute_query(query)
            logger.info(f"Fetched {len(result)} nodes.")
            return result
        except Exception as e:
            logger.error("Error while fetching nodes", exc_info=True)
            raise e

    async def fetch_os_types(self):
        """
        Fetches distinct operating system types used by the nodes.

        :return: A list of distinct OS types.
        :raises: Exception if there is an error during database execution.
        """
        logger.info("Fetching OS types...")
        query = "MATCH (n:Node) RETURN DISTINCT n.os AS OS"
        try:
            records = await self.db_manager.execute_query(query)
            os_types = [record["OS"] for record in records]
            logger.info(f"Fetched {len(os_types)} OS types.")
            return os_types
        except Exception as e:
            logger.error("Error while fetching OS types", exc_info=True)
            raise e

    async def fetch_clients(self):
        """
        Fetches distinct client types used by the nodes.

        :return: A list of distinct client types.
        :raises: Exception if there is an error during database execution.
        """
        logger.info("Fetching client types...")
        query = """
        MATCH (n:Node)
        RETURN DISTINCT n.client AS Client
        """
        try:
            records = await self.db_manager.execute_query(query)
            clients = [record["Client"] for record in records]
            logger.info(f"Fetched {len(clients)} client types.")
            return clients
        except Exception as e:
            logger.error("Error while fetching client types", exc_info=True)
            raise e

    async def fetch_countries(self):
        """
        Fetches distinct countries where the nodes are located.

        :return: A list of distinct countries.
        :raises: Exception if there is an error during database execution.
        """
        logger.info("Fetching countries...")
        query = """
        MATCH (n:Node)
        RETURN DISTINCT n.country_name AS Country
        """
        try:
            records = await self.db_manager.execute_query(query)
            countries = [record["Country"] for record in records]
            logger.info(f"Fetched {len(countries)} countries.")
            return countries
        except Exception as e:
            logger.error("Error while fetching countries", exc_info=True)
            raise e

    async def fetch_isps(self):
        """
        Fetches distinct Internet Service Providers (ISPs) associated with the nodes.

        :return: A list of distinct ISPs.
        :raises: Exception if there is an error during database execution.
        """
        logger.info("Fetching ISPs...")
        query = """
        MATCH (n:Node)
        RETURN DISTINCT n.isp AS ISP
        """
        try:
            records = await self.db_manager.execute_query(query)
            isps = [record["ISP"] for record in records]
            logger.info(f"Fetched {len(isps)} ISPs.")
            return isps
        except Exception as e:
            logger.error("Error while fetching ISPs", exc_info=True)
            raise e

    async def fetch_node_ids(self):
        """
        Fetches distinct node IDs from the database.

        :return: A list of distinct node IDs.
        :raises: Exception if there is an error during database execution.
        """
        logger.info("Fetching node IDs...")
        query = """
        MATCH (n:Node)
        RETURN DISTINCT n.id AS NodeID
        """
        try:
            records = await self.db_manager.execute_query(query)
            node_ids = [record["NodeID"] for record in records]
            logger.info(f"Fetched {len(node_ids)} node IDs.")
            return node_ids
        except Exception as e:
            logger.error("Error while fetching node IDs", exc_info=True)
            raise e

    async def fetch_node_count(self):
        """
        Fetches the total number of distinct nodes in the database.

        :return: The total number of nodes as an integer.
        :raises: Exception if there is an error during database execution.
        """
        logger.info("Fetching node count...")
        query = """
        MATCH (n:Node)
        RETURN COUNT(DISTINCT n.id) AS NumberOfNodes
        """
        try:
            result = await self.db_manager.execute_query(query)
            node_count = result[0]["NumberOfNodes"] if result else 0
            logger.info(f"Node count: {node_count}")
            return node_count
        except Exception as e:
            logger.error("Error while fetching node count", exc_info=True)
            raise e

    async def fetch_node_details(self, node_id):
        """
        Fetches detailed information about a specific node by its ID.

        :param node_id: The unique identifier of the node.
        :return: A dictionary containing the node details or None if the node is not found.
        :raises: Exception if there is an error during database execution.
        """
        logger.info(f"Fetching details for node ID: {node_id}")
        query = """
        MATCH (n:Node {id: $node_id})
        RETURN n.id AS NodeId, n.host AS Host, n.port AS Port, n.client AS Client, n.os AS OS, n.status AS Status,
        n.latitude AS Latitude, n.longitude AS Longitude, n.isp AS ISP, n.country_name AS Country, n.created_at AS CreatedAt
        """
        try:
            result = await self.db_manager.execute_query(query, {"node_id": node_id})
            if result:
                logger.info(f"Details for node ID {node_id} fetched successfully.")
            else:
                logger.warning(f"No details found for node ID {node_id}.")
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error while fetching details for node ID {node_id}", exc_info=True)
            raise e

    async def fetch_latest_nodes(self, limit):
        """
        Fetches the latest nodes up to a specified limit.

        :param limit: The maximum number of latest nodes to retrieve.
        :return: A list of the latest nodes.
        :raises: Exception if there is an error during database execution.
        """
        logger.info(f"Fetching latest {limit} nodes...")
        query = """
        MATCH (n:Node)
        RETURN n.id AS NodeId, n.host AS Host, n.port AS Port, n.created_at AS CreatedAt,
               n.country_name AS Country, n.client AS Client, n.os AS OS, n.isp AS ISP
        ORDER BY n.created_at DESC
        LIMIT $limit
        """
        try:
            result = await self.db_manager.execute_query(query, {"limit": limit})
            nodes = self.helper.process_nodes(result)
            logger.info(f"Fetched {len(nodes)} latest nodes.")
            return nodes
        except Exception as e:
            logger.error(f"Error while fetching latest nodes (limit: {limit})", exc_info=True)
            raise e

    async def fetch_relationships(self, country_name):
        """
        Fetches relationships for a given country, including ISP, OS, client, and node relationships.

        :param country_name: The name of the country to fetch relationships for.
        :return: A list of relationships for the specified country.
        :raises: Exception if there is an error during database execution.
        """
        logger.info(f"Fetching relationships for country: {country_name}")
        query = """
        MATCH (root:Root {name: 'World'})-[:HAS_COUNTRY]->(c:Country {name: $country_name})-[:HAS_ISP]->(isp:ISP)
        -[:HAS_OS]->(os:OS)-[:HAS_CLIENT]->(client:Client)-[:HAS_NODE]->(n:Node) 
        RETURN root, c, isp, os, client, n
        """
        try:
            result = await self.db_manager.execute_query(query, {"country_name": country_name})
            logger.debug(f"Fetched relationships result: {result}")
            if isinstance(result, dict) and "error" in result:
                logger.warning(f"Error while fetching relationships for {country_name}: {result}")
            else:
                logger.info(f"Fetched {len(result)} relationships for country {country_name}.")
            return [record for record in result]
        except Exception as e:
            logger.error(f"Error while fetching relationships for country {country_name}", exc_info=True)
            return {"error": "Failed to fetch relationships", "details": str(e)}

    async def fetch_total_nodes(self):
        """
        Fetches the total number of nodes available in the database.

        :return: The total number of nodes as an integer.
        :raises: Exception if there is an error during database execution.
        """
        logger.info("Fetching total number of nodes...")
        total_nodes_query = """
        MATCH (n:Node)
        RETURN count(n) AS total_nodes
        """
        try:
            result = await self.db_manager.execute_query(total_nodes_query)
            total_nodes = result[0]["total_nodes"] if result else 0
            logger.info(f"Total number of nodes: {total_nodes}")
            return total_nodes
        except Exception as e:
            logger.error("Error while fetching total number of nodes", exc_info=True)
            raise e

    async def fetch_statistics(self, data_type):
        """
        Fetches statistics for a specific data type (OS, client, ISP, or country).

        :param data_type: The type of data for which statistics are being fetched (e.g., os, client, isp, country).
        :return: A dictionary containing the statistics for the requested data type.
        :raises: Exception if there is an error during database execution.
        """
        logger.info(f"Fetching statistics for data type: {data_type}")
        try:
            total_nodes = await self.fetch_total_nodes()
            queries = {
                "os": """
                    MATCH (n:Node)
                    WITH CASE
                        WHEN toLower(n.os) CONTAINS 'linux' THEN 'Linux'
                        WHEN toLower(n.os) CONTAINS 'windows' THEN 'Windows'
                        WHEN toLower(n.os) CONTAINS 'macos' THEN 'MacOS'
                        ELSE 'Other OSs'
                    END AS type, COUNT(n) AS count, (COUNT(n) * 100.0 / $total) AS percentage
                    RETURN type, count, percentage
                    ORDER BY percentage DESC
                """,
                "client": """
                    MATCH (n:Node)
                    WITH CASE
                        WHEN toLower(n.client) CONTAINS 'geth' THEN 'Geth'
                        WHEN toLower(n.client) CONTAINS 'nethermind' THEN 'Nethermind'
                        WHEN toLower(n.client) CONTAINS 'besu' THEN 'Besu'
                        WHEN toLower(n.client) CONTAINS 'erigon' THEN 'Erigon'
                        ELSE 'Other Clients'
                    END AS type, COUNT(n) AS count, (COUNT(n) * 100.0 / $total) AS percentage
                    RETURN type, count, percentage
                    ORDER BY percentage DESC
                """,
                "isp": """
                    MATCH (n:Node)
                    WITH CASE
                        WHEN toLower(n.isp) CONTAINS 'aws' THEN 'AWS'
                        ELSE 'Other ISPs'
                    END AS type, COUNT(n) AS count, (COUNT(n) * 100.0 / $total) AS percentage
                    RETURN type, count, percentage
                    ORDER BY percentage DESC
                """,
                "country": """
                    MATCH (n:Node)
                    RETURN n.country_name AS type, COUNT(n) AS count, (COUNT(n) * 100.0 / $total) AS percentage
                    ORDER BY type ASC
                """
            }

            if data_type in queries:
                query = queries[data_type]
                result = await self.db_manager.execute_query(query, {"total": total_nodes})
                logger.info(f"Fetched statistics for {data_type}.")
                return {data_type: result}
            else:
                logger.warning(f"Invalid data type requested: {data_type}")
                return {"error": "Invalid data type requested"}
        except Exception as e:
            logger.error(f"Error while fetching statistics for {data_type}", exc_info=True)
            raise e

    async def fetch_filtered_nodes(self, country=None, os=None, client=None, isp=None):
        """
        Fetches nodes that match the given filter criteria (country, OS, client, and ISP).

        :param country: The country to filter nodes by (optional).
        :param os: The operating system to filter nodes by (optional).
        :param client: The client type to filter nodes by (optional).
        :param isp: The ISP to filter nodes by (optional).
        :return: A list of nodes that match the specified filters.
        :raises: Exception if there is an error during database execution.
        """
        logger.info(f"Fetching filtered nodes with country={country}, os={os}, client={client}, isp={isp}")
        query = """
        MATCH (n:Node)
        WHERE 
            ($country IS NULL OR toLower(n.country_name) = toLower($country)) AND
            ($os IS NULL OR toLower(n.os) = toLower($os)) AND
            ($client IS NULL OR toLower(n.client) = toLower($client)) AND
            ($isp IS NULL OR toLower(n.isp) = toLower($isp))
        RETURN n.id AS NodeId, n.host AS Host, n.port AS Port, n.client AS Client, n.os AS OS, n.status AS Status,
               n.latitude AS Latitude, n.longitude AS Longitude, n.isp AS ISP, n.country_name AS Country, n.created_at AS CreatedAt
        """
        try:
            result = await self.db_manager.execute_query(query,
                                                         {"country": country, "os": os, "client": client, "isp": isp})
            logger.info(f"Fetched {len(result)} filtered nodes.")
            return result
        except Exception as e:
            logger.error("Error while fetching filtered nodes", exc_info=True)
            raise e
