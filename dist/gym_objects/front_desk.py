import pygame
from gym_objects.base_object import GymObject

class FrontDesk(GymObject):
    def __init__(self, x, y, scale=1.0):
        spritesheet_path = "Graphics/front_desk.png"
        
        super().__init__(x, y, spritesheet_path, scale)
        
        self.sprite_width = int(64 * scale)
        self.sprite_height = int(64 * scale)
        
        self.rect = pygame.Rect(x, y, self.sprite_width, self.sprite_height)
        self.hitboxes = {
            "body": {"x": 0, "y": 0, "width": self.sprite_width, "height": self.sprite_height}
        }
        
        self.interaction_duration = 3.0
        
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.3
        self.animation_frames = [0, 1, 2, 3]
        
        self.set_custom_hitbox(64, 8, 0, -24)
        
        collision_rect = self.get_collision_rect()
        self.depth_y = collision_rect.bottom
    
    def get_depth_y(self):
        return self.depth_y
    
    def start_interaction(self, npc):
        if super().start_interaction(npc):
            self.interaction_duration = 3.0
            self._notify_pathfinding_update()
            return True
        return False
    
    def update(self, delta_time):
        super().update(delta_time)
        
        if self.occupied:
            self.animation_timer += delta_time
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % len(self.animation_frames)
    
    def draw(self, screen, camera):
        if self.occupied:
            frame = self.animation_frames[self.animation_frame]
        else:
            frame = 0
        
        if self._cached_sprite is None or self._cached_scale != self.scale or self._cached_zoom != camera.zoom:
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
        
        screen_x, screen_y = camera.apply_pos(self.x, self.y)
        draw_x = screen_x - (self._cached_sprite.get_width() // 2)
        draw_y = screen_y - (self._cached_sprite.get_height() // 2)
        
        screen.blit(self._cached_sprite, (draw_x, draw_y))
    
    def _notify_pathfinding_update(self):
        pass
    
    def get_front_desk_info(self):
        return {
            'type': 'front_desk',
            'position': (self.x, self.y),
            'occupied': self.occupied,
            'states': list(self.states)
        }
