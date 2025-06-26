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

class Request_Response(Enum):
    """
    Types of responses to request
    """
    NO_PATH = 'no-path'
    ENTANGLED_SUCCESS = 'entangled-success'
    ENTANGLED_FAIL = 'entangled-fail'

class Protocol_Types(Enum):
    """
    Types of protocols 
    """
    ENTANGLEMENT = 'entanglement'
    SWAPPING_A = 'swapping-a'
    SWAPPING_B = 'swapping-b'