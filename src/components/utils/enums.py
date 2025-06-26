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