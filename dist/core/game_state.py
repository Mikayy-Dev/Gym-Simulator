import pygame
from .constants import *

class StateManager:
    """Manages different game states and their transitions"""
    
    def __init__(self, audio_system=None):
        self.current_state = None
        self.states = {}
        self.audio_system = audio_system
        self._initialize_states()
    
    def _initialize_states(self):
        """Initialize all game states"""
        from .screens.title_screen_state import TitleScreenState
        from .screens.game_screen_state import GameScreenState
        from .screens.settings_screen_state import SettingsScreenState
        
        self.states = {
            "title": TitleScreenState(),
            "game": GameScreenState(self.audio_system),
            "settings": SettingsScreenState()
        }
    
    def change_state(self, state_name):
        """Change to a different state"""
        if state_name in self.states:
            # Clean up current state
            if self.current_state and hasattr(self.states[self.current_state], 'exit'):
                self.states[self.current_state].exit()
            
            # Handle audio transitions
            self._handle_audio_transition(self.current_state, state_name)
            
            # Switch to new state
            self.current_state = state_name
            
            # Initialize new state
            if hasattr(self.states[self.current_state], 'enter'):
                self.states[self.current_state].enter()
    
    def get_current_state(self):
        """Get the name of the current state"""
        return self.current_state
    
    def update(self, delta_time, events):
        """Update current state"""
        if self.current_state and self.current_state in self.states:
            action = self.states[self.current_state].update(delta_time, events)
            if action:
                self._handle_state_transition(action)
    
    def draw(self, screen):
        """Draw current state"""
        if self.current_state and self.current_state in self.states:
            self.states[self.current_state].draw(screen)
    
    def _handle_audio_transition(self, from_state, to_state):
        """Handle audio transitions between states"""
        if not self.audio_system:
            return
        
        # Title to Game transition
        if from_state == "title" and to_state == "game":
            self.audio_system.audio_manager.stop_all_sound_effects()  # Stop title music
            self.audio_system.set_volume(0.7)  # Reset to normal volume
            self.audio_system.play_background_music(loop=True)
        
        # Game to Title transition
        elif from_state == "game" and to_state == "title":
            self.audio_system.stop_background_music()  # Stop game music
            self.audio_system.set_volume(0.3)  # Set to 30% volume
            self.audio_system.play_sound("title_music")
    
    def _handle_state_transition(self, action):
        """Handle transitions between states"""
        if action == "Start Game":
            self.change_state("game")
        elif action == "Quit":
            return "quit"
        elif action == "Back to Title":
            self.change_state("title")
        elif action == "Settings":
            self.change_state("settings")
        
        return None

class TitleState:
    """Handles title screen state"""
    
    def __init__(self):
        self.title_screen = None
    
    def update(self, delta_time, events):
        if not self.title_screen:
            from .title_screen import TitleScreen
            self.title_screen = TitleScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        self.title_screen.update(delta_time)
        return self.title_screen.handle_input(events)
    
    def draw(self, screen):
        if self.title_screen:
            self.title_screen.draw(screen)

class GameState:
    """Handles main game state"""
    
    def __init__(self):
        self.initialized = False
        self.player = None
        self.camera = None
        self.tilemap = None
        self.gym_manager = None
        self.npcs = []
        self.npc_configs = []
    
    def initialize(self):
        """Initialize game components"""
        if self.initialized:
            return
        
        from .player import Player
        from .camera import Camera
        from .tile_map import TileMap
        from gym_objects import GymObjectManager
        
        self.player = Player(320, 208)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.tilemap = TileMap("tilemap/gym2_Tile Layer 1.csv", "tilemap/gym2_Tile Layer 2.csv")
        self.player.set_tilemap(self.tilemap)
        self.tilemap.player = self.player
        
        self.gym_manager = GymObjectManager()
        self.gym_manager.setup_from_tilemap(self.tilemap)
        
        if hasattr(self.player, 'collision_system'):
            self.player.collision_system.set_gym_manager(self.gym_manager)
        
        self.npcs = []
        self.npc_configs = []
        self.initialized = True
    
    def update(self, delta_time, events):
        """Update game logic"""
        if not self.initialized:
            self.initialize()
        
        # Handle input events
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.handle_key_input(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_input(event)
        
        # Update game components
        self.update_game_components(delta_time)
        
        return None
    
    def handle_key_input(self, event):
        """Handle keyboard input"""
        if event.key == pygame.K_ESCAPE:
            return "Back to Title"
        # Add other key handling here
    
    def handle_mouse_input(self, event):
        """Handle mouse input"""
        # Add mouse handling here
        pass
    
    def update_game_components(self, delta_time):
        """Update all game components"""
        if not self.initialized:
            return
        
        # Update player
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.camera.follow(self.player)
        self.player.update_stamina(delta_time)
        
        # Update gym objects
        self.gym_manager.update_all(delta_time)
        
        # Update NPCs
        for npc in self.npcs:
            npc.update(delta_time)
    
    def draw(self, screen):
        """Draw game"""
        if not self.initialized:
            return
        
        screen.fill("black")
        
        # Draw game components
        self.tilemap.draw_floors_only(screen, self.camera)
        self.gym_manager.draw_all(screen, self.camera)
        self.tilemap.draw_walls_only(screen, self.camera)
        
        # Draw entities
        for npc in self.npcs:
            npc.draw(screen, self.camera)
        
        self.player.draw(screen)

class SettingsState:
    """Handles settings state"""
    
    def update(self, delta_time, events):
        # Add settings logic here
        return None
    
    def draw(self, screen):
        # Add settings drawing here
        pass
