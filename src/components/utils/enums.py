from enum import Enum

class Directions(Enum):
    """
    Directons of the memory
    """
    LEFT: str = 'left'
    RIGHT: str = 'right'

class Topologies(Enum):
    """
    Topologies of the network
    """
    GRID: str = 'grid'
    LINE: str = 'line'
    RING: str = 'ring'
    ERDOS_RENYI: str = 'erdos-renyi'
    BARABASI_ALBERT: str = 'basabasi-albert'