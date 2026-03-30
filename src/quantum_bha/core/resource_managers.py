from __future__ import annotations
from typing import Type, TYPE_CHECKING

from sequence.protocol import Protocol
from sequence.components.memory import Memory
from abc import ABC, abstractmethod
import logging

from ..utils.enums import Directions

if TYPE_CHECKING:
    from .node import QuantumRepeater

log: logging.Logger = logging.getLogger(__name__)


class BaseManager(ABC):
    """
    Base Manager to create to resource managers.
    """

    def __init__(self, owner: QuantumRepeater) -> None:
        self._owner: QuantumRepeater | None = owner
        self.raw_counter: int = 0
        self.ent_counter: int = 0

    @property
    def owner(self) -> QuantumRepeater:
        if self._owner is None:
            raise RuntimeError("The owner has been destroyed")
        return self._owner

    def update(self, protocol: Type[Protocol], memory: Memory, state: str) -> None:
        if state == "RAW":
            self.raw_counter += 1
            memory.reset()
        else:
            self.ent_counter += 1

    def destroy(self) -> None:
        """
        Destroy node reference
        """
        self._owner = None

    @abstractmethod
    def get_memory(self, memory_position: Directions) -> Memory:
        pass


class RepeaterManager(BaseManager):
    """
    Manager to control the resources to perform entanglements and entanglements swapping in repeater nodes.
    """

    def __init__(self, owner: QuantumRepeater) -> None:
        super().__init__(owner)
        log.debug(f"Repeater Manager initiated in {self.owner.name}")

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
