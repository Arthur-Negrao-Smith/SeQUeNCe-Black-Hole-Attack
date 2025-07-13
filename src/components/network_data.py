from .utils.enums import Attack_Types, Topologies

from typing import Any

# for translate enum to string
TOPOLOGIES_DICT: dict[Topologies, str] = {
    Topologies.BARABASI_ALBERT:'Barabási-Albert',
    Topologies.ERDOS_RENYI:'Erdős–Rényi',
    Topologies.GRID:'Grid',
    Topologies.LINE:'Line',
    Topologies.RING:'Ring',
    Topologies.STAR:'Star'
}

# for translate enum to string
ATTACKS_DICT: dict[Attack_Types, str] = {
    Attack_Types.BLACK_HOLE:'Black-hole',
    Attack_Types.HIJACKING:"Hijacking"
}

# Dict keys
REQUESTS: str = "requests"
CONSUMED_EPRS: str = "consumed_eprs"
TOTAL_ROUTE_FIDELITY: str = "total_route_fidelity"
TOTAL_REQUEST_SUCCESS: str = "total_request_success"
TOTAL_REQUEST_FAILS: str = "total_request_fails"
TOTAL_NO_PATHS: str = "total_no_paths"
TOTAL_ROUTE_LENGTH: str = "total_route_length"
TOTAL_REQUEST_ATTEMPTS: str = "total_request_attempts" 
NUMBER_OF_NODES: str = "number_of_nodes"
TOTAL_ENTANGLEMENT_ATTEMPTS: str = "total_entanglement_attempts"
TOTAL_SWAPPING_ATTEMPTS: str = "total_swapping_attempts"
TOTAL_SWAPPING_SUCCESS: str = "total_swapping_success"
TOTAL_SWAPPING_FAILS: str = "total_swapping_fails"
TOPOLOGY: str = "topology"
NUMBER_OF_BLACK_HOLES: str = "black_holes"
TARGETS_PER_BLACK_HOLE: str = "targets_per_black_hole"
SIMULATION_TIME: str = 'simulation_time'
ATTACK_NAME: str = 'attack_name'

class Network_Data:
    """
    Data to storage in Network
    """
    def __init__(self) -> None:
        """
        Constructor for Network_Data
        """
        self._data: dict = {
            REQUESTS:0, 
            CONSUMED_EPRS:0, 
            TOTAL_ROUTE_FIDELITY:0, 
            TOTAL_REQUEST_SUCCESS:0, 
            TOTAL_REQUEST_FAILS:0, 
            TOTAL_NO_PATHS:0, 
            TOTAL_ROUTE_LENGTH:0, 
            TOTAL_REQUEST_ATTEMPTS:0, 
            TOTAL_ENTANGLEMENT_ATTEMPTS:0, 
            TOTAL_SWAPPING_ATTEMPTS:0,
            TOTAL_SWAPPING_SUCCESS:0,
            TOTAL_SWAPPING_FAILS:0,
            NUMBER_OF_NODES:0, 
            TOPOLOGY:"Not defined", 
            SIMULATION_TIME:0,
            NUMBER_OF_BLACK_HOLES:0,
            TARGETS_PER_BLACK_HOLE:0,
            ATTACK_NAME:"No attack",
        }

    def clear(self) -> None:
        """
        Clean all data
        """
        self._data.clear()

    def increment(self, key: str, increment_number: int | float = 1) -> None:
        """
        Increment any data's number

        Args:
            key (str): Key to access data
            increment_number (int | float): Number to add
        """
        self._data[key] += increment_number

    def change_number(self, key: str, new_number: int | float) -> None:
        """
        Increment any data's number

        Args:
            key (str): Key to access data
            new_number (int | float): Number to updates data
        """
        self._data[key] = new_number

    def change_string(self, key: str, new_string: str) -> None:
        """
        Change any data's string

        Args:
            key (str): Key to access data
            string (str): String to updates data
        """
        self._data[key] = new_string

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
