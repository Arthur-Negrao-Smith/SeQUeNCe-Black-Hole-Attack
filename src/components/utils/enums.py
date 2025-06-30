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

class Attack_Types(Enum):
    """
    Type of attacks
    """
    BLACK_HOLE = 'black-hole'
    HIJACKING = 'hijacking'

class Request_Response(Enum):
    """
    Request protocol's response types
    """
    NO_PATH = 'no-path'
    NO_ENTANGLED = 'no-entangled'
    ENTANGLED_SUCCESS = 'entangled-success'
    ENTANGLED_FAIL = 'entangled-fail'
    NON_EXISTENT_NODE = 'non-existent-node'
    NON_EXISTENT_BSM_NODE = 'non-existent-bsm-node'
    SAME_NODE = 'same-node'

class Swapping_Response(Enum):
    """
    Swapping protocol's response types
    """
    NO_ENTANGLED = 'no-entangled'
    SWAPPING_SUCCESS = 'swapping-success'
    SWAPPING_FAIL = 'swapping-fail'

class Entanglement_Response(Enum):
    """
    Entanglement protocol's response types
    """
    SUCCESS = 'success'
    FAIL = 'fail'
    NON_EXISTENT_BSM_NODE = 'non-existent-bsm-node'

class Protocol_Types(Enum):
    """
    Types of protocols 
    """
    ENTANGLEMENT = 'entanglement'
    SWAPPING_A = 'swapping-a'
    SWAPPING_B = 'swapping-b'