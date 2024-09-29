import logging
from quart import Blueprint, abort, request
from api.controllers.node_controller import NodeController
from api.utils.node_helper import NodeHelper


class NodeRouter:
    def __init__(self):
        """
        Initializes the NodeRouter class by setting up the Blueprint and registering routes.
        """
        self.logger = logging.getLogger('quart_app.routes.node_router')
        self.logger.debug("::NodeRouter:: Initializing NodeRouter.")
        self.node_controller = NodeController()
        self.node_helper = NodeHelper()
        self.node_bp = Blueprint('node_bp', __name__)
        self.register_routes()
        self.logger.info("::NodeRouter:: NodeRouter initialized successfully.")

    def register_routes(self):
        """
        Registers routes by mapping URLs to private view functions.
        """
        try:
            self.logger.debug("::register_routes:: Registering routes.")
            self.node_bp.add_url_rule('/nodes', 'get_nodes', self._get_nodes, methods=['GET'])
            self.node_bp.add_url_rule('/nodes/operating-systems', 'get_os_types', self._get_os_types, methods=['GET'])
            self.node_bp.add_url_rule('/nodes/clients', 'get_clients', self._get_clients, methods=['GET'])
            self.node_bp.add_url_rule('/nodes/countries', 'get_countries', self._get_countries, methods=['GET'])
            self.node_bp.add_url_rule('/nodes/isps', 'get_isps', self._get_isps, methods=['GET'])
            self.node_bp.add_url_rule('/nodes/ids', 'get_node_ids', self._get_node_ids, methods=['GET'])
            self.node_bp.add_url_rule('/nodes/details/<node_id>', 'get_node_details', self._get_node_details,
                                      methods=['GET'])
            self.node_bp.add_url_rule('/nodes/relationships/<country_name>', 'get_relationships', self._get_relationships,
                                      methods=['GET'])
            self.node_bp.add_url_rule('/nodes/count', 'get_node_count', self._get_summary_counts, methods=['GET'])
            self.node_bp.add_url_rule('/nodes/latest', 'get_latest_nodes', self._get_latest_nodes, methods=['GET'])
            self.node_bp.add_url_rule('/nodes/filter', 'get_filter_nodes', self._get_filtered_nodes, methods=['GET'])
            self.node_bp.add_url_rule('/statistics/<data_type>', 'get_statistics', self._get_statistics,
                                      methods=['GET'])
            self.logger.info("::register_routes:: All routes have been successfully registered.")
        except Exception as e:
            self.logger.exception(f"::register_routes:: Failed to register routes: {e}")

    def get_blueprint(self) -> Blueprint:
        """
        Returns the registered Blueprint with all routes.

        :return: The Blueprint instance containing all registered routes.
        """
        self.logger.debug("::get_blueprint:: Returning the Blueprint with all registered routes.")
        return self.node_bp

    async def _get_nodes(self):
        """
        Handles GET requests to retrieve all nodes.

        :return: The response from the NodeController's get_nodes method.
        """
        try:
            self.logger.debug("::_get_nodes:: Handling request to get all nodes.")
            response = await self.node_controller.get_nodes()
            self.logger.info("::_get_nodes:: Successfully retrieved all nodes.")
            self.logger.debug("::_get_nodes:: Exiting _get_nodes.")
            return response
        except Exception as e:
            self.logger.exception(f"::_get_nodes:: Error while fetching nodes: {e}")

    async def _get_os_types(self):
        """
        Handles GET requests to retrieve operating system types.

        :return: The response from the NodeController's get_os_types method.
        """
        try:
            self.logger.debug("::_get_os_types:: Handling request to get operating system types.")
            response = await self.node_controller.get_os_types()
            self.logger.info("::_get_os_types:: Successfully retrieved operating system types.")
            self.logger.debug("::_get_os_types:: Exiting _get_os_types.")
            return response
        except Exception as e:
            self.logger.exception(f"::_get_os_types:: Error while fetching OS types: {e}")

    async def _get_clients(self):
        """
        Handles GET requests to retrieve client types.

        :return: The response from the NodeController's get_clients method.
        """
        try:
            self.logger.debug("::_get_clients:: Handling request to get clients.")
            response = await self.node_controller.get_clients()
            self.logger.info("::_get_clients:: Successfully retrieved client types.")
            self.logger.debug("::_get_clients:: Exiting _get_clients.")
            return response
        except Exception as e:
            self.logger.exception(f"::_get_clients:: Error while fetching client types: {e}")

    async def _get_countries(self):
        """
        Handles GET requests to retrieve countries.

        :return: The response from the NodeController's get_countries method.
        """
        try:
            self.logger.debug("::_get_countries:: Handling request to get countries.")
            response = await self.node_controller.get_countries()
            self.logger.info("::_get_countries:: Successfully retrieved countries.")
            self.logger.debug("::_get_countries:: Exiting _get_countries.")
            return response
        except Exception as e:
            self.logger.exception(f"::_get_countries:: Error while fetching countries: {e}")

    async def _get_isps(self):
        """
        Handles GET requests to retrieve ISPs.

        :return: The response from the NodeController's get_isps method.
        """
        try:
            self.logger.debug("::_get_isps:: Handling request to get ISPs.")
            response = await self.node_controller.get_isps()
            self.logger.info("::_get_isps:: Successfully retrieved ISPs.")
            self.logger.debug("::_get_isps:: Exiting _get_isps.")
            return response
        except Exception as e:
            self.logger.exception(f"::_get_isps:: Error while fetching ISPs: {e}")

    async def _get_node_ids(self):
        """
        Handles GET requests to retrieve distinct node IDs.

        :return: The response from the NodeController's get_node_ids method.
        """
        try:
            self.logger.debug("::_get_node_ids:: Handling request to get distinct node IDs.")
            response = await self.node_controller.get_node_ids()
            self.logger.info("::_get_node_ids:: Successfully retrieved node IDs.")
            self.logger.debug("::_get_node_ids:: Exiting _get_node_ids.")
            return response
        except Exception as e:
            self.logger.exception(f"::_get_node_ids:: Error while fetching node IDs: {e}")

    async def _get_node_details(self, node_id):
        """
        Handles GET requests to retrieve details of a specific node.

        :param node_id: The identifier of the node to retrieve details for.
        :return: The response from the NodeController's get_node_details method.
        """
        if not self.node_helper.is_hexadecimal(node_id):
            self.logger.warning(f"::_get_node_details:: Invalid node_id format: {node_id}")
            abort(400, description="Invalid node_id format. Expected a hexadecimal string.")
        try:
            self.logger.debug(f"::_get_node_details:: Handling request to get details for node ID: {node_id}.")
            response = await self.node_controller.get_node_details(node_id)
            self.logger.info(f"::_get_node_details:: Successfully retrieved details for node ID: {node_id}.")
            self.logger.debug("::_get_node_details:: Exiting _get_node_details.")
            return response
        except Exception as e:
            self.logger.exception(f"::_get_node_details:: Error in _get_node_details for node ID {node_id}: {e}")

    async def _get_relationships(self, country_name):
        """
        Handles GET requests to retrieve relationships based on country name.

        :param country_name: The name of the country to filter relationships by.
        :return: The response from the NodeController's get_relationships method.
        """
        self.logger.debug(f"::_get_relationships:: Handling request to get relationships for country: {country_name}.")
        try:
            countries_response, status_code = await self.node_controller.get_countries()
            countries_data = await countries_response.get_json()
            self.logger.debug(f"::_get_relationships:: Available countries: {countries_data}")
            if country_name not in countries_data:
                self.logger.warning(f"::_get_relationships:: Country {country_name} not found.")
                abort(404, description=f"Country {country_name} not found")
            response = await self.node_controller.get_relationships(country_name)
            self.logger.info(f"::_get_relationships:: Successfully retrieved relationships for country: {country_name}.")
            self.logger.debug("::_get_relationships:: Exiting _get_relationships.")
            return response
        except Exception as e:
            self.logger.exception(f"::_get_relationships:: Error in _get_relationships for country {country_name}: {e}")

    async def _get_summary_counts(self):
        """
        Handles GET requests to retrieve summary counts for countries, nodes, and ISPs.

        :return: The response from the NodeController's get_summary_counts method.
        """
        try:
            self.logger.debug("::_get_summary_counts:: Handling request to get summary counts.")
            response = await self.node_controller.get_summary_counts()
            self.logger.info("::_get_summary_counts:: Successfully retrieved summary counts.")
            self.logger.debug("::_get_summary_counts:: Exiting _get_summary_counts.")
            return response
        except Exception as e:
            self.logger.exception(f"::_get_summary_counts:: Error in _get_summary_counts: {e}")

    async def _get_latest_nodes(self):
        """
        Handles GET requests to retrieve the latest nodes.

        :return: The response from the NodeController's get_latest_nodes method.
        """
        limit = request.args.get('limit', default=50, type=int)
        if limit <= 0:
            self.logger.warning(f"::_get_latest_nodes:: Invalid limit value received: {limit}")
            abort(400, description="Invalid limit value. Must be greater than zero.")
        try:
            self.logger.debug(f"::_get_latest_nodes:: Handling request to get latest {limit} nodes.")
            response = await self.node_controller.get_latest_nodes(limit)
            self.logger.info(f"::_get_latest_nodes:: Successfully retrieved latest {limit} nodes.")
            self.logger.debug("::_get_latest_nodes:: Exiting _get_latest_nodes.")
            return response
        except Exception as e:
            self.logger.exception(f"::_get_latest_nodes:: Error in _get_latest_nodes (limit: {limit}): {e}")

    async def _get_filtered_nodes(self):
        """
        Handles GET requests to retrieve nodes based on filters.

        :return: The response from the NodeController's get_filter_nodes method.
        """
        try:
            country = request.args.get('country') or None
            os_type = request.args.get('os') or None
            client = request.args.get('client') or None
            isp = request.args.get('isp') or None
            self.logger.debug(
                f"::_get_filtered_nodes:: Handling request to get filtered nodes with filters: country={country}, os={os_type}, client={client}, isp={isp}.")
            response = await self.node_controller.get_filtered_nodes(country, os_type, client, isp)
            self.logger.info("::_get_filtered_nodes:: Successfully retrieved filtered nodes.")
            self.logger.debug("::_get_filtered_nodes:: Exiting _get_filtered_nodes.")
            return response
        except Exception as e:
            self.logger.exception(f"::_get_filtered_nodes:: Error in _get_filtered_nodes: {e}")

    async def _get_statistics(self, data_type: str):
        """
        Handles GET requests to retrieve statistics based on data type.

        :param data_type: The type of data for which statistics are requested.
        :return: The response from the NodeController's get_statistics method.
        """
        if data_type not in ['os', 'client', 'country', 'isp']:
            self.logger.warning(f"::_get_statistics:: Invalid data type requested: {data_type}")
            abort(400, description='Invalid data type requested')
        try:
            self.logger.debug(f"::_get_statistics:: Handling request to get statistics for data type: {data_type}.")
            response = await self.node_controller.get_statistics(data_type)
            self.logger.info(f"::_get_statistics:: Successfully retrieved statistics for data type: {data_type}.")
            self.logger.debug("::_get_statistics:: Exiting _get_statistics.")
            return response
        except Exception as e:
            self.logger.exception(f"::_get_statistics:: Error in _get_statistics for data type {data_type}: {e}")