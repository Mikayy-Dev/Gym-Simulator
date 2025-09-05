import pygame
import math

class Entity:
    def __init__(self, x, y, spritesheet_path, scale=1.0, entity_id=None):
        # Position (x, y represent sprite center, not top-left)
        self.x = x
        self.y = y
        self.base_speed = 0.5
        self.speed = self.base_speed
        self.accumulated_x = 0.0
        self.accumulated_y = 0.0
        
        # Load and scale spritesheet
        self.full_sprite = pygame.image.load(spritesheet_path)
        self.scale = scale
        self.sprite_width = int(16 * scale)
        self.sprite_height = int(32 * scale)
        self.sprite = pygame.Surface((self.sprite_width, self.sprite_height))
        self.rect = self.sprite.get_rect()
        # Set rect position based on sprite center
        self.rect.x = x - (self.sprite_width // 2)
        self.rect.y = y - (self.sprite_height // 2)
        
        # Hitbox system
        self.hitboxes = {
            "body": {"x": 6 * scale, "y": 10 * scale, "width": 4 * scale, "height": 12 * scale},
            "feet": {"x": 4 * scale, "y": 22 * scale, "width": 8 * scale, "height": 6 * scale}
        }
        
        # Animation system
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 8
        self.direction = "down"
        self.moving = False
        
        # Entity identification
        self.entity_id = entity_id
        self.name = f"Entity_{entity_id}" if entity_id else "Entity"
        
        # Collision system
        self.tilemap = None
        self.collision_system = None
        
        # Debug options
        self.show_hitboxes = False
        self.pivot_offset = 4  # Offset for collision pivot point (lower than sprite center)
    
    def set_tilemap(self, tilemap):
        """Set the tilemap for collision detection"""
        self.tilemap = tilemap
        if hasattr(tilemap, 'collision_system'):
            self.collision_system = tilemap.collision_system
    
    def center_on_tile(self):
        """Position entity centered on tile for better pathfinding"""
        current_tile_x = int(self.x // 16)
        current_tile_y = int(self.y // 16)
        
        # Calculate position: center of tile
        pos_x = current_tile_x * 16 + 8  # Center horizontally (8 = 16/2)
        pos_y = current_tile_y * 16 + 8  # Center vertically
        
        # Update position (entity's x,y is now the sprite center)
        self.x = pos_x
        self.y = pos_y
        self.rect.x = pos_x - (self.sprite_width // 2)  # Top-left for rect
        self.rect.y = pos_y - (self.sprite_height // 2)  # Top-left for rect
    
    def check_collision(self, new_x, new_y):
        """Check if movement to new position would cause collision"""
        if not self.collision_system:
            return False
        
        # Use lower pivot point for collision detection (feet level)
        collision_x = new_x
        collision_y = new_y + self.pivot_offset  # Lower pivot point
        
        # Convert to top-left for collision
        rect_x = collision_x - (self.sprite_width // 2)
        rect_y = collision_y - (self.sprite_height // 2)
        
        hitbox_rects = self.collision_system.get_hitbox_rects(rect_x, rect_y, self.hitboxes)
        # Determine entity type - NPCs have npc_id, players don't
        entity_type = "npc" if hasattr(self, 'npc_id') else "player"
        return not self.collision_system.can_move_to(rect_x, rect_y, hitbox_rects, entity_type)
    
    def move_to(self, new_x, new_y):
        """Move entity to new position if no collision"""
        if not self.check_collision(new_x, new_y):
            self.x = new_x
            self.y = new_y
            # Update rect to match sprite center
            self.rect.x = new_x - (self.sprite_width // 2)
            self.rect.y = new_y - (self.sprite_height // 2)
            return True
        return False
    
    def update_animation(self, delta_time):
        """Update entity animation"""
        if self.moving:
            self.animation_timer += delta_time
            if self.animation_timer >= 1.0 / self.animation_speed:
                self.animation_frame = (self.animation_frame + 1) % 4
                self.animation_timer = 0
        else:
            self.animation_frame = 0
            self.animation_timer = 0
    
    def update(self, delta_time):
        """Base update method - should be overridden by subclasses"""
        self.update_animation(delta_time)
    
    def draw(self, screen, camera):
        """Base draw method - should be overridden by subclasses"""
        # Calculate screen position
        screen_x, screen_y = camera.apply_pos(self.x, self.y)
        scaled_width = self.sprite_width * camera.zoom
        scaled_height = self.sprite_height * camera.zoom
        
        # Extract current animation frame from spritesheet
        frame_width = 16
        frame_height = 32
        
        # Calculate frame position based on direction and animation frame
        if self.direction == "down":
            frame_x = self.animation_frame * frame_width
            frame_y = 0
        elif self.direction == "right":
            frame_x = (self.animation_frame + 4) * frame_width
            frame_y = 0
        elif self.direction == "up":
            frame_x = (self.animation_frame + 8) * frame_width
            frame_y = 0
        elif self.direction == "left":
            frame_x = (self.animation_frame + 12) * frame_width
            frame_y = 0
        
        # Ensure coordinates are within sprite sheet bounds
        sprite_width = self.full_sprite.get_width()
        sprite_height = self.full_sprite.get_height()
        
        if frame_x + frame_width > sprite_width or frame_y + frame_height > sprite_height:
            frame_x = 0
            frame_y = 0
        
        # Extract frame from spritesheet
        frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame_surface.blit(self.full_sprite, (0, 0), (frame_x, frame_y, frame_width, frame_height))
        
        # Scale frame to desired size
        scaled_frame = pygame.transform.scale(frame_surface, (scaled_width, scaled_height))
        
        # Draw on screen - center the sprite since self.x, self.y represents sprite center
        draw_x = screen_x - (scaled_width // 2)
        draw_y = screen_y - (scaled_height // 2)
        screen.blit(scaled_frame, (draw_x, draw_y))
        
        # Draw debug information if enabled
        if self.show_hitboxes:
            self._draw_debug_info(screen, camera)
    
    def _draw_debug_info(self, screen, camera):
        """Draw debug information for the entity"""
        # Draw pivot point dot (where self.x, self.y is located)
        pivot_screen_x, pivot_screen_y = camera.apply_pos(self.x, self.y)
        pygame.draw.circle(screen, (255, 0, 255), (int(pivot_screen_x), int(pivot_screen_y)), 3)  # Magenta dot for pivot point
        
        # Draw collision pivot point (feet level)
        collision_pivot_x, collision_pivot_y = camera.apply_pos(self.x, self.y + self.pivot_offset)
        pygame.draw.circle(screen, (255, 255, 0), (int(collision_pivot_x), int(collision_pivot_y)), 3)  # Yellow dot for collision pivot
    
    def get_position(self):
        """Get current position"""
        return (self.x, self.y)
    
    def set_position(self, x, y):
        """Set position and update rect"""
        self.x = x
        self.y = y
        self.rect.x = x - (self.sprite_width // 2)
        self.rect.y = y - (self.sprite_height // 2)
    
    def is_moving(self):
        """Check if entity is currently moving"""
        return self.moving
    
    def set_moving(self, moving):
        """Set movement state"""
        self.moving = moving
    
    def get_entity_info(self):
        """Get basic entity information for debugging"""
        return {
            'id': self.entity_id,
            'name': self.name,
            'position': (int(self.x), int(self.y)),
            'moving': self.moving,
            'direction': self.direction,
            'animation_frame': self.animation_frame
        }
