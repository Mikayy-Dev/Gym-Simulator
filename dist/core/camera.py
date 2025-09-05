import pygame

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.zoom = 3.0 
        self.x = 0
        self.y = 0
    
    def follow(self, target):
        # Center the camera on the target
        self.x = target.x - (self.width // (2 * self.zoom))
        self.y = target.y - (self.height // (2 * self.zoom))
    
    def apply(self, entity):
        # Use the actual sprite dimensions for proper scaling
        if hasattr(entity, 'get_current_sprite'):
            current_sprite = entity.get_current_sprite()
            sprite_width = current_sprite.get_width()
            sprite_height = current_sprite.get_height()
        elif hasattr(entity, 'sprite'):
            sprite_width = entity.sprite.get_width()
            sprite_height = entity.sprite.get_height()
        else:
            sprite_width = entity.rect.width
            sprite_height = entity.rect.height
        
        # Calculate screen position
        screen_x = (entity.x - self.x) * self.zoom
        screen_y = (entity.y - self.y) * self.zoom
        screen_width = sprite_width * self.zoom
        screen_height = sprite_height * self.zoom
        
        return pygame.Rect(screen_x, screen_y, screen_width, screen_height)
    
    def apply_pos(self, x, y):
        return ((x - self.x) * self.zoom, (y - self.y) * self.zoom)
    
    def reverse_apply_pos(self, screen_x, screen_y):
        """Convert screen coordinates back to world coordinates"""
        world_x = (screen_x / self.zoom) + self.x
        world_y = (screen_y / self.zoom) + self.y
        return (world_x, world_y)
    
    def apply_sprite(self, sprite):
        return pygame.transform.scale(sprite, (sprite.get_width() * self.zoom, sprite.get_height() * self.zoom))
    
    def apply_rect(self, world_rect):
        """Convert a world rectangle to screen coordinates"""
        screen_x = (world_rect.x - self.x) * self.zoom
        screen_y = (world_rect.y - self.y) * self.zoom
        screen_width = world_rect.width * self.zoom
        screen_height = world_rect.height * self.zoom
        return pygame.Rect(screen_x, screen_y, screen_width, screen_height)
