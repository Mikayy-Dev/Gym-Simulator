import pygame
from gym_objects.base_object import GymObject

class SquatRack(GymObject):
    def __init__(self, x, y, scale=1.0):
        spritesheet_path = "Graphics/squat_rack.png"
        
        super().__init__(x, y, spritesheet_path, scale)
        
        self.sprite_width = int(64 * scale)
        self.sprite_height = int(64 * scale)
        
        self.rect = pygame.Rect(x, y, self.sprite_width, self.sprite_height)
        self.hitboxes = {
            "body": {"x": 0, "y": 0, "width": self.sprite_width, "height": self.sprite_height}
        }
        
        self.interaction_duration = 10
    
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1  # Animation speed for squat rack
        self.animation_frames = [1, 2, 3, 4, 5]  # Frames 1-5 for in-use animation
        self.current_animation_index = 0  # Index into animation_frames array
        self.frame_count = 0  # Track how many frames have been drawn
        
        # Squat racks don't become dirty (they don't need cleaning)
        self.can_become_dirty = False
           
        self.set_custom_hitbox(48, 12, 0, 4)
        
        # Set interaction hitbox for player clicks (full sprite dimensions for easier clicking)
        self.set_interaction_hitbox(self.sprite_width, self.sprite_height, offset_x=0, offset_y=0)
        
        # Weight system properties
        self.weight_capacity = 500  # Default weight capacity
        self.current_weight = 0
        self.weight_plates = []
        
        # Plate dropping system (no floor graphics - direct pickup like dumbbells)
        self.plate_floor_sprites = {}
        
        # Visual state system for squat rack
        self.current_visual_frame = 0  # Start with frame 0 (full rack)
        self.max_plates = 4  # Maximum plates on rack
        self.plate_count = 4  # Start with 4 plates (full rack)
        
        # Caching for animation
        self._cached_frame = None
        
        collision_rect = self.get_collision_rect()
        self.depth_y = collision_rect.bottom
        
        
       
    
    def get_depth_y(self):
        return self.depth_y
    
    def add_weight(self, weight):
        if self.current_weight + weight <= self.weight_capacity:
            self.current_weight += weight
            self.weight_plates.append(weight)
            return True
        return False
    
    def remove_weight(self, weight):
        if weight in self.weight_plates:
            self.weight_plates.remove(weight)
            self.current_weight -= weight
            return True
        return False
    
    def start_interaction(self, npc):
        if super().start_interaction(npc):
            #print(f"DEBUG: Squat rack interaction started with NPC {npc.npc_id}")
            self.interaction_duration = 5.0
            self._notify_pathfinding_update()
           
            return True
    
        return False
    
    def update(self, delta_time):
        """Update squat rack logic and animation"""
        # Check if the occupying NPC is departing - if so, end interaction immediately
        if (self.occupied and self.occupying_npc and 
            hasattr(self.occupying_npc, 'departure_pending') and 
            self.occupying_npc.departure_pending):
            self.end_interaction()
            return
        
        super().update(delta_time)
        
        # Update squat rack animation when occupied
        if self.occupied:
            self.animation_timer += delta_time
            
            
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_animation_index = (self.current_animation_index + 1) % len(self.animation_frames)
                current_frame = self.animation_frames[self.current_animation_index]
               
        else:
            # Reset animation when not occupied
            if self.current_animation_index != 0:
                self.current_animation_index = 0
                self.animation_timer = 0
        
        # Cleaning animation is handled by the base object (frames 7-12)
    
    def end_interaction(self):
        """End interaction and handle plate dropping based on chance"""
        if self.occupying_npc:
            
            # Clear the squat rack flag
            if hasattr(self.occupying_npc, 'using_squat_rack'):
                self.occupying_npc.using_squat_rack = False
            
            # Always drop plates when NPC finishes workout
            # 50% chance to drop 2 plates (frame 6), 50% chance to drop 4 plates (frame 8)
            import random
            drop_chance = random.random()
            
            if drop_chance < 0.5:  # 50% chance to drop 2 plates
                plate_count = min(2, self.plate_count)
            else:  # 50% chance to drop 4 plates
                plate_count = min(4, self.plate_count)
            
            # Create floor plates and update visual state
            self._create_floor_plates(self.occupying_npc, plate_count)
        else:
            pass
        
        # Call the base object's end_interaction method
        super().end_interaction()
        
    
    def draw(self, screen, camera):
        """Draw squat rack with animation support"""
        try:
            # Determine which frame to draw
            if self.occupied:
                # Use animation frame when occupied
                frame = self.animation_frames[self.current_animation_index]
            else:
                # Use visual frame when not occupied (for plate states)
                frame = self.current_visual_frame
            
            # Check if we need to update the cached sprite
            if (self._cached_sprite is None or 
                self._cached_scale != self.scale or 
                self._cached_zoom != camera.zoom or
                self._cached_frame != frame):
                
                self._cached_scale = self.scale
                self._cached_zoom = camera.zoom
                self._cached_frame = frame
                
                # Calculate scaled dimensions
                sprite_width = int(self.sprite_width * camera.zoom)
                sprite_height = int(self.sprite_height * camera.zoom)
                
                # Scale the spritesheet
                scaled_spritesheet = pygame.transform.scale(self.spritesheet, 
                    (int(self.spritesheet.get_width() * self.scale * camera.zoom), 
                     int(self.spritesheet.get_height() * self.scale * camera.zoom)))
                
                # Extract the frame
                frame_width = sprite_width
                frame_height = sprite_height
                
                # Calculate frame position in the spritesheet
                frame_x = frame * frame_width
                frame_y = 0
                
                # Check if frame is within spritesheet bounds
                if frame_x + frame_width <= scaled_spritesheet.get_width():
                    self._cached_sprite = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    self._cached_sprite.blit(scaled_spritesheet, (0, 0), 
                        (frame_x, frame_y, frame_width, frame_height))
                else:
                    # Fallback to frame 0 if requested frame doesn't exist
                    self._cached_sprite = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    self._cached_sprite.blit(scaled_spritesheet, (0, 0), 
                        (0, 0, frame_width, frame_height))
            
            # Calculate screen position
            screen_x, screen_y = camera.apply_pos(self.x, self.y)
            
            # Center the sprite
            draw_x = screen_x - (self._cached_sprite.get_width() // 2)
            draw_y = screen_y - (self._cached_sprite.get_height() // 2)
            
            # Draw the sprite
            screen.blit(self._cached_sprite, (draw_x, draw_y))
            
            # Draw state indicators
            self._draw_state_indicators(screen, camera, screen_x, screen_y)
            
        except Exception as e:
            # Fallback to base class drawing
            super().draw(screen, camera)
    
    def _notify_pathfinding_update(self):
        pass
    
    def _create_floor_plates(self, npc, plate_count):
        """Handle plate dropping (no visual floor graphics - just track for pickup)"""
        # Check if there are already plates on the floor from previous NPCs
        total_floor_plates = 0
        if 'floor_total' in self.plate_floor_sprites:
            total_floor_plates = self.plate_floor_sprites['floor_total']['count']
        
        # Add the new plates to the total
        new_total = total_floor_plates + plate_count
        
        # Store count for pickup (no visual sprites)
        self.plate_floor_sprites['floor_total'] = {
            'count': new_total
        }
        if npc:
            pass
        else:
            pass
        
        # Update the squat rack's plate count and visual state
        self.plate_count -= plate_count
        self.update_visual_state()
    

    
    
    def update_visual_state(self):
        """Update the visual state based on rack plate count and floor plates"""
        # Only update visual state if we're not in the middle of a manual frame progression
        # Manual frame progression is handled in pickup_floor_plates and return_plates_to_rack
        
        # Check if there are floor plates
        floor_plate_count = 0
        if 'floor_total' in self.plate_floor_sprites:
            floor_plate_count = self.plate_floor_sprites['floor_total']['count']
        
        has_floor_plates = floor_plate_count > 0
        
        # Only auto-calculate frame if we're in a state that needs it
        # (e.g., when NPC drops plates or when returning to default state)
        if self.current_visual_frame == 0 and self.plate_count == 4:
            # Already in correct default state
            return
        elif self.current_visual_frame in [1, 2, 3, 4, 5]:
            # In animation state - don't change
            return
        elif self.current_visual_frame in [6, 7, 8, 9, 10]:
            # In manual progression state - don't auto-calculate
            # Just ensure cache is invalidated for visual updates
            self._cached_sprite = None
            self._cached_scale = None
            self._cached_zoom = None
            self._cached_frame = None
            return
        
        # Only auto-calculate for initial plate drops from NPCs
        if self.plate_count == 2 and has_floor_plates and floor_plate_count == 2:
            target_frame = 6  # NPC dropped 1 group (2 plates on rack, 2 on floor)
        elif self.plate_count == 0 and has_floor_plates and floor_plate_count == 4:
            target_frame = 8  # NPC dropped 2 groups (0 plates on rack, 4 on floor)
        elif self.plate_count == 4 and not has_floor_plates:
            target_frame = 0  # Default state (full rack)
        else:
            # Don't change frame if we don't recognize the state
            return
        
        # Only update if the frame needs to change
        if target_frame != self.current_visual_frame:
            self.current_visual_frame = target_frame
            # Force cache refresh for new frame
            self._cached_sprite = None
            self._cached_scale = None
            self._cached_zoom = None
            self._cached_frame = None
        
    
    def is_available(self):
        """Override to check if rack is available for NPC use"""
        base_available = super().is_available()
        
        # Rack is only available if base available, has plates, AND is in frame 0 (full rack)
        result = base_available and self.plate_count > 0 and self.current_visual_frame == 0
        
        return result
    
    def is_mouse_over_floor_plates(self, mouse_x, mouse_y, camera):
        """Check if there are floor plates available for pickup"""
        # Only return True if the squat rack has plates on the floor (frames 6, 7, 8, 9, 10)
        return self.current_visual_frame in [6, 7, 8, 9, 10]
    
    def pickup_floor_plates(self, mouse_x, mouse_y, camera, player, tilemap=None):
        """Pick up 2 plates at a time from the squat rack when right-clicked"""
        
        # Check if player is within range (if tilemap is provided)
        if tilemap:
            world_x, world_y = camera.reverse_apply_pos(mouse_x, mouse_y)
            tile_x = int(world_x // 16)
            tile_y = int(world_y // 16)
            
            if not tilemap.is_within_player_range(tile_x, tile_y):
                return False  # Player not in range
        
        # Check if there are plates on the floor to pick up
        if 'floor_total' in self.plate_floor_sprites:
            floor_data = self.plate_floor_sprites['floor_total']
            current_count = floor_data['count']
            
            if current_count > 0:
                # Pick up 2 plates at a time
                plates_to_pickup = min(2, current_count)  # Pick up 2 plates or remaining amount
                
                # Add plates to player inventory
                if hasattr(player, 'add_weight_plates'):
                    player.add_weight_plates(plates_to_pickup)
                else:
                    player.weight_plate_count += plates_to_pickup
                
                
                # Update floor plate count
                floor_data['count'] = current_count - plates_to_pickup
                
                # Manual frame progression for pickup:
                # Frame 6 → Frame 7 (when picking up 2 weights from frame 6)
                # Frame 8 → Frame 9 (when picking up 2 weights from frame 8)
                # Frame 9 → Frame 10 (when picking up remaining weights from frame 9)
                if self.current_visual_frame == 6:
                    # Picking up from frame 6: 6 → 7 (2 weights picked up, 2 remain on floor)
                    self.current_visual_frame = 7
                elif self.current_visual_frame == 8:
                    # Picking up from frame 8: 8 → 9 (2 weights picked up, 2 remain on floor)
                    self.current_visual_frame = 9
                elif self.current_visual_frame == 9:
                    # Picking up from frame 9: 9 → 10 (remaining 2 weights picked up)
                    self.current_visual_frame = 10
                
                # If no more plates on floor, remove the floor data
                if floor_data['count'] <= 0:
                    del self.plate_floor_sprites['floor_total']
                
                # Update visual state (after manual frame progression)
                self.update_visual_state()
                
                return True  # Successfully picked up
        
        return False  # No plates picked up
    
    def return_plates_to_rack(self, player):
        """Player returns plates to the rack"""
        if not hasattr(player, 'weight_plate_count') or player.weight_plate_count <= 0:
            return False, "No weight plates to return"
        
        # Calculate how many plates to return
        available_space = self.max_plates - self.plate_count
        player_plates = player.weight_plate_count
        
        # Check if rack can accept more plates
        if available_space <= 0:
            return False, "Rack is full"
        
        # Return exactly 2 plates at a time (or remaining if less than 2)
        return_amount = min(available_space, player_plates, 2)
        
        # Remove plates from player
        if hasattr(player, 'remove_weight_plates'):
            success = player.remove_weight_plates(return_amount)
        else:
            player.weight_plate_count -= return_amount
        
        # Add plates back to rack
        self.plate_count += return_amount
        
        # Frame progression when returning plates:
        # Frame 10 → Frame 7 (when returning 2 weights)
        # Frame 7 → Frame 0 (when returning 2 more weights)
        if self.current_visual_frame == 10:
            # First return: 10 → 7 (2 weights returned)
            self.current_visual_frame = 7
        elif self.current_visual_frame == 7:
            # Second return: 7 → 0 (2 more weights returned)
            self.current_visual_frame = 0
        
        # Update visual state to show more plates (after manual frame progression)
        self.update_visual_state()
        
        return True, f"Returned {return_amount} weight plate(s) to rack"
    

    
    def _needs_attention(self):
        """Override to check if rack needs attention"""
        # Show attention if rack is not full (has less than 4 plates)
        return self.plate_count < self.max_plates

    def get_squat_rack_info(self):
        return {
            'type': 'squat_rack',
            'position': (self.x, self.y),
            'occupied': self.occupied,
            'states': list(self.states),
            'current_weight': self.current_weight,
            'weight_capacity': self.weight_capacity,
            'weight_plates': self.weight_plates.copy(),
            'plate_count': self.plate_count,
            'max_plates': self.max_plates,
            'current_visual_frame': self.current_visual_frame
        }
