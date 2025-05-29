# Nodes and Memory
from sequence.topology.node import Node
from sequence.topology.node import BSMNode
from sequence.components.memory import Memory

# Channels
from sequence.components.optical_channel import QuantumChannel, ClassicalChannel

# Protocols
from sequence.entanglement_management.entanglement_protocol import EntanglementProtocol
from sequence.entanglement_management.generation import EntanglementGenerationA

# Kernel components
from sequence.kernel.timeline import Timeline

# Constant
RAW: str = 'RAW'
MEM_FIDELITY: float = 0.9
MEM_FREQUENCY: int = 2000
MEM_EFFICIENCY: float = 1
MEM_COHERENCE_TIME: int = -1
MEM_WAVELENGHT: int = 500


class SimpleManager:
    """
    Class to create entanglement protocol and monitor their success
    """
    def __init__(self, owner: Node, memo_name: str) -> None:
        self.owner: Node = owner
        self.memo_name: str = memo_name
        self.raw_counter: int = 0
        self.ent_counter: int = 0

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