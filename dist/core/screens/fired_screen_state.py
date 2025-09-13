"""
Fired Screen State
Handles the "YOU'RE FIRED!" screen when happiness reaches 0
"""

import pygame
from .base_screen_state import BaseScreenState

class FiredScreenState(BaseScreenState):
    """Handles the fired screen state"""
    
    def __init__(self, audio_system=None):
        super().__init__()
        self.audio_system = audio_system
        self.current_cursor = "default"
        self.fired_font = None
        self.subtitle_font = None
        self.button_font = None
        self.fade_alpha = 0
        self.fade_duration = 2.0
        self.fade_timer = 0.0
        self.show_buttons = False
        self.button_rects = {}
        self.hovered_button = None
        self.button_icon = None
        
    def enter(self):
        """Called when entering this state"""
        pygame.mouse.set_visible(True)
        
        # Load fonts
        try:
            self.fired_font = pygame.font.Font("Font/Retro Gaming.ttf", 72)
            self.subtitle_font = pygame.font.Font("Font/Retro Gaming.ttf", 36)
            self.button_font = pygame.font.Font("Font/Retro Gaming.ttf", 24)
        except:
            self.fired_font = pygame.font.Font(None, 72)
            self.subtitle_font = pygame.font.Font(None, 36)
            self.button_font = pygame.font.Font(None, 24)
        
        # Load button icon
        try:
            self.button_icon = pygame.image.load("Graphics/button_icon.png")
        except:
            self.button_icon = None
        
        # Reset fade
        self.fade_alpha = 0
        self.fade_timer = 0.0
        self.show_buttons = False
        
        # Play fired sound effect if available
        if self.audio_system:
            try:
                self.audio_system.play_sound("ronnie_coleman")
            except:
                pass
    
    def exit(self):
        """Called when exiting this state"""
        pygame.mouse.set_visible(False)
    
    def update(self, delta_time, events):
        """Update fired screen logic"""
        # Handle fade in
        if self.fade_timer < self.fade_duration:
            self.fade_timer += delta_time
            self.fade_alpha = min(255, int((self.fade_timer / self.fade_duration) * 255))
            
            # Show buttons after fade in is complete
            if self.fade_timer >= self.fade_duration:
                self.show_buttons = True
        
        # Handle input events
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return "Start Game"  # Reset/start new game
                elif event.key == pygame.K_ESCAPE:
                    return "title"  # Back to title
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    if self.show_buttons:
                        if "reset" in self.button_rects and self.button_rects["reset"].collidepoint(mouse_pos):
                            return "Start Game"  # Reset/start new game
                        elif "quit" in self.button_rects and self.button_rects["quit"].collidepoint(mouse_pos):
                            return "title"  # Back to title
            elif event.type == pygame.MOUSEMOTION:
                if self.show_buttons:
                    mouse_pos = pygame.mouse.get_pos()
                    self.hovered_button = None
                    for button_name, rect in self.button_rects.items():
                        if rect.collidepoint(mouse_pos):
                            self.hovered_button = button_name
                            break
        
        return None
    
    def draw(self, screen):
        """Draw fired screen"""
        # Clear screen with black background
        screen.fill((0, 0, 0))
        
        # Create overlay for fade effect
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(255 - self.fade_alpha)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Get screen dimensions
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Draw main "YOU'RE FIRED!" text
        fired_text = self.fired_font.render("YOU'RE FIRED!", True, (255, 0, 0))
        fired_rect = fired_text.get_rect()
        fired_rect.centerx = screen_width // 2
        fired_rect.centery = screen_height // 2 - 100
        
        # Add text shadow
        shadow_text = self.fired_font.render("YOU'RE FIRED!", True, (100, 0, 0))
        shadow_rect = shadow_text.get_rect()
        shadow_rect.centerx = fired_rect.centerx + 3
        shadow_rect.centery = fired_rect.centery + 3
        screen.blit(shadow_text, shadow_rect)
        
        # Draw main text
        screen.blit(fired_text, fired_rect)
        
        # Draw subtitle
        subtitle_text = self.subtitle_font.render("Happiness reached 0%", True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect()
        subtitle_rect.centerx = screen_width // 2
        subtitle_rect.centery = screen_height // 2 - 20
        screen.blit(subtitle_text, subtitle_rect)
        
        # Draw buttons if fade in is complete
        if self.show_buttons:
            self._draw_buttons(screen, screen_width, screen_height)
    
    def _draw_buttons(self, screen, screen_width, screen_height):
        """Draw the action buttons"""
        button_width = 200
        button_height = 50
        button_spacing = 20
        total_width = (button_width * 2) + button_spacing
        start_x = (screen_width - total_width) // 2
        button_y = screen_height // 2 + 100
        
        # Reset button
        reset_rect = pygame.Rect(start_x, button_y, button_width, button_height)
        self.button_rects["reset"] = reset_rect
        
        # Draw button background using icon if available
        if self.button_icon:
            # Scale button icon to fit button size
            scaled_icon = pygame.transform.scale(self.button_icon, (button_width, button_height))
            screen.blit(scaled_icon, reset_rect)
        else:
            # Fallback to colored rectangle
            button_color = (0, 100, 0) if self.hovered_button != "reset" else (0, 150, 0)
            pygame.draw.rect(screen, button_color, reset_rect)
            pygame.draw.rect(screen, (255, 255, 255), reset_rect, 2)
        
        # Button text color based on hover
        text_color = (255, 255, 255) if self.hovered_button == "reset" else (200, 200, 200)
        
        reset_text = self.button_font.render("Reset", True, text_color)
        reset_text_rect = reset_text.get_rect()
        reset_text_rect.center = reset_rect.center
        screen.blit(reset_text, reset_text_rect)
        
        # Quit button
        quit_rect = pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, button_height)
        self.button_rects["quit"] = quit_rect
        
        # Draw button background using icon if available
        if self.button_icon:
            # Scale button icon to fit button size
            scaled_icon = pygame.transform.scale(self.button_icon, (button_width, button_height))
            screen.blit(scaled_icon, quit_rect)
        else:
            # Fallback to colored rectangle
            button_color = (100, 0, 0) if self.hovered_button != "quit" else (150, 0, 0)
            pygame.draw.rect(screen, button_color, quit_rect)
            pygame.draw.rect(screen, (255, 255, 255), quit_rect, 2)
        
        # Button text color based on hover
        text_color = (255, 255, 255) if self.hovered_button == "quit" else (200, 200, 200)
        
        quit_text = self.button_font.render("Quit", True, text_color)
        quit_text_rect = quit_text.get_rect()
        quit_text_rect.center = quit_rect.center
        screen.blit(quit_text, quit_text_rect)
    
    def get_cursor_type(self):
        """Get the current cursor type for the game engine"""
        return self.current_cursor
