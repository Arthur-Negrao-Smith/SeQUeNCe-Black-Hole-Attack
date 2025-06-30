from sequence.kernel.timeline import Timeline
from sequence.topology.topology import Node, BSMNode

import networkx as nx

from components.nodes import QuantumRepeater
from components.utils.enums import Topologies

from typing import Optional
import logging

log: logging.Logger = logging.getLogger(__name__)

class Network:
    """
    Network class to create the quantum network
    """
    def __init__(self, topology: Topologies, start_seed: Optional[int] = None) -> None:
        """
        Network constructor

        Args:
            topology (Topologies): Topology to build
            start_seed (Optional[int]): Seed to replicate the simulation. Default is None
        """ 
        self.timeline: Timeline = Timeline()
       
        self.number_of_nodes: int
        self.nodes: dict[int, QuantumRepeater] = dict()
        self.normal_nodes: dict[int, QuantumRepeater] = dict()
        self.black_holes: dict[int, QuantumRepeater] = dict()
        self.bsm_nodes: dict[tuple[int, int], BSMNode] = dict()
        
        from .topologies import TopologyGen
        self.topology: Topologies = topology
        self.graph: nx.Graph
        self.topology_generator = TopologyGen(self, start_seed=start_seed)

        from components.network_manager import Network_Manager
        self.network_manager: Network_Manager = Network_Manager(self)

        log.debug("Initiated Network")

    def draw(self, labels: bool = True) -> None:
        """
        Draw the graph (Only can show on jupyter)

        Args:
            labels (bool): Bool to show labels
        """
        nx.draw(self.graph, with_labels=labels)

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

    def update_topology(self, topology_name: Topologies) -> None:
        """
        Update the network's topology_name 

        Args:
            topology_name (Topologies): New topology to updates
        """
        self.topology = topology_name

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

    def get_black_holes(self) -> dict[str, dict[str, float | int] | None]:
        """
        Get black holes and targets

        Returns:
            dict[str, dict[str, float | int] | None]: Dict with black holes' name and your targets
        """
        tmp_bh_dict: dict[str, dict[str, float | int] | None] = dict()
        for bh in self.black_holes.values():
            tmp_bh_dict[bh.name] = bh._black_hole_targets

        return tmp_bh_dict
    
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