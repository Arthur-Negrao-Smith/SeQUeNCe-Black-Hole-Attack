from sequence.topology.topology import Node
from sequence.protocol import Protocol
from sequence.components.memory import Memory
from sequence.entanglement_management.swapping import EntanglementSwappingA, EntanglementSwappingB
from sequence.entanglement_management.generation import EntanglementGenerationA

from components.nodes import QuantumRepeater

from .utils.constants import SWAP_DEGRADATION
from .utils.enums import Directions

from abc import ABC, abstractmethod
from typing import Type

class BaseManager(ABC):
    """
    Base Manager to create to entanglement swapping managers
    """
    def __init__(self, owner: QuantumRepeater) -> None:
        self.owner: QuantumRepeater = owner
        self.raw_counter: int = 0
        self.ent_counter: int = 0

    def update(self, protocol: Type[Protocol], memory: Memory, state: str) -> None:
        if state == 'RAW':
            self.raw_counter += 1
            memory.reset()
        else:
            self.ent_counter += 1

    @abstractmethod
    def get_memory(self, memory_position: Directions) -> Memory:
        pass


class RepeaterManager(BaseManager):
    """
    Manager to control entanglement and entanglement swapping in repeater nodes
    """
    from .nodes import QuantumRepeater
    def __init__(self, owner: QuantumRepeater) -> None:
        super().__init__(owner)

    def create_swapping_protocolA(self) -> None:
        """
        Create a protocol to perform the entanglement swapping at the middle node.
        """
        left_memo: Memory = self.owner.components[self.owner.left_memo_name]
        right_memo: Memory = self.owner.components[self.owner.right_memo_name]
        protocol: EntanglementSwappingA = EntanglementSwappingA(self.owner, 
                                                        f'{self.owner.name}.Entanglement_SwappingA', 
                                                        left_memo, 
                                                        right_memo, 
                                                        self.owner.swap_prob,
                                                        SWAP_DEGRADATION)
        self.owner.protocols.append(protocol)
        
    def create_swapping_protocolB(self, memory_position: Directions) -> None:
        """
        Create a protocol to perform the entanglement swapping at the side node.

        Args:
            memory_position (Directions): Position of the memory to entanglement (left or right)
        """
        if memory_position == Directions.LEFT:
            left_memo: Memory = self.owner.components[self.owner.left_memo_name]
            protocol: EntanglementSwappingB = EntanglementSwappingB(self.owner, f'{self.owner.name}.Entanglement_SwappingB', left_memo)
            self.owner.protocols.append(protocol)
        
        elif memory_position == Directions.RIGHT:
            right_memo: Memory = self.owner.components[self.owner.right_memo_name]
            protocol: EntanglementSwappingB = EntanglementSwappingB(self.owner, f'{self.owner.name}.Entanglement_SwappingB', right_memo)
            self.owner.protocols.append(protocol)

    def create_entanglement_protocol(self, memory_position: Directions, middle_node: str, other_node: str) -> None:
        """
        Create a protocol to perform the entanglement at the side node.

        Args:
            memory_position (Directions): Position of the memory to entanglement (left or right)
            middle_node (str): Name of the BSMNode that will generate the entanglement.
            other_node (str): Name of the RepeaterNode that will be entangled.
        """
        if memory_position == Directions.LEFT:
            memory: Memory = self.owner.components[self.owner.left_memo_name]
        else:
            memory: Memory = self.owner.components[self.owner.right_memo_name]
        protocol: EntanglementGenerationA = EntanglementGenerationA(self.owner, f"{self.owner.name}.Entanglement_GenerationA", 
                                                                    middle_node, other_node, memory)
        self.owner.protocols.append(protocol)

    def get_memory(self, memory_position: Directions) -> Memory:
        if memory_position == Directions.LEFT:
            return self.owner.components[self.owner.left_memo_name]
        else:
            return self.owner.components[self.owner.right_memo_name]