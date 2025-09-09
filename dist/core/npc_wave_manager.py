"""
NPC Wave Manager
Handles burst-based NPC spawning system
"""

import random

class NPCWaveManager:
    """Manages NPC spawning with burst pattern: 30 seconds active every 90 seconds"""
    
    def __init__(self, game_clock=None):
        self.game_clock = game_clock
        
        # Peak time configuration (early morning, afternoon, evening)
        self.peak_spawn_interval = 60.0  # 60 seconds between spawn chances
        self.peak_spawn_cooldown = 10.0  # 10 seconds between individual NPC spawns
        self.peak_spawns_per_cycle = 3   # 3 spawn chances per cycle
        self.peak_npcs_per_spawn = (1, 2)  # 1-2 NPCs per spawn chance
        
        # Non-peak time configuration
        self.non_peak_spawn_interval = 90.0  # 90 seconds between spawn chances
        self.non_peak_spawn_cooldown = 15.0  # 15 seconds between individual NPC spawns
        self.non_peak_spawns_per_cycle = 2   # 2 spawn chances per cycle
        self.non_peak_npcs_per_spawn = (1, 2)  # 1-2 NPCs per spawn chance
        
        # Peak time hours
        self.peak_hours = {
            "early_morning": (5, 7),    # 5-7 AM
            "afternoon": (13, 18),      # 1-6 PM
            "evening": (21, 23)         # 9-11 PM
        }
        
        # State tracking
        self.last_spawn_time = -30.0  # Start with negative value so first spawn triggers immediately
        self.spawns_this_cycle = 0
        self.cycle_start_time = 0.0
        
        # Overall limits
        self.max_total_npcs = 20  # Maximum NPCs in the gym at once
        self.total_npcs_spawned = 0
        
    def is_peak_time(self):
        """Check if current time is during peak hours"""
        if not self.game_clock:
            return False
            
        current_hour = self.game_clock.current_hour
        
        for wave_name, (start_hour, end_hour) in self.peak_hours.items():
            if start_hour <= current_hour < end_hour:
                return True
        return False
    
    def should_spawn_npc(self, current_time, npc_count):
        """Check if we should spawn NPCs using 6-spawn cycle pattern"""
        if npc_count >= self.max_total_npcs:
            return False, 0
        
        is_peak = self.is_peak_time()
        
        # Determine spawn configuration based on peak/non-peak
        if is_peak:
            spawn_interval = self.peak_spawn_interval
            spawn_cooldown = self.peak_spawn_cooldown
            spawns_per_cycle = self.peak_spawns_per_cycle
            npcs_per_spawn = self.peak_npcs_per_spawn
        else:
            spawn_interval = self.non_peak_spawn_interval
            spawn_cooldown = self.non_peak_spawn_cooldown
            spawns_per_cycle = self.non_peak_spawns_per_cycle
            npcs_per_spawn = self.non_peak_npcs_per_spawn
        
        # Check if we need to start a new cycle
        if self.spawns_this_cycle >= spawns_per_cycle:
            # Reset cycle
            self.spawns_this_cycle = 0
            self.cycle_start_time = current_time
        
        # Check if enough time has passed since last spawn
        if current_time - self.last_spawn_time >= spawn_cooldown:
            # Check if we're within the spawn interval for this cycle
            if self.spawns_this_cycle < spawns_per_cycle:
                # Random spawn count between min and max
                max_possible_spawns = min(npcs_per_spawn[1], self.max_total_npcs - npc_count)
                if max_possible_spawns > 0:
                    spawn_count = random.randint(npcs_per_spawn[0], max_possible_spawns)
                    return True, spawn_count
        
        return False, 0
    
    def spawn_npcs(self, current_time, spawn_count):
        """Spawn NPCs and update cycle data"""
        self.spawns_this_cycle += 1
        self.last_spawn_time = current_time
        
        # Update total count
        self.total_npcs_spawned += spawn_count
        
        return True
    
    def reset_wave_counts(self):
        """Reset spawn cycle state (call at start of new day)"""
        self.last_spawn_time = -30.0  # Reset to trigger immediate spawning
        self.spawns_this_cycle = 0
        self.cycle_start_time = 0.0
        self.total_npcs_spawned = 0
