import pygame
from .collision import CollisionSystem

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_speed = 1
        self.sprint_multiplier = 1.6
        self.speed = self.base_speed
        self.accumulated_x = 0.0  # Track fractional movement
        self.accumulated_y = 0.0  # Track fractional movement
        self.full_sprite = pygame.image.load("Graphics/player_temp.png")
        self.sprite = pygame.Surface((16, 32))
        self.rect = self.sprite.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Stamina system
        self.max_stamina = 25
        self.current_stamina = self.max_stamina
        self.stamina_regen_rate = 25  # stamina per second
        self.sprint_stamina_drain = 40  # stamina per second
        self.stamina_timer = 0
        
        # Hitbox system - define collision areas relative to player position
        # Small, precise hitboxes for minimal collision detection
        self.hitboxes = {
            "body": {"x": 6, "y": 10, "width": 4, "height": 12},   # Main body hitbox (very small, centered)
            "feet": {"x": 4, "y": 22, "width": 8, "height": 6}     # Feet hitbox (very small, centered)
        }
        
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 8
        self.direction = "down"
        self.moving = False
        
        self.tilemap = None
        self.collision_system = None
        
        # Dumbbell inventory system
        self.dumbbell_count = 0
        
        # Weight plate inventory system
        self.weight_plate_count = 0
        self.weight_plate_sprite = pygame.image.load("Graphics/weight_plate.png")
        self.dumbbell_sprite = pygame.image.load("Graphics/dumbbellx16.png")
    
    def set_tilemap(self, tilemap):
        self.tilemap = tilemap
        # Initialize collision system
        from .collision import CollisionSystem
        self.collision_system = CollisionSystem(tilemap)
    
    def update_stamina(self, delta_time):
        """Update stamina based on current state"""
        if self.speed > self.base_speed:  # Sprinting
            self.current_stamina = max(0, self.current_stamina - self.sprint_stamina_drain * delta_time)
        else:  # Not sprinting
            self.current_stamina = min(self.max_stamina, self.current_stamina + self.stamina_regen_rate * delta_time)
    
    def draw_stamina_bar(self, screen, camera):
        """Draw stamina bar at bottom left of screen"""
        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = screen.get_height() - 40
        
        # Draw background bar
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # Draw stamina bar
        stamina_width = int((self.current_stamina / self.max_stamina) * bar_width)
        if stamina_width > 0:
            color = (0, 255, 0)  # Always green
            pygame.draw.rect(screen, color, (bar_x, bar_y, stamina_width, bar_height))
        
        # Draw border
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
    

    
    def check_collision(self, new_x, new_y):
        """Use the collision system's hybrid approach: tile-based for walls, hitbox-based for objects"""
        if not self.collision_system:
            return False
        
        # Pass the hitbox data directly to the collision system
        return not self.collision_system.can_move_to(new_x, new_y, self.hitboxes)
    
    def _check_hitbox_based_collision(self, x, y, hitboxes):
        """
        Check collision using PURE hitbox-based detection
        This completely bypasses tile boundaries and uses only hitbox collision
        """
        # Check multiple points around the player position for comprehensive collision detection
        # Cover all four faces: top, bottom, left, right
        check_points = [
            # Top face - check multiple points across the top edge
            (x + 6, y + 10),     # Top-left
            (x + 8, y + 10),     # Top-center  
            (x + 10, y + 10),    # Top-right
            
            # Bottom face - check multiple points across the bottom edge
            (x + 6, y + 22),     # Bottom-left
            (x + 8, y + 22),     # Bottom-center
            (x + 10, y + 22),    # Bottom-right
            
            # Left face - check multiple points along the left edge
            (x + 6, y + 10),     # Left-top
            (x + 6, y + 16),     # Left-center
            (x + 6, y + 22),     # Left-bottom
            
            # Right face - check multiple points along the right edge
            (x + 10, y + 10),    # Right-top
            (x + 10, y + 16),    # Right-center
            (x + 10, y + 22),    # Right-bottom
            
            # Center points for additional coverage
            (x + 8, y + 16),     # Center-center
        ]
        
        # PURE HITBOX-BASED COLLISION - NO TILE LOGIC
        for point_x, point_y in check_points:
            # Check if this point collides with any object using pure hitbox detection
            # This bypasses all tile-based logic and uses only hitbox rectangles
            if self._check_point_collision_pure_hitbox(point_x, point_y, hitboxes):
                return True
        
        return False  # No collision
    
    def _check_point_collision_pure_hitbox(self, point_x, point_y, player_hitboxes):
        """
        Check collision using ONLY hitbox detection - no tiles, no tile IDs
        This is pure hitbox-to-hitbox collision checking
        """
        # Create a tiny hitbox for the point we're checking
        point_hitbox = pygame.Rect(point_x, point_y, 1, 1)
        
        # Check collision with gym objects using the gym manager
        if hasattr(self, 'collision_system') and hasattr(self.collision_system, 'gym_manager') and self.collision_system.gym_manager:
            gym_manager = self.collision_system.gym_manager
            
            # Check collision with each gym object
            for pos, obj in gym_manager.get_collision_objects():
                collision_rect = obj.get_collision_rect()
                if collision_rect and point_hitbox.colliderect(collision_rect):
                    return True  # Collision detected
        else:
            # Fallback to old method if gym manager not available
            for tile_y in range(len(self.tilemap.layer2_tiles)):
                for tile_x in range(len(self.tilemap.layer2_tiles[0])):
                    object_tile_id = self.tilemap.layer2_tiles[tile_y][tile_x]
                    if object_tile_id >= 0:  # This tile has an object
                        # Create a simple hitbox for the tile
                        tile_hitbox = pygame.Rect(tile_x * 16, tile_y * 16, 16, 16)
                        if point_hitbox.colliderect(tile_hitbox):
                            return True  # Collision detected
        
        return False  # No collision
    
    def handle_input(self, keys):
        # Update speed based on shift key and stamina
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.current_stamina > 0:
            self.speed = self.base_speed * self.sprint_multiplier
        else:
            self.speed = self.base_speed
            
        self.moving = False
        new_x = self.x
        new_y = self.y
        
        # Handle horizontal movement
        if keys[pygame.K_a]:
            new_x = self.x - self.speed
            self.direction = "left"
            self.moving = True
        elif keys[pygame.K_d]:
            new_x = self.x + self.speed
            self.direction = "right"
            self.moving = True
        
        # Handle vertical movement
        if keys[pygame.K_w]:
            new_y = self.y - self.speed
            if not self.moving:
                self.direction = "up"
            self.moving = True
        elif keys[pygame.K_s]:
            new_y = self.y + self.speed
            if not self.moving:
                self.direction = "down"
            self.moving = True
        
        # Check collision and apply movement
        if self.moving:
            # Try to move in both directions
            can_move_x = not self.check_collision(new_x, self.y)
            can_move_y = not self.check_collision(self.x, new_y)
            

            
            # Apply movement based on what's possible
            if can_move_x:
                self.x = new_x
            if can_move_y:
                self.y = new_y
        
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Update animation
        self.update_animation()
    
    def add_dumbbells(self, amount):
        """Add dumbbells to player inventory"""
        self.dumbbell_count += amount
        print(f"Player picked up {amount} dumbbells. Total: {self.dumbbell_count}")
    
    def remove_dumbbells(self, amount):
        """Remove dumbbells from player inventory"""
        if self.dumbbell_count >= amount:
            self.dumbbell_count -= amount
            print(f"Player removed {amount} dumbbells. Total: {self.dumbbell_count}")
            return True
        return False
    
    def add_weight_plates(self, amount):
        """Add weight plates to player inventory"""
        self.weight_plate_count += amount
        print(f"Player picked up {amount} weight plates. Total: {self.weight_plate_count}")
    
    def remove_weight_plates(self, amount):
        """Remove weight plates from player inventory"""
        if self.weight_plate_count >= amount:
            self.weight_plate_count -= amount
            print(f"Player returned {amount} weight plates. Total: {self.weight_plate_count}")
            return True
        return False
    
    def get_dumbbell_count(self):
        """Get current dumbbell count"""
        return self.dumbbell_count
    
    def update_animation(self):
        """Update player animation"""
        if self.moving:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 4
        else:
            self.animation_frame = 0
            self.animation_timer = 0
    
    def get_current_sprite(self):
        if self.direction == "down":
            frame_x = self.animation_frame * 16
            frame_y = 0
        elif self.direction == "right":
            frame_x = (self.animation_frame + 4) * 16
            frame_y = 0
        elif self.direction == "up":
            frame_x = (self.animation_frame + 8) * 16
            frame_y = 0
        elif self.direction == "left":
            frame_x = (self.animation_frame + 12) * 16
            frame_y = 0
        
        # Ensure coordinates are within sprite sheet bounds
        sprite_width = self.full_sprite.get_width()
        sprite_height = self.full_sprite.get_height()
        
        if frame_x + 16 > sprite_width or frame_y + 32 > sprite_height:
            # Fallback to first frame if out of bounds
            frame_x = 0
            frame_y = 0
        
        self.sprite = pygame.Surface((16, 32), pygame.SRCALPHA)
        self.sprite.blit(self.full_sprite, (0, 0), (frame_x, frame_y, 16, 32))
        return self.sprite
    
    def draw(self, screen):
        current_sprite = self.get_current_sprite()
        screen.blit(current_sprite, self.rect)
    
    def draw_dumbbell_inventory(self, screen, camera):
        """Draw dumbbell inventory display under the player"""
        if self.dumbbell_count > 0:
            # Get the player's screen position using the same method as the game loop
            player_rect = camera.apply(self)
            screen_x = player_rect.x + player_rect.width // 2
            screen_y = player_rect.y + player_rect.height
            
            # Scale the dumbbell icon to 1.5x size
            scale_factor = 1.5
            scaled_width = int(self.dumbbell_sprite.get_width() * scale_factor)
            scaled_height = int(self.dumbbell_sprite.get_height() * scale_factor)
            
            # Create scaled sprite
            scaled_sprite = pygame.transform.scale(self.dumbbell_sprite, (scaled_width, scaled_height))
            
            # Position scaled dumbbell icon under the player
            icon_x = screen_x - (scaled_width // 2)
            icon_y = screen_y + 2  # Position below the player sprite
            
            # Draw the scaled dumbbell icon
            screen.blit(scaled_sprite, (icon_x, icon_y))
            
            # Draw the count text
            font = pygame.font.Font(None, 16)
            count_text = font.render(str(self.dumbbell_count), True, (255, 255, 255))
            
            # Position count text below the scaled icon
            text_x = icon_x + (scaled_width // 2) - (count_text.get_width() // 2)
            text_y = icon_y + scaled_height + 2
            
            # Draw count text
            screen.blit(count_text, (text_x, text_y))
    
    def draw_weight_plate_inventory(self, screen, camera):
        """Draw weight plate inventory display under the player"""
        if self.weight_plate_count > 0:
            # Get the player's screen position using the same method as the game loop
            player_rect = camera.apply(self)
            screen_x = player_rect.x + player_rect.width // 2
            screen_y = player_rect.y + player_rect.height
            
            # Scale the weight plate icon to 1.5x size
            scale_factor = 1.5
            scaled_width = int(self.weight_plate_sprite.get_width() * scale_factor)
            scaled_height = int(self.weight_plate_sprite.get_height() * scale_factor)
            
            # Create scaled sprite
            scaled_sprite = pygame.transform.scale(self.weight_plate_sprite, (scaled_width, scaled_height))
            
            # Position scaled weight plate icon under the player (offset to the right of dumbbells)
            icon_x = screen_x - (scaled_width // 2) + 20  # Offset 20 pixels to the right
            icon_y = screen_y + 2  # Position below the player sprite
            
            # Draw the scaled weight plate icon
            screen.blit(scaled_sprite, (icon_x, icon_y))
            
            # Draw the count text
            font = pygame.font.Font(None, 16)
            count_text = font.render(str(self.weight_plate_count), True, (255, 255, 255))
            
            # Position count text below the scaled icon
            text_x = icon_x + (scaled_width // 2) - (count_text.get_width() // 2)
            text_y = icon_y + scaled_height + 2
            
            # Draw count text
            screen.blit(count_text, (text_x, text_y))
