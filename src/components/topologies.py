from sequence.topology.topology import Node, BSMNode, SingleAtomBSM
from sequence.components.optical_channel import ClassicalChannel, QuantumChannel

from .utils.constants import BSM_EFFICIENCY, QCHANNEL_ATTENUATION, QCHANNEL_DISTANCE, CCHANNEL_DISTANCE, CCHANNEL_DELAY, ENTANGLEMENT_SWAPPING_PROB
from .utils.enums import Topologies, Node_Types
from .nodes import QuantumRepeater

import networkx as nx
from typing import Type, Union

# Topologies generator
class TopologyGen:
    from .network import Network
    def __init__(self, network: Network, start_seed: Union[None, int] = None):
        
        self.network: Network = network

        self.seed: None | int = start_seed

    def _create_nodes(self, number_of_nodes: int) -> dict[int, QuantumRepeater]:
        """
        Create all grid nodes and return them in a dictionary

        Args:
            number_of_nodes (int): Number of nodes on the network

        Returns:
            dict[int, QuantumRepeater]: A dictionary where each key is a unique 
            integer node ID, and each value is the corresponding node instance placed in the grid.
        """

        nodes: dict[int, QuantumRepeater] = dict()
        for c in range(0, number_of_nodes):
            tmp_node: QuantumRepeater = QuantumRepeater(name=f"node{c}", timeline=self.network.timeline, swap_prob=ENTANGLEMENT_SWAPPING_PROB)

            if self.seed is not None:
                tmp_node.set_seed(self.seed)
                self.seed += 1
            nodes[c] = tmp_node
        
        self.network.update_number_of_nodes(number_of_nodes)
        self.network.update_nodes(nodes)

        return nodes

    def _create_BSMNode(self, nodeA_id: int, nodeB_id: int, edge: tuple[int, int]) -> BSMNode:

        bsm_node: BSMNode = BSMNode(name=f'bsm_node({nodeA_id}, {nodeB_id})', timeline=self.network.timeline,
                                        other_nodes=[f'node{nodeA_id}', f'node{nodeB_id}'])
        if self.seed is not None:
            bsm_node.set_seed(self.seed)
            self.seed += 1
        
        self.network.bsm_nodes[edge] = bsm_node # adding bsm node in a dict
        bsm: SingleAtomBSM = bsm_node.get_components_by_type("SingleAtomBSM")[0] # <- Get the bsm without node
        bsm.update_detectors_params('efficiency', BSM_EFFICIENCY) # <- Change the detector efficiency

        return bsm_node

    def _connect_quantum_channels(self, nodeA_id: int, nodeB_id: int, bsm_node: BSMNode, 
                                  qc_attenuation: int, qc_distance: int) -> None:
            # Quantum channel initiation
            qc1 = QuantumChannel(name=f'qc({self.network.nodes[nodeA_id].name}, {bsm_node.name})',
                                  timeline=self.network.timeline,
                                attenuation=qc_attenuation, distance=qc_distance)
            qc2 = QuantumChannel(name=f'qc({bsm_node.name}, {self.network.nodes[nodeB_id].name})', timeline=self.network.timeline,
                                attenuation=qc_attenuation, distance=qc_distance)

            qc1.set_ends(self.network.nodes[nodeA_id], bsm_node.name)
            qc2.set_ends(self.network.nodes[nodeB_id], bsm_node.name)

    def _connect_classical_channels(self, cc_distance: int, cc_delay: int) -> None:
        nodes: list[QuantumRepeater | BSMNode] = list(self.network.nodes.values())
        nodes += list(self.network.bsm_nodes.values())

        for nodeA in nodes:
            for nodeB in nodes:
                # Classical channel initiation
                cc = ClassicalChannel(name=f"cc({nodeA.name}, {nodeB.name})", timeline=self.network.timeline, 
                            distance=cc_distance, delay=cc_delay)
                cc.set_ends(nodeA, nodeB.name)

    def _update_network_topology(self, graph: nx.Graph, topology_name: str) -> None:
        self.network.update_graph(graph)
        self.network.update_topology(topology_name)
        self.network.update_bsm_nodes(dict())

    def _connect_network_channels(self) -> None:
        for edge in self.network.edges():
            nodeA_id: int = edge[0]
            nodeB_id: int = edge[1]

            bsm_node: BSMNode = self._create_BSMNode(nodeA_id=nodeA_id, nodeB_id=nodeB_id,
                                            edge=edge)
            
            self._connect_quantum_channels(nodeA_id=nodeA_id, nodeB_id=nodeB_id, bsm_node=bsm_node,
                            qc_attenuation=QCHANNEL_ATTENUATION, qc_distance=QCHANNEL_DISTANCE)           

        self._connect_classical_channels(cc_distance=CCHANNEL_DISTANCE, cc_delay=CCHANNEL_DELAY)

    def grid_topology(self, rows: int, columns: int) -> dict[int, QuantumRepeater]:
        
        self._create_nodes(rows*columns)

        graph: nx.Graph =  nx.grid_2d_graph(rows, columns)
        graph = nx.convert_node_labels_to_integers(graph)

        self._update_network_topology(graph=graph, topology_name=Topologies.GRID)
        
        self._connect_network_channels()

        return self.network.nodes

    def line_topology(self, number_of_nodes: int) -> dict[int, QuantumRepeater]:
        
        self._create_nodes(number_of_nodes)

        graph: nx.Graph = nx.path_graph(number_of_nodes)
        graph = nx.convert_node_labels_to_integers(graph)

        self._update_network_topology(graph=graph, topology_name=Topologies.LINE)

        self._connect_network_channels()

        return self.network.nodes
    
    def erdos_renyi_topology(self, number_of_nodes: int, prob_edge_creation: float) -> dict[int, QuantumRepeater]:

        self._create_nodes(number_of_nodes)

        graph: nx.Graph = nx.erdos_renyi_graph(number_of_nodes, prob_edge_creation)
        graph = nx.convert_node_labels_to_integers(graph)

        self._update_network_topology(graph=graph, topology_name=Topologies.ERDOS_RENYI)

        self._connect_network_channels()

        return self.network.nodes
    
    def barabasi_albert_topology(self, number_of_nodes: int, edges_to_attach: int) -> dict[int, QuantumRepeater]:

        self._create_nodes(number_of_nodes)

        graph: nx.Graph = nx.barabasi_albert_graph(number_of_nodes, edges_to_attach)
        graph = nx.convert_node_labels_to_integers(graph)

        self._update_network_topology(graph=graph, topology_name=Topologies.BARABASI_ALBERT)

        self._connect_network_channels()

        return self.network.nodes
    
    def star_topology(self, number_of_nodes: int) -> dict[int, QuantumRepeater]:

        self._create_nodes(number_of_nodes)

        graph: nx.Graph = nx.star_graph(number_of_nodes-1) # Star graph has n-1 leaves and 1 center node
        graph = nx.convert_node_labels_to_integers(graph)

        self._update_network_topology(graph=graph, topology_name=Topologies.STAR)

        self._connect_network_channels()

        return self.network.nodes
    
    def ring_topology(self, number_of_nodes: int) -> dict[int, QuantumRepeater]:

        self._create_nodes(number_of_nodes)

        graph: nx.Graph = nx.cycle_graph(number_of_nodes)
        graph = nx.convert_node_labels_to_integers(graph)

        self._update_network_topology(graph=graph, topology_name=Topologies.RING)

        self._connect_network_channels()

        return self.network.nodes
    