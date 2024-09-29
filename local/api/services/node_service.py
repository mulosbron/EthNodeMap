import logging
from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer
from api.utils.node_helper import NodeHelper
from api.db.neo4j_manager import AsyncSessionManager


class NodeService:
    def __init__(self):
        self.logger = logging.getLogger('quart_app.services.node_service')
        self.db_manager = AsyncSessionManager()
        self.helper = NodeHelper()
        self.cache = Cache(
            Cache.MEMORY,
            serializer=PickleSerializer()
        )
        self.logger.debug("::NodeService:: Initialized.")

    @cached(ttl=900, cache=Cache.MEMORY, key="fetch_nodes")
    async def fetch_nodes(self):
        """
        Fetches all nodes from the database.

        :return: A list of dictionaries representing nodes with details such as NodeId, Host, Port, etc.
        """
        self.logger.debug("::fetch_nodes:: Entering fetch_nodes method.")
        self.logger.info("::fetch_nodes:: Fetching all nodes...")
        query = """
        MATCH (n:Node)
        RETURN n.id AS NodeId, n.host AS Host, n.port AS Port, n.client AS Client, n.os AS OS, n.status AS Status,
        n.latitude AS Latitude, n.longitude AS Longitude, n.isp AS ISP, n.country_name AS Country, n.created_at AS CreatedAt
        """
        try:
            result = await self.db_manager.execute_query(query)
            self.logger.debug(f"::fetch_nodes:: Query executed successfully: {query}")
            self.logger.info(f"::fetch_nodes:: Fetched {len(result)} nodes.")
            self.logger.debug("::fetch_nodes:: Exiting fetch_nodes method with result.")
            return result
        except Exception as e:
            self.logger.exception(f"::fetch_nodes:: Error while fetching nodes: {e}")
            self.logger.debug("::fetch_nodes:: Exiting fetch_nodes method with error.")
            raise e

    @cached(ttl=300, cache=Cache.MEMORY, key="fetch_os_types")
    async def fetch_os_types(self):
        """
        Fetches distinct operating system types used by the nodes.

        :return: A list of distinct OS types.
        """
        self.logger.debug("::fetch_os_types:: Entering fetch_os_types method.")
        self.logger.info("::fetch_os_types:: Fetching OS types...")
        query = "MATCH (n:Node) RETURN DISTINCT n.os AS OS"
        try:
            records = await self.db_manager.execute_query(query)
            self.logger.debug(f"::fetch_os_types:: Query executed successfully: {query}")
            os_types = [record["OS"] for record in records]
            self.logger.info(f"::fetch_os_types:: Fetched {len(os_types)} OS types.")
            self.logger.debug(f"::fetch_os_types:: OS types: {os_types}")
            self.logger.debug("::fetch_os_types:: Exiting fetch_os_types method with result.")
            return os_types
        except Exception as e:
            self.logger.exception(f"::fetch_os_types:: Error while fetching OS types: {e}")
            self.logger.debug("::fetch_os_types:: Exiting fetch_os_types method with error.")
            raise e

    @cached(ttl=300, cache=Cache.MEMORY, key="fetch_clients")
    async def fetch_clients(self):
        """
        Fetches distinct client types used by the nodes.

        :return: A list of distinct client types.
        """
        self.logger.debug("::fetch_clients:: Entering fetch_clients method.")
        self.logger.info("::fetch_clients:: Fetching client types...")
        query = """
        MATCH (n:Node)
        RETURN DISTINCT n.client AS Client
        """
        try:
            records = await self.db_manager.execute_query(query)
            self.logger.debug(f"::fetch_clients:: Query executed successfully: {query}")
            clients = [record["Client"] for record in records]
            self.logger.info(f"::fetch_clients:: Fetched {len(clients)} client types.")
            self.logger.debug(f"::fetch_clients:: Client types: {clients}")
            self.logger.debug("::fetch_clients:: Exiting fetch_clients method with result.")
            return clients
        except Exception as e:
            self.logger.exception(f"::fetch_clients:: Error while fetching client types: {e}")
            self.logger.debug("::fetch_clients:: Exiting fetch_clients method with error.")
            raise e

    @cached(ttl=300, cache=Cache.MEMORY, key="fetch_countries")
    async def fetch_countries(self):
        """
        Fetches distinct countries where the nodes are located.

        :return: A list of distinct countries.
        """
        self.logger.debug("::fetch_countries:: Entering fetch_countries method.")
        self.logger.info("::fetch_countries:: Fetching countries...")
        query = """
        MATCH (n:Node)
        RETURN DISTINCT n.country_name AS Country
        """
        try:
            records = await self.db_manager.execute_query(query)
            self.logger.debug(f"::fetch_countries:: Query executed successfully: {query}")
            countries = [record["Country"] for record in records]
            self.logger.info(f"::fetch_countries:: Fetched {len(countries)} countries.")
            self.logger.debug(f"::fetch_countries:: Countries: {countries}")
            self.logger.debug("::fetch_countries:: Exiting fetch_countries method with result.")
            return countries
        except Exception as e:
            self.logger.exception(f"::fetch_countries:: Error while fetching countries: {e}")
            self.logger.debug("::fetch_countries:: Exiting fetch_countries method with error.")
            raise e

    @cached(ttl=300, cache=Cache.MEMORY, key="fetch_isps")
    async def fetch_isps(self):
        """
        Fetches distinct Internet Service Providers (ISPs) associated with the nodes.

        :return: A list of distinct ISPs.
        """
        self.logger.debug("::fetch_isps:: Entering fetch_isps method.")
        self.logger.info("::fetch_isps:: Fetching ISPs...")
        query = """
        MATCH (n:Node)
        RETURN DISTINCT n.isp AS ISP
        """
        try:
            records = await self.db_manager.execute_query(query)
            self.logger.debug(f"::fetch_isps:: Query executed successfully: {query}")
            isps = [record["ISP"] for record in records]
            self.logger.info(f"::fetch_isps:: Fetched {len(isps)} ISPs.")
            self.logger.debug(f"::fetch_isps:: ISPs: {isps}")
            self.logger.debug("::fetch_isps:: Exiting fetch_isps method with result.")
            return isps
        except Exception as e:
            self.logger.exception(f"::fetch_isps:: Error while fetching ISPs: {e}")
            self.logger.debug("::fetch_isps:: Exiting fetch_isps method with error.")
            raise e

    @cached(ttl=300, cache=Cache.MEMORY, key="fetch_node_ids")
    async def fetch_node_ids(self):
        """
        Fetches distinct node IDs from the database.

        :return: A list of distinct node IDs.
        """
        self.logger.debug("::fetch_node_ids:: Entering fetch_node_ids method.")
        self.logger.info("::fetch_node_ids:: Fetching node IDs...")
        query = """
        MATCH (n:Node)
        RETURN DISTINCT n.id AS NodeID
        """
        try:
            records = await self.db_manager.execute_query(query)
            self.logger.debug(f"::fetch_node_ids:: Query executed successfully: {query}")
            node_ids = [record["NodeID"] for record in records]
            self.logger.info(f"::fetch_node_ids:: Fetched {len(node_ids)} node IDs.")
            self.logger.debug(f"::fetch_node_ids:: Node IDs: {node_ids}")
            self.logger.debug("::fetch_node_ids:: Exiting fetch_node_ids method with result.")
            return node_ids
        except Exception as e:
            self.logger.exception(f"::fetch_node_ids:: Error while fetching node IDs: {e}")
            self.logger.debug("::fetch_node_ids:: Exiting fetch_node_ids method with error.")
            raise e

    @cached(ttl=300, cache=Cache.MEMORY, key="fetch_summary_counts")
    async def fetch_summary_counts(self):
        """
        Fetches the counts for countries, nodes, and ISPs.

        :return: A dictionary containing CountryCount, NumberOfNodes, and ISPCount.
        """
        self.logger.debug("::fetch_summary_counts:: Entering fetch_summary_counts method.")
        self.logger.info("::fetch_summary_counts:: Fetching summary counts for countries, nodes, and ISPs...")
        queries = {
            "NumberOfCountries": """
                MATCH (n:Country)
                WHERE n.name IS NOT NULL
                RETURN COUNT(DISTINCT n.name) AS NumberOfCountries
            """,
            "NumberOfNodes": """
                MATCH (n:Node)
                RETURN COUNT(DISTINCT n.id) AS NumberOfNodes
            """,
            "NumberOfISPs": """
                MATCH (n:Node)
                WHERE n.isp IS NOT NULL
                RETURN COUNT(DISTINCT n.isp) AS NumberOfISPs
            """
        }
        summary = {}
        try:
            for key, query in queries.items():
                self.logger.debug(f"::fetch_summary_counts:: Executing query for {key}: {query}")
                result = await self.db_manager.execute_query(query)
                if result is None:
                    self.logger.error(f"::fetch_summary_counts:: Failed to fetch {key} due to database error.")
                    raise Exception(f"Failed to fetch {key} from the database.")
                if len(result) > 0:
                    summary[key] = result[0][key]
                    self.logger.debug(f"::fetch_summary_counts:: {key} result: {summary[key]}")
                else:
                    summary[key] = 0
                    self.logger.warning(f"::fetch_summary_counts:: No result for {key}, defaulting to 0.")
            self.logger.info("::fetch_summary_counts:: Successfully fetched summary counts.")
            self.logger.debug(f"::fetch_summary_counts:: Summary counts: {summary}")
            self.logger.debug("::fetch_summary_counts:: Exiting fetch_summary_counts method with result.")
            return summary
        except Exception as e:
            self.logger.exception(f"::fetch_summary_counts:: Error while fetching summary counts: {e}")
            self.logger.debug("::fetch_summary_counts:: Exiting fetch_summary_counts method with error.")
            raise e

    @cached(ttl=300, cache=Cache.MEMORY,
            key=lambda f, data_type: f"fetch_statistics:{data_type}")
    async def fetch_statistics(self, data_type):
        """
        Fetches statistics for a specific data type (OS, client, ISP, or country).

        :param data_type: The type of data for which statistics are being fetched (e.g., os, client, isp, country).
        :return: A dictionary containing the statistics for the requested data type.
        """
        self.logger.debug(f"::fetch_statistics:: Entering fetch_statistics method with data_type: {data_type}")
        self.logger.info(f"::fetch_statistics:: Fetching statistics for data type: {data_type}")
        try:
            total_nodes = await self.fetch_total_nodes()
            self.logger.debug(f"::fetch_statistics:: Total nodes retrieved: {total_nodes}")
            queries = {
                "os":
                    """
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
                "client":
                    """
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
                "isp":
                    """
                        MATCH (n:Node)
                        WITH CASE
                            WHEN toLower(n.isp) CONTAINS 'contabo' THEN 'Contabo'
                            WHEN toLower(n.isp) CONTAINS 'aws' OR toLower(n.isp) CONTAINS 'amazon' THEN 'AWS'
                            WHEN toLower(n.isp) CONTAINS 'azure' OR toLower(n.isp) CONTAINS 'microsoft' THEN 'Azure'
                            WHEN toLower(n.isp) CONTAINS 'google' THEN 'Google'
                            WHEN toLower(n.isp) CONTAINS 'alibaba' THEN 'Alibaba'
                            WHEN toLower(n.isp) CONTAINS 'oracle' THEN 'Oracle'
                            WHEN toLower(n.isp) CONTAINS 'ibm' THEN 'IBM'
                            WHEN toLower(n.isp) CONTAINS 'tencent' THEN 'Tencent'
                            WHEN toLower(n.isp) CONTAINS 'ovh' THEN 'OVHCloud'
                            WHEN toLower(n.isp) CONTAINS 'digitalocean' THEN 'DigitalOcean'
                            WHEN toLower(n.isp) CONTAINS 'linode' OR toLower(n.isp) CONTAINS 'akamai' THEN 'Linode'
                            WHEN toLower(n.isp) CONTAINS 'salesforce' THEN 'Salesforce'
                            WHEN toLower(n.isp) CONTAINS 'huawei' AND toLower(n.isp) CONTAINS 'cloud' THEN 'Huawei'
                            WHEN toLower(n.isp) CONTAINS 'dell' AND toLower(n.isp) CONTAINS 'cloud' THEN 'Dell'
                            WHEN toLower(n.isp) CONTAINS 'vultr' THEN 'Vultr'
                            WHEN toLower(n.isp) CONTAINS 'heroku' THEN 'Heroku'
                            WHEN toLower(n.isp) CONTAINS 'hetzner' THEN 'Hetzner'
                            WHEN toLower(n.isp) CONTAINS 'scaleway' THEN 'Scaleway'
                            WHEN toLower(n.isp) CONTAINS 'upcloud' THEN 'Upcloud'
                            WHEN toLower(n.isp) CONTAINS 'kamatera' THEN 'Kamatera'
                            ELSE 'Other ISPs'
                        END AS type, COUNT(n) AS count, (COUNT(n) * 100.0 / $total) AS percentage
                        RETURN type, count, percentage
                        ORDER BY percentage DESC
                    """,
                "country":
                    """
                        MATCH (n:Node)
                        RETURN n.country_name AS type, COUNT(n) AS count, (COUNT(n) * 100.0 / $total) AS percentage
                        ORDER BY type ASC
                    """
            }
            if data_type in queries:
                query = queries[data_type]
                self.logger.debug(f"::fetch_statistics:: Executing query for {data_type}: {query}")
                result = await self.db_manager.execute_query(query, {"total": total_nodes})
                if result is None:
                    self.logger.error("::fetch_statistics:: Failed to fetch statistics due to database error.")
                    raise Exception("Failed to fetch statistics from the database.")
                self.logger.info(f"::fetch_statistics:: Fetched statistics for {data_type}.")
                self.logger.debug(f"::fetch_statistics:: Statistics result: {result}")
                self.logger.debug("::fetch_statistics:: Exiting fetch_statistics method with result.")
                return {data_type: result}
            else:
                self.logger.warning(f"::fetch_statistics:: Invalid data type requested: {data_type}")
                self.logger.debug("::fetch_statistics:: Exiting fetch_statistics method with error.")
                return {"error": "Invalid data type requested"}
        except Exception as e:
            self.logger.exception(f"::fetch_statistics:: Error while fetching statistics: {e}")
            self.logger.debug("::fetch_statistics:: Exiting fetch_statistics method with error.")
            raise e

    @cached(ttl=300, cache=Cache.MEMORY,
            key=lambda f, node_id: f"fetch_node_details:{node_id}")
    async def fetch_node_details(self, node_id):
        """
        Fetches detailed information about a specific node by its ID.

        :param node_id: The unique identifier of the node.
        :return: A dictionary containing the node details or None if the node is not found.
        """
        self.logger.debug(f"::fetch_node_details:: Entering fetch_node_details method with node_id: {node_id}")
        self.logger.info(f"::fetch_node_details:: Fetching details for node ID: {node_id}")
        query = """
                        MATCH (n:Node {id: $node_id})
                        RETURN n.id AS NodeId, n.host AS Host, n.port AS Port, n.client AS Client, n.os AS OS, n.status AS Status,
                        n.latitude AS Latitude, n.longitude AS Longitude, n.isp AS ISP, n.country_name AS Country, n.created_at AS CreatedAt
                        """
        try:
            result = await self.db_manager.execute_query(query, {"node_id": node_id})
            self.logger.debug(f"::fetch_node_details:: Query executed successfully: {query}")
            if result:
                self.logger.info(f"::fetch_node_details:: Details for node ID {node_id} fetched successfully.")
                self.logger.debug(f"::fetch_node_details:: Node details: {result[0]}")
            else:
                self.logger.warning(f"::fetch_node_details:: No details found for node ID {node_id}.")
            self.logger.debug("::fetch_node_details:: Exiting fetch_node_details method with result.")
            return result[0]
        except Exception as e:
            self.logger.exception(f"::fetch_node_details:: Error while fetching details for node ID {node_id}: {e}")
            self.logger.debug("::fetch_node_details:: Exiting fetch_node_details method with error.")
            raise e

    @cached(ttl=300, cache=Cache.MEMORY, key=lambda f, limit: f"fetch_latest_nodes:{limit}")
    async def fetch_latest_nodes(self, limit):
        """
        Fetches the latest nodes up to a specified limit.

        :param limit: The maximum number of latest nodes to retrieve.
        :return: A list of the latest nodes.
        """
        self.logger.debug(f"::fetch_latest_nodes:: Entering fetch_latest_nodes method with limit: {limit}")
        self.logger.info(f"::fetch_latest_nodes:: Fetching latest {limit} nodes...")
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
            self.logger.info(f"::fetch_latest_nodes:: Fetched {len(nodes)} latest nodes.")
            self.logger.debug(f"::fetch_latest_nodes:: Latest nodes: {nodes}")
            self.logger.debug("::fetch_latest_nodes:: Exiting fetch_latest_nodes method with result.")
            return nodes
        except Exception as e:
            self.logger.exception(f"::fetch_latest_nodes:: Error while fetching latest nodes (limit: {limit}): {e}")
            self.logger.debug("::fetch_latest_nodes:: Exiting fetch_latest_nodes method with error.")
            raise e

    @cached(ttl=300, cache=Cache.MEMORY,
            key=lambda f, country_name: f"fetch_relationships:{country_name}")
    async def fetch_relationships(self, country_name):
        """
        Fetches relationships for a given country, including ISP, OS, client, and node relationships.

        :param country_name: The name of the country to fetch relationships for.
        :return: A list of relationships for the specified country.
        """
        self.logger.debug(f"::fetch_relationships:: Entering fetch_relationships method with country_name: {country_name}")
        self.logger.info(f"::fetch_relationships:: Fetching relationships for country: {country_name}")
        query = """
        MATCH (root:Root {name: 'World'})-[:HAS_COUNTRY]->(c:Country {name: $country_name})-[:HAS_ISP]->(isp:ISP)
        -[:HAS_OS]->(os:OS)-[:HAS_CLIENT]->(client:Client)-[:HAS_NODE]->(n:Node) 
        RETURN root, c, isp, os, client, n
        """
        try:
            result = await self.db_manager.execute_query(query, {"country_name": country_name})
            self.logger.debug(f"::fetch_relationships:: Query executed successfully: {query}")
            self.logger.debug(f"::fetch_relationships:: Fetched relationships result: {result}")
            if isinstance(result, dict) and "error" in result:
                self.logger.warning(f"::fetch_relationships:: Error while fetching relationships for {country_name}: {result}")
            else:
                self.logger.info(f"::fetch_relationships:: Fetched {len(result)} relationships for country {country_name}.")
            self.logger.debug("::fetch_relationships:: Exiting fetch_relationships method with result.")
            return [record for record in result]
        except Exception as e:
            self.logger.exception(f"::fetch_relationships:: Error while fetching relationships for country {country_name}: {e}")
            self.logger.debug("::fetch_relationships:: Exiting fetch_relationships method with error.")
            raise e

    @cached(ttl=300, cache=Cache.MEMORY, key="fetch_total_nodes")
    async def fetch_total_nodes(self):
        """
        Fetches the total number of nodes available in the database.

        :return: The total number of nodes as an integer.
        """
        self.logger.debug("::fetch_total_nodes:: Entering fetch_total_nodes method.")
        self.logger.info("::fetch_total_nodes:: Fetching total number of nodes...")
        total_nodes_query = """
        MATCH (n:Node)
        RETURN count(n) AS total_nodes
        """
        try:
            result = await self.db_manager.execute_query(total_nodes_query)
            self.logger.debug(f"::fetch_total_nodes:: Query executed successfully: {total_nodes_query}")
            total_nodes = result[0]["total_nodes"] if result else 0
            self.logger.info(f"::fetch_total_nodes:: Total number of nodes: {total_nodes}")
            self.logger.debug("::fetch_total_nodes:: Exiting fetch_total_nodes method with result.")
            return total_nodes
        except Exception as e:
            self.logger.exception(f"::fetch_total_nodes:: Error while fetching total number of nodes: {e}")
            self.logger.debug("::fetch_total_nodes:: Exiting fetch_total_nodes method with error.")
            raise e

    @cached(ttl=300, cache=Cache.MEMORY,
            key=lambda f, country, os, client, isp: f"fetch_filtered_nodes:{country}:{os}:{client}:{isp}")
    async def fetch_filtered_nodes(self, country=None, os=None, client=None, isp=None):
        """
        Fetches nodes that match the given filter criteria (country, OS, client, and ISP).

        :param country: The country to filter nodes by (optional).
        :param os: The operating system to filter nodes by (optional).
        :param client: The client type to filter nodes by (optional).
        :param isp: The ISP to filter nodes by (optional).
        :return: A list of nodes that match the specified filters.
        """
        self.logger.debug(
            f"::fetch_filtered_nodes:: Entering fetch_filtered_nodes method with filters: country={country}, os={os}, client={client}, isp={isp}")
        self.logger.info(f"::fetch_filtered_nodes:: Fetching filtered nodes with country={country}, os={os}, client={client}, isp={isp}")
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
            params = {"country": country, "os": os, "client": client, "isp": isp}
            self.logger.debug(f"::fetch_filtered_nodes:: Executing query with parameters: {params}")
            result = await self.db_manager.execute_query(query, params)
            self.logger.info(f"::fetch_filtered_nodes:: Fetched {len(result)} filtered nodes.")
            self.logger.debug(f"::fetch_filtered_nodes:: Filtered nodes result: {result}")
            self.logger.debug("::fetch_filtered_nodes:: Exiting fetch_filtered_nodes method with result.")
            return result
        except Exception as e:
            self.logger.exception(f"::fetch_filtered_nodes:: Error while fetching filtered nodes: {e}")
            self.logger.debug("::fetch_filtered_nodes:: Exiting fetch_filtered_nodes method with error.")
            raise e
