import pygame

class UpgradePointManager:
    def __init__(self, x=50, y=100, star_size=32):
        self.x = x
        self.y = y
        self.star_size = star_size
        self.points = 0
        self.max_display_points = 10  # Maximum number of stars to display
        
        # Load star graphic
        try:
            self.star_image = pygame.image.load("Graphics/star.png")
            self.star_image = pygame.transform.scale(self.star_image, (self.star_size, self.star_size))
        except pygame.error:
            # Fallback if star.png is not found
            self.star_image = None
        
        # Font for point counter
        self.font = pygame.font.Font(None, 24)
        
    def add_point(self):
        """Add one upgrade point"""
        self.points += 1
        
    def spend_point(self):
        """Spend one upgrade point (returns True if successful, False if no points)"""
        if self.points > 0:
            self.points -= 1
            return True
        return False
        
    def get_points(self):
        """Get current number of upgrade points"""
        return self.points
        
    def set_points(self, points):
        """Set the number of upgrade points"""
        self.points = max(0, points)
        
    def draw(self, screen):
        """Draw the upgrade points display"""
        # Position star to the left of the time overlay (top-right corner)
        # Time overlay is positioned at screen.get_width() - 10, 10 with 2x scale
        # Position star with some spacing to the left of the time overlay
        star_x = screen.get_width() - 150  # Position well to the left of time overlay
        star_y = 90  # Lower than time overlay
        
        # Always draw the star (even when points = 0)
        if self.star_image:
            screen.blit(self.star_image, (star_x, star_y))
        else:
            # Fallback: draw a yellow circle if star image not found
            pygame.draw.circle(screen, (255, 255, 0), 
                             (star_x + self.star_size // 2, star_y + self.star_size // 2), 
                             self.star_size // 2)
            # Also draw a red rectangle as additional debug indicator
            pygame.draw.rect(screen, (255, 0, 0), (star_x, star_y, self.star_size, self.star_size), 2)
        
        # Draw total count number (always show, even when 0)
        count_text = str(self.points)
        count_surface = self.font.render(count_text, True, (255, 255, 255))
        count_rect = count_surface.get_rect()
        count_rect.topleft = (star_x + self.star_size + 5, star_y + (self.star_size - count_rect.height) // 2)
        screen.blit(count_surface, count_rect)
