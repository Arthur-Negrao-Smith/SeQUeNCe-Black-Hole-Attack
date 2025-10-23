from .utils.enums import Attack_Types, Topologies

from typing import Any

# Dict keys
REQUESTS: str = "Requests"
CONSUMED_EPRS: str = "Consumed EPRs"
NUMBER_OF_NODES: str = "Number of Nodes"
TOTAL_ROUTE_FIDELITY: str = "Total Route Fidelity"
TOTAL_REQUEST_SUCCESS: str = "Total Request Success"
TOTAL_REQUEST_FAILS: str = "Total Request Fails"
TOTAL_NO_PATHS: str = "Total No Paths"
TOTAL_ROUTE_LENGTH: str = "Total Route Length"
TOTAL_REQUEST_ATTEMPTS: str = "Total Request Attempts"
TOTAL_ENTANGLEMENT_ATTEMPTS: str = "Total Entanglement Attempts"
TOTAL_SWAPPING_ATTEMPTS: str = "Total Swapping Attempts"
TOTAL_SWAPPING_SUCCESS: str = "Total Swapping Success"
TOTAL_SWAPPING_FAILS: str = "Total Swapping Fails"
TOPOLOGY: str = "Topology"
NUMBER_OF_BLACK_HOLES: str = "Black Holes"
TARGETS_PER_BLACK_HOLE: str = "Targets per Black Hole"
SIMULATION_TIME: str = "Simulation Time"
ATTACK_TYPE: str = "Attack Type"
PARAMETER: str = "Parameter"
BLACK_HOLE_SWAP_PROB: str = "Black Hole Swap Prob"
NORMAL_NODE_SWAP_PROB: str = "Normal Node Swap Prob"
INTENSITY: str = "Intensity"


class Network_Data:
    """
    Data to storage in Network
    """

    def __init__(self) -> None:
        """
        Constructor for Network_Data
        """
        self._data: dict = {
            REQUESTS: [0],
            CONSUMED_EPRS: [0],
            TOTAL_ROUTE_FIDELITY: [0],
            TOTAL_REQUEST_SUCCESS: [0],
            TOTAL_REQUEST_FAILS: [0],
            TOTAL_NO_PATHS: [0],
            TOTAL_ROUTE_LENGTH: [0],
            TOTAL_REQUEST_ATTEMPTS: [0],
            TOTAL_ENTANGLEMENT_ATTEMPTS: [0],
            TOTAL_SWAPPING_ATTEMPTS: [0],
            TOTAL_SWAPPING_SUCCESS: [0],
            TOTAL_SWAPPING_FAILS: [0],
            NUMBER_OF_NODES: [0],
            TOPOLOGY: [Topologies.NOT_DEFINED.value],
            SIMULATION_TIME: [0],
            NUMBER_OF_BLACK_HOLES: [0],
            TARGETS_PER_BLACK_HOLE: [0],
            ATTACK_TYPE: [Attack_Types.NO_ATTACK.value],
            PARAMETER: [-1.0],
            BLACK_HOLE_SWAP_PROB: [-1.0],
            NORMAL_NODE_SWAP_PROB: [-1.0],
            INTENSITY: ["i: -1.0"],
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
        self._data[key][0] += increment_number

    def change_value(self, key: str, new_value: int | float | str) -> None:
        """
        Change a value in network_data

        Args:
            key (str): Key to access data
            new_value (int | float | str): New value to replace
        """
        self._data[key][0] = new_value

    def get_item(self, item_name) -> Any:
        """
        Get any data's item

        Args:
           item_name (str): Key to access data

        Returns:
            Any: Any data item
        """
        return self._data[item_name][0]

    def get_all_data(self) -> dict:
        """
        Get data in a dict

        Returns:
            dict: Dict with all data
        """
        return self._data
