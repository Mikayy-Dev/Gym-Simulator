import pygame
import sys
import math
from .audio import AudioManager

class TitleScreen:
    def __init__(self, screen_width=1280, screen_height=720):
        self.screen_width = screen_width
        self.screen_height = screen_height
        # Load custom font
        try:
            self.custom_font = pygame.font.Font("Font/Retro Gaming.ttf", 24)
            self.font_large = pygame.font.Font("Font/Retro Gaming.ttf", 36)
            self.font_medium = pygame.font.Font("Font/Retro Gaming.ttf", 24)
            self.font_small = pygame.font.Font("Font/Retro Gaming.ttf", 16)
        except:
            # Fallback to default fonts if custom font fails to load
            self.font_large = pygame.font.Font(None, 36)
            self.font_medium = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 16)
        
        self.selected_option = 0
        self.options = ["Start Game", "Quit"]
        self.option_positions = []
        
        self.background_color = (0, 0, 0)
        self.title_color = (255, 255, 255)
        self.option_color = (200, 200, 200)
        self.selected_color = (100, 150, 255)
        
        self.animation_timer = 0
        self.animation_speed = 0.02
        
        # Load Ronnie Coleman image
        try:
            self.ronnie_image = pygame.image.load("Graphics/Ronnie_Coleman.png")
            # Scale the image to fill the left half of the screen
            left_half_width = self.screen_width // 2
            self.ronnie_image = pygame.transform.scale(self.ronnie_image, (left_half_width, self.screen_height))
        except:
            self.ronnie_image = None
        
        # Load logo image
        try:
            self.logo_image = pygame.image.load("Graphics/logo.png")
            # Scale the logo to an appropriate size (keeping aspect ratio)
            logo_width = 400
            logo_height = int(self.logo_image.get_height() * (logo_width / self.logo_image.get_width()))
            self.logo_image = pygame.transform.scale(self.logo_image, (logo_width, logo_height))
        except:
            self.logo_image = None
        
        # Load button icon
        try:
            self.button_icon = pygame.image.load("Graphics/button_icon.png")
            # Scale button icon to appropriate size
            self.button_width = 200
            self.button_height = 50
            self.button_icon = pygame.transform.scale(self.button_icon, (self.button_width, self.button_height))
        except:
            self.button_icon = None
        
    def calculate_positions(self):
        self.option_positions = []
        start_y = self.screen_height // 2 + 50
        
        # Position options on the right side of the screen
        right_half_center = self.screen_width // 2 + (self.screen_width // 4)  # Center of right half
        
        for i, option in enumerate(self.options):
            # Center button horizontally
            x = right_half_center - self.button_width // 2
            y = start_y + i * 80
            self.option_positions.append((x, y))
    
    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self.options[self.selected_option]
                elif event.key == pygame.K_ESCAPE:
                    return "Quit"
        return None
    
    def update(self, delta_time):
        self.animation_timer += delta_time
    
    def draw(self, screen):
        # Fill background
        screen.fill(self.background_color)
        
        # Draw Ronnie Coleman image on the left side
        if self.ronnie_image:
            screen.blit(self.ronnie_image, (0, 0))
        
        self.calculate_positions()
        
        # Position logo on the right side
        if self.logo_image:
            right_half_center = self.screen_width // 2 + (self.screen_width // 4)  # Center of right half
            logo_x = right_half_center - self.logo_image.get_width() // 2
            logo_y = self.screen_height // 4  # Moved up from // 3 to // 4
            screen.blit(self.logo_image, (logo_x, logo_y))
        
        for i, (option, (x, y)) in enumerate(zip(self.options, self.option_positions)):
            # Draw button icon
            if self.button_icon:
                button_surface = self.button_icon.copy()
                
                if i == self.selected_option:
                    # Apply pulsing effect to selected button
                    pulse = abs(math.sin(self.animation_timer * 3)) * 0.3 + 0.7
                    # Create a colored overlay for the selected button
                    overlay = pygame.Surface((self.button_width, self.button_height))
                    overlay.set_alpha(int(50 * pulse))
                    overlay.fill(self.selected_color)
                    button_surface.blit(overlay, (0, 0))
                
                screen.blit(button_surface, (x, y))
            
            # Draw text on button
            color = self.selected_color if i == self.selected_option else self.option_color
            
            if i == self.selected_option:
                pulse = abs(math.sin(self.animation_timer * 3)) * 0.3 + 0.7
                color = tuple(int(c * pulse) for c in color)
            
            text_surface = self.font_medium.render(option, True, color)
            text_x = x + (self.button_width - text_surface.get_width()) // 2
            text_y = y + (self.button_height - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))
        
        instructions_text = "Use Arrow Keys to Navigate Enter to Select ESC to Quit"
        instructions_surface = self.font_small.render(instructions_text, True, (100, 100, 100))
        right_half_center = self.screen_width // 2 + (self.screen_width // 4)  # Center of right half
        instructions_x = right_half_center - instructions_surface.get_width() // 2
        instructions_y = self.screen_height - 50
        screen.blit(instructions_surface, (instructions_x, instructions_y))
