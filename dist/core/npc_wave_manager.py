"""
NPC Wave Manager
Handles dynamic NPC spawning based on time waves
"""

import random

class NPCWaveManager:
    """Manages NPC spawning waves based on game time"""
    
    def __init__(self, game_clock=None):
        self.game_clock = game_clock
        self.waves = {
            "early_morning": {
                "start_hour": 5,
                "end_hour": 7,
                "spawn_interval": 20,  # seconds between spawns
                "spawn_count_range": (1, 2),  # Random range of NPCs to spawn
                "spawned_count": 0,
                "last_spawn_time": 0
            },
            "afternoon": {
                "start_hour": 13,
                "end_hour": 18,
                "spawn_interval": 20,  # seconds between spawns
                "spawn_count_range": (1, 2),  # Random range of NPCs to spawn
                "spawned_count": 0,
                "last_spawn_time": 0
            },
            "evening": {
                "start_hour": 21,
                "end_hour": 23,
                "spawn_interval": 20,  # seconds between spawns
                "spawn_count_range": (1, 2),  # Random range of NPCs to spawn
                "spawned_count": 0,
                "last_spawn_time": 0
            }
        }
        self.total_npcs_spawned = 0
        self.max_total_npcs = 20  # Maximum NPCs in the gym at once
        
    def get_current_wave(self):
        """Get the current wave based on game time"""
        if not self.game_clock:
            return None, None
            
        current_hour = self.game_clock.current_hour
        
        for wave_name, wave_data in self.waves.items():
            if wave_data["start_hour"] <= current_hour < wave_data["end_hour"]:
                return wave_name, wave_data
        
        return None, None
    
    def is_in_between_time(self):
        """Check if current time is in between active wave periods"""
        if not self.game_clock:
            return False
            
        current_hour = self.game_clock.current_hour
        # In-between times: 9am-1pm, 6pm-9pm, 11pm-5am
        return (9 <= current_hour < 13) or (18 <= current_hour < 21) or (current_hour >= 23 or current_hour < 5)
    
    def should_spawn_npc(self, current_time, npc_count):
        """Check if we should spawn NPCs"""
        if npc_count >= self.max_total_npcs:
            return False, 0
            
        wave_name, wave_data = self.get_current_wave()
        
        # Check if we're in an active wave period
        if wave_data:
            # Special check for early morning wave - don't start until 5:05 AM
            if wave_name == "early_morning":
                # This would need game clock integration
                pass
            
            # Check if enough time has passed since last spawn
            if current_time - wave_data["last_spawn_time"] >= wave_data["spawn_interval"]:
                # Random spawn count between 1-4
                spawn_count = random.randint(wave_data["spawn_count_range"][0], wave_data["spawn_count_range"][1])
                return True, spawn_count
        # Check if we're in between times with 50% chance
        elif self.is_in_between_time():
            if random.random() < 0.5:  # 50% chance
                # Random spawn count between 1-4
                spawn_count = random.randint(1, 4)
                return True, spawn_count
                
        return False, 0
    
    def spawn_npcs(self, current_time, spawn_count):
        """Spawn multiple NPCs and update wave data"""
        wave_name, wave_data = self.get_current_wave()
        
        # Update wave data if we're in an active wave
        if wave_data:
            wave_data["last_spawn_time"] = current_time
        
        # Update total count
        self.total_npcs_spawned += spawn_count
        
        return True
    
    def reset_wave_counts(self):
        """Reset spawn counts for all waves (call at start of new day)"""
        for wave_data in self.waves.values():
            wave_data["spawned_count"] = 0
        self.total_npcs_spawned = 0
