from sequence.kernel.timeline import Timeline
from sequence.topology.node import Node
from sequence.components.memory import Memory, MemoryArray
from sequence.components.optical_channel import ClassicalChannel
from sequence.entanglement_management.swapping import EntanglementSwappingA, EntanglementSwappingB
from sequence.message import Message
from sequence.protocol import Protocol
from abc import ABC, abstractmethod


# Constant
ENTANGLEMENT_SWAPPING_PROB: float = 0.9
SWAP_DEGRADATION: float = 0.99
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
        self.counter: int = 0

    def update(self, protocol: Protocol, memory: Memory, state: str) -> None:
        if state == 'RAW':
            self.raw_counter += 1
            memory.reset()
        else:
            self.ent_counter += 1

    @abstractmethod
    def create_protocol(self) -> None:
        pass


class RepeaterManager(BaseManager):
    """
    Managerw to control repeater nodes
    """
    def __init__(self, owner: "QuantumRepeater") -> None:
        super().__init__(owner)

    def create_protocol(self) -> None:
        left_memo: Memory = self.owner.components[self.owner.left_memo_name]
        right_memo: Memory = self.owner.components[self.owner.right_memo_name]
        self.owner.protocols.append(EntanglementSwappingA(self.owner, 
                                                        'ESA', 
                                                        left_memo, 
                                                        right_memo, 
                                                        ENTANGLEMENT_SWAPPING_PROB,  # type: ignore
                                                        SWAP_DEGRADATION))
        
        
class SwapManager(BaseManager):
    """
    Manager to control swap nodes
    """
    def __init__(self, owner: Node) -> None:
        super().__init__(owner)
        
    def create_protocol(self) -> None:
        memo: Memory = self._choice_memory()
        self.owner.protocols.append(EntanglementSwappingB(self.owner, f'{self.owner.name}.ESB', memo))

    def _choice_memory(self) -> Memory:
        memo: Memory = self.owner.components[self.owner.memo_name]
        self.counter += 1
        return memo

class QuantumRepeater(Node):
    """
    Quantum Router to increase the entanglement range on the Network
    """
    def __init__(self, name: str, tl: Timeline) -> None:
        super().__init__(name, tl)
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


class SwapNode(Node):
    """
    Quantum Node to request Entanglement Swapping
    """
    def __init__(self, name: str, tl: Timeline) -> None:
        super().__init__(name, tl)
        memory_array: MemoryArray = MemoryArray(name=f"{self.owner.name}{MEMORY_ARRAY_NAME}",
                                                      timeline=self.owner.timeline, num_memories=MEMORY_ARRAY_SIZE,
                                                        fidelity=MEMORY_FIDELITY, frequency=MEMORY_FREQUENCY,
                                                        coherence_time=MEMORY_COHERENCE_TIME, wavelength=MEMORY_WAVELENGTH)
        self.add_component(memory_array)
        self.memo_name: str = f'{name}.memo'
        memo = Memory(self.memo_name, tl, MEMORY_FIDELITY, MEMORY_FREQUENCY, MEMORY_EFFICIENCY, MEMORY_COHERENCE_TIME, MEMORY_WAVELENGTH)
        self.add_component(memo)

        self.resource_manager: SwapManager = SwapManager(self)
        self.owner.protocols = []

    def receive_message(self, src: str, msg: "Message") -> None:
        self.protocols[0].received_message(src, msg) # type: ignore

    def create_protocol(self) -> None:
        self.protocols: list[EntanglementSwappingB] = [EntanglementSwappingB(self, f'{self.name}.ESB', self.memo)] # type: ignore

    def entangle_memory(self, memo1: Memory, memo2: Memory, fidelity: float) -> None:
        SQRT_HALF: float = 0.5 ** 0.5
        phi_plus: list[float | int] = [SQRT_HALF, 0, 0, SQRT_HALF]

        memo1.reset()
        memo2.reset()
        self.timeline.quantum_manager.set([memo1.qstate_key, memo2.qstate_key], phi_plus) # type: ignore

        memo1.entangled_memory['node_id'] = memo2.owner.name # type: ignore
        memo1.entangled_memory['memo_id'] = memo2.name # type: ignore
        memo2.entangled_memory['node_id'] = memo1.owner.name # type: ignore
        memo2.entangled_memory['memo_id'] = memo1.name # type: ignore

        memo1.fidelity = memo2.fidelity = fidelity # type: ignore

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


