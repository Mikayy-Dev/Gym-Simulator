"""
Asset Manager
Centralized asset loading and management system
"""

import pygame
import os
from typing import Dict, Any

class AssetManager:
    """Manages all game assets (textures, sounds, fonts)"""
    
    def __init__(self):
        self.textures = {}
        self.sounds = {}
        self.fonts = {}
        self._load_default_assets()
    
    def _load_default_assets(self):
        """Load default game assets"""
        # Load default font
        try:
            self.fonts['default'] = pygame.font.Font("Font/Retro Gaming.ttf", 24)
        except:
            self.fonts['default'] = pygame.font.Font(None, 24)
        
        # Load cursor images
        self._load_cursors()
        
        # Load sound effects
        self._load_sound_effects()
    
    def _load_cursors(self):
        """Load custom cursor images"""
        cursor_names = [
            "cursor1.png", "cursor2.png", "cursor3.png", 
            "pointer-cursor.png", "hand_cursor.png", "scanner_cursor.png"
        ]
        
        for i, cursor_file in enumerate(cursor_names):
            try:
                cursor_path = f"Graphics/{cursor_file}"
                cursor_img = pygame.image.load(cursor_path)
                cursor_img = pygame.transform.scale(cursor_img, (24, 24))
                self.textures[f'cursor_{i}'] = cursor_img
            except Exception as e:
                print(f"Warning: Could not load cursor {cursor_file}: {e}")
    
    def _load_sound_effects(self):
        """Load sound effects"""
        sound_files = {
            "spray_bottle": "Audio/Spray Bottle - Sound Effect (HD).mp3",
            "machine_shutdown": "Audio/machine shutdown.mp3",
            "star_full": "Audio/ronnie_coleman.wav",
            "all_stars_full": "Audio/Woohoo!.wav",
            "title_music": "Audio/title_screen.mp3",
            "dumbbell": "Audio/dumbbell.mp3",
            "squat_rerack": "Audio/squat_rerack.wav",
            "scanner": "Audio/scanner.mp3"
        }
        
        for name, path in sound_files.items():
            try:
                if os.path.exists(path):
                    sound = pygame.mixer.Sound(path)
                    self.sounds[name] = sound
            except Exception as e:
                print(f"Warning: Could not load sound {name}: {e}")
    
    def get_texture(self, name: str) -> pygame.Surface:
        """Get a texture by name"""
        return self.textures.get(name)
    
    def get_sound(self, name: str) -> pygame.mixer.Sound:
        """Get a sound by name"""
        return self.sounds.get(name)
    
    def get_font(self, name: str = 'default') -> pygame.font.Font:
        """Get a font by name"""
        return self.fonts.get(name, self.fonts['default'])
    
    def load_texture(self, name: str, path: str) -> bool:
        """Load a texture from file"""
        try:
            texture = pygame.image.load(path)
            self.textures[name] = texture
            return True
        except Exception as e:
            print(f"Error loading texture {name}: {e}")
            return False
    
    def load_sound(self, name: str, path: str) -> bool:
        """Load a sound from file"""
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
            return True
        except Exception as e:
            print(f"Error loading sound {name}: {e}")
            return False
