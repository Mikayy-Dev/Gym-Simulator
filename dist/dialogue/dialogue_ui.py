import pygame

class DialogueUI:
    """Handles dialogue UI rendering and interaction"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # UI dimensions
        self.dialogue_box_height = 200
        self.dialogue_box_y = screen_height - self.dialogue_box_height
        self.padding = 20
        self.text_margin = 30
        
        # Colors
        self.background_color = (0, 0, 0, 200)  # Semi-transparent black
        self.border_color = (255, 255, 255)
        self.text_color = (255, 255, 255)
        self.highlight_color = (100, 150, 255)
        
        # Fonts
        try:
            self.title_font = pygame.font.Font("Font/Retro Gaming.ttf", 24)
            self.text_font = pygame.font.Font("Font/Retro Gaming.ttf", 18)
            self.response_font = pygame.font.Font("Font/Retro Gaming.ttf", 16)
        except:
            self.title_font = pygame.font.Font(None, 24)
            self.text_font = pygame.font.Font(None, 18)
            self.response_font = pygame.font.Font(None, 16)
        
        # Animation
        self.text_animation_timer = 0
        self.text_animation_speed = 0.05
        self.current_text_display = ""
        self.full_text = ""
        self.text_complete = False
    
    def update(self, delta_time):
        """Update dialogue UI animation"""
        if not self.text_complete:
            self.text_animation_timer += delta_time
            if self.text_animation_timer >= self.text_animation_speed:
                self.text_animation_timer = 0
                if len(self.current_text_display) < len(self.full_text):
                    self.current_text_display = self.full_text[:len(self.current_text_display) + 1]
                else:
                    self.text_complete = True
    
    def set_dialogue_text(self, text):
        """Set the dialogue text to display"""
        self.full_text = text
        self.current_text_display = ""
        self.text_complete = False
        self.text_animation_timer = 0
    
    def draw(self, screen, dialogue_text, responses):
        """Draw the dialogue UI"""
        if not dialogue_text:
            return
        
        # Set current text for animation
        if self.full_text != dialogue_text:
            self.set_dialogue_text(dialogue_text)
        
        # Draw semi-transparent background
        dialogue_surface = pygame.Surface((self.screen_width, self.dialogue_box_height), pygame.SRCALPHA)
        dialogue_surface.fill(self.background_color)
        screen.blit(dialogue_surface, (0, self.dialogue_box_y))
        
        # Draw border
        pygame.draw.rect(screen, self.border_color, 
                        (0, self.dialogue_box_y, self.screen_width, self.dialogue_box_height), 3)
        
        # Draw dialogue text
        self._draw_dialogue_text(screen, self.current_text_display)
        
        # Draw responses if text is complete
        if self.text_complete and responses:
            self._draw_responses(screen, responses)
    
    def _draw_dialogue_text(self, screen, text):
        """Draw the main dialogue text"""
        # Wrap text to fit in dialogue box
        max_width = self.screen_width - (self.padding * 2)
        wrapped_lines = self._wrap_text(text, self.text_font, max_width)
        
        # Draw each line
        y_offset = self.dialogue_box_y + self.text_margin
        for line in wrapped_lines:
            text_surface = self.text_font.render(line, True, self.text_color)
            screen.blit(text_surface, (self.padding, y_offset))
            y_offset += self.text_font.get_height() + 5
    
    def _draw_responses(self, screen, responses):
        """Draw response options"""
        if not responses:
            return
        
        # Calculate starting position for responses
        response_start_y = self.dialogue_box_y + 100
        
        for i, response in enumerate(responses):
            response_text = f"{i + 1}. {response['text']}"
            response_surface = self.response_font.render(response_text, True, self.text_color)
            
            # Position responses
            response_x = self.padding
            response_y = response_start_y + (i * (self.response_font.get_height() + 10))
            
            screen.blit(response_surface, (response_x, response_y))
    
    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
