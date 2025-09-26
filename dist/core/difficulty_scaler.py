"""
Difficulty Scaling System
Handles progressive difficulty increases over time
"""

class DifficultyScaler:
    """Manages difficulty scaling based on game time and performance"""
    
    def __init__(self, game_clock):
        self.game_clock = game_clock
        self.base_difficulty = 1.0
        self.max_difficulty = 3.0
        
        # Time-based scaling
        self.time_scaling_factor = 0.08  # 8% increase per hour (reduced for easier progression)
        self.peak_hours = [17, 18, 19, 20]  # Evening rush hours
        
        # Performance-based scaling
        self.performance_scaling = True
        self.happiness_threshold = 50.0  # Below this, difficulty increases faster (reduced from 70%)
        
    def get_time_multiplier(self):
        """Calculate difficulty multiplier based on time of day"""
        current_hour = self.game_clock.current_hour
        
        # Base time scaling (gradual increase throughout the day)
        hours_elapsed = current_hour - self.game_clock.start_hour
        if hours_elapsed < 0:
            hours_elapsed = 0
        
        time_multiplier = 1.0 + (hours_elapsed * self.time_scaling_factor)
        
        # Peak hours bonus (evening rush)
        if current_hour in self.peak_hours:
            time_multiplier *= 1.15  # Reduced from 1.4 to 1.15 for gentler peak hours
        
        return min(time_multiplier, self.max_difficulty)
    
    def get_performance_multiplier(self, current_happiness):
        """Calculate difficulty multiplier based on current performance"""
        if not self.performance_scaling:
            return 1.0
        
        if current_happiness >= self.happiness_threshold:
            return 1.0  # No penalty for good performance
        else:
            # Scale difficulty inversely with happiness
            # At 0% happiness, multiplier is 1.5 (reduced from 2.0)
            # At 50% happiness, multiplier is 1.0
            performance_factor = 1.0 + (self.happiness_threshold - current_happiness) / self.happiness_threshold * 0.5
            return min(performance_factor, 1.5)
    
    def get_npc_spawn_multiplier(self, current_happiness=None):
        """Get multiplier for NPC spawning difficulty"""
        time_mult = self.get_time_multiplier()
        perf_mult = self.get_performance_multiplier(current_happiness) if current_happiness is not None else 1.0
        
        # Combine time and performance scaling
        return min(time_mult * perf_mult, self.max_difficulty)
    
    def get_happiness_decay_multiplier(self, current_happiness=None):
        """Get multiplier for happiness decay rate"""
        time_mult = self.get_time_multiplier()
        perf_mult = self.get_performance_multiplier(current_happiness) if current_happiness is not None else 1.0
        
        # Decay increases with difficulty
        return min(time_mult * perf_mult, self.max_difficulty)
    
    def get_penalty_multiplier(self, current_happiness=None):
        """Get multiplier for penalty severity"""
        time_mult = self.get_time_multiplier()
        perf_mult = self.get_performance_multiplier(current_happiness) if current_happiness is not None else 1.0
        
        # Penalties become harsher with difficulty
        return min(time_mult * perf_mult, self.max_difficulty)
    
    def get_equipment_maintenance_multiplier(self):
        """Get multiplier for equipment maintenance requirements"""
        time_mult = self.get_time_multiplier()
        
        # Equipment breaks down faster as time progresses
        return min(time_mult, self.max_difficulty)
    
    def get_npc_patience_multiplier(self):
        """Get multiplier for NPC patience (lower = more impatient)"""
        time_mult = self.get_time_multiplier()
        
        # NPCs become more impatient as time progresses
        return max(0.3, 1.0 / time_mult)  # Minimum 30% patience
    
    def get_equipment_breakdown_rate(self):
        """Get rate at which equipment breaks down (0.0 to 1.0)"""
        time_mult = self.get_time_multiplier()
        
        # Equipment breaks down more frequently as time progresses
        base_rate = 0.005  # 0.5% chance per update at base difficulty (reduced from 1%)
        return min(base_rate * time_mult, 0.02)  # Max 2% chance per update (reduced from 5%)
    
    def get_difficulty_level(self, current_happiness=None):
        """Get current difficulty level as a string"""
        time_mult = self.get_time_multiplier()
        perf_mult = self.get_performance_multiplier(current_happiness) if current_happiness is not None else 1.0
        total_mult = min(time_mult * perf_mult, self.max_difficulty)
        
        if total_mult < 1.2:
            return "Easy"
        elif total_mult < 1.8:
            return "Normal"
        elif total_mult < 2.2:
            return "Hard"
        else:
            return "Extreme"
    
    def get_difficulty_description(self, current_happiness=None):
        """Get description of current difficulty effects"""
        level = self.get_difficulty_level(current_happiness)
        time_mult = self.get_time_multiplier()
        perf_mult = self.get_performance_multiplier(current_happiness) if current_happiness is not None else 1.0
        
        descriptions = {
            "Easy": "Relaxed pace, forgiving penalties",
            "Normal": "Balanced challenge",
            "Hard": "Faster NPCs, harsher penalties",
            "Extreme": "Maximum pressure, equipment breaks frequently"
        }
        
        base_desc = descriptions.get(level, "Unknown")
        
        # Add specific details
        details = []
        if time_mult > 1.5:
            details.append("Peak hours")
        if perf_mult > 1.2:
            details.append("Performance pressure")
        
        if details:
            return f"{base_desc} ({', '.join(details)})"
        return base_desc
