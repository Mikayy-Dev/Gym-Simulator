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
        if self.points == 0:
            return  # Don't draw anything if no points
        
        # Draw single star
        if self.star_image:
            screen.blit(self.star_image, (self.x, self.y))
        else:
            # Fallback: draw a yellow circle if star image not found
            pygame.draw.circle(screen, (255, 255, 0), 
                             (self.x + self.star_size // 2, self.y + self.star_size // 2), 
                             self.star_size // 2)
        
        # Draw total count number
        count_text = str(self.points)
        count_surface = self.font.render(count_text, True, (255, 255, 255))
        count_rect = count_surface.get_rect()
        count_rect.topleft = (self.x + self.star_size + 5, self.y + (self.star_size - count_rect.height) // 2)
        screen.blit(count_surface, count_rect)
