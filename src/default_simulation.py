from components.data_manager import Data_Manager
from components.network import Network
from components.simulations import AsyncSimulator

from random import choice
from copy import copy
from datetime import datetime

FILENAME: str = '/home/negrao/Documentos/Sequence/SeQUeNCe-Black-Hole-Attack/src/data/default_simulation/default_simulation.json'

# Topology constants
ROWS: int = 3
COLUMNS: int = 4

# Attack constants
TARGETS: list[int] = [0, 1]
BLACK_HOLES_NUMBER: list[int] = [1, 3, 5]
INTENSITIES: list[float] = [0.1*i for i in range(1, 8)]

def simulation(runs: int, resquests_per_run: int, attempts_per_request: int) -> Data_Manager:

    all_data: Data_Manager = Data_Manager()
    all_data.load_json(filename=FILENAME, create_file_if_not_exist=True)

    # Run without black holes
    for run in range(runs):
        print(f"Network without black hole run: {run}")
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
        all_data.insert_data_in_json(element_key=run, keys=['no-black-hole'])
        all_data.write_json(filename=FILENAME)

    # run simulations with black holes
    for target in TARGETS:
        for bh_number in BLACK_HOLES_NUMBER: 
            for intensity in INTENSITIES:
                for run in range(runs):
                    print(f"Network with black holes. run: {run}, target: {target}, bh_number: {bh_number}, intensity: {intensity}")
                    network: Network = Network()
                    network.topology_generator.grid_topology(ROWS, COLUMNS)
                    network.attack_manager.create_black_holes(number_of_black_holes=bh_number, swap_prob=(0.8 - intensity), targets_per_black_hole=target)
                    nodes: list[int] = list(network.nodes.keys())

                    for request in range(resquests_per_run):
                        tmp_nodes: list[int] = copy(nodes)

                        nodeA_id: int = choice(tmp_nodes)
                        tmp_nodes.remove(nodeA_id)

                        nodeB_id: int = choice(tmp_nodes)
                        
                        network.network_manager.request(nodeA_id=nodeA_id, nodeB_id=nodeB_id, 
                                                        max_attempts_per_entanglement=attempts_per_request, max_request_attempts=2)
                        
                    all_data.update_data(network.network_data)
                    all_data.insert_data_in_json(element_key=run, keys=[target, bh_number, intensity])
                    all_data.write_json(filename=FILENAME)
                        
        
    return all_data


sim = AsyncSimulator(simulation_function=simulation, runs=10, cores=3)
sim.run(100, 2)