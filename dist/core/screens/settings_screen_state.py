"""
Settings Screen State
Handles the settings screen
"""

import pygame
from .base_screen_state import BaseScreenState

class SettingsScreenState(BaseScreenState):
    """Handles settings screen state"""
    
    def __init__(self):
        super().__init__()
        self.font = None
        self.title_font = None
        self.settings = {
            "volume": 0.7,
            "music_volume": 0.5,
            "show_fps": False,
            "debug_mode": False
        }
        self.selected_setting = 0
        self.settings_list = list(self.settings.keys())
    
    def enter(self):
        """Called when entering this state"""
        try:
            self.font = pygame.font.Font("Font/Retro Gaming.ttf", 24)
            self.title_font = pygame.font.Font("Font/Retro Gaming.ttf", 36)
        except:
            self.font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 36)
    
    def update(self, delta_time, events):
        """Update settings screen logic"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "Back to Title"
                elif event.key == pygame.K_UP:
                    self.selected_setting = (self.selected_setting - 1) % len(self.settings_list)
                elif event.key == pygame.K_DOWN:
                    self.selected_setting = (self.selected_setting + 1) % len(self.settings_list)
                elif event.key == pygame.K_LEFT:
                    self._decrease_setting()
                elif event.key == pygame.K_RIGHT:
                    self._increase_setting()
        
        return None
    
    def _decrease_setting(self):
        """Decrease the currently selected setting"""
        setting = self.settings_list[self.selected_setting]
        if setting in ["volume", "music_volume"]:
            self.settings[setting] = max(0.0, self.settings[setting] - 0.1)
        elif setting in ["show_fps", "debug_mode"]:
            self.settings[setting] = False
    
    def _increase_setting(self):
        """Increase the currently selected setting"""
        setting = self.settings_list[self.selected_setting]
        if setting in ["volume", "music_volume"]:
            self.settings[setting] = min(1.0, self.settings[setting] + 0.1)
        elif setting in ["show_fps", "debug_mode"]:
            self.settings[setting] = True
    
    def draw(self, screen):
        """Draw settings screen"""
        screen.fill((0, 0, 0))
        
        # Draw title
        title_text = self.title_font.render("Settings", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title_text, title_rect)
        
        # Draw settings
        y_offset = 200
        for i, (setting, value) in enumerate(self.settings.items()):
            color = (255, 255, 0) if i == self.selected_setting else (255, 255, 255)
            
            if setting in ["volume", "music_volume"]:
                text = f"{setting.replace('_', ' ').title()}: {value:.1f}"
            else:
                text = f"{setting.replace('_', ' ').title()}: {'ON' if value else 'OFF'}"
            
            setting_text = self.font.render(text, True, color)
            setting_rect = setting_text.get_rect(center=(screen.get_width() // 2, y_offset))
            screen.blit(setting_text, setting_rect)
            y_offset += 50
        
        # Draw instructions
        instructions = [
            "Use UP/DOWN to select setting",
            "Use LEFT/RIGHT to change value",
            "Press ESC to go back"
        ]
        
        y_offset += 50
        for instruction in instructions:
            inst_text = self.font.render(instruction, True, (128, 128, 128))
            inst_rect = inst_text.get_rect(center=(screen.get_width() // 2, y_offset))
            screen.blit(inst_text, inst_rect)
            y_offset += 30
