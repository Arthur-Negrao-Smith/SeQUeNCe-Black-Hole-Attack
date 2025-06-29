from sequence.protocol import Protocol
from sequence.components.memory import Memory
from sequence.entanglement_management.swapping import EntanglementSwappingA, EntanglementSwappingB
from sequence.entanglement_management.generation import EntanglementGenerationA

from components.nodes import QuantumRepeater

from .utils.constants import SWAP_DEGRADATION
from .utils.enums import Directions

from abc import ABC, abstractmethod
from typing import Type
import logging

log: logging.Logger = logging.getLogger(__name__)

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
        log.debug(f"Repeater Manager initiated in {self.owner.name}")

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
                                                        self.owner._swap_prob, # type: ignore
                                                        SWAP_DEGRADATION)

        node_left_name: str | None = left_memo.entangled_memory['node_id']
        # if is entangled
        if node_left_name is not None and node_left_name:
            # if node have targets to atack and left node is a target
            if (self.owner._black_hole_targets is not None) and (node_left_name in self.owner._black_hole_targets.keys()):
                protocol = EntanglementSwappingA(self.owner, 
                                            f'{self.owner.name}.Entanglement_SwappingA', 
                                            left_memo, 
                                            right_memo, 
                                            self.owner._black_hole_targets[node_left_name], # type: ignore
                                            SWAP_DEGRADATION)


        self.owner.protocols.append(protocol)
        
    def create_swapping_protocolB(self, memory_position: Directions) -> None:
        """
        Create a protocol to perform the entanglement swapping at the side node.

        Args:
            memory_position (Directions): Position of the memory to entanglement (Directions.LEFT or Directions.RIGHT)
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
            memory_position (Directions): Position of the memory to entanglement (Directions.LEFT or Directions.RIGHT).
            middle_node (str): BSMNode's name that will generate the entanglement.
            other_node (str): RepeaterNode's nanme that will be entangled.
        """
        memory: Memory = self.get_memory(memory_position)
        
        protocol: EntanglementGenerationA = EntanglementGenerationA(self.owner, f"{self.owner.name}.Entanglement_GenerationA", 
                                                                    middle_node, other_node, memory)
        self.owner.protocols.append(protocol)

    def get_memory(self, memory_position: Directions) -> Memory:
        """
        Get the node's memory

        Args:
            memory_position (Directions): Position of the memory to entanglement (left or right)

        Retuns:
            Memory: Memory of the node
        """
        if memory_position == Directions.LEFT:
            return self.owner.components[self.owner.left_memo_name]
        else:
            return self.owner.components[self.owner.right_memo_name]

    def _update_swap_prob(self, new_swap_prob: float | int) -> None:
        """
        Update the node's entanglement swapping probability

        Args:
            new_swap_prob (float): New entanglement swapping probability
        """
        self.owner._swap_prob = new_swap_prob

    def _turn_black_hole(self, new_swap_prob: float | int, targets: dict[str, float | int] | None) -> None:
        """
        Turn the node in a black hole to affect pwapping protocol A

        Args:
            new_swap_prob (float | int): New entanglement probability
            targets (list[int]): Black hole's targets with node ID and probability for this node. If prob == -1, then new_swap_prob will be aplied
        """
        self.owner._is_black_hole = True

        # don't have targets
        if targets is None:
            self._update_swap_prob(new_swap_prob)
            return
        
        # if target's dict doens't exists
        if self.owner._black_hole_targets is None:
            self.owner._black_hole_targets = dict()

        # loop to add targets and probabilities
        for node_name, prob in targets.items():
            if prob == -1:
                self.owner._black_hole_targets[node_name] = new_swap_prob
            else:
                self.owner._black_hole_targets[node_name] = prob

    def _turn_normal_node(self, new_swap_prob: int | float) -> None:
        """
        Turn the black hole in a normal node

        Args:
            new_swap_prob (int | float): New entanglement probability
        """
        self.owner._is_black_hole = False
        self.owner._black_hole_targets = None
        self._update_swap_prob(new_swap_prob)
