"""
Input System
Handles all input processing and state management
"""

import pygame
from typing import List, Dict, Any

class InputSystem:
    """Manages all input handling"""
    
    def __init__(self):
        self.keys_pressed = {}
        self.mouse_pos = (0, 0)
        self.mouse_buttons = {}
        self.input_handlers = []
    
    def update(self, events: List[pygame.event.Event]):
        """Update input system with new events"""
        # Update mouse position
        self.mouse_pos = pygame.mouse.get_pos()
        
        # Update key states
        self.keys_pressed = pygame.key.get_pressed()
        
        # Update mouse button states
        mouse_buttons = pygame.mouse.get_pressed()
        self.mouse_buttons = {
            'left': mouse_buttons[0],
            'middle': mouse_buttons[1],
            'right': mouse_buttons[2]
        }
        
        # Process events
        for event in events:
            self._process_event(event)
    
    def _process_event(self, event: pygame.event.Event):
        """Process individual events"""
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
        elif event.type == pygame.KEYUP:
            self._handle_keyup(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self._handle_mouse_up(event)
    
    def _handle_keydown(self, event: pygame.event.Event):
        """Handle key down events"""
        # Add any global key handling here
        pass
    
    def _handle_keyup(self, event: pygame.event.Event):
        """Handle key up events"""
        # Add any global key handling here
        pass
    
    def _handle_mouse_down(self, event: pygame.event.Event):
        """Handle mouse button down events"""
        # Add any global mouse handling here
        pass
    
    def _handle_mouse_up(self, event: pygame.event.Event):
        """Handle mouse button up events"""
        # Add any global mouse handling here
        pass
    
    def is_key_pressed(self, key: int) -> bool:
        """Check if a key is currently pressed"""
        return self.keys_pressed[key]
    
    def is_mouse_button_pressed(self, button: str) -> bool:
        """Check if a mouse button is currently pressed"""
        return self.mouse_buttons.get(button, False)
    
    def get_mouse_position(self) -> tuple:
        """Get current mouse position"""
        return self.mouse_pos
    
    def add_input_handler(self, handler):
        """Add an input handler"""
        self.input_handlers.append(handler)
    
    def remove_input_handler(self, handler):
        """Remove an input handler"""
        if handler in self.input_handlers:
            self.input_handlers.remove(handler)
