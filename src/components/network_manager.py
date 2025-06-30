from sequence.topology.topology import BSMNode
from sequence.entanglement_management.entanglement_protocol import EntanglementProtocol
from sequence.components.memory import Memory

from components.utils.enums import Directions, Entanglement_Response, Request_Response, Swapping_Response
from .nodes import QuantumRepeater
from .utils.constants import ENTANGLEMENT_FIDELITY, SWAPPING_INCREMENT_TIME, ENTANGLEMENT_INCREMENT_TIME

import networkx as nx
from typing import Optional, Type
from random import choice
import logging

log: logging.Logger = logging.getLogger(__name__)

class Network_Manager:
    """
    Manager to control the network's protocols and requests
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

    def request(self, nodeA_id: int, nodeB_id: int, max_request_attempts: int = 2, force_entanglement: bool = False, max_attempts_per_entanglement: int = -1) -> Request_Response:
        """
        Create a request from nodeA to nodeB

        Args:
            nodeA_id (int): Source node
            nodeB_id (int): Destination node
            max_request_attempts (int): Max request attempts
            force_entanglement (bool): If is True the entanglement don't need protocol
            max_entanglement_attempts (int): Attempts to try create a entanglement. If max_attempts < 0, then try until entangle. If force_entanglement is True ignore this parameter
        
        Returns:
            Request_Response: If nodeA_id is equal nodeB_id then returns Request_Response.SAME_NODE.
                If don't has a path from nodeA to nodeB then returns Request_Response.NO_PATH.
                If nodeA or nodeB no exist then returns Request_Response.NON_EXISTENT_NODE.
                If bsm doens't exists then returns Request_Response.NON_EXISTENT_BSM_NODE.
                If fail request then returns Request_Response.SWAPPING_FAIL.
                If success request then returns Request_Response.SWAPPING_SUCCESS.
        """
        log.debug(f"Starting request from node[{nodeA_id}] to node[{nodeB_id}]")

        # if nodeA and nodeB are the same node
        if nodeA_id == nodeB_id:
            log.warning(f"The request failed. The node[{nodeA_id}] can't do a request to himself.")
            return Request_Response.SAME_NODE

        path: list[int] = self.find_path(nodeA_id, nodeB_id)
        # if don't have a path
        if path == []:
            return Request_Response.NO_PATH
        
        # if nodeA or nodeB isn't in network
        if path == [-1]:
            return Request_Response.NON_EXISTENT_NODE
 
        # Discard first node, because he is the nodeA
        path.pop(0)

        # start attempts counter
        request_attempts: int = 0

        # Try request
        for attempt in range(max_request_attempts):

            request_attempts += 1

            log.debug(f"Request attempt: {request_attempts}")

            # Try do an entanglement between nodeA and tmp_mid_node
            entanglement_response: Entanglement_Response = self._entangle_two_nodes(nodeA_id=nodeA_id, nodeB_id=path[0],
                                                                  force_entanglement=force_entanglement, max_attempts=max_attempts_per_entanglement)
            
            # if the entanglement is successful
            if entanglement_response == Entanglement_Response.SUCCESS:
                entanglement_success: bool = True 
            # if bsm doesn't exists
            elif entanglement_response == Entanglement_Response.NON_EXISTENT_BSM_NODE:
                log.warning(f"Request failed. BSMNode wasn't found between: node[{nodeA_id}] and node[{path[0]}]")
                entanglement_success: bool = False
                return Request_Response.NON_EXISTENT_BSM_NODE
            # if the entanglement fails
            else: 
                entanglement_success: bool = False
                continue

            # try a sequence of entanglements and entanglement swappings
            for path_position, tmp_mid_node_id in enumerate(path):

                # break if is last node
                if path_position == len(path)-1:
                    break

                # define the temporary nodeB
                tmp_nodeB_id: int = path[path_position+1]

                # try do an entanglement between tmp_mid_node and tmp_nodeB
                entanglement_response = self._entangle_two_nodes(nodeA_id=tmp_mid_node_id, nodeB_id=tmp_nodeB_id, force_entanglement=force_entanglement)
                
                # to check if entanglements exists
                entanglement_success = (entanglement_success and (True if entanglement_response == Entanglement_Response.SUCCESS else False))

                # if nodes aren't entangled
                if not entanglement_success:
                    break

                # if failed because BSMNode wasn't found
                if entanglement_response == Entanglement_Response.NON_EXISTENT_BSM_NODE:
                    log.warning(f"Request failed. BSMNode wasn't found between: node[{tmp_mid_node_id}] and node[{tmp_nodeB_id}]")
                    return Request_Response.NON_EXISTENT_BSM_NODE
                
                # try entanglement swapping
                swapping_response: Swapping_Response = self._swapping_two_nodes(nodeA_id=nodeA_id, nodeB_id=tmp_nodeB_id, node_mid_id=tmp_mid_node_id)

                # if entanglement swapping was a success
                if swapping_response == Swapping_Response.SWAPPING_SUCCESS:
                    continue

                # if entanglement swapping failed
                if swapping_response == Swapping_Response.SWAPPING_FAIL:
                    break

                # if entanglement swapping failed beacause no memories entangled
                if swapping_response == Swapping_Response.NO_ENTANGLED:
                    log.warning("Request failed. The nodes aren't entangled")
                    return Request_Response.NO_ENTANGLED

            # if the request was a success    
            if self._is_entangled(nodeA_id=nodeA_id, nodeB_id=nodeB_id, nodeA_memory_position=Directions.RIGHT, nodeB_memory_position=Directions.LEFT):
                log.debug(f"Request was a successful. The nodes node[{nodeA_id}] and node[{nodeB_id}] are entangled. {request_attempts} request attempts were made")
                return Request_Response.ENTANGLED_SUCCESS
            
        # if the request failed
        log.debug(f"The request from node[{nodeA_id}] to node [{nodeB_id}] failed. {request_attempts} request attempts were made")
        return Request_Response.ENTANGLED_FAIL
        
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
        protocol_B.set_others(protocol_A.name, nodeA.name, [nodeA_memory]) # type: ignore

        log.debug(f"The entanglement generation protocols of node[{nodeA_id}] and node[{nodeB_id}] have been successfully paired")

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
        self.network.timeline.quantum_manager.set([memoA.qstate_key, memoB.qstate_key], state) # type: ignore

        memoA.entangled_memory['node_id'] = memoB.owner.name # type: ignore
        memoA.entangled_memory['memo_id'] = memoB.name       # type: ignore
        memoB.entangled_memory['node_id'] = memoA.owner.name # type: ignore
        memoB.entangled_memory['memo_id'] = memoA.name       # type: ignore

        memoA.fidelity = memoB.fidelity = fidelity # type: ignore

        self.network._increment_time(SWAPPING_INCREMENT_TIME)

        log.debug(f"The {nodeA_memory_position} memory of node[{nodeA_id}] was forced entangled with {nodeB_memory_position} memory of the node[{nodeB_id}]")

    def _entangle_two_nodes(self, nodeA_id: int, nodeB_id: int, force_entanglement: bool, max_attempts: int = -1) -> Entanglement_Response:
        """
        Create a entanglement between two nodes

        Args:
            nodeA_id (int): Node to entanglement right memory
            nodeB_id (int): Node to entanglement left memory
            force_entanglement (bool): If is True the entanglement don't need protocol
            max_attempts (int): Attempts to try create a entanglement. If max_attempts < 0, then try until entangle. If force_entanglement is True this parameter is ignored

        Returns:
            Entanglement_Response:  If BSMNode doesn't exists then Returns Entanglement_Response.NON_EXISTENT_BSM_NODE.
                if entanglement fail then returns Entanglement_Response.FAIL, else returns Entanglement_Response.SUCCESS
        """
        # If doesn't wants to use a protocol
        if force_entanglement:
            self._force_entanglement(nodeA_id=nodeA_id, nodeB_id=nodeB_id, nodeA_memory_position=Directions.RIGHT, 
                                     nodeB_memory_position=Directions.LEFT, fidelity=ENTANGLEMENT_FIDELITY)
            return Entanglement_Response.SUCCESS

        nodeA: QuantumRepeater = self.network.nodes[nodeA_id]
        nodeB: QuantumRepeater = self.network.nodes[nodeB_id]
        bsm_node: BSMNode | None = self.network.get_bsm_node(nodeA_id, nodeB_id)

        # if bsm_node doesn't exists
        if bsm_node is None:
            log.warning(f"BSMNode between {nodeA.name} and {nodeB.name} doesn't exist")
            return Entanglement_Response.NON_EXISTENT_BSM_NODE
        
        entangled: bool = False
        attempts: int = max_attempts
        while (not entangled) and (attempts != 0):
            nodeA.resource_manager.create_entanglement_protocol(memory_position=Directions.RIGHT, middle_node=bsm_node.name, other_node=nodeB.name)
            nodeB.resource_manager.create_entanglement_protocol(memory_position=Directions.LEFT, middle_node=bsm_node.name, other_node=nodeA.name)
            self._pair_EntanglementGeneration_protocols(nodeA_id=nodeA_id, nodeB_id=nodeB_id)

            # run protocols
            nodeA.run_protocol()
            nodeB.run_protocol()
        
            # run events
            self.network._run()

            # clean up used protocols
            nodeA.remove_used_protocol()
            nodeB.remove_used_protocol()

            # check the entanglement
            entangled = self._is_entangled(nodeA_id=nodeA_id, nodeB_id=nodeB_id, nodeA_memory_position=Directions.RIGHT, nodeB_memory_position=Directions.LEFT)

            # updates network's time
            self.network._increment_time(ENTANGLEMENT_INCREMENT_TIME)

            # if the attempts isn't a negative number
            if attempts > 0:
                attempts -= 1

        if entangled:
            log.debug(f"Entanglement success: {nodeA.name} and {nodeB.name} are entangled")
            return Entanglement_Response.SUCCESS
        
        log.debug(f"Entanglement fails: {nodeA.name} and {nodeB.name} aren't entangled")
        return Entanglement_Response.FAIL
    
    def _swapping_two_nodes(self, nodeA_id: int, nodeB_id: int, node_mid_id: int) -> Swapping_Response:
        """
        Execute a entanglement swapping protocol with nodeA, nodeB and node_mid

        Args:
            nodeA_id (int): Node with right memory entangled with left node_mid's memory entangled
            nodeB_id (int): Node with left memory entangled with right node_mid's memory entangled
            node_mid_id (int): Node to perform the entanglement swapping

        Returns:
            Swapping_Response: Returns Swapping_Response.SWAPPING_SUCCESS if protocols was a success. 
                If protocol failed returns Swapping_Response.SWAPPING_FAIL. 
                If Memories aren't previous entangled returns Swapping_Response.NO_ENTANGLED
        """
        nodeA: QuantumRepeater = self.network.nodes[nodeA_id]
        nodeB: QuantumRepeater = self.network.nodes[nodeB_id]
        node_mid: QuantumRepeater = self.network.nodes[node_mid_id]

        entangled_nodeA_and_node_mid: bool = self._is_entangled(nodeA_id=nodeA_id, nodeB_id=node_mid_id, 
                                                      nodeA_memory_position=Directions.RIGHT, 
                                                      nodeB_memory_position=Directions.LEFT)
        
        entangled_nodeB_and_node_mid: bool = self._is_entangled(nodeA_id=node_mid_id, nodeB_id=nodeB_id, 
                                                      nodeA_memory_position=Directions.RIGHT, 
                                                      nodeB_memory_position=Directions.LEFT)
        # if memories aren't entangled
        if not (entangled_nodeA_and_node_mid or entangled_nodeB_and_node_mid):
            log.warning(f" Swapping fails: {nodeA.name} isn't entangled with {node_mid.name} or {nodeB.name} isn't entangled with {node_mid.name}")
            return Swapping_Response.NO_ENTANGLED
        
        nodeA.resource_manager.create_swapping_protocolB(Directions.RIGHT)
        node_mid.resource_manager.create_swapping_protocolA()
        nodeB.resource_manager.create_swapping_protocolB(Directions.LEFT)

        self._pair_Swapping_protocols(nodeA_id=nodeA_id, nodeB_id=nodeB_id, node_mid_id=node_mid_id)

        nodeA.run_protocol()
        node_mid.run_protocol()
        nodeB.run_protocol()

        self.network._run()

        self.network._increment_time(SWAPPING_INCREMENT_TIME)

        # clean used protocols
        nodeA.remove_used_protocol()
        nodeB.remove_used_protocol()
        node_mid.remove_used_protocol()

        # check the success
        success: bool = self._is_entangled(nodeA_id=nodeA_id, nodeB_id=nodeB_id, 
                                            nodeA_memory_position=Directions.RIGHT, 
                                            nodeB_memory_position=Directions.LEFT)
        # if the swapping protocoal was a success
        if success:
            log.debug(f"The entanglement swapping protocol between {nodeA.name} and {nodeB.name} was a success")
            return Swapping_Response.SWAPPING_SUCCESS
        
        # if the swapping protocoal filed
        log.debug(f"The entanglement swapping protocol between {nodeA.name} and {nodeB.name} failed")
        return Swapping_Response.SWAPPING_FAIL
    
    def _is_entangled(self, nodeA_id: int, nodeB_id: int, nodeA_memory_position: Directions, nodeB_memory_position: Directions) -> bool:
        """
        Check the entanglement between nodeA and nodeB

        Args:
            nodeA_id (int): Node to check the entanglement
            nodeB_id (int): Node to check the entanglement
            nodeA_memory_position (Directions): Memory's position of the nodeA
            nodeB_memory_position (Directions): Memory's position of the nodeB

        Returns:
            bool: If are entangled returns True, else returns False
        """
        nodeA: QuantumRepeater = self.network.nodes[nodeA_id]
        nodeB: QuantumRepeater = self.network.nodes[nodeB_id]

        nodeA_memory: Memory = nodeA.resource_manager.get_memory(nodeA_memory_position)
        nodeB_memory: Memory = nodeB.resource_manager.get_memory(nodeB_memory_position)

        # if memories aren't entangled
        if (nodeA_memory.entangled_memory['node_id'] != nodeB.name or
             nodeB_memory.entangled_memory['node_id'] != nodeA.name):
            return False

        return True

    def get_data(self) -> dict:
        return self.data