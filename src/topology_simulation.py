from components.data_manager import Data_Manager, sum_jsons
from components.network import Network
from components.simulations import AsyncSimulator
from components.utils.enums import Topologies as TP
from components.network_data import Network_Data
import components.network_data as nd

from random import choice
from copy import copy
from datetime import datetime
import os
import glob

PATH: str = "src/data/topology_simulation/topology_simulation"

# Topology constants
ROWS: int = 3
COLUMNS: int = 4

# Attack constants
SWAP_PROB: float = 0.4
PASS_OF_NODE: int = 12
TARGETS: tuple[int, int] = (0, 1)
TOPOLOGIES: tuple[TP, TP, TP] = (TP.GRID, TP.BARABASI_ALBERT, TP.ERDOS_RENYI)
NUMBER_OF_NODES: tuple[int, ...] = tuple([i for i in range(12, 108, PASS_OF_NODE)])
TOPOLOGY_PARAMS: tuple[float, float, float] = (0.1, 0.3, 0.5)
GRIDE_NODES: dict[int, tuple[int, int]] = {
    12: (3, 4),
    24: (4, 6),
    36: (6, 6),
    48: (6, 8),
    60: (6, 10),
    72: (8, 9),
    84: (7, 12),
    96: (8, 12),
}

# Simulations Params
RUNS: int = 1000
REQUESTS_PER_RUN: int = 100
ATTEMPTS_PER_REQUEST: int = 2


def sim_normal_network(
    topology: TP,
    attempts_per_request: int,
    requests_per_run: int,
    tmp_parameter: list | tuple[int, int],
    seed: int | float | None = None,
) -> Network_Data:
    network: Network = Network(start_seed=seed)

    network.topology_generator.select_topology(topology, *tmp_parameter)
    nodes: list[int] = list(network.nodes.keys())

    for requests in range(requests_per_run):
        tmp_nodes: list[int] = copy(nodes)

        nodeA_id: int = choice(tmp_nodes)
        tmp_nodes.remove(nodeA_id)

        nodeB_id: int = choice(tmp_nodes)

        network.network_manager.request(
            nodeA_id=nodeA_id,
            nodeB_id=nodeB_id,
            max_attempts_per_entanglement=attempts_per_request,
            max_request_attempts=2,
        )

    network.destroy(preserve_network_data=True)  # cleanup all network
    return network.network_data


def sim_attacked_network(
    topology: TP,
    attempts_per_request: int,
    requests_per_run: int,
    tmp_parameter: list | tuple[int, int],
    bh_number: int,
    target: int,
    seed: int | float | None = None,
) -> Network_Data:
    network: Network = Network(start_seed=seed)
    network.topology_generator.select_topology(topology, *tmp_parameter)
    network.attack_manager.create_black_holes(
        number_of_black_holes=bh_number,
        swap_prob=SWAP_PROB,
        targets_per_black_hole=target,
    )
    nodes: list[int] = list(network.nodes.keys())

    for request in range(requests_per_run):
        tmp_nodes: list[int] = copy(nodes)

        nodeA_id: int = choice(tmp_nodes)
        tmp_nodes.remove(nodeA_id)

        nodeB_id: int = choice(tmp_nodes)

        network.network_manager.request(
            nodeA_id=nodeA_id,
            nodeB_id=nodeB_id,
            max_attempts_per_entanglement=attempts_per_request,
            max_request_attempts=2,
        )

    network.destroy(preserve_network_data=True)  # cleanup all network
    return network.network_data


