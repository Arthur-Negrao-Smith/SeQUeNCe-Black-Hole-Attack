from sequence.topology.topology import Node
from sequence.protocol import Protocol
from sequence.components.memory import Memory
from sequence.entanglement_management.swapping import EntanglementSwappingA, EntanglementSwappingB

from .nodes import QuantumRepeater
from .utils.constant import SWAP_DEGRADATION
from .utils.enums import Directions

from abc import ABC
from typing import Type

class BaseManager(ABC):
    """
    Base Manager to create to entanglement swapping managers
    """
    def __init__(self, owner: Node) -> None:
        self.owner: Node = owner
        self.raw_counter: int = 0
        self.ent_counter: int = 0

    def update(self, protocol: Type[Protocol], memory: Memory, state: str) -> None:
        if state == 'RAW':
            self.raw_counter += 1
            memory.reset()
        else:
            self.ent_counter += 1


class RepeaterManager(BaseManager):
    """
    Manager to control entanglement swapping in repeater nodes
    """
    def __init__(self, owner: Type[QuantumRepeater]) -> None:
        super().__init__(owner)

    def create_swapping_protocolA(self) -> None:
        """
        Create a Protocol to realize the entanglement swapping in mid node
        """
        left_memo: Memory = self.owner.components[self.owner.left_memo_name]
        right_memo: Memory = self.owner.components[self.owner.right_memo_name]
        protocol: EntanglementSwappingA = EntanglementSwappingA(self.owner, 
                                                        f'{self.owner.name}.ESA', 
                                                        left_memo, 
                                                        right_memo, 
                                                        self.owner.swap_prob,
                                                        SWAP_DEGRADATION)
        self.owner.protocols.append(protocol)
        
    def create_swapping_protocolB(self, memory_position: str) -> None:
        """
        Create a Protocol to Entanglement a memory in side node

        Args:
            memory_position (str): Position of the memory to entanglement (left or right)
        """
        if memory_position == Directions.LEFT:
            left_memo: Memory = self.owner.components[self.owner.left_memo_name]
            protocol: EntanglementSwappingB = EntanglementSwappingB(self.owner, f'{self.owner.name}.ESB', left_memo)
            self.owner.protocols.append(protocol)
        
        elif memory_position == Directions.RIGHT:
            right_memo: Memory = self.owner.components[self.owner.right_memo_name]
            protocol: EntanglementSwappingB = EntanglementSwappingB(self.owner, f'{self.owner.name}.ESB', right_memo)
            self.owner.protocols.append(protocol)