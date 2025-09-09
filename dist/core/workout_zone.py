import pygame

class WorkoutZone:
    def __init__(self, x, y, width, height, zone_type="dumbbell"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.zone_type = zone_type
        self.rect = pygame.Rect(x, y, width, height)
    
    def contains_point(self, x, y):
        return self.rect.collidepoint(x, y)
    
    def contains_tile(self, tile_x, tile_y, tile_size=16):
        tile_left = tile_x * tile_size
        tile_top = tile_y * tile_size
        tile_right = tile_left + tile_size
        tile_bottom = tile_top + tile_size
        
        return (self.rect.left <= tile_left and 
                self.rect.right >= tile_right and 
                self.rect.top <= tile_top and 
                self.rect.bottom >= tile_bottom)
    
    def draw_debug(self, screen, camera):
        screen_x, screen_y = camera.apply_pos(self.x, self.y)
        scaled_width = self.width * camera.zoom
        scaled_height = self.height * camera.zoom
        
        debug_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        debug_surface.fill((0, 255, 0, 50))
        screen.blit(debug_surface, (screen_x, screen_y))

class WorkoutZoneManager:
    def __init__(self):
        self.zones = []
    
    def add_zone(self, x, y, width, height, zone_type="dumbbell"):
        zone = WorkoutZone(x, y, width, height, zone_type)
        self.zones.append(zone)
        return zone
    
    def is_in_workout_zone(self, x, y, zone_type="dumbbell"):
        for zone in self.zones:
            if zone.zone_type == zone_type and zone.contains_point(x, y):
                return True
        return False
    
    def is_tile_in_workout_zone(self, tile_x, tile_y, zone_type="dumbbell", tile_size=16):
        for zone in self.zones:
            if zone.zone_type == zone_type and zone.contains_tile(tile_x, tile_y, tile_size):
                return True
        return False
    
    def get_zones_by_type(self, zone_type):
        return [zone for zone in self.zones if zone.zone_type == zone_type]
    
    def draw_debug(self, screen, camera):
        for zone in self.zones:
            zone.draw_debug(screen, camera)
