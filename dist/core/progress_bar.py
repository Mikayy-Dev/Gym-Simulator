import pygame

class ProgressBar:
    def __init__(self, x=50, y=50, width=200, height=20, max_progress=100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_progress = max_progress
        self.current_progress = 0
        self.level = 1
        self.base_requirement = 100
        self.is_charging = False  # Whether player is currently doing tasks
        self.last_activity_time = 0
        self.activity_timeout = 2000  # 2 seconds of inactivity before decay starts
        self.base_charge_rate = 3.0  # Base charge rate (reduced from 6.0)
        self.base_decay_rate = 1.0  # Base decay rate (reduced from 2.0)
        self.charge_rate = self.base_charge_rate  # Current charge rate
        self.decay_rate = self.base_decay_rate  # Current decay rate
        
        # Colors
        self.bg_color = (50, 50, 50)
        self.fill_color = (0, 255, 0)
        self.charge_color = (0, 255, 255)  # Cyan when charging
        self.border_color = (255, 255, 255)
        
    def start_charging(self):
        """Start charging the progress bar - called when player does a task"""
        self.is_charging = True
        self.last_activity_time = pygame.time.get_ticks()
    
    def stop_charging(self):
        """Stop charging the progress bar - called when player stops doing tasks"""
        self.is_charging = False
    
    def update(self, delta_time):
        """Update charge bar (handle charging and decay)"""
        current_time = pygame.time.get_ticks()
        time_since_activity = current_time - self.last_activity_time
        
        # Check if we should stop charging due to timeout
        if self.is_charging and time_since_activity >= self.activity_timeout:
            self.is_charging = False
        
        # Handle charging/decay based on activity state
        if self.is_charging:
            # Charging while actively doing tasks
            charge_amount = self.charge_rate * delta_time
            self.current_progress += charge_amount
            
            # Check if bar is full and needs to level up
            if self.current_progress >= self.max_progress:
                self.level_up()
        else:
            # Decaying when not charging
            decay_amount = self.decay_rate * delta_time
            self.current_progress = max(self.current_progress - decay_amount, 0)
    
    def draw(self, screen):
        """Draw the charge bar"""
        # Scale factors for overlay (smaller than stamina bar)
        scale_factor = 1.5
        scaled_width = self.width * scale_factor
        scaled_height = self.height * scale_factor
        
        # Draw fill (scaled with padding)
        if self.current_progress > 0:
            padding = 6  # Slightly less padding for smaller bar
            fill_width = int((self.current_progress / self.max_progress) * (scaled_width - padding * 2))
            fill_rect = pygame.Rect(self.x + padding, self.y + padding, fill_width, scaled_height - padding * 2)
            
            # Change color based on charging state
            if self.is_charging:
                # Cyan when charging
                fill_color = self.charge_color
            else:
                # Green when stable/decaying
                fill_color = self.fill_color
            
            pygame.draw.rect(screen, fill_color, fill_rect)
        
        # Overlay stamina bar image
        try:
            stamina_bar_image = pygame.image.load("Graphics/stamina_bar.png")
            stamina_bar_image = pygame.transform.scale(stamina_bar_image, (scaled_width, scaled_height))
            screen.blit(stamina_bar_image, (self.x, self.y))
        except pygame.error:
            pass
        
        # Draw progress text with charge indicator (adjusted for scaled bar)
        try:
            font = pygame.font.Font("Font/Retro Gaming.ttf", 16)
        except:
            font = pygame.font.Font(None, 16)
        
        charge_text = "CHARGING" if self.is_charging else "DECAYING"
        progress_text = f"{int(self.current_progress)}/{self.max_progress}"
        level_text = f"Tier {self.level}"
        
        # Draw charge indicator
        charge_surface = font.render(charge_text, True, self.charge_color if self.is_charging else (255, 100, 100))
        charge_rect = charge_surface.get_rect()
        charge_rect.topleft = (self.x, self.y - 20)
        screen.blit(charge_surface, charge_rect)
        
        # Draw level text
        level_surface = font.render(level_text, True, (255, 255, 0))
        level_rect = level_surface.get_rect()
        level_rect.topleft = (self.x, self.y - 40)
        screen.blit(level_surface, level_rect)
        
        # Draw progress numbers (centered on scaled bar)
        text_surface = font.render(progress_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = (self.x + scaled_width // 2, self.y + scaled_height // 2)
        screen.blit(text_surface, text_rect)
    
    def get_progress_percentage(self):
        """Get current progress as percentage (0-100)"""
        return (self.current_progress / self.max_progress) * 100
    
    def is_full(self):
        """Check if progress bar is full"""
        return self.current_progress >= self.max_progress
    
    def is_empty(self):
        """Check if progress bar is empty"""
        return self.current_progress <= 0
    
    def is_charging(self):
        """Check if progress bar is currently charging"""
        return self.is_charging
    
    def get_charge_percentage(self):
        """Get current charge as percentage (0-100)"""
        return (self.current_progress / self.max_progress) * 100
    
    def level_up(self):
        """Level up the progress bar - reset progress and increase requirement"""
        self.level += 1
        self.current_progress = 0
        self.max_progress = self.base_requirement * self.level
        
        # Increase both charge and decay rates
        self.charge_rate = self.base_charge_rate * self.level
        self.decay_rate = self.base_decay_rate * self.level
        
        # Award skill points based on level progression
        if hasattr(self, 'upgrade_point_manager') and self.upgrade_point_manager:
            points_to_award = self._get_skill_points_for_level(self.level)
            for _ in range(points_to_award):
                self.upgrade_point_manager.add_point()
    
    def _get_skill_points_for_level(self, level):
        """Get the number of skill points to award for reaching a specific level"""
        if level == 2:
            return 1
        elif level == 4:
            return 1
        elif level == 6:
            return 2
        elif level == 8:
            return 2
        elif level == 10:
            return 3
        else:
            return 0  # No points for other levels
    
    def set_upgrade_point_manager(self, upgrade_point_manager):
        """Set the upgrade point manager to award points to"""
        self.upgrade_point_manager = upgrade_point_manager
    
    def reset(self):
        """Reset the progress bar to initial state"""
        self.current_progress = 0
        self.level = 1
        self.max_progress = self.base_requirement
        self.is_charging = False
        self.last_activity_time = 0
        self.charge_rate = self.base_charge_rate
        self.decay_rate = self.base_decay_rate