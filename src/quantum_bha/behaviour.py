from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from weakref import ReferenceType, ref

from sequence.network_management.reservation import (
    EntanglementSwappingA,
    EntanglementSwappingB,
)
from sequence.topology.node import Memory

from quantum_bha.nodes import QuantumRepeater
from quantum_bha.utils.constants import SWAP_DEGRADATION
from quantum_bha.utils.enums import Directions

if TYPE_CHECKING:
    from .resource_managers import RepeaterManager


class NodeBehavior(ABC):
    """
    Base interface to behaviour of nodes (Normal or Attack).
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
            left_memo: Memory = self.owner.components[self.owner.left_memo_name]
            protocol: EntanglementSwappingB = EntanglementSwappingB(
                self.owner, f"{self.owner.name}.Entanglement_SwappingB", left_memo
            )
            self.owner.protocols.append(protocol)

        elif memory_position == Directions.RIGHT:
            right_memo: Memory = self.owner.components[self.owner.right_memo_name]
            protocol: EntanglementSwappingB = EntanglementSwappingB(
                self.owner, f"{self.owner.name}.Entanglement_SwappingB", right_memo
            )
            self.owner.protocols.append(protocol)


class BHABehaviour(NodeBehavior):
    def __init__(
        self,
        owner: QuantumRepeater,
        swap_prob: float | int | None = None,
        black_hole_targets: dict[str, float | int] | None = None,
    ) -> None:
        super().__init__(owner)

        if swap_prob is not None:
            self.owner._swap_prob = swap_prob

        self._black_hole_targets: dict[str, float | int] | None = black_hole_targets

    def create_swapping_protocolA(self) -> None:
        left_memo: Memory = self.owner.components[self.owner.left_memo_name]
        right_memo: Memory = self.owner.components[self.owner.right_memo_name]
        protocol: EntanglementSwappingA = EntanglementSwappingA(
            self.owner,
            f"{self.owner.name}.Entanglement_SwappingA",
            left_memo,
            right_memo,
            self.owner._swap_prob,  # type: ignore
            SWAP_DEGRADATION,
        )

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
                    self.owner._black_hole_targets[node_left_name],  # type: ignore
                    SWAP_DEGRADATION,
                )

        self.owner.protocols.append(protocol)
