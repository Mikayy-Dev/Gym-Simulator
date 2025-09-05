"""
Render System
Handles all rendering operations and camera management
"""

import pygame
from core.camera import Camera

class RenderSystem:
    """Manages all rendering operations"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.camera = None
        self.render_queue = []
    
    def set_camera(self, camera: Camera):
        """Set the camera for rendering"""
        self.camera = camera
    
    def clear_screen(self, color: tuple = (0, 0, 0)):
        """Clear the screen with specified color"""
        self.screen.fill(color)
    
    def draw_sprite(self, sprite: pygame.Surface, position: tuple, scale: float = 1.0):
        """Draw a sprite at the given position"""
        if self.camera:
            screen_pos = self.camera.apply_pos(position[0], position[1])
            scaled_sprite = self.camera.apply_sprite(sprite)
            self.screen.blit(scaled_sprite, screen_pos)
        else:
            self.screen.blit(sprite, position)
    
    def draw_rect(self, rect: pygame.Rect, color: tuple, width: int = 0):
        """Draw a rectangle"""
        if self.camera:
            screen_rect = self.camera.apply_rect(rect)
            pygame.draw.rect(self.screen, color, screen_rect, width)
        else:
            pygame.draw.rect(self.screen, color, rect, width)
    
    def draw_circle(self, center: tuple, radius: int, color: tuple, width: int = 0):
        """Draw a circle"""
        if self.camera:
            screen_center = self.camera.apply_pos(center[0], center[1])
            pygame.draw.circle(self.screen, color, screen_center, radius, width)
        else:
            pygame.draw.circle(self.screen, color, center, radius, width)
    
    def draw_text(self, text: str, position: tuple, font: pygame.font.Font, color: tuple = (255, 255, 255)):
        """Draw text at the given position"""
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, position)
    
    def add_to_render_queue(self, item: dict):
        """Add an item to the render queue for depth sorting"""
        self.render_queue.append(item)
    
    def sort_render_queue(self):
        """Sort render queue by depth (Y position)"""
        self.render_queue.sort(key=lambda item: item.get('depth', 0))
    
    def render_queue(self):
        """Render all items in the queue"""
        for item in self.render_queue:
            if item['type'] == 'sprite':
                self.draw_sprite(item['sprite'], item['position'], item.get('scale', 1.0))
            elif item['type'] == 'rect':
                self.draw_rect(item['rect'], item['color'], item.get('width', 0))
            elif item['type'] == 'circle':
                self.draw_circle(item['center'], item['radius'], item['color'], item.get('width', 0))
            elif item['type'] == 'text':
                self.draw_text(item['text'], item['position'], item['font'], item.get('color', (255, 255, 255)))
        
        self.render_queue.clear()
    
    def present(self):
        """Present the rendered frame"""
        pygame.display.flip()
