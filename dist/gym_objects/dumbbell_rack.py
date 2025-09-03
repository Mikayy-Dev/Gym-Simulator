import pygame
from gym_objects.base_object import GymObject

class DumbbellRack(GymObject):
    def __init__(self, x, y, rack_type="standard", scale=1.0):
        spritesheet_path = "Graphics/stardew_style_dumbellrack.png"
        super().__init__(x, y, spritesheet_path, scale)
        
        # Get the actual spritesheet dimensions and force update
        actual_width = self.spritesheet.get_width()
        actual_height = self.spritesheet.get_height()
        
        # Force update the sprite dimensions to match the actual spritesheet
        self.sprite_width = actual_width
        self.sprite_height = actual_height
        

        
        # Clear cached sprite since dimensions changed
        self._cached_sprite = None
        self._cached_scale = None
        self._cached_zoom = None
        
        # Add a unique identifier to force cache refresh
        self._cache_version = 1
        
        # Update rect and hitboxes with correct dimensions
        self.rect = pygame.Rect(x, y, self.sprite_width, self.sprite_height)
        self.hitboxes = {
            "body": {"x": 0, "y": 0, "width": self.sprite_width, "height": self.sprite_height}
        }
        
        # Set custom hitbox for better interaction
        self.set_custom_hitbox(self.sprite_width, self.sprite_height, -7)
        
        #print(f"DumbbellRack: After setup - dimensions are {self.sprite_width}x{self.sprite_height}")
        
        self.rack_type = rack_type
        self.dumbbells_available = 6
        self.max_dumbbells = 6
        self.workout_intensity = 0
        self.last_workout_time = 0
        self.workout_cooldown = 5000
        
        # Add missing attributes for workout effects
        self.workout_particles = []
        self.dumbbell_glow = []
        self.available_weights = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
        self.racked_dumbbells = {weight: 4 for weight in self.available_weights}
        self.borrowed_dumbbells = {}
        self.interaction_duration = 6.0
        
        # Dumbbell floor system - shows dropped dumbbells under NPCs
        self.dumbbell_floor_sprites = {}
        self.floor_spritesheet = pygame.image.load("Graphics/dumbbell_floor.png")
        self.floor_sprite_width = 32  # Each frame is 32x32
        self.floor_sprite_height = 32
        

        
        # Add rack-specific states
        self.states.add("available")
        if self.dumbbells_available < self.max_dumbbells:
            self.states.add("low_supply")
        

        
        # Dumbbell rack visual progression system
        self.dumbbell_count = 6  # Start with 6 dumbbells (full rack)
        self.max_dumbbells = 6   # Maximum capacity
        # Each interaction will progress through frames: 0->1->2->3
        self.available_frames = [0, 1, 2, 3]  # Available visual frames
        self.current_visual_frame = 0  # Start with frame 0 (full rack)
        
        # Set depth sorting Y position (use actual collision area bottom)
        collision_rect = self.get_collision_rect()
        self.depth_y = collision_rect.bottom  # Bottom of actual collision area
        
        # Sync visual state with actual dumbbell count
        self.update_visual_state()
    
    def get_depth_y(self):
        """Get Y position for depth sorting"""
        return self.depth_y
    
    def get_sprite_dimensions(self):
        """Get the actual sprite dimensions for this rack"""
        return 32, 32  # Always return correct dimensions
    
    def set_position(self, x, y):
        """Override set_position to preserve our sprite dimensions"""
        self.x = x
        self.y = y
        # Use our corrected sprite dimensions, not the base class ones
        self.rect.x = x - (self.sprite_width // 2)
        self.rect.y = y - (self.sprite_height // 2)
    
    def borrow_dumbbells(self, npc, weights):
        """NPC borrows dumbbells from the rack"""
        print(f"DEBUG: NPC {npc.npc_id} attempting to borrow weights: {weights}")
        if npc not in self.borrowed_dumbbells:
            self.borrowed_dumbbells[npc] = []
        
        borrowed = []
        for weight in weights:
            if self.racked_dumbbells.get(weight, 0) > 0:
                self.racked_dumbbells[weight] -= 1
                self.borrowed_dumbbells[npc].append(weight)
                borrowed.append(weight)
                print(f"DEBUG: Successfully borrowed weight {weight}")
        
        print(f"DEBUG: Final borrowed list: {borrowed}")
        return borrowed
    
    def has_space_for_dumbbells(self, count):
        """Check if this rack has space for the specified number of dumbbells"""
        available_space = self.max_dumbbells - self.dumbbell_count
        return available_space >= count
    

    
    def find_closest_available_rack(self, npc, dumbbell_count):
        """Find the closest dumbbell rack that has space for the dumbbells"""
        if not hasattr(npc, 'collision_system') or not hasattr(npc.collision_system, 'gym_manager'):
            return None
        
        gym_manager = npc.collision_system.gym_manager
        if not gym_manager:
            return None
        
        # Get all dumbbell racks
        all_racks = []
        for pos, obj in gym_manager.get_collision_objects():
            if hasattr(obj, '__class__') and 'DumbbellRack' in obj.__class__.__name__:
                all_racks.append(obj)
        
        if not all_racks:
            return None
        
        # Find the closest rack with available space
        closest_rack = None
        min_distance = float('inf')
        
        for rack in all_racks:
            if rack.has_space_for_dumbbells(dumbbell_count):
                # Calculate distance from NPC to rack
                distance = ((npc.x - rack.x) ** 2 + (npc.y - rack.y) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    closest_rack = rack
        
        return closest_rack

    def return_dumbbells(self, npc):
        """NPC returns dumbbells to the rack, finding closest available rack if this one is full"""
        print(f"DEBUG: return_dumbbells() called for NPC {npc.npc_id if hasattr(npc, 'npc_id') else 'unknown'}")
        print(f"DEBUG: Current dumbbell_count before return: {self.dumbbell_count}")
        print(f"DEBUG: Borrowed dumbbells: {self.borrowed_dumbbells}")
        
        if npc in self.borrowed_dumbbells:
            returned_count = len(self.borrowed_dumbbells[npc])
            print(f"DEBUG: Returning {returned_count} dumbbells")
            
            # Check if this rack has space
            if self.has_space_for_dumbbells(returned_count):
                print(f"DEBUG: This rack has space, returning dumbbells here")
                # Return to this rack
                for weight in self.borrowed_dumbbells[npc]:
                    self.racked_dumbbells[weight] += 1
                del self.borrowed_dumbbells[npc]
                
                # Update visual dumbbell count to show dumbbells returned
                old_count = self.dumbbell_count
                self.dumbbell_count += returned_count
                print(f"DEBUG: Visual dumbbell count updated: {old_count} -> {self.dumbbell_count}")
            else:
                print(f"DEBUG: This rack is full, finding closest available rack")
                # Find closest available rack
                closest_rack = self.find_closest_available_rack(npc, returned_count)
                
                if closest_rack:
                    print(f"DEBUG: Found closest available rack at ({closest_rack.x}, {closest_rack.y})")
                    # Move dumbbells to the closest available rack
                    for weight in self.borrowed_dumbbells[npc]:
                        closest_rack.racked_dumbbells[weight] += 1
                    
                    # Update visual count on the closest rack
                    old_count = closest_rack.dumbbell_count
                    closest_rack.dumbbell_count += returned_count
                    closest_rack.update_visual_state()
                    print(f"DEBUG: Moved {returned_count} dumbbells to rack at ({closest_rack.x}, {closest_rack.y})")
                    print(f"DEBUG: Closest rack count updated: {old_count} -> {closest_rack.dumbbell_count}")
                    
                    # Clear borrowed dumbbells from this rack
                    del self.borrowed_dumbbells[npc]
                else:
                    print(f"DEBUG: No available racks found, dropping dumbbells on floor")
                    # No available racks, drop on floor instead
                    self._create_floor_dumbbells(npc)
        else:
            print(f"DEBUG: No borrowed dumbbells found for this NPC")
    
    def update_visual_state(self):
        """Update the visual state to match the actual dumbbell count"""
        print(f"DEBUG: [Rack at ({self.x}, {self.y})] update_visual_state() called - dumbbell_count: {self.dumbbell_count}, current_frame: {self.current_visual_frame}")
        
        # Calculate the correct visual frame based on actual dumbbell count
        # Only valid states: 6/6, 4/6, 2/6, 0/6
        if self.dumbbell_count == 0:
            target_frame = 3  # Empty (0/6)
        elif self.dumbbell_count == 2:
            target_frame = 2  # Almost empty (2/6)
        elif self.dumbbell_count == 4:
            target_frame = 1  # Half full (4/6)
        elif self.dumbbell_count == 6:
            target_frame = 0  # Full (6/6)
        else:
            # Invalid state - clamp to nearest valid state
            if self.dumbbell_count < 2:
                target_frame = 3  # Empty
            elif self.dumbbell_count < 4:
                target_frame = 2  # Almost empty
            elif self.dumbbell_count < 6:
                target_frame = 1  # Half full
            else:
                target_frame = 0  # Full
        
        print(f"DEBUG: [Rack at ({self.x}, {self.y})] Calculated target_frame: {target_frame}")
        
        # Only update if the frame needs to change
        if target_frame != self.current_visual_frame:
            old_frame = self.current_visual_frame
            self.current_visual_frame = target_frame
            print(f"DEBUG: [Rack at ({self.x}, {self.y})] Visual frame updated: {old_frame} -> {target_frame} (dumbbell_count: {self.dumbbell_count})")
            
            # Force cache refresh for new frame
            self._cached_sprite = None
            self._cached_scale = None
            self._cached_zoom = None
        else:
            print(f"DEBUG: [Rack at ({self.x}, {self.y})] No visual frame change needed (already at {target_frame})")
      
    
    def use_dumbbell(self):
        """NPC uses dumbbells from the rack (takes 2 at a time)"""
        print(f"DEBUG: [Rack at ({self.x}, {self.y})] use_dumbbell() called - current count: {self.dumbbell_count}, visual frame: {self.current_visual_frame}")
        
        if self.dumbbell_count >= 2:  # NPCs need 2 dumbbells
            old_count = self.dumbbell_count
            self.dumbbell_count -= 2  # Take 2 dumbbells
            print(f"DEBUG: [Rack at ({self.x}, {self.y})] Dumbbell count: {old_count} -> {self.dumbbell_count}")
           
            self.update_visual_state()
            
            print(f"DEBUG: [Rack at ({self.x}, {self.y})] After update_visual_state() - visual frame: {self.current_visual_frame}")
            return True
        else:
            print(f"DEBUG: [Rack at ({self.x}, {self.y})] Not enough dumbbells (need 2, have {self.dumbbell_count})")
            return False
    
    def is_available(self):
        """Override to check if rack has dumbbells available"""
        base_available = super().is_available()
        
        # Check if rack is empty based on visual frame (frame 3 = empty)
        rack_empty = self.current_visual_frame == 3
        
        # Rack is available if: base available, has dumbbells, and not visually empty
        result = base_available and self.dumbbell_count > 0 and not rack_empty
        
        return result
    
    def get_available_weights(self):
        """Get list of weights that are currently available"""
        return [weight for weight, count in self.racked_dumbbells.items() if count > 0]
    
    def start_interaction(self, npc):
        """Start dumbbell workout interaction"""
        
        # Don't clear floor dumbbells when starting interaction - let them accumulate
        # if hasattr(npc, 'npc_id'):
        #     self.remove_floor_dumbbells(npc.npc_id)
        
        if super().start_interaction(npc):
            # Use a dumbbell from the rack
            
            if not self.use_dumbbell():
                # No dumbbells available, end interaction
               
                super().end_interaction()
                return False
        
            # NPC borrows appropriate dumbbells
            if hasattr(npc, 'preferred_weight'):
                preferred = npc.preferred_weight
            else:
                preferred = 20  # Default weight
            
                         # Find closest available weight
                available = self.get_available_weights()
            if available:
                 closest_weight = min(available, key=lambda x: abs(x - preferred))
                 print(f"DEBUG: NPC {npc.npc_id} borrowing weight {closest_weight}")
                 # Each NPC uses 2 dumbbells per workout
                 self.borrow_dumbbells(npc, [closest_weight, closest_weight])
                 print(f"DEBUG: After borrowing, borrowed_dumbbells: {self.borrowed_dumbbells}")
        
            return True
        
        return False
    
    def end_interaction(self):
        """End interaction and handle dumbbell return/drop based on chance"""
        print(f"DEBUG: DumbbellRack.end_interaction() called - occupying_npc: {self.occupying_npc}")
        if self.occupying_npc:
            print(f"DEBUG: Ending interaction for NPC {self.occupying_npc.npc_id}")
            print(f"DEBUG: Borrowed dumbbells before handling: {self.borrowed_dumbbells}")
            
            # 40% chance to drop dumbbells on floor, 60% chance to return to rack
            import random
            drop_chance = random.random()
            
            if drop_chance < 0.4:  # 40% chance to drop
                print(f"DEBUG: NPC {self.occupying_npc.npc_id} dropped dumbbells on floor (chance: {drop_chance:.2f})")
                self._create_floor_dumbbells(self.occupying_npc)
                # Don't return to rack - they're on the floor
            else:  # 60% chance to return to rack
                print(f"DEBUG: NPC {self.occupying_npc.npc_id} returned dumbbells to rack (chance: {drop_chance:.2f})")
                self.return_dumbbells(self.occupying_npc)
                # Update visual state to show dumbbells returned
                self.update_visual_state()
                print(f"DEBUG: Visual state updated after returning dumbbells")
        else:
            print(f"DEBUG: No occupying NPC found in end_interaction()")
        super().end_interaction()
    
    def _create_floor_dumbbells(self, npc):
        """Create floor dumbbells under the NPC when they finish their workout"""
        if npc in self.borrowed_dumbbells:
            borrowed_count = len(self.borrowed_dumbbells[npc])
            if borrowed_count > 0:
                # Check if there are already dumbbells on the floor from previous NPCs
                total_floor_dumbbells = 0
                if 'floor_total' in self.dumbbell_floor_sprites:
                    total_floor_dumbbells = self.dumbbell_floor_sprites['floor_total']['count']
                
                print(f"DEBUG: Current floor total: {total_floor_dumbbells}, adding {borrowed_count} new dumbbells")
                print(f"DEBUG: Current floor sprites: {self.dumbbell_floor_sprites}")
                
                # Add the new dumbbells to the total
                new_total = total_floor_dumbbells + borrowed_count
                print(f"DEBUG: New total will be: {new_total}")
                
                # Map the total count to the appropriate floor sprite frame
                # Based on your sprite: frame 0 = 2 dumbbells, frame 1 = 4 dumbbells, frame 2 = 6 dumbbells
                if new_total <= 2:
                    floor_frame = 0  # 1-2 dumbbells → Frame 0 (shows 2 dumbbells)
                elif new_total <= 4:
                    floor_frame = 1  # 3-4 dumbbells → Frame 1 (shows 4 dumbbells)
                elif new_total >= 5:
                    floor_frame = 2  # 5+ dumbbells → Frame 2 (shows 6 dumbbells)
                else:
                    floor_frame = 0  # Default to frame 0
                
                # Clear all existing floor dumbbells and create one entry with the total
                self.dumbbell_floor_sprites.clear()
                
                # Store frame and count - we'll get scaled sprite during drawing
                self.dumbbell_floor_sprites['floor_total'] = {
                    'frame': floor_frame,
                    'x': self.x,  # Position at the RACK's location (centralized)
                    'y': self.y + 32,  # Position BELOW the rack (16 pixels down)
                    'count': new_total  # Store the total count
                }
                
                print(f"DEBUG: Created floor dumbbells for NPC {npc.npc_id} - {borrowed_count} new + {total_floor_dumbbells} existing = {new_total} total, floor frame {floor_frame}")
                print(f"DEBUG: After creation, floor sprites: {self.dumbbell_floor_sprites}")
                
                # Clear the borrowed dumbbells since they're now on the floor
                del self.borrowed_dumbbells[npc]
                

    
    def _get_floor_sprite(self, frame):
        """Get the floor dumbbell sprite for the specified frame"""
        # Extract frame from spritesheet
        frame_x = frame * self.floor_sprite_width
        frame_y = 0
        
        # Create surface and extract sprite
        sprite = pygame.Surface((self.floor_sprite_width, self.floor_sprite_height), pygame.SRCALPHA)
        sprite.blit(self.floor_spritesheet, (0, 0), (frame_x, frame_y, self.floor_sprite_width, self.floor_sprite_height))
        
        return sprite
    
    def _get_scaled_floor_sprite(self, frame, camera):
        """Get the floor dumbbell sprite scaled to match camera zoom"""
        base_sprite = self._get_floor_sprite(frame)
        
        # Scale the sprite to match camera zoom
        scaled_width = int(self.floor_sprite_width * camera.zoom)
        scaled_height = int(self.floor_sprite_height * camera.zoom)
        
        scaled_sprite = pygame.transform.scale(base_sprite, (scaled_width, scaled_height))
        return scaled_sprite
    
    def remove_floor_dumbbells(self, npc_id):
        """Remove floor dumbbells for a specific NPC"""
        if npc_id in self.dumbbell_floor_sprites:
            del self.dumbbell_floor_sprites[npc_id]
        elif 'floor_total' in self.dumbbell_floor_sprites:
            # If using the new accumulated system, clear the floor total
            del self.dumbbell_floor_sprites['floor_total']
    
    def is_mouse_over_floor_dumbbells(self, mouse_x, mouse_y, camera):
        """Check if mouse is hovering over any floor dumbbell sprites"""
        for npc_id, floor_data in self.dumbbell_floor_sprites.items():
            # Convert world coordinates to screen coordinates
            screen_x, screen_y = camera.apply_pos(floor_data['x'], floor_data['y'])
            
            # Get scaled sprite for this frame
            scaled_sprite = self._get_scaled_floor_sprite(floor_data['frame'], camera)
            
            # Calculate sprite bounds
            sprite_width = scaled_sprite.get_width()
            sprite_height = scaled_sprite.get_height()
            
            # Position sprite centered under NPC
            sprite_left = screen_x - (sprite_width // 2)
            sprite_top = screen_y - (sprite_height // 2)
            sprite_right = sprite_left + sprite_width
            sprite_bottom = sprite_top + sprite_height
            
            # Check if mouse is within sprite bounds
            if (sprite_left <= mouse_x <= sprite_right and 
                sprite_top <= mouse_y <= sprite_bottom):
                return True
        
        return False
    
    def pickup_floor_dumbbells(self, mouse_x, mouse_y, camera, player):
        """Pick up dumbbells from floor when right-clicked"""
        print(f"DEBUG: Attempting pickup at mouse position ({mouse_x}, {mouse_y})")
        print(f"DEBUG: Current floor sprites: {len(self.dumbbell_floor_sprites)}")
        for npc_id, floor_data in list(self.dumbbell_floor_sprites.items()):
            # Convert world coordinates to screen coordinates
            screen_x, screen_y = camera.apply_pos(floor_data['x'], floor_data['y'])
            
            # Get scaled sprite for this frame
            scaled_sprite = self._get_scaled_floor_sprite(floor_data['frame'], camera)
            
            # Calculate sprite bounds
            sprite_width = scaled_sprite.get_width()
            sprite_height = scaled_sprite.get_height()
            
            # Position sprite centered under NPC
            sprite_left = screen_x - (sprite_width // 2)
            sprite_top = screen_y - (sprite_height // 2)
            sprite_right = sprite_left + sprite_width
            sprite_bottom = sprite_top + sprite_height
            
            # Check if mouse is within sprite bounds
            if (sprite_left <= mouse_x <= sprite_right and 
                sprite_top <= mouse_y <= sprite_bottom):
                
                print(f"DEBUG: Mouse is over floor sprite for {npc_id}")
                
                # Calculate how many dumbbells to pick up (in 2s: 2, 4, 6, etc.)
                current_count = floor_data['count']
                
                # Pick up all remaining dumbbells (minimum 1, but prefer 2)
                if current_count >= 2:
                    pickup_amount = 2  # Pick up 2 if available
                else:
                    pickup_amount = current_count  # Pick up remaining 1 if that's all there is
                
                print(f"DEBUG: Picking up {pickup_amount} dumbbells from {current_count} available")
                
                # Add to player inventory - always add 2 to maintain 2s progression
                if hasattr(player, 'add_dumbbells'):
                    player.add_dumbbells(2)  # Always add 2 to player inventory
                
                # Update floor dumbbell count
                new_count = current_count - pickup_amount
                if new_count <= 0:
                    # Remove completely if no more dumbbells
                    del self.dumbbell_floor_sprites[npc_id]
                    print(f"DEBUG: Picked up all dumbbells from floor")
                else:
                    # Update count and potentially change frame
                    floor_data['count'] = new_count
                    
                                         # Update frame based on new count - match the creation logic
                     # Based on your sprite: frame 0 = 2 dumbbells, frame 1 = 4 dumbbells, frame 2 = 6 dumbbells
                    if new_count <= 2:
                        floor_data['frame'] = 0  # 1-2 dumbbells → Frame 0 (shows 2 dumbbells)
                    elif new_count <= 4:
                        floor_data['frame'] = 1  # 3-4 dumbbells → Frame 1 (shows 4 dumbbells)
                    elif new_count >= 5:
                        floor_data['frame'] = 2  # 5+ dumbbells → Frame 2 (shows 6 dumbbells)
                    else:
                        floor_data['frame'] = 0  # Default to frame 0
                    
                    print(f"DEBUG: Picked up {pickup_amount} dumbbells, {new_count} remaining on floor")
                
                return True  # Successfully picked up
        
        return False  # No dumbbells picked up
    
    def return_dumbbells_to_rack(self, player):
        """Player returns dumbbells to the rack"""
        if not hasattr(player, 'dumbbell_count') or player.dumbbell_count <= 0:
            return False, "No dumbbells to return"
        
        # Calculate how many dumbbells to return (prefer returning in pairs)
        available_space = self.max_dumbbells - self.dumbbell_count
        player_dumbbells = player.dumbbell_count
        
        print(f"DEBUG: Rack has {self.dumbbell_count}/{self.max_dumbbells} dumbbells, available space: {available_space}")
        print(f"DEBUG: Player has {player_dumbbells} dumbbells")
        
        # Check if rack can accept more dumbbells
        if available_space <= 0:
            return False, "Rack is full"
        
        # Calculate exact amount that can be returned to fill the rack
        print(f"DEBUG: Checking return logic - available_space: {available_space}, player_dumbbells: {player_dumbbells}")
        
        # Calculate how many dumbbells can be returned to fill the rack
        if available_space > 0:
            # Return the minimum of: available space, player's dumbbells, and 6 (max per return)
            return_amount = min(available_space, player_dumbbells, 6)
            print(f"DEBUG: Can return {return_amount} dumbbells (space: {available_space}, player: {player_dumbbells})")
        else:
            print(f"DEBUG: No space available in rack")
            return False, "Rack is full"
        
        print(f"DEBUG: Final return_amount calculated: {return_amount}")
        print(f"DEBUG: This should remove {return_amount} from player inventory")
        
        # Remove dumbbells from player
        print(f"DEBUG: Before removal - Player has {player.dumbbell_count} dumbbells, will remove {return_amount}")
        if hasattr(player, 'remove_dumbbells'):
            success = player.remove_dumbbells(return_amount)
            print(f"DEBUG: Player.remove_dumbbells({return_amount}) returned: {success}")
            print(f"DEBUG: After removal - Player now has {player.dumbbell_count} dumbbells")
        else:
            old_count = player.dumbbell_count
            player.dumbbell_count -= return_amount
            print(f"DEBUG: Direct removal: {old_count} -> {player.dumbbell_count} (removed {return_amount})")
        
        # Add dumbbells back to rack (exact amount that fits)
        old_rack_count = self.dumbbell_count
        self.dumbbell_count += return_amount
        print(f"DEBUG: Rack count: {old_rack_count} -> {self.dumbbell_count} (added {return_amount})")
        
        # Update visual state to show more dumbbells
        self._update_visual_state_for_return(return_amount)
        
        return True, f"Returned {return_amount} dumbbell(s) to rack"
    
    def _update_visual_state_for_return(self, return_amount):
        """Update visual state when dumbbells are returned"""
        # Calculate target frame based on new dumbbell count
        # Cap the dumbbell count at max_dumbbells for visual purposes
        visual_count = min(self.dumbbell_count, self.max_dumbbells)
        
        if visual_count <= 1:
            target_frame = 3  # Empty
        elif visual_count <= 2:
            target_frame = 2  # Almost empty
        elif visual_count <= 4:
            target_frame = 1  # Half full
        else:
            target_frame = 0  # Full
        
        # Always update to the correct frame when returning dumbbells
        if target_frame != self.current_visual_frame:
            self.current_visual_frame = target_frame
            # Force cache refresh for new frame
            self._cached_sprite = None
            self._cached_scale = None
            self._cache_version = getattr(self, '_cache_version', 0) + 1
    
    def update(self, delta_time):
        """Update rack logic including workout effects"""
        super().update(delta_time)
    
    def draw(self, screen, camera):
        """Draw rack with workout effects and dumbbell availability"""
        # Draw the main sprite
        screen_x, screen_y = camera.apply_pos(self.x, self.y)
        sprite = self.get_cached_sprite(camera)
        
        # Position sprite with proper centering
        draw_x = screen_x - (sprite.get_width() // 2)  # Center horizontally
        draw_y = screen_y - (sprite.get_height() // 2) # Center vertically
        
        # Try adjusting the position to find the right visual spot
        draw_x -= 24  # Adjust horizontal offset (try moving right)
        draw_y += 0  # Adjust vertical offset
        
        screen.blit(sprite, (draw_x, draw_y))
        
        # Draw state indicators (including attention sprite) using base class method
        self._draw_state_indicators(screen, camera, screen_x, screen_y)
        
        # Draw floor dumbbells under NPCs
        self._draw_floor_dumbbells(screen, camera)
    
    def _draw_floor_dumbbells(self, screen, camera):
        """Draw dumbbells on the floor under NPCs"""
        for npc_id, floor_data in self.dumbbell_floor_sprites.items():
            # Get scaled sprite for this frame
            scaled_sprite = self._get_scaled_floor_sprite(floor_data['frame'], camera)
            
            # Convert world coordinates to screen coordinates
            screen_x, screen_y = camera.apply_pos(floor_data['x'], floor_data['y'])
            
            # Position floor sprite centered under NPC
            draw_x = screen_x - (scaled_sprite.get_width() // 2)
            draw_y = screen_y - (scaled_sprite.get_height() // 2)
            
            # Draw the scaled floor dumbbell sprite
            screen.blit(scaled_sprite, (draw_x, draw_y))
        
    def _needs_attention(self):
        """Override to check if there are dumbbells on the floor and the rack is empty"""
        # Check if rack is empty (0 dumbbells)
        rack_empty = self.dumbbell_count == 0
        
        # Check if there are dumbbells on the floor
        has_floor_dumbbells = len(self.dumbbell_floor_sprites) > 0
        
        # Show attention if rack is empty AND there are dumbbells on the floor
        return rack_empty and has_floor_dumbbells
    
    def get_rack_info(self):
        """Get rack information for debugging"""
        return {
            'type': self.rack_type,
            'available_weights': self.get_available_weights(),
            'total_available': sum(self.racked_dumbbells.values()),
            'borrowed_dumbbells': {str(npc): weights for npc, weights in self.borrowed_dumbbells.items()},
            'occupied': self.occupied,
            'workout_intensity': self.workout_intensity,
            'states': list(self.states)
        }

    def get_cached_sprite(self, camera):
        """Override to ensure correct sprite extraction with visual state frames"""
        
        # Check if we need to update the cached sprite (new frame, zoom change, or cache version change)
        if (self._cached_sprite is None or 
            self._cached_scale != camera.zoom or 
            self._cache_version != getattr(self, '_cache_version', 0) or
            not hasattr(self, '_cached_frame') or 
            self._cached_frame != self.current_visual_frame):
            
            print(f"DEBUG: Updating cached sprite - frame: {self.current_visual_frame}, zoom: {camera.zoom}")
            
            # Get the correct dimensions
            width, height = self.get_sprite_dimensions()
            
            # Calculate frame position in spritesheet
            frame_x = self.current_visual_frame * width
            frame_y = 0
            
            print(f"DEBUG: Extracting sprite from spritesheet at frame_x: {frame_x}")
            
            # Extract the sprite from the spritesheet at the correct frame
            sprite = pygame.Surface((width, height), pygame.SRCALPHA)
            sprite.blit(self.spritesheet, (0, 0), (frame_x, frame_y, width, height))
            
            # Scale the sprite
            scaled_width = int(width * camera.zoom)
            scaled_height = int(height * camera.zoom)
            scaled_sprite = pygame.transform.scale(sprite, (scaled_width, scaled_height))
            
            # Cache the result
            self._cached_sprite = scaled_sprite
            self._cached_scale = camera.zoom
            self._cache_version = getattr(self, '_cache_version', 0)
            self._cached_frame = self.current_visual_frame
            
            print(f"DEBUG: Cached sprite updated for frame {self.current_visual_frame}")
        
        return self._cached_sprite
