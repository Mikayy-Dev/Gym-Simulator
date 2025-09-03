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
        self.animation_speed = 0.1  # Slower animation for better visibility
        self.animation_frames = [1, 2, 3, 4, 5]  # Frames 1-6 for in-use animation
        self.current_animation_index = 0  # Index into animation_frames array
        self.frame_count = 0  # Track how many frames have been drawn
        
        # Squat racks don't become dirty (they don't need cleaning)
        self.can_become_dirty = False
           
        self.set_custom_hitbox(48, 12, 0, 4)
        
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
        
        collision_rect = self.get_collision_rect()
        self.depth_y = collision_rect.bottom
        
        print(f"SQUAT RACK: Created at ({self.x}, {self.y}) with {self.plate_count} plates (Frame {self.current_visual_frame})")
        
       
    
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
            self.interaction_duration = 5.0
            self._notify_pathfinding_update()
           
            return True
        
        return False
    
    def update(self, delta_time):
        
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
        
        # Cleaning animation is handled by the base object (frames 7-12)
    
    def end_interaction(self):
        """End interaction and handle plate dropping based on chance"""
        print(f"DEBUG: SquatRack.end_interaction() called - occupying_npc: {self.occupying_npc}")
        if self.occupying_npc:
            print(f"DEBUG: Ending interaction for NPC {self.occupying_npc.npc_id}")
            
            # 50% chance to drop plates, 50% chance to keep them on rack
            import random
            drop_chance = random.random()
            
            if drop_chance < 0.5:  # 50% chance to drop plates
                print(f"DEBUG: NPC {self.occupying_npc.npc_id} dropped plates (chance: {drop_chance:.2f})")
                # Trigger plate drop
                if hasattr(self, 'trigger_plate_drop'):
                    success, message = self.trigger_plate_drop(self.occupying_npc)
                    if success:
                        print(f"DEBUG: {message}")
            else:  # 50% chance to keep plates on rack
                print(f"DEBUG: NPC {self.occupying_npc.npc_id} kept plates on rack (chance: {drop_chance:.2f})")
        else:
            print(f"DEBUG: No occupying NPC found in end_interaction()")
        
        # Call the base object's end_interaction method
        super().end_interaction()
    
    def draw(self, screen, camera):
        # Determine which frame to draw
        if self.cleaning:
            frame = self.cleaning_frame
        elif self.occupied:
            frame = self.animation_frames[self.current_animation_index]  # Use frames 1-5 for in-use
            self.frame_count += 1
        else:
            frame = self.current_visual_frame  # Use visual frame for idle state
            # Debug: Print frame being drawn for idle state
            if hasattr(self, '_last_debug_frame') and self._last_debug_frame != frame:
                print(f"SQUAT RACK: Drawing frame {frame} (visual_frame: {self.current_visual_frame}, plate_count: {self.plate_count})")
                self._last_debug_frame = frame
            elif not hasattr(self, '_last_debug_frame'):
                self._last_debug_frame = frame
        
        # Check if we need to recreate the sprite (new frame, scale change, or zoom change)
        if (self._cached_sprite is None or 
            self._cached_scale != self.scale or 
            self._cached_zoom != camera.zoom or
            not hasattr(self, '_cached_frame') or 
            self._cached_frame != frame):
            
            self._cached_scale = self.scale
            self._cached_zoom = camera.zoom
            
            sprite_width = int(self.sprite_width * camera.zoom)
            sprite_height = int(self.sprite_height * camera.zoom)
            
            frame_width = int(64 * self.scale * camera.zoom)
            frame_height = int(64 * self.scale * camera.zoom)
            
            scaled_spritesheet = pygame.transform.scale(self.spritesheet, 
                (int(self.spritesheet.get_width() * self.scale * camera.zoom), 
                 int(self.spritesheet.get_height() * self.scale * camera.zoom)))
            
            self._cached_sprite = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            self._cached_sprite.blit(scaled_spritesheet, (0, 0), 
                (frame * frame_width, 0, frame_width, frame_height))
            
            # Store the frame that was cached
            self._cached_frame = frame
        
        screen_x, screen_y = camera.apply_pos(self.x, self.y)
        draw_x = screen_x - (self._cached_sprite.get_width() // 2)
        draw_y = screen_y - (self._cached_sprite.get_height() // 2)
        
        screen.blit(self._cached_sprite, (draw_x, draw_y))
        
        # Draw state indicators (including attention sprite) using base class method
        self._draw_state_indicators(screen, camera, screen_x, screen_y)
    
    def _notify_pathfinding_update(self):
        pass
    
    def _create_floor_plates(self, npc, plate_count):
        """Handle plate dropping (no visual floor graphics - just track for pickup)"""
        if npc:
            print(f"DEBUG: NPC {npc.npc_id} dropped {plate_count} plates")
        else:
            print(f"DEBUG: Player dropped {plate_count} plates")
        
        # Check if there are already plates on the floor from previous NPCs
        total_floor_plates = 0
        if 'floor_total' in self.plate_floor_sprites:
            total_floor_plates = self.plate_floor_sprites['floor_total']['count']
        
        # Add the new plates to the total
        new_total = total_floor_plates + plate_count
        print(f"DEBUG: Total plates on floor: {new_total}")
        
        # Store count for pickup (no visual sprites)
        self.plate_floor_sprites['floor_total'] = {
            'count': new_total
        }
        
        if npc:
            print(f"DEBUG: Created floor plates for NPC {npc.npc_id} - {plate_count} new + {total_floor_plates} existing = {new_total} total")
        else:
            print(f"DEBUG: Created floor plates for player - {plate_count} new + {total_floor_plates} existing = {new_total} total")
        
        # Update the squat rack's plate count and visual state
        self.plate_count -= plate_count
        self.update_visual_state()
    

    
    def trigger_plate_drop(self, npc=None):
        """Trigger plate dropping - only for NPCs"""
        if self.plate_count <= 0:
            return False, "No plates to drop"
        
        # Only allow NPCs to trigger plate drops
        if not npc:
            return False, "Only NPCs can drop plates"
        
        # 50% chance to drop 2 plates, 50% chance to drop all 4 plates
        import random
        drop_chance = random.random()
        
        if drop_chance < 0.5:  # 50% chance to drop 2 plates
            plate_count = min(2, self.plate_count)  # Don't drop more than available
            print(f"SQUAT RACK: Dropping {plate_count} plates (chance: {drop_chance:.2f} - 2 plates)")
        else:  # 50% chance to drop all 4 plates
            plate_count = min(4, self.plate_count)  # Don't drop more than available
            print(f"SQUAT RACK: Dropping {plate_count} plates (chance: {drop_chance:.2f} - 4 plates)")
        
        # Create floor plates and update visual state
        self._create_floor_plates(npc, plate_count)
        
        print(f"SQUAT RACK: Successfully dropped {plate_count} plates. Rack now has {self.plate_count} plates.")
        return True, f"Triggered drop of {plate_count} plates"
    
    def update_visual_state(self):
        """Update the visual state based on rack plate count and floor plates"""
        # Calculate the correct visual frame based on rack plate count and floor plates
        # Frame 0: Default state (4 plates on rack)
        # Frame 6: 2 plates dropped (2 plates on rack, 2 plates on floor)
        # Frame 7: 1 plate on rack (3 plates picked up from floor)
        # Frame 8: All 4 plates dropped (0 plates on rack, 4 plates on floor)
        # Frame 9: 2 plates on floor (2 plates picked up from frame 8)
        # Frame 10: All plates picked up (0 plates on floor)
        
        has_floor_plates = len(self.plate_floor_sprites) > 0
        
        if self.plate_count == 4:
            target_frame = 0  # Default state (full rack)
        elif has_floor_plates:
            if self.plate_count == 2:
                target_frame = 6  # 2 plates dropped (2 plates on rack, 2 on floor)
            elif self.plate_count == 0:
                # Check how many plates are on the floor to determine frame
                if 'floor_total' in self.plate_floor_sprites:
                    floor_plate_count = self.plate_floor_sprites['floor_total']['count']
                else:
                    floor_plate_count = 0
                    
                if floor_plate_count == 4:
                    target_frame = 8  # All 4 plates dropped (0 plates on rack, 4 on floor)
                elif floor_plate_count == 2:
                    target_frame = 9  # 2 plates on floor (2 plates picked up from frame 8)
                elif floor_plate_count == 0:
                    target_frame = 10  # All plates picked up (0 plates on floor)
                else:
                    target_frame = 8  # Default to frame 8
            elif self.plate_count == 1:
                target_frame = 7  # 1 plate on rack (3 plates picked up from floor)
            else:
                target_frame = 6  # Default to frame 6 for other cases
        else:
            # No floor plates - check if we have plates on the rack
            if self.plate_count == 0:
                target_frame = 10  # All plates picked up (0 plates on floor, 0 on rack)
            else:
                target_frame = 7  # Some plates on rack, none on floor
        
        # Only update if the frame needs to change
        if target_frame != self.current_visual_frame:
            old_frame = self.current_visual_frame
            self.current_visual_frame = target_frame
            # Force cache refresh for new frame
            self._cached_sprite = None
            self._cached_scale = None
            self._cached_zoom = None
            print(f"SQUAT RACK: Visual frame updated from {old_frame} to {target_frame} (rack: {self.plate_count})")
        else:
            print(f"SQUAT RACK: No visual frame change needed (already at {target_frame}, rack: {self.plate_count})")
    
    def is_available(self):
        """Override to check if rack is available for NPC use"""
        base_available = super().is_available()
        
        # Rack is only available if base available, has plates, AND is in frame 0 (full rack)
        result = base_available and self.plate_count > 0 and self.current_visual_frame == 0
        
        return result
    
    def is_mouse_over_floor_plates(self, mouse_x, mouse_y, camera):
        """Check if there are floor plates available for pickup"""
        # Only return True if the squat rack has plates on the floor (frames 6, 8, 9)
        return self.current_visual_frame in [6, 8, 9]
    
    def pickup_floor_plates(self, mouse_x, mouse_y, camera, player):
        """Pick up 2 plates at a time from the squat rack when right-clicked"""
        print(f"DEBUG: Attempting plate pickup at mouse position ({mouse_x}, {mouse_y})")
        print(f"DEBUG: Current floor sprites: {len(self.plate_floor_sprites)}")
        
        # Check if there are plates on the floor to pick up
        if 'floor_total' in self.plate_floor_sprites:
            floor_data = self.plate_floor_sprites['floor_total']
            current_count = floor_data['count']
            
            if current_count > 0:
                # Pick up 2 plates at a time
                plates_to_pickup = min(2, current_count)  # Pick up 2 plates or remaining amount
                print(f"DEBUG: Picking up {plates_to_pickup} plates from floor (was {current_count})")
                
                # Add plates to player inventory
                if hasattr(player, 'add_weight_plates'):
                    player.add_weight_plates(plates_to_pickup)
                else:
                    player.weight_plate_count += plates_to_pickup
                
                print(f"DEBUG: Player now has {player.weight_plate_count} plates")
                
                # Update floor plate count
                floor_data['count'] = current_count - plates_to_pickup
                
                # If no more plates on floor, remove the floor data
                if floor_data['count'] <= 0:
                    del self.plate_floor_sprites['floor_total']
                    print(f"DEBUG: Picked up all plates from floor")
                else:
                    print(f"DEBUG: {floor_data['count']} plates remaining on floor")
                
                # Update visual state (should progress through frames 8->9->10->7)
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
        
        print(f"DEBUG: Rack has {self.plate_count}/{self.max_plates} plates, available space: {available_space}")
        print(f"DEBUG: Player has {player_plates} plates")
        
        # Check if rack can accept more plates
        if available_space <= 0:
            return False, "Rack is full"
        
        # Return 2 plates at a time
        return_amount = min(available_space, player_plates, 2)
        print(f"DEBUG: Can return {return_amount} plates (2 at a time)")
        
        # Remove plates from player
        if hasattr(player, 'remove_weight_plates'):
            success = player.remove_weight_plates(return_amount)
            print(f"DEBUG: Player.remove_weight_plates({return_amount}) returned: {success}")
        else:
            old_count = player.weight_plate_count
            player.weight_plate_count -= return_amount
            print(f"DEBUG: Direct removal: {old_count} -> {player.weight_plate_count} (removed {return_amount})")
        
        # Add plates back to rack
        old_rack_count = self.plate_count
        self.plate_count += return_amount
        print(f"DEBUG: Rack count: {old_rack_count} -> {self.plate_count} (added {return_amount})")
        
        # Update visual state to show more plates
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
