"""
Game Engine - Main game loop and system coordination
Handles the core game loop, timing, and system updates
"""

import pygame
from .game_state import StateManager
from .managers.asset_manager import AssetManager
from .managers.entity_manager import EntityManager
from .systems.audio.audio_system import AudioSystem
from .systems.input.input_system import InputSystem
from .systems.rendering.render_system import RenderSystem
from .constants import *

class GameEngine:
    """Main game engine class that coordinates all systems"""
    
    def __init__(self):
        """Initialize the game engine"""
        # Initialize Pygame display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Gym Simulation")
        
        # Initialize clock for FPS control
        self.clock = pygame.time.Clock()
        self.running = True
        self.delta_time = 0.0
        
        # Initialize core systems
        self.asset_manager = AssetManager()
        self.entity_manager = EntityManager()
        self.audio_system = AudioSystem()
        self.state_manager = StateManager(self.audio_system)
        
        # Initialize game systems
        self.input_system = InputSystem()
        self.render_system = RenderSystem(self.screen)
        
        # Set up custom cursors
        self._setup_cursors()
        
        # Initialize game state
        self.state_manager.change_state("title")
    
    def _setup_cursors(self):
        """Set up custom cursors for the game"""
        self.cursor_images = {}
        cursor_names = [
            "cursor1.png", "cursor2.png", "cursor3.png", 
            "pointer-cursor.png", "hand_cursor.png", "scanner_cursor.png",
            "spray_bottle.png"
        ]
        
        # Load cursors individually, don't fail if some are missing
        loaded_count = 0
        for i, cursor_file in enumerate(cursor_names):
            try:
                cursor_path = f"Graphics/{cursor_file}"
                cursor_img = pygame.image.load(cursor_path)
                cursor_img = pygame.transform.scale(cursor_img, (24, 24))
                self.cursor_images[i] = cursor_img
                loaded_count += 1
            except Exception as e:
                pass  # Silently skip missing cursors
        
        if loaded_count > 0:
            self.current_cursor = self.cursor_images[0]
            pygame.mouse.set_visible(False)
            self.custom_cursor = True
        else:
            self.custom_cursor = False
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Calculate delta time
            self.delta_time = self.clock.get_time() / 1000.0
            
            # Handle events
            events = pygame.event.get()
            self._handle_events(events)
            
            # Update systems
            self._update_systems(events)
            
            # Render frame
            self._render_frame()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)
    
    def _handle_events(self, events):
        """Handle pygame events"""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._handle_escape_key()
    
    def _handle_escape_key(self):
        """Handle escape key based on current state"""
        current_state = self.state_manager.get_current_state()
        if current_state == "game":
            self.state_manager.change_state("title")
        elif current_state == "title":
            self.running = False
    
    def _update_systems(self, events):
        """Update all game systems"""
        # Update input system
        self.input_system.update(events)
        
        # Update current state
        self.state_manager.update(self.delta_time, events)
        
        # Update entity manager
        self.entity_manager.update(self.delta_time)
        
        # Update audio system
        self.audio_system.update(self.delta_time)
    
    def _render_frame(self):
        """Render the current frame"""
        # Clear screen
        self.screen.fill("black")
        
        # Render current state
        self.state_manager.draw(self.screen)
        
        # Draw custom cursor if enabled
        if self.custom_cursor:
            self._draw_custom_cursor()
    
    def _draw_custom_cursor(self):
        """Draw custom cursor at mouse position"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Get cursor type from current state
        cursor_type = self._get_cursor_type()
        cursor_image = self._get_cursor_image(cursor_type)
        
        cursor_x = mouse_x - cursor_image.get_width() // 2
        cursor_y = mouse_y - cursor_image.get_height() // 2
        self.screen.blit(cursor_image, (cursor_x, cursor_y))
    
    def _get_cursor_type(self):
        """Get cursor type from current state"""
        current_state = self.state_manager.get_current_state()
        if current_state in self.state_manager.states:
            state = self.state_manager.states[current_state]
            if hasattr(state, 'get_cursor_type'):
                return state.get_cursor_type()
        return "default"
    
    def _get_cursor_image(self, cursor_type):
        """Get cursor image based on type"""
        cursor_mapping = {
            "default": 0,      # cursor1.png
            "hand": 4,         # hand_cursor.png
            "pointer": 3,      # pointer-cursor.png
            "scanner": 5,      # scanner_cursor.png
            "spray_bottle": 6  # spray_bottle.png
        }
        
        cursor_index = cursor_mapping.get(cursor_type, 0)
        return self.cursor_images.get(cursor_index, self.cursor_images[0])
    
    def quit(self):
        """Clean shutdown of the game engine"""
        self.running = False
        self.audio_system.cleanup()
        pygame.quit()
