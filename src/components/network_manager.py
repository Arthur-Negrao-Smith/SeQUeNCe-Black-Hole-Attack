from sequence.protocol import Protocol
from sequence.topology.topology import BSMNode
from sequence.entanglement_management.generation import EntanglementGenerationA, EntanglementGenerationB
from sequence.entanglement_management.entanglement_protocol import EntanglementProtocol
from sequence.components.memory import Memory

from components.network import Network
from components.utils.enums import Directions, Protocol_Types, Request_Response
from .nodes import QuantumRepeater

import networkx as nx
from typing import Type
import logging

log: logging.Logger = logging.getLogger(__name__)

class Network_Manager:
    """
    Manager to control the protocols and requests of the network 
    """
    from .network import Network
    def __init__(self, network: Network) -> None:
        self.network: Network = network
        self.data: dict

    def request(self) -> None:
        pass
        

    def find_path(self, nodeA_id: int, nodeB_id: int) -> list[int]:
        """
        Find the best path of nodeA to nodeB

        Args:
            nodeA_id (int): Source node to search path
            nodeB_id (int): Destination node to search path

        Returns:
            list[int]: Will return [-1] if any node (nodeA or nodeB) don't exist. Return [] if don't have path, else [nodeA_id, ..., nodeB_id] 
        """
        if nodeA_id not in self.network.nodes.keys() or nodeB_id in self.network.nodes.keys():
            log.warning(f"The node[{nodeA_id}] or node[{nodeB_id}] don't exist")
            return [-1]

        else:
            try:
                path: list[int] = list(nx.shortest_path(self.network.graph, nodeA_id, nodeB_id))
                log.debug(f"The path of the node[{nodeA_id}] to node[{nodeB_id}] is: {path}")
                return path
            except:
                log.debug(f"Don't have path of the node[{nodeA_id}] to node[{nodeB_id}]")
                return []


    def _create_protocols(self, node_id: int, protocol_type: Protocol_Types, **kwargs) -> bool:
        """
        Create protocol in selected node

        Args:
            node_id (int): Id of the desired node to create protocol
            protocol_type (Protocol_Types): Type of the desired protocol
            **kwargs (str, Unknow): Args to create the protocol

        Returns:
            bool: Return False if don't exist protocol type, else return True
        """
        node: QuantumRepeater = self.network.nodes[node_id]
        if protocol_type == Protocol_Types.ENTANGLEMENT:
            node.resource_manager.create_entanglement_protocol(memory_position=kwargs['memory_position'], 
                                                                                      middle_node=kwargs['middle_node'],
                                                                                      other_node=kwargs['other_node'])
            log.debug(f"Protocol {protocol_type} created in the node[{node_id}]")
        elif protocol_type == Protocol_Types.SWAPPING_A:
            node.resource_manager.create_swapping_protocolA()
            log.debug(f"Protocol {protocol_type} created in the node[{node_id}]")
        elif protocol_type == Protocol_Types.SWAPPING_B:
            node.resource_manager.create_swapping_protocolB(memory_position=kwargs['memory_position'])
            log.debug(f"Protocol {protocol_type} created in the node[{node_id}]")
        else:
            log.warning(f"Protocol {protocol_type} wasn't created in the node[{node_id}], because don't exist this protocol type")
            return False
        
        return True

    def _pair_EntanglementGeneration_protocols(self, nodeA_id: int, nodeB_id: int) -> None:
        """
        Pair entanglement generation protocols

        Args:
            nodeA_id (int): Node to entanglement your right memory
            nodeB_id (int): Node to entanglement your left memory
        """
        nodeA: QuantumRepeater = self.network.nodes[nodeA_id]
        nodeB: QuantumRepeater = self.network.nodes[nodeB_id]

        protocol_A: Type[EntanglementProtocol] = nodeA.get_protocol()
        protocol_B: Type[EntanglementProtocol] = nodeB.get_protocol()

        nodeA_memory: Memory = nodeA.resource_manager.get_memory(Directions.RIGHT)
        nodeB_memory: Memory = nodeB.resource_manager.get_memory(Directions.LEFT)

        protocol_A.set_others(protocol_B.name, nodeB.name, [nodeB_memory]) # type: ignore
        protocol_A.set_others(protocol_A.name, nodeA.name, [nodeA_memory]) # type: ignore

        log.debug(f"node[{nodeA_id}] and node[{nodeB_id}] were your entanglement generation protocols paired")

    def _pair_Swapping_protocols(self, nodeA_id: int, nodeB_id: int, node_mid_id: int) -> None:
        """
        Pair entanglement generation protocols

        Args:
            nodeA_id (int): Node to entanglement swapping your right memory
            nodeB_id (int): Node to entanglement swapping your left memory
            node_mid_id (int): Node to do entanglement swapping between nodeA and nodeB
        """
        nodeA: QuantumRepeater = self.network.nodes[nodeA_id]
        nodeB: QuantumRepeater = self.network.nodes[nodeB_id]
        node_mid: QuantumRepeater = self.network.nodes[node_mid_id]

        protocol_A: Type[EntanglementProtocol] = nodeA.get_protocol()
        protocol_B: Type[EntanglementProtocol] = nodeB.get_protocol()
        protocol_mid: Type[EntanglementProtocol] = node_mid.get_protocol()

        node_mid_left_memory: Memory = node_mid.resource_manager.get_memory(Directions.LEFT)
        node_mid_right_memory: Memory = node_mid.resource_manager.get_memory(Directions.RIGHT)

        protocol_A.set_others(protocol_mid.name, node_mid.name, [node_mid_left_memory, node_mid_right_memory]) # type: ignore
        protocol_B.set_others(protocol_mid.name, node_mid.name, [node_mid_left_memory, node_mid_right_memory]) # type: ignore
        protocol_mid.set_others(protocol_A.name, nodeA.name, [nodeA.right_memo_name]) # type: ignore
        protocol_mid.set_others(protocol_B.name, nodeB.name, [nodeB.left_memo_name]) # type: ignore

        log.debug(f"node[{nodeA_id}], node[{node_mid_id}] and node[{nodeB_id}] were your entanglement swapping protocols paired")

    def _force_entanglement(self, nodeA_id: int, nodeB_id: int, nodeA_memory_position: Directions, nodeB_memory_positions: Directions) -> None:
        """
        Force the memory of node to create a entanglement
        """
        pass

    def get_data(self) -> dict:
        return self.data