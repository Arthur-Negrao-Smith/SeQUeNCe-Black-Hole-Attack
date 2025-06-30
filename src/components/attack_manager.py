from .utils.enums import Attack_Types
from .nodes import QuantumRepeater

from random import choice
import logging
log: logging.Logger = logging.getLogger(__name__)

class Attack_Manager:
    """
    Class to manage attacks to network
    """
    from .network import Network
    def __init__(self, network: Network):
        self._attack_type: Attack_Types
        self.network: Network = network # type: ignore

    def create_black_holes(self, number_of_black_holes: int, swap_prob: int | float, targets_per_black_hole: int) -> None:
        """
        Create black holes to attack the network

        Args:
            number_of_black_holes (int): Number of black holes in the network
            swap_prob (int | float): BHA's entanglement swapping probability.
            targets_per_black_hole (int): Target's number of each black hole. If targets_per_black_hole < 1 this is parameter ignored
        """
        # if entanglement swapping isn't valid
        if swap_prob < 0 or swap_prob > 1:
            log.warning(f"No black hole was created. The parameter swap_prob is invalid: {swap_prob}")
            return
        
        # Add the attack type
        self._update_attack_type(Attack_Types.BLACK_HOLE)

        if targets_per_black_hole < 1:
            self._create_black_holes_no_targets(number_of_black_holes=number_of_black_holes, swap_prob=swap_prob)
        else:
            self._create_black_holes_with_targets(number_of_black_holes=number_of_black_holes, swap_prob=swap_prob, targets_per_black_hole=targets_per_black_hole)

        for bh in self.network.black_holes.values():
            log.debug(f"{bh.name} is a black hole with targets: {bh._black_hole_targets}")

    def _update_attack_type(self, attack_type: Attack_Types) -> None:
        """
        To updates the attack type's name

        Args:
            attack_type (Attack_Types): Attack type to updates
        """
        self._attack_type = attack_type

    def _create_black_holes_no_targets(self, number_of_black_holes: int, swap_prob: int | float) -> None:
        """
        Create black holes withtout targets in the network

        Args:
            number_of_black_holes (int): Number of black holes in the network
            swap_prob (int | float): BHA's entanglement swapping probability
        """
        if number_of_black_holes < 1:
            log.warning(f"No black hole was created. The parameter number_of_black_holes is invalid: {number_of_black_holes}")
            return
        
        if number_of_black_holes >= len(self.network.normal_nodes):
            log.warning(f"No black hole was created. The parameter number_of_black_holes is invalid: {number_of_black_holes} > number of normal nodes")
            return
        
        counter: int = number_of_black_holes
        avaliable_nodes_IDs: list[int] = list(self.network.normal_nodes.keys())
        while counter != 0:
            
            # select a random node
            tmp_id: int = choice(avaliable_nodes_IDs)
            avaliable_nodes_IDs.remove(tmp_id)

            # change the entanglement swapping probability
            tmp_node: QuantumRepeater = self.network.nodes[tmp_id]
            tmp_node.resource_manager._turn_black_hole(new_swap_prob=swap_prob, targets=None)
            
            # add to black holes
            self.network.black_holes[tmp_id] = self.network.nodes[tmp_id]

            # remove from normal nodes
            self.network.normal_nodes.pop(tmp_id)
            counter -= 1

        log.debug(f"The black holes: {self.network.black_holes.keys()}")

    def _create_black_holes_with_targets(self, number_of_black_holes: int, swap_prob: int | float, targets_per_black_hole: int) -> None:
        """
        Create black holes witht targets in the network

        Args:
            number_of_black_holes (int): Number of black holes in the network
            swap_prob (int | float): BHA's entanglement swapping probability
            targets_per_black_hole (int): Target's number of each black hole
        """
        if number_of_black_holes <= 0:
            log.warning(f"No black hole was created. The parameter number_of_black_holes is invalid: {number_of_black_holes}")
            return
        elif number_of_black_holes == self.network.number_of_nodes:
            log.warning(f"No black hole was created. The parameter number_of_black_holes is invalid: {number_of_black_holes} >= number of normal nodes")
            return
        
        if targets_per_black_hole <= 0:
            log.warning(f"No black hole was created. The parameter targets_per_black_hole is invalid: {targets_per_black_hole}")
            return
        elif len(self.network.normal_nodes) <= targets_per_black_hole:
            log.warning(f"No black hole was created. The parameter targets_per_black_hole is invalid: {targets_per_black_hole} >= number of normal nodes")
            return
        
        counter: int = number_of_black_holes

        while counter > 0:
            
            # convert normal nodes to a list
            avaliable_nodes_IDs: list = list(self.network.normal_nodes.keys())
            
            # select a random node to be a black hole
            tmp_bh_id: int = choice(avaliable_nodes_IDs)
            
            # remove the node from normal nodes' list
            avaliable_nodes_IDs.remove(tmp_bh_id)

            tmp_bh_node: QuantumRepeater = self.network.nodes[tmp_bh_id]

            # create a targets dict
            tmp_targets: dict[str, int | float] = dict()
            targets_counter: int = targets_per_black_hole
            while targets_counter > 0:
                tmp_normal_node_id: int = choice(avaliable_nodes_IDs)

                # update temporary targets
                tmp_normal_node: QuantumRepeater = self.network.nodes[tmp_normal_node_id]
                tmp_targets[tmp_normal_node.name] = swap_prob

                # remove the target from normal nodes
                avaliable_nodes_IDs.remove(tmp_normal_node_id)
                targets_counter -= 1

            # turn the node in a black hole
            tmp_bh_node.resource_manager._turn_black_hole(new_swap_prob=swap_prob, targets=tmp_targets)
            self.network.black_holes[tmp_bh_id] = tmp_bh_node

            # remove node from normal nodes
            self.network.normal_nodes.pop(tmp_bh_id)

            # update counter
            counter -= 1

        log.debug(f"{number_of_black_holes} were created with {targets_per_black_hole} targets. Black Holes: {self.network.black_holes.keys()}")
