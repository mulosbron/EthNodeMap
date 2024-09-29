import os
from quart import Blueprint, abort
from controllers.node_controller import NodeController
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger('quart_app.routes.node_route')


class NodeRoutes:
    def __init__(self):
        """
        Initializes the NodeRoutes class by setting up the Blueprint and registering routes.

        :raises EnvironmentError: If necessary environment variables are missing.
        :raises HTTPException: If Blueprint registration fails.
        """
        self.node_controller = NodeController()
        self.node_bp = Blueprint('node_bp', __name__)
        self.register_routes()

    def register_routes(self):
        """
        Registers routes by mapping URLs to private view functions.

        :raises HTTPException: If route registration fails.
        """
        try:
            self.node_bp.add_url_rule('/nodes', 'get_nodes', self._get_nodes, methods=['GET'])
            self.node_bp.add_url_rule('/nodes/operating-systems', 'get_os_types', self._get_os_types, methods=['GET'])
            self.node_bp.add_url_rule('/nodes/clients', 'get_clients', self._get_clients, methods=['GET'])
            self.node_bp.add_url_rule('/nodes/countries', 'get_countries', self._get_countries, methods=['GET'])
            self.node_bp.add_url_rule('/nodes/isps', 'get_isps', self._get_isps, methods=['GET'])
            self.node_bp.add_url_rule('/nodes/ids', 'get_node_ids', self._get_node_ids, methods=['GET'])
            self.node_bp.add_url_rule('/nodes/details/<node_id>', 'get_node_details', self._get_node_details,
                                      methods=['GET'])
            self.node_bp.add_url_rule('/nodes/country/<country_name>', 'get_relationships', self._get_relationships,
                                      methods=['GET'])
            self.node_bp.add_url_rule('/nodes/count', 'get_node_count', self._get_node_count, methods=['GET'])
            self.node_bp.add_url_rule('/nodes/latest', 'get_latest_nodes', self._get_latest_nodes, methods=['GET'])
            self.node_bp.add_url_rule('/nodes/filter', 'get_filter_nodes', self._get_filter_nodes, methods=['GET'])
            self.node_bp.add_url_rule('/statistics/<data_type>', 'get_statistics', self._get_statistics,
                                      methods=['GET'])
            logger.info("All routes have been successfully registered.")
        except Exception as e:
            logger.error(f"Failed to register routes: {e}", exc_info=True)
            abort(500, description="Failed to register routes.")

    async def _get_nodes(self) -> Any:
        """
        Handles GET requests to retrieve all nodes.

        :return: The response from the NodeController's get_nodes method.
        :rtype: Any
        :raises HTTPException: If an error occurs while retrieving nodes.
        """
        try:
            logger.debug("Handling request to get all nodes.")
            return await self.node_controller.get_nodes()
        except Exception as e:
            logger.error(f"Error in _get_nodes: {e}", exc_info=True)
            abort(500, description="Failed to retrieve nodes.")

    async def _get_os_types(self) -> Any:
        """
        Handles GET requests to retrieve operating system types.

        :return: The response from the NodeController's get_os_types method.
        :rtype: Any
        :raises HTTPException: If an error occurs while retrieving OS types.
        """
        try:
            logger.debug("Handling request to get operating system types.")
            return await self.node_controller.get_os_types()
        except Exception as e:
            logger.error(f"Error in _get_os_types: {e}", exc_info=True)
            abort(500, description="Failed to retrieve operating system types.")

    async def _get_clients(self) -> Any:
        """
        Handles GET requests to retrieve client types.

        :return: The response from the NodeController's get_clients method.
        :rtype: Any
        :raises HTTPException: If an error occurs while retrieving clients.
        """
        try:
            logger.debug("Handling request to get clients.")
            return await self.node_controller.get_clients()
        except Exception as e:
            logger.error(f"Error in _get_clients: {e}", exc_info=True)
            abort(500, description="Failed to retrieve clients.")

    async def _get_countries(self) -> Any:
        """
        Handles GET requests to retrieve countries.

        :return: The response from the NodeController's get_countries method.
        :rtype: Any
        :raises HTTPException: If an error occurs while retrieving countries.
        """
        try:
            logger.debug("Handling request to get countries.")
            return await self.node_controller.get_countries()
        except Exception as e:
            logger.error(f"Error in _get_countries: {e}", exc_info=True)
            abort(500, description="Failed to retrieve countries.")

    async def _get_isps(self) -> Any:
        """
        Handles GET requests to retrieve ISPs.

        :return: The response from the NodeController's get_isps method.
        :rtype: Any
        :raises HTTPException: If an error occurs while retrieving ISPs.
        """
        try:
            logger.debug("Handling request to get ISPs.")
            return await self.node_controller.get_isps()
        except Exception as e:
            logger.error(f"Error in _get_isps: {e}", exc_info=True)
            abort(500, description="Failed to retrieve ISPs.")

    async def _get_node_ids(self) -> Any:
        """
        Handles GET requests to retrieve distinct node IDs.

        :return: The response from the NodeController's get_node_ids method.
        :rtype: Any
        :raises HTTPException: If an error occurs while retrieving node IDs.
        """
        try:
            logger.debug("Handling request to get distinct node IDs.")
            return await self.node_controller.get_node_ids()
        except Exception as e:
            logger.error(f"Error in _get_node_ids: {e}", exc_info=True)
            abort(500, description="Failed to retrieve node IDs.")

    async def _get_node_details(self, node_id: str) -> Any:
        """
        Handles GET requests to retrieve details of a specific node.

        :param node_id: The identifier of the node to retrieve details for.
        :type node_id: str
        :return: The response from the NodeController's get_node_details method.
        :rtype: Any
        :raises HTTPException: If an error occurs while retrieving node details.
        """
        try:
            logger.debug(f"Handling request to get details for node ID: {node_id}.")
            return await self.node_controller.get_node_details(node_id)
        except Exception as e:
            logger.error(f"Error in _get_node_details: {e}", exc_info=True)
            abort(500, description="Failed to retrieve node details.")

    async def _get_relationships(self, country_name: str) -> Any:
        """
        Handles GET requests to retrieve relationships based on country name.

        :param country_name: The name of the country to filter relationships by.
        :type country_name: str
        :return: The response from the NodeController's get_relationships method.
        :rtype: Any
        :raises HTTPException: If an error occurs while retrieving relationships.
        """
        try:
            logger.debug(f"Handling request to get relationships for country: {country_name}.")
            return await self.node_controller.get_relationships(country_name)
        except Exception as e:
            logger.error(f"Error in _get_relationships: {e}", exc_info=True)
            abort(500, description="Failed to retrieve relationships.")

    async def _get_node_count(self) -> Any:
        """
        Handles GET requests to retrieve the count of nodes.

        :return: The response from the NodeController's get_node_count method.
        :rtype: Any
        :raises HTTPException: If an error occurs while retrieving node count.
        """
        try:
            logger.debug("Handling request to get node count.")
            return await self.node_controller.get_node_count()
        except Exception as e:
            logger.error(f"Error in _get_node_count: {e}", exc_info=True)
            abort(500, description="Failed to retrieve node count.")

    async def _get_latest_nodes(self) -> Any:
        """
        Handles GET requests to retrieve the latest nodes.

        :return: The response from the NodeController's get_latest_nodes method.
        :rtype: Any
        :raises HTTPException: If an error occurs while retrieving latest nodes.
        """
        try:
            logger.debug("Handling request to get latest nodes.")
            return await self.node_controller.get_latest_nodes()
        except Exception as e:
            logger.error(f"Error in _get_latest_nodes: {e}", exc_info=True)
            abort(500, description="Failed to retrieve latest nodes.")

    async def _get_filter_nodes(self) -> Any:
        """
        Handles GET requests to retrieve nodes based on filters.

        :return: The response from the NodeController's get_filter_nodes method.
        :rtype: Any
        :raises HTTPException: If an error occurs while retrieving filtered nodes.
        """
        try:
            logger.debug("Handling request to get filtered nodes.")
            return await self.node_controller.get_filter_nodes()
        except Exception as e:
            logger.error(f"Error in _get_filter_nodes: {e}", exc_info=True)
            abort(500, description="Failed to retrieve filtered nodes.")

    async def _get_statistics(self, data_type: str) -> Any:
        """
        Handles GET requests to retrieve statistics based on data type.

        :param data_type: The type of data for which statistics are requested.
        :type data_type: str
        :return: The response from the NodeController's get_statistics method.
        :rtype: Any
        :raises HTTPException: If an error occurs while retrieving statistics.
        """
        try:
            logger.debug(f"Handling request to get statistics for data type: {data_type}.")
            return await self.node_controller.get_statistics(data_type)
        except Exception as e:
            logger.error(f"Error in _get_statistics: {e}", exc_info=True)
            abort(500, description="Failed to retrieve statistics.")

    def get_blueprint(self) -> Blueprint:
        """
        Returns the registered Blueprint with all routes.

        :return: The Blueprint instance containing all registered routes.
        :rtype: Blueprint
        """
        logger.debug("Returning the Blueprint with all registered routes.")
        return self.node_bp
