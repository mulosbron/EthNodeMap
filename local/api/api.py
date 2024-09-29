import os
from dotenv import load_dotenv
from quart import Quart
from quart_cors import cors
import uvicorn
import logging
from api.routes.node_router import NodeRouter
from api.utils.node_helper import NodeHelper
from api.log.logging_config import LoggingConfig


class ApiServer:
    def __init__(self):
        load_dotenv()
        self.log_level = logging.DEBUG if os.getenv("FLASK_ENV") == "development" else logging.INFO
        self.logger = self.setup_logging()
        self.api = None
        self.host = None
        self.helper = NodeHelper()
        self.app = Quart(__name__)
        self.app = cors(self.app, allow_origin="*")
        self.register_routes()
        self.setup_app_hooks()

    def setup_logging(self):
        """
        Configures the logging system using the LoggingConfig class.

        :return: Configured logger instance.
        """
        logging_config = LoggingConfig()
        logger = logging_config.configure_logging()
        logger.setLevel(self.log_level)
        return logger

    def register_routes(self):
        """
        Registers the routes for the application by attaching the blueprint from NodeRoutes.
        """
        node_router = NodeRouter()
        self.app.register_blueprint(node_router.get_blueprint())

    def setup_app_hooks(self):
        """
        Sets up various lifecycle hooks for the application.
        """
        @self.app.before_serving
        async def startup():
            self.logger.info("::setup_app_hooks::Application startup complete.")

    def start_server(self):
        """
        Starts the Uvicorn server to run the Quart application.
        """
        host, port = self.helper.get_valid_host_and_port()
        uvicorn.run(self.app, host=host, port=port)


if __name__ == '__main__':
    server = ApiServer()
    server.start_server()
