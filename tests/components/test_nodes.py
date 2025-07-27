from components.nodes import QuantumRepeater
from components.utils.enums import Directions
from sequence.kernel.timeline import Timeline
from sequence.entanglement_management.swapping import EntanglementSwappingA
import pytest as pt

@pt.fixture
def node() -> QuantumRepeater:
    swap_prob: int | float = 1
    temp_node: QuantumRepeater = QuantumRepeater(name='test_node', timeline=Timeline(), swap_prob=swap_prob)
    temp_node.protocols.append(EntanglementSwappingA(temp_node, "test_protocol", 
                                                     temp_node.resource_manager.get_memory(Directions.LEFT), 
                                                     temp_node.resource_manager.get_memory(Directions.RIGHT)))
    return temp_node

class Test_QuantumRepeater:
    
    def test_destroy_node(self, node: QuantumRepeater) -> None:

        node.destroy()

        assert node.protocols  == []
        assert node.components == {}
        assert node.cchannels  == {}
        assert node.qchannels  == {}
        assert node._black_hole_targets is None
        assert node.resource_manager._owner is None


    def test_get_protocol(self, node: QuantumRepeater) -> None:

        assert isinstance(node.get_protocol(), EntanglementSwappingA)


    def test_remove_used_protocol(self, node: QuantumRepeater) -> None:

        node.remove_used_protocol()
        assert node.protocols == []

