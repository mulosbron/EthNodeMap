from quart import jsonify, request
from neo4j.exceptions import ServiceUnavailable
from services.node_service import NodeService
from utils.node_helper import NodeHelper
import logging

logger = logging.getLogger('quart_app.controller.node_controller')


class NodeController:
    def __init__(self):
        """
        Constructor for NodeController class.
        """
        self.node_service = NodeService()
        self.helper = NodeHelper()

    async def get_nodes(self):
        """
        Retrieves a list of all nodes from the database via NodeService.
        """
        try:
            nodes = await self.node_service.fetch_nodes()
            return jsonify(nodes), 200
        except ServiceUnavailable as e:
            return jsonify({"error": f"Database service unavailable: {str(e)}"}), 504
        except TimeoutError:
            return jsonify({"error": "Database query timed out."}), 504
        except Exception as e:
            # Hata mesajını exception mesajıyla birlikte döndür
            return jsonify({"error": f"Error fetching nodes: {str(e)}"}), 500

    async def get_os_types(self):
        """
        Retrieves the types of operating systems associated with the nodes.
        """
        try:
            os_types = await self.node_service.fetch_os_types()
            return jsonify(os_types)
        except Exception as e:
            return jsonify({"error": f"Error fetching operating systems: {str(e)}"}), 500

    async def get_clients(self):
        """
        Retrieves the types of clients associated with the nodes.
        """
        try:
            client_types = await self.node_service.fetch_clients()
            return jsonify(client_types)
        except Exception as e:
            return jsonify({"error": f"Error fetching clients: {str(e)}"}), 500

    async def get_countries(self):
        """
        Retrieves a list of countries where the nodes are located.
        """
        try:
            countries = await self.node_service.fetch_countries()
            return jsonify(countries)
        except Exception as e:
            return jsonify({"error": f"Error fetching countries: {str(e)}"}), 500

    async def get_isps(self):
        """
        Retrieves a list of ISPs associated with the nodes.
        """
        try:
            isps = await self.node_service.fetch_isps()
            return jsonify(isps)
        except Exception as e:
            return jsonify({"error": f"Error fetching ISPs: {str(e)}"}), 500

    async def get_node_ids(self):
        """
        Retrieves a list of distinct node IDs from the database via NodeService.

        :return: A JSON response containing the list of node IDs.
        :rtype: Response
        :raises HTTPException: If an error occurs while retrieving node IDs.
        """
        try:
            logger.debug("Handling request to get distinct node IDs.")
            node_ids = await self.node_service.fetch_node_ids()
            return jsonify({"NodeIDs": node_ids}), 200
        except ServiceUnavailable as e:
            logger.error(f"Database service unavailable: {e}")
            return jsonify({"error": f"Database service unavailable: {str(e)}"}), 504
        except TimeoutError:
            logger.error("Database query timed out.")
            return jsonify({"error": "Database query timed out."}), 504
        except Exception as e:
            logger.error(f"Error fetching node IDs: {e}")
            return jsonify({"error": f"Error fetching node IDs: {str(e)}"}), 500

    async def get_node_details(self, node_id):
        """
        Retrieves the details of a specific node given its node_id.
        """
        # Reintroduced node_id validation
        if not self.helper.is_hexadecimal(node_id):
            return jsonify({"error": "Invalid node_id format. Expected a hexadecimal string."}), 400
        try:
            node_details = await self.node_service.fetch_node_details(node_id)
            if node_details:
                return jsonify(node_details), 200
            else:
                return jsonify({"error": f"No details found for node_id {node_id}"}), 404
        except Exception as e:
            return jsonify({"error": f"Error fetching details for node {node_id}: {str(e)}"}), 500

    async def get_relationships(self, country_name):
        """
        Retrieves the relationships between nodes for a specific country.
        """
        try:
            result = await self.node_service.fetch_relationships(country_name)
            if not result:
                return jsonify({"message": f"No nodes found for country {country_name}"}), 404
            data = self.helper.process_relationships(result)
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": f"Error fetching relationships for country {country_name}: {str(e)}"}), 500

    async def get_node_count(self):
        """
        Retrieves the total count of nodes in the system.
        """
        try:
            node_count = await self.node_service.fetch_node_count()
            return jsonify({"NumberOfNodes": node_count})
        except Exception as e:
            return jsonify({"error": f"Error fetching node count: {str(e)}"}), 500

    async def get_latest_nodes(self):
        """
        Retrieves a list of the latest nodes with a given limit.
        """
        try:
            limit = request.args.get('limit', default=50, type=int)
            if limit <= 0:
                return jsonify({"error": "Invalid limit value. Must be greater than zero."}), 400
            latest_nodes = await self.node_service.fetch_latest_nodes(limit)
            return jsonify(latest_nodes)
        except Exception as e:
            return jsonify({"error": f"Failed to fetch latest nodes with limit {limit}: {str(e)}"}), 500

    async def get_filter_nodes(self):
        """
        Filters nodes based on country, OS, client, and ISP parameters.
        """
        try:
            country = request.args.get('country') or None
            os = request.args.get('os') or None
            client = request.args.get('client') or None
            isp = request.args.get('isp') or None
            nodes = await self.node_service.fetch_filtered_nodes(country, os, client, isp)
            if not nodes:
                return jsonify({"message": "No nodes found for the given filters"}), 404
            return jsonify(nodes), 200
        except Exception as e:
            return jsonify({"error": f"Error fetching filtered nodes: {str(e)}"}), 500

    async def get_statistics(self, data_type):
        """
        Retrieves node statistics based on the data type (e.g., os, client, country, isp).
        """
        try:
            if data_type in ['os', 'client', 'country', 'isp']:
                statistics = await self.node_service.fetch_statistics(data_type)
                return jsonify(statistics)
            else:
                # Return a 400 response for invalid data type
                return jsonify({"error": "Invalid data type requested"}), 400
        except Exception as e:
            # Return a 500 response if there's an exception
            return jsonify({"error": f"Failed to fetch statistics for data type {data_type}: {str(e)}"}), 500
