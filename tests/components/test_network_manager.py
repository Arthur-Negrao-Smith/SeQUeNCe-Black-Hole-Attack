from sequence.kernel.timeline import Timeline
from components.network import Network
from components.utils.enums import Request_Response
import networkx as nx
import pytest as pt

from components.nodes import QuantumRepeater


@pt.fixture
def network() -> Network:
    seed: int = 0
    number_of_nodes: int = 5

    tmp_network: Network = Network(start_seed=seed)
    tmp_network.topology_generator.line_topology(number_of_nodes)

    return tmp_network

@pt.fixture
def network_no_path() -> Network:

    network = Network()

    graph: nx.Graph = nx.Graph()
    graph.add_node(0)
    graph.add_node(1)

    network.update_graph(graph=graph)
    network.update_nodes({0: QuantumRepeater('0', Timeline(), 1), 1: QuantumRepeater('1', Timeline(), 1)})

    return network



class Test_Network_Manager:

    def test_find_path_if_path_exists(self, network: Network) -> None:

        # test normal function
        assert network.network_manager.find_path(0, 2) == [0, 1, 2]


    def test_find_path_if_node_doesnt_exists(self, network: Network) -> None:

        # test nodeA doesn't exists
        assert network.network_manager.find_path(10, 3) == [-1]

        # test nodeB doesn't exists
        assert network.network_manager.find_path(0, 10) == [-1]


    def test_find_path_if_path_doenst_exists(self, network_no_path: Network) -> None:

        # test if path doesn't exists
        assert network_no_path.network_manager.find_path(0, 1) == []


    def test_request_if_node_doesnt_exists(self, network: Network) -> None:

        # force entanglement is off
        assert network.network_manager.request(0, -1, force_entanglement=False) == Request_Response.NON_EXISTENT_NODE
        assert network.network_manager.request(-1, 0, force_entanglement=False) == Request_Response.NON_EXISTENT_NODE

        # force entanglement is on
        assert network.network_manager.request(0, -1, force_entanglement=True) == Request_Response.NON_EXISTENT_NODE
        assert network.network_manager.request(-1, 0, force_entanglement=True) == Request_Response.NON_EXISTENT_NODE


    def test_request_if_is_same_node(self, network: Network) -> None:

        # force entanglement is off
        assert network.network_manager.request(0, 0, force_entanglement=False) == Request_Response.SAME_NODE

        # force entanglement is on
        assert network.network_manager.request(0, 0, force_entanglement=True) == Request_Response.SAME_NODE


    def test_request_if_path_doenst_exists(self, network_no_path: Network) -> None:

        assert network_no_path.network_manager.request(0, 1) == Request_Response.NO_PATH
        assert network_no_path.network_manager.request(1, 0) == Request_Response.NO_PATH
