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

def network_with_seed() -> Network:
    start_seed: int = 0

    number_of_nodes: int = 10
    network: Network = Network(start_seed=start_seed)
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


    def test_reproducibility_for_black_hole_without_targets_creation(self) -> None:

        network_1: Network = network_with_seed()
        network_1.attack_manager.create_black_holes(number_of_black_holes=self.number_of_black_holes, swap_prob=self.swap_prob, targets_per_black_hole=0)

        network_2: Network = network_with_seed()
        network_2.attack_manager.create_black_holes(number_of_black_holes=self.number_of_black_holes, swap_prob=self.swap_prob, targets_per_black_hole=0)

        assert len(network_1.black_holes) == len(network_2.black_holes)
        assert network_1.black_holes.keys() == network_2.black_holes.keys()
 
        network_1_bha: QuantumRepeater = list(network_1.black_holes.values())[0]
        network_2_bha: QuantumRepeater = list(network_1.black_holes.values())[0]

        assert (network_1_bha._black_hole_targets is None) and (network_2_bha._black_hole_targets is None)
        assert network_1_bha._swap_prob == network_2_bha._swap_prob


    def test_reproducibility_for_black_hole_with_targets_creation(self) -> None:

        network_1: Network = network_with_seed()
        network_1.attack_manager.create_black_holes(number_of_black_holes=self.number_of_black_holes, swap_prob=self.swap_prob, targets_per_black_hole=self.targets_per_black_hole)

        network_2: Network = network_with_seed()
        network_2.attack_manager.create_black_holes(number_of_black_holes=self.number_of_black_holes, swap_prob=self.swap_prob, targets_per_black_hole=self.targets_per_black_hole)

        assert len(network_1.black_holes) == len(network_2.black_holes)
        assert network_1.black_holes.keys() == network_2.black_holes.keys()

        network_1_bha: QuantumRepeater = list(network_1.black_holes.values())[0]
        network_2_bha: QuantumRepeater = list(network_1.black_holes.values())[0]

        assert network_1_bha._black_hole_targets == network_2_bha._black_hole_targets
        assert network_1_bha._swap_prob == network_2_bha._swap_prob
