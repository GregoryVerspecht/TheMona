from enum import Enum

class GameState(str, Enum):
    IDLE = "IDLE"
    LOBBY = "LOBBY"
    RUNNING = "RUNNING"
    ENDED = "ENDED"
