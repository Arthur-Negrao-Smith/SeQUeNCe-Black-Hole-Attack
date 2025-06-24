from sequence.kernel.timeline import Timeline
from sequence.topology.node import Node
from sequence.components.memory import Memory, MemoryArray
from sequence.components.optical_channel import ClassicalChannel
from sequence.entanglement_management.swapping import EntanglementSwappingA, EntanglementSwappingB
from sequence.message import Message
from sequence.protocol import Protocol
from abc import ABC
from queue import Queue

# CONSTANT
LEFT: str = "left"
RIGHT: str = "right"

# Swap constant
ENTANGLEMENT_SWAPPING_PROB: float = 0.9
SWAP_DEGRADATION: float = 0.99

# Memory Constant
MEMORY_ARRAY_SIZE: int = 10
MEMORY_ARRAY_NAME: str = ".MemoryArray"
MEMORY_FIDELITY: float = 0.9
MEMORY_FREQUENCY: int = 2000
MEMORY_EFFICIENCY: float = 1
MEMORY_COHERENCE_TIME: int = -1
MEMORY_WAVELENGTH: int = 500


class BaseManager(ABC):
    """
    Base Manager to create to entanglement swapping managers
    """
    def __init__(self, owner: Node) -> None:
        self.owner: Node = owner
        self.raw_counter: int = 0
        self.ent_counter: int = 0

    def update(self, protocol: Protocol, memory: Memory, state: str) -> None:
        if state == 'RAW':
            self.raw_counter += 1
            memory.reset()
        else:
            self.ent_counter += 1


class RepeaterManager(BaseManager):
    """
    Manager to control entanglement swapping in repeater nodes
    """
    def __init__(self, owner: "QuantumRepeater") -> None:
        super().__init__(owner)

    def create_protocolA(self) -> None:
        """
        Create a Protocol to realize the entanglement swapping in mid node
        """
        left_memo: Memory = self.owner.components[self.owner.left_memo_name]
        right_memo: Memory = self.owner.components[self.owner.right_memo_name]
        protocol: EntanglementSwappingA = EntanglementSwappingA(self.owner, 
                                                        f'{self.owner.name}.ESA', 
                                                        left_memo, 
                                                        right_memo, 
                                                        ENTANGLEMENT_SWAPPING_PROB,  # type: ignore
                                                        SWAP_DEGRADATION)
        self.owner.protocols_queue.put(protocol)
        self.owner.protocols.append(protocol)
        
    def create_protocolB(self, memory_position: str) -> None:
        """
        Create a Protocol to Entanglement a memory in side node

        Args:
            memory_position (str): Position of the memory to entanglement (left or right)
        """
        if memory_position == LEFT:
            left_memo: Memory = self.owner.components[self.owner.left_memo_name]
            protocol: EntanglementSwappingB = EntanglementSwappingB(self.owner, f'{self.owner.name}.ESB', left_memo)
            self.owner.protocols_queue.put(protocol)
            self.owner.protocols.append(protocol)
        
        elif memory_position == RIGHT:
            right_memo: Memory = self.owner.components[self.owner.right_memo_name]
            protocol: EntanglementSwappingB = EntanglementSwappingB(self.owner, f'{self.owner.name}.ESB', right_memo)
            self.owner.protocols_queue.put(protocol)
            self.owner.protocols.append(protocol)

        

class QuantumRepeater(Node):
    """
    Quantum Router to increase the entanglement range on the Network
    """
    def __init__(self, name: str, tl: Timeline) -> None:
        super().__init__(name, tl)

        self.protocols_queue: Queue[EntanglementSwappingA | EntanglementSwappingB] = Queue()

        self.left_memo_name: str = f'{name}.left_memo'
        self.right_memo_name: str = f'{name}.right_memo'

        left_memo: Memory = Memory(self.left_memo_name, tl, MEMORY_FIDELITY, MEMORY_FREQUENCY, MEMORY_EFFICIENCY, MEMORY_COHERENCE_TIME, MEMORY_WAVELENGTH)
        right_memo: Memory = Memory(self.right_memo_name, tl, MEMORY_FIDELITY, MEMORY_FREQUENCY, MEMORY_EFFICIENCY, MEMORY_COHERENCE_TIME, MEMORY_WAVELENGTH)
        
        self.add_component(left_memo)
        self.add_component(right_memo)

        self.resource_manager: RepeaterManager = RepeaterManager(self)
        self.owner.protocols = []

    def receive_message(self, src: str, msg: "Message") -> None:
        self.protocols[0].received_message(src, msg)

    def run_protocol(self) -> None:
        """
        Remove first protocol in the queue and run
        """
        self.protocols.pop(0)
        self.protocols_queue.get().start()

    def get_protocol(self) -> Protocol:
        """
        Get and remove the next protocol on the queue
        """
        return self.protocols[0]


