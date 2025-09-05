"""
Title Screen State
Handles the title screen logic and rendering
"""

import pygame
from .base_screen_state import BaseScreenState
from core.title_screen import TitleScreen

class TitleScreenState(BaseScreenState):
    """Handles title screen state"""
    
    def __init__(self):
        super().__init__()
        self.title_screen = None
        self.current_cursor = "default"
    
    def enter(self):
        """Called when entering this state"""
        if not self.title_screen:
            self.title_screen = TitleScreen(1280, 720)
        pygame.mouse.set_visible(False)
    
    def exit(self):
        """Called when exiting this state"""
        pygame.mouse.set_visible(False)
    
    def update(self, delta_time, events):
        """Update title screen logic"""
        if not self.title_screen:
            return None
        
        self.title_screen.update(delta_time)
        return self.title_screen.handle_input(events)
    
    def draw(self, screen):
        """Draw title screen"""
        if self.title_screen:
            self.title_screen.draw(screen)
    
    def get_cursor_type(self):
        """Get the current cursor type for the game engine"""
        return self.current_cursor
