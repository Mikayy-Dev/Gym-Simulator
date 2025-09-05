"""
Audio System
Handles all audio playback and management
"""

import pygame
from core.audio import AudioManager

class AudioSystem:
    """Manages all audio in the game"""
    
    def __init__(self):
        self.audio_manager = AudioManager()
        self._setup_audio()
    
    def _setup_audio(self):
        """Set up audio system with default settings"""
        # Load sound effects
        self.audio_manager.load_sound_effect("spray_bottle", "Audio/spray.mp3")
        self.audio_manager.load_sound_effect("machine shutdown", "Audio/machine shutdown.mp3")
        self.audio_manager.load_sound_effect("star_full", "Audio/ronnie_coleman.wav")
        self.audio_manager.load_sound_effect("all_stars_full", "Audio/Woohoo!.wav")
        self.audio_manager.load_sound_effect("title_music", "Audio/title_screen.mp3")
        self.audio_manager.load_sound_effect("dumbbell", "Audio/dumbbell.mp3")
        self.audio_manager.load_sound_effect("squat_rerack", "Audio/squat_rerack.wav")
        self.audio_manager.load_sound_effect("scanner", "Audio/scanner.mp3")
        
        # Set initial volume
        self.audio_manager.set_sfx_volume(0.3)
        self.audio_manager.play_sound_effect("title_music")
    
    def update(self, delta_time: float):
        """Update audio system"""
        # Audio system doesn't need per-frame updates
        pass
    
    def play_sound(self, sound_name: str):
        """Play a sound effect"""
        self.audio_manager.play_sound_effect(sound_name)
    
    def play_background_music(self, loop: bool = True):
        """Play background music"""
        self.audio_manager.play_background_music(loop=loop)
    
    def stop_background_music(self):
        """Stop background music"""
        self.audio_manager.stop_background_music()
    
    def set_volume(self, volume: float):
        """Set sound effects volume"""
        self.audio_manager.set_sfx_volume(volume)
    
    def set_music_volume(self, volume: float):
        """Set music volume"""
        self.audio_manager.set_music_volume(volume)
    
    def toggle_mute(self):
        """Toggle audio mute"""
        self.audio_manager.toggle_mute()
    
    def cleanup(self):
        """Clean up audio resources"""
        self.audio_manager.cleanup()
