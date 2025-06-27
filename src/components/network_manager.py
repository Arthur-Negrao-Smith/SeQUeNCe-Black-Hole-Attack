from sequence.topology.topology import BSMNode
from sequence.entanglement_management.generation import EntanglementGenerationA, EntanglementGenerationB
from sequence.entanglement_management.entanglement_protocol import EntanglementProtocol
from sequence.components.memory import Memory

from components.utils.enums import Directions, Protocol_Types, Request_Response
from .nodes import QuantumRepeater
from .utils.constants import ENTANGLEMENT_FIDELITY

import networkx as nx
from typing import Optional, Type
from random import randint
import logging

log: logging.Logger = logging.getLogger(__name__)

class Network_Manager:
    """
    Manager to control the protocols and requests of the network 
    """
    from .network import Network
    def __init__(self, network: Network) -> None:
        """
        Constructor for Network Manager

        Args:
            network (Network): Network to manage
        """
        self.network: Network = network # type: ignore
        self.data: dict

        log.debug(f"Network Manager initiated")

    # TODO: Finalize the request function
    def request(self, nodeA_id: int, nodeB_id: int, max_attempts: int = 2, force_entanglement: bool = False) -> Request_Response:
        """
        Create a request from nodeA to nodeB

        Args:
            nodeA_id (int): Source node
            nodeB_id (int): Destination node
            max_attempts (int): Max request attempts
            force_entanglement (bool): If is True the entanglement don't need protocol
        """
        # if nodeA and nodeB is the same node
        if nodeA_id == nodeB_id:
            return Request_Response.NO_PATH

        path: list[int] = self.find_path(nodeA_id, nodeB_id)
        # if don't have a path
        if path == []:
            return Request_Response.NO_PATH
        # if nodeA or nodeB isn't in network
        if path == [-1]:
            return Request_Response.NON_EXISTENT_NODE
 
        nodeA: QuantumRepeater = self.network.nodes[nodeA_id]
        
        return Request_Response.ENTANGLED_SUCCESS
        
    def find_path(self, nodeA_id: int, nodeB_id: int) -> list[int]:
        """
        Find the best path of nodeA to nodeB

        Args:
            nodeA_id (int): Source node to search path
            nodeB_id (int): Destination node to search path

        Returns:
            list[int]: Will return [-1] if any node (nodeA or nodeB) doesn't exists. Return [] if don't have path, else [nodeA_id, ..., nodeB_id] 
        """
        if nodeA_id not in self.network.nodes.keys() or nodeB_id not in self.network.nodes.keys():
            log.warning(f"The node[{nodeA_id}] or node[{nodeB_id}] don't exist")
            return [-1]

        else:
            try:
                path: list[int] = list(nx.shortest_path(self.network.graph, nodeA_id, nodeB_id))
                log.debug(f"The path of the node[{nodeA_id}] to node[{nodeB_id}] is: {path}")
                return path
            except nx.NodeNotFound:
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
            bool: Return False if doesn't exists this protocol type, else return True
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

    def _force_entanglement(self, nodeA_id: int, nodeB_id: int,
                             nodeA_memory_position: Directions, 
                             nodeB_memory_position: Directions,
                             fidelity: float,
                             entanglement_state: Optional[list[float | int]] = None) -> None:
        """
        Force the memories of nodes to create a entanglement

        Args:
            nodeA_id (int): Node to entanglement memory
            nodeB_id (int): Node to entanglement memory
            nodeA_memory_position (Directions): Direction of the nodeA memory
            nodeB_memory_position (Directions): Direction of the nodeB memory
            fidelity (float): Fidelity of the entanglement
            entanglement_state (Optional[list[float | int]]): Optional argument to select the state of entanglement, 
                if is None than state is phi plus
        """
        if entanglement_state is None:
            SQRT_HALF: float = 0.5 ** 0.5
            state: list[float | int] = [SQRT_HALF, 0, 0, SQRT_HALF] # phi plus

        memoA: Memory = self.network.nodes[nodeA_id].resource_manager.get_memory(nodeA_memory_position)
        memoB: Memory = self.network.nodes[nodeB_id].resource_manager.get_memory(nodeB_memory_position)

        memoA.reset()
        memoB.reset()
        tl.quantum_manager.set([memoA.qstate_key, memoB.qstate_key], state) # type: ignore

        memoA.entangled_memory['node_id'] = memoB.owner.name # type: ignore
        memoA.entangled_memory['memo_id'] = memoB.name       # type: ignore
        memoB.entangled_memory['node_id'] = memoA.owner.name # type: ignore
        memoB.entangled_memory['memo_id'] = memoA.name       # type: ignore

        memoA.fidelity = memoB.fidelity = fidelity # type: ignore

        log.debug(f"The {nodeA_memory_position} memory of node[{nodeA_id}] was forced entangled with {nodeB_memory_position} memory of the node[{nodeB_id}]")

    def _entangle_two_nodes(self, nodeA_id: int, nodeB_id: int, force_entanglement: bool) -> bool:
        """
        Create a entanglement between two nodes

        Args:
            nodeA_id (int): Node to entanglement right memory
            nodeB_id (int): Node to entanglement left memory
            force_entanglement (bool): If is True the entanglement don't need protocol

        Returns:
            bool: Return False if BSMNode doesn't exists, else return True
        """
        # If doesn't wants use a protocol
        if force_entanglement:
            self._force_entanglement(nodeA_id=nodeA_id, nodeB_id=nodeB_id, nodeA_memory_position=Directions.RIGHT, 
                                     nodeB_memory_position=Directions.LEFT, fidelity=ENTANGLEMENT_FIDELITY)
            return True

        nodeA: QuantumRepeater = self.network.nodes[nodeA_id]
        nodeB: QuantumRepeater = self.network.nodes[nodeB_id]
        bsm_node: BSMNode | None = self.network.get_bsm_node(nodeA_id, nodeB_id)

        if bsm_node is None:
            log.warning(f"BSMNode between {nodeA.name} and {nodeB.name} doesn't exist")
            return False
        
        nodeA.resource_manager.create_entanglement_protocol(memory_position=Directions.RIGHT, middle_node=bsm_node.name, other_node=nodeB.name)
        nodeB.resource_manager.create_entanglement_protocol(memory_position=Directions.LEFT, middle_node=bsm_node.name, other_node=nodeA.name)
        self._pair_EntanglementGeneration_protocols(nodeA_id=nodeA_id, nodeB_id=nodeB_id)
        self.network._run()
        
        return True

    def create_black_holes(self, number_of_black_holes: int, swap_prob: int) -> None:
        """
        Create black holes in the network

        Args:
            number_of_black_holes (int): Number of black holes in the network
            swap_prob (int): BHA's entanglement swapping probability
        """
        counter: int = number_of_black_holes
        while counter != 0:
            
            tmp_id: int = randint(0, len(self.network.nodes))
            # if black hole already exists
            if tmp_id in self.network.black_holes.keys():
                continue

            self.network.nodes[tmp_id].resource_manager.update_swap_prob(swap_prob)
            self.network.black_holes[tmp_id] = self.network.nodes[tmp_id]
            counter -= 1

        log.debug(f"The black holes: {self.network.black_holes.values()}")

    def get_data(self) -> dict:
        return self.data