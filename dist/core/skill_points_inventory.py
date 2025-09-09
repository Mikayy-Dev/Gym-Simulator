import pygame
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT

class SkillPointsInventory:
    def __init__(self, upgrade_point_manager=None, player=None):
        self.is_open = False
        self.clipboard_image = None
        self.font = None
        self.title_font = None
        self.game_paused = False
        self.upgrade_point_manager = upgrade_point_manager
        self.player = player
        
        # Menu positioning
        self.menu_width = 400
        self.menu_height = 500
        self.menu_x = (SCREEN_WIDTH - self.menu_width) // 2
        self.menu_y = (SCREEN_HEIGHT - self.menu_height) // 2
        
        # Skill categories
        self.skills = {
            "Speed": 0,
            "Endurance": 0,
            "Management": 0
        }
        
        # Button properties
        self.button_width = 80
        self.button_height = 30
        self.button_spacing = 40
        self.skill_buttons = {}
        self.hovered_button = None
        self.feedback_message = ""
        self.feedback_timer = 0
        
        self._load_assets()
    
    def _load_assets(self):
        """Load required assets"""
        try:
            self.clipboard_image = pygame.image.load("Graphics/clipboard.png").convert_alpha()
            # Scale the clipboard up by 3x
            original_width = self.clipboard_image.get_width()
            original_height = self.clipboard_image.get_height()
            self.clipboard_image = pygame.transform.scale(self.clipboard_image, (original_width * 3, original_height * 3))
            
            # Set menu dimensions to the scaled size
            self.menu_width = self.clipboard_image.get_width()
            self.menu_height = self.clipboard_image.get_height()
            # Recalculate menu position based on actual size
            self.menu_x = (SCREEN_WIDTH - self.menu_width) // 2
            self.menu_y = (SCREEN_HEIGHT - self.menu_height) // 2
        except pygame.error as e:
            # Create a fallback surface
            self.clipboard_image = pygame.Surface((self.menu_width, self.menu_height), pygame.SRCALPHA)
            pygame.draw.rect(self.clipboard_image, (200, 200, 200), (0, 0, self.menu_width, self.menu_height))
            pygame.draw.rect(self.clipboard_image, (100, 100, 100), (0, 0, self.menu_width, self.menu_height), 3)
        
        try:
            self.font = pygame.font.Font("Font/Retro Gaming.ttf", 24)
            self.title_font = pygame.font.Font("Font/Retro Gaming.ttf", 32)
        except:
            self.font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 32)
    
    def toggle(self):
        """Toggle the inventory menu"""
        self.is_open = not self.is_open
        self.game_paused = self.is_open
    
    def open(self):
        """Open the inventory menu"""
        self.is_open = True
        self.game_paused = True
    
    def close(self):
        """Close the inventory menu"""
        self.is_open = False
        self.game_paused = False
    
    def add_skill_points(self, points):
        """Add skill points to the inventory"""
        if self.upgrade_point_manager:
            for _ in range(points):
                self.upgrade_point_manager.add_point()
    
    def spend_skill_points(self, skill_name, points):
        """Spend skill points on a skill"""
        if (self.upgrade_point_manager and 
            self.upgrade_point_manager.get_points() >= points and 
            skill_name in self.skills and
            self.skills[skill_name] + points <= 5):  # Max level 5
            
            for _ in range(points):
                if not self.upgrade_point_manager.spend_point():
                    return False
            
            self.skills[skill_name] += points
            
            # Update player skill levels
            if self.player:
                self.player.update_skill_levels(
                    self.skills["Speed"],
                    self.skills["Endurance"],
                    self.skills["Management"]
                )
                
                # Ensure tilemap has the updated player reference
                if hasattr(self.player, 'tilemap') and self.player.tilemap:
                    self.player.tilemap.set_player(self.player)
                    # Also ensure the player's tilemap reference is correct
                    if hasattr(self.player.tilemap, 'player'):
                        self.player.tilemap.player = self.player
            
            return True
        return False
    
    def get_available_points(self):
        """Get the number of available skill points"""
        if self.upgrade_point_manager:
            return self.upgrade_point_manager.get_points()
        return 0
    
    def get_management_level(self):
        """Get the current management skill level for NPC happiness system"""
        return self.skills.get("Management", 0)
    
    def set_player(self, player):
        """Update the player reference and ensure tilemap is updated"""
        self.player = player
        if player and hasattr(player, 'tilemap') and player.tilemap:
            player.tilemap.set_player(player)
    
    def _create_skill_buttons(self):
        """Create button rectangles for each skill"""
        center_x = self.menu_x + self.menu_width // 2
        y_offset = 225
        
        for skill_name in self.skills.keys():
            button_x = center_x + 100  # Position to the right of skill text
            button_y = self.menu_y + y_offset - 15  # Center vertically with text
            self.skill_buttons[skill_name] = pygame.Rect(button_x, button_y, self.button_width, self.button_height)
            y_offset += self.button_spacing
    
    def _is_button_clicked(self, mouse_x, mouse_y, skill_name):
        """Check if a skill button was clicked"""
        if skill_name in self.skill_buttons:
            return self.skill_buttons[skill_name].collidepoint(mouse_x, mouse_y)
        return False
    
    def _can_upgrade_skill(self, skill_name):
        """Check if a skill can be upgraded"""
        return (self.get_available_points() > 0 and 
                self.skills[skill_name] < 5)
    
    def _show_feedback(self, message):
        """Show a feedback message for 2 seconds"""
        self.feedback_message = message
        self.feedback_timer = 120  # 2 seconds at 60 FPS
    
    def update(self):
        """Update the inventory (call this every frame)"""
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
            if self.feedback_timer <= 0:
                self.feedback_message = ""
    
    def handle_input(self, event):
        """Handle input events when menu is open"""
        if not self.is_open:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                self.close()
                return True
        elif event.type == pygame.MOUSEMOTION:
            # Handle mouse hover
            mouse_x, mouse_y = event.pos
            self.hovered_button = None
            for skill_name in self.skills.keys():
                if self._is_button_clicked(mouse_x, mouse_y, skill_name):
                    self.hovered_button = skill_name
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                
                # Check if clicking outside menu
                if self._is_click_outside_menu(mouse_x, mouse_y):
                    self.close()
                    return True
                
                # Check skill button clicks
                for skill_name in self.skills.keys():
                    if self._is_button_clicked(mouse_x, mouse_y, skill_name):
                        if self._can_upgrade_skill(skill_name):
                            if self.spend_skill_points(skill_name, 1):
                                self._show_feedback(f"{skill_name} upgraded!")
                                # Don't return True here - let other input be processed
                                return False
                        else:
                            if self.get_available_points() == 0:
                                self._show_feedback("Not enough points!")
                            elif self.skills[skill_name] >= 5:
                                self._show_feedback(f"{skill_name} is max level!")
                        break
        
        return False
    
    def _is_click_outside_menu(self, mouse_x, mouse_y):
        """Check if click is outside the menu area"""
        return (mouse_x < self.menu_x or mouse_x > self.menu_x + self.menu_width or
                mouse_y < self.menu_y or mouse_y > self.menu_y + self.menu_height)
    
    def draw(self, screen):
        """Draw the skill points inventory menu"""
        if not self.is_open:
            return
        
        # Create buttons if they don't exist
        if not self.skill_buttons:
            self._create_skill_buttons()
        
        # Draw semi-transparent background overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Draw clipboard background
        screen.blit(self.clipboard_image, (self.menu_x, self.menu_y))
        
        # Calculate text positioning based on actual clipboard size
        center_x = self.menu_x + self.menu_width // 2
        
        # Draw title
        title_text = self.title_font.render("SKILL POINTS", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(center_x, self.menu_y + 145))
        screen.blit(title_text, title_rect)
        
        # Draw available skill points
        available_points = self.get_available_points()
        points_text = self.font.render(f"Available Points: {available_points}", True, (0, 0, 0))
        points_rect = points_text.get_rect(center=(center_x, self.menu_y + 185))
        screen.blit(points_text, points_rect)
        
        # Draw skill categories with upgrade buttons
        y_offset = 225
        for skill_name, skill_level in self.skills.items():
            # Draw skill text
            skill_text = self.font.render(f"{skill_name}: {skill_level}/5", True, (0, 0, 0))
            skill_rect = skill_text.get_rect(center=(center_x - 50, self.menu_y + y_offset))
            screen.blit(skill_text, skill_rect)
            
            # Draw upgrade button
            if skill_name in self.skill_buttons:
                button_rect = self.skill_buttons[skill_name]
                can_upgrade = self._can_upgrade_skill(skill_name)
                is_hovered = (self.hovered_button == skill_name)
                
                # Button colors based on state
                if can_upgrade:
                    if is_hovered:
                        button_color = (120, 220, 120)  # Brighter green when hovered
                    else:
                        button_color = (100, 200, 100)  # Green when upgradeable
                    text_color = (0, 0, 0)
                else:
                    if is_hovered:
                        button_color = (170, 170, 170)  # Slightly brighter gray when hovered
                    else:
                        button_color = (150, 150, 150)  # Gray when not upgradeable
                    text_color = (100, 100, 100)
                
                # Draw button
                pygame.draw.rect(screen, button_color, button_rect)
                pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)
                
                # Draw button text
                button_text = self.font.render("+1", True, text_color)
                button_text_rect = button_text.get_rect(center=button_rect.center)
                screen.blit(button_text, button_text_rect)
            
            y_offset += 40
        
        # Draw feedback message
        if self.feedback_message:
            feedback_text = self.font.render(self.feedback_message, True, (200, 50, 50))
            feedback_rect = feedback_text.get_rect(center=(center_x, self.menu_y + self.menu_height - 80))
            screen.blit(feedback_text, feedback_rect)
        
        # Draw instructions
        instruction_text = self.font.render("Click +1 to upgrade skills", True, (100, 100, 100))
        instruction_rect = instruction_text.get_rect(center=(center_x, self.menu_y + self.menu_height - 60))
        screen.blit(instruction_text, instruction_rect)
        
        instruction_text2 = self.font.render("Press I or ESC to close", True, (100, 100, 100))
        instruction_rect2 = instruction_text2.get_rect(center=(center_x, self.menu_y + self.menu_height - 40))
        screen.blit(instruction_text2, instruction_rect2)
