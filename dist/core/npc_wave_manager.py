"""
NPC Wave Manager
Handles steady stream NPC spawning system
"""

import random

class NPCWaveManager:
    """Manages NPC spawning with steady stream pattern"""
    
    def __init__(self, game_clock=None, difficulty_scaler=None):
        self.game_clock = game_clock
        self.difficulty_scaler = difficulty_scaler
        
        # Steady stream configuration
        self.base_spawn_interval = 8.0  # 8 seconds between spawns at base difficulty
        self.spawn_variance = 3.0  # ±3 seconds random variance
        self.npcs_per_spawn = (1, 1)  # Always spawn 1 NPC
        
        # State tracking
        self.last_spawn_time = -10.0  # Start with negative value so first spawn triggers immediately
        self.next_spawn_time = 2.0  # Start spawning 2 seconds after game starts
        
        # Overall limits
        self.base_max_npcs = 20  # Maximum NPCs in the gym at once at base difficulty
        self.total_npcs_spawned = 0
        
    def should_spawn_npc(self, current_time, npc_count, current_happiness=None):
        """Check if we should spawn NPCs using steady stream pattern"""
        # Calculate difficulty-adjusted limits
        max_npcs = self._get_max_npcs()
        if npc_count >= max_npcs:
            return False, 0
        
        # Calculate difficulty-adjusted spawn interval
        spawn_interval = self._get_spawn_interval(current_happiness)
        
        # Initialize next spawn time if not set
        if self.next_spawn_time == 0.0:
            self.next_spawn_time = current_time + spawn_interval + random.uniform(-self.spawn_variance, self.spawn_variance)
        
        # Check if it's time to spawn
        if current_time >= self.next_spawn_time:
            # Calculate next spawn time with variance
            self.next_spawn_time = current_time + spawn_interval + random.uniform(-self.spawn_variance, self.spawn_variance)
            return True, 1  # Always spawn 1 NPC
        
        return False, 0
    
    def spawn_npcs(self, current_time, spawn_count):
        """Spawn NPCs and update tracking data"""
        self.last_spawn_time = current_time
        
        # Update total count
        self.total_npcs_spawned += spawn_count
        
        return True
    
    def _get_max_npcs(self):
        """Get maximum NPCs based on difficulty"""
        if not self.difficulty_scaler:
            return self.base_max_npcs
        
        # Increase max NPCs with difficulty (up to 15% more)
        multiplier = self.difficulty_scaler.get_npc_spawn_multiplier()
        return int(self.base_max_npcs * (1.0 + (multiplier - 1.0) * 0.15))
    
    def _get_spawn_interval(self, current_happiness=None):
        """Get spawn interval based on difficulty"""
        if not self.difficulty_scaler:
            return self.base_spawn_interval
        
        # Decrease spawn interval with difficulty (faster spawning)
        multiplier = self.difficulty_scaler.get_npc_spawn_multiplier(current_happiness)
        return max(5.0, self.base_spawn_interval / (multiplier * 0.5))  # Minimum 5 seconds between spawns, much reduced scaling
    
    def get_difficulty_info(self, current_happiness=None):
        """Get current difficulty information for display"""
        if not self.difficulty_scaler:
            return {
                'level': 'Normal',
                'spawn_interval': self.base_spawn_interval,
                'max_npcs': self.base_max_npcs
            }
        
        return {
            'level': self.difficulty_scaler.get_difficulty_level(current_happiness),
            'spawn_interval': self._get_spawn_interval(current_happiness),
            'max_npcs': self._get_max_npcs(),
            'description': self.difficulty_scaler.get_difficulty_description(current_happiness)
        }
    
    def reset_wave_counts(self):
        """Reset spawn state (call at start of new day)"""
        self.last_spawn_time = -10.0  # Reset to trigger immediate spawning
        self.next_spawn_time = 0.0
        self.total_npcs_spawned = 0
