from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.node import QuantumRepeater


class AttackFactory:
    """
    Factory responsible for create and apply behaviors into nodes.
    """

    @staticmethod
    def turn_into_black_hole(
        node: QuantumRepeater, swap_prob: float, targets: dict[str, float] | None = None
    ) -> None:
        """
        Turn a default node in a black hole node.
        """
        from .behavior import BHBehavior

        bh_behavior = BHBehavior(node, swap_prob, targets)
        node.set_behavior(bh_behavior)

    @staticmethod
    def turn_into_hijacked(
        node: QuantumRepeater, helpers: tuple[int, ...] | None = None
    ) -> None:
        """
        Turn a default node in a hijacked node.
        """
        from .behavior import HijackedBehavior

        hijacked_behavior = HijackedBehavior(node, helpers)
        node.set_behavior(hijacked_behavior)

    @staticmethod
    def restore_normal(node: QuantumRepeater) -> None:
        """
        Removes the any attack behavior and restore the default behavior.
        """
        from .behavior import DefaultBehavior

        normal_behavior = DefaultBehavior(node)
        node.set_behavior(normal_behavior)
