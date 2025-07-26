from components.network import Network
from components.nodes import QuantumRepeater
from components.utils.enums import Attack_Types
import pytest as pt

@pt.fixture
def network() -> Network:
    number_of_nodes: int = 10
    network: Network = Network()
    network.topology_generator.line_topology(number_of_nodes)

    return network


class Test_Attack_Manager:
    number_of_black_holes: int = 4
    swap_prob: float = 0.2
    targets_per_black_hole: int = 3


    def test_number_of_black_holes(self, network: Network) -> None:

        assert network.black_holes == dict()

        network.attack_manager.create_black_holes(number_of_black_holes=self.number_of_black_holes, swap_prob=self.swap_prob, targets_per_black_hole=0)

        assert len(network.black_holes) == self.number_of_black_holes


    def test_number_of_black_holes_in_get_black_holes(self, network: Network) -> None:

        assert network.attack_manager.get_black_holes() == dict()

        network.attack_manager.create_black_holes(number_of_black_holes=self.number_of_black_holes, swap_prob=self.swap_prob, targets_per_black_hole=0)

        assert len(network.attack_manager.get_black_holes()) == self.number_of_black_holes


    def test_black_hole_attack_type(self, network: Network) -> None:

        network.attack_manager.create_black_holes(number_of_black_holes=self.number_of_black_holes, swap_prob=self.swap_prob, targets_per_black_hole=0)

        assert network.attack_manager._attack_type == Attack_Types.BLACK_HOLE


    def test_number_of_targets_per_black_hole(self, network: Network) -> None:

        network.attack_manager.create_black_holes(number_of_black_holes=self.number_of_black_holes, swap_prob=self.swap_prob, targets_per_black_hole=self.targets_per_black_hole)
        tmp_bha: QuantumRepeater = tuple(network.black_holes.values())[0]

        assert tmp_bha._black_hole_targets is not None
        assert len(tmp_bha._black_hole_targets) == self.targets_per_black_hole


    def test_attack_manager_destroy_to_remove_network(self, network: Network) -> None:

        network.attack_manager.destroy()

        assert network.attack_manager.network is None
