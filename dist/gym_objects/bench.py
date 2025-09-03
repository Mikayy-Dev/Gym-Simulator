import pygame
from gym_objects.base_object import GymObject

class Bench(GymObject):
    def __init__(self, x, y, bench_type="standard", scale=1.0):
        # Choose spritesheet based on bench type
        if bench_type == "small":
            spritesheet_path = "Graphics/stardew_style_bench_small.png"
        else:
            spritesheet_path = "Graphics/stardew_style_bench.png"
        
        # Call parent constructor first
        super().__init__(x, y, spritesheet_path, scale)
        
        # Now override the dimensions based on bench type
        if bench_type == "small":
            self.sprite_width = int(32 * scale)
            self.sprite_height = int(32 * scale)
        else:
            self.sprite_width = int(48 * scale)
            self.sprite_height = int(48 * scale)
        
        # Update rect and hitboxes with new dimensions
        self.rect = pygame.Rect(x, y, self.sprite_width, self.sprite_height)
        self.hitboxes = {
            "body": {"x": 0, "y": 0, "width": self.sprite_width, "height": self.sprite_height}
        }
        
        # Bench-specific properties
        self.bench_type = bench_type
        self.weight_capacity = 300 if bench_type == "standard" else 150
        self.current_weight = 0
        self.exercise_type = "bench_press"
        
        # Interaction properties
        self.interaction_duration = 8.0  # Longer workout time
        self.workout_intensity = 1.0
        
        # Visual effects
        self.weight_plates = []
        self.workout_particles = []
        
        # Animation properties
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.2  # Time between frames (seconds)
        self.animation_frames = [0, 1, 2, 3, 4]  # Frames 0-4 (0 is idle, 1-5 are workout frames)
        
        # Cleaning animation properties
        self.cleaning = False
        self.cleaning_frame = 7  # Start with frame 7
        self.cleaning_timer = 0
        self.cleaning_speed = 0.3  # Time between cleaning frames (seconds)
        self.cleaning_frames = [7, 8, 9]  # Cleaning animation frames
        
        # Set custom hitbox based on bench type
        if bench_type == "small":
            self.set_custom_hitbox(22, 22, -1, 0)  # 32x22 hitbox, offset 4,6
        else:
            self.set_custom_hitbox(32, 23, 0, 0)  # 48x23 hitbox, no offset
        
        # Set depth sorting Y position (use actual collision area bottom)
        collision_rect = self.get_collision_rect()
        self.depth_y = collision_rect.bottom  # Bottom of actual collision area
        
        # Benches can become dirty and need cleaning
        self.can_become_dirty = True
    
    def get_depth_y(self):
        """Get Y position for depth sorting"""
        return self.depth_y
    
    def add_weight(self, weight):
        """Add weight to the bench"""
        if self.current_weight + weight <= self.weight_capacity:
            self.current_weight += weight
            self.weight_plates.append(weight)
            return True
        return False
    
    def remove_weight(self, weight):
        """Remove weight from the bench"""
        if weight in self.weight_plates:
            self.weight_plates.remove(weight)
            self.current_weight -= weight
            return True
        return False
    
    def start_interaction(self, npc):
        """Start bench workout interaction"""
        if super().start_interaction(npc):
            # Set fixed 5-second workout duration for all NPCs
            self.interaction_duration = 5.0
            
            # Notify pathfinding system that this bench is now occupied
            self._notify_pathfinding_update()
            return True
        return False
    
    def update(self, delta_time):
        """Update bench logic including workout effects"""
        # Call base class update to handle interaction timing (5-second timeout)
        super().update(delta_time)
        
        # Update animation based on current state
        if self.cleaning:
            # Update cleaning animation
            self.cleaning_timer += delta_time
            if self.cleaning_timer >= self.cleaning_speed:
                self.cleaning_timer = 0
                # Cycle through cleaning frames 7-9
                current_index = self.cleaning_frames.index(self.cleaning_frame)
                next_index = (current_index + 1) % len(self.cleaning_frames)
                self.cleaning_frame = self.cleaning_frames[next_index]
                
                # Check if cleaning animation is complete
                if next_index == 0:  # Back to first cleaning frame
                    self.cleaning = False
                    self.remove_state("dirty")
        elif "in_use" in self.states and "dirty" not in self.states:
            # Only animate if in use AND not dirty
            self.animation_timer += delta_time
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                # Cycle through workout frames 1-4
                self.animation_frame = ((self.animation_frame) % 4) + 1
        else:
            # Reset to idle frame when not in use or when dirty
            self.animation_frame = 0
        
    def draw(self, screen, camera):
        """Draw bench with workout effects"""
        super().draw(screen, camera)
    
    def get_bench_info(self):
        """Get bench information for debugging"""
        return {
            'type': self.bench_type,
            'weight_capacity': self.weight_capacity,
            'current_weight': self.current_weight,
            'occupied': self.occupied,
            'workout_intensity': self.workout_intensity,
            'states': list(self.states)
        }
    
    # State management methods for compatibility
    def toggle_animation(self):
        """Toggle bench animation (for compatibility with old system)"""
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
            self.interaction_duration = 5.0

    
    def toggle_state(self, state):
        """Toggle a specific state (for compatibility with old system)"""
        if state in self.states:
            self.remove_state(state)
        else:
            self.add_state(state)
    
    def start_cleaning(self):
        """Start the cleaning animation"""
        if "dirty" in self.states and not self.cleaning:
            self.cleaning = True
            self.cleaning_frame = 7  # Start with first cleaning frame
            self.cleaning_timer = 0
    
    def is_animated(self):
        """Check if bench is animated (for compatibility with old system)"""
        return "in_use" in self.states
    
    def get_cached_sprite(self, camera):
        """Get cached sprite for the current animation frame and camera zoom"""
        # Determine which frame to show based on states
        if self.cleaning:
            display_frame = self.cleaning_frame  # Cleaning animation frames (7-9)
        elif "dirty" in self.states:
            display_frame = 6  # Dirty sprite
        elif "in_use" in self.states:
            display_frame = self.animation_frame  # Current animation frame (1-4)
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