def simulation(
    runs: int,
    process_id: int,
    requests_per_run: int,
    attempts_per_request: int,
    is_a_dataset: bool,
) -> Data_Manager:
    """
    Simulation to simulation a black hole attack to a entanglement network with grid topology

    Args:
        runs (int): Total runs to execute in simulation
        process_id (int): Id to identify process to use AsyncSimulator
        requests_per_run (int): Total requests calls per run
        attempts_per_request (int): Total attempts to try per request
        is_a_dataset (bool): If the data will used to create a dataset. If is True all simulations will be equally balanced

    Returns:
        Data_Manager: Return all data in json format within the Data_Manager
    """

    json_filename: str = f"{PATH}_{process_id}.json"
    csv_filename: str = f"{PATH}.csv"

    all_data: Data_Manager = Data_Manager()

    if is_a_dataset:
        total_default_runs: int = runs * len(TARGETS)
    else:
        total_default_runs = runs

    # Run without black holes
    print(f"Network without black hole is running {total_default_runs} runs")
    for topology in TOPOLOGIES:
        for parameter in TOPOLOGY_PARAMS:

            # if it is grid topology and not the first run and this simulation will not used to create a dataset just ignore
            if (
                topology == TP.GRID
                and parameter != TOPOLOGY_PARAMS[0]
                and not is_a_dataset
            ):
                continue

            for number_of_nodes in NUMBER_OF_NODES:

                print(
                    f"No BHA >> topology: {topology.value}, param: {int(parameter * 10)}, number-of-nodes: {number_of_nodes}"
                )

                tmp_parameter: list | tuple[int, int]

                # to select param for each topology
                match topology:
                    case TP.BARABASI_ALBERT:
                        tmp_parameter = [number_of_nodes, int(parameter * 10)]
                    case TP.ERDOS_RENYI:
                        tmp_parameter = [number_of_nodes, parameter]
                    case _:
                        tmp_parameter = GRIDE_NODES[number_of_nodes]

                for run in range(total_default_runs):
                    tmp_data: Network_Data = sim_normal_network(
                        topology=topology,
                        attempts_per_request=attempts_per_request,
                        requests_per_run=requests_per_run,
                        tmp_parameter=tmp_parameter,
                        seed=(process_id * total_default_runs + run),
                    )

                    all_data.update_data(tmp_data)

                    all_data.append_data_in_csv_file(
                        filename=csv_filename, append_in_csv_dict=True
                    )

    # run simulations with black holes
    print("Network with black holes is running.")
    for target in TARGETS:
        for topology in TOPOLOGIES:
            for parameter in TOPOLOGY_PARAMS:

                # if it is grid topology and not the first run just ignore
                if topology == TP.GRID and parameter != TOPOLOGY_PARAMS[0]:
                    continue

                for number_of_nodes in NUMBER_OF_NODES:
                    print(
                        f"BHA >> targets: {target}, topology: {topology.value}, param: {int(parameter * 10)}, number-of-nodes: {number_of_nodes}"
                    )

                    bh_number: int = int(
                        number_of_nodes * 20 / 100
                    )  # 20% of black holes

                    tmp_parameter: list | tuple[int, int]

                    # to select param for each topology
                    match topology:
                        case TP.BARABASI_ALBERT:
                            tmp_parameter = [number_of_nodes, int(parameter * 10)]
                        case TP.ERDOS_RENYI:
                            tmp_parameter = [number_of_nodes, parameter]
                        case _:
                            tmp_parameter = GRIDE_NODES[number_of_nodes]

                    for run in range(runs):
                        tmp_data: Network_Data = sim_attacked_network(
                            topology=topology,
                            attempts_per_request=attempts_per_request,
                            requests_per_run=requests_per_run,
                            tmp_parameter=tmp_parameter,
                            bh_number=bh_number,
                            target=target,
                            seed=(process_id * runs + run),
                        )

                        all_data.update_data(tmp_data)

                        all_data.append_data_in_csv_file(
                            filename=csv_filename, append_in_csv_dict=True
                        )

    return all_data


# select cores number
cores: int | None = os.cpu_count()
if cores is None:
    cores = 4  # max cores in your machine

# limite cores to reproduce the experiment
if cores > 16:
    cores = 16

# calculate time
start: datetime = datetime.now()

# remove 1 core to avoid operation system's errors
sim = AsyncSimulator(
    simulation_function=simulation, runs=RUNS, cores=cores - 1, need_id=True
)
sim.run(
    requests_per_run=REQUESTS_PER_RUN,
    attempts_per_request=ATTEMPTS_PER_REQUEST,
    is_a_dataset=False,
)

# show simulation time
print(f"\nAll simulations are finished. Simulation time: {datetime.now()-start}")
