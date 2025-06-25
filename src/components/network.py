from sequence.kernel.timeline import Timeline
from sequence.topology.topology import Node, BSMNode

import networkx as nx

from .topologies import TopologyGen

from typing import Type


class Network:
    def __init__(self) -> None:
        self.timeline: Timeline = Timeline()
        self.topology: str
        self.graph: nx.Graph
        self.nodes: dict[int, Type[Node]]
        self.number_of_nodes: int
        self.bsm_nodes: dict[tuple[int, int], BSMNode]
        self.topology_generator = TopologyGen(self)

    def draw(self, labels: bool = True) -> None:
        """
        Draw the graph (Only can show on jupyter)

        Args:
            labels (bool): Bool to show labels
        """
        nx.draw(self.graph, with_labels=labels)

    def edges(self) -> list[tuple[int, int]]:
        return self.graph.edges()
    
    def update_nodes(self, nodes: dict[int, Type[Node]]) -> None:
        self.nodes = nodes

    def update_topology(self, topology_name: str) -> None:
        self.topology = topology_name

    def update_graph(self, graph: nx.Graph) -> None:
        self.graph = graph

    def update_number_of_nodes(self, number_of_nodes: int) -> None:
        self.number_of_nodes = number_of_nodes

    def update_bsm_nodes(self, bsm_nodes: dict[tuple[int, int], BSMNode]) -> None:
        self.bsm_nodes = bsm_nodes