import pygame

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.zoom = 3.0 
        self.x = 0
        self.y = 0
    
    def follow(self, target):
        self.x = target.x - (self.width // (2 * self.zoom))
        self.y = target.y - (self.height // (2 * self.zoom))
    
    def apply(self, entity):
        return pygame.Rect(
            (entity.x - self.x) * self.zoom,
            (entity.y - self.y) * self.zoom,
            entity.rect.width * self.zoom,
            entity.rect.height * self.zoom
        )
    
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
