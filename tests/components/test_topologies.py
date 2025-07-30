from components.network import Network
from components.utils.enums import Topologies
import pytest as pt


@pt.fixture
def network() -> Network:
    return Network()


class Test_TopologyGen:
    number_of_nodes: int = 9
    number_of_rows: int = 3
    number_of_columns: int = 3
    prob_edge_creation: float = 0.5
    edges_to_attach: int = 3
    seed_test: int = 0


    def test_grid_topology_number_of_nodes_and_topology_name(self, network: Network) -> None:

        network.topology_generator.grid_topology(rows=3, columns=3)

        assert network.number_of_nodes == self.number_of_nodes
        assert network.topology == Topologies.GRID


    def test_ring_topology_number_of_nodes_and_topology_name(self, network: Network) -> None:

        network.topology_generator.ring_topology(number_of_nodes=self.number_of_nodes)

        assert network.number_of_nodes == self.number_of_nodes
        assert network.topology == Topologies.RING


    def test_star_topology_number_of_nodes_and_topology_name(self, network: Network) -> None:

        network.topology_generator.star_topology(number_of_nodes=self.number_of_nodes)

        assert network.number_of_nodes == self.number_of_nodes
        assert network.topology == Topologies.STAR


    def test_line_topology_number_of_nodes_and_topology_name(self, network: Network) -> None:

        network.topology_generator.line_topology(number_of_nodes=self.number_of_nodes)

        assert network.number_of_nodes == self.number_of_nodes
        assert network.topology == Topologies.LINE


    def test_erdos_renyi_topology_number_of_nodes_and_topology_name(self, network: Network) -> None:

        network.topology_generator.erdos_renyi_topology(number_of_nodes=self.number_of_nodes, prob_edge_creation=self.prob_edge_creation)

        assert network.number_of_nodes == self.number_of_nodes
        assert network.topology == Topologies.ERDOS_RENYI


    def test_barabasi_albert_topology_number_of_nodes_and_topology_name(self, network: Network) -> None:

        network.topology_generator.barabasi_albert_topology(number_of_nodes=self.number_of_nodes, edges_to_attach=self.edges_to_attach)

        assert network.number_of_nodes == self.number_of_nodes
        assert network.topology == Topologies.BARABASI_ALBERT


    def test_destroy_TopologyGen(self, network: Network) -> None:

        network.topology_generator.destroy()

        assert network.topology_generator.network is None


    def test_reproducibility_of_erdos_renyi(self) -> None:

        network_1: Network = Network(start_seed=self.seed_test)
        network_1.topology_generator.erdos_renyi_topology(number_of_nodes=self.number_of_nodes, prob_edge_creation=self.prob_edge_creation)

        network_2: Network = Network(start_seed=self.seed_test)
        network_2.topology_generator.erdos_renyi_topology(number_of_nodes=self.number_of_nodes, prob_edge_creation=self.prob_edge_creation)

        assert network_1.edges() == network_2.edges()


    def test_reproducibility_of_barabasi_albert(self) -> None:

        network_1: Network = Network(start_seed=self.seed_test)
        network_1.topology_generator.barabasi_albert_topology(number_of_nodes=self.number_of_nodes, edges_to_attach=self.edges_to_attach)

        network_2: Network = Network(start_seed=self.seed_test)
        network_2.topology_generator.barabasi_albert_topology(number_of_nodes=self.number_of_nodes, edges_to_attach=self.edges_to_attach)

        assert network_1.edges() == network_2.edges()


    def test_select_topology(self) -> None:

        args: dict[Topologies, tuple] = {
            Topologies.BARABASI_ALBERT: (self.number_of_nodes, self.edges_to_attach),
            Topologies.ERDOS_RENYI: (self.number_of_nodes, self.prob_edge_creation),
            Topologies.GRID: (self.number_of_rows, self.number_of_columns),
            Topologies.LINE: (self.number_of_nodes,),
            Topologies.RING: (self.number_of_nodes,),
            Topologies.STAR: (self.number_of_nodes,),
        }

        for topology in Topologies:
            network: Network = Network()
            network.topology_generator.select_topology(topology, *args[topology])

            assert network.topology == topology

            network.destroy()

