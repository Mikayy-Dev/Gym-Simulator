"""
Base Screen State
Abstract base class for all screen states
"""

class BaseScreenState:
    """Base class for all screen states"""
    
    def __init__(self):
        pass
    
    def enter(self):
        """Called when entering this state"""
        pass
    
    def exit(self):
        """Called when exiting this state"""
        pass
    
    def update(self, delta_time, events):
        """Update state logic"""
        return None
    
    def draw(self, screen):
        """Draw state"""
        pass
