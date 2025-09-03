import pygame
from gym_objects.base_object import GymObject
from gym_objects.bench import Bench
from gym_objects.treadmill import Treadmill
from gym_objects.dumbbell_rack import DumbbellRack
from gym_objects.squat_rack import SquatRack
from gym_objects.front_desk import FrontDesk
from gym_objects.trashcan import Trashcan

class GymObjectManager:
    def __init__(self):
        self.gym_objects = {}  # {(x, y): GymObject}
        self.object_types = {}  # {(x, y): "bench", "treadmill", etc.}
        self.show_hitboxes = False  # Flag to toggle hitbox visibility
        self._depth_cache_dirty = True
        
    def add_gym_object(self, x, y, object_type, **kwargs):
        """Add a gym object at the specified position"""
        if object_type == "bench":
            obj = Bench(x, y, **kwargs)
        elif object_type == "treadmill":
            obj = Treadmill(x, y, **kwargs)
        elif object_type == "dumbbell_rack":
            obj = DumbbellRack(x, y, **kwargs)
        elif object_type == "squat_rack":
            obj = SquatRack(x, y, **kwargs)
        elif object_type == "front_desk":
            obj = FrontDesk(x, y, **kwargs)
        elif object_type == "trashcan":
            obj = Trashcan(x, y, **kwargs)
        else:
            raise ValueError(f"Unknown gym object type: {object_type}")
        
        self.gym_objects[(x, y)] = obj
        self.object_types[(x, y)] = object_type
        self._depth_cache_dirty = True
        return obj
    
    def get_gym_object(self, x, y):
        """Get gym object at specified position"""
        return self.gym_objects.get((x, y))
    
    def get_gym_objects_by_type(self, object_type):
        """Get all gym objects of a specific type"""
        return [obj for pos, obj in self.gym_objects.items() 
                if self.object_types[pos] == object_type]
    
    def update_all(self, delta_time):
        """Update all gym objects"""
        for obj in self.gym_objects.values():
            obj.update(delta_time)
    
    def draw_all(self, screen, camera):
        """Draw all gym objects"""
        for pos, obj in self.gym_objects.items():
            try:
                obj.draw(screen, camera)
            except Exception as e:
                print(f"Error drawing gym object at {pos}: {e}")
    
    def get_collision_objects(self):
        """Get all gym objects for collision detection"""
        return [(pos, obj) for pos, obj in self.gym_objects.items()]
    
    def get_depth_sorted_objects(self):
        """Get gym objects sorted by depth for rendering order"""
        if not hasattr(self, '_depth_cache') or self._depth_cache_dirty:
            objects_with_depth = []
            for pos, obj in self.gym_objects.items():
                if hasattr(obj, 'get_depth_y'):
                    depth_y = obj.get_depth_y()
                else:
                    depth_y = obj.y + (obj.sprite_height // 2)
                objects_with_depth.append((depth_y, pos, obj))
            
            # Sort by depth (Y position)
            objects_with_depth.sort(key=lambda x: x[0])
            self._depth_cache = objects_with_depth
            self._depth_cache_dirty = False
        
        return self._depth_cache
    
    def tile_to_world_coords(self, tile_x, tile_y):
        """Convert tile coordinates to world coordinates"""
        return tile_x * 16 + 8, tile_y * 16 + 8
    
    def get_object_at_tile(self, tile_x, tile_y):
        """Get gym object at tile coordinates"""
        # Convert tile coordinates to world coordinates
        world_x, world_y = self.tile_to_world_coords(tile_x, tile_y)
        
        # Look for objects that are within this tile's bounds
        tile_left = tile_x * 16
        tile_top = tile_y * 16
        tile_right = tile_left + 16
        tile_bottom = tile_top + 16
        
        # Look for objects that are within this tile's bounds
        for pos, obj in self.gym_objects.items():
            obj_x, obj_y = pos
            # Check if object is within the tile bounds
            if (tile_left <= obj_x < tile_right and tile_top <= obj_y < tile_bottom):
                return obj
        # Fallback: try exact world coordinate match
        return self.get_gym_object(world_x, world_y)
    
    def setup_from_tilemap(self, tilemap):
        """Set up gym objects based on tilemap data"""
        # Clear existing objects
        self.gym_objects.clear()
        self.object_types.clear()
        self._depth_cache_dirty = True
        
        # Process layer 2 tiles to create gym objects
        for y, row in enumerate(tilemap.layer2_tiles):
            for x, tile_id in enumerate(row):
                if tile_id == -1:  # Skip empty tiles
                    continue
                
                # Convert tile coordinates to world coordinates
                world_x, world_y = self.tile_to_world_coords(x, y)
                
                # Create gym object based on tile ID
                if tile_id == 0:  # Regular bench
                    self.add_gym_object(world_x, world_y, "bench", bench_type="standard")
                elif tile_id == 1:  # Treadmill
            
                    self.add_gym_object(world_x, world_y, "treadmill", treadmill_type="v3")
                elif tile_id == 2:  # Dumbbell rack
                    self.add_gym_object(world_x, world_y, "dumbbell_rack")
                elif tile_id == 3:  # Small bench
                    self.add_gym_object(world_x, world_y, "bench", bench_type="small")
                elif tile_id == 4:  # Squat rack
                    print(f"SQUAT RACK: Adding at tile ({x}, {y}) -> world ({world_x}, {world_y})")
                    self.add_gym_object(world_x, world_y, "squat_rack")
                elif tile_id == 5:  # Front desk
                    self.add_gym_object(world_x, world_y, "front_desk")
                elif tile_id == 6:  # Trashcan
                    self.add_gym_object(world_x, world_y, "trashcan")
    
    def get_tiles_needing_interaction(self):
        """Get list of tile coordinates that need player interaction"""
        tiles_needing_interaction = []
        
        for (world_x, world_y), obj in self.gym_objects.items():
            # Convert world coordinates to tile coordinates
            tile_x = int(world_x // 16)
            tile_y = int(world_y // 16)
            
            # Only show red highlight if the attention icon is actually being displayed
            if hasattr(obj, '_needs_attention') and obj._needs_attention():
                tiles_needing_interaction.append((tile_x, tile_y))
        
        return tiles_needing_interaction
    
    def get_object_info(self):
        """Get information about all gym objects for debugging"""
        info = {}
        for pos, obj in self.gym_objects.items():
            obj_type = self.object_types[pos]
            if hasattr(obj, f'get_{obj_type}_info'):
                method = getattr(obj, f'get_{obj_type}_info')
                info[pos] = method()
            else:
                info[pos] = {
                    'type': obj_type,
                    'position': (obj.x, obj.y),
                    'occupied': obj.occupied,
                    'states': list(obj.states)
                }
        return info
    
    def toggle_hitboxes(self):
        """Toggle hitbox visibility for all gym objects"""
        self.show_hitboxes = not self.show_hitboxes
    
    def draw_hitboxes(self, screen, camera):
        """Draw hitboxes for all gym objects if enabled"""
        if not self.show_hitboxes:
            return
        
        for pos, obj in self.gym_objects.items():
            try:
                # Get the actual collision rectangle that the game uses
                collision_rect = obj.get_collision_rect()
                
                # Apply camera transformation using apply_rect for pygame.Rect objects
                screen_rect = camera.apply_rect(collision_rect)
                
                # Draw the hitbox (red outline)
                pygame.draw.rect(screen, (255, 0, 0), screen_rect, 2)
                
                # Draw hitbox center point
                center_x = screen_rect.centerx
                center_y = screen_rect.centery
                pygame.draw.circle(screen, (255, 0, 0), (center_x, center_y), 3)
                
            except Exception as e:
                print(f"Error drawing hitbox for gym object at {pos}: {e}")
    
    def is_mouse_over_floor_dumbbells(self, mouse_x, mouse_y, camera):
        """Check if mouse is hovering over any floor dumbbell sprites across all dumbbell racks"""
        for pos, obj in self.gym_objects.items():
            if hasattr(obj, 'is_mouse_over_floor_dumbbells'):
                if obj.is_mouse_over_floor_dumbbells(mouse_x, mouse_y, camera):
                    return True
        return False
    
    def pickup_floor_dumbbells(self, mouse_x, mouse_y, camera, player):
        """Pick up dumbbells from floor when right-clicked across all dumbbell racks"""
        for pos, obj in self.gym_objects.items():
            if hasattr(obj, 'pickup_floor_dumbbells'):
                if obj.pickup_floor_dumbbells(mouse_x, mouse_y, camera, player):
                    return True
        return False
    
    def is_mouse_over_floor_plates(self, mouse_x, mouse_y, camera):
        """Check if mouse is hovering over any floor plate sprites across all squat racks"""
        for pos, obj in self.gym_objects.items():
            if hasattr(obj, 'is_mouse_over_floor_plates'):
                if obj.is_mouse_over_floor_plates(mouse_x, mouse_y, camera):
                    return True
        return False
    
    def pickup_floor_plates(self, mouse_x, mouse_y, camera, player):
        """Pick up weight plates from floor when right-clicked across all squat racks"""
        for pos, obj in self.gym_objects.items():
            if hasattr(obj, 'pickup_floor_plates'):
                if obj.pickup_floor_plates(mouse_x, mouse_y, camera, player):
                    return True
        return False