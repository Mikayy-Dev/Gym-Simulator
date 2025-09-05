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
        
        self.set_custom_hitbox(16, 10, 0, 4)
        
        # Set interaction hitbox for player clicks (full sprite dimensions for easier clicking)
        self.set_interaction_hitbox(self.sprite_width, self.sprite_height, offset_x=0, offset_y=0)
        
        collision_rect = self.get_collision_rect()
        self.depth_y = collision_rect.bottom
    
    def get_depth_y(self):
        return self.depth_y
    
    def is_available(self):
        return True
    
    def start_interaction(self, npc):
        return False
    
    def draw(self, screen, camera):
        """Draw trashcan using base class method for proper dimensions"""
        super().draw(screen, camera)