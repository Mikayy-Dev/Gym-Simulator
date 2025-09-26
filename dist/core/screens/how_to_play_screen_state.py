"""
How to Play Screen State
Handles the how to play screen logic and rendering
"""

import pygame
from .base_screen_state import BaseScreenState

class HowToPlayScreenState(BaseScreenState):
    """Handles how to play screen state"""
    
    def __init__(self):
        super().__init__()
        self.current_cursor = "default"
        self.button_rects = {}
        self.hovered_button = None
        
        # Scrolling variables
        self.scroll_y = 0
        self.scroll_speed = 30
        self.max_scroll = 0
        self.content_height = 0
        
        # Load fonts
        try:
            self.title_font = pygame.font.Font("Font/Retro Gaming.ttf", 48)
            self.text_font = pygame.font.Font("Font/Retro Gaming.ttf", 24)
            self.small_font = pygame.font.Font("Font/Retro Gaming.ttf", 18)
        except:
            self.title_font = pygame.font.Font(None, 48)
            self.text_font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
        
        # Load button icon
        try:
            self.button_icon = pygame.image.load("Graphics/button_icon.png")
        except:
            self.button_icon = None
        
        # Game instructions
        self.instructions = [
            "GAME OBJECTIVES:",
            "",
            " Keep the gym clean and organized",
            " Maintain customer happiness above zero",
            " Complete tasks to earn skill points",
            " Avoid getting fired by keeping customers satisfied",
            "",
            "CONTROLS:",
            "",
            " WASD/Arrow Keys: Move around the gym",
            " Mouse: Click to interact with equipment and NPCs",
            " ESC: Pause the game",
            " I: Open skill points inventory",
            " Shift: Sprint (drains stamina)",
            "",
            "EQUIPMENT INTERACTIONS:",
            "",
            " Right-click dirty equipment: Clean with spray bottle",
            " Right-click running equipment: Turn off machines",
            " Right-click dumbbells on floor: Pick up and return to rack",
            " Right-click weight plates on floor: Pick up and return to rack",
            " Left-click NPCs: Check them in at the front desk",
            "",
            "GAME MECHANICS:",
            "",
            " Equipment gets dirty after NPCs use it",
            " Clean equipment to maintain customer satisfaction",
            " Pick up dropped weights to keep the gym organized",
            " Turn off equipment when not in use to save energy",
            " Check in NPCs to start their workout sessions",
            "",
            "HAPPINESS SYSTEM:",
            "",
            " Keep the happiness bar above zero to avoid being fired",
            " Cleaning equipment increases customer happiness",
            " Returning weights to racks improves gym organization",
            " Turning off unused equipment shows good management",
            " The happiness bar slowly decreases over time",
            "",

        ]
    
    def enter(self):
        """Called when entering this state"""
        pygame.mouse.set_visible(True)
    
    def exit(self):
        """Called when exiting this state"""
        pygame.mouse.set_visible(False)
    
    def update(self, delta_time, events):
        """Update how to play screen logic"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return "Back to Title"
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    # Scroll up
                    self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    # Scroll down
                    self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    if "back" in self.button_rects and self.button_rects["back"].collidepoint(mouse_pos):
                        return "Back to Title"
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                self.hovered_button = None
                for button_name, rect in self.button_rects.items():
                    if rect.collidepoint(mouse_pos):
                        self.hovered_button = button_name
                        break
            elif event.type == pygame.MOUSEWHEEL:
                # Handle mouse wheel scrolling
                if event.y > 0:  # Scroll up
                    self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
                elif event.y < 0:  # Scroll down
                    self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)
        
        return None
    
    def draw(self, screen):
        """Draw how to play screen"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Fill background
        screen.fill((0, 0, 0))
        
        # Calculate content height and max scroll
        self._calculate_scroll_limits(screen_width, screen_height)
        
        # Define text area boundaries (with border)
        text_area_x = 50
        text_area_y = 50
        text_area_width = screen_width - 100  # 50px margin on each side
        text_area_height = screen_height - 200  # Leave space for back button
        
        # Draw border around text area
        border_rect = pygame.Rect(text_area_x - 5, text_area_y - 5, text_area_width + 10, text_area_height + 10)
        pygame.draw.rect(screen, (100, 100, 100), border_rect, 3)  # Border
        pygame.draw.rect(screen, (20, 20, 20), border_rect)  # Background
        
        # Create a surface for the scrollable content
        content_surface = pygame.Surface((text_area_width, self.content_height))
        content_surface.fill((20, 20, 20))  # Match border background
        
        # Draw title on content surface
        title_text = self.title_font.render("HOW TO PLAY", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(text_area_width // 2, 60))
        content_surface.blit(title_text, title_rect)
        
        # Draw instructions on content surface
        y_offset = 120
        for instruction in self.instructions:
            if instruction == "":
                y_offset += 20
                continue
            
            if instruction.endswith(":"):
                # Section headers
                color = (100, 150, 255)
                font = self.text_font
            else:
                # Regular text
                color = (200, 200, 200)
                font = self.small_font
            
            text_surface = font.render(instruction, True, color)
            text_rect = text_surface.get_rect(center=(text_area_width // 2, y_offset))
            content_surface.blit(text_surface, text_rect)
            y_offset += 30
        
        # Set clipping area for the text region
        old_clip = screen.get_clip()
        screen.set_clip(text_area_x, text_area_y, text_area_width, text_area_height)
        
        # Blit the scrolled content to the screen within the clipped area
        screen.blit(content_surface, (text_area_x, text_area_y - self.scroll_y))
        
        # Restore original clipping
        screen.set_clip(old_clip)
        
        # Draw back button (always visible at bottom)
        self._draw_back_button(screen, screen_width, screen_height)
        
        # Draw scroll indicators
        self._draw_scroll_indicators(screen, screen_width, screen_height)
    
    def _draw_back_button(self, screen, screen_width, screen_height):
        """Draw the back button"""
        button_width = 200
        button_height = 50
        button_x = screen_width // 2 - button_width // 2
        button_y = screen_height - 100
        
        back_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        self.button_rects["back"] = back_rect
        
        # Draw button background using icon if available
        if self.button_icon:
            scaled_icon = pygame.transform.scale(self.button_icon, (button_width, button_height))
            screen.blit(scaled_icon, back_rect)
        else:
            # Fallback to colored rectangle
            button_color = (100, 150, 255) if self.hovered_button == "back" else (50, 100, 200)
            pygame.draw.rect(screen, button_color, back_rect)
            pygame.draw.rect(screen, (255, 255, 255), back_rect, 2)
        
        # Button text color based on hover
        text_color = (255, 255, 255) if self.hovered_button == "back" else (200, 200, 200)
        
        back_text = self.text_font.render("BACK", True, text_color)
        back_text_rect = back_text.get_rect()
        back_text_rect.center = back_rect.center
        screen.blit(back_text, back_text_rect)
        
        # Instructions
        instructions = self.small_font.render("Press ESC, ENTER, or click BACK to return", True, (128, 128, 128))
        inst_rect = instructions.get_rect()
        inst_rect.centerx = screen_width // 2
        inst_rect.y = button_y + 70
        screen.blit(instructions, inst_rect)
    
    def _calculate_scroll_limits(self, screen_width, screen_height):
        """Calculate the total content height and maximum scroll position"""
        # Calculate content height
        y_offset = 120  # Start after title
        for instruction in self.instructions:
            if instruction == "":
                y_offset += 20
            else:
                y_offset += 30
        
        # Add some padding at the bottom
        y_offset += 50
        
        self.content_height = y_offset
        
        # Calculate max scroll (content height - visible text area height)
        text_area_height = screen_height - 200  # Leave space for back button
        self.max_scroll = max(0, self.content_height - text_area_height)
    
    def _draw_scroll_indicators(self, screen, screen_width, screen_height):
        """Draw scroll position indicators"""
        if self.max_scroll <= 0:
            return  # No scrolling needed
        
        # Define text area boundaries (same as in draw method)
        text_area_x = 50
        text_area_y = 50
        text_area_width = screen_width - 100
        text_area_height = screen_height - 200
        
        # Draw scroll bar on the right side of the text area
        scroll_bar_width = 8
        scroll_bar_x = text_area_x + text_area_width - scroll_bar_width - 5
        scroll_bar_y = text_area_y
        scroll_bar_height = text_area_height
        
        # Background of scroll bar
        pygame.draw.rect(screen, (50, 50, 50), (scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height))
        
        # Scroll thumb
        thumb_height = max(20, int(scroll_bar_height * (scroll_bar_height / self.content_height)))
        thumb_y = scroll_bar_y + int((scroll_bar_height - thumb_height) * (self.scroll_y / self.max_scroll))
        pygame.draw.rect(screen, (150, 150, 150), (scroll_bar_x, thumb_y, scroll_bar_width, thumb_height))
        
        # Draw scroll instructions
        scroll_text = self.small_font.render("Use mouse wheel or arrow keys to scroll", True, (100, 100, 100))
        text_rect = scroll_text.get_rect()
        text_rect.centerx = screen_width // 2
        text_rect.y = screen_height - 150
        screen.blit(scroll_text, text_rect)
    
    def get_cursor_type(self):
        """Get the current cursor type for the game engine"""
        return self.current_cursor
