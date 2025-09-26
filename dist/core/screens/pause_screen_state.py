"""
Pause Screen State
Handles the pause menu overlay
"""

import pygame
from .base_screen_state import BaseScreenState
from ..constants import *

class PauseScreenState(BaseScreenState):
    """Handles the pause menu screen"""
    
    def __init__(self, audio_system=None):
        super().__init__()
        self.audio_system = audio_system
        self.selected_option = 0
        self.options = ["Resume", "Back to Title"]
        self.font = None
        self.title_font = None
        self.background_surface = None
        
    def enter(self):
        """Called when entering the pause state"""
        try:
            self.font = pygame.font.Font("Font/Retro Gaming.ttf", 32)
            self.title_font = pygame.font.Font("Font/Retro Gaming.ttf", 48)
        except:
            self.font = pygame.font.Font(None, 32)
            self.title_font = pygame.font.Font(None, 48)
        
        self.selected_option = 0
        self.background_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background_surface.set_alpha(128)
        self.background_surface.fill((0, 0, 0))
        pygame.mouse.set_visible(False)
        
        # Pause background music when entering pause screen
        if self.audio_system:
            self.audio_system.pause_background_music()
    
    def exit(self):
        """Called when exiting the pause state"""
        pygame.mouse.set_visible(False)
    
    def update(self, delta_time, events):
        """Update pause menu logic"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "Resume"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    clicked_option = self._get_option_at_position(mouse_x, mouse_y)
                    if clicked_option is not None:
                        return self.options[clicked_option]
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                hovered_option = self._get_option_at_position(mouse_x, mouse_y)
                if hovered_option is not None:
                    self.selected_option = hovered_option
        
        return None
    
    def _get_option_at_position(self, mouse_x, mouse_y):
        """Get the option index at the given mouse position"""
        for i, option in enumerate(self.options):
            option_text = self.font.render(option, True, (255, 255, 255))
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 50))
            
            # Expand the clickable area slightly
            expanded_rect = option_rect.inflate(20, 10)
            if expanded_rect.collidepoint(mouse_x, mouse_y):
                return i
        return None
    
    def draw(self, screen):
        """Draw the pause menu"""
        # Draw semi-transparent background
        screen.blit(self.background_surface, (0, 0))
        
        # Draw title
        title_text = self.title_font.render("PAUSED", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(title_text, title_rect)
        
        # Draw options
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
            option_text = self.font.render(option, True, color)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 50))
            
            # Draw background for selected/hovered option
            if i == self.selected_option:
                background_rect = option_rect.inflate(20, 10)
                pygame.draw.rect(screen, (50, 50, 50), background_rect)
                pygame.draw.rect(screen, (100, 100, 100), background_rect, 2)
            
            screen.blit(option_text, option_rect)
        
        # Draw instructions
        instruction_text = self.font.render("Click to select, ESC to resume", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(instruction_text, instruction_rect)
    
    def get_cursor_type(self):
        """Get the current cursor type for the game engine"""
        return "default"
