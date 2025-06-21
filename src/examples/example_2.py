from click import FLOAT
from sequence.kernel.timeline import Timeline
from sequence.topology.node import Node
from sequence.components.memory import Memory, MemoryArray
from sequence.components.optical_channel import ClassicalChannel
from sequence.entanglement_management.swapping import EntanglementSwappingA, EntanglementSwappingB
from sequence.message import Message
from sequence.protocol import Protocol
from zmq import MECHANISM


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



class SimpleManager:
    """
    Simple Resource Manager to create an entanglement swapping protocol
    """
    def __init__(self, owner: Node, memo_names: list[str]) -> None:
        self.owner: Node = owner
        self.memo_names: list[str] = memo_names
        self.raw_counter = 0
        self.ent_counter = 0

    def update(self, protocol: Protocol, memory: Memory, state: str) -> None:
        if state == 'RAW':
            self.raw_counter += 1
            memory.reset()
        else:
            self.ent_counter += 1

    def create_protocol(self) -> None:
        if type(self.owner) is QuantumRepeater:
            left_memo: Memory = self.owner.components[self.memo_names[0]]
            right_memo: Memory = self.owner.components[self.memo_names[1]]
            self.owner.protocols = [EntanglementSwappingA(self.owner, 
                                                          'ESA', 
                                                          left_memo, 
                                                          right_memo, 
                                                          ENTANGLEMENT_SWAPPING_PROB,  # type: ignore
                                                          SWAP_DEGRADATION)]
        else:
            memo: Memory = self.owner.components[self.memo_names[0]]
            self.owner.protocols = [EntanglementSwappingB(self.owner, f'{self.owner.name}.ESB', memo)]


class QuantumRepeater(Node):
    """
    Quantum Router to increase the entanglement range on the Network
    """
    def __init__(self, name: str, tl: Timeline) -> None:
        super().__init__(name, tl)
        left_memo_name: str = f'{name}.left_memo'
        right_memo_name: str = f'{name}.right_memo'
        left_memo: Memory = Memory(left_memo_name, tl, MEMORY_FIDELITY, MEMORY_FREQUENCY, MEMORY_EFFICIENCY, MEMORY_COHERENCE_TIME, MEMORY_WAVELENGTH)
        right_memo: Memory = Memory(right_memo_name, tl, MEMORY_FIDELITY, MEMORY_FREQUENCY, MEMORY_EFFICIENCY, MEMORY_COHERENCE_TIME, MEMORY_WAVELENGTH)
        self.add_component(left_memo)
        self.add_component(right_memo)

        self.resource_manager: SimpleManager = SimpleManager(self, [f"{self.name}[0]", f"{self.name}[1]"])

    def receive_message(self, src: str, msg: "Message") -> None:
        self.protocols[0].received_message(src, msg)


class SwapNode(Node):
    """
    Quantum Node to request Entanglement Swapping
    """
    def __init__(self, name: str, tl: Timeline) -> None:
        super().__init__(name, tl)
        self.memory_array: MemoryArray = MemoryArray(name=f"{self.owner.name}{MEMORY_ARRAY_NAME}",
                                                      timeline=self.owner.timeline, num_memories=MEMORY_ARRAY_SIZE,
                                                        fidelity=MEMORY_FIDELITY, frequency=MEMORY_FREQUENCY,
                                                        coherence_time=MEMORY_COHERENCE_TIME, wavelength=MEMORY_WAVELENGTH)
        memo_name: str = f'{name}.memo'
        memo = Memory(memo_name, tl, MEMORY_FIDELITY, MEMORY_FREQUENCY, MEMORY_EFFICIENCY, MEMORY_COHERENCE_TIME, MEMORY_WAVELENGTH)
        self.add_component(memo)

        self.resource_manager: SimpleManager = SimpleManager(self, [memo_name])

    def receive_message(self, src: str, msg: "Message") -> None:
        self.protocols[0].received_message(src, msg) # type: ignore

    def create_protocol(self) -> None:
        self.protocols: list[EntanglementSwappingB] = [EntanglementSwappingB(self, f'{self.name}.ESB', self.memo)] # type: ignore


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


def pair_protocol(node1, node2, node_mid) -> None:
    p1: EntanglementSwappingB = node1.protocols[0]
    p2: EntanglementSwappingB = node2.protocols[0]
    pmid: EntanglementSwappingA = node_mid.protocols[0]
    p1.set_others(pmid.name, node_mid.name,
                  [node_mid.resource_manager.memo_names[0], node_mid.resource_manager.memo_names[1]])
    p2.set_others(pmid.name, node_mid.name,
                  [node_mid.resource_manager.memo_names[0], node_mid.resource_manager.memo_names[1]])
    pmid.set_others(p1.name, node1.name, [node1.resource_manager.memo_names[0]])
    pmid.set_others(p2.name, node2.name, [node2.resource_manager.memo_names[0]])


"""
tl = Timeline()

left_node = SwapNode('left', tl)
right_node = SwapNode('right', tl)
mid_node = QuantumRepeater('mid', tl)
left_node.set_seed(0)
right_node.set_seed(1)
mid_node.set_seed(2)

nodes: list[SwapNode | QuantumRepeater] = [left_node, right_node, mid_node]

for i in range(3):
    for j in range(3):
        if i != j:
            cc = ClassicalChannel(f'cc_{nodes[i].name}_{nodes[j].name}', tl, 1000, 1e9)
            cc.set_ends(nodes[i], nodes[j].name)

left_memo = left_node.components[left_node.resource_manager.memo_names[0]]
right_memo = right_node.components[right_node.resource_manager.memo_names[0]]
mid_left_memo = mid_node.components[mid_node.resource_manager.memo_names[0]]
mid_right_memo = mid_node.components[mid_node.resource_manager.memo_names[1]]
entangle_memory(tl, left_memo, mid_left_memo, 0.9)
entangle_memory(tl, right_memo, mid_right_memo, 0.9)

for node in nodes:
    node.resource_manager.create_protocol()

pair_protocol(left_node, right_node, mid_node)

print('--------')
print('Before swapping:')
print(tl.quantum_manager.states[0], '\n')
print(tl.quantum_manager.states[1], '\n')
print(tl.quantum_manager.states[2], '\n')
print(tl.quantum_manager.states[3], '\n')

print(left_memo.entangled_memory)
print(mid_left_memo.entangled_memory)
print(mid_right_memo.entangled_memory)
print(right_memo.entangled_memory)
print(left_memo.fidelity)


tl.init()
for node in nodes:
    node.protocols[0].start()
tl.run()

print('--------')
print('after swapping:')
print(tl.quantum_manager.states[0], '\n')
print(tl.quantum_manager.states[1], '\n')
print(tl.quantum_manager.states[2], '\n')
print(tl.quantum_manager.states[3], '\n')

print(left_memo.entangled_memory)
print(mid_left_memo.entangled_memory)
print(mid_right_memo.entangled_memory)
print(right_memo.entangled_memory)
print(left_memo.fidelity)"""
