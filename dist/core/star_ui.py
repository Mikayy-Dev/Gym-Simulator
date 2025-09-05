import pygame

class StarUI:
    def __init__(self, x=1200, y=50, max_stars=5, star_size=64, audio_manager=None):
        """
        Initialize the Star UI component
        
        Args:
            x: X position on screen (default: 1200 - right side)
            y: Y position on screen (default: 50)
            max_stars: Maximum number of stars to display (default: 5)
            star_size: Size of each star in pixels (default: 64)
            audio_manager: Audio manager for playing sound effects
        """
        self.x = x
        self.y = y
        self.max_stars = max_stars
        self.star_size = star_size
        self.current_stars = 0  # Number of filled stars
        self.total_progress = 0  # Total progress points (0 to max_stars * 6)
        self.audio_manager = audio_manager
        self.star_full_states = [False] * max_stars  # Track which stars have reached full
        self.star_sound_cached = None  # Cache the star sound for faster playback
        self.all_stars_sound_cached = None  # Cache the all stars sound
        self.all_stars_played = False  # Track if all stars sound has been played
        
        # Load the star spritesheet
        try:
            self.star_spritesheet = pygame.image.load("Graphics/star.png")
            self.star_spritesheet = self.star_spritesheet.convert_alpha()
            
            # Get spritesheet dimensions
            self.spritesheet_width = self.star_spritesheet.get_width()
            self.spritesheet_height = self.star_spritesheet.get_height()
            
            # Calculate frame width (assuming frames are arranged horizontally)
            # Since you mentioned it's a 32x32 sprite, let's assume each frame is 32x32
            self.frame_width = 32  # Each frame is 32 pixels wide
            self.frame_height = 32  # Each frame is 32 pixels tall
            self.total_frames = 6  # You confirmed it has 6 frames
            
            
        except pygame.error as e:
            self.star_spritesheet = None
        
        # Calculate spacing between stars (vertical stacking)
        self.star_spacing = 10  # pixels between stars
        
        # Calculate total height needed for all stars (vertical layout)
        self.total_height = (self.star_size * self.max_stars) + (self.star_spacing * (self.max_stars - 1))
        self.total_width = self.star_size  # Only one star wide
        
        # Cache for scaled sprites
        self._cached_sprites = {}
    
    def set_stars(self, count):
        """Set the number of filled stars (0 to max_stars)"""
        self.current_stars = max(0, min(count, self.max_stars))
    
    def add_progress(self, points=1):
        """Add progress points to fill stars frame by frame"""
        max_progress = self.max_stars * 6  # 6 frames per star
        old_progress = self.total_progress
        self.total_progress = min(self.total_progress + points, max_progress)
        
        # Check if any stars reached full (frame 5) and play sound
        self._check_star_completion(old_progress, self.total_progress)
       
    
    def _check_star_completion(self, old_progress, new_progress):
        """Check if any stars reached full and play sound effect"""
        if not self.audio_manager:
            return
            
        # Check each star to see if it just reached full (frame 5)
        for star_index in range(self.max_stars):
            # Calculate the progress range for this star (0-5, 6-11, 12-17, etc.)
            star_start = star_index * 6
            star_end = star_start + 5
            
            # Check if this star just reached full (progress 5)
            old_star_progress = max(0, old_progress - star_start)
            new_star_progress = max(0, new_progress - star_start)
            
            # If the star just reached frame 5 (full) and wasn't full before
            if (new_star_progress >= 5 and old_star_progress < 5 and 
                not self.star_full_states[star_index]):
                self.star_full_states[star_index] = True
                
                # Check if all stars are now full
                if all(self.star_full_states) and not self.all_stars_played:
                    self._play_all_stars_sound()
                    self.all_stars_played = True
                else:
                    # Play individual star sound
                    self._play_star_sound_immediately()
    
    def _play_star_sound_immediately(self):
        """Play star sound with minimal delay"""
        try:
            # Cache the sound for faster access
            if not self.star_sound_cached and "star_full" in self.audio_manager.sound_effects:
                self.star_sound_cached = self.audio_manager.sound_effects["star_full"]
            
            # Stop any currently playing star sounds to avoid overlap
            if self.star_sound_cached:
                self.star_sound_cached.stop()
            
            # Play the sound immediately using cached reference at lower volume
            if self.star_sound_cached:
                # Play at 20% of the normal SFX volume
                star_volume = self.audio_manager.sfx_volume * 0.3
                self.star_sound_cached.set_volume(star_volume)
                self.star_sound_cached.play()
            else:
                # Fallback to regular method with lower volume
                if "star_full" in self.audio_manager.sound_effects:
                    sound = self.audio_manager.sound_effects["star_full"]
                    star_volume = self.audio_manager.sfx_volume * 0.3
                    sound.set_volume(star_volume)
                    sound.play()
        except Exception as e:
            pass
    def _play_all_stars_sound(self):
        """Play the special sound when all stars are full"""
        try:
            # Cache the all stars sound for faster access
            if not self.all_stars_sound_cached and "all_stars_full" in self.audio_manager.sound_effects:
                self.all_stars_sound_cached = self.audio_manager.sound_effects["all_stars_full"]
            
            # Stop any currently playing sounds
            if self.all_stars_sound_cached:
                self.all_stars_sound_cached.stop()
            
            # Play the Woohoo sound at normal volume
            if self.all_stars_sound_cached:
                self.all_stars_sound_cached.set_volume(self.audio_manager.sfx_volume)
                self.all_stars_sound_cached.play()
            else:
                # Fallback to regular method
                self.audio_manager.play_sound_effect("all_stars_full")
        except Exception as e:
            pass
    def get_star_frame(self, star_index):
        """Get the frame (0-5) for a specific star based on total progress"""
        # Calculate which frame this star should show
        # Each star has 6 frames (0-5), so star 0 uses progress 0-5, star 1 uses 6-11, etc.
        star_progress = self.total_progress - (star_index * 6)
        
        if star_progress <= 0:
            return 0  # Empty
        elif star_progress >= 6:
            return 5  # Full
        else:
            return star_progress  # Progressive fill (1-4)
    
    def add_star(self):
        """Add one star (if not at maximum) - legacy method for compatibility"""
        if self.current_stars < self.max_stars:
            self.current_stars += 1
    
    def remove_star(self):
        """Remove one star (if not at minimum) - legacy method for compatibility"""
        if self.current_stars > 0:
            self.current_stars -= 1
    
    def set_progress(self, progress):
        """Set progress directly (for testing)"""
        max_progress = self.max_stars * 6
        old_progress = self.total_progress
        self.total_progress = max(0, min(progress, max_progress))
        
        # Reset star full states based on new progress
        self._update_star_full_states()
        
        # Reset all stars played flag if not all stars are full
        if not all(self.star_full_states):
            self.all_stars_played = False
        
    
    def _update_star_full_states(self):
        """Update star full states based on current progress"""
        for star_index in range(self.max_stars):
            star_start = star_index * 6
            star_progress = max(0, self.total_progress - star_start)
            self.star_full_states[star_index] = (star_progress >= 5)
    
    def get_star_sprite(self, frame_index, size):
        """Get a scaled star sprite for the given frame"""
        if not self.star_spritesheet:
            return None
        
        # Create cache key
        cache_key = (frame_index, size)
        
        # Check if sprite is already cached
        if cache_key in self._cached_sprites:
            return self._cached_sprites[cache_key]
        
        # Extract frame from spritesheet
        frame_x = frame_index * self.frame_width
        frame_y = 0
        
        # Create surface for the frame
        frame_surface = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        frame_surface.blit(self.star_spritesheet, (0, 0), (frame_x, frame_y, self.frame_width, self.frame_height))
        
        # Scale the frame to the desired size
        scaled_sprite = pygame.transform.scale(frame_surface, (size, size))
        
        # Cache the result
        self._cached_sprites[cache_key] = scaled_sprite
        
        return scaled_sprite
    
    def draw(self, screen):
        """Draw the star UI on the screen"""
        if not self.star_spritesheet:
            # Draw fallback rectangles if spritesheet failed to load
            for i in range(self.max_stars):
                star_x = self.x
                star_y = self.y + (i * (self.star_size + self.star_spacing))
                
                # Draw empty star (gray rectangle)
                empty_rect = pygame.Rect(star_x, star_y, self.star_size, self.star_size)
                pygame.draw.rect(screen, (100, 100, 100), empty_rect)
                pygame.draw.rect(screen, (200, 200, 200), empty_rect, 2)
                
                # Draw filled star (yellow rectangle) if this star should be filled
                if i < self.current_stars:
                    filled_rect = pygame.Rect(star_x, star_y, self.star_size, self.star_size)
                    pygame.draw.rect(screen, (255, 255, 0), filled_rect)
            return
        
        # Draw stars using spritesheet (stacked vertically)
        for i in range(self.max_stars):
            star_x = self.x
            star_y = self.y + (i * (self.star_size + self.star_spacing))
            
            # Get the frame for this star based on total progress
            # Fill from bottom to top, so we need to reverse the star index
            bottom_star_index = self.max_stars - 1 - i
            frame_index = self.get_star_frame(bottom_star_index)
            
            # Get the appropriate star sprite
            star_sprite = self.get_star_sprite(frame_index, self.star_size)
            
            if star_sprite:
                screen.blit(star_sprite, (star_x, star_y))
    
    def get_rect(self):
        """Get the bounding rectangle of the entire star UI"""
        return pygame.Rect(self.x, self.y, self.total_width, self.total_height)
    
    def is_mouse_over(self, mouse_x, mouse_y):
        """Check if mouse is over the star UI"""
        return self.get_rect().collidepoint(mouse_x, mouse_y)
    
    def handle_click(self, mouse_x, mouse_y):
        """Handle mouse click on the star UI (for testing purposes)"""
        if not self.is_mouse_over(mouse_x, mouse_y):
            return False
        
        # Calculate which star was clicked (vertical layout)
        relative_y = mouse_y - self.y
        star_index = relative_y // (self.star_size + self.star_spacing)
        
        if 0 <= star_index < self.max_stars:
            # Toggle the clicked star and all stars before it
            new_star_count = star_index + 1
            if new_star_count == self.current_stars:
                # If clicking the last filled star, reduce by 1
                new_star_count = star_index
            
            self.set_stars(new_star_count)
            return True
        
        return False
