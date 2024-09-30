import os
from datetime import datetime
import logging


class NodeHelper:
    def __init__(self):
        self.logger = logging.getLogger('quart_app.utils.node_helper')

    def is_hexadecimal(self, s):
        """
        Checks if a string is in hexadecimal format.

        :param s: The string to check.
        :return: True if the string is hexadecimal, False otherwise.
        """
        self.logger.debug(f"::Entering is_hexadecimal:: with argument: s='{s}'")
        try:
            int(s, 16)
            self.logger.info(f"::is_hexadecimal:: String '{s}' is a valid hexadecimal.")
            self.logger.debug("::Exiting is_hexadecimal:: with result: True")
            return True
        except ValueError as e:
            self.logger.warning(f"::is_hexadecimal:: String '{s}' is not a valid hexadecimal. Exception: {e}")
            self.logger.debug("::Exiting is_hexadecimal:: with result: False")
            return False

    def _create_enode(self, record):
        """
        Creates the enode format from a record.

        :param record: A dictionary containing node details.
        :return: The formatted enode string if successful, None otherwise.
        """
        self.logger.debug(f"::Entering create_enode:: with record: {record}")
        try:
            node_id = record['NodeId']
            host = record['Host']
            port = record['Port']
            self.logger.debug(f"::create_enode:: Extracted NodeId: {node_id}, Host: {host}, Port: {port}")
            enode = f"enode://{node_id}@{host}:{port}"
            self.logger.info(f"::create_enode:: Successfully created enode: {enode}")
            self.logger.debug("::Exiting create_enode:: with enode")
            return enode
        except KeyError as e:
            self.logger.critical(f"::create_enode:: Missing key in record when creating enode: {e}")
            self.logger.debug("::Exiting create_enode:: with error due to missing key")
            raise KeyError(f"Missing key in record: {e}") from e
        except TypeError as e:
            self.logger.critical(f"::create_enode:: Invalid type in record when creating enode: {e}")
            self.logger.debug("::Exiting create_enode:: with error due to invalid type")
            raise TypeError(f"Invalid type in record: {e}") from e

    def _calculate_minutes_ago(self, current_time, created_at):
        """
        Calculates the minutes between two datetime objects.

        :param current_time: The current datetime.
        :param created_at: The datetime to compare against.
        :return: The number of minutes between current_time and created_at.
        """
        self.logger.debug(f"::Entering calculate_minutes_ago:: with current_time: {current_time}, created_at: {created_at}")
        delta = current_time - created_at
        minutes_ago = int(delta.total_seconds() / 60)
        self.logger.info(f"::calculate_minutes_ago:: Calculated time difference: {minutes_ago} minutes ago.")
        self.logger.debug("::Exiting calculate_minutes_ago:: with result")
        return minutes_ago

    def _create_node_data(self, record, enode, minutes_ago):
        """
        Returns desired information from a node record.

        :param record: A dictionary containing node details.
        :param enode: The enode string.
        :param minutes_ago: Minutes elapsed since the node was created.
        :return: A dictionary with selected node information.
        """
        self.logger.debug(
            f"::Entering create_node_data:: with record: {record}, enode: {enode}, minutes_ago: {minutes_ago}")
        node_data = {
            "Country": record.get("Country", "Unknown"),
            "Client": record.get("Client", "Unknown"),
            "OS": record.get("OS", "Unknown"),
            "ISP": record.get("ISP", "Unknown"),
            "Enode": enode,
            "MinutesAgo": minutes_ago
        }
        self.logger.info(f"::create_node_data:: Node data prepared: {node_data}")
        self.logger.debug("::Exiting create_node_data:: with node_data")
        return node_data

    def process_nodes(self, result):
        """
        Processes the node results and returns a list of formatted node data.

        :param result: A list of node records from the database.
        :return: A list of processed node data dictionaries.
        """
        self.logger.debug(f"::Entering process_nodes:: with result: {result}")
        nodes = []
        current_time = datetime.now()
        self.logger.debug(f"::process_nodes:: Current time set to: {current_time}")
        try:
            for record in result:
                self.logger.debug(f"::process_nodes:: Processing record: {record}")
                enode = self._create_enode(record)
                if not enode:
                    self.logger.warning(
                        f"::process_nodes:: Skipping record {record.get('NodeId', 'Unknown')} due to enode creation failure.")
                    continue
                created_at_str = record.get("CreatedAt")
                if not created_at_str:
                    self.logger.warning(f"::process_nodes:: Record {record.get('NodeId', 'Unknown')} has no 'CreatedAt' field.")
                    continue
                try:
                    created_at = datetime.fromisoformat(created_at_str)
                    self.logger.debug(f"::process_nodes:: Parsed 'CreatedAt' to datetime: {created_at}")
                except ValueError as ve:
                    self.logger.error(f"::process_nodes:: Invalid date format for record {record.get('NodeId', 'Unknown')}: {ve}")
                    continue
                minutes_ago = self._calculate_minutes_ago(current_time, created_at)
                node_data = self._create_node_data(record, enode, minutes_ago)
                nodes.append(node_data)
                self.logger.debug(f"::process_nodes:: Appended node data to list: {node_data}")
            self.logger.info(f"::process_nodes:: Processed {len(nodes)} nodes successfully.")
            self.logger.debug("::Exiting process_nodes:: with nodes list")
            return nodes
        except Exception as e:
            self.logger.exception(f"::process_nodes:: Error processing nodes: {e}")
            self.logger.debug("::Exiting process_nodes:: with error")

    def process_relationships(self, result):
        """
        Processes the given relationships and returns a list or an error message.

        :param result: The relationships data or an error dictionary.
        :return: Processed relationships or an error message.
        """
        self.logger.debug(f"::Entering process_relationships:: with result: {result}")
        try:
            if isinstance(result, dict) and "error" in result:
                self.logger.error(f"::process_relationships:: Error in relationships result: {result['error']}")
                self.logger.debug("::Exiting process_relationships:: with error")
                return result
            processed_relationships = [record for record in result]
            self.logger.info(f"::process_relationships:: Processed {len(processed_relationships)} relationships successfully.")
            self.logger.debug("::Exiting process_relationships:: with processed_relationships")
            return processed_relationships
        except Exception as e:
            self.logger.exception(f"::process_relationships:: Error processing relationships: {e}")
            self.logger.debug("::Exiting process_relationships:: with error")

    def get_valid_host_and_port(self):
        """
        Retrieves valid host and port values from environment variables. Returns default values if not set.

        :return: A tuple containing the host (str) and port (int).
        """
        self.logger.debug("::Entering get_valid_host_and_port::")
        try:
            host = os.getenv("APP_HOST", "127.0.0.1")
            port_str = os.getenv("APP_PORT", "5001")
            self.logger.debug(f"::get_valid_host_and_port:: Retrieved host from environment: {host}")
            self.logger.debug(f"::get_valid_host_and_port:: Retrieved port string from environment: {port_str}")
            port = int(port_str)
            self.logger.debug(f"::get_valid_host_and_port:: Converted port string to integer: {port}")
            if not (0 <= port <= 65535):
                self.logger.critical(f"::get_valid_host_and_port:: Port number {port} is out of valid range (0-65535). Using default port 5001.")
                port = 5001
            self.logger.info(f"::get_valid_host_and_port:: Using host and port: {host}:{port}")
            self.logger.debug("::Exiting get_valid_host_and_port:: with host and port")
            return host, port
        except ValueError as ve:
            self.logger.critical(f"::get_valid_host_and_port:: Invalid port number in environment: {ve}")
            self.logger.debug("::Exiting get_valid_host_and_port:: with error due to invalid port")
            raise
