from datetime import datetime
from quart import abort
import os
import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger('quart_app.utils.node_helper')


class NodeHelper:
    @staticmethod
    def is_hexadecimal(s: str) -> bool:
        """
        Checks if a string is in hexadecimal format.

        :param s: The string to check.
        :return: True if the string is hexadecimal, False otherwise.
        """
        try:
            int(s, 16)
            logger.debug(f"String '{s}' is hexadecimal.")
            return True
        except ValueError:
            logger.debug(f"String '{s}' is not hexadecimal.")
            return False

    @staticmethod
    def create_enode(record: Dict[str, Any]) -> Optional[str]:
        """
        Creates the enode format from a record.

        :param record: A dictionary containing node details.
        :return: The formatted enode string if successful, None otherwise.
        :raises KeyError: If required keys are missing in the record.
        :raises TypeError: If the values for 'NodeId', 'Host', or 'Port' are not of expected types.
        """
        try:
            node_id = record['NodeId']
            host = record['Host']
            port = record['Port']
            enode = f"enode://{node_id}@{host}:{port}"
            logger.debug(f"Created enode: {enode}")
            return enode
        except KeyError as e:
            logger.error(f"Missing key in record when creating enode: {e}")
            raise KeyError(f"Missing key in record: {e}") from e
        except TypeError as e:
            logger.error(f"Invalid type in record when creating enode: {e}")
            raise TypeError(f"Invalid type in record: {e}") from e

    @staticmethod
    def calculate_minutes_ago(current_time: datetime, created_at: datetime) -> int:
        """
        Calculates the minutes between two datetime objects.

        :param current_time: The current datetime.
        :param created_at: The datetime to compare against.
        :return: The number of minutes between current_time and created_at.
        """
        delta = current_time - created_at
        minutes_ago = int(delta.total_seconds() / 60)
        logger.debug(f"Calculated minutes ago: {minutes_ago} minutes.")
        return minutes_ago

    @staticmethod
    def create_node_data(record: Dict[str, Any], enode: str, minutes_ago: int) -> Dict[str, Any]:
        """
        Returns desired information from a node record.

        :param record: A dictionary containing node details.
        :param enode: The enode string.
        :param minutes_ago: Minutes elapsed since the node was created.
        :return: A dictionary with selected node information.
        """
        node_data = {
            "Country": record.get("Country", "Unknown"),
            "Client": record.get("Client", "Unknown"),
            "OS": record.get("OS", "Unknown"),
            "ISP": record.get("ISP", "Unknown"),
            "Enode": enode,
            "MinutesAgo": minutes_ago
        }
        logger.debug(f"Created node data: {node_data}")
        return node_data

    def process_nodes(self, result: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes the node results and returns a list of formatted node data.

        :param result: A list of node records from the database.
        :return: A list of processed node data dictionaries.
        :raises Exception: If an error occurs during processing nodes.
        """
        nodes = []
        current_time = datetime.now()

        if not result:
            logger.error("Empty result set provided for processing nodes.")
            abort(400, description="No node data available for processing.")

        try:
            for record in result:
                enode = self.create_enode(record)
                if not enode:
                    logger.warning(f"Skipping record {record.get('NodeId', 'Unknown')} due to enode creation failure.")
                    continue

                created_at_str = record.get("CreatedAt")
                if not created_at_str:
                    logger.warning(f"Record {record.get('NodeId', 'Unknown')} has no 'CreatedAt' field.")
                    continue

                try:
                    created_at = datetime.fromisoformat(created_at_str)
                except ValueError as ve:
                    logger.error(f"Invalid date format for record {record.get('NodeId', 'Unknown')}: {ve}")
                    continue

                minutes_ago = self.calculate_minutes_ago(current_time, created_at)
                node_data = self.create_node_data(record, enode, minutes_ago)
                nodes.append(node_data)

            logger.info(f"Processed {len(nodes)} nodes successfully.")
            return nodes

        except Exception as e:
            logger.error(f"Error processing nodes: {e}", exc_info=True)
            abort(500, description="An error occurred while processing nodes.")

    @staticmethod
    def process_relationships(result: Union[List[Dict[str, Any]], Dict[str, Any]]) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Processes the given relationships and returns a list or an error message.

        :param result: The relationships data or an error dictionary.
        :return: Processed relationships or an error message.
        :raises Exception: If an unexpected error occurs during processing relationships.
        """
        try:
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Error in relationships result: {result['error']}")
                return result
            processed_relationships = [record for record in result]
            logger.info(f"Processed {len(processed_relationships)} relationships successfully.")
            return processed_relationships
        except Exception as e:
            logger.error(f"Error processing relationships: {e}", exc_info=True)
            abort(500, description="Failed to process relationships.")

    @staticmethod
    def get_valid_host_and_port() -> (str, int):
        """
        Retrieves valid host and port values from environment variables. Returns default values if not set.

        :return: A tuple containing the host (str) and port (int).
        :raises ValueError: If the port environment variable cannot be converted to an integer.
        """
        host = os.getenv('HOST', '127.0.0.1')
        port = os.getenv('PORT', 5001)
        try:
            logger.debug(f"Retrieved host and port from environment: {host}:{port}")
            return host, port
        except ValueError:
            logger.error(f"Invalid port number in environment: {port_str}")
            abort(500, description="Invalid port number in environment variables.")
