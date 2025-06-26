from sequence.kernel.timeline import Timeline
from sequence.topology.topology import Node, BSMNode

import networkx as nx

from components.nodes import QuantumRepeater
from components.utils.enums import Topologies

from typing import Type, Union


class Network:
    def __init__(self, topology: Topologies, start_seed: Union[None, int] = None) -> None:
        from .topologies import TopologyGen
        
        self.timeline: Timeline = Timeline()
       
        self.number_of_nodes: int
        self.nodes: dict[int, QuantumRepeater]
        self.bsm_nodes: dict[tuple[int, int], BSMNode]
        
        self.topology: Topologies = topology
        self.graph: nx.Graph
        self.topology_generator = TopologyGen(self, start_seed=start_seed)

    def draw(self, labels: bool = True) -> None:
        """
        Draw the graph (Only can show on jupyter)

        Args:
            labels (bool): Bool to show labels
        """
        nx.draw(self.graph, with_labels=labels)

    def edges(self) -> list[tuple[int, int]]:
        return self.graph.edges()
    
    def update_nodes(self, nodes: dict[int, QuantumRepeater]) -> None:
        self.nodes = nodes

    def update_topology(self, topology_name: Topologies) -> None:
        self.topology = topology_name

    def update_graph(self, graph: nx.Graph) -> None:
        self.graph = graph

    def update_number_of_nodes(self, number_of_nodes: int) -> None:
        self.number_of_nodes = number_of_nodes

    def update_bsm_nodes(self, bsm_nodes: dict[tuple[int, int], BSMNode]) -> None:
        self.bsm_nodes = bsm_nodes