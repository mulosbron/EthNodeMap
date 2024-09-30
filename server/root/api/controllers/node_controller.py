from quart import jsonify
from api.services.node_service import NodeService
from api.utils.node_helper import NodeHelper
import logging


class NodeController:
    def __init__(self):
        """
        Constructor for NodeController class.
        """
        self.logger = logging.getLogger('quart_app.controller.node_controller')
        self.node_service = NodeService()
        self.helper = NodeHelper()
        self.logger.debug("::NodeController:: Initialized.")

    async def get_nodes(self):
        """
        Retrieves a list of all nodes from the database via NodeService.

        :return: A JSON response containing the list of nodes or an error message.
        """
        self.logger.debug("::get_nodes:: Entering get_nodes method.")
        try:
            nodes = await self.node_service.fetch_nodes()
            self.logger.info("::get_nodes:: Successfully retrieved all nodes.")
            self.logger.debug("::get_nodes:: Exiting get_nodes method.")
            return jsonify(nodes), 200
        except Exception as e:
            self.logger.exception(f"::get_nodes:: Error in get_nodes: {e}")

    async def get_os_types(self):
        """
        Retrieves the types of operating systems associated with the nodes.

        :return: A JSON response containing the OS types or an error message.
        """
        self.logger.debug("::get_os_types:: Entering get_os_types method.")
        try:
            os_types = await self.node_service.fetch_os_types()
            self.logger.info("::get_os_types:: Successfully retrieved OS types.")
            self.logger.debug("::get_os_types:: Exiting get_os_types method.")
            return jsonify(os_types), 200
        except Exception as e:
            self.logger.exception(f"::get_os_types:: Error in get_os_types: {e}")

    async def get_clients(self):
        """
        Retrieves the types of clients associated with the nodes.

        :return: A JSON response containing the client types or an error message.
        """
        self.logger.debug("::get_clients:: Entering get_clients method.")
        try:
            client_types = await self.node_service.fetch_clients()
            self.logger.info("::get_clients:: Successfully retrieved client types.")
            self.logger.debug("::get_clients:: Exiting get_clients method.")
            return jsonify(client_types), 200
        except Exception as e:
            self.logger.exception(f"::get_clients:: Error in get_clients: {e}")

    async def get_countries(self):
        """
        Retrieves a list of countries where the nodes are located.

        :return: A JSON response containing the countries or an error message.
        """
        self.logger.debug("::get_countries:: Entering get_countries method.")
        try:
            countries = await self.node_service.fetch_countries()
            self.logger.info("::get_countries:: Successfully retrieved countries.")
            self.logger.debug("::get_countries:: Exiting get_countries method.")
            return jsonify(countries), 200
        except Exception as e:
            self.logger.exception(f"::get_countries:: Error in get_countries: {e}")

    async def get_isps(self):
        """
        Retrieves a list of ISPs associated with the nodes.

        :return: A JSON response containing the ISPs or an error message.
        """
        self.logger.debug("::get_isps:: Entering get_isps method.")
        try:
            isps = await self.node_service.fetch_isps()
            self.logger.info("::get_isps:: Successfully retrieved ISPs.")
            self.logger.debug("::get_isps:: Exiting get_isps method.")
            return jsonify(isps), 200
        except Exception as e:
            self.logger.exception(f"::get_isps:: Error in get_isps: {e}")

    async def get_node_ids(self):
        """
        Retrieves a list of distinct node IDs from the database via NodeService.

        :return: A JSON response containing the list of node IDs.
        """
        self.logger.debug("::get_node_ids:: Entering get_node_ids method.")
        try:
            node_ids = await self.node_service.fetch_node_ids()
            self.logger.info("::get_node_ids:: Successfully retrieved node IDs.")
            self.logger.debug("::get_node_ids:: Exiting get_node_ids method.")
            return jsonify(node_ids), 200
        except Exception as e:
            self.logger.exception(f"::get_node_ids:: Error in get_node_ids: {e}")

    async def get_node_details(self, node_id):
        """
        Retrieves the details of a specific node given its node_id.

        :param node_id: The ID of the node to retrieve.
        :return: A JSON response containing the node details or an error message.
        """
        self.logger.debug(f"::get_node_details:: Entering get_node_details method with node_id: {node_id}")
        try:
            node_details = await self.node_service.fetch_node_details(node_id)
            if node_details:
                self.logger.info(f"::get_node_details:: Successfully retrieved details for node ID: {node_id}")
            else:
                self.logger.warning(f"::get_node_details:: No details found for node ID: {node_id}")
            self.logger.debug("::get_node_details:: Exiting get_node_details method.")
            return jsonify(node_details), 200
        except Exception as e:
            self.logger.exception(f"::get_node_details:: Error in get_node_details: {e}")

    async def get_relationships(self, country_name):
        """
        Retrieves the relationships between nodes for a specific country.

        :param country_name: The name of the country to filter relationships by.
        :return: A JSON response containing the relationships or an error message.
        """
        self.logger.debug(f"::get_relationships:: Entering get_relationships method with country_name: {country_name}")
        try:
            result = await self.node_service.fetch_relationships(country_name)
            data = self.helper.process_relationships(result)
            self.logger.info(f"::get_relationships:: Successfully retrieved relationships for country: {country_name}")
            self.logger.debug("::get_relationships:: Exiting get_relationships method.")
            return jsonify(data), 200
        except Exception as e:
            self.logger.exception(f"::get_relationships:: Error in get_relationships: {e}")

    async def get_summary_counts(self):
        """
        Retrieves the summary counts for countries, nodes, and ISPs.

        :return: A JSON response containing CountryCount, NumberOfNodes, and ISPCount.
        """
        self.logger.debug("::get_summary_counts:: Entering get_summary_counts method.")
        try:
            summary = await self.node_service.fetch_summary_counts()
            self.logger.info("::get_summary_counts:: Successfully retrieved summary counts.")
            self.logger.debug("::get_summary_counts:: Exiting get_summary_counts method.")
            return jsonify(summary), 200
        except Exception as e:
            self.logger.exception(f"::get_summary_counts:: Error in get_summary_counts: {e}")

    async def get_latest_nodes(self, limit):
        """
        Retrieves a list of the latest nodes with a given limit.

        :return: A JSON response containing the latest nodes or an error message.
        """
        self.logger.debug(f"::get_latest_nodes:: Entering get_latest_nodes method with limit: {limit}")
        try:
            latest_nodes = await self.node_service.fetch_latest_nodes(limit)
            self.logger.info(f"::get_latest_nodes:: Successfully retrieved latest {limit} nodes.")
            self.logger.debug("::get_latest_nodes:: Exiting get_latest_nodes method.")
            return jsonify(latest_nodes), 200
        except Exception as e:
            self.logger.exception(f"::get_latest_nodes:: Error in get_latest_nodes: {e}")

    async def get_filtered_nodes(self, country, os, client, isp):
        """
        Filters nodes based on country, OS, client, and ISP parameters.

        :return: A JSON response containing the filtered nodes or an error message.
        """
        self.logger.debug(
            f"::get_filtered_nodes:: Entering get_filtered_nodes method with filters: country={country}, os={os}, client={client}, isp={isp}")
        try:
            nodes = await self.node_service.fetch_filtered_nodes(country, os, client, isp)
            if not nodes:
                self.logger.info("::get_filtered_nodes:: No nodes found matching the filter criteria.")
                self.logger.debug("::get_filtered_nodes:: Exiting get_filtered_nodes method.")
                return jsonify(nodes), 204
            self.logger.info(f"::get_filtered_nodes:: Successfully retrieved {len(nodes)} filtered nodes.")
            self.logger.debug("::get_filtered_nodes:: Exiting get_filtered_nodes method.")
            return jsonify(nodes), 200
        except Exception as e:
            self.logger.exception(f"::get_filtered_nodes:: Error in get_filtered_nodes: {e}")

    async def get_statistics(self, data_type):
        """
        Retrieves node statistics based on the data type (e.g., os, client, country, isp).

        :param data_type: The type of data for which statistics are requested.
        :return: A JSON response containing the statistics or an error message.
        """
        self.logger.debug(f"::get_statistics:: Entering get_statistics method with data_type: {data_type}")
        try:
            statistics = await self.node_service.fetch_statistics(data_type)
            self.logger.info(f"::get_statistics:: Successfully retrieved statistics for data type: {data_type}")
            self.logger.debug("::get_statistics:: Exiting get_statistics method.")
            return jsonify(statistics), 200
        except Exception as e:
            self.logger.exception(f"::get_statistics:: Error in get_statistics: {e}")
