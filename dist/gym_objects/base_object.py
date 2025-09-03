import pygame

class GymObject:
    def __init__(self, x, y, spritesheet_path, scale=1.0):
        self.x = x
        self.y = y
        self.spritesheet = pygame.image.load(spritesheet_path)
        self.scale = scale
        
        # Default dimensions (can be overridden by subclasses)
        self.sprite_width = int(32 * scale)  # Default to 32x32
        self.sprite_height = int(32 * scale)
        
        # Pre-render the sprite for performance
        self._cached_sprite = None
        self._cached_scale = None
        self._cached_zoom = None
        
        # Interaction properties
        self.interaction_zone = None
        self.occupied = False
        self.occupying_npc = None
        self.interaction_timer = 0
        self.interaction_duration = 5.0
        
        # Visual properties
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 8
        self.moving = False
        
        # State management
        self.states = set()  # empty, in_use, dirty, cluttered
        self.cleaning = False
        self.cleaning_frame = 7
        self.cleaning_timer = 0
        
        # Collision properties
        self.rect = pygame.Rect(x, y, self.sprite_width, self.sprite_height)
        self.hitboxes = {
            "body": {"x": 0, "y": 0, "width": self.sprite_width, "height": self.sprite_height}
        }
        
        # Custom hitbox support
        self.custom_hitbox = None
    
    def set_custom_hitbox(self, width, height, offset_x=0, offset_y=0):
        """Set custom hitbox for the object"""
        self.custom_hitbox = {
            "width": width,
            "height": height,
            "offset_x": offset_x,
            "offset_y": offset_y
        }
    
    def get_collision_rect(self):
        """Get the collision rectangle for this object"""
        if self.custom_hitbox:
            return pygame.Rect(
                self.x - (self.custom_hitbox["width"] // 2) + self.custom_hitbox["offset_x"],
                self.y - (self.custom_hitbox["height"] // 2) + self.custom_hitbox["offset_y"],
                self.custom_hitbox["width"],
                self.custom_hitbox["height"]
            )
        # Position hitbox exactly like the sprite is drawn (centered on object position)
        return pygame.Rect(
            self.x - (self.sprite_width // 2),
            self.y - (self.sprite_height // 2),
            self.sprite_width,
            self.sprite_height
        )
    
    def add_state(self, state):
        """Add a state to the object"""
        self.states.add(state)
    
    def remove_state(self, state):
        """Remove a state from the object"""
        self.states.discard(state)
    
    def has_state(self, state):
        """Check if object has a specific state"""
        return state in self.states
    
    def get_states(self):
        """Get all current states"""
        return self.states.copy()
    
    def start_cleaning(self):
        """Start cleaning animation"""
        if "dirty" in self.states:
            self.cleaning = True
            self.cleaning_frame = 7
            self.cleaning_timer = 0
    
    def is_available(self):
        """Check if the object is available for interaction"""
        return not self.occupied and "dirty" not in self.states
    
    def start_interaction(self, npc):
        """Start interaction with an NPC"""
        if not self.is_available():
            return False
        
        self.occupied = True
        self.occupying_npc = npc
        self.interaction_timer = 0
        self.add_state("in_use")
        return True
    
    def end_interaction(self):
        """End current interaction"""

        
        # Notify the NPC that the interaction is complete
        if self.occupying_npc and hasattr(self.occupying_npc, '_complete_gym_interaction'):
            self.occupying_npc._complete_gym_interaction()
        
        self.occupied = False
        self.occupying_npc = None
        self.interaction_timer = 0
        self.remove_state("in_use")
        
        # Notify pathfinding system that this object is now free
        self._notify_pathfinding_update()
    
    def update(self, delta_time):
        """Update object logic"""
        if self.occupied:
            self.interaction_timer += delta_time
            if self.interaction_timer >= self.interaction_duration:
                print(f"DEBUG: Base object interaction timer expired, calling end_interaction()")
                self.end_interaction()
                # Transition to dirty state after use (100% chance for testing)
                # But only for objects that actually need cleaning (benches)
                import random
                if random.random() < 1.0:  # Always dirty
                    # Only add dirty state for objects that can be cleaned
                    if hasattr(self, 'can_become_dirty') and self.can_become_dirty:
                        self.add_state("dirty")
        
        # Update cleaning animation
        if self.cleaning:
            self.cleaning_timer += delta_time
            if self.cleaning_timer >= 0.2:  # Animation speed
                self.cleaning_timer = 0
                self.cleaning_frame += 1
                
                # Check if cleaning is complete
                if self.cleaning_frame >= 12:
                    self.cleaning = False
                    self.remove_state("dirty")
                    self.cleaning_frame = 7
    
    def draw(self, screen, camera):
        """Draw the object on screen"""
        try:
            screen_x, screen_y = camera.apply_pos(self.x, self.y)
            
            # Get cached sprite (much faster than recreating every frame)
            sprite = self.get_cached_sprite(camera)
            
            # Draw on screen
            draw_x = screen_x - (sprite.get_width() // 2)
            draw_y = screen_y - (sprite.get_height() // 2)
            screen.blit(sprite, (draw_x, draw_y))
            
            # Draw state indicators
            self._draw_state_indicators(screen, camera, screen_x, screen_y)
            
        except Exception as e:
            # Draw a simple colored rectangle if drawing fails
            screen_x, screen_y = camera.apply_pos(self.x, self.y)
            scaled_width = self.sprite_width * camera.zoom
            scaled_height = self.sprite_height * camera.zoom
            draw_x = screen_x - (scaled_width // 2)
            draw_y = screen_y - (scaled_height // 2)
            
            # Draw a red rectangle as fallback
            fallback_surface = pygame.Surface((scaled_width, scaled_height))
            fallback_surface.fill((255, 0, 0))
            screen.blit(fallback_surface, (draw_x, draw_y))

    
    def get_position(self):
        """Get current position"""
        return (self.x, self.y)
    
    def set_position(self, x, y):
        """Set position and update rect"""
        self.x = x
        self.y = y
        self.rect.x = x - (self.sprite_width // 2)
        self.rect.y = y - (self.sprite_height // 2)
    
    def toggle_animation(self):
        """Toggle animation state (for compatibility with old system)"""
        if "in_use" in self.states:
            self.remove_state("in_use")
        else:
            self.add_state("in_use")
    
    def toggle_state(self, state):
        """Toggle a specific state (for compatibility with old system)"""
        if state in self.states:
            self.remove_state(state)
        else:
            self.add_state(state)
    

    def get_cached_sprite(self, camera):
        """Get cached sprite for the current camera zoom level"""
        if (self._cached_sprite is None or 
            self._cached_scale != self.scale or 
            self._cached_zoom != camera.zoom):
            
            # Extract first frame from spritesheet
            frame_surface = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
            frame_surface.blit(self.spritesheet, (0, 0), (0, 0, self.sprite_width, self.sprite_height))
            
            # Scale to camera zoom
            scaled_width = self.sprite_width * camera.zoom
            scaled_height = self.sprite_height * camera.zoom
            self._cached_sprite = pygame.transform.scale(frame_surface, (scaled_width, scaled_height))
            self._cached_scale = self.scale
            self._cached_zoom = camera.zoom
        
        return self._cached_sprite
    
    def _notify_pathfinding_update(self):
        """Notify the pathfinding system that this object's occupancy has changed"""
        # This method will be called by NPCs to update their pathfinding
        pass
    
    def _draw_state_indicators(self, screen, camera, screen_x, screen_y):
        """Draw visual indicators for different states"""
        # Draw attention indicator above objects that need attention
        if self._needs_attention():
            self._draw_attention_indicator(screen, camera, screen_x, screen_y)
        
    
    def _needs_attention(self):
        """Check if this object needs attention (dirty or on but not occupied)"""
        return "dirty" in self.states or (hasattr(self, 'on_but_not_occupied') and self.on_but_not_occupied)
    
    def _draw_attention_indicator(self, screen, camera, screen_x, screen_y):
        """Draw the animated attention.png image as a waypoint indicator"""
        try:
            # Load and cache the attention spritesheet
            if not hasattr(self, '_attention_spritesheet'):
                self._attention_spritesheet = pygame.image.load("Graphics/attention.png")
                self._attention_frame_width = self._attention_spritesheet.get_width() // 4  # 4 frames
                self._attention_frame_height = self._attention_spritesheet.get_height()
                self._attention_animation_timer = 0
                self._attention_animation_speed = 0.2  # Time between frames (seconds)
                self._attention_current_frame = 0
            
            # Update animation timer
            if not hasattr(self, '_last_update_time'):
                self._last_update_time = 0
            
            current_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
            if current_time - self._last_update_time >= self._attention_animation_speed:
                self._attention_current_frame = (self._attention_current_frame + 1) % 4
                self._last_update_time = current_time
            
            # Calculate frame position in spritesheet
            frame_x = self._attention_current_frame * self._attention_frame_width
            
            # Extract current frame
            frame_surface = pygame.Surface((self._attention_frame_width, self._attention_frame_height), pygame.SRCALPHA)
            frame_surface.blit(self._attention_spritesheet, (0, 0), (frame_x, 0, self._attention_frame_width, self._attention_frame_height))
            
            # Get screen dimensions
            screen_width = screen.get_width()
            screen_height = screen.get_height()
            
            # Check if object is off-screen
            margin = 50  # Margin from screen edge
            is_off_screen = (screen_x < -margin or screen_x > screen_width + margin or 
                           screen_y < -margin or screen_y > screen_height + margin)
            
            if is_off_screen:
                # Draw waypoint indicator on screen edge
                self._draw_waypoint_indicator(screen, screen_x, screen_y, screen_width, screen_height, frame_surface)
            else:
                # Draw normal attention indicator above the object
                scaled_width = int(self._attention_frame_width * camera.zoom)
                scaled_height = int(self._attention_frame_height * camera.zoom)
                
                # Position the attention image above the object
                attention_x = screen_x - (scaled_width // 2)
                attention_y = screen_y - (self.sprite_height * camera.zoom // 2) - scaled_height - 10
                
                # Scale the frame if needed
                if camera.zoom != 1.0:
                    scaled_frame = pygame.transform.scale(frame_surface, (scaled_width, scaled_height))
                    screen.blit(scaled_frame, (attention_x, attention_y))
                else:
                    screen.blit(frame_surface, (attention_x, attention_y))
                
        except Exception as e:
            # Fallback: draw a red triangle if image loading fails
            triangle_points = [
                (int(screen_x), int(screen_y - self.sprite_height * camera.zoom // 2 - 20)),
                (int(screen_x - 10), int(screen_y - self.sprite_height * camera.zoom // 2 - 40)),
                (int(screen_x + 10), int(screen_y - self.sprite_height * camera.zoom // 2 - 40))
            ]
            pygame.draw.polygon(screen, (255, 0, 0), triangle_points)
    
    def _draw_waypoint_indicator(self, screen, screen_x, screen_y, screen_width, screen_height, frame_surface):
        """Draw waypoint indicator on screen edge pointing toward off-screen object"""
        # Calculate direction from screen center to object
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        # Calculate angle to object
        dx = screen_x - center_x
        dy = screen_y - center_y
        
        # Simple edge detection and positioning
        waypoint_x = center_x
        waypoint_y = center_y
        
        # Check which edge the object is closest to
        if screen_x < 0:  # Object is to the left
            waypoint_x = 30
            waypoint_y = center_y + (dy * 0.5)  # Scale down the vertical offset
        elif screen_x > screen_width:  # Object is to the right
            waypoint_x = screen_width - 30
            waypoint_y = center_y + (dy * 0.5)  # Scale down the vertical offset
        elif screen_y < 0:  # Object is above
            waypoint_x = center_x + (dx * 0.5)  # Scale down the horizontal offset
            waypoint_y = 30
        elif screen_y > screen_height:  # Object is below
            waypoint_x = center_x + (dx * 0.5)  # Scale down the horizontal offset
            waypoint_y = screen_height - 30
        
        # Clamp waypoint to screen bounds with margin
        margin = 30
        waypoint_x = max(margin, min(screen_width - margin, waypoint_x))
        waypoint_y = max(margin, min(screen_height - margin, waypoint_y))
        
        # Scale the attention sprite for waypoint (smaller)
        waypoint_size = 24
        scaled_frame = pygame.transform.scale(frame_surface, (waypoint_size, waypoint_size))
        
        # Draw the waypoint indicator
        waypoint_rect = scaled_frame.get_rect(center=(waypoint_x, waypoint_y))
        screen.blit(scaled_frame, waypoint_rect)
