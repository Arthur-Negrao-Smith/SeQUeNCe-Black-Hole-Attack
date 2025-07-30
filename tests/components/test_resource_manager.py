from components.network import Network
from components.nodes import QuantumRepeater
from components.utils.enums import Directions
from components.utils.constants import ENTANGLEMENT_SWAPPING_PROB
from sequence.entanglement_management.swapping import EntanglementSwappingA, EntanglementSwappingB
from sequence.entanglement_management.generation import EntanglementGenerationA
from sequence.kernel.timeline import Timeline
import pytest as pt


@pt.fixture
def network() -> Network:
    number_of_nodes: int = 3
    temp_network: Network = Network()
    temp_network.topology_generator.line_topology(number_of_nodes=number_of_nodes)

    return temp_network


class Test_Repeater_Manager:
    new_swap_prob: float | int = 0.7
    new_swap_prob_to_target: float | int = 0.5

    def test_get_memory(self) -> None:

        node: QuantumRepeater = QuantumRepeater(name="test_node", timeline=Timeline(), swap_prob=1.0)

        assert node.resource_manager.get_memory(Directions.LEFT).name  == node.left_memo_name
        assert node.resource_manager.get_memory(Directions.RIGHT).name == node.right_memo_name


    def test_creating_swapping_protocolA(self, network: Network) -> None:

        node: QuantumRepeater = network.nodes[0]

        node.resource_manager.create_swapping_protocolA()
        assert isinstance(node.get_protocol(), EntanglementSwappingA)


    def test_creating_swapping_protocolB(self, network: Network) -> None:

        node: QuantumRepeater = network.nodes[0]

        node.resource_manager.create_swapping_protocolB(Directions.RIGHT)
        assert isinstance(node.get_protocol(), EntanglementSwappingB)

        node.remove_used_protocol()
        node.resource_manager.create_swapping_protocolB(Directions.LEFT)
        assert isinstance(node.get_protocol(), EntanglementSwappingB)


    def test_creating_entanglement_protocol(self, network: Network) -> None:

        node: QuantumRepeater = network.nodes[0]
        node.resource_manager.create_entanglement_protocol(Directions.LEFT, 'middle_node', 'other_node')
        assert isinstance(node.get_protocol(), EntanglementGenerationA)

        node.remove_used_protocol()
        node.resource_manager.create_entanglement_protocol(Directions.RIGHT, 'middle_node', 'other_node')
        assert isinstance(node.get_protocol(), EntanglementGenerationA)


    def test_turn_black_hole(self, network: Network) -> None:

        nodeA: QuantumRepeater = network.nodes[0]
        nodeB: QuantumRepeater = network.nodes[1]
        nodeC: QuantumRepeater = network.nodes[2]

        nodeA.resource_manager._turn_black_hole(new_swap_prob=self.new_swap_prob, targets=None)
        assert nodeA._is_black_hole == True
        assert nodeA._swap_prob == self.new_swap_prob
        assert nodeA._black_hole_targets is None

        nodeB.resource_manager._turn_black_hole(new_swap_prob=self.new_swap_prob, targets={nodeA.name: self.new_swap_prob_to_target})
        assert nodeB._is_black_hole == True
        assert nodeB._swap_prob == ENTANGLEMENT_SWAPPING_PROB
        assert nodeB._black_hole_targets is not None
        assert nodeB._black_hole_targets[nodeA.name] == self.new_swap_prob_to_target

        nodeC.resource_manager._turn_black_hole(new_swap_prob=self.new_swap_prob, targets={nodeB.name: -1})
        assert nodeC._is_black_hole == True
        assert nodeC._black_hole_targets is not None
        assert nodeC._black_hole_targets[nodeB.name] == self.new_swap_prob


    def test_turn_normal_node(self, network: Network) -> None:


        nodeA: QuantumRepeater = network.nodes[0]
        nodeB: QuantumRepeater = network.nodes[1]
        nodeC: QuantumRepeater = network.nodes[2]

        nodeA.resource_manager._turn_black_hole(new_swap_prob=self.new_swap_prob, targets=None)
        nodeA.resource_manager._turn_normal_node(new_swap_prob=ENTANGLEMENT_SWAPPING_PROB)
        assert nodeA._is_black_hole == False
        assert nodeA._swap_prob == ENTANGLEMENT_SWAPPING_PROB
        assert nodeA._black_hole_targets is None

        nodeB.resource_manager._turn_black_hole(new_swap_prob=self.new_swap_prob, targets={nodeA.name: self.new_swap_prob_to_target})
        nodeB.resource_manager._turn_normal_node(new_swap_prob=ENTANGLEMENT_SWAPPING_PROB)
        assert nodeB._is_black_hole == False
        assert nodeB._swap_prob == ENTANGLEMENT_SWAPPING_PROB
        assert nodeB._black_hole_targets is None

        nodeC.resource_manager._turn_black_hole(new_swap_prob=self.new_swap_prob, targets={nodeB.name: -1})
        nodeC.resource_manager._turn_normal_node(new_swap_prob=ENTANGLEMENT_SWAPPING_PROB)
        assert nodeC._is_black_hole == False
        assert nodeC._swap_prob == ENTANGLEMENT_SWAPPING_PROB
        assert nodeC._black_hole_targets is None
