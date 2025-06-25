from sequence.kernel.timeline import Timeline
from sequence.topology.node import Node
from sequence.components.memory import Memory
from sequence.protocol import Message, Protocol

from .managers import RepeaterManager
from .utils.constant import MEMORY_FIDELITY, MEMORY_FREQUENCY, MEMORY_EFFICIENCY, MEMORY_COHERENCE_TIME, MEMORY_WAVELENGTH

from typing import Type

class QuantumRepeater(Node):
    """
    Quantum Router to increase the entanglement range on the Network
    """
    def __init__(self, name: str, tl: Timeline, swap_prob: float) -> None:
        super().__init__(name, tl)

        self.left_memo_name: str = f'{name}.left_memo'
        self.right_memo_name: str = f'{name}.right_memo'

        left_memo: Memory = Memory(self.left_memo_name, tl, MEMORY_FIDELITY, MEMORY_FREQUENCY, MEMORY_EFFICIENCY, MEMORY_COHERENCE_TIME, MEMORY_WAVELENGTH)
        right_memo: Memory = Memory(self.right_memo_name, tl, MEMORY_FIDELITY, MEMORY_FREQUENCY, MEMORY_EFFICIENCY, MEMORY_COHERENCE_TIME, MEMORY_WAVELENGTH)
        
        self.add_component(left_memo)
        self.add_component(right_memo)

        self.resource_manager: RepeaterManager = RepeaterManager(self)

        self.swap_prob: float = swap_prob

    def receive_message(self, src: str, msg: Type[Message]) -> None:
        self.protocols[0].received_message(src, msg)

    def run_protocol(self) -> None:
        """
        Start first protocol in the queue
        """
        self.protocols[0].start()

    def get_protocol(self) -> Type[Protocol]:
        """
        Get the first protocol on the queue
        """
        return self.protocols[0]
    
    def remove_used_protocol(self) -> None:
        """
        remove first protocol on the queue
        """
        self.protocols.pop(0)
