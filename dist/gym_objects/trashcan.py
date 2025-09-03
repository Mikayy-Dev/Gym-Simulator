import pygame
from gym_objects.base_object import GymObject

class Trashcan(GymObject):
    def __init__(self, x, y, scale=1.0):
        spritesheet_path = "Graphics/trash-can.png"
        
        super().__init__(x, y, spritesheet_path, scale)
        
        self.sprite_width = int(16 * scale)
        self.sprite_height = int(35 * scale)
        
        self.rect = pygame.Rect(x, y, self.sprite_width, self.sprite_height)
        self.hitboxes = {
            "body": {"x": 0, "y": 0, "width": self.sprite_width, "height": self.sprite_height}
        }
        
        self.set_custom_hitbox(16, 12, 0, 4)
        
        collision_rect = self.get_collision_rect()
        self.depth_y = collision_rect.bottom
    
    def get_depth_y(self):
        return self.depth_y
    
    def is_available(self):
        return True
    
    def start_interaction(self, npc):
        return False
