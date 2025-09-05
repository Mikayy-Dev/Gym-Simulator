"""
Game Clock System
Handles in-game time management
"""

class GameClock:
    """Manages in-game time"""
    
    def __init__(self):
        self.start_hour = 5  # 5 AM
        self.end_hour = 23   # 11 PM
        self.current_hour = 5
        self.current_minute = 0  # Start at 5:00 AM
        self.time_scale = 1.0  # 1 real second = 1 game minute
        self.timer = 0.0
        
    def update(self, delta_time):
        """Update the game clock"""
        self.timer += delta_time
        if self.timer >= self.time_scale:
            self.timer = 0.0
            self.current_minute += 1
            if self.current_minute >= 60:
                self.current_minute = 0
                self.current_hour += 1
                if self.current_hour >= 24:
                    self.current_hour = 0
    
    def get_time_string(self):
        """Get formatted time string"""
        # Format time as HH:MM AM/PM
        if self.current_hour == 0:
            display_hour = 12
            period = "AM"
        elif self.current_hour < 12:
            display_hour = self.current_hour
            period = "AM"
        elif self.current_hour == 12:
            display_hour = 12
            period = "PM"
        else:
            display_hour = self.current_hour - 12
            period = "PM"
        
        return f"{display_hour:02d}:{self.current_minute:02d} {period}"
    
    def is_gym_open(self):
        """Check if gym is currently open"""
        return self.start_hour <= self.current_hour < self.end_hour
