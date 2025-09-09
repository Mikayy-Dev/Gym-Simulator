"""
Settings Screen State
Handles the settings screen
"""

import pygame
from .base_screen_state import BaseScreenState

class SettingsScreenState(BaseScreenState):
    """Handles settings screen state"""
    
    def __init__(self, audio_system=None, game_engine=None, from_state="pause"):
        super().__init__()
        self.font = None
        self.title_font = None
        self.audio_system = audio_system
        self.game_engine = game_engine
        self.from_state = from_state
        self.settings = {
            "volume": 0.7,
            "music_volume": 0.5,
            "show_fps": False,
            "debug_mode": False
        }
        self.selected_setting = 0
        self.settings_list = list(self.settings.keys())
        # Set back option based on where we came from
        if from_state == "pause":
            self.back_option = "Back to Pause Menu"
        else:
            self.back_option = "Back to Title"
    
    def enter(self):
        """Called when entering this state"""
        try:
            self.font = pygame.font.Font("Font/Retro Gaming.ttf", 24)
            self.title_font = pygame.font.Font("Font/Retro Gaming.ttf", 36)
        except:
            self.font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 36)
        pygame.mouse.set_visible(False)
    
    def update(self, delta_time, events):
        """Update settings screen logic"""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                clicked_setting = self._get_setting_at_position(mouse_x, mouse_y)
                
                if clicked_setting is not None:
                    if clicked_setting == len(self.settings_list):  # Back option
                        return self.back_option
                    else:
                        self.selected_setting = clicked_setting
                        setting = self.settings_list[self.selected_setting]
                        
                        if event.button == 1:  # Left click
                            if setting in ["volume", "music_volume"]:
                                self._decrease_volume_setting(setting)
                            else:
                                self._toggle_setting()
                        elif event.button == 3:  # Right click
                            if setting in ["volume", "music_volume"]:
                                self._increase_volume_setting(setting)
                            else:
                                self._toggle_setting()
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                hovered_setting = self._get_setting_at_position(mouse_x, mouse_y)
                if hovered_setting is not None:
                    self.selected_setting = hovered_setting
        
        return None
    
    def _get_setting_at_position(self, mouse_x, mouse_y):
        """Get the setting index at the given mouse position"""
        y_offset = 200
        for i, (setting, value) in enumerate(self.settings.items()):
            # Create text to get proper rect size
            if setting in ["volume", "music_volume"]:
                text = f"{setting.replace('_', ' ').title()}: {value:.1f}"
            else:
                text = f"{setting.replace('_', ' ').title()}: {'ON' if value else 'OFF'}"
            
            setting_text = self.font.render(text, True, (255, 255, 255))
            setting_rect = setting_text.get_rect(center=(1280 // 2, y_offset))
            expanded_rect = setting_rect.inflate(20, 10)
            
            if expanded_rect.collidepoint(mouse_x, mouse_y):
                return i
            y_offset += 50
        
        # Check for back option
        back_text = self.font.render(self.back_option, True, (255, 255, 255))
        back_rect = back_text.get_rect(center=(1280 // 2, y_offset))
        expanded_back_rect = back_rect.inflate(20, 10)
        
        if expanded_back_rect.collidepoint(mouse_x, mouse_y):
            return len(self.settings_list)  # Back option index
        
        return None
    
    def _toggle_setting(self):
        """Toggle the currently selected setting"""
        setting = self.settings_list[self.selected_setting]
        if setting in ["volume", "music_volume"]:
            # For volume settings, cycle through values
            if self.settings[setting] >= 1.0:
                self.settings[setting] = 0.0
            else:
                self.settings[setting] = min(1.0, self.settings[setting] + 0.2)
            
            # Apply volume settings to audio system
            if self.audio_system:
                if setting == "volume":
                    self.audio_system.set_volume(self.settings[setting])
                elif setting == "music_volume":
                    self.audio_system.set_music_volume(self.settings[setting])
                    
        elif setting in ["show_fps", "debug_mode"]:
            # For boolean settings, toggle
            self.settings[setting] = not self.settings[setting]
            
            # Apply debug settings to game engine
            if self.game_engine:
                if setting == "show_fps":
                    self.game_engine.show_fps = self.settings[setting]
                elif setting == "debug_mode":
                    self.game_engine.debug_mode = self.settings[setting]
                    # Debug mode only enables the TAB key functionality
                    # Hitboxes are controlled by TAB key, not automatically shown
    
    def _decrease_setting(self):
        """Decrease the currently selected setting"""
        setting = self.settings_list[self.selected_setting]
        if setting in ["volume", "music_volume"]:
            self.settings[setting] = max(0.0, self.settings[setting] - 0.1)
        elif setting in ["show_fps", "debug_mode"]:
            self.settings[setting] = False
            # Apply settings to game engine
            if self.game_engine:
                if setting == "show_fps":
                    self.game_engine.show_fps = self.settings[setting]
                elif setting == "debug_mode":
                    self.game_engine.debug_mode = self.settings[setting]
    
    def _increase_setting(self):
        """Increase the currently selected setting"""
        setting = self.settings_list[self.selected_setting]
        if setting in ["volume", "music_volume"]:
            self.settings[setting] = min(1.0, self.settings[setting] + 0.1)
        elif setting in ["show_fps", "debug_mode"]:
            self.settings[setting] = True
            # Apply settings to game engine
            if self.game_engine:
                if setting == "show_fps":
                    self.game_engine.show_fps = self.settings[setting]
                elif setting == "debug_mode":
                    self.game_engine.debug_mode = self.settings[setting]
    
    def _increase_volume_setting(self, setting):
        """Increase volume setting"""
        self.settings[setting] = min(1.0, self.settings[setting] + 0.1)
        # Apply volume settings to audio system
        if self.audio_system:
            if setting == "volume":
                self.audio_system.set_volume(self.settings[setting])
            elif setting == "music_volume":
                self.audio_system.set_music_volume(self.settings[setting])
    
    def _decrease_volume_setting(self, setting):
        """Decrease volume setting"""
        self.settings[setting] = max(0.0, self.settings[setting] - 0.1)
        # Apply volume settings to audio system
        if self.audio_system:
            if setting == "volume":
                self.audio_system.set_volume(self.settings[setting])
            elif setting == "music_volume":
                self.audio_system.set_music_volume(self.settings[setting])
    
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
            
            # Draw background for selected/hovered setting
            if i == self.selected_setting:
                background_rect = setting_rect.inflate(20, 10)
                pygame.draw.rect(screen, (50, 50, 50), background_rect)
                pygame.draw.rect(screen, (100, 100, 100), background_rect, 2)
            
            screen.blit(setting_text, setting_rect)
            y_offset += 50
        
        # Draw back option
        back_color = (255, 255, 0) if self.selected_setting == len(self.settings_list) else (255, 255, 255)
        back_text = self.font.render(self.back_option, True, back_color)
        back_rect = back_text.get_rect(center=(screen.get_width() // 2, y_offset))
        
        # Draw background for selected/hovered back option
        if self.selected_setting == len(self.settings_list):
            background_rect = back_rect.inflate(20, 10)
            pygame.draw.rect(screen, (50, 50, 50), background_rect)
            pygame.draw.rect(screen, (100, 100, 100), background_rect, 2)
        
        screen.blit(back_text, back_rect)
        y_offset += 50
        
        # Draw instructions
        instructions = [
            "Left click: decrease volume / toggle setting",
            "Right click: increase volume / toggle setting",
            "Hover to highlight options"
        ]
        
        y_offset += 50
        for instruction in instructions:
            inst_text = self.font.render(instruction, True, (128, 128, 128))
            inst_rect = inst_text.get_rect(center=(screen.get_width() // 2, y_offset))
            screen.blit(inst_text, inst_rect)
            y_offset += 30
    
    def get_cursor_type(self):
        """Get the current cursor type for the game engine"""
        return "default"
