"""
Task Tracker
Tracks all tasks performed by the player during the game session
"""

class TaskTracker:
    """Tracks all tasks performed by the player"""
    
    def __init__(self):
        self.tasks = {
            "npcs_checked_in": 0,
            "machines_cleaned": 0,
            "dumbbells_returned": 0,
            "weight_plates_returned": 0,
            "floor_dumbbells_picked_up": 0,
            "floor_plates_picked_up": 0,
            "equipment_turned_off": 0,
            "gym_objects_interacted": 0,
            "total_tasks": 0
        }
        
        # Track additional statistics
        self.stats = {
            "total_npcs_served": 0,
            "happiness_events_triggered": 0,
            "time_played": 0.0,
            "efficiency_score": 0.0
        }
    
    def track_task(self, task_type):
        """Track a specific task type"""
        if task_type in self.tasks:
            self.tasks[task_type] += 1
            self.tasks["total_tasks"] += 1
            print(f"TASK TRACKER: {task_type} - Total: {self.tasks[task_type]}")
    
    def track_stat(self, stat_type, value=1):
        """Track a statistic"""
        if stat_type in self.stats:
            if stat_type == "time_played":
                self.stats[stat_type] = value
            else:
                self.stats[stat_type] += value
    
    def get_task_summary(self):
        """Get a summary of all tasks performed"""
        return {
            "tasks": self.tasks.copy(),
            "stats": self.stats.copy()
        }
    
    def calculate_efficiency_score(self):
        """Calculate efficiency score based on tasks performed"""
        # Base score from total tasks
        base_score = self.tasks["total_tasks"] * 8
        
        # Bonus for customer service (NPCs checked in)
        customer_service_bonus = self.tasks["npcs_checked_in"] * 20
        
        # Bonus for maintenance tasks
        maintenance_tasks = self.tasks["machines_cleaned"] + self.tasks["equipment_turned_off"]
        maintenance_bonus = maintenance_tasks * 12
        
        # Bonus for organization tasks
        organization_tasks = (self.tasks["dumbbells_returned"] + 
                            self.tasks["weight_plates_returned"] + 
                            self.tasks["floor_dumbbells_picked_up"] + 
                            self.tasks["floor_plates_picked_up"])
        organization_bonus = organization_tasks * 10
        
        # Bonus for variety across categories
        categories_with_tasks = 0
        if self.tasks["npcs_checked_in"] > 0 or self.tasks["gym_objects_interacted"] > 0:
            categories_with_tasks += 1
        if self.tasks["machines_cleaned"] > 0 or self.tasks["equipment_turned_off"] > 0:
            categories_with_tasks += 1
        if (self.tasks["dumbbells_returned"] > 0 or self.tasks["weight_plates_returned"] > 0 or 
            self.tasks["floor_dumbbells_picked_up"] > 0 or self.tasks["floor_plates_picked_up"] > 0):
            categories_with_tasks += 1
        
        variety_bonus = categories_with_tasks * 15
        
        # Time efficiency bonus (more tasks in less time = better)
        time_played = self.stats["time_played"]
        if time_played > 0:
            tasks_per_second = self.tasks["total_tasks"] / time_played
            time_efficiency_bonus = tasks_per_second * 50
        else:
            time_efficiency_bonus = 0
        
        efficiency = (base_score + customer_service_bonus + maintenance_bonus + 
                    organization_bonus + variety_bonus + time_efficiency_bonus)
        self.stats["efficiency_score"] = max(0, efficiency)
        
        return self.stats["efficiency_score"]
    
    def reset(self):
        """Reset all tracking data"""
        for task in self.tasks:
            self.tasks[task] = 0
        for stat in self.stats:
            if stat == "time_played":
                self.stats[stat] = 0.0
            else:
                self.stats[stat] = 0
