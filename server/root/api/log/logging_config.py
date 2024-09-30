import logging
from logging.handlers import RotatingFileHandler
import os


class LoggingConfig:

    def __init__(self):
        self.logger = logging.getLogger('quart_app')
        self.logger.setLevel(logging.DEBUG)
        self.console_handler = None
        self.file_handler = None
        self.log_directory = None

    def _create_log_directory(self):
        """
        Creates the log directory if it does not exist.
        """
        self.log_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

    def _console_handler_setup(self):
        """
        Sets up the console handler with appropriate level and formatter.
        """
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.console_handler.setFormatter(console_formatter)

    def _file_handler_setup(self):
        log_file = os.path.join(self.log_directory, 'app.log')
        self.file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
        self.file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.file_handler.setFormatter(file_formatter)

    def configure_logging(self):
        """
        Configures the logging system for the application.

        :return: Configured logger instance.
        """
        self._create_log_directory()
        self._console_handler_setup()
        self._file_handler_setup()
        if not self.logger.handlers:
            self.logger.addHandler(self.console_handler)
            self.logger.addHandler(self.file_handler)
        return self.logger
