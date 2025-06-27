from enum import Enum

class Directions(Enum):
    """
    Directons of the memory
    """
    LEFT = 'left'
    RIGHT = 'right'

class Topologies(Enum):
    """
    Topologies of the network
    """
    BARABASI_ALBERT = 'basabasi-albert'
    ERDOS_RENYI = 'erdos-renyi'
    GRID = 'grid'
    LINE = 'line'
    RING = 'ring'
    STAR = 'star'

class Node_Types(Enum):
    """
    Types of Nodes
    """
    QUANTUM_REPEATER = 'quantum-repeater'
    BSM_NODE = 'bsm-node'

class Request_Response(Enum):
    """
    Types of responses to request
    """
    NO_PATH = 'no-path'
    NO_ENTANGLED = 'no-entangled'
    ENTANGLED_SUCCESS = 'entangled-success'
    ENTANGLED_FAIL = 'entangled-fail'
    NON_EXISTENT_NODE = 'non-existent-node'
    NON_EXISTENT_BSM_NODE = 'non-existent-bsm-node'

class Swapping_Response(Enum):
    """
    Types of responses to entanglement swapping protocol
    """
    NO_ENTANGLED = 'no-entangled'
    SWAPPING_SUCCESS = 'swapping-success'
    SWAPPING_FAIL = 'swapping-fail'


class Protocol_Types(Enum):
    """
    Types of protocols 
    """
    ENTANGLEMENT = 'entanglement'
    SWAPPING_A = 'swapping-a'
    SWAPPING_B = 'swapping-b'