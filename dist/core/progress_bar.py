import pygame

class ProgressBar:
    def __init__(self, x=50, y=50, width=200, height=20, max_progress=100, difficulty_scaler=None, npc_happiness=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_progress = max_progress
        self.current_progress = 0
        self.level = 1
        self.base_requirement = 100
        self.is_charging = False
        self.last_activity_time = 0
        self.recent_event_label_ms = 400
        self.difficulty_scaler = difficulty_scaler
        self.npc_happiness = npc_happiness
        
        # Colors
        self.bg_color = (50, 50, 50)
        self.fill_color = (0, 255, 0)
        self.charge_color = (0, 255, 255)  # Cyan when charging
        self.border_color = (255, 255, 255)
        
    def start_charging(self, amount: float = 15.0, action: str = "Task completed"):
        """Apply an immediate progress increment for an event."""
        self.is_charging = True
        self.last_activity_time = pygame.time.get_ticks()
        
        # Apply difficulty scaling to XP amount
        scaled_amount = float(amount)
        if self.difficulty_scaler:
            # Get current difficulty multiplier (time + performance based)
            difficulty_multiplier = self.difficulty_scaler.get_time_multiplier()
            # Scale XP based on difficulty - higher difficulty = more XP
            scaled_amount *= difficulty_multiplier
        
        self.current_progress += scaled_amount
        
        # Add chat log message for XP earned with action description
        if self.npc_happiness:
            xp_message = f"{action}: +{int(scaled_amount)} XP"
            self.npc_happiness._add_chat_log_entry(xp_message)
        
        if self.current_progress >= self.max_progress:
            self.level_up()
    
    def stop_charging(self):
        """Stop charging the progress bar - called when player stops doing tasks"""
        self.is_charging = False
    
    def update(self, delta_time):
        """No passive charge/decay; only clear the charging label after a short delay."""
        current_time = pygame.time.get_ticks()
        if self.is_charging and (current_time - self.last_activity_time) >= self.recent_event_label_ms:
            self.is_charging = False
        # Clamp bounds
        if self.current_progress < 0:
            self.current_progress = 0
        # level_up already clamps when crossing max; otherwise allow exceeding until level_up is called
    
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
                fill_color = self.charge_color
            else:
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
        
        charge_text = "CHARGING" if self.is_charging else ""
        progress_text = f"{int(self.current_progress)}/{self.max_progress}"
        level_text = f"Tier {self.level}"
        
        # Draw charge indicator
        if charge_text:
            charge_surface = font.render(charge_text, True, self.charge_color)
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
    
    # Removed ambiguous is_charging() accessor to avoid name collision with attribute
    
    def get_charge_percentage(self):
        """Get current charge as percentage (0-100)"""
        return (self.current_progress / self.max_progress) * 100
    
    def level_up(self):
        """Level up the progress bar - reset progress and increase requirement"""
        self.level += 1
        self.current_progress = 0
        self.max_progress = self.base_requirement * self.level
        
        # Award skill points based on level progression
        if hasattr(self, 'upgrade_point_manager') and self.upgrade_point_manager:
            points_to_award = self._get_skill_points_for_level(self.level)
            for _ in range(points_to_award):
                self.upgrade_point_manager.add_point()
    
    def _get_skill_points_for_level(self, level):
        """Get the number of skill points to award for reaching a specific level"""
        return 1  # 1 skill point per level
    
    def set_upgrade_point_manager(self, upgrade_point_manager):
        """Set the upgrade point manager to award points to"""
        self.upgrade_point_manager = upgrade_point_manager
    
    def set_difficulty_scaler(self, difficulty_scaler):
        """Set the difficulty scaler for XP scaling"""
        self.difficulty_scaler = difficulty_scaler
    
    def reset(self):
        """Reset the progress bar to initial state"""
        self.current_progress = 0
        self.level = 1
        self.max_progress = self.base_requirement
        self.is_charging = False
        self.last_activity_time = 0