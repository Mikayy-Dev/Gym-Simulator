import pygame
from gym_objects.base_object import GymObject

class Treadmill(GymObject):
    def __init__(self, x, y, treadmill_type="standard", scale=1.0):
        # Choose spritesheet based on treadmill type
        spritesheet_path = "Graphics/stardew_style_treadmill-sheet.png"
        
        # Call parent constructor first
        super().__init__(x, y, spritesheet_path, scale)
        
        # Now override the dimensions based on treadmill type (all are 48x64)
        self.sprite_width = int(48 * scale)
        self.sprite_height = int(64 * scale)
        

        
        # Clear cached sprite since dimensions changed
        self._cached_sprite = None
        self._cached_scale = None
        self._cached_zoom = None
        
        # Update rect and hitboxes with new dimensions
        self.rect = pygame.Rect(x, y, self.sprite_width, self.sprite_height)
        self.hitboxes = {
            "body": {"x": 0, "y": 0, "width": self.sprite_width, "height": self.sprite_height}
        }
         
        # State tracking
        self.on_but_not_occupied = False  # Treadmill is running but no one is using it
        
        # Animation properties
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1  # Time between frames (seconds) - faster than bench
        self.animation_frames = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Frames 0=idle, 1-6=workout, 7-10=on but not occupied
      
        # Set custom hitbox for treadmill (bottom half collideable)
        self.set_custom_hitbox(48, 24, 0, 10)  # 48x24 hitbox, offset 32 pixels down
        
        # Set interaction hitbox for player clicks (full sprite dimensions for easier clicking)
        self.set_interaction_hitbox(self.sprite_width, self.sprite_height, offset_x=0, offset_y=0)
        
        # Depth sorting properties - use actual collision area bottom
        collision_rect = self.get_collision_rect()
        self.depth_y = collision_rect.bottom  # Bottom of actual collision area
    
    def start_interaction(self, npc):
        """Start treadmill workout interaction"""
        # Check if treadmill is in "on but not occupied" state
        if self.on_but_not_occupied:
            return False
        
        if super().start_interaction(npc):
            # Set fixed 8-second cardio session for all NPCs
            self.interaction_duration = 8.0
            
            return True
        else:
            return False
    
    def end_interaction(self):
        """Override to handle treadmill-specific state transitions"""
        # Check if the occupying NPC is departing - if so, stop animation immediately
        if (self.occupying_npc and hasattr(self.occupying_npc, 'departure_pending') and 
            self.occupying_npc.departure_pending):
            # NPC is departing, stop animation and reset to idle
            self.animation_frame = 0
            self.on_but_not_occupied = False
        else:
            # Normal completion - check if we should enter "on but not occupied" state (40% chance)
            import random
            if random.random() < 0.4:  # 40% chance
                self.on_but_not_occupied = True
                self.animation_frame = 7  # Start at frame 7
            else:
                self.animation_frame = 0  # Reset to idle
        
        # Clean up treadmill state without calling parent (to avoid dirty state)
        if self.occupying_npc and hasattr(self.occupying_npc, '_complete_gym_interaction'):
            self.occupying_npc._complete_gym_interaction()
        
        self.occupied = False
        self.occupying_npc = None
        self.interaction_timer = 0
        self.remove_state("in_use")
    
    def update(self, delta_time):
        """Update treadmill logic including workout animation and effects"""
        # Handle interaction timing without calling parent (to avoid dirty state)
        if self.occupied:
            # Check if the occupying NPC is departing - if so, end interaction immediately
            if (self.occupying_npc and hasattr(self.occupying_npc, 'departure_pending') and 
                self.occupying_npc.departure_pending):
                self.end_interaction()
                return
            
            self.interaction_timer += delta_time
            if self.interaction_timer >= self.interaction_duration:
                self.end_interaction()
        
        # Update workout animation - simplified logic
        if self.occupied and "in_use" in self.states:
            # Update workout animation frames
            self.animation_timer += delta_time
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                # Cycle through workout frames 1-6
                if self.animation_frame >= 6:
                    self.animation_frame = 1  # Reset to frame 1
                else:
                    self.animation_frame += 1  # Move to next frame

        elif self.on_but_not_occupied:
            # Keep cycling through frames 7-10
            self.animation_timer += delta_time
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                if self.animation_frame >= 10:
                    self.animation_frame = 7  # Reset to frame 7
                else:
                    self.animation_frame += 1
        else:
            # Reset to idle when not in use
            self.animation_frame = 0
    
    def get_depth_y(self):
        """Get Y position for depth sorting"""
        return self.depth_y
    
    def turn_off(self):
        """Player turns off the treadmill"""
        if self.on_but_not_occupied:
            self.on_but_not_occupied = False
            self.animation_frame = 0  # Reset to idle
            return True
        return False
    
    def is_available(self):
        """Override to check if treadmill is available for interaction"""
        return not self.occupied and not self.on_but_not_occupied
    
    def _draw_state_indicators(self, screen, camera, screen_x, screen_y):
        """Override to show attention indicator"""
        # Call base class to draw attention indicator
        super()._draw_state_indicators(screen, camera, screen_x, screen_y)
    
    def get_treadmill_info(self):
        """Get treadmill information for debugging"""
        return {
            'states': list(self.states)
        }
    
    def toggle_animation(self):
        """Toggle treadmill animation (for compatibility with old system)"""
        if "in_use" in self.states:
            # Stop the workout
            self.remove_state("in_use")
            self.animation_frame = 0  # Reset to idle frame
            # End the interaction properly
            self.end_interaction()
        else:
            # Start a workout (create a dummy NPC for timing)
            self.add_state("in_use")
            self.animation_frame = 1  # Start from first workout frame
            # Start a proper interaction with timing
            self.occupied = True
            self.interaction_timer = 0
            self.interaction_duration = 8.0

    
    def get_cached_sprite(self, camera):
        """Get cached sprite for the current animation frame and camera zoom"""
        # Determine which frame to show based on states
        if "in_use" in self.states and self.occupied:
            display_frame = self.animation_frame  # Current animation frame (1-6)
        elif self.on_but_not_occupied:
            display_frame = self.animation_frame  # Current animation frame (7-10)
        else:
            display_frame = 0  # Idle sprite
        
        # Create a cache key that includes the display frame
        cache_key = (display_frame, self.scale, camera.zoom)
        
        if not hasattr(self, '_animation_cache'):
            self._animation_cache = {}
        
        if cache_key not in self._animation_cache:
            # Extract the current display frame from spritesheet
            frame_x = display_frame * self.sprite_width
            frame_surface = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
            frame_surface.blit(self.spritesheet, (0, 0), (frame_x, 0, self.sprite_width, self.sprite_height))
            
            # Scale to camera zoom
            scaled_width = self.sprite_width * camera.zoom
            scaled_height = self.sprite_height * camera.zoom
            self._animation_cache[cache_key] = pygame.transform.scale(frame_surface, (scaled_width, scaled_height))
        
        return self._animation_cache[cache_key]
