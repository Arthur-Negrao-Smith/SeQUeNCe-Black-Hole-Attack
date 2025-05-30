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

# Constant
RAW: str = 'RAW'
MEM_FIDELITY: float = 0.9
MEM_FREQUENCY: int = 2_000
MEM_EFFICIENCY: float = 1
MEM_COHERENCE_TIME: int = -1
MEM_WAVELENGHT: int = 500
BSM_EFFICIENCY: int = 1
QCHANNEL_DISTANCE: int = 1_000
QCHANNEL_ATTENUATION: int = 0


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


def grid_topology(rows: int, columns: int, timeline: Timeline, node_type: str) -> dict[int, Node]:
    if node_type == "node":
        node = Node
    elif node_type == "entanglegennode":
        node = EntangleGenNode

    graph: list = nx.grid_2d_graph(rows, columns).edges()
    print(graph) # (0, 0) <- i = 0, j = 0

    '''
    nodes: dict[int, Node] = dict()
    for c in range(0, rows*columns):
        nodes[c] = node(name=f"node{c}", timeline=timeline, seed=c)
    
    for row in range(0, rows):
        for column in range(0, columns):
            
            if row == 0 and column == 0:
                pass'''


tl = Timeline()

'''
node1: EntangleGenNode = EntangleGenNode("node1", tl)
node2: EntangleGenNode = EntangleGenNode("node2", tl)
bsm_node: BSMNode = BSMNode(name='bsm_node', timeline=tl, other_nodes=['node1', 'node2'])
node1.set_seed(0)
node2.set_seed(1)
bsm_node.set_seed(2)

bsm: SingleAtomBSM = bsm_node.get_components_by_type("SingleAtomBSM") # <- Get the bsm without node
bsm.update_detectors_param('efficiency', BSM_EFFICIENCY) # <- Change the detector efficiency

qc1 = QuantumChannel('qc1', tl, attenuation=0, distance=QCHANNEL_DISTANCE)
qc2 = QuantumChannel('qc2', tl, attenuation=0, distance=QCHANNEL_DISTANCE)
'''

grid_topology(2, 2, timeline=tl, node_type='node')