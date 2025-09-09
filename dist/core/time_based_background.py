"""
Time-Based Background System
Handles gradual background color changes based on time of day
"""

import pygame
import math

class TimeBasedBackground:
    """Manages time-based background color transitions"""
    
    def __init__(self):
        # Define time periods and their corresponding colors
        # Colors are defined as (R, G, B) tuples
        self.time_periods = {
            'dawn': (5, 6),      # 5:00 AM - 6:00 AM
            'morning': (6, 12),  # 6:00 AM - 12:00 PM
            'afternoon': (12, 17), # 12:00 PM - 5:00 PM
            'evening': (17, 20), # 5:00 PM - 8:00 PM
            'dusk': (20, 21),    # 8:00 PM - 9:00 PM
            'night': (21, 5)     # 9:00 PM - 5:00 AM (next day)
        }
        
        # Base colors for each time period (applied as tints to floor tiles)
        self.period_colors = {
            'dawn': (255, 200, 150),      # Warm orange-pink
            'morning': (255, 255, 200),   # Bright yellow-white
            'afternoon': (255, 255, 255), # Pure white (no tint)
            'evening': (255, 220, 180),   # Warm golden
            'dusk': (200, 150, 200),      # Purple-pink
            'night': (100, 100, 150)      # Cool blue-purple
        }
        
        # Intensity of the color effect (0.0 = no effect, 1.0 = full effect)
        self.color_intensity = 0.3
        
    def get_current_period(self, current_hour):
        """Get the current time period based on hour"""
        for period, (start_hour, end_hour) in self.time_periods.items():
            if period == 'night':
                # Night period wraps around midnight
                if current_hour >= start_hour or current_hour < end_hour:
                    return period
            else:
                if start_hour <= current_hour < end_hour:
                    return period
        return 'afternoon'  # Default fallback
    
    def get_color_tint(self, current_hour, current_minute=0):
        """Get the color tint to apply based on current time"""
        # Convert to decimal hours for smoother transitions
        decimal_hour = current_hour + (current_minute / 60.0)
        
        # Get current and next periods
        current_period = self.get_current_period(current_hour)
        next_period = self._get_next_period(current_period)
        
        # Calculate transition progress within the current period
        period_start, period_end = self.time_periods[current_period]
        
        if current_period == 'night':
            # Handle night period wrapping around midnight
            if current_hour >= period_start:
                # Before midnight
                period_progress = (decimal_hour - period_start) / (24 - period_start)
            else:
                # After midnight
                period_progress = (decimal_hour + (24 - period_start)) / (24 - period_start)
        else:
            period_progress = (decimal_hour - period_start) / (period_end - period_start)
        
        # Clamp progress between 0 and 1
        period_progress = max(0.0, min(1.0, period_progress))
        
        # Get colors for current and next periods
        current_color = self.period_colors[current_period]
        next_color = self.period_colors[next_period]
        
        # Interpolate between colors
        r = int(current_color[0] + (next_color[0] - current_color[0]) * period_progress)
        g = int(current_color[1] + (next_color[1] - current_color[1]) * period_progress)
        b = int(current_color[2] + (next_color[2] - current_color[2]) * period_progress)
        
        return (r, g, b)
    
    def _get_next_period(self, current_period):
        """Get the next time period after the current one"""
        period_order = ['dawn', 'morning', 'afternoon', 'evening', 'dusk', 'night']
        current_index = period_order.index(current_period)
        next_index = (current_index + 1) % len(period_order)
        return period_order[next_index]
    
    def apply_color_tint(self, surface, color_tint):
        """Apply a color tint to a surface"""
        if not surface:
            return surface
        
        # Create a copy of the surface to avoid modifying the original
        tinted_surface = surface.copy()
        
        # Create a color overlay
        overlay = pygame.Surface(tinted_surface.get_size(), pygame.SRCALPHA)
        overlay.fill((*color_tint, int(255 * self.color_intensity)))
        
        # Blend the overlay with the surface
        tinted_surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_MULT)
        
        return tinted_surface
    
    def get_background_color(self, current_hour, current_minute=0):
        """Get the background color for the entire screen based on time"""
        color_tint = self.get_color_tint(current_hour, current_minute)
        
        # Scale down the color for background (darker)
        bg_r = int(color_tint[0] * 0.1)
        bg_g = int(color_tint[1] * 0.1)
        bg_b = int(color_tint[2] * 0.1)
        
        return (bg_r, bg_g, bg_b)
