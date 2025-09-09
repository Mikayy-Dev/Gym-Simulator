"""
Cutscene Screen State
Handles MP4 cutscene playback before title screen
"""

import pygame
import cv2
import numpy as np
import os
import subprocess
import threading
import time
from .base_screen_state import BaseScreenState

class CutsceneScreenState(BaseScreenState):
    """Handles cutscene playback state"""
    
    def __init__(self):
        super().__init__()
        self.video_path = "cutscene/Everybody Wants To Be a Bodybuilder, But Nobody Wants to Lift No Heavy-ass Weights.mp4"
        self.cap = None
        self.playing = False
        self.skipped = False
        self.current_cursor = "default"
        self.show_skip_text = False
        self.skip_text_timer = 0.0
        self.skip_text_duration = 2.0
        self.font = None
        self.flash_timer = 0.0
        self.flash_speed = 3.0
        self.audio_process = None
        self.video_duration = 0.0
        self.video_start_time = 0.0
        self.audio_file = None
        self.audio_channel = None
        
    def enter(self):
        """Called when entering this state"""
        pygame.mouse.set_visible(False)
        self._start_cutscene()
        self._setup_font()
    
    def exit(self):
        """Called when exiting this state"""
        self._stop_cutscene()
        pygame.mouse.set_visible(False)
    
    def _start_cutscene(self):
        """Start playing the cutscene"""
        if os.path.exists(self.video_path):
            self.cap = cv2.VideoCapture(self.video_path)
            self.playing = True
            self.skipped = False
            
            # Get video duration for reference
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            frame_count = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            self.video_duration = frame_count / fps if fps > 0 else 0
            
            # Start audio and video simultaneously
            self.video_start_time = time.time()
            self._extract_and_play_audio()
        else:
            self.playing = False
    
    def _extract_and_play_audio(self):
        """Play audio from existing MP3 file"""
        try:
            # Use the existing MP3 file in Audio folder
            audio_path = "Audio/cutscene_audio.mp3"
            
            if not os.path.exists(audio_path):
                return
            
            # Initialize pygame mixer if not already done
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            
            # Load and play audio
            self.audio_file = pygame.mixer.Sound(audio_path)
            self.audio_channel = self.audio_file.play()
            
        except Exception as e:
            pass
    
    def _stop_cutscene(self):
        """Stop the cutscene and clean up"""
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.audio_channel:
            self.audio_channel.stop()
            self.audio_channel = None
        if self.audio_file:
            self.audio_file = None
        self.playing = False
    
    def _setup_font(self):
        """Set up font for skip text"""
        try:
            self.font = pygame.font.Font("Font/Retro Gaming.ttf", 24)
        except:
            self.font = pygame.font.Font(None, 24)
    
    def update(self, delta_time, events):
        """Update cutscene logic"""
        if not self.playing:
            return "title"
        
        # Update skip text timer
        if self.show_skip_text:
            self.skip_text_timer += delta_time
            self.flash_timer += delta_time
            if self.skip_text_timer >= self.skip_text_duration:
                self.show_skip_text = False
                self.skip_text_timer = 0.0
                self.flash_timer = 0.0
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.skipped = True
                    return "title"
                else:
                    # Show skip text for any other key press
                    self.show_skip_text = True
                    self.skip_text_timer = 0.0
                    self.flash_timer = 0.0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Show skip text for mouse click
                self.show_skip_text = True
                self.skip_text_timer = 0.0
                self.flash_timer = 0.0
        
        return None
    
    def draw(self, screen):
        """Draw the cutscene frame"""
        if not self.playing or not self.cap:
            return
        
        ret, frame = self.cap.read()
        if not ret:
            # Video ended naturally
            self.playing = False
            return
        
        # Get current frame position for debugging
        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        
        # Debug every 30 frames (about once per second)
        if int(current_frame) % 30 == 0:
            elapsed_time = time.time() - self.video_start_time
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (screen.get_width(), screen.get_height()))
        
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        screen.blit(frame_surface, (0, 0))
        
        # Draw skip text if it should be shown
        if self.show_skip_text and self.font:
            self._draw_skip_text(screen)
        
        if self.skipped:
            self.playing = False
    
    def _draw_skip_text(self, screen):
        """Draw the skip text with flashing effect"""
        text = "Press SPACE to Skip"
        
        # Calculate flashing alpha based on flash timer
        flash_cycle = (self.flash_timer * self.flash_speed) % 2.0
        if flash_cycle < 1.0:
            alpha = int(255 * flash_cycle)  # Fade in
        else:
            alpha = int(255 * (2.0 - flash_cycle))  # Fade out
        
        # Create text surface with alpha
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_surface.set_alpha(alpha)
        
        # Add black outline for better visibility (also with alpha)
        outline_surface = self.font.render(text, True, (0, 0, 0))
        outline_surface.set_alpha(alpha)
        
        # Calculate position (bottom right with padding)
        text_rect = text_surface.get_rect()
        x = screen.get_width() - text_rect.width - 20
        y = screen.get_height() - text_rect.height - 20
        
        # Draw outline (offset by 1 pixel in each direction)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    screen.blit(outline_surface, (x + dx, y + dy))
        
        # Draw main text
        screen.blit(text_surface, (x, y))
    
    def get_cursor_type(self):
        """Get the current cursor type"""
        return self.current_cursor
