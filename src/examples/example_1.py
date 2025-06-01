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
NODE: str = 'node'
ENTANGLEGENNODE: str = 'entanglegennode'


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

    def creat_protocol(self, middle: str, other: str) -> None:
        self.owner.protocols = [EntanglementGenerationA(self.owner, f"{self.owner.name}.eg", 
                                                        middle, other, self.owner.components[self.memo_name])]
        

class EntangleGenNode(Node):
    def __init__(self, name, timeline) -> None:
        super().__init__(name, timeline)

        memo_name: str = f"{name}.memo"
        memory: Memory = Memory(memo_name, timeline, MEM_FIDELITY, MEM_FREQUENCY, MEM_EFFICIENCY, MEM_COHERENCE_TIME, MEM_WAVELENGHT)
        memory.owner = self
        memory.add_receiver(self)
        self.add_component(self)

        self.resource_manager: SimpleManager = SimpleManager(self, memo_name)

    def init(self) -> None:
        memory: Memory = self.get_components_by_type("Memory")[0]
        memory.reset()

    def receive_message(self, src: str, msg: 'Message') -> None: # type: ignore
        self.protocols[0].received_message(src, msg)

    def get(self, photon, **kwargs):
        self.send_qubit(kwargs['dst'], photon)


def create_grid_nodes(timeline: Timeline, node_type: str,
                       rows: int, columns: int) -> dict[int, Union[Node, EntangleGenNode]]:
    """
    Create all grid nodes and return them in a dictionary

    Args:
        timeline (Timeline): Timeline to add on Nodes
        node_type (str): The type of node to create
        rows (int): Numbem of rows in the grid
        columns (int): Number of columns in the grid

    Returns:
        dict[int, Union[Node, EntangleGenNode]]: A dictionary where each key is a unique 
        integer node ID, and each value is the corresponding node instance placed in the grid.
    """

    node: Union[Node, EntangleGenNode]
    if node_type ==  NODE:
        node = Node
    elif node_type == ENTANGLEGENNODE:
        node = EntangleGenNode
    else:
        node = Node

    nodes: dict[int, Union[Node, EntangleGenNode]] = dict()
    for c in range(0, rows*columns):
        tmp_node: Union[Node, EntangleGenNode] = node(name=f"node{c}", timeline=timeline)
        tmp_node.set_seed(c)
        nodes[c] = tmp_node

    return nodes


def connect_channels(timeline: Timeline, nodes: dict[int, Union[Node, EntangleGenNode]], 
                     nodeA_id: int, nodeB_id: int, bsm_node: BSMNode, counter: int, 
                     qc_attenuation: int, qc_distance: int, cc_distance: int, cc_delay: int) -> None:
        # Quantum channel initiation
        qc1 = QuantumChannel(name=f'qc{counter}', timeline=timeline,
                              attenuation=qc_attenuation, distance=qc_distance)
        qc2 = QuantumChannel(name=f'qc{counter+1}', timeline=timeline,
                              attenuation=qc_attenuation, distance=qc_distance)

        qc1.set_ends(nodes[nodeA_id], bsm_node.name)
        qc2.set_ends(nodes[nodeB_id], bsm_node.name)

        # Classical channel initiation
        cc = ClassicalChannel(name=f"cc[{nodeA_id}, {nodeB_id}]", timeline=timeline, 
                              distance=cc_distance, delay=cc_delay)
        cc.set_ends(nodes[nodeA_id], nodes[nodeB_id].name)


def grid_topology(rows: int, columns: int,
                   timeline: Timeline, node_type: str) -> dict[int, Node]:
    
    nodes: dict[int, Union[Node, EntangleGenNode]] = create_grid_nodes(timeline=timeline, 
                                                                       node_type=node_type, 
                                                                       rows=rows, 
                                                                       columns=columns)

    graph: nx.Graph =  nx.grid_2d_graph(rows, columns)
    graph = nx.convert_node_labels_to_integers(graph)

    print(graph.edges())
    # nx.draw(G=graph, with_labels=True) # to use in jupyter notebook

    bsm_nodes: dict[tuple[int, int], BSMNode] = dict()
    counter: int = 0
    for edge in graph.edges():
        nodeA_id: int = edge[0]
        nodeB_id: int = edge[1]

        bsm_node: BSMNode = BSMNode(name=f'bsm_node[{nodeA_id}, {nodeB_id}]', timeline=timeline,
                                     other_nodes=[f'node{nodeA_id}', f'node{nodeB_id}'])
        bsm_node.set_seed(counter)
        bsm_nodes[edge] = bsm_node # adding bsm node in a dict
        bsm = bsm_node.get_components_by_type("SingleAtomBSM")[0] # <- Get the bsm without node
        bsm.update_detectors_params('efficiency', BSM_EFFICIENCY) # <- Change the detector efficiency

        connect_channels(timeline=timeline, nodes=nodes, nodeA_id=nodeA_id, nodeB_id=nodeB_id, bsm_node=bsm_node,
                          counter=counter, qc_attenuation=QCHANNEL_ATTENUATION, qc_distance=QCHANNEL_DISTANCE,
                          cc_distance=CCHANNEL_DISTANCE, cc_delay=CCHANNEL_DELAY) 
        counter += 2


tl = Timeline()

grid_topology(2, 2, timeline=tl, node_type='node')