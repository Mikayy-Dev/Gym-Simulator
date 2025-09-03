import pygame
import csv

class TileMap:
    def __init__(self, layer1_csv, layer2_csv, tile_size=16):
        self.tile_size = tile_size
        self.layer1_tiles = []
        self.layer2_tiles = []
        
        # Note: Sprite configuration and gym object handling moved to GymObjectManager
        # This class now only handles basic tile data
        
        # Load Layer 1 CSV data (16x16 tiles)
        with open(layer1_csv, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                self.layer1_tiles.append([int(tile_id) for tile_id in row])
        
        # Load Layer 2 CSV data (48x48 tiles)
        with open(layer2_csv, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                self.layer2_tiles.append([int(tile_id) for tile_id in row])
        
        self.width = len(self.layer1_tiles[0]) * tile_size
        self.height = len(self.layer1_tiles) * tile_size
        
        # Cache the floor and walls images for performance
        try:
            self.floor_image = pygame.image.load("Graphics/floor.png")
            self.walls_image = pygame.image.load("Graphics/walls.png")
        except:
            self.floor_image = None
            self.walls_image = None
        
        # Note: Animation manager and gym object setup moved to GymObjectManager
    
    def draw(self, screen, camera):
        """Main draw method - now only draws layer 1 (floor and walls)"""
        self.draw_layer1(screen, camera)
        # Note: Layer 2 (gym objects) are now drawn by GymObjectManager
    
    def draw_layer1(self, screen, camera):
        """Draw Layer 1 (16x16 tiles - floor and walls)"""
        for y, row in enumerate(self.layer1_tiles):
            for x, tile_id in enumerate(row):
                tile_x = x * self.tile_size
                tile_y = y * self.tile_size
                
                # Apply camera transform
                screen_x, screen_y = camera.apply_pos(tile_x, tile_y)
                scaled_tile_size = self.tile_size * camera.zoom
                
                # Create surface for the tile
                tile_surface = pygame.Surface((self.tile_size, self.tile_size))
                
                # Choose tile image based on ID and extract the specific sprite
                if tile_id == 46:
                    # Floor tile - extract from cached floor image
                    if self.floor_image:
                        sprite_x = (tile_id % 32) * self.tile_size
                        sprite_y = (tile_id // 32) * self.tile_size
                        tile_surface.blit(self.floor_image, (0, 0), (sprite_x, sprite_y, self.tile_size, self.tile_size))
                    else:
                        # Fallback: draw a colored rectangle
                        tile_surface.fill((100, 100, 100))
                else:
                    # Wall tile - extract from cached walls image
                    if self.walls_image:
                        sprite_x = (tile_id % 30) * self.tile_size
                        sprite_y = (tile_id // 30) * self.tile_size
                        tile_surface.blit(self.walls_image, (0, 0), (sprite_x, sprite_y, self.tile_size, self.tile_size))
                    else:
                        # Fallback: draw a colored rectangle
                        tile_surface.fill((150, 150, 150))
                
                # Scale the extracted sprite
                scaled_tile = pygame.transform.scale(tile_surface, (scaled_tile_size, scaled_tile_size))
                screen.blit(scaled_tile, (screen_x, screen_y))
    
    def is_collidable(self, tile_id):
        # Define collidable tile IDs - easy to modify
        collidable_ids = {882, 912, 853, 763, 793, 823, 883, 822, 732, 791,821, 851,761, 942}
        return tile_id in collidable_ids
    
    def toggle_hitbox_debug(self):
        """Toggle hitbox visualization on/off"""
        if not hasattr(self, 'show_hitboxes'):
            self.show_hitboxes = False
        self.show_hitboxes = not self.show_hitboxes
    
    def draw_hitbox_debug(self, screen, camera):
        """Draw hitboxes for debugging if enabled"""
        if not hasattr(self, 'show_hitboxes') or not self.show_hitboxes:
            return
        
        # Note: Gym object hitboxes are now drawn by the gym manager
        # This method only handles basic tile hitboxes if needed
    
    def is_within_player_range(self, tile_x, tile_y):
        """Check if a tile position is within the player's 5x5 interaction range"""
        if not hasattr(self, 'player') or not self.player:
            return False
        
        # Convert player position to tile coordinates (center of player sprite)
        # Player sprite is 16x32, so center is at (x + 8, y + 16)
        player_center_x = self.player.x + 8
        player_center_y = self.player.y + 16
        player_tile_x = int(player_center_x // self.tile_size)
        player_tile_y = int(player_center_y // self.tile_size)
        
        # Check if tile is within 5x5 radius (2 tiles in each direction from center)
        range_size = 2
        return (abs(tile_x - player_tile_x) <= range_size and 
                abs(tile_y - player_tile_y) <= range_size)
    
    def draw_tile_highlight(self, screen, camera):
        """Draw a highlight around the tile the mouse is currently over"""
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Convert screen coordinates to world coordinates
        world_x, world_y = camera.reverse_apply_pos(mouse_x, mouse_y)
        
        # Convert world coordinates to tile coordinates
        tile_x = int(world_x // self.tile_size)
        tile_y = int(world_y // self.tile_size)
        
        # Check bounds
        if (tile_y >= 0 and tile_y < len(self.layer1_tiles) and 
            tile_x >= 0 and tile_x < len(self.layer1_tiles[0])):
            
            # Only show highlight if tile is within player range
            if self.is_within_player_range(tile_x, tile_y):
                # Calculate tile position in world coordinates
                world_tile_x = tile_x * self.tile_size
                world_tile_y = tile_y * self.tile_size
                
                # Convert to screen coordinates
                screen_tile_x, screen_tile_y = camera.apply_pos(world_tile_x, world_tile_y)
                screen_tile_size = self.tile_size * camera.zoom
                
                # Create a semi-transparent highlight overlay
                highlight_surface = pygame.Surface((screen_tile_size, screen_tile_size), pygame.SRCALPHA)
                highlight_surface.fill((0, 0, 0, 51))  # Black with 20% opacity (51/255 ≈ 0.2)
                screen.blit(highlight_surface, (screen_tile_x, screen_tile_y))
                
                # Draw black frame around the tile
                highlight_rect = pygame.Rect(screen_tile_x, screen_tile_y, screen_tile_size, screen_tile_size)
                pygame.draw.rect(screen, (0, 0, 0), highlight_rect, 1)  # Black frame
