from sequence.kernel.timeline import Timeline
from sequence.topology.topology import BSMNode

from .nodes import QuantumRepeater
from .utils.enums import Topologies
from .utils.logger import show_logs
import components.network_data as nd

import networkx as nx
from typing import Optional
import logging

log: logging.Logger = logging.getLogger(__name__)

class Network:
    """
    Network class to create the quantum network
    """
    def __init__(self, start_seed: Optional[int] = None, display_logs: bool = False) -> None:
        """
        Network constructor

        Args:
            start_seed (Optional[int]): Seed to replicate the simulation. Default is None
            display_logs (bool): Show all logs
        """ 

        if display_logs:
            show_logs()

        self.timeline: Timeline = Timeline()

        self.number_of_nodes: int

        self.nodes: dict[int, QuantumRepeater] = dict()
        self.normal_nodes: dict[int, QuantumRepeater] = dict()
        self.black_holes: dict[int, QuantumRepeater] = dict()
        self.bsm_nodes: dict[tuple[int, int], BSMNode] = dict()

        from .topologies import TopologyGen
        self.graph: nx.Graph
        self.topology: Topologies
        self._topology_generator: Optional[TopologyGen] = TopologyGen(self, start_seed=start_seed)

        from .network_manager import Network_Manager
        self._network_manager: Optional[Network_Manager] = Network_Manager(self)

        from .attack_manager import Attack_Manager
        self._attack_manager: Optional[Attack_Manager] = Attack_Manager(self)

        from .network_data import Network_Data
        self._network_data: Optional[Network_Data] = Network_Data()

        log.debug("Initiated Network")
    
    def destroy(self) -> None:
        """
        Cleanup all references
        """
        if self._topology_generator is not None:
            self._topology_generator.destroy()
            self._topology_generator = None

        if self._network_manager is not None:
            self._network_manager.destroy()
            self._network_manager = None

        if self._attack_manager is not None:
            self._attack_manager.destroy()
            self._attack_manager = None

        if self._network_data is not None:
            self._network_data.clear()
            self._network_data = None

        self.nodes.clear()
        self.normal_nodes.clear()
        self.black_holes.clear()
        self.bsm_nodes.clear()

    def draw(self, labels: bool = True) -> None:
        """
        Draw the graph (Only can show on jupyter)

        Args:
            labels (bool): Bool to show labels
        """
        nx.draw(self.graph, with_labels=labels)

    @property
    def topology_generator(self):
        if self._topology_generator is None:
            raise RuntimeError("Topology generator has been destroyed")
        return self._topology_generator
    
    @property
    def network_manager(self):
        if self._network_manager is None:
            raise RuntimeError("Network manager has been destroyed")
        return self._network_manager
    
    @property
    def attack_manager(self):
        if self._attack_manager is None:
            raise RuntimeError("Attack manager has been destroyed")
        return self._attack_manager
    
    @property
    def network_data(self):
        if self._network_data is None:
            raise RuntimeError("Network data has been destroyed")
        return self._network_data

    def edges(self) -> list[tuple[int, int]]:
        """
        Return the graph's edges

        Returns:
            list[tuple[int, int]]: List with all edges
        """
        return self.graph.edges()

    def update_nodes(self, nodes: dict[int, QuantumRepeater]) -> None:
        """
        Update the network's nodes 

        Args:
            nodes (dict[int, QuantumRepeater]): New nodes to attach
        """
        self.nodes = nodes

    def update_topology(self, topology: Topologies) -> None:
        """
        Update the network's topology_name 

        Args:
            topology (Topologies): New topology to updates
        """
        self.topology = topology

        # update network's data
        self.network_data.change_string(key=nd.TOPOLOGY, new_string=nd.TOPOLOGIES_DICT[topology])

    def update_graph(self, graph: nx.Graph) -> None:
        """
        Update the network's graph 

        Args:
            graph (nx.Graph): New graph to updates
        """
        self.graph = graph

    def update_number_of_nodes(self, number_of_nodes: int) -> None:
        """
        Update the network's number of nodes

        Args:
            number_of_nodes (int): New number of nodes to updates
        """
        self.number_of_nodes = number_of_nodes

        # updates network's data
        self.network_data.change_number(key=nd.NUMBER_OF_NODES, new_number=number_of_nodes)

    def update_normal_nodes(self, normal_nodes: dict[int, QuantumRepeater]) -> None:
        """
        Update the network's normal nodes

        Args:
            normal_nodes (dict[int, QuantumRepeater]): Normal nodes to update
        """
        self.normal_nodes = normal_nodes

    def update_bsm_nodes(self, bsm_nodes: dict[tuple[int, int], BSMNode]) -> None:
        """
        Update the network's bsm nodes

        Args:
            bsm_nodes (dict[tuple[int, int], BSMNode]): New BSM
        """
        self.bsm_nodes = bsm_nodes

    def get_bsm_node(self, nodeA_id: int, nodeB_id: int) -> BSMNode | None:
        """
        Get the bsm node attached in nodeA and nodeB

        Args:
            nodeA_id (int): Node attached in bsm
            nodeB_id (int): Anothe node attached in bsm

        Returns:
            Union[BSMNode, None]: Returns None if bsm doesn't exists, else return BSMNode
        """
        if (nodeA_id, nodeB_id) in self.bsm_nodes.keys():
            return self.bsm_nodes[(nodeA_id, nodeB_id)]
        if (nodeB_id, nodeA_id) in self.bsm_nodes.keys():
            return self.bsm_nodes[(nodeB_id, nodeA_id)]

        return None

    def _run(self) -> None:
        """
        Run network's events
        """
        self.timeline.run()

    def _increment_time(self, time_to_increment: float | int) -> None:
        """
        Increment network's time to run events

        Args:
            time_to_increment (float | int): Time to increment in network's time
        """
        self.timeline.time = self.timeline.now() + time_to_increment

        # updates network's data
        self.network_data.increment(key=nd.SIMULATION_TIME, increment_number=time_to_increment)
