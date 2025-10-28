from components.data_manager import Data_Manager
from components.network import Network
from components.simulations import AsyncSimulator
from components.utils.constants import ENTANGLEMENT_SWAPPING_PROB

from random import choice
from copy import copy
from datetime import datetime
import os

PATH: str = "src/data/default_simulation/default_simulation"

# Topology constants
ROWS: int = 3
COLUMNS: int = 4

# Attack constants
TARGETS: list[int] = [0, 1]
BLACK_HOLES_NUMBER: list[int] = [1, 3, 5]
INTENSITIES: list[float] = [0.1 * i for i in range(1, 8)]

# Simulations Params
RUNS: int = 5000
REQUESTS_PER_RUN: int = 100
ATTEMPTS_PER_REQUEST: int = 2


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

    csv_filename: str = f"{PATH}.csv"

    all_data: Data_Manager = Data_Manager()

    if is_a_dataset:
        total_default_runs = (
            runs * len(TARGETS) * len(BLACK_HOLES_NUMBER) * len(INTENSITIES)
        )
    else:
        total_default_runs = runs

    # Run without black holes
    print(f"Network without black hole is running {total_default_runs} runs")
    seed: int = process_id
    for _ in range(total_default_runs):
        network: Network = Network(start_seed=seed)
        network.topology_generator.grid_topology(ROWS, COLUMNS)
        nodes: list[int] = list(network.nodes.keys())

        for _ in range(requests_per_run):
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

        all_data.update_data(network.network_data)

        # append data in csv file
        all_data.append_data_in_csv_file(filename=csv_filename, append_in_csv_dict=True)

        # update the seed
        seed += 1

    # run simulations with black holes
    for target in TARGETS:
        for bh_number in BLACK_HOLES_NUMBER:
            for intensity in INTENSITIES:
                print(
                    f"Network with black holes. bh_targets: {target}, bh_number: {bh_number}, intensity: {intensity:.1f}"
                )
                seed: int = process_id
                for _ in range(runs):

                    network: Network = Network(start_seed=seed)
                    network.topology_generator.grid_topology(ROWS, COLUMNS)
                    network.attack_manager.create_black_holes(
                        number_of_black_holes=bh_number,
                        swap_prob=(ENTANGLEMENT_SWAPPING_PROB - intensity),
                        targets_per_black_hole=target,
                    )
                    nodes: list[int] = list(network.nodes.keys())

                    for _ in range(requests_per_run):
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

                    all_data.update_data(network.network_data)

                    # append data in csv file
                    all_data.append_data_in_csv_file(
                        filename=csv_filename, append_in_csv_dict=True
                    )

                    seed += 1  # update seed

    return all_data


# select cores number
cores: int | None = os.cpu_count()
if cores is None:
    cores = 4  # max cores in your machine

# calculate time
start: datetime = datetime.now()

# remove 1 core to avoid operation system's errors
sim = AsyncSimulator(
    simulation_function=simulation, runs=RUNS, cores=cores - 1, need_id=True
)
sim.run(
    requests_per_run=REQUESTS_PER_RUN,
    attempts_per_request=ATTEMPTS_PER_REQUEST,
    is_a_dataset=True,
)

# show simulation time
print(f"\nAll simulations are finished. Simulation time: {datetime.now()-start}")
