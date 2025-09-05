import pygame

class NPCCleaning:
    """Handles NPC cleaning behavior"""
    
    def __init__(self, npc):
        self.npc = npc
        self.cleaning_phase = None
        self.cleaning_bench_coords = None
        self.target_trashcan = None
    
    def should_clean_bench(self, obj_x, obj_y):
        """Check if NPC should clean the bench (40% chance if dirty)"""
        if (hasattr(self.npc, 'collision_system') and 
            hasattr(self.npc.collision_system, 'gym_manager') and 
            self.npc.collision_system.gym_manager):
            
            obj = self.npc.collision_system.gym_manager.get_object_at_tile(obj_x, obj_y)
            if obj and obj.has_state("dirty"):
                import random
                return random.random() < 0.4  # 40% chance
        
        return False
    
    def start_cleaning_behavior(self, bench_x, bench_y):
        """Start the cleaning behavior sequence"""
        if not hasattr(self.npc, 'collision_system') or not hasattr(self.npc.collision_system, 'gym_manager'):
            return
        
        gym_manager = self.npc.collision_system.gym_manager
        trashcan = self._find_nearest_trashcan(gym_manager)
        
        if not trashcan:
            self.npc._finish_gym_interaction_normally()
            return
        
        self.npc.hidden = False
        self.cleaning_bench_coords = (bench_x, bench_y)
        self._move_to_trashcan(trashcan)
    
    def update(self, delta_time):
        """Update cleaning behavior"""
        if not self.cleaning_phase:
            return
        
        if self.cleaning_phase == "going_to_trashcan":
            if self.npc.ai_state == "idle" and self.target_trashcan:
                self._return_to_bench()
            elif self.target_trashcan:
                distance = ((self.npc.x - self.target_trashcan.x) ** 2 + 
                           (self.npc.y - self.target_trashcan.y) ** 2) ** 0.5
                if distance < 20:
                    self._check_bench_and_return()
        
        elif self.cleaning_phase == "returning_to_bench":
            if self.npc.ai_state == "idle" and self.cleaning_bench_coords:
                self._complete_cleaning_sequence()
        
        elif self.cleaning_phase == "cleaning_bench":
            self._check_cleaning_completion()
    
    def _find_nearest_trashcan(self, gym_manager):
        """Find the nearest trashcan"""
        trashcans = gym_manager.get_gym_objects_by_type("trashcan")
        if not trashcans:
            return None
        
        nearest = None
        min_distance = float('inf')
        
        for trashcan in trashcans:
            distance = ((self.npc.x - trashcan.x) ** 2 + (self.npc.y - trashcan.y) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                nearest = trashcan
        
        return nearest
    
    def _move_to_trashcan(self, trashcan):
        """Move to trashcan position"""
        possible_targets = [
            (trashcan.x + 16, trashcan.y + 8),
            (trashcan.x - 16, trashcan.y + 8),
            (trashcan.x, trashcan.y + 35),
            (trashcan.x, trashcan.y - 16),
            (trashcan.x + 8, trashcan.y + 8),
            (trashcan.x - 8, trashcan.y + 8),
        ]
        
        self.target_trashcan = trashcan
        self.cleaning_phase = "going_to_trashcan"
        
        for target_x, target_y in possible_targets:
            self.npc.move_to_position(target_x, target_y)
            if self.npc.current_path and len(self.npc.current_path) > 0:
                self.npc.ai_state = "moving"
                self.npc.moving = True
                return
        
        self._abort_cleaning()
    
    def _check_bench_and_return(self):
        """Check if bench is still dirty and return to clean it"""
        if not self.cleaning_bench_coords:
            self._abort_cleaning()
            return
        
        bench_x, bench_y = self.cleaning_bench_coords
        if (hasattr(self.npc, 'collision_system') and 
            hasattr(self.npc.collision_system, 'gym_manager')):
            
            gym_manager = self.npc.collision_system.gym_manager
            obj = gym_manager.get_object_at_tile(bench_x, bench_y)
            
            if obj and obj.has_state("dirty"):
                self._return_to_bench()
            else:
                self._abort_cleaning()
        else:
            self._abort_cleaning()
    
    def _return_to_bench(self):
        """Return to bench to clean it"""
        if not self.cleaning_bench_coords:
            return
        
        bench_x, bench_y = self.cleaning_bench_coords
        target_x = bench_x * 16 + 8
        target_y = (bench_y + 1) * 16 + 8
        
        possible_positions = [
            (target_x, target_y),
            (target_x + 16, target_y),
            (target_x - 16, target_y),
            (target_x, target_y + 16),
            (target_x + 8, target_y + 8),
            (target_x - 8, target_y + 8),
        ]
        
        for pos_x, pos_y in possible_positions:
            self.npc.move_to_position(pos_x, pos_y)
            if self.npc.current_path and len(self.npc.current_path) > 0:
                self.npc.ai_state = "moving"
                self.npc.moving = True
                self.cleaning_phase = "returning_to_bench"
                return
        
        self._abort_cleaning()
    
    def _complete_cleaning_sequence(self):
        """Complete cleaning by cleaning the bench"""
        if not self.cleaning_bench_coords:
            return
        
        bench_x, bench_y = self.cleaning_bench_coords
        
        if (hasattr(self.npc, 'collision_system') and 
            hasattr(self.npc.collision_system, 'gym_manager')):
            
            gym_manager = self.npc.collision_system.gym_manager
            obj = gym_manager.get_object_at_tile(bench_x, bench_y)
            
            if obj and obj.has_state("dirty"):
                self.npc.hidden = False
                obj.start_cleaning()
                self.cleaning_phase = "cleaning_bench"
                self.npc.ai_state = "interacting"
                return
        
        self.npc._finish_gym_interaction_normally()
    
    def _check_cleaning_completion(self):
        """Check if cleaning animation is complete"""
        if not self.cleaning_bench_coords:
            return
        
        bench_x, bench_y = self.cleaning_bench_coords
        
        if (hasattr(self.npc, 'collision_system') and 
            hasattr(self.npc.collision_system, 'gym_manager')):
            
            gym_manager = self.npc.collision_system.gym_manager
            obj = gym_manager.get_object_at_tile(bench_x, bench_y)
            
            if obj:
                if not obj.has_state("dirty"):
                    self._abort_cleaning()
                    return
                
                if not (hasattr(obj, 'cleaning') and obj.cleaning):
                    self._finish_cleaning()
                    return
            else:
                self._abort_cleaning()
        else:
            self._abort_cleaning()
    
    def _finish_cleaning(self):
        """Finish cleaning sequence"""
        if self.cleaning_bench_coords:
            bench_x, bench_y = self.cleaning_bench_coords
            self.npc._update_last_gym_object_type_from_coords(bench_x, bench_y)
        
        self._clear_cleaning_state()
        
        if hasattr(self.npc, 'departure_pending') and self.npc.departure_pending:
            delattr(self.npc, 'departure_pending')
            exit_x = -80
            exit_y = 10 * 16 + 8
            self.npc.start_departure(exit_x, exit_y)
        else:
            self.npc._finish_gym_interaction_normally()
    
    def _abort_cleaning(self):
        """Abort cleaning sequence"""
        self._clear_cleaning_state()
        
        if hasattr(self.npc, 'departure_pending') and self.npc.departure_pending:
            delattr(self.npc, 'departure_pending')
            exit_x = -80
            exit_y = 10 * 16 + 8
            self.npc.start_departure(exit_x, exit_y)
        else:
            self.npc._finish_gym_interaction_normally()
    
    def _clear_cleaning_state(self):
        """Clear all cleaning-related state"""
        if hasattr(self.npc, 'cleaning_bench_coords'):
            delattr(self.npc, 'cleaning_bench_coords')
        if hasattr(self.npc, 'target_trashcan'):
            delattr(self.npc, 'target_trashcan')
        if hasattr(self.npc, 'cleaning_phase'):
            delattr(self.npc, 'cleaning_phase')
        
        self.cleaning_phase = None
        self.cleaning_bench_coords = None
        self.target_trashcan = None
