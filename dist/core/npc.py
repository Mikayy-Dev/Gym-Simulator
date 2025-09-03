import pygame
from .collision import CollisionSystem
from .ai import GymPathfinder
from .entity import Entity
import math

class NPC(Entity):
    def __init__(self, x, y, spritesheet_path="Graphics/player_temp.png", scale=1.0, npc_id=None):
        # Initialize base Entity class
        super().__init__(x, y, spritesheet_path, scale, npc_id)
        
        # NPC-specific properties
        self.npc_id = npc_id
        self.name = f"NPC_{npc_id}" if npc_id else "NPC"
        
        # Pathfinding system
        self.pathfinder = None
        self.current_path = []
        self.path_index = 0
        self.target_object = None
        self.ai_state = "idle"  # idle, moving, interacting
        
        # AI behavior
        self.behavior_timer = 0
        self.behavior_interval = 2  # 5 seconds
        
        # Debug options
        self.show_paths = False
        
        # Interaction system
        self.hidden = False
        self.interaction_timer = 0
        self.interaction_duration = 5.0  # 5 seconds
        
        # Gym object targeting restrictions
        self.last_gym_object_type = None  # Track last gym object type used
        self.gym_object_type_restriction = True  # Enable/disable the restriction
        
        # Workout animation properties
        self.workout_sprite = None
        self.workout_animation_timer = 0
        self.workout_animation_speed = 0.2  # Time between frames
        self.workout_animation_index = 0
        self.workout_frames = 8  # 8 frames for dumbbell workout
        self.is_working_out = False
        self.workout_type = None  # "dumbbell", "bench", etc.
    
    def is_gym_object_type_allowed(self, tile_id):
        """Check if the NPC can target this gym object type based on last usage"""
        if not self.gym_object_type_restriction:
            return True
        
        # Map tile IDs to gym object types
        gym_object_types = {
            0: "bench",      # Regular bench
            1: "treadmill",  # Treadmill
            2: "dumbbell_rack", # Dumbbell rack
            3: "bench",      # Small bench (same type as regular bench)
            4: "squat_rack"  # Squat rack
        }
        
        if tile_id not in gym_object_types:
            return True  # Allow non-gym objects
        
        target_type = gym_object_types[tile_id]
        
        # If no previous gym object used, allow any type
        if self.last_gym_object_type is None:
            return True
        
        # If same type as last used, block it
        if target_type == self.last_gym_object_type:
            
            return False
        
        # Different type, allow it
        
        return True
    
    def _update_last_gym_object_type(self, tile_id):
        """Update the last gym object type used by this NPC"""
        # Map tile IDs to gym object types
        gym_object_types = {
            0: "bench",      # Regular bench
            1: "treadmill",  # Treadmill
            2: "dumbbell_rack", # Dumbbell rack
            3: "bench",      # Small bench (same type as regular bench)
            4: "squat_rack"  # Squat rack
        }
        
        if tile_id in gym_object_types:
            new_type = gym_object_types[tile_id]
            old_type = self.last_gym_object_type
            self.last_gym_object_type = new_type
    
    
    def _update_last_gym_object_type_from_coords(self, tile_x, tile_y):
        """Update the last gym object type from tile coordinates"""
        if not self.tilemap:
            return
        
        # Get the tile ID from the coordinates
        if (tile_y < len(self.tilemap.layer2_tiles) and 
            tile_x < len(self.tilemap.layer2_tiles[0])):
            tile_id = self.tilemap.layer2_tiles[tile_y][tile_x]
            self._update_last_gym_object_type(tile_id)
    
    def set_tilemap(self, tilemap, gym_manager=None):
        # Call parent method first
        super().set_tilemap(tilemap)
        # Add NPC-specific tilemap setup
        self.collision_system = CollisionSystem(tilemap, gym_manager)
        self.pathfinder = GymPathfinder(tilemap, gym_manager)
    
    def update(self, delta_time):
        """Update NPC logic including pathfinding and AI behavior"""
        #print(f"NPC update called - AI state: {self.ai_state}, hidden: {self.hidden}")
        # Call parent update method for animation
        super().update(delta_time)
        self._update_pathfinding(delta_time)
        self._update_ai_behavior(delta_time)
        self._update_cleaning_behavior(delta_time)
        self._update_pending_cleaning_check()
        self._update_workout_animation(delta_time)
    
    def _update_pathfinding(self, delta_time):
        """Update pathfinding movement"""
        if not self.current_path or self.path_index >= len(self.current_path):
            # Don't change AI state if we're currently interacting
            if self.ai_state != "interacting":
                self.ai_state = "idle"
            return
        
        # Get next waypoint
        next_waypoint = self.current_path[self.path_index]
        target_x, target_y = self.pathfinder.grid_to_screen(*next_waypoint)
        
        # Calculate direction to waypoint using collision pivot point
        collision_x = self.x
        collision_y = self.y + self.pivot_offset
        dx = target_x - collision_x
        dy = target_y - collision_y
        
        # Check if we've reached the waypoint using collision pivot point
        if abs(dx) < 3 and abs(dy) < 3:  # Within 3 pixels (more precise waypoint detection)
            self.path_index += 1
            if self.path_index >= len(self.current_path):
                # Reached final destination
                self.moving = False
                
                # Check if this is a cleaning destination (trashcan or bench return) FIRST
                if hasattr(self, 'cleaning_phase'):
                    # This is a cleaning destination, set to idle so cleaning behavior can handle it
                    
                    self.ai_state = "idle"
                    return
                
                # Not a cleaning destination, process as regular gym object
                self.ai_state = "interacting"
                
                # Check what type of object this is and handle accordingly
                if hasattr(self, 'target_object_coords'):
                    obj_x, obj_y = self.target_object_coords
                    
                    # Check if this is actually a bench object
                    if (obj_y < len(self.tilemap.layer2_tiles) and 
                        obj_x < len(self.tilemap.layer2_tiles[0])):
                        tile_id = self.tilemap.layer2_tiles[obj_y][obj_x]
                        
                        # Start interaction sequence for gym objects
                        if tile_id in [0, 1, 2, 3, 4]:  # Bench (0), Treadmill (1), DumbbellRack (2), Small Bench (3), SquatRack (4)
                            
                            self._start_gym_object_interaction()
                        else:
                            
                            self.ai_state = "idle"
                    else:
                        #print(f"Invalid coordinates for object interaction: ({obj_x}, {obj_y})")
                        self.ai_state = "idle"
                
                # Don't choose new behavior - stay at the bench
                return
        
        # Move towards waypoint
        if abs(dx) > 0 or abs(dy) > 0:
            self.moving = True

            # Store current position for next frame comparison
            self.last_position = (self.x, self.y)
            
            # Normalize movement
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 0:
                dx = (dx / distance) * self.speed
                dy = (dy / distance) * self.speed
                
                # Update direction for animation - only when close to tile center
                # Check if NPC is close to the center of the current tile using collision pivot
                current_tile_x = int(collision_x // 16)
                current_tile_y = int(collision_y // 16)
                tile_center_x = current_tile_x * 16 + 8
                tile_center_y = current_tile_y * 16 + 8
                
                # Only change direction if within 4 pixels of tile center
                if abs(collision_x - tile_center_x) < 4 and abs(collision_y - tile_center_y) < 4:
                    if abs(dx) > abs(dy):
                        self.direction = "right" if dx > 0 else "left"
                    else:
                        self.direction = "down" if dy > 0 else "up"
                
                # Move
                new_x = self.x + dx
                new_y = self.y + dy
                
                if not self.check_collision(new_x, new_y):
                    self.x = new_x
                    self.y = new_y
                    # Update rect to match sprite center
                    self.rect.x = new_x - (self.sprite_width // 2)
                    self.rect.y = new_y - (self.sprite_height // 2)
    
    def _update_ai_behavior(self, delta_time):
        """Update AI behavior and decision making"""
        #print(f"NPC AI behavior update - state: {self.ai_state}")
        
        # Check if this is a cleaning NPC - COMPLETELY bypass regular AI for cleaning
        if hasattr(self, 'cleaning_phase'):
            # This is a cleaning NPC, let the cleaning behavior handle it
            # Don't let any other AI system interfere
            return
        
        # Only allow automatic behavior if not manually targeted to a bench
        if self.ai_state == "idle" and not hasattr(self, 'manually_targeted'):
            self.behavior_timer += delta_time
            if self.behavior_timer >= self.behavior_interval:
        
                self._choose_new_behavior()
                self.behavior_timer = 0
        
        elif self.ai_state == "moving":
            self.behavior_timer += delta_time
    
        elif self.ai_state == "interacting":
            #print(f"NPC in interacting state, hidden: {self.hidden}")
            
            # Check if we still have target coordinates (if not, something went wrong)
            if not hasattr(self, 'target_object_coords'):
                #print(f"NPC in interacting state but no target coordinates - resetting to idle")
                self.ai_state = "idle"
                return
            
            # Only check for animation completion if NPC is hidden (bench objects only)
            if self.hidden:
                obj_x, obj_y = self.target_object_coords
                #print(f"NPC in interacting state, checking bench interaction at ({obj_x}, {obj_y})")
                
                # Check if animation is still playing (for bench objects)
                if (hasattr(self, 'collision_system') and hasattr(self.collision_system, 'gym_manager') and 
                    self.collision_system.gym_manager):
                    obj = self.collision_system.gym_manager.get_object_at_tile(obj_x, obj_y)
                    if obj and obj.has_state("in_use"):
                        # Animation is playing, wait for it to complete
                        # The gym manager handles the animation timing
                        pass
                    else:
                        # Object is no longer in use, complete interaction
                       
                        self._complete_bench_interaction()
                else:
                    # Gym manager not available, wait a bit longer before completing
                    pass
            else:
                # NPC is visible but in interacting state - this means it reached a non-bench object
                obj_x, obj_y = self.target_object_coords
                if (obj_y < len(self.tilemap.layer2_tiles) and 
                    obj_x < len(self.tilemap.layer2_tiles[0])):
                    tile_id = self.tilemap.layer2_tiles[obj_y][obj_x]
                    if tile_id == 2:  # Dumbbell rack - wait for full interaction duration
                        # Check if dumbbell rack interaction is still active
                        if (hasattr(self, 'collision_system') and hasattr(self.collision_system, 'gym_manager') and 
                            self.collision_system.gym_manager):
                            obj = self.collision_system.gym_manager.get_object_at_tile(obj_x, obj_y)
                            if obj and obj.has_state("in_use"):
                                # Interaction still active, wait for it to complete
                                
                                return
                            else:
                                # Interaction completed, the dumbbell rack's end_interaction() was called
                                # which already handled the drop/return logic, so just complete the NPC interaction
                                self._complete_non_bench_interaction()
                    elif tile_id != 0:  # Other non-bench objects (treadmill, squat rack)
                        #print(f"NPC reached non-bench object (tile_id: {tile_id}) - completing interaction")
                        self._complete_non_bench_interaction()
    
    def _choose_new_behavior(self):
        """Choose a new behavior for the NPC"""
        #print("=== _choose_new_behavior() CALLED ===")
        
        # Don't choose new behavior if NPC is cleaning
        if hasattr(self, 'cleaning_phase'):
            return
            
        if not self.tilemap:
            return
        
        
        # Find available gym objects to interact with using the gym manager
        available_objects = []
        
        # Use gym manager if available
        if hasattr(self, 'collision_system') and hasattr(self.collision_system, 'gym_manager') and self.collision_system.gym_manager:
            gym_manager = self.collision_system.gym_manager
            
            
            # Get all gym objects from the manager, excluding front desk and trashcan
            for pos, obj in gym_manager.get_collision_objects():
                # Skip front desk and trashcan (unless NPC is cleaning)
                obj_type = gym_manager.object_types.get(pos)
                if obj_type in ["front_desk", "trashcan"]:
                    continue
                
        
                
                # Get the collision rectangle from the gym object
                collision_rect = obj.get_collision_rect()
                if collision_rect:
                    # Use the actual gym object instead of creating a fake one
                    # The pathfinder will use the real collision rectangle
                    available_objects.append(obj)
        else:
            
            # Fallback to old method if gym manager not available
            for y, row in enumerate(self.tilemap.layer2_tiles):
                for x, tile_id in enumerate(row):
                    # Target specific gym equipment: bench(0), treadmill(1), dumbbell_rack(2), small_bench(3), squat_rack(4)
                    # Exclude front_desk(5) and trashcan(6)
                    if tile_id in [0, 1, 2, 3, 4]:
                        # Create a simple object representation without hitbox
                        # Target the tile below the object (y+1) so NPC stands in front of equipment
                        target_tile_x = x
                        target_tile_y = y + 1  # Target tile below the object
                        
                        obj = type('GymObject', (), {
                            'rect': pygame.Rect(x * 16, y * 16, 16, 16), 
                            'tile_id': tile_id,
                            'tile_x': target_tile_x,
                            'tile_y': target_tile_y
                        })()
                        available_objects.append(obj)
        
        if available_objects:
            # Debug: Show what objects we found
            
            for i, obj in enumerate(available_objects):
                obj_type = type(obj).__name__
                if hasattr(obj, 'x') and hasattr(obj, 'y'):
            
              
            
            # Smart targeting: Give different equipment types a fair chance
                    import random
            
            
            # Categorize objects by type and apply gym object type restrictions
            benches = [obj for obj in available_objects if hasattr(obj, '__class__') and 'Bench' in obj.__class__.__name__]
            treadmills = [obj for obj in available_objects if hasattr(obj, '__class__') and 'Treadmill' in obj.__class__.__name__]
            # Filter dumbbell racks to only include those with available dumbbells
            dumbbell_racks = [obj for obj in available_objects if hasattr(obj, '__class__') and 'DumbbellRack' in obj.__class__.__name__ and obj.is_available()]
            squat_racks = [obj for obj in available_objects if hasattr(obj, '__class__') and 'SquatRack' in obj.__class__.__name__]
            
            # Apply gym object type restrictions
            if self.last_gym_object_type == "bench":
                benches = []  # Block benches if last used was bench
               
            elif self.last_gym_object_type == "treadmill":
                treadmills = []  # Block treadmills if last used was treadmill
               
            elif self.last_gym_object_type == "dumbbell_rack":
                dumbbell_racks = []  # Block dumbbell racks if last used was dumbbell rack
                
            elif self.last_gym_object_type == "squat_rack":
                squat_racks = []  # Block squat racks if last used was squat rack
            
            # First, randomly choose which equipment type to target (25% each)
            available_types = []
            if treadmills:
                available_types.append("Treadmill")
            if benches:
                available_types.append("Bench")
            if dumbbell_racks:
                available_types.append("DumbbellRack")
            if squat_racks:
                available_types.append("SquatRack")
            
            # Randomly choose equipment type (equal probability)
            chosen_type = random.choice(available_types)
            
            # Then randomly choose from that type
            if chosen_type == "Treadmill":
                target = random.choice(treadmills)
            elif chosen_type == "Bench":
                target = random.choice(benches)
            elif chosen_type == "DumbbellRack":
                target = random.choice(dumbbell_racks)
            elif chosen_type == "SquatRack":
                target = random.choice(squat_racks)
            
            if not target:
                return
            
 
            
            # Store the target and available types for fallback
            self.current_target = target
            self.available_types = available_types
            self.chosen_type = chosen_type
            self.target_attempts = 0
            

            self.move_to_object(target)
        else:
            # If no gym objects available, move to a random walkable position
            #print("No gym objects found - NPC wandering randomly")
            self._wander_randomly()
    
    def _try_alternative_target(self):
        """Try alternative targets when pathfinding fails"""
        if not hasattr(self, 'available_types') or not self.available_types:
            self.current_path = []
            self.path_index = 0
            self.ai_state = "idle"
            return
        
        # Remove the failed type from available types
        failed_type = self.chosen_type
        self.available_types = [t for t in self.available_types if t != failed_type]
        
        if not self.available_types:
            self.current_path = []
            self.path_index = 0
            self.ai_state = "idle"
            return
        
        # Try the next available type
        import random
        next_type = random.choice(self.available_types)
        
        # Choose a new target from the new type
        if next_type == "Treadmill":
            target = random.choice([obj for obj in self.collision_system.gym_manager.get_collision_objects() if 'Treadmill' in type(obj[1]).__name__])
            target = target[1]  # Get the actual object
        elif next_type == "Bench":
            target = random.choice([obj for obj in self.collision_system.gym_manager.get_collision_objects() if 'Bench' in type(obj[1]).__name__])
            target = target[1]  # Get the actual object
        elif next_type == "DumbbellRack":
            target = random.choice([obj for obj in self.collision_system.gym_manager.get_collision_objects() if 'DumbbellRack' in type(obj[1]).__name__])
            target = target[1]  # Get the actual object
        elif next_type == "SquatRack":
            target = random.choice([obj for obj in self.collision_system.gym_manager.get_collision_objects() if 'SquatRack' in type(obj[1]).__name__])
            target = target[1]  # Get the actual object
        
        # Update current target and try again
        self.current_target = target
        self.chosen_type = next_type
        self.move_to_object(target)
    
    def _wander_randomly(self):
        """Move to a random walkable position"""
        if not self.pathfinder:
            return
        
        # Don't wander if NPC is cleaning
        if hasattr(self, 'cleaning_phase'):
            return
        
        # Find a random walkable position
        import random
        attempts = 0
        max_attempts = 20
        
        while attempts < max_attempts:
            # Pick random grid coordinates
            grid_x = random.randint(0, self.pathfinder.width - 1)
            grid_y = random.randint(0, self.pathfinder.height - 1)
            
            # Check if position is walkable
            if self.pathfinder.is_valid(grid_x, grid_y):
                # Convert to screen coordinates
                target_x, target_y = self.pathfinder.grid_to_screen(grid_x, grid_y)
                self.move_to_position(target_x, target_y)
                return
            
            attempts += 1
    
    def set_behavior(self, behavior_type, **kwargs):
        """Manually set NPC behavior"""
        if behavior_type == "idle":
            self.ai_state = "idle"
            self.current_path = []
            self.path_index = 0
            self.moving = False
        elif behavior_type == "move_to_object":
            if 'target_object' in kwargs:
                self.move_to_object(kwargs['target_object'])
        elif behavior_type == "move_to_position":
            if 'x' in kwargs and 'y' in kwargs:
                self.move_to_position(kwargs['x'], kwargs['y'])
        elif behavior_type == "wander":
            self._wander_randomly()
    
    def get_ai_state(self):
        """Get current AI state for debugging"""
        # Calculate current tile position
        current_tile_x = int(self.x // 16)
        current_tile_y = int(self.y // 16)
        
        return {
            'state': self.ai_state,
            'moving': self.moving,
            'path_length': len(self.current_path),
            'path_index': self.path_index,
            'has_target': self.target_object is not None,
            'tile_x': current_tile_x,
            'tile_y': current_tile_y,
            'pos_x': int(self.x),
            'pos_y': int(self.y)
        }
    
    def move_to_object(self, target_object):
        """Move towards a target object using pathfinding"""
        if not self.pathfinder:
            return
        
        # Don't allow targeting if NPC is cleaning
        if hasattr(self, 'cleaning_phase'):
            return
        
        self.target_object = target_object
        start_pos = (self.x, self.y)
        
        # If this is a real gym object, calculate the target position properly
        if hasattr(target_object, 'get_collision_rect'):
            # Get the actual collision rectangle
            collision_rect = target_object.get_collision_rect()
            
            # Calculate target position - stand in front of the object
            # For most objects, stand below (south) of the object
            target_x = collision_rect.centerx
            target_y = collision_rect.bottom + 16  # 16 pixels below the object
            
    
            
            # Convert to screen coordinates for pathfinding
            target_screen_pos = (target_x, target_y)
            
            # Find path to the calculated position
            path = self.pathfinder.find_path(start_pos, target_screen_pos)
            
            if path:
                self.current_path = path
                self.path_index = 0
                self.ai_state = "moving"
                self.moving = True
                
                # Store the object's actual tile coordinates for interaction
                # We need to find the tile coordinates by looking up the object in the tilemap
                # since the object's world position might not exactly match the tile coordinates
                if hasattr(self, 'tilemap') and self.tilemap:
                    # Find the tile coordinates by searching the tilemap
                    found_tile = self._find_object_tile_coordinates(target_object)
                    if found_tile:
                        obj_tile_x, obj_tile_y = found_tile
                        
                    else:
                        # Fallback to calculated coordinates
                        obj_tile_x = int(collision_rect.centerx // 16)
                        obj_tile_y = int(collision_rect.centery // 16)
                        
                else:
                    # Fallback to calculated coordinates
                    obj_tile_x = int(collision_rect.centerx // 16)
                    obj_tile_y = int(collision_rect.centery // 16)
                
                # Store the tile coordinates for interaction
                self.target_object_coords = (obj_tile_x, obj_tile_y)
                
                # Calculate target position tile coordinates for debug output
                target_tile_x = int(target_x // 16)
                target_tile_y = int(target_y // 16)
                
                pass
            else:
                # No path found, try alternative targets
                
                self._try_alternative_target()
        else:
            # Fallback for old-style objects
            path = self.pathfinder.find_path_to_object(start_pos, target_object)
            
            if path:
                self.current_path = path
                self.path_index = 0
                self.ai_state = "moving"
                self.moving = True
            else:
                # No path found, stay idle
                self.ai_state = "idle"
    
    def move_to_position(self, target_x, target_y):
        """Move to a specific position using pathfinding"""
        if not self.pathfinder:
            return
        
        start_pos = (self.x, self.y)
        goal_pos = (target_x, target_y)
        
        # Find path to position
        path = self.pathfinder.find_path(start_pos, goal_pos)
        
        if path:
            self.current_path = path
            self.path_index = 0
            self.ai_state = "moving"
            self.moving = True
            
        else:
            # No path found, clear current path and stay idle
            
            self.current_path = []
            self.path_index = 0
            self.ai_state = "idle"
    
    def target_specific_bench(self, tile_x, tile_y):
        """Target a specific bench at the given tile coordinates"""
        if not self.pathfinder:
            return
        
        # Create a target object for the bench
        # The target should be the tile below the bench (y+1) for interaction
        target_tile_y = tile_y + 1
        
        # Convert tile coordinates to screen coordinates
        target_x = tile_x * 16 + 8  # Center of tile
        target_y = target_tile_y * 16 + 8  # Center of tile below bench
        
        # Move to the position in front of the bench
        self.move_to_position(target_x, target_y)
        
        # Store bench coordinates for animation control
        self.target_object_coords = (tile_x, tile_y)
        
        # Mark as manually targeted to prevent automatic behavior
        self.manually_targeted = True
    
    def _start_gym_object_interaction(self):
        """Start gym object interaction when NPC reaches the target"""
        if not hasattr(self, 'target_object_coords') or not self.tilemap:
            return
        
        obj_x, obj_y = self.target_object_coords
        
        # Check if this is actually a gym object (not front desk or trashcan)
        if (obj_y < len(self.tilemap.layer2_tiles) and 
            obj_x < len(self.tilemap.layer2_tiles[0])):
            tile_id = self.tilemap.layer2_tiles[obj_y][obj_x]
            
            # Skip front desk and trashcan (unless NPC is cleaning)
            if tile_id in [5, 6]:  # Front desk (5), Trashcan (6)
                self.ai_state = "idle"
                return
            
            # Handle different gym equipment types
            if tile_id == 0:  # Regular bench
                if (hasattr(self, 'collision_system') and hasattr(self.collision_system, 'gym_manager') and 
                    self.collision_system.gym_manager):
                    # Start the bench interaction properly using the gym manager
                    obj = self.collision_system.gym_manager.get_object_at_tile(obj_x, obj_y)
                    if obj and hasattr(obj, 'start_interaction'):
                        # Start proper interaction with this NPC
                        success = obj.start_interaction(self)
                        if success:
                            # Update pathfinding cache for all NPCs
                            if hasattr(self, 'pathfinder'):
                                self.pathfinder.mark_cache_dirty()
                        else:

                            # Bench is occupied, find another target
                            self.ai_state = "idle"
                            return
                    
                    # Hide the NPC - animation will handle the 5-second duration
                    self.hidden = True
                    
            elif tile_id == 1:  # Treadmill
                if (hasattr(self, 'collision_system') and hasattr(self.collision_system, 'gym_manager') and 
                    self.collision_system.gym_manager):
                    # Start the treadmill interaction properly using the gym manager
                    obj = self.collision_system.gym_manager.get_object_at_tile(obj_x, obj_y)
                    
                    if obj and hasattr(obj, 'start_interaction'):
                        # Start proper interaction with this NPC
                        success = obj.start_interaction(self)
                        
                        if success:
                            # Update pathfinding cache for all NPCs
                            if hasattr(self, 'pathfinder'):
                                self.pathfinder.mark_cache_dirty()
                        else:
                            # Treadmill is occupied, find another target
                            self.ai_state = "idle"
                            return
                    
                    # Hide the NPC - animation will handle the 8-second duration
                    self.hidden = True
                    
            elif tile_id == 2:  # DumbbellRack
                if (hasattr(self, 'collision_system') and hasattr(self.collision_system, 'gym_manager') and 
                    self.collision_system.gym_manager):
                    # Start the dumbbell rack interaction properly using the gym manager
                    obj = self.collision_system.gym_manager.get_object_at_tile(obj_x, obj_y)
                    if obj and hasattr(obj, 'start_interaction'):
                        # Start proper interaction with this NPC
                        success = obj.start_interaction(self)
                        if success:
                    
                            # Start dumbbell workout animation
                            self.start_workout_animation("dumbbell")
                            # Update pathfinding cache for all NPCs
                            if hasattr(self, 'pathfinder'):
                                self.pathfinder.mark_cache_dirty()
                        else:
                    
                            # Dumbbell rack is occupied, find another target
                            self.ai_state = "idle"
                            return
                   
            
                    
            elif tile_id == 4:  # SquatRack
                if (hasattr(self, 'collision_system') and hasattr(self.collision_system, 'gym_manager') and 
                    self.collision_system.gym_manager):
                    # Start the squat rack interaction properly using the gym manager
                    obj = self.collision_system.gym_manager.get_object_at_tile(obj_x, obj_y)
                    if obj and hasattr(obj, 'start_interaction'):
                        # Start proper interaction with this NPC
                        success = obj.start_interaction(self)
                        if success:
                            # Update pathfinding cache for all NPCs
                            if hasattr(self, 'pathfinder'):
                                self.pathfinder.mark_cache_dirty()
                            # Hide the NPC - animation will handle the 5-second duration
                            self.hidden = True
                        else:
                            # Squat rack is occupied, find another target
                            self.ai_state = "idle"
                            return
                    else:
                        # No valid object found, reset to idle
                        self.ai_state = "idle"
                        return
                else:
                    # No gym manager available, reset to idle
                    self.ai_state = "idle"
                    return
    def _complete_gym_interaction(self):
        """Complete the gym equipment interaction after the animation completes"""
        
        
        if not hasattr(self, 'target_object_coords') or not self.tilemap:
            
            return
        
        obj_x, obj_y = self.target_object_coords
       
        
        # Get the object type to determine completion message
        tile_id = self.tilemap.layer2_tiles[obj_y][obj_x]

        
        # Skip front desk and trashcan interactions
        if tile_id in [5, 6]:  # Front desk (5), Trashcan (6)
            
            self.ai_state = "idle"
            return
        
        equipment_name = "equipment"
        if tile_id == 0:
            equipment_name = "bench"
        elif tile_id == 1:
            equipment_name = "treadmill"
        elif tile_id == 2:
            equipment_name = "dumbbell rack"
            # Stop dumbbell workout animation
            if self.is_working_out and self.workout_type == "dumbbell":
                self.stop_workout_animation()
        elif tile_id == 4:
            equipment_name = "squat rack"
        
        
        
        # Update the last gym object type used for targeting restrictions
        self._update_last_gym_object_type(tile_id)
        
        # Check if this is a bench that might become dirty and NPC should clean it
        if tile_id in [0, 3]:  # Regular bench or small bench
            # Delay the cleaning check to next frame to allow bench to become dirty
            self.pending_cleaning_check = True
            self.pending_cleaning_coords = (obj_x, obj_y)
           
            return
        
        # Update pathfinding cache since equipment is now free
        if hasattr(self, 'pathfinder'):
            self.pathfinder.mark_cache_dirty()
        
        # Unhide the NPC and reset interaction
        self.hidden = False
        self.ai_state = "idle"
        
        # Clear the manual targeting so NPC can resume normal behavior
        if hasattr(self, 'manually_targeted'):
            delattr(self, 'manually_targeted')
        
        # Clear the target coordinates so NPC won't target the same equipment again
        if hasattr(self, 'target_object_coords'):
            delattr(self, 'target_object_coords')
    
    def _update_workout_animation(self, delta_time):
        """Update workout animation if NPC is working out"""
        if not self.is_working_out or not self.workout_sprite:
            return
        
        self.workout_animation_timer += delta_time
        if self.workout_animation_timer >= self.workout_animation_speed:
            self.workout_animation_timer = 0
            self.workout_animation_index = (self.workout_animation_index + 1) % self.workout_frames
           
    
    def start_workout_animation(self, workout_type):
        """Start workout animation for the NPC"""
        if workout_type == "dumbbell":
            # Load dumbbell workout sprite
            try:
                self.workout_sprite = pygame.image.load("Graphics/npc_working_out_dumbbell.png").convert_alpha()
                
            except pygame.error as e:
                
                return False
            
            self.workout_type = workout_type
            self.is_working_out = True
            self.workout_animation_timer = 0
            self.workout_animation_index = 0
    
            return True
        return False
    
    def stop_workout_animation(self):
        """Stop workout animation and return to normal sprite"""
        self.is_working_out = False
        self.workout_type = None
        self.workout_sprite = None
        
        
    def _should_clean_bench(self, obj_x, obj_y):
        """Check if NPC should clean the bench (80% chance if bench is dirty)"""
        import random
        
        # Check if the bench is dirty
        if (hasattr(self, 'collision_system') and hasattr(self.collision_system, 'gym_manager') and 
            self.collision_system.gym_manager):
            obj = self.collision_system.gym_manager.get_object_at_tile(obj_x, obj_y)
            if obj and obj.has_state("dirty"):
                # 80% chance to clean the bench
                should_clean = random.random() < 0.4
                
                return should_clean
        return False
    
    def _start_cleaning_behavior(self, bench_x, bench_y):
        """Start the cleaning behavior: walk to trashcan, then back to clean the bench"""
        
        
        if not hasattr(self, 'collision_system') or not hasattr(self.collision_system, 'gym_manager'):
           
            return
        
        gym_manager = self.collision_system.gym_manager
        
        # Find the nearest trashcan
        trashcan = self._find_nearest_trashcan(gym_manager)
        if not trashcan:
           
            # No trashcan found, complete interaction normally
            self._complete_gym_interaction()
            return
        
       
        
        # Make NPC visible again for cleaning behavior
        self.hidden = False
    
        
        # Store the bench coordinates for when we return
        self.cleaning_bench_coords = (bench_x, bench_y)
        
        
        # Move to trashcan first
        self._move_to_trashcan(trashcan)
    
    def _find_object_tile_coordinates(self, target_object):
        """Find the tile coordinates for a given gym object by searching the tilemap"""
        if not hasattr(self, 'tilemap') or not self.tilemap:
            return None
        
        # Get the object's world position
        if not hasattr(target_object, 'x') or not hasattr(target_object, 'y'):
            return None
        
        obj_world_x = target_object.x
        obj_world_y = target_object.y
        
        # Search through the tilemap to find matching objects
        for y, row in enumerate(self.tilemap.layer2_tiles):
            for x, tile_id in enumerate(row):
                if tile_id == -1:  # Skip empty tiles
                    continue
                
                # Convert tile coordinates to world coordinates
                tile_world_x = x * 16 + 8
                tile_world_y = y * 16 + 8
                
                # Check if this tile position matches the object's world position
                # Use a small tolerance since positions might not be exactly the same
                tolerance = 16  # Within one tile
                if (abs(obj_world_x - tile_world_x) < tolerance and 
                    abs(obj_world_y - tile_world_y) < tolerance):
                    return (x, y)
        
        return None
    
    def _update_pending_cleaning_check(self):
        """Handle delayed cleaning check after bench has had chance to become dirty"""
        if not hasattr(self, 'pending_cleaning_check') or not self.pending_cleaning_check:
            return
        
      
        
        if hasattr(self, 'pending_cleaning_coords'):
            obj_x, obj_y = self.pending_cleaning_coords
            
            
            # Now check if bench is dirty and start cleaning behavior
            if self._should_clean_bench(obj_x, obj_y):
                
                self._start_cleaning_behavior(obj_x, obj_y)
            else:
             
                # Complete the interaction normally
                self._finish_gym_interaction_normally()
        
        # Clear the pending check
        self.pending_cleaning_check = False
        if hasattr(self, 'pending_cleaning_coords'):
            
            delattr(self, 'pending_cleaning_coords')
    
    def _finish_gym_interaction_normally(self):
        """Finish gym interaction normally without cleaning"""
        # Update pathfinding cache since equipment is now free
        if hasattr(self, 'pathfinder'):
            self.pathfinder.mark_cache_dirty()
        
        # Unhide the NPC and reset interaction
        self.hidden = False
        self.ai_state = "idle"
        
       
        
        # Clear the manual targeting so NPC can resume normal behavior
        if hasattr(self, 'manually_targeted'):
            delattr(self, 'manually_targeted')
        
        # Clear the target coordinates so NPC won't target the same equipment again
        if hasattr(self, 'target_object_coords'):
            delattr(self, 'target_object_coords')
    
    def _find_nearest_trashcan(self, gym_manager):
        """Find the nearest trashcan to the NPC's current position"""
        trashcans = gym_manager.get_gym_objects_by_type("trashcan")
        if not trashcans:
            return None
        
        # Find the closest trashcan
        nearest_trashcan = None
        min_distance = float('inf')
        
        for trashcan in trashcans:
            distance = ((self.x - trashcan.x) ** 2 + (self.y - trashcan.y) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                nearest_trashcan = trashcan
        
        return nearest_trashcan
    
    def _move_to_trashcan(self, trashcan):
        """Move to the trashcan position"""
        # Try multiple positions around the trashcan to find one that's reachable
        # The trashcan is 16x35 pixels, so try different offsets
        possible_targets = [
            (trashcan.x + 16, trashcan.y + 8),      # Right of trashcan
            (trashcan.x - 16, trashcan.y + 8),      # Left of trashcan  
            (trashcan.x, trashcan.y + 35),          # Below trashcan
            (trashcan.x, trashcan.y - 16),          # Above trashcan
            (trashcan.x + 8, trashcan.y + 8),       # Diagonal right
            (trashcan.x - 8, trashcan.y + 8),       # Diagonal left
        ]
        
        
        
        # Store trashcan info for when we reach it
        self.target_trashcan = trashcan
        self.cleaning_phase = "going_to_trashcan"
        
        # Try each possible target position
        for i, (target_x, target_y) in enumerate(possible_targets):
          
            # Try to move to this position
            
            self.move_to_position(target_x, target_y)
            
            # Check if pathfinding succeeded
            
            
            if self.current_path and len(self.current_path) > 0:
                self.ai_state = "moving"
                self.moving = True
                
                return
        
        # If we get here, all positions failed
        
        self._abort_cleaning()
        return
    
    def _complete_cleaning_sequence(self):
        """Complete the cleaning sequence by cleaning the bench"""
        if not hasattr(self, 'cleaning_bench_coords'):
            
            return
        
        bench_x, bench_y = self.cleaning_bench_coords
        
     
        
        # Get the bench object and start cleaning
        if (hasattr(self, 'collision_system') and hasattr(self.collision_system, 'gym_manager') and 
            self.collision_system.gym_manager):
            gym_manager = self.collision_system.gym_manager
            obj = gym_manager.get_object_at_tile(bench_x, bench_y)
            
            if obj and obj.has_state("dirty"):
                # Use the bench's built-in cleaning animation
                
                
                # Ensure NPC remains visible during cleaning
                self.hidden = False
              
                
                # Start the bench's cleaning animation
                obj.start_cleaning()
             
                
                # Set cleaning phase and wait for completion
                self.cleaning_phase = "cleaning_bench"
                self.ai_state = "interacting"
               
                return
        
        # If we can't clean, complete interaction normally
       
        self._finish_gym_interaction_normally()
    
    def _abort_cleaning(self):
        """Abort the cleaning sequence due to pathfinding failure"""

        
        # Clear all cleaning-related attributes
        if hasattr(self, 'cleaning_bench_coords'):
            delattr(self, 'cleaning_bench_coords')
        if hasattr(self, 'target_trashcan'):
            delattr(self, 'target_trashcan')
        if hasattr(self, 'cleaning_phase'):
            delattr(self, 'cleaning_phase')
        if hasattr(self, 'cleaning_timer'):
            delattr(self, 'cleaning_timer')
        if hasattr(self, 'cleaning_duration'):
            delattr(self, 'cleaning_duration')
        
        # Complete the interaction normally
        self._finish_gym_interaction_normally()
    
    def _update_cleaning_behavior(self, delta_time):
        """Update cleaning behavior logic"""
        if not hasattr(self, 'cleaning_phase'):
            return
        
        
        if self.cleaning_phase == "going_to_trashcan":
            # Check if we reached the trashcan
            
           
        
            
            if self.ai_state == "idle" and hasattr(self, 'target_trashcan'):
        
                # We reached the trashcan, now go back to the bench
                self._return_to_bench()
            else:

                
                                # Check if we're close enough to the trashcan to consider it reached
                if hasattr(self, 'target_trashcan'):
                    distance_to_trashcan = ((self.x - self.target_trashcan.x) ** 2 + (self.y - self.target_trashcan.y) ** 2) ** 0.5
                    if distance_to_trashcan < 20:  # Within 20 pixels
                        
                        # Before returning, check if the bench is still dirty
                        if hasattr(self, 'cleaning_bench_coords'):
                            bench_x, bench_y = self.cleaning_bench_coords
                            if (hasattr(self, 'collision_system') and hasattr(self.collision_system, 'gym_manager') and 
                                self.collision_system.gym_manager):
                                gym_manager = self.collision_system.gym_manager
                                obj = gym_manager.get_object_at_tile(bench_x, bench_y)
                                
                                if obj and obj.has_state("dirty"):
                                    
                                    self._return_to_bench()
                                else:
                                    
                                    self._abort_cleaning()
                                    return
                            else:
                                
                                self._abort_cleaning()
                                return
                        else:
                            
                            self._abort_cleaning()
                            return
                
        elif self.cleaning_phase == "returning_to_bench":
            # Check if we reached the bench
            if self.ai_state == "idle" and hasattr(self, 'cleaning_bench_coords'):
               
                
                # Check if the bench is still dirty before starting cleaning
                bench_x, bench_y = self.cleaning_bench_coords
                if (hasattr(self, 'collision_system') and hasattr(self.collision_system, 'gym_manager') and 
                    self.collision_system.gym_manager):
                    gym_manager = self.collision_system.gym_manager
                    obj = gym_manager.get_object_at_tile(bench_x, bench_y)
                    
                    if obj and obj.has_state("dirty"):
                      
                        # We reached the bench and it's still dirty, start cleaning
                        self._complete_cleaning_sequence()
                    else:
                       
                        # Bench was cleaned by someone else, abandon cleaning
                        self._abort_cleaning()
                        return
                else:
                    
                    self._abort_cleaning()
                    return
           
        
        elif self.cleaning_phase == "cleaning_bench":
            # Check if the bench's cleaning animation is complete
            if hasattr(self, 'cleaning_bench_coords'):
                bench_x, bench_y = self.cleaning_bench_coords
                
                # Get the bench object and check its cleaning state
                if (hasattr(self, 'collision_system') and hasattr(self.collision_system, 'gym_manager') and 
                    self.collision_system.gym_manager):
                    gym_manager = self.collision_system.gym_manager
                    obj = gym_manager.get_object_at_tile(bench_x, bench_y)
                    
                    if obj:
                        # Check if bench is still dirty (in case it was cleaned manually during animation)
                        if not obj.has_state("dirty"):
                           
                            self._abort_cleaning()
                            return
                        
                        # Check if cleaning animation is still running
                        if hasattr(obj, 'cleaning') and obj.cleaning:
                            # Animation still running, wait
                            pass
                        else:
                            # Cleaning animation is complete
                            self._finish_cleaning()
                            return
                    else:
                        
                        self._abort_cleaning()
                        return
                else:
                   
                    self._abort_cleaning()
                    return
    
    def _return_to_bench(self):
        """Return to the bench to clean it"""
        if not hasattr(self, 'cleaning_bench_coords'):
           
            return
        
        bench_x, bench_y = self.cleaning_bench_coords
        
       
        
        # Move to position in front of the bench - use a more reasonable offset
        # Stand 16 pixels below (south) of the bench, but with some horizontal offset
        target_x = bench_x * 16 + 8  # Center of tile
        target_y = (bench_y + 1) * 16 + 8  # Position in front of bench
        
        # Try multiple positions around the bench to find one that's reachable
        possible_bench_positions = [
            (target_x, target_y),           # Directly in front
            (target_x + 16, target_y),      # Right of front
            (target_x - 16, target_y),      # Left of front
            (target_x, target_y + 16),      # Further below
            (target_x + 8, target_y + 8),   # Diagonal right
            (target_x - 8, target_y + 8),   # Diagonal left
        ]
        
       
        
        # Try each possible bench position to find one that's reachable
        for i, (pos_x, pos_y) in enumerate(possible_bench_positions):
    
            
            # Try to move to this position
            self.move_to_position(pos_x, pos_y)
            
            # Check if pathfinding succeeded
            if self.current_path and len(self.current_path) > 0:
                self.ai_state = "moving"
                self.moving = True
                self.cleaning_phase = "returning_to_bench"
                
                return
            
        
        # If we get here, all positions failed
    
        self._abort_cleaning()
        return
    
    def _finish_cleaning(self):
        """Finish the cleaning sequence and complete the interaction"""
        # The bench's cleaning animation has already removed the dirty state
        if hasattr(self, 'cleaning_bench_coords'):
            bench_x, bench_y = self.cleaning_bench_coords
           
            
            # Update the last gym object type to "bench" since we just cleaned a bench
            self._update_last_gym_object_type_from_coords(bench_x, bench_y)
        
        # Clear cleaning-related attributes
        if hasattr(self, 'cleaning_bench_coords'):
            delattr(self, 'cleaning_bench_coords')
        if hasattr(self, 'target_trashcan'):
            delattr(self, 'target_trashcan')
        if hasattr(self, 'cleaning_phase'):
            delattr(self, 'cleaning_phase')
        
        # Complete the interaction normally
        self._finish_gym_interaction_normally()
    

    
    def _complete_bench_interaction(self):
        """Complete interaction with bench objects"""
        if not hasattr(self, 'target_object_coords') or not self.tilemap:
            return
        
        obj_x, obj_y = self.target_object_coords
        
        # Unhide the NPC and reset interaction
        self.hidden = False
        self.ai_state = "idle"
        
        # Clear the manual targeting so NPC can resume normal behavior
        if hasattr(self, 'manually_targeted'):
            delattr(self, 'manually_targeted')
        
        # Clear the target coordinates so NPC won't target the same object again
        if hasattr(self, 'target_object_coords'):
            delattr(self, 'target_object_coords')
        
       
    
    def _complete_non_bench_interaction(self):
        """Complete interaction with non-bench objects (treadmill, dumbbell rack, etc.)"""
        if not hasattr(self, 'target_object_coords') or not self.tilemap:
            return
        
        obj_x, obj_y = self.target_object_coords
        
        # Unhide the NPC and reset interaction
        self.hidden = False
        self.ai_state = "idle"
        
        # Clear the manual targeting so NPC can resume normal behavior
        if hasattr(self, 'manually_targeted'):
            delattr(self, 'manually_targeted')
        
        # Clear the target coordinates so NPC won't target the same object again
        if hasattr(self, 'target_object_coords'):
            delattr(self, 'target_object_coords')
        
       
    
    def draw(self, screen, camera, is_selected=False):
        # Don't draw if NPC is hidden
        if self.hidden:
            return
        
        
        
        # Check if NPC is working out and should show workout sprite
        if self.is_working_out and self.workout_sprite:
            
            self._draw_workout_sprite(screen, camera)
        else:
           
            # Call parent draw method for basic sprite rendering
            super().draw(screen, camera)
        
        # Calculate screen position for NPC-specific drawing
        screen_x, screen_y = camera.apply_pos(self.x, self.y)
        scaled_width = self.sprite_width * camera.zoom
        
        # Draw selection highlight if this NPC is selected
        if is_selected:
            # Draw a green circle around the NPC to show it's selected
            selection_radius = int(scaled_width * 0.8)
            pygame.draw.circle(screen, (0, 255, 0), (int(screen_x), int(screen_y)), selection_radius, 3)
        
        # Debug: Show pivot point coordinates
        #print(f"Pivot point: ({self.x:.1f}, {self.y:.1f})")
        
        # Debug: Draw path if moving and paths are enabled
        if self.current_path and self.ai_state == "moving" and self.show_paths:
            self._draw_path_debug(screen, camera)
    
    def _draw_workout_sprite(self, screen, camera):
        """Draw the workout sprite instead of the normal NPC sprite"""
        if not self.workout_sprite:
            return
        
        # Calculate screen position
        screen_x, screen_y = camera.apply_pos(self.x, self.y)
        
        # Extract current frame from spritesheet (8 frames, each 16x32)
        frame_width = 16
        frame_height = 32
        
        # Get current frame
        current_frame = self.workout_animation_index
        frame_x = current_frame * frame_width
        
        # Create surface for current frame
        frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame_surface.blit(self.workout_sprite, (0, 0), (frame_x, 0, frame_width, frame_height))
        
        # Scale frame to match NPC size
        scaled_frame = pygame.transform.scale(frame_surface, 
            (int(frame_width * self.scale * camera.zoom), 
             int(frame_height * self.scale * camera.zoom)))
        
        # Draw centered on NPC position
        draw_x = screen_x - (scaled_frame.get_width() // 2)
        draw_y = screen_y - (scaled_frame.get_height() // 2)
        
        screen.blit(scaled_frame, (draw_x, draw_y))
        
      
            
    def _draw_path_debug(self, screen, camera):
        """Draw the current path for debugging"""
        if not self.current_path:
            return
        
        # Draw path lines
        for i in range(len(self.current_path) - 1):
            start_pos = self.pathfinder.grid_to_screen(*self.current_path[i])
            end_pos = self.pathfinder.grid_to_screen(*self.current_path[i + 1])
            
            start_screen = camera.apply_pos(*start_pos)
            end_screen = camera.apply_pos(*end_pos)
            
            pygame.draw.line(screen, (255, 0, 0), start_screen, end_screen, 2)
        
        # Draw waypoints at tile centers
        for waypoint in self.current_path:
            pos = self.pathfinder.grid_to_screen(*waypoint)
            screen_pos = camera.apply_pos(*pos)
            # Draw larger waypoint circles to show they're at tile centers
            pygame.draw.circle(screen, (0, 255, 0), (int(screen_pos[0]), int(screen_pos[1])), 4)
            # Draw a small cross to mark the exact center
            pygame.draw.line(screen, (255, 255, 255), 
                           (int(screen_pos[0]) - 2, int(screen_pos[1])), 
                           (int(screen_pos[0]) + 2, int(screen_pos[1])), 1)
            pygame.draw.line(screen, (255, 255, 255), 
                           (int(screen_pos[0]), int(screen_pos[1]) - 2), 
                           (int(screen_pos[0]), int(screen_pos[1]) + 2), 1)
        

            
    def _draw_npc_position_debug(self, screen, camera):
        """Draw debug information showing NPC's actual position vs expected tile position"""
        # Get NPC's current screen position
        npc_screen_pos = camera.apply_pos(self.x, self.y)
        
        # Draw NPC's actual position (red dot)
        pygame.draw.circle(screen, (255, 0, 0), (int(npc_screen_pos[0]), int(npc_screen_pos[1])), 6)
        
        # Calculate what tile the NPC thinks it's on
        npc_tile_x = int(self.x // 16)
        npc_tile_y = int(self.y // 16)
        
        # Get the center of that tile
        tile_center = self.pathfinder.grid_to_screen(npc_tile_x, npc_tile_y)
        tile_center_screen = camera.apply_pos(*tile_center)
        
        # Draw the tile center the NPC thinks it's on (blue dot)
        pygame.draw.circle(screen, (0, 0, 255), (int(tile_center_screen[0]), int(tile_center_screen[1])), 4)
        
        # Draw a line between NPC position and tile center
        pygame.draw.line(screen, (255, 255, 0), 
                        (int(npc_screen_pos[0]), int(npc_screen_pos[1])),
                        (int(tile_center_screen[0]), int(tile_center_screen[1])), 2)
        
        # Draw tile boundaries around NPC
        tile_left = npc_tile_x * 16
        tile_top = npc_tile_y * 16
        tile_rect = pygame.Rect(tile_left, tile_top, 16, 16)
        tile_rect_screen = camera.apply_rect(tile_rect)
        pygame.draw.rect(screen, (255, 255, 0), tile_rect_screen, 1)
        

        
        # Draw sprite bounds for reference (self.x, self.y is now sprite center)
        sprite_rect = pygame.Rect(self.x - (self.sprite_width // 2), self.y - (self.sprite_height // 2), self.sprite_width, self.sprite_height)
        sprite_rect_screen = camera.apply_rect(sprite_rect)
        pygame.draw.rect(screen, (255, 128, 0), sprite_rect_screen, 2)  # Orange rectangle for sprite bounds
        
        # Draw a few surrounding tiles for reference
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                ref_tile_x = npc_tile_x + dx
                ref_tile_y = npc_tile_y + dy
                if 0 <= ref_tile_x < self.pathfinder.width and 0 <= ref_tile_y < self.pathfinder.height:
                    ref_tile_left = ref_tile_x * 16
                    ref_tile_top = ref_tile_y * 16
                    ref_tile_rect = pygame.Rect(ref_tile_left, ref_tile_top, 16, 16)
                    ref_tile_rect_screen = camera.apply_rect(ref_tile_rect)
                    pygame.draw.rect(screen, (100, 100, 100), ref_tile_rect_screen, 1)
            


def create_npc(x, y, spritesheet_path="Graphics/player_temp.png", scale=1.0):
    return NPC(x, y, spritesheet_path, scale)
