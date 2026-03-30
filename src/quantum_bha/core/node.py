from __future__ import annotations
from typing import TYPE_CHECKING, Type

from sequence.kernel.timeline import Timeline
from sequence.topology.node import Node
from sequence.components.memory import Memory
from sequence.entanglement_management.entanglement_protocol import EntanglementProtocol
from sequence.message import Message
from sequence.components.photon import Photon

from ..utils.constants import (
    MEMORY_FIDELITY,
    MEMORY_FREQUENCY,
    MEMORY_EFFICIENCY,
    MEMORY_COHERENCE_TIME,
    MEMORY_WAVELENGTH,
)

if TYPE_CHECKING:
    from ..attack.behavior import NodeBehavior

from ..attack.behavior import DefaultBehavior


class QuantumRepeater(Node):
    """
    Quantum Router to increase the entanglement range on the Network
    """

    def __init__(self, name: str, timeline: Timeline, swap_prob: float) -> None:
        """
        Constructor for QuantumRepeater

        Args:
            name (str): Node's name
            timeline (Timeline): Timeline to create events
            swap_prob (float): Entanglement Swapping probability
        """
        super().__init__(name, timeline)

        # create memories
        self.left_memo_name: str = f"{name}.left_memo"
        self.right_memo_name: str = f"{name}.right_memo"

        left_memo: Memory = Memory(
            self.left_memo_name,
            timeline,
            MEMORY_FIDELITY,
            MEMORY_FREQUENCY,
            MEMORY_EFFICIENCY,
            MEMORY_COHERENCE_TIME,
            MEMORY_WAVELENGTH,
        )
        right_memo: Memory = Memory(
            self.right_memo_name,
            timeline,
            MEMORY_FIDELITY,
            MEMORY_FREQUENCY,
            MEMORY_EFFICIENCY,
            MEMORY_COHERENCE_TIME,
            MEMORY_WAVELENGTH,
        )

        left_memo.add_receiver(self)
        right_memo.add_receiver(self)

        self.add_component(left_memo)
        self.add_component(right_memo)

        # Manager to control resources
        from .resource_managers import RepeaterManager

        self.resource_manager: RepeaterManager = RepeaterManager(self)

        # initial node behavior
        self.behavior: NodeBehavior = DefaultBehavior(self)

        # initial entanglement swapping probability
        self._swap_prob: float | int = swap_prob

        # initial state isn't a bh (black hole)
        self._is_black_hole: bool = False

        # black hole's targets: If target is None, then bha affect all requests, else just affect target
        self._black_hole_targets: dict[str, float | int] | None = None

    def destroy(self) -> None:
        """
        Cleanup all references and data
        """
        self.cchannels.clear()
        self.qchannels.clear()
        self.protocols.clear()
        self.components.clear()
        self._black_hole_targets = None
        self.resource_manager.destroy()

    def receive_message(self, src: str, msg: Message) -> None:
        self.protocols[0].received_message(src, msg)

    def get(self, photon: Photon, **kwargs) -> None:  # type: ignore
        self.send_qubit(kwargs["dst"], photon)

    def run_protocol(self) -> None:
        """
        Start first protocol in the queue
        """
        self.protocols[0].start()

    def get_protocol(self) -> Type[EntanglementProtocol]:
        """
        Get the first protocol on the queue
        """
        return self.protocols[0]

    def remove_used_protocol(self) -> None:
        """
        Remove first protocol on the queue
        """
        self.protocols.pop(0)

    def set_behavior(self, behavior: NodeBehavior) -> None:
        """
        Set the default node's behavior.

        Args:
            behavior (NodeBehavior): The new behavior.
        """
        self.behavior = behavior

    @property
    def swap_prob(self) -> float:
        """
        Get the default entanglement swapping probability

        Returns:
            float: Return the default entanglement swapping probability
        """
        return self._swap_prob

    @swap_prob.setter
    def swap_prob(self, new_prob: float | int) -> None:
        """
        Set the default entanglement swapping probability

        Args:
            new_prob (float | int): New entanglement swapping probability
        """
        self._swap_prob = new_prob
