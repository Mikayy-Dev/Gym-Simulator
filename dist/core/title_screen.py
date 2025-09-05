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
        
        self.options = ["Start Game", "Quit"]
        self.option_positions = []
        self.hovered_option = None
        
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
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    # Check if clicking on any button
                    for i, (x, y) in enumerate(self.option_positions):
                        if x <= mouse_x <= x + self.button_width and y <= mouse_y <= y + self.button_height:
                            return self.options[i]
        return None
    
    def update(self, delta_time):
        self.animation_timer += delta_time
        # Check for mouse hover
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.hovered_option = None
        for i, (x, y) in enumerate(self.option_positions):
            if x <= mouse_x <= x + self.button_width and y <= mouse_y <= y + self.button_height:
                self.hovered_option = i
                break
    
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
                
                # Apply hover effect
                if i == self.hovered_option:
                    overlay = pygame.Surface((self.button_width, self.button_height))
                    overlay.set_alpha(30)
                    overlay.fill(self.selected_color)
                    button_surface.blit(overlay, (0, 0))
                
                screen.blit(button_surface, (x, y))
            
            # Draw text on button
            if i == self.hovered_option:
                color = self.selected_color
            else:
                color = self.option_color
            
            text_surface = self.font_medium.render(option, True, color)
            text_x = x + (self.button_width - text_surface.get_width()) // 2
            text_y = y + (self.button_height - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))
        
        instructions_text = "Click to Select or Press Enter"
        instructions_surface = self.font_small.render(instructions_text, True, (100, 100, 100))
        right_half_center = self.screen_width // 2 + (self.screen_width // 4)  # Center of right half
        instructions_x = right_half_center - instructions_surface.get_width() // 2
        instructions_y = self.screen_height - 50
        screen.blit(instructions_surface, (instructions_x, instructions_y))
