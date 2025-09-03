import pygame

class CollisionSystem:
    def __init__(self, tilemap, gym_manager=None):
        self.tilemap = tilemap
        self.gym_manager = gym_manager
    
    def set_gym_manager(self, gym_manager):
        """Set the gym manager for collision detection"""
        self.gym_manager = gym_manager
    
    def check_collision(self, x, y, hitboxes):
        # Check if position collides with walls or objects
        if not self.tilemap:
            return False
        
        # Check collision points around entity
        check_points = [
            (x + 8, y + 8),
            (x + 8, y + 24),
            (x + 4, y + 16),
            (x + 12, y + 16),
        ]
        
        # Check wall collisions
        for point_x, point_y in check_points:
            tile_x = int(point_x // 16)
            tile_y = int(point_y // 16)
            
            if tile_y < 0 or tile_y >= len(self.tilemap.layer1_tiles) or tile_x < 0 or tile_x >= len(self.tilemap.layer1_tiles[0]):
                return True
            
            tile_id = self.tilemap.layer1_tiles[tile_y][tile_x]
            if self.tilemap.is_collidable(tile_id):
                return True
        
        # Check gym object collisions using new manager
        if self.gym_manager and self._check_gym_object_collision(x, y, hitboxes):
            return True
        
        return False
    
    def can_move_to(self, new_x, new_y, hitboxes):
        # Check if entity can move to new position
        if self._check_wall_collision_hitbox(new_x, new_y, hitboxes):
            return False
        
        if self.gym_manager and self._check_gym_object_collision(new_x, new_y, hitboxes):
            return False
        
        return True
    
    def _check_wall_collision_hitbox(self, x, y, hitboxes):
        # Check wall collision using tile-based logic
        check_points = [
            (x + 8, y + 8),
            (x + 8, y + 24),
            (x + 4, y + 16),
            (x + 12, y + 16),
        ]
        
        for point_x, point_y in check_points:
            tile_x = int(point_x // 16)
            tile_y = int(point_y // 16)
            
            if tile_y < 0 or tile_y >= len(self.tilemap.layer1_tiles) or tile_x < 0 or tile_x >= len(self.tilemap.layer1_tiles[0]):
                return True
            
            tile_id = self.tilemap.layer1_tiles[tile_y][tile_x]
            if self.tilemap.is_collidable(tile_id):
                return True
        
        return False
    
    def _check_gym_object_collision(self, x, y, hitboxes):
        """Check collision with gym objects using new manager"""
        if not self.gym_manager:
            return False
        
        # Convert hitbox data to pygame.Rect objects
        hitbox_rects = self.get_hitbox_rects(x, y, hitboxes)
        
        # Check collision with each gym object
        for pos, obj in self.gym_manager.get_collision_objects():
            collision_rect = obj.get_collision_rect()
            for hitbox_rect in hitbox_rects:
                if hitbox_rect.colliderect(collision_rect):
                    return True
        
        return False
    
    def get_hitbox_rects(self, x, y, hitbox_data):
        """Convert hitbox data to pygame.Rect objects - handles both dict and list formats"""
        hitbox_rects = []
        
        # Handle dictionary format (from player.hitboxes)
        if isinstance(hitbox_data, dict):
            for hitbox_name, hitbox_info in hitbox_data.items():
                hitbox_rect = pygame.Rect(
                    x + hitbox_info["x"],
                    y + hitbox_info["y"],
                    hitbox_info["width"],
                    hitbox_info["height"]
                )
                hitbox_rects.append(hitbox_rect)
        
        # Handle list format (already converted hitbox rectangles)
        elif isinstance(hitbox_data, list):
            hitbox_rects = hitbox_data
        
        return hitbox_rects
