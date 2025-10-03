
"""
Gym Simulaton Game - Main Entry Point
""" 

import pygame
import sys
from core.game_engine import GameEngine

def main():
    """Main entry point for the game"""
    try:
        # Initialize Pygame
        pygame.init()
        
        # Create and run the game engine
        game_engine = GameEngine()
        game_engine.run()
        
    except Exception as e:
        sys.exit(1)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
