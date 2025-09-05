import random
import pygame

class NPCBehavior:
    """Handles NPC behavior logic and decision making"""
    
    def __init__(self, npc):
        self.npc = npc
        self.behavior_timer = 0
        self.behavior_interval = 2
        self.last_gym_object_type = None
        self.gym_object_type_restriction = True
    
    def update(self, delta_time):
        """Update behavior logic"""
        if self.npc.is_departing or hasattr(self.npc, 'cleaning_phase'):
            return
        
        if self.npc.ai_state == "idle" and not hasattr(self.npc, 'manually_targeted') and self.npc.checked_in:
            self.behavior_timer += delta_time
            if self.behavior_timer >= self.behavior_interval:
                self._choose_new_behavior()
                self.behavior_timer = 0
    
    def _choose_new_behavior(self):
        """Choose a new behavior for the NPC"""
        if not self.npc.tilemap:
            return
        
        available_objects = self._get_available_objects()
        if available_objects:
            target = self._select_target(available_objects)
            if target:
                self.npc.move_to_object(target)
    
    def _get_available_objects(self):
        """Get available gym objects for targeting"""
        available_objects = []
        
        if (hasattr(self.npc, 'collision_system') and 
            hasattr(self.npc.collision_system, 'gym_manager') and 
            self.npc.collision_system.gym_manager):
            
            gym_manager = self.npc.collision_system.gym_manager
            for pos, obj in gym_manager.get_collision_objects():
                obj_type = gym_manager.object_types.get(pos)
                if obj_type not in ["front_desk", "trashcan"]:
                    collision_rect = obj.get_collision_rect()
                    if collision_rect:
                        available_objects.append(obj)
        
        return available_objects
    
    def _select_target(self, available_objects):
        """Select a target from available objects"""
        # Categorize objects by type
        benches = [obj for obj in available_objects if 'Bench' in type(obj).__name__]
        treadmills = [obj for obj in available_objects if 'Treadmill' in type(obj).__name__]
        dumbbell_racks = [obj for obj in available_objects if 'DumbbellRack' in type(obj).__name__ and obj.is_available()]
        squat_racks = [obj for obj in available_objects if 'SquatRack' in type(obj).__name__]
        
        # Apply restrictions
        if self.last_gym_object_type == "bench":
            benches = []
        elif self.last_gym_object_type == "treadmill":
            treadmills = []
        elif self.last_gym_object_type == "dumbbell_rack":
            dumbbell_racks = []
        elif self.last_gym_object_type == "squat_rack":
            squat_racks = []
        
        # Select preferred type or random
        preferred_type = self._get_preferred_type(benches, treadmills, dumbbell_racks, squat_racks)
        if preferred_type:
            chosen_type = preferred_type
        else:
            available_types = []
            if treadmills: available_types.append("Treadmill")
            if benches: available_types.append("Bench")
            if dumbbell_racks: available_types.append("DumbbellRack")
            if squat_racks: available_types.append("SquatRack")
            
            if available_types:
                chosen_type = random.choice(available_types)
            else:
                return None
        
        # Select random object from chosen type
        if chosen_type == "Treadmill":
            return random.choice(treadmills) if treadmills else None
        elif chosen_type == "Bench":
            return random.choice(benches) if benches else None
        elif chosen_type == "DumbbellRack":
            return random.choice(dumbbell_racks) if dumbbell_racks else None
        elif chosen_type == "SquatRack":
            return random.choice(squat_racks) if squat_racks else None
        
        return None
    
    def _get_preferred_type(self, benches, treadmills, dumbbell_racks, squat_racks):
        """Get preferred behavior type based on NPC's behavior_type"""
        if not hasattr(self.npc, 'behavior_type'):
            return None
        
        if self.npc.behavior_type == "dumbbell_user" and dumbbell_racks:
            return "DumbbellRack"
        elif self.npc.behavior_type == "bench_user" and benches:
            return "Bench"
        elif self.npc.behavior_type == "treadmill_user" and treadmills:
            return "Treadmill"
        elif self.npc.behavior_type == "squat_rack_user" and squat_racks:
            return "SquatRack"
        
        return None
    
    def update_last_gym_object_type(self, tile_id):
        """Update the last gym object type used"""
        gym_object_types = {
            0: "bench",
            1: "treadmill", 
            2: "dumbbell_rack",
            4: "squat_rack"
        }
        
        if tile_id in gym_object_types:
            self.last_gym_object_type = gym_object_types[tile_id]
