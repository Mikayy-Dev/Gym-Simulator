import pygame
import os

class AudioManager:
    def __init__(self):
        self.background_music = None
        self.sound_effects = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.is_muted = False
        
        # Initialize pygame mixer with very low latency settings
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=256)
        pygame.mixer.init()
        
        # Load background music
        self.load_background_music()
        
    def load_background_music(self):
        """Load background music from the audio folder"""
        audio_folder = "Audio"
        if os.path.exists(audio_folder):
            # Look for common audio files
            audio_files = [f for f in os.listdir(audio_folder) 
                         if f.lower().endswith(('.mp3', '.wav', '.ogg'))]
            
            if audio_files:
                # Use the first audio file found
                music_path = os.path.join(audio_folder, audio_files[0])
                try:
                    pygame.mixer.music.load(music_path)
                except Exception as e:
                    pass
            else:
                pass
        else:
            pass
    
    def play_background_music(self, loop=True):
        """Play background music"""
        if not self.is_muted and pygame.mixer.music.get_busy() == 0:
            try:
                pygame.mixer.music.play(-1 if loop else 0)
                pygame.mixer.music.set_volume(self.music_volume)
            except Exception as e:
                pass
    
    def stop_background_music(self):
        """Stop background music"""
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            pass
    
    def pause_background_music(self):
        """Pause background music"""
        try:
            pygame.mixer.music.pause()
        except Exception as e:
            print(f"Could not pause background music: {e}")
    
    def unpause_background_music(self):
        """Unpause background music"""
        try:
            pygame.mixer.music.unpause()
        except Exception as e:
            print(f"Could not unpause background music: {e}")
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def toggle_mute(self):
        """Toggle mute state"""
        self.is_muted = not self.is_muted
        if self.is_muted:
            pygame.mixer.music.set_volume(0.0)
        else:
            pygame.mixer.music.set_volume(self.music_volume)
        return self.is_muted
    
    def load_sound_effect(self, name, file_path):
        """Load a sound effect"""
        try:
            print(f"DEBUG: Loading sound effect '{name}' from '{file_path}'")
            sound = pygame.mixer.Sound(file_path)
            self.sound_effects[name] = sound
            print(f"DEBUG: Successfully loaded sound effect '{name}'")
        except Exception as e:
            print(f"Could not load sound effect {name}: {e}")
    
    def play_sound_effect(self, name):
        """Play a sound effect"""
        print(f"DEBUG: Attempting to play sound effect '{name}'")
        print(f"DEBUG: Muted: {self.is_muted}, Sound exists: {name in self.sound_effects}")
        print(f"DEBUG: Available sound effects: {list(self.sound_effects.keys())}")
        if not self.is_muted and name in self.sound_effects:
            try:
                sound = self.sound_effects[name]
                sound.set_volume(self.sfx_volume)
                sound.play()
                print(f"DEBUG: Successfully playing sound effect '{name}'")
            except Exception as e:
                print(f"Could not play sound effect {name}: {e}")
        else:
            if self.is_muted:
                print(f"DEBUG: Sound effect '{name}' not played - audio is muted")
            elif name not in self.sound_effects:
                print(f"DEBUG: Sound effect '{name}' not found in loaded effects")
    
    def stop_sound_effect(self, name):
        """Stop a specific sound effect"""
        if name in self.sound_effects:
            try:
                sound = self.sound_effects[name]
                sound.stop()
            except Exception as e:
                print(f"Could not stop sound effect {name}: {e}")
    
    def stop_all_sound_effects(self):
        """Stop all currently playing sound effects"""
        try:
            pygame.mixer.stop()
        except Exception as e:
            print(f"Could not stop sound effects: {e}")
    
    def cleanup(self):
        """Clean up audio resources"""
        pygame.mixer.quit()
