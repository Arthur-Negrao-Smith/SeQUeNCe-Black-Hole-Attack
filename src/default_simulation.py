from components.network import Network
from components.simulations import AsyncSimulator

from random import choice
from copy import copy
from datetime import datetime

# Topology constants
ROWS: int = 3
COLUMNS: int = 4

# Attack constants
TARGETS: list[int] = [0, 1]
BLACK_HOLES_NUMBER: list[int] = [1, 3, 5]
INTENSITIES: list[float] = [0.1*i for i in range(1, 8)]

def simulation(runs: int, resquests_per_run: int, attempts_per_request: int) -> dict:

    # Run without black holes
    for run in range(runs):
        print(f"Rodando a rede padrão run: {run}")
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

    # run simulations with black holes
    for target in TARGETS:
        for bh_number in BLACK_HOLES_NUMBER: 
            for intensity in INTENSITIES:
                for run in range(runs):
                    print(f"Rodando a rede atacada. run: {run}, target: {target}, bh_number: {bh_number}, intensity: {intensity}")
                    network: Network = Network()
                    network.topology_generator.grid_topology(ROWS, COLUMNS)
                    network.attack_manager.create_black_holes(number_of_black_holes=bh_number, swap_prob=(0.8 - intensity), targets_per_black_hole=target)
                    nodes: list[int] = list(network.nodes.keys())

                    for request in range(requests):
                        tmp_nodes: list[int] = copy(nodes)

                        nodeA_id: int = choice(tmp_nodes)
                        tmp_nodes.remove(nodeA_id)

                        nodeB_id: int = choice(tmp_nodes)
                        
                        network.network_manager.request(nodeA_id=nodeA_id, nodeB_id=nodeB_id, 
                                                        max_attempts_per_entanglement=attempts_per_request, max_request_attempts=2)
                        
        
    return dict()