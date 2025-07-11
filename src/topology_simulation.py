from components.data_manager import Data_Manager
from components.network import Network
from components.simulations import AsyncSimulator
from components.utils.constants import ENTANGLEMENT_SWAPPING_PROB
from components.utils.enums import Topologies as TP
from components.network_data import TOPOLOGIES_DICT

from random import choice
from copy import copy
from datetime import datetime
import os

PATH: str = 'src/data/topology_simulation'

# Topology constants
ROWS: int = 3
COLUMNS: int = 4

# Attack constants
PASS_OF_NODE: int = 12
TARGETS: tuple[int, int] = (0, 1)
TOPOLOGIES: tuple[TP, TP, TP] = (TP.GRID, TP.BARABASI_ALBERT, TP.ERDOS_RENYI)
NUMBER_OF_NODES: tuple[int, ...] = tuple([i for i in range(12, 108, PASS_OF_NODE)])
TOPOLOGY_PARAMS: tuple[float, float, float] = (0.1, 0.3, 0.5)
GRADE_NODES: dict[int, tuple[int, int]] = {
    12:(3, 4),
    24:(4, 6),
    36:(6, 6),
    48:(6, 8),
    60:(6, 10),
    72:(8, 9),
    84:(7, 12),
    96:(8, 12)
}

# Simulations Params
RUNS: int = 1000
REQUESTS_PER_RUN: int = 100
ATTEMPTS_PER_REQUEST: int = 2


def select_topology(network: Network, topology: TP, *args) -> None:
    match topology:
        case TP.GRID:
            network.topology_generator.grid_topology(*GRADE_NODES[args[0]])
        case TP.BARABASI_ALBERT:
            network.topology_generator.barabasi_albert_topology(args[0], int(args[1]*10))
        case TP.ERDOS_RENYI:
            network.topology_generator.erdos_renyi_topology(args[0], args[1])
        case _:
            print("Erro: Topology doens't valid")
            return


def simulation(runs: int, process_id: int, resquests_per_run: int, attempts_per_request: int) -> Data_Manager:
    """
    Simulation to simulation a black hole attack to a entanglement network with grid topology

    Args:
        runs (int): Total runs to execute in simulation
        process_id (int): Id to identify process to use AsyncSimulator
        requests_per_run (int): Total requests calls per run
        attempts_per_request (int): Total attempts to try per request

    Returns:
        Data_Manager: Return all data in json format within the Data_Manager
    """

    filename: str = f"{PATH}/topology_simulation_{process_id}.json"

    all_data: Data_Manager = Data_Manager()

    # Run without black holes
    print(f"Network without black hole is running")
    for run in range(runs):
        network: Network = Network()
        network.topology_generator.grid_topology(ROWS, COLUMNS)
        nodes: list[int] = list(network.nodes.keys())

        for requests in range(resquests_per_run):
            tmp_nodes: list[int] = copy(nodes)

            nodeA_id: int = choice(tmp_nodes)
            tmp_nodes.remove(nodeA_id)

            nodeB_id: int = choice(tmp_nodes)

            network.network_manager.request(nodeA_id=nodeA_id, nodeB_id=nodeB_id, 
                                            max_attempts_per_entanglement=attempts_per_request, max_request_attempts=2)

        all_data.update_data(network.network_data)
        all_data.insert_data_in_json(element_key=(f'run: {runs*process_id + run}'), keys=['no-black-hole'])
        all_data.write_json(filename=filename)

    # run simulations with black holes
    for target in TARGETS:
        for topology in TOPOLOGIES: 
            for num_of_nodes in NUMBER_OF_NODES:
                print(f"Network with black holes. bh_targets: {target}, bh_number: {bh_number}, intensity: {intensity:.1f}")
                for run in range(runs):
                    network: Network = Network()
                    network.topology_generator.grid_topology(ROWS, COLUMNS)
                    network.attack_manager.create_black_holes(number_of_black_holes=bh_number, swap_prob=(ENTANGLEMENT_SWAPPING_PROB - intensity), targets_per_black_hole=target)
                    nodes: list[int] = list(network.nodes.keys())

                    for request in range(resquests_per_run):
                        tmp_nodes: list[int] = copy(nodes)

                        nodeA_id: int = choice(tmp_nodes)
                        tmp_nodes.remove(nodeA_id)

                        nodeB_id: int = choice(tmp_nodes)

                        network.network_manager.request(nodeA_id=nodeA_id, nodeB_id=nodeB_id, 
                                                        max_attempts_per_entanglement=attempts_per_request, max_request_attempts=2)

                    all_data.update_data(network.network_data)
                    all_data.insert_data_in_json(element_key=f'run: {(runs*process_id + run)}', keys=['with-black-hole',f'targets: {target}', f'number of bh: {bh_number}', f'intensity: {intensity:.1f}'])
                    all_data.write_json(filename=filename)

    return all_data


# select cores number
cores: int | None = os.cpu_count()
if cores is None:
    cores = 4 # max cores in your machine

# calculate time
start: datetime = datetime.now()

# remove 1 core to avoid operation system's errors
sim = AsyncSimulator(simulation_function=simulation, runs=RUNS, cores=cores-1, need_id=True)
sim.run(REQUESTS_PER_RUN, ATTEMPTS_PER_REQUEST)

# show simulation time
print(f"\nAll simulations are finished. Simulation time: {datetime.now()-start}")
