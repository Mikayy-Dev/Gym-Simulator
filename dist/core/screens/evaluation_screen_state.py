"""
Evaluation Screen State
Shows task statistics and performance evaluation when timer runs out
"""

import pygame
from .base_screen_state import BaseScreenState

class EvaluationScreenState(BaseScreenState):
    """Handles the evaluation screen state"""
    
    def __init__(self, audio_system=None, task_tracker=None):
        super().__init__()
        self.audio_system = audio_system
        self.task_tracker = task_tracker
        self.current_cursor = "default"
        
        # Fonts
        self.title_font = None
        self.header_font = None
        self.text_font = None
        self.score_font = None
        
        # UI elements
        self.button_rects = {}
        self.hovered_button = None
        self.button_icon = None
        
        # Animation
        self.slide_offset = 0
        self.slide_duration = 0.3
        self.slide_timer = 0.0
        self.fade_alpha = 0
        self.fade_duration = 1.0
        self.fade_timer = 0.0
        self.show_content = False
        
        # No scrolling needed
        
    def enter(self):
        """Called when entering this state"""
        pygame.mouse.set_visible(True)
        
        # Load fonts - smaller sizes to fit better
        try:
            self.title_font = pygame.font.Font("Font/Retro Gaming.ttf", 36)
            self.header_font = pygame.font.Font("Font/Retro Gaming.ttf", 24)
            self.text_font = pygame.font.Font("Font/Retro Gaming.ttf", 16)
            self.score_font = pygame.font.Font("Font/Retro Gaming.ttf", 22)
        except:
            self.title_font = pygame.font.Font(None, 36)
            self.header_font = pygame.font.Font(None, 24)
            self.text_font = pygame.font.Font(None, 16)
            self.score_font = pygame.font.Font(None, 22)
        
        # Load button icon
        try:
            self.button_icon = pygame.image.load("Graphics/button_icon.png")
        except:
            self.button_icon = None
        
        # Reset animation - start with fade effect
        self.slide_offset = 0
        self.slide_timer = 0.0
        self.fade_alpha = 0
        self.fade_timer = 0.0
        self.show_content = False
        
        # Calculate efficiency score
        if self.task_tracker:
            self.task_tracker.calculate_efficiency_score()
        
        # Play completion sound if available
        if self.audio_system:
            try:
                self.audio_system.play_sound("Woohoo!")
            except:
                pass
    
    def exit(self):
        """Called when exiting this state"""
        pygame.mouse.set_visible(False)
    
    def update(self, delta_time, events):
        """Update evaluation screen logic"""
        # Handle fade-in animation
        if not self.show_content:
            self.fade_timer += delta_time
            if self.fade_timer >= self.fade_duration:
                self.show_content = True
                self.fade_alpha = 255
            else:
                self.fade_alpha = int((self.fade_timer / self.fade_duration) * 255)
        
        # Handle slide-in animation
        if self.slide_timer < self.slide_duration:
            self.slide_timer += delta_time
            progress = min(self.slide_timer / self.slide_duration, 1.0)
            # Slide in from right
            self.slide_offset = int((1.0 - progress) * 100)
        
        # Handle input events
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return "Start Game"  # Start a new game with reset
                elif event.key == pygame.K_ESCAPE:
                    return "title"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    if self._handle_button_click(mouse_x, mouse_y):
                        return "Start Game"  # Start a new game with reset
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                self._update_button_hover(mouse_x, mouse_y)
            # No scroll handling needed
        
        return None
    
    def _handle_button_click(self, mouse_x, mouse_y):
        """Handle button clicks"""
        for button_name, rect in self.button_rects.items():
            if rect.collidepoint(mouse_x, mouse_y):
                if button_name == "continue":
                    return True
        return False
    
    def _update_button_hover(self, mouse_x, mouse_y):
        """Update button hover states"""
        self.hovered_button = None
        for button_name, rect in self.button_rects.items():
            if rect.collidepoint(mouse_x, mouse_y):
                self.hovered_button = button_name
                break
    
    def draw(self, screen):
        """Draw the evaluation screen"""
        # Clear screen with background
        screen.fill((0, 0, 0))  # Black background
        
        # Only draw content if fade-in is complete or in progress
        if self.fade_alpha > 0:
            # Create a surface for the content with slide offset
            content_surface = pygame.Surface(screen.get_size())
            content_surface.fill((0, 0, 0))  # Black background
            
            # Draw content on the content surface
            self._draw_background(content_surface)
            self._draw_title(content_surface)
            self._draw_task_stats(content_surface)
            self._draw_efficiency_score(content_surface)
            self._draw_buttons(content_surface)
            
            # Apply fade effect
            if self.fade_alpha < 255:
                content_surface.set_alpha(self.fade_alpha)
            
            # Blit content surface with slide offset
            screen.blit(content_surface, (self.slide_offset, 0))
    
    def _draw_background(self, screen):
        """Draw background elements"""
        # No background elements - just solid black
        pass
    
    def _draw_title(self, screen):
        """Draw the title"""
        title_text = self.title_font.render("SESSION COMPLETE!", True, (255, 255, 255))
        title_rect = title_text.get_rect()
        title_rect.centerx = screen.get_width() // 2
        title_rect.y = 50
        screen.blit(title_text, title_rect)
        
        subtitle_text = self.text_font.render("Here's how you performed:", True, (255, 255, 255))
        subtitle_rect = subtitle_text.get_rect()
        subtitle_rect.centerx = screen.get_width() // 2
        subtitle_rect.y = title_rect.bottom + 10
        screen.blit(subtitle_text, subtitle_rect)
    
    def _draw_task_stats(self, screen):
        """Draw task statistics"""
        if not self.task_tracker:
            return
        
        start_y = 120
        x_offset = 50
        screen_height = screen.get_height()
        
        # Task statistics section
        header_text = self.header_font.render("TASK BREAKDOWN", True, (255, 255, 255))
        screen.blit(header_text, (x_offset, start_y))
        start_y += 35
        
        # Draw consolidated task categories
        categories = {
            "Customer Service": {
                "npcs_checked_in": "NPCs Checked In",
                "gym_objects_interacted": "Equipment Interactions"
            },
            "Maintenance": {
                "machines_cleaned": "Machines Cleaned",
                "equipment_turned_off": "Equipment Turned Off"
            },
            "Organization": {
                "dumbbells_returned": "Dumbbells Returned",
                "weight_plates_returned": "Weight Plates Returned",
                "floor_dumbbells_picked_up": "Floor Items Picked Up",
                "floor_plates_picked_up": "Floor Plates Picked Up"
            }
        }
        
        for category_name, tasks in categories.items():
            # Category header
            category_text = self.header_font.render(category_name, True, (255, 255, 255))
            screen.blit(category_text, (x_offset, start_y))
            start_y += 30
            
            # Tasks in this category
            category_total = 0
            for task_key, description in tasks.items():
                if task_key in self.task_tracker.tasks:
                    count = self.task_tracker.tasks[task_key]
                    category_total += count
                    color = (255, 255, 255) if count > 0 else (200, 200, 200)
                    
                    task_text = self.text_font.render(f"  {description}: {count}", True, color)
                    screen.blit(task_text, (x_offset + 20, start_y))
                    start_y += 20
            
            # Category total
            category_total_text = self.text_font.render(f"  {category_name} Total: {category_total}", True, (0, 200, 0))
            screen.blit(category_total_text, (x_offset + 20, start_y))
            start_y += 30
        
        # Overall stats
        start_y += 15
        stats_text = self.header_font.render("SESSION SUMMARY", True, (255, 255, 255))
        screen.blit(stats_text, (x_offset, start_y))
        start_y += 35
        
        # Total tasks
        total_text = self.text_font.render(f"Total Tasks: {self.task_tracker.tasks['total_tasks']}", True, (255, 255, 255))
        screen.blit(total_text, (x_offset + 20, start_y))
        start_y += 20
        
        # Time played
        time_played = self.task_tracker.stats.get("time_played", 0)
        time_text = self.text_font.render(f"Duration: {time_played:.1f}s", True, (255, 255, 255))
        screen.blit(time_text, (x_offset + 20, start_y))
        start_y += 20
        
        # Tasks per minute
        if time_played > 0:
            tasks_per_minute = (self.task_tracker.tasks['total_tasks'] / time_played) * 60
            efficiency_text = self.text_font.render(f"Tasks/min: {tasks_per_minute:.1f}", True, (255, 255, 255))
            screen.blit(efficiency_text, (x_offset + 20, start_y))
    
    def _draw_efficiency_score(self, screen):
        """Draw efficiency score"""
        if not self.task_tracker:
            return
        
        # Draw score on the right side without a box
        score_x = screen.get_width() - 350
        score_y = 200
        
        # Draw score title
        score_title = self.header_font.render("EFFICIENCY SCORE", True, (255, 255, 255))
        title_rect = score_title.get_rect()
        title_rect.x = score_x
        title_rect.y = score_y
        screen.blit(score_title, title_rect)
        
        # Draw score value
        efficiency_score = self.task_tracker.stats.get("efficiency_score", 0)
        score_text = self.score_font.render(f"{efficiency_score:.0f}", True, (255, 255, 255))
        score_rect = score_text.get_rect()
        score_rect.x = score_x
        score_rect.y = score_y + 60
        screen.blit(score_text, score_rect)
        
        # Draw score description
        if efficiency_score >= 200:
            desc = "EXCELLENT!"
        elif efficiency_score >= 150:
            desc = "GOOD!"
        elif efficiency_score >= 100:
            desc = "FAIR"
        else:
            desc = "NEEDS IMPROVEMENT"
        
        desc_text = self.text_font.render(desc, True, (255, 255, 255))
        desc_rect = desc_text.get_rect()
        desc_rect.x = score_x
        desc_rect.y = score_y + 100
        screen.blit(desc_text, desc_rect)
        
        # Draw score breakdown
        breakdown_text = self.text_font.render("Based on tasks completed", True, (255, 255, 255))
        breakdown_rect = breakdown_text.get_rect()
        breakdown_rect.x = score_x
        breakdown_rect.y = score_y + 130
        screen.blit(breakdown_text, breakdown_rect)
    
    def _draw_buttons(self, screen):
        """Draw buttons"""
        # Button size - match fired screen pattern
        button_width = 200
        button_height = 50
        button_x = screen.get_width() // 2 - button_width // 2
        button_y = screen.get_height() - 120
        
        # Continue button
        continue_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        self.button_rects["continue"] = continue_rect
        
        # Draw button background using icon if available
        if self.button_icon:
            # Scale button icon to fit button size
            scaled_icon = pygame.transform.scale(self.button_icon, (button_width, button_height))
            screen.blit(scaled_icon, continue_rect)
        else:
            # Fallback to colored rectangle
            button_color = (100, 150, 255) if self.hovered_button != "continue" else (120, 180, 255)
            pygame.draw.rect(screen, button_color, continue_rect)
            pygame.draw.rect(screen, (255, 255, 255), continue_rect, 2)
        
        # Button text color based on hover
        text_color = (100, 150, 255) if self.hovered_button == "continue" else (255, 255, 255)
        
        continue_text = self.text_font.render("CONTINUE", True, text_color)
        continue_text_rect = continue_text.get_rect()
        continue_text_rect.center = continue_rect.center
        screen.blit(continue_text, continue_text_rect)
        
        # Instructions
        instructions = self.text_font.render("Press ENTER, SPACE, or click to continue", True, (255, 255, 255))
        inst_rect = instructions.get_rect()
        inst_rect.centerx = screen.get_width() // 2
        inst_rect.y = button_y + 70
        screen.blit(instructions, inst_rect)
    
