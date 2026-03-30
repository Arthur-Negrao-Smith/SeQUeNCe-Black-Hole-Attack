from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from weakref import ReferenceType, ref

from sequence.network_management.reservation import (
    EntanglementGenerationA,
    EntanglementSwappingA,
    EntanglementSwappingB,
)
from sequence.topology.node import Memory

from .utils.constants import SWAP_DEGRADATION
from .utils.enums import Directions

if TYPE_CHECKING:
    from .nodes import QuantumRepeater


class NodeBehavior(ABC):
    """
    Base interface to behavior of nodes (Normal or Attack).
    """

    def __init__(self, owner: QuantumRepeater) -> None:
        self._owner_ref: ReferenceType[QuantumRepeater] = ref(owner)

    @property
    def owner(self) -> QuantumRepeater:
        """
        Get the owner node reference.
        """
        owner: QuantumRepeater | None = self._owner_ref()
        if owner is None:
            raise RuntimeError("The owner node has been destroyed")

        return owner

    @abstractmethod
    def create_swapping_protocolA(self) -> None:
        """
        Create a protocol to perform the entanglement swapping at the middle node.
        """
        pass

    def create_swapping_protocolB(self, memory_position: Directions) -> None:
        """
        Create a protocol to perform the entanglement swapping at the side node.

        Args:
            memory_position (Directions): Position of the memory to entanglement (Directions.LEFT or Directions.RIGHT).
        """
        if memory_position == Directions.LEFT:
            left_memo: Memory = self.owner.resource_manager.get_memory(Directions.LEFT)
            protocol: EntanglementSwappingB = EntanglementSwappingB(
                self.owner, f"{self.owner.name}.Entanglement_SwappingB", left_memo
            )
            self.owner.protocols.append(protocol)

        elif memory_position == Directions.RIGHT:
            right_memo: Memory = self.owner.resource_manager.get_memory(
                Directions.RIGHT
            )
            protocol: EntanglementSwappingB = EntanglementSwappingB(
                self.owner, f"{self.owner.name}.Entanglement_SwappingB", right_memo
            )
            self.owner.protocols.append(protocol)

    def create_entanglement_protocol(
        self, memory_position: Directions, middle_node: str, other_node: str
    ) -> None:
        """
        Create a protocol to perform the entanglement at the side node.

        Args:
            memory_position (Directions): Position of the memory to entanglement (Directions.LEFT or Directions.RIGHT).
            middle_node (str): BSMNode's name that will generate the entanglement.
            other_node (str): RepeaterNode's nanme that will be entangled.
        """
        memory: Memory = self.owner.resource_manager.get_memory(memory_position)

        protocol: EntanglementGenerationA = EntanglementGenerationA(
            self.owner,
            f"{self.owner.name}.Entanglement_GenerationA",
            middle_node,
            other_node,
            memory,
        )
        self.owner.protocols.append(protocol)


class DefaultBehavior(NodeBehavior):
    """
    Default Quantum Repeater behavior.
    """

    def __init__(self, owner: QuantumRepeater) -> None:
        super().__init__(owner)

    def create_swapping_protocolA(self) -> None:
        left_memo: Memory = self.owner.resource_manager.get_memory(Directions.LEFT)
        right_memo: Memory = self.owner.resource_manager.get_memory(Directions.RIGHT)
        protocol: EntanglementSwappingA = EntanglementSwappingA(
            self.owner,
            f"{self.owner.name}.Entanglement_SwappingA",
            left_memo,
            right_memo,
            self.owner.swap_prob,  # type: ignore
            SWAP_DEGRADATION,
        )

        self.owner.protocols.append(protocol)


class BHBehaviour(NodeBehavior):
    """
    Black Hole Repeater behavior.
    """

    def __init__(
        self,
        owner: QuantumRepeater,
        swap_prob: float | int | None = None,
        black_hole_targets: dict[str, float | int] | None = None,
    ) -> None:
        super().__init__(owner)

        if swap_prob is not None:
            self.owner.swap_prob = swap_prob

        self._black_hole_targets: dict[str, float | int] | None = black_hole_targets

    def create_swapping_protocolA(self) -> None:
        left_memo: Memory = self.owner.resource_manager.get_memory(Directions.LEFT)
        right_memo: Memory = self.owner.resource_manager.get_memory(Directions.RIGHT)
        protocol: EntanglementSwappingA = EntanglementSwappingA(
            self.owner,
            f"{self.owner.name}.Entanglement_SwappingA",
            left_memo,
            right_memo,
            self.owner.swap_prob,  # type: ignore
            SWAP_DEGRADATION,
        )

        # if the attacker has a specify entanglement swapping probability for this node
        node_left_name: str | None = left_memo.entangled_memory["node_id"]

        # if is entangled
        if node_left_name is not None and node_left_name:
            # if node have targets to atack and left node is a target
            if (self._black_hole_targets is not None) and (
                node_left_name in self._black_hole_targets.keys()
            ):
                protocol = EntanglementSwappingA(
                    self.owner,
                    f"{self.owner.name}.Entanglement_SwappingA",
                    left_memo,
                    right_memo,
                    self._black_hole_targets[node_left_name],  # type: ignore
                    SWAP_DEGRADATION,
                )

        self.owner.protocols.append(protocol)
