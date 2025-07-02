# Data constants
from typing import Any


REQUESTS: str = "requests"
CONSUMED_EPRS: str = "consumed_eprs"
TOTAL_ROUTE_FIDELITY: str = "total_route_fidelity"
TOTAL_SUCCESS: str = "total_success"
TOTAL_FAILS: str = "total_fails"
TOTAL_NO_PATHS: str = "total_no_paths"
TOTAL_ROUTE_LENGTH: str = "total_route_length"
TOTAL_REQUEST_ATTEMPTS: str = "total_request_attempts" 
NUMBER_OF_NODES: str = "number_of_nodes"
TOTAL_ENTANGLEMENT_ATTEMPTS: str = "total_entanglement_attempts"
TOPOLOGY: str = "topology"
BLACK_HOLES: str = "black_holes"



class Network_Data:
    def __init__(self) -> None:
        self._data: dict = {
            REQUESTS:0, 
            CONSUMED_EPRS:0, 
            TOTAL_ROUTE_FIDELITY:0, 
            TOTAL_SUCCESS:0, 
            TOTAL_FAILS:0, 
            TOTAL_NO_PATHS:0, 
            TOTAL_ROUTE_LENGTH:0, 
            TOTAL_REQUEST_ATTEMPTS:0, 
            NUMBER_OF_NODES:0, 
            TOTAL_ENTANGLEMENT_ATTEMPTS:0, 
            TOPOLOGY:"not defined", 
            BLACK_HOLES:[]
        }

    def increment(self, key: str, increment_number: int) -> None:
        """
        Increment any data's number

        Args:
            key (str): Key to access data
            increment_number (int): Number to add
        """
        self._data[key] += increment_number

    def change_string(self, key: str, string: str) -> None:
        """
        Change any data's string

        Args:
            key (str): Key to access data
            string (str): String to updates data
        """
        self._data[key] = string

    def change_list(self, key: str, new_list: list) -> None:
        """
        Change any data's list

        Args:
            key (str): Key to access data
            new_list (list): List to updates data
        """
        self._data[key] = new_list

    def get_item(self, item_name) -> Any:
        """
        Get any data's item

        Args:
           item_name (str): Key to access data

        Returns:
            Any: Any data item
        """
        return self._data[item_name]

    def get_all_data(self) -> dict:
        """
        Get data in a dict

        Returns:
            dict: Dict with all data
        """
        return self._data
    