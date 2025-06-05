# Nodes and Memory
from sequence.topology.node import Node
from sequence.topology.node import BSMNode, SingleAtomBSM
from sequence.components.memory import Memory

# Channels
from sequence.components.optical_channel import QuantumChannel, ClassicalChannel

# Protocols
from sequence.entanglement_management.entanglement_protocol import EntanglementProtocol
from sequence.entanglement_management.generation import EntanglementGenerationA

# Kernel components
from sequence.kernel.timeline import Timeline

# To create topologies
import networkx as nx

# To add types
from typing import Union

# Constants
RAW: str = 'RAW'
MEM_FIDELITY: float = 0.9
MEM_FREQUENCY: int = 2_000
MEM_EFFICIENCY: float = 1
MEM_COHERENCE_TIME: int = -1
MEM_WAVELENGHT: int = 500
BSM_EFFICIENCY: int = 1
QCHANNEL_DISTANCE: int = 1_000
QCHANNEL_ATTENUATION: int = 0
CCHANNEL_DISTANCE: int = 1_000
CCHANNEL_DELAY: int = 1e8
GRID: str = 'grid'

class SimpleManager:
    """
    Class to create entanglement protocol and monitor their success
    """
    def __init__(self, owner: Node, memo_name: str) -> None:
        self.owner: Node = owner
        self.memo_name: str = memo_name
        self.raw_counter: int = 0 # <- no memory entangled counter
        self.ent_counter: int = 0 # <- memory entangled counter

    def update(self, protocol: EntanglementProtocol, memory: Memory, state: str) -> None:
        if state == RAW:
            self.raw_counter += 1
            memory.reset()
        else:
            self.ent_counter += 1

    def create_protocol(self, middle: str, other: str) -> None:
        self.owner.protocols = [EntanglementGenerationA(self.owner, f"{self.owner.name}.eg", 
                                                        middle, other, self.owner.components[self.memo_name])]
        

class EntangleGenNode(Node):
    def __init__(self, name, timeline) -> None:
        super().__init__(name, timeline)

        memo_name: str = f"{name}.memo"
        memory: Memory = Memory(memo_name, timeline, MEM_FIDELITY, MEM_FREQUENCY, MEM_EFFICIENCY, MEM_COHERENCE_TIME, MEM_WAVELENGHT)
        memory.owner = self
        memory.add_receiver(self)
        self.add_component(memory)

        self.resource_manager: SimpleManager = SimpleManager(self, memo_name)

    def init(self) -> None:
        memory: Memory = self.get_components_by_type("Memory")[0]
        memory.reset()

    def receive_message(self, src: str, msg: 'Message') -> None: # type: ignore
        self.protocols[0].received_message(src, msg)

    def get(self, photon, **kwargs) -> None:
        self.send_qubit(kwargs['dst'], photon)


# Topologies generator
class TopologyGen:
    def __init__(self, network: 'Network'):
        self.network: Network = network

    def _create_nodes(self, number_of_nodes: int) -> dict[int, EntangleGenNode]:
        """
        Create all grid nodes and return them in a dictionary

        Args:
            number_of_nodes (int): Number of nodes on the network

        Returns:
            dict[int, EntangleGenNode]: A dictionary where each key is a unique 
            integer node ID, and each value is the corresponding node instance placed in the grid.
        """

        nodes: dict[int, EntangleGenNode] = dict()
        for c in range(0, number_of_nodes):
            tmp_node: EntangleGenNode = EntangleGenNode(name=f"node{c}", timeline=self.network.timeline)
            tmp_node.set_seed(c)
            nodes[c] = tmp_node
        
        self.network.update_number_of_nodes(number_of_nodes)
        self.network.update_nodes(nodes)

        return nodes

    def _create_BSMNode(self, nodeA_id: int, nodeB_id: int, seed_counter: int, edge: tuple[int, int]) -> BSMNode:

        bsm_node: BSMNode = BSMNode(name=f'bsm_node({nodeA_id}, {nodeB_id})', timeline=self.network.timeline,
                                        other_nodes=[f'node{nodeA_id}', f'node{nodeB_id}'])
        bsm_node.set_seed(seed_counter)
        self.network.bsm_nodes[edge] = bsm_node # adding bsm node in a dict
        bsm: SingleAtomBSM = bsm_node.get_components_by_type("SingleAtomBSM")[0] # <- Get the bsm without node
        bsm.update_detectors_params('efficiency', BSM_EFFICIENCY) # <- Change the detector efficiency

        return bsm_node

    def _connect_quantum_channels(self, nodeA_id: int, nodeB_id: int, bsm_node: BSMNode, 
                                  seed_counter: int, qc_attenuation: int, qc_distance: int) -> None:
            # Quantum channel initiation
            qc1 = QuantumChannel(name=f'qc{seed_counter}', timeline=self.network.timeline,
                                attenuation=qc_attenuation, distance=qc_distance)
            qc2 = QuantumChannel(name=f'qc{seed_counter+1}', timeline=self.network.timeline,
                                attenuation=qc_attenuation, distance=qc_distance)

            qc1.set_ends(self.network.nodes[nodeA_id], bsm_node.name)
            qc2.set_ends(self.network.nodes[nodeB_id], bsm_node.name)

            """# Classical channel initiation
            cc = ClassicalChannel(name=f"cc({nodeA_id}, {nodeB_id})", timeline=self.network.timeline, 
                                distance=cc_distance, delay=cc_delay)
            cc.set_ends(self.network.nodes[nodeA_id], self.network.nodes[nodeB_id].name)"""

    def _connect_classical_channels(self, cc_distance: int, cc_delay: int) -> None:
        for nodeA_id in range(network.number_of_nodes):
            for nodeB_id in range(network.number_of_nodes):
                # Classical channel initiation
                cc = ClassicalChannel(name=f"cc({nodeA_id}, {nodeB_id})", timeline=self.network.timeline, 
                            distance=cc_distance, delay=cc_delay)
                cc.set_ends(self.network.nodes[nodeA_id], self.network.nodes[nodeB_id].name)

    def _update_network_topology(self, graph: nx.Graph, topology_name: str) -> None:
        self.network.update_graph(graph)
        self.network.update_topology(topology_name)
        self.network.update_bsm_nodes(dict())

    def _connect_network_channels(self) -> None:
        seed_counter: int = 0
        for edge in self.network.edges():
            nodeA_id: int = edge[0]
            nodeB_id: int = edge[1]

            bsm_node: BSMNode = self._create_BSMNode(nodeA_id=nodeA_id, nodeB_id=nodeB_id,
                                            seed_counter=seed_counter, edge=edge)
            
            self._connect_quantum_channels(nodeA_id=nodeA_id, nodeB_id=nodeB_id, bsm_node=bsm_node,
                            seed_counter=seed_counter, qc_attenuation=QCHANNEL_ATTENUATION, 
                            qc_distance=QCHANNEL_DISTANCE) 
            
            seed_counter += 2 # update seed_counter

        self._connect_classical_channels(cc_distance=CCHANNEL_DISTANCE, cc_delay=CCHANNEL_DELAY)

    def grid_topology(self, rows: int, columns: int) -> dict[int, EntangleGenNode]:
        
        self._create_nodes(rows*columns)

        graph: nx.Graph =  nx.grid_2d_graph(rows, columns)
        graph = nx.convert_node_labels_to_integers(graph)

        self._update_network_topology(graph=graph, topology_name=GRID)
        
        self._connect_network_channels()

        return self.network.nodes


class Network:
    def __init__(self) -> None:
        self.timeline: Timeline = Timeline()
        self.topology: str
        self.graph: nx.Graph
        self.nodes: dict[int, EntangleGenNode]
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
    
    def update_nodes(self, nodes: dict[int, EntangleGenNode]) -> None:
        self.nodes = nodes

    def update_topology(self, topology_name: str) -> None:
        self.topology = topology_name

    def update_graph(self, graph: nx.Graph) -> None:
        self.graph = graph

    def update_number_of_nodes(self, number_of_nodes: int) -> None:
        self.number_of_nodes = number_of_nodes

    def update_bsm_nodes(self, bsm_nodes: dict[tuple[int, int], BSMNode]) -> None:
        self.bsm_nodes = bsm_nodes

def pair_protocol(node1: Node, node2: Node):
    p1 = node1.protocols[0]
    p2 = node2.protocols[0]
    node1_memo_name = node1.get_components_by_type("Memory")[0].name
    node2_memo_name = node2.get_components_by_type("Memory")[0].name
    p1.set_others(p2.name, node2.name, [node2_memo_name])
    p2.set_others(p1.name, node1.name, [node1_memo_name])


network = Network()
network.topology_generator.grid_topology(2, 2)
print(network.edges())
print(network.nodes)

node0: EntangleGenNode = network.nodes[0]
node1: EntangleGenNode = network.nodes[1]
print(node0.name)

node0.resource_manager.create_protocol('bsm_node(0, 1)', 'node1')
node1.resource_manager.create_protocol('bsm_node(0, 1)', 'node0')
pair_protocol(node0, node1)

memory = node0.get_components_by_type("Memory")[0]


print('before', memory.entangled_memory, memory.fidelity)

network.timeline.init()
node0.protocols[0].start()
node1.protocols[0].start()
network.timeline.run()

print('after', memory.entangled_memory, memory.fidelity)