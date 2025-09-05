"""
Gym Simulation Core Package
Main game engine and core systems
"""

from .game_engine import GameEngine
from .game_state import StateManager
from .game_clock import GameClock

__version__ = "1.0.0"
__author__ = "Gym Sim Developer"

# Control what gets imported with "from core import *"
__all__ = [
    "GameEngine",
    "StateManager", 
    "GameClock"
]