def entangle_memory(tl: Timeline, memo1: Memory, memo2: Memory, fidelity: float) -> None:
    SQRT_HALF: float = 0.5 ** 0.5
    phi_plus: list[float | int] = [SQRT_HALF, 0, 0, SQRT_HALF]

    memo1.reset()
    memo2.reset()
    tl.quantum_manager.set([memo1.qstate_key, memo2.qstate_key], phi_plus) # type: ignore

    memo1.entangled_memory['node_id'] = memo2.owner.name # type: ignore
    memo1.entangled_memory['memo_id'] = memo2.name # type: ignore
    memo2.entangled_memory['node_id'] = memo1.owner.name # type: ignore
    memo2.entangled_memory['memo_id'] = memo1.name # type: ignore

    memo1.fidelity = memo2.fidelity = fidelity # type: ignore


def pair_protocol(node1: QuantumRepeater, node2: QuantumRepeater, node_mid: QuantumRepeater) -> None:
    p1: EntanglementSwappingB = node1.get_protocol()
    p2: EntanglementSwappingB = node2.get_protocol()
    pmid: EntanglementSwappingA = node_mid.get_protocol()
    p1.set_others(pmid.name, node_mid.name,
                  [node_mid.left_memo_name, node_mid.right_memo_name])
    p2.set_others(pmid.name, node_mid.name,
                  [node_mid.left_memo_name, node_mid.right_memo_name])
    pmid.set_others(p1.name, node1.name, [node1.right_memo_name])
    pmid.set_others(p2.name, node2.name, [node2.left_memo_name])


tl = Timeline()

node0 = QuantumRepeater('node0', tl)
node1 = QuantumRepeater('node1', tl)
node2 = QuantumRepeater('node2', tl)
node3 = QuantumRepeater('node3', tl)
node0.set_seed(0)
node1.set_seed(1)
node2.set_seed(2)
node3.set_seed(3)

nodes: list[QuantumRepeater] = [node0, node1, node2, node3]

for i in range(len(nodes)):
    for j in range(len(nodes)):
        if i != j:
            cc = ClassicalChannel(f'cc_{nodes[i].name}_{nodes[j].name}', tl, 1000, 1e9)
            cc.set_ends(nodes[i], nodes[j].name)


node0_right_memo: Memory = node0.components[node0.right_memo_name]

node1_left_memo: Memory = node1.components[node1.left_memo_name]
node1_right_memo: Memory = node1.components[node1.right_memo_name]

node2_left_memo: Memory = node2.components[node2.left_memo_name]
node2_right_memo: Memory = node2.components[node2.right_memo_name]

node3_left_memo: Memory = node3.components[node3.left_memo_name]

entangle_memory(tl, node0_right_memo, node1_left_memo, MEMORY_FIDELITY)
entangle_memory(tl, node1_right_memo, node2_left_memo, MEMORY_FIDELITY)
entangle_memory(tl, node2_right_memo, node3_left_memo, MEMORY_FIDELITY)

node0.resource_manager.create_protocolB(RIGHT)
node0.resource_manager.create_protocolB(RIGHT)
node1.resource_manager.create_protocolA()
node2.resource_manager.create_protocolB(LEFT)
node2.resource_manager.create_protocolA()
node3.resource_manager.create_protocolB(LEFT)

pair_protocol(node0, node2, node1)

print('--------')
print('Before swapping:')
print(tl.quantum_manager.states[0], '\n')
print(tl.quantum_manager.states[1], '\n')
print(tl.quantum_manager.states[2], '\n')
print(tl.quantum_manager.states[3], '\n')

print(node0_right_memo.entangled_memory)
print(node2_left_memo.entangled_memory)
print(node2_right_memo.entangled_memory)
print(node3_left_memo.entangled_memory)
print(node0_right_memo.fidelity)

tl.init()

node0.run_protocol()
node1.run_protocol()
node2.run_protocol()
tl.run()
tl.time = tl.now() + 1e11

pair_protocol(node0, node3, node2)
node0.run_protocol()
node2.run_protocol()
node3.run_protocol()
tl.run()

print('--------')
print('after swapping:')
print(tl.quantum_manager.states[0], '\n')
print(tl.quantum_manager.states[1], '\n')
print(tl.quantum_manager.states[2], '\n')
print(tl.quantum_manager.states[3], '\n')

print(node0_right_memo.entangled_memory)
print(node2_left_memo.entangled_memory)
print(node2_right_memo.entangled_memory)
print(node3_left_memo.entangled_memory)
print(node0_right_memo.fidelity)