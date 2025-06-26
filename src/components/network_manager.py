from sequence.protocol import Protocol
from sequence.topology.topology import BSMNode
from sequence.entanglement_management.generation import EntanglementGenerationA, EntanglementGenerationB
from sequence.entanglement_management.entanglement_protocol import EntanglementProtocol
from sequence.components.memory import Memory

from components.network import Network
from components.utils.enums import Directions, Protocol_Types, Request_Response
from .nodes import QuantumRepeater

from typing import Type
import logging

log: logging.Logger = logging.getLogger(__name__)

class Network_Manager:
    from .network import Network
    def __init__(self, network: Network) -> None:
        self.network: Network = network
        self.data: dict

    def request(self):
        pass
        

    def find_path(self, nodeA_id: int, nodeB_id: int):
        pass

    def _create_protocols(self, node_id: int, protocol_type: Protocol_Types, **kwargs) -> bool:
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

    def _force_entanglement(self) -> None:
        pass

    def get_data(self) -> dict:
        return self.data