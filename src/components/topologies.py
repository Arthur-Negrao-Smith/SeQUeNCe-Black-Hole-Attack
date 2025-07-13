from sequence.topology.topology import BSMNode, SingleAtomBSM
from sequence.components.optical_channel import ClassicalChannel, QuantumChannel

from .utils.constants import BSM_EFFICIENCY, QCHANNEL_ATTENUATION, QCHANNEL_DISTANCE, CCHANNEL_DISTANCE, CCHANNEL_DELAY, ENTANGLEMENT_SWAPPING_PROB
from .utils.enums import Topologies
from .nodes import QuantumRepeater

import networkx as nx
from copy import copy
from typing import Optional, Any
import logging

log: logging.Logger = logging.getLogger(__name__)

# Topologies generator
class TopologyGen:
    from .network import Network
    def __init__(self, network: Network, start_seed: Optional[int] = None) -> None:
        """
        TopologyGen constructor

        Args:
            network (Network): Network to build the topology
            start_seed (Optional[int]): Seed to replicate the simulation. Default is None
        """

        self.network: Network = network # type: ignore

        self.seed: None | int = start_seed

        log.debug("TopologyGen initiated")

    def destroy(self) -> None:
        """
        Cleanup all references
        """
        self.network = None
    
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
            tmp_node: QuantumRepeater = QuantumRepeater(name=f"node[{c}]", timeline=self.network.timeline, swap_prob=ENTANGLEMENT_SWAPPING_PROB)

            if self.seed is not None:
                tmp_node.set_seed(self.seed)
                self.seed += 1
            nodes[c] = tmp_node

        self.network.update_number_of_nodes(number_of_nodes)
        self.network.update_nodes(nodes)
        self.network.update_normal_nodes(copy(nodes))

        return nodes
    
    def _create_BSMNode(self, nodeA_id: int, nodeB_id: int, edge: tuple[int, int]) -> BSMNode:
        """
        Create BSMNode between two nodes

        Args:
            nodeA_id (int): First node ID
            nodeB_id (int): Second node ID
            edge tuple(int, int): Edge between nodeA and nodeB

        Returns:
            BSMNode: BSMNode connected with nodeA and nodeB
        """

        bsm_node: BSMNode = BSMNode(name=f'bsm_node({nodeA_id}, {nodeB_id})', timeline=self.network.timeline,
                                        other_nodes=[f'node[{nodeA_id}]', f'node[{nodeB_id}]'])
        if self.seed is not None:
            bsm_node.set_seed(self.seed)
            self.seed += 1

        self.network.bsm_nodes[edge] = bsm_node # adding bsm node in a dict
        bsm: SingleAtomBSM = bsm_node.get_components_by_type("SingleAtomBSM")[0] # <- Get the bsm without node
        bsm.update_detectors_params('efficiency', BSM_EFFICIENCY) # <- Change the detector efficiency

        log.debug(f"Created {bsm_node.name} to connect node[{nodeA_id}] to node[{nodeB_id}]")

        return bsm_node

    def _connect_quantum_channels(self, nodeA_id: int, nodeB_id: int, bsm_node: BSMNode, 
                                  qc_attenuation: int, qc_distance: int) -> None:
        """
        Connect quantum channels between nodeA, nodeB and bsm

        Args:
            nodeA_id (int): NodeA ID
            nodeB_id (int): NodeB ID
            bsm_node (BSMNode): BSMNode between nodeA and nodeB
            qc_attenuation (int): Quantum channel attenuation
            qc_distance (int): Quantum channel distance
        """

        # Quantum channel initiation
        qc1 = QuantumChannel(name=f'qc({self.network.nodes[nodeA_id].name}, {bsm_node.name})',
                                timeline=self.network.timeline,
                            attenuation=qc_attenuation, distance=qc_distance)
        qc2 = QuantumChannel(name=f'qc({bsm_node.name}, {self.network.nodes[nodeB_id].name})', timeline=self.network.timeline,
                            attenuation=qc_attenuation, distance=qc_distance)

        qc1.set_ends(self.network.nodes[nodeA_id], bsm_node.name)
        qc2.set_ends(self.network.nodes[nodeB_id], bsm_node.name)

    def _connect_bsm_classical_channels(self, cc_distance: int, cc_delay: int) -> None:
        """
        Connect all BSM with classical channels. This function will reduce unnecessary connections

        Args:
            cc_distance (int): Classical channel distance
            cc_delay (int): Classical channel delay
        """
        for edge, bsm in self.network.bsm_nodes.items():
            nodeA: QuantumRepeater = self.network.nodes[edge[0]]
            nodeB: QuantumRepeater = self.network.nodes[edge[1]]

            # connecting nodes with bsm
            cc = ClassicalChannel(name=f"cc({nodeA.name}, {bsm.name})", timeline=self.network.timeline, 
                            distance=cc_distance, delay=cc_delay)
            cc.set_ends(nodeA, bsm.name)

            cc = ClassicalChannel(name=f"cc({nodeB.name}, {bsm.name})", timeline=self.network.timeline, 
                            distance=cc_distance, delay=cc_delay)
            cc.set_ends(nodeB, bsm.name)

            # connecting bsm with nodes
            cc = ClassicalChannel(name=f"cc({bsm.name}, {nodeB.name})", timeline=self.network.timeline, 
                            distance=cc_distance, delay=cc_delay)
            cc.set_ends(bsm, nodeB.name)

            cc = ClassicalChannel(name=f"cc({bsm.name}, {nodeA.name})", timeline=self.network.timeline, 
                            distance=cc_distance, delay=cc_delay)
            cc.set_ends(bsm, nodeA.name)

    def _connect_classical_channels(self, cc_distance: int, cc_delay: int) -> None:
        """
        Connect all classical channels

        Args:
            cc_distance (int): Classical channel distance
            cc_delay (int): Classical channel delay
        """

        self._connect_bsm_classical_channels(cc_distance=cc_distance, cc_delay=cc_delay)

        nodes: list[QuantumRepeater] = self.network.nodes.values()
        for nodeA in nodes:
            for nodeB in nodes:
                # Optimization to don't produce unnecessary connections
                if nodeA == nodeB:
                    continue
                # Classical channel initiation
                cc = ClassicalChannel(name=f"cc({nodeA.name}, {nodeB.name})", timeline=self.network.timeline, 
                            distance=cc_distance, delay=cc_delay)
                cc.set_ends(nodeA, nodeB.name)

    def _update_network_topology(self, graph: nx.Graph, topology_name: Topologies) -> None:
        """
        Updates networks's attributes

        Args:
            graph (nx.Graph): Graph with all edges
            topology_name (Topologies):
        """
        self.network.update_graph(graph)
        self.network.update_topology(topology_name)
        self.network.update_bsm_nodes(dict())

    def _connect_network_channels(self) -> None:
        """
        Connect all channels: Classical and Quantum channels
        """
        for edge in self.network.edges():
            nodeA_id: int = edge[0]
            nodeB_id: int = edge[1]

            bsm_node: BSMNode = self._create_BSMNode(nodeA_id=nodeA_id, nodeB_id=nodeB_id,
                                            edge=edge)

            self._connect_quantum_channels(nodeA_id=nodeA_id, nodeB_id=nodeB_id, bsm_node=bsm_node,
                            qc_attenuation=QCHANNEL_ATTENUATION, qc_distance=QCHANNEL_DISTANCE)           

        self._connect_classical_channels(cc_distance=CCHANNEL_DISTANCE, cc_delay=CCHANNEL_DELAY)
        # init network's entities
        self.network.timeline.init()

    def _analyze_parameters(self, params_types: list[Any], args) -> None:
        """
        Analyze the parameters of args

        Args:
            params_type (list[Any]): List with all parameters types.
            *args: Collection with args to use in functions.

        Raises:
            Exception: If number of parameters in args is invalid.
            Exception: If type of parameter is diferent between args and params_types.
        """
        if len(args) != len(params_types):
            raise Exception(f"The number of parameters in args is incompatible. args: {args}")

        for position, param in enumerate(args):
            if not isinstance(param, params_types[position]):
                raise Exception(f"The type of the prameter is incompatible with needed type by the function. param: {param} in args position: {position}")

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
    
    def select_topology(self, topology: Topologies, *args) -> dict[int, QuantumRepeater]:
        """
        Simplified way of choosing a topology

        Args:
            topology (Topologies): Topology selected.
            *args: Collection with all parameter to use in topology's function.

        Returns:
            dict[int, QuantumRepeater]: Dict with all created nodes.

        Raises:
            Exception: If topology isn't avaliable in function.
            Exception: If it is different from the number of parameters required by the selected topology's function.
            Exception: If parameters' type are different of types of parameters required by the selected topology's function.
        """

        match topology:
            case Topologies.GRID:
                self._analyze_parameters(args=args, params_types=[int, int])
                return self.grid_topology(*args)
            
            case Topologies.LINE:
                self._analyze_parameters(args=args, params_types=[int])
                return self.line_topology(*args)
            
            case Topologies.STAR:
                self._analyze_parameters(args=args, params_types=[int])
                return self.star_topology(*args)

            case Topologies.ERDOS_RENYI:
                self._analyze_parameters(args=args, params_types=[int, float])
                return self.erdos_renyi_topology(*args)

            case Topologies.BARABASI_ALBERT:
                self._analyze_parameters(args=args, params_types=[int, int])
                return self.barabasi_albert_topology(*args)

            case Topologies.RING:
                self._analyze_parameters(args=args, params_types=[int])
                return self.ring_topology(*args)

            case _:
                raise Exception(f"Topology selected isn't avaliable.")