def pair_protocol(node1: SwapNode, node2: SwapNode, node_mid: QuantumRepeater, protocol_IDS: list[int]) -> None:
    p1: EntanglementSwappingB = node1.protocols[protocol_IDS[0]]
    p2: EntanglementSwappingB = node2.protocols[protocol_IDS[1]]
    pmid: EntanglementSwappingA = node_mid.protocols[protocol_IDS[2]]
    p1.set_others(pmid.name, node_mid.name,
                  [node_mid.left_memo_name, node_mid.right_memo_name])
    p2.set_others(pmid.name, node_mid.name,
                  [node_mid.left_memo_name, node_mid.right_memo_name])
    pmid.set_others(p1.name, node1.name, [node1.memo_name])
    pmid.set_others(p2.name, node2.name, [node2.memo_name])



tl = Timeline()

node0 = SwapNode('node0', tl)
node1 = SwapNode('node1', tl)
mid_node0 = QuantumRepeater('mid0', tl)
node0.set_seed(0)
node1.set_seed(1)
mid_node0.set_seed(2)
#node2 = SwapNode('node2', tl)
#mid_node1 = QuantumRepeater('mid1', tl)

#nodes: list[SwapNode | QuantumRepeater] = [node0, node1, node2, mid_node0, mid_node1]
nodes: list[SwapNode | QuantumRepeater] = [node0, node1, mid_node0]

for i in range(len(nodes)):
    for j in range(len(nodes)):
        if i != j:
            cc = ClassicalChannel(f'cc_{nodes[i].name}_{nodes[j].name}', tl, 1000, 1e9)
            cc.set_ends(nodes[i], nodes[j].name)

node0_memo: Memory = node0.components[node0.memo_name]
node1_memo: Memory = node1.components[node1.memo_name]
#node2_memo: Memory = node2.components[node2.memo_name]
mid0_left_memo: Memory = mid_node0.components[mid_node0.left_memo_name]
mid0_right_memo: Memory = mid_node0.components[mid_node0.right_memo_name]
#mid1_left_memo: Memory = mid_node1.components[mid_node1.left_memo_name]
#mid1_right_memo: Memory = mid_node1.components[mid_node1.right_memo_name]
entangle_memory(tl, node0_memo, mid0_left_memo, 0.9)
entangle_memory(tl, node1_memo, mid0_right_memo, 0.9)
#entangle_memory(tl, node1_memo, mid1_left_memo, 0.9)
#entangle_memory(tl, node2_memo, mid1_right_memo, 0.9)

for node in nodes:
    node.resource_manager.create_protocol()

#node1.resource_manager.create_protocol()

pair_protocol(node0, node1, mid_node0, [0, 0, 0])
#pair_protocol(node1, node2, mid_node1, [1, 0, 0])

print('--------')
print('Before swapping:')
print(tl.quantum_manager.states[0], '\n')
print(tl.quantum_manager.states[1], '\n')
print(tl.quantum_manager.states[2], '\n')
print(tl.quantum_manager.states[3], '\n')

print(node0_memo.entangled_memory)
print(mid0_left_memo.entangled_memory)
print(mid0_right_memo.entangled_memory)
print(node1_memo.entangled_memory)
print(node0_memo.fidelity)


tl.init()
nodes: list[SwapNode | QuantumRepeater] = [node0, node1, mid_node0]
for node in nodes:
    node.protocols[0].start()
tl.run()

print('--------')
print('after swapping:')
print(tl.quantum_manager.states[0], '\n')
print(tl.quantum_manager.states[1], '\n')
print(tl.quantum_manager.states[2], '\n')
print(tl.quantum_manager.states[3], '\n')

print(node0_memo.entangled_memory)
print(mid0_left_memo.entangled_memory)
print(mid0_right_memo.entangled_memory)
print(node1_memo.entangled_memory)
print(node0_memo.fidelity)
