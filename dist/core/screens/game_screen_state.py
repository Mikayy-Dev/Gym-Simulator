"""
Game Screen State
Handles the main gameplay screen
"""

import pygame
from .base_screen_state import BaseScreenState
from ..camera import Camera
from ..tile_map import TileMap
from ..progress_bar import ProgressBar
from ..upgrade_point_manager import UpgradePointManager
from gym_objects import GymObjectManager
from ..npc import create_npc
from ..workout_zone import WorkoutZoneManager
from dialogue import DialogueManager, DialogueUI
from ..skill_points_inventory import SkillPointsInventory
from ..npc_happiness import NPCHappinessManager
from ..queue_manager import QueueManager
from ..task_tracker import TaskTracker
from ..difficulty_scaler import DifficultyScaler

class GameScreenState(BaseScreenState):
    """Handles the main game screen"""
    
    def __init__(self, audio_system=None, game_engine=None):
        super().__init__()
        self.initialized = False
        self.player = None
        self.camera = None
        self.tilemap = None
        self.gym_manager = None
        self.npcs = []
        self.progress_bar = None
        self.upgrade_point_manager = None
        self.game_clock = None
        self.npc_wave_manager = None
        self.audio_system = audio_system
        self.game_engine = game_engine
        self.current_cursor = "default"
        self.show_paths = False
        
        # Debug system
        self.show_entity_hitboxes = False
        self.show_gym_hitboxes = False
        self.show_interaction_hitboxes = False
        self._debug_points_applied = False
        self._debug_points_baseline = None
        
        # Dialogue system
        self.dialogue_manager = None
        self.dialogue_ui = None
        self._dialogue_zoom_active = False
        self._camera_zoom_target = None
        self._camera_base_zoom = None
        self._camera_zoom_speed = 2.0
        
        # Workout zone system
        self.workout_zone_manager = None
        
        # Skill points inventory
        self.skill_inventory = None
        
        # NPC happiness system
        self.npc_happiness = None
        
        # Queue management system
        self.queue_manager = None
        
        # Task tracking system
        self.task_tracker = None
        
        # Difficulty scaling
        self.difficulty_scaler = None
        
        # Real time tracking
        self.real_start_time = 0.0
        
        # Time overlay image
        self.time_overlay_image = None
        
        # Pre-game countdown overlay
        self.countdown_overlay_active = True
        self.countdown_overlay_timer = 0.0
        self.countdown_phases = [3, 2, 1, 0]  # 0 represents "GO!"
        self.current_countdown_phase = 0
        self.countdown_phase_duration = 1.0  # 1 second per phase
        self.countdown_sound_played = False
        
    def enter(self):
        """Called when entering the game state"""
        if not self.initialized:
            # Only reset when starting a completely new game (not from pause)
            self.reset_game_state()
            self._initialize_game()
        pygame.mouse.set_visible(False)
        # Ensure debug skill points are synced on enter
        self._sync_debug_skill_points()
    
    def exit(self):
        """Called when exiting the game state"""
        pygame.mouse.set_visible(True)
    
    def reset_game_state(self):
        """Reset the game state to initial values for a fresh start"""
        # Reset basic state variables first
        self.npcs = []
        self.countdown_overlay_active = True
        self.countdown_overlay_timer = 0.0
        self.current_countdown_phase = 0
        self.countdown_sound_played = False
        self._debug_points_applied = False
        self._debug_points_baseline = None
        
        # Reset components if they exist
        if self.progress_bar:
            self.progress_bar.reset()
        
        if self.upgrade_point_manager:
            self.upgrade_point_manager.set_points(0)
        
        if self.npc_happiness:
            self.npc_happiness.reset_happiness()
        
        if self.queue_manager:
            self.queue_manager.reset()
        
        if self.task_tracker:
            self.task_tracker.reset()
        
        if self.gym_manager:
            self.gym_manager.reset_all_objects()
        
        # Mark as needing re-initialization
        self.initialized = False
    
    def force_reset_and_enter(self):
        """Force a complete reset and enter the game state (for new games)"""
        self.reset_game_state()
        self.enter()
    
    def _initialize_game(self):
        """Initialize all game components"""
        # Initialize player
        self.player = Player(150, 220)
        
        # Initialize camera
        self.camera = Camera(1280, 720)
        
        # Initialize tilemap
        self.tilemap = TileMap("tilemap/gym2_Tile Layer 1.csv", "tilemap/gym2_Tile Layer 2.csv")
        self.player.set_tilemap(self.tilemap)
        self.tilemap.player = self.player
        
        # Initialize gym manager with difficulty scaler
        self.gym_manager = GymObjectManager(self.difficulty_scaler)
        self.gym_manager.setup_from_tilemap(self.tilemap)
        
        # Set up collision system
        if hasattr(self.player, 'collision_system'):
            self.player.collision_system.set_gym_manager(self.gym_manager)
        
        # Initialize NPCs
        self.npcs = []
        
        # Initialize progress bar
        self.progress_bar = ProgressBar(x=50, y=50, width=200, height=20, max_progress=100, difficulty_scaler=self.difficulty_scaler)
        
        # Initialize upgrade point manager
        self.upgrade_point_manager = UpgradePointManager(x=50, y=100, star_size=32)
        
        # Connect progress bar to upgrade point manager
        self.progress_bar.set_upgrade_point_manager(self.upgrade_point_manager)
        
        # Initialize game clock
        self.game_clock = GameClock()
        
        # Initialize difficulty scaler
        self.difficulty_scaler = DifficultyScaler(self.game_clock)
        
        # Connect game clock to tilemap for time-based effects
        self.tilemap.set_game_clock(self.game_clock)
        
        # Initialize NPC wave manager with difficulty scaler
        self.npc_wave_manager = NPCWaveManager(self.game_clock, self.difficulty_scaler)
        
        # Initialize dialogue system
        self.dialogue_manager = DialogueManager()
        self.dialogue_ui = DialogueUI(1280, 720)
        self.dialogue_manager.set_dialogue_ui(self.dialogue_ui)
        self.dialogue_manager.set_player(self.player)
        # Hook zoom on dialogue start/end
        self.dialogue_manager.on_dialogue_started = self._on_dialogue_started
        self.dialogue_manager.on_dialogue_ended = self._on_dialogue_ended
        
        # Initialize workout zone system
        self.workout_zone_manager = WorkoutZoneManager()
        self._setup_workout_zones()
        
        # Initialize skill points inventory
        self.skill_inventory = SkillPointsInventory(self.upgrade_point_manager, self.player)
        # Ensure the skill inventory has the correct player reference
        self.skill_inventory.set_player(self.player)
        
        
        # Initialize NPC happiness manager (uses gym object states)
        self.npc_happiness = NPCHappinessManager(
            self.gym_manager,
            get_management_level_fn=(self.skill_inventory.get_management_level if self.skill_inventory else None),
            x_offset=30,
            bar_height=300,
            difficulty_scaler=self.difficulty_scaler
        )
        
        # Initialize queue manager
        front_desks = self.gym_manager.get_gym_objects_by_type("front_desk")
        if front_desks:
            front_desk = front_desks[0]
            # Convert world coordinates to tile coordinates
            front_desk_tile_x = int(front_desk.x // 16)
            front_desk_tile_y = int(front_desk.y // 16)
            self.queue_manager = QueueManager((front_desk_tile_x, front_desk_tile_y))
        else:
            # Fallback to hardcoded position if no front desk found
            self.queue_manager = QueueManager((8, 10))  # Default front desk position
        
        # Initialize task tracker
        self.task_tracker = TaskTracker()
        
        # Set real start time
        self.real_start_time = pygame.time.get_ticks() / 1000.0
        
        # Load time overlay image
        try:
            self.time_overlay_image = pygame.image.load("Graphics/time_overlay.png")
        except pygame.error:
            self.time_overlay_image = None
        
        self.initialized = True
    
    def update(self, delta_time, events):
        """Update game logic"""
        if not self.initialized:
            return None
        
        # Sync debug skill points each frame in case debug mode toggled from settings
        self._sync_debug_skill_points()
        
        # Refresh player references to ensure they're always up to date
        self._refresh_player_references()

        # Handle input events
        for event in events:
            # Handle skill inventory input first (only when open)
            if self.skill_inventory and self.skill_inventory.handle_input(event):
                return None
            
            if event.type == pygame.KEYDOWN:
                action = self._handle_key_input(event)
                if action:
                    return action
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_input(event)
        
        # Update skill inventory (for feedback messages)
        if self.skill_inventory:
            self.skill_inventory.update()
        
        # Check if game should be paused due to skill inventory
        if self.skill_inventory and self.skill_inventory.game_paused:
            return None  # Skip game updates when paused
        
        # Update countdown overlay
        if self.countdown_overlay_active:
            # Play countdown sound effect once when countdown starts
            if not self.countdown_sound_played and self.audio_system:
                self.audio_system.play_sound("countdown")
                self.countdown_sound_played = True
            
            self.countdown_overlay_timer += delta_time
            if self.countdown_overlay_timer >= self.countdown_phase_duration:
                self.countdown_overlay_timer = 0.0
                self.current_countdown_phase += 1
                if self.current_countdown_phase >= len(self.countdown_phases):
                    self.countdown_overlay_active = False
                    # Start background music when countdown is complete
                    if self.audio_system:
                        self.audio_system.play_background_music(loop=True)
            
            # Center camera on player during countdown
            if self.camera and self.player:
                self.camera.follow(self.player)
            
            return None  # Skip game updates during countdown
        
        # Update game components
        self._update_game_components(delta_time)

        # Update NPC happiness manager (always updates while game runs)
        if hasattr(self, 'npc_happiness') and self.npc_happiness:
            try:
                self.npc_happiness.set_npc_count_for_decay(len(self.npcs))
            except Exception:
                pass
            self.npc_happiness.update(delta_time)
        
        # Update queue manager (handles timeouts and queue management)
        if hasattr(self, 'queue_manager') and self.queue_manager:
            self.queue_manager.update_queue_timeouts(delta_time)

        # Consume and apply any NPC happiness events raised this frame
        try:
            for npc in self.npcs:
                if hasattr(npc, 'happiness_event_dirty_machine') and npc.happiness_event_dirty_machine:
                    self.npc_happiness.on_dirty_machine_encountered()
                    delattr(npc, 'happiness_event_dirty_machine')
                if hasattr(npc, 'happiness_event_squat_plates_on_floor') and npc.happiness_event_squat_plates_on_floor:
                    self.npc_happiness.on_squat_rack_weights_on_floor()
                    delattr(npc, 'happiness_event_squat_plates_on_floor')
                if hasattr(npc, 'happiness_event_treadmill_unattended') and npc.happiness_event_treadmill_unattended:
                    self.npc_happiness.on_treadmill_unattended_running()
                    delattr(npc, 'happiness_event_treadmill_unattended')
                if hasattr(npc, 'happiness_event_dumbbell_empty') and npc.happiness_event_dumbbell_empty:
                    self.npc_happiness.on_dumbbell_rack_empty()
                    delattr(npc, 'happiness_event_dumbbell_empty')
                if hasattr(npc, 'happiness_event_queue_timeout') and npc.happiness_event_queue_timeout:
                    self.npc_happiness.on_queue_timeout()
                    delattr(npc, 'happiness_event_queue_timeout')
        except Exception:
            pass
        
        # Update progress bar
        if self.progress_bar:
            self.progress_bar.update(delta_time)
        
        # Update task tracker time
        if self.task_tracker:
            # Calculate time in seconds since game start
            time_in_seconds = (self.game_clock.current_hour - 5) * 3600 + self.game_clock.current_minute * 60
            self.task_tracker.track_stat("time_played", time_in_seconds)
        
        # Check if timer ran out - trigger evaluation screen
        if self.game_clock.current_hour >= 24:
            # Add a brief transition effect before switching
            return "Evaluation"
        
        # Check if happiness reached 0 - trigger fired screen
        if hasattr(self, 'npc_happiness') and self.npc_happiness and self.npc_happiness.current_happiness <= 0:
            # Calculate final score before transitioning
            self._calculate_final_score()
            return "Fired"
        
        return None
    
    def _calculate_final_score(self):
        """Calculate the final score for the game over screen"""
        # Calculate real time played in minutes
        current_real_time = pygame.time.get_ticks() / 1000.0
        time_played_seconds = current_real_time - self.real_start_time
        time_played_minutes = time_played_seconds / 60.0
        
        # Count NPCs served (total NPCs that have been in the gym)
        npcs_served = 0
        if self.npc_wave_manager:
            npcs_served = self.npc_wave_manager.total_npcs_spawned
        
        # Calculate score based on time played and NPCs served
        # Base score: 100 points per minute + 50 points per NPC served
        base_score = (time_played_minutes * 100) + (npcs_served * 50)
        
        # Bonus for management level
        management_bonus = 0
        if self.skill_inventory:
            management_level = self.skill_inventory.get_management_level()
            management_bonus = management_level * 100
        
        # Final score
        final_score = base_score + management_bonus
        
        # Store the score data for the fired screen
        self.final_score_data = {
            'score': int(final_score),
            'time_played': time_played_minutes,
            'npcs_served': npcs_served,
            'management_level': management_level if self.skill_inventory else 0
        }
    
    def _handle_key_input(self, event):
        """Handle keyboard input"""
        # Handle dialogue input first
        if self.dialogue_manager and self.dialogue_manager.handle_input(event):
            return None  # Dialogue handled the input
        
        if event.key == pygame.K_ESCAPE:
            return "Pause"
        elif event.key == pygame.K_TAB and self._is_debug_mode_enabled():
            # Toggle all hitbox visualizations
            self.show_entity_hitboxes = not self.show_entity_hitboxes
            self.show_gym_hitboxes = not self.show_gym_hitboxes
            self.tilemap.toggle_hitbox_debug()
        elif event.key == pygame.K_i:
            # Toggle skill points inventory (always available)
            if self.skill_inventory:
                self.skill_inventory.toggle()
        elif event.key == pygame.K_j and self._is_debug_mode_enabled():
            # Toggle interaction hitboxes (debug mode only)
            self.show_interaction_hitboxes = not self.show_interaction_hitboxes
        elif event.key == pygame.K_o and self._is_debug_mode_enabled():
            # Toggle NPC path visualization
            self.show_paths = not self.show_paths
            for npc in self.npcs:
                npc.show_paths = self.show_paths
        # Add other key handling here
    
    def _is_debug_mode_enabled(self):
        """Check if debug mode is enabled through settings"""
        if self.game_engine and hasattr(self.game_engine, 'debug_mode'):
            return self.game_engine.debug_mode
        return False

    def _sync_debug_skill_points(self):
        """Grant/remove 99 skill points when debug mode toggles"""
        if not hasattr(self, 'upgrade_point_manager') or not self.upgrade_point_manager:
            return
        debug_enabled = self._is_debug_mode_enabled()
        if debug_enabled and not self._debug_points_applied:
            # Save baseline and grant 99 points
            self._debug_points_baseline = self.upgrade_point_manager.get_points()
            self.upgrade_point_manager.set_points(99)
            self._debug_points_applied = True
        elif not debug_enabled and self._debug_points_applied:
            # Restore baseline points
            baseline = self._debug_points_baseline if self._debug_points_baseline is not None else 0
            self.upgrade_point_manager.set_points(baseline)
            self._debug_points_baseline = None
            self._debug_points_applied = False
    
    def _refresh_player_references(self):
        """Refresh all player references to ensure they're up to date"""
        if self.player and self.tilemap:
            self.tilemap.set_player(self.player)
            # Also ensure the skill inventory has the correct player reference
            if self.skill_inventory:
                self.skill_inventory.set_player(self.player)
    
    def _handle_mouse_input(self, event):
        """Handle mouse input"""
        if event.button == 1:  # Left click
            mouse_x, mouse_y = event.pos
            self._handle_left_click(mouse_x, mouse_y)
        elif event.button == 3:  # Right click
            mouse_x, mouse_y = event.pos
            self._handle_right_click(mouse_x, mouse_y)
    
    def _update_game_components(self, delta_time):
        """Update all game components"""
        # Update player
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        if self._dialogue_zoom_active and self.dialogue_manager and self.dialogue_manager.is_dialogue_active():
            npc = self.dialogue_manager.get_talking_npc()
            if npc:
                center_x = (self.player.x + npc.x) / 2
                center_y = (self.player.y + npc.y) / 2
                self.camera.center_on(center_x, center_y)
        else:
            self.camera.follow(self.player)
        self.player.update_stamina(delta_time)
        self.player.update_global_interruption_cooldown(delta_time)
        
        # Update gym objects
        self.gym_manager.update_all(delta_time)
        
        # Update NPCs and remove those that have left the gym
        npcs_to_remove = []
        for npc in self.npcs:
            # Setup chase target for interruption system
            if not npc.chase_target:
                npc.set_chase_target(self.player)
            
            # Check if NPC is ready for dialogue
            if npc.is_chasing_player:
                dialogue_ready = npc.update_chasing(delta_time)
                if dialogue_ready:
                    # Start dialogue with this NPC
                    self.dialogue_manager.start_dialogue(npc, "interruptions")
            
            npc.update(delta_time)
            # Check if NPC is ready to be removed (has left the gym)
            if hasattr(npc, 'is_ready_to_remove') and npc.is_ready_to_remove():
                npcs_to_remove.append(npc)
        
        # Remove NPCs that have left the gym
        for npc in npcs_to_remove:
            if hasattr(npc, 'cleanup'):
                npc.cleanup()  # Clean up any resources
            self.npcs.remove(npc)
        
        # Update game clock
        self.game_clock.update(delta_time)
        
        # Update dialogue system
        if self.dialogue_manager:
            self.dialogue_manager.update(delta_time)

        # Smooth camera zoom toward target
        if self._camera_zoom_target is not None and self.camera:
            current_zoom = self.camera.zoom
            target_zoom = self._camera_zoom_target
            if abs(current_zoom - target_zoom) < 0.01:
                self.camera.zoom = target_zoom
                if not self._dialogue_zoom_active:
                    self._camera_zoom_target = None
            else:
                # Use smooth interpolation instead of linear
                zoom_diff = target_zoom - current_zoom
                self.camera.zoom = current_zoom + zoom_diff * self._camera_zoom_speed * delta_time
        
        # Update cursor based on mouse position
        self._update_cursor()
        
        # Dynamic NPC spawning based on time waves
        current_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
        
        # Check if we should spawn NPCs
        current_happiness = self.npc_happiness.current_happiness if self.npc_happiness else None
        should_spawn, spawn_count = self.npc_wave_manager.should_spawn_npc(current_time, len(self.npcs), current_happiness)
        if should_spawn:
            # Spawn multiple NPCs off-screen to the left
            offscreen_spawn_x = -80  # Off-screen to the left
            entrance_y = 10 * 16 + 8  # Row 10, center of tile
            
            for i in range(spawn_count):
                # Stagger spawn positions slightly
                spawn_x = offscreen_spawn_x - (i * 20)  # Space them out horizontally
                
                # Create new NPC
                npc = create_npc(spawn_x, entrance_y)
                npc.set_tilemap(self.tilemap, self.gym_manager)
                npc.center_on_tile()
                npc.npc_id = len(self.npcs)  # Give unique ID based on current count
                npc.name = f"NPC_{npc.npc_id}"  # Simple name
                npc.arrival_time = current_time  # Set arrival time for departure system
                npc.show_paths = self.show_paths  # Set path visualization state
                
                # Ensure NPC's collision system has the gym manager
                if hasattr(npc, 'collision_system'):
                    npc.collision_system.set_gym_manager(self.gym_manager)
                
                # Set workout zone manager for the NPC
                if hasattr(npc, 'set_workout_zone_manager'):
                    npc.set_workout_zone_manager(self.workout_zone_manager)
                
                # Add to NPCs list
                self.npcs.append(npc)
                
                # Add to queue manager if it needs check-in
                if self.queue_manager and npc.needs_check_in:
                    self.queue_manager.add_npc_to_queue(npc)
            
            # Update wave manager
            self.npc_wave_manager.spawn_npcs(current_time, spawn_count)
            
            # Give all NPCs reference to updated list for queue management
            for existing_npc in self.npcs:
                existing_npc.all_npcs = self.npcs
    
    def _handle_left_click(self, mouse_x, mouse_y):
        """Handle left mouse click interactions"""
        
        # Check for returning items to racks using hitbox detection
        obj = self.gym_manager.get_object_at_mouse_position(mouse_x, mouse_y, self.camera)
        if obj:
            # Check if object is within player range using world coordinates
            world_x, world_y = self.camera.reverse_apply_pos(mouse_x, mouse_y)
            tile_x = int(world_x // 16)
            tile_y = int(world_y // 16)
            
            if self.tilemap.is_within_player_range(tile_x, tile_y):
                # Try to return dumbbells to rack
                if hasattr(obj, 'return_dumbbells_to_rack'):
                    success, message = obj.return_dumbbells_to_rack(self.player)
                    if success:
                        # Track task
                        if self.task_tracker:
                            self.task_tracker.track_task("dumbbells_returned")
                        
                        # Play dumbbell sound effect
                        if self.audio_system:
                            self.audio_system.play_sound("dumbbell")
                        
                        # Start charging for returning dumbbells
                        if self.progress_bar:
                            self.progress_bar.start_charging()
                        if self.npc_happiness:
                            self.npc_happiness.start_charging()
                
                # Try to return weight plates to rack
                if hasattr(obj, 'return_plates_to_rack') and self.player.weight_plate_count > 0:
                    success, message = obj.return_plates_to_rack(self.player)
                    if success:
                        # Track task
                        if self.task_tracker:
                            self.task_tracker.track_task("weight_plates_returned")
                        
                        # Play squat rerack sound effect
                        if self.audio_system:
                            self.audio_system.play_sound("squat_rerack")
                        
                        # Start charging for returning weight plates
                        if self.progress_bar:
                            self.progress_bar.start_charging()
                        if self.npc_happiness:
                            self.npc_happiness.start_charging()
    
    def _handle_right_click(self, mouse_x, mouse_y):
        """Handle right mouse click interactions"""
        world_x, world_y = self.camera.reverse_apply_pos(mouse_x, mouse_y)
        tile_x = int(world_x // 16)
        tile_y = int(world_y // 16)
        
        # First check if clicking on a non-checked-in NPC (within range)
        clicked_npc = self._get_npc_at_mouse_position(mouse_x, mouse_y)
        if (clicked_npc and not clicked_npc.checked_in and 
            self.tilemap.is_within_player_range(tile_x, tile_y)):
            # Use QueueManager to check in the NPC
            if self.queue_manager and self.queue_manager.check_in_npc(clicked_npc):
                # Track task
                if self.task_tracker:
                    self.task_tracker.track_task("npcs_checked_in")
                    self.task_tracker.track_stat("total_npcs_served")
                
                # Check-in successful
                # Play scanner sound effect
                if self.audio_system:
                    self.audio_system.play_sound("scanner")
                
                # Apply happiness bonus for successful check-in
                if self.npc_happiness:
                    self.npc_happiness.on_npc_checked_in()
            
            # Start charging for checking in NPC
            if self.progress_bar:
                self.progress_bar.start_charging()
            if self.npc_happiness:
                self.npc_happiness.start_charging()
        
        # Then check if clicking on floor dumbbells (within range)
        elif (self.tilemap.is_within_player_range(tile_x, tile_y) and 
              self.gym_manager.pickup_floor_dumbbells(mouse_x, mouse_y, self.camera, self.player, self.tilemap)):
            # Track task
            if self.task_tracker:
                self.task_tracker.track_task("floor_dumbbells_picked_up")
            
            # Successfully picked up dumbbells
            print("DEBUG: Successfully picked up dumbbells!")
            if self.progress_bar:
                self.progress_bar.start_charging()
            if self.npc_happiness:
                self.npc_happiness.start_charging()
        else:
            # Debug: Check why dumbbell pickup failed
            if self.tilemap.is_within_player_range(tile_x, tile_y):
                print(f"DEBUG: Player in range but dumbbell pickup failed - tile({tile_x},{tile_y})")
                # Check if there are any floor dumbbells at all
                for pos, obj in self.gym_manager.gym_objects.items():
                    if hasattr(obj, 'dumbbell_floor_sprites') and len(obj.dumbbell_floor_sprites) > 0:
                        print(f"DEBUG: Found {len(obj.dumbbell_floor_sprites)} floor sprites at {pos}")
                        for sprite_id, sprite_data in obj.dumbbell_floor_sprites.items():
                            print(f"DEBUG: Sprite {sprite_id}: world({sprite_data['x']},{sprite_data['y']}), count={sprite_data['count']}")
            else:
                print(f"DEBUG: Player not in range for dumbbell pickup - tile({tile_x},{tile_y})")
            
            # Then check for other interactions using hitbox detection
            obj = self.gym_manager.get_object_at_mouse_position(mouse_x, mouse_y, self.camera)
            if obj and self.tilemap.is_within_player_range(tile_x, tile_y):
                # Check if clicking on floor plates (only when actually on the squat rack)
                if hasattr(obj, 'is_mouse_over_floor_plates') and obj.is_mouse_over_floor_plates(mouse_x, mouse_y, self.camera):
                    if self.gym_manager.pickup_floor_plates(mouse_x, mouse_y, self.camera, self.player, self.tilemap):
                        # Track task
                        if self.task_tracker:
                            self.task_tracker.track_task("floor_plates_picked_up")
                        
                        # Successfully picked up plates - trigger happiness bonus
                        if self.npc_happiness:
                            self.npc_happiness.on_weights_organized()
                            self.npc_happiness.start_charging()
                        if self.progress_bar:
                            self.progress_bar.start_charging()
                
                # Check for other gym object interactions
                elif hasattr(obj, 'interact'):
                    obj.interact(self.player)
                    # Track task
                    if self.task_tracker:
                        self.task_tracker.track_task("gym_objects_interacted")
                    # Start charging for gym object interaction
                    if self.progress_bar:
                        self.progress_bar.start_charging()
                
                # Check for cleaning interactions
                elif obj.has_state("dirty"):
                    if self.audio_system:
                        self.audio_system.play_sound("spray_bottle")
                    if hasattr(obj, 'start_cleaning'):
                        obj.start_cleaning()
                        # Track task
                        if self.task_tracker:
                            self.task_tracker.track_task("machines_cleaned")
                        # Trigger happiness bonus for cleaning
                    if self.npc_happiness:
                        self.npc_happiness.on_machine_cleaned()
                        self.npc_happiness.start_charging()
                    if self.progress_bar:
                        self.progress_bar.start_charging()
                
                # Check for turning off equipment
                elif hasattr(obj, 'on_but_not_occupied') and obj.on_but_not_occupied:
                    if self.audio_system:
                        self.audio_system.play_sound("machine shutdown")
                    obj.turn_off()
                    # Track task
                    if self.task_tracker:
                        self.task_tracker.track_task("equipment_turned_off")
                    # Trigger happiness bonus for turning off treadmill
                    if self.npc_happiness:
                        self.npc_happiness.on_treadmill_turned_off()
                        self.npc_happiness.start_charging()
                    if self.progress_bar:
                        self.progress_bar.start_charging()
    
    def _get_npc_at_mouse_position(self, mouse_x, mouse_y):
        """Get NPC at mouse position"""
        world_x, world_y = self.camera.reverse_apply_pos(mouse_x, mouse_y)
        
        for npc in self.npcs:
            # Check if mouse is over NPC using their rect
            if hasattr(npc, 'rect') and npc.rect.collidepoint(world_x, world_y):
                return npc
        return None

    def _on_dialogue_started(self, npc):
        self._dialogue_zoom_active = True
        if self.camera:
            if self._camera_base_zoom is None:
                self._camera_base_zoom = self.camera.zoom
            self._camera_zoom_target = max(self.camera.zoom, 3.5)

    def _on_dialogue_ended(self, npc):
        self._dialogue_zoom_active = False
        if self.camera:
            base = self._camera_base_zoom if self._camera_base_zoom is not None else 3.0
            self._camera_zoom_target = base
    
    
    def _update_cursor(self):
        """Update cursor based on what's under the mouse"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        
        # Check if mouse is over a non-checked-in NPC
        clicked_npc = self._get_npc_at_mouse_position(mouse_x, mouse_y)
        if clicked_npc and not clicked_npc.checked_in:
            self.current_cursor = "scanner"
            return
        
        # Check if mouse is over floor dumbbells (for cursor change only)
        if self.gym_manager.is_mouse_over_floor_dumbbells(mouse_x, mouse_y, self.camera):
            self.current_cursor = "hand"
            return
        
        # Check if mouse is over an interactive gym object
        obj = self.gym_manager.get_object_at_mouse_position(mouse_x, mouse_y, self.camera)
        if obj:
            # Check if mouse is over floor plates (for cursor change only)
            if hasattr(obj, 'is_mouse_over_floor_plates') and obj.is_mouse_over_floor_plates(mouse_x, mouse_y, self.camera):
                self.current_cursor = "hand"
                return
            world_x, world_y = self.camera.reverse_apply_pos(mouse_x, mouse_y)
            tile_x = int(world_x // 16)
            tile_y = int(world_y // 16)
            
            if self.tilemap.is_within_player_range(tile_x, tile_y):
                # Check what type of interaction is available
                if obj.has_state("dirty"):
                    # Dirty equipment needs cleaning - use spray bottle cursor
                    self.current_cursor = "spray_bottle"
                    return
                elif (hasattr(obj, 'return_dumbbells_to_rack') or 
                      hasattr(obj, 'return_plates_to_rack') or
                      hasattr(obj, 'interact') or
                      (hasattr(obj, 'on_but_not_occupied') and obj.on_but_not_occupied)):
                    self.current_cursor = "hand"
                    return
        
        # Default cursor
        self.current_cursor = "default"
    
    def get_cursor_type(self):
        """Get the current cursor type for the game engine"""
        return self.current_cursor
    
    def draw(self, screen):
        """Draw the game"""
        if not self.initialized:
            return
        
        # Clear screen with time-based background color
        if self.game_clock:
            bg_color = self.tilemap.time_background.get_background_color(
                self.game_clock.current_hour, 
                self.game_clock.current_minute
            )
            screen.fill(bg_color)
        else:
            screen.fill("black")
        
        # Draw game components
        self.tilemap.draw_floors_only(screen, self.camera)
        self.tilemap.draw_walls_only(screen, self.camera)
        
        # Draw floor sprites first (behind everything)
        self._draw_floor_sprites(screen)
        
        # Draw all entities with depth sorting
        self._draw_entities_with_depth_sorting(screen)
        
        # Check if dialogue is active to hide overlays
        dialogue_active = self.dialogue_manager and self.dialogue_manager.is_dialogue_active()
        
        # Draw progress bar (hidden during dialogue)
        if self.progress_bar and not dialogue_active:
            self.progress_bar.draw(screen)
        
        # Draw tile highlighting (hidden during dialogue)
        if not dialogue_active:
            self.tilemap.draw_tile_highlight(screen, self.camera)
        
        # Draw game clock (hidden during dialogue)
        if not dialogue_active:
            self._draw_game_clock(screen)
        
        # Draw upgrade points (hidden during dialogue) - after game clock so it appears on top
        if self.upgrade_point_manager and not dialogue_active:
            self.upgrade_point_manager.draw(screen)
        
        # Draw debug hitboxes (hidden during dialogue)
        if not dialogue_active:
            self._draw_debug_hitboxes(screen)
        
        # Draw workout zones (debug) (hidden during dialogue)
        if self._is_debug_mode_enabled() and self.workout_zone_manager and not dialogue_active:
            self.workout_zone_manager.draw_debug(screen, self.camera)
        
        # Draw dialogue UI (always drawn when active)
        if self.dialogue_manager:
            self.dialogue_manager.draw(screen)
        
        # Draw skill points inventory (hidden during dialogue)
        if self.skill_inventory and not dialogue_active:
            self.skill_inventory.draw(screen)
        
        # Draw NPC happiness bar (right side) (hidden during dialogue)
        if hasattr(self, 'npc_happiness') and self.npc_happiness and not dialogue_active:
            # Calculate timer overlay center for alignment
            timer_center_x = None
            timer_height = None
            if self.time_overlay_image:
                timer_scale = 2.0
                timer_width = int(self.time_overlay_image.get_width() * timer_scale)
                timer_height = int(self.time_overlay_image.get_height() * timer_scale)
                timer_center_x = screen.get_width() - 10 - (timer_width // 2)
            self.npc_happiness.draw(screen, timer_center_x, timer_height)
        
        # Draw difficulty information (hidden during dialogue)
        if self.difficulty_scaler and not dialogue_active:
            self._draw_difficulty_info(screen)
        
        # Draw stamina bar (hidden during dialogue)
        if self.player and not dialogue_active:
            self.player.draw_stamina_bar(screen, self.camera)
        
        # Draw countdown overlay
        if self.countdown_overlay_active:
            self._draw_countdown_overlay(screen)
    
    def _draw_difficulty_info(self, screen):
        """Draw difficulty information on screen"""
        if not self.difficulty_scaler:
            return
        
        # Get difficulty information
        current_happiness = self.npc_happiness.current_happiness if self.npc_happiness else None
        difficulty_info = self.npc_wave_manager.get_difficulty_info(current_happiness) if self.npc_wave_manager else None
        
        if not difficulty_info:
            return
        
        # Load font
        try:
            font = pygame.font.Font("Font/Retro Gaming.ttf", 16)
        except:
            font = pygame.font.Font(None, 16)
        
        # Position in top-left corner, moved down
        x = 10
        y = 80
        
        # Draw difficulty level
        level_text = f"Difficulty: {difficulty_info['level']}"
        level_surface = font.render(level_text, True, (255, 255, 255))
        screen.blit(level_surface, (x, y))
        
        # Draw description
        if 'description' in difficulty_info:
            desc_text = difficulty_info['description']
            desc_surface = font.render(desc_text, True, (200, 200, 200))
            screen.blit(desc_surface, (x, y + 20))
        
        # Draw maintenance stats if available
        if self.gym_manager:
            maintenance_stats = self.gym_manager.get_maintenance_stats()
            if maintenance_stats['maintenance_required'] > 0:
                maint_text = f"Maintenance: {maintenance_stats['maintenance_required']}/{maintenance_stats['total_objects']}"
                maint_surface = font.render(maint_text, True, (255, 200, 0))
                screen.blit(maint_surface, (x, y + 60))
    
    def _draw_countdown_overlay(self, screen):
        """Draw the pre-game countdown overlay"""
        # Create a semi-transparent overlay
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Get the current countdown text
        if self.current_countdown_phase < len(self.countdown_phases):
            countdown_value = self.countdown_phases[self.current_countdown_phase]
            if countdown_value == 0:
                countdown_text = "GO!"
            else:
                countdown_text = f"{countdown_value}!"
        else:
            countdown_text = "GO!"
        
        # Create large font for countdown
        try:
            countdown_font = pygame.font.Font("Font/Retro Gaming.ttf", 120)
        except:
            countdown_font = pygame.font.Font(None, 120)
        
        # Render countdown text
        text_surface = countdown_font.render(countdown_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = (screen.get_width() // 2, screen.get_height() // 2)
        
        # Draw countdown text
        screen.blit(text_surface, text_rect)
    
    def _draw_floor_sprites(self, screen):
        """Draw floor sprites (dropped items) for all gym objects"""
        for obj in self.gym_manager.gym_objects.values():
            try:
                # Draw floor sprites if the object has them
                if hasattr(obj, '_draw_floor_dumbbells') and hasattr(obj, 'dumbbell_floor_sprites') and len(obj.dumbbell_floor_sprites) > 0:
                    obj._draw_floor_dumbbells(screen, self.camera)
                if hasattr(obj, '_draw_floor_plates') and hasattr(obj, 'plate_floor_sprites') and len(obj.plate_floor_sprites) > 0:
                    obj._draw_floor_plates(screen, self.camera)
            except Exception as e:
                pass
    
    def _draw_entities_with_depth_sorting(self, screen):
        """Draw all entities sorted by Y position for proper depth"""
        # Collect all drawable entities
        entities = []
        
        # Add gym objects using proper depth calculation
        for depth_y, pos, obj in self.gym_manager.get_depth_sorted_objects():
            entities.append((depth_y, obj, 'gym_object'))
        
        # Add NPCs with center Y position
        for npc in self.npcs:
            npc_y = npc.y + 16  # NPC's center Y position
            entities.append((npc_y, npc, 'npc'))
        
        # Add player with center Y position
        player_y = self.player.y + 16  # Player's center Y position
        entities.append((player_y, self.player, 'player'))
        
        # Sort by Y position (depth) - higher Y renders first/behind
        entities.sort(key=lambda x: x[0])
        
        # Draw entities in depth order
        for y_pos, entity, entity_type in entities:
            if entity_type == 'gym_object':
                entity.draw(screen, self.camera)
            elif entity_type == 'npc':
                entity.draw(screen, self.camera)
            elif entity_type == 'player':
                entity.draw(screen, self.camera)
                # Draw player inventory
                entity.draw_dumbbell_inventory(screen, self.camera)
                entity.draw_weight_plate_inventory(screen, self.camera)
    
    def _draw_game_clock(self, screen):
        """Draw the game clock and score"""
        # Draw time overlay image first if available
        if self.time_overlay_image:
            # Scale the overlay image to be larger
            scale_factor = 2.0
            original_width = self.time_overlay_image.get_width()
            original_height = self.time_overlay_image.get_height()
            scaled_width = int(original_width * scale_factor)
            scaled_height = int(original_height * scale_factor)
            
            scaled_overlay = pygame.transform.scale(self.time_overlay_image, (scaled_width, scaled_height))
            overlay_rect = scaled_overlay.get_rect()
            overlay_rect.topright = (screen.get_width() - 10, 10)  # Moved closer to corner
            screen.blit(scaled_overlay, overlay_rect)
        
        try:
            clock_font = pygame.font.Font("Font/Retro Gaming.ttf", 14)
            score_font = pygame.font.Font("Font/Retro Gaming.ttf", 12)
        except:
            clock_font = pygame.font.Font(None, 14)
            score_font = pygame.font.Font(None, 12)
        
        # Position text within the scaled overlay
        if self.time_overlay_image:
            # Position text within the scaled overlay area
            text_x = screen.get_width() - 10 - (scaled_width // 2)  # Adjusted for new overlay position
            text_y = 10 + (scaled_height // 3)  # Adjusted for new overlay position
        else:
            # Fallback positioning if no overlay
            text_x = screen.get_width() - 20
            text_y = 20
        
        # Draw score if task tracker is available
        if self.task_tracker:
            score = int(self.task_tracker.calculate_efficiency_score())
            score_text = score_font.render(f"SCORE: {score}", True, (255, 255, 255))
            score_rect = score_text.get_rect()
            score_rect.centerx = text_x
            score_rect.centery = text_y
            screen.blit(score_text, score_rect)
        
    
    def _draw_debug_hitboxes(self, screen):
        """Draw debug hitboxes for entities and gym objects"""
        if self.show_entity_hitboxes:
            self._draw_entity_hitboxes(screen)
        
        if self.show_gym_hitboxes:
            self._draw_gym_hitboxes(screen)
        
        if self.show_interaction_hitboxes:
            self._draw_interaction_hitboxes(screen)
    
    def _draw_entity_hitboxes(self, screen):
        """Draw hitboxes for player and NPCs"""
        # Draw player hitboxes
        self._draw_player_hitboxes(screen)
        
        # Draw NPC hitboxes
        for npc in self.npcs:
            self._draw_npc_hitboxes(screen, npc)
    
    def _draw_player_hitboxes(self, screen):
        """Draw player hitboxes"""
        if not hasattr(self.player, 'hitboxes'):
            return
        
        # Convert player position to screen coordinates
        screen_x, screen_y = self.camera.apply_pos(self.player.x, self.player.y)
        
        # Draw each hitbox
        for hitbox_name, hitbox_info in self.player.hitboxes.items():
            # Calculate hitbox position relative to player's top-left corner
            hitbox_x = screen_x + hitbox_info["x"] * self.camera.zoom
            hitbox_y = screen_y + hitbox_info["y"] * self.camera.zoom
            hitbox_width = hitbox_info["width"] * self.camera.zoom
            hitbox_height = hitbox_info["height"] * self.camera.zoom
            
            # Draw hitbox rectangle
            hitbox_rect = pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)
            
            # Use different colors for different hitbox types
            if hitbox_name == "body":
                color = (255, 0, 0)  # Red for body
            elif hitbox_name == "feet":
                color = (0, 255, 0)  # Green for feet
            else:
                color = (255, 255, 0)  # Yellow for other hitboxes
            
            pygame.draw.rect(screen, color, hitbox_rect, 2)
            
            # Draw hitbox label
            font = pygame.font.Font(None, 16)
            label = font.render(f"P_{hitbox_name}", True, color)
            screen.blit(label, (hitbox_x, hitbox_y - 15))
    
    def _draw_npc_hitboxes(self, screen, npc):
        """Draw NPC hitboxes"""
        if not hasattr(npc, 'hitboxes'):
            return
        
        # Convert NPC position to screen coordinates
        screen_x, screen_y = self.camera.apply_pos(npc.x, npc.y)
        
        # Draw each hitbox
        for hitbox_name, hitbox_info in npc.hitboxes.items():
            # Calculate hitbox position relative to NPC center
            hitbox_x = screen_x + (hitbox_info["x"] - npc.sprite_width // 2) * self.camera.zoom
            hitbox_y = screen_y + (hitbox_info["y"] - npc.sprite_height // 2) * self.camera.zoom
            hitbox_width = hitbox_info["width"] * self.camera.zoom
            hitbox_height = hitbox_info["height"] * self.camera.zoom
            
            # Draw hitbox rectangle
            hitbox_rect = pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)
            
            # Use different colors for different hitbox types
            if hitbox_name == "body":
                color = (255, 100, 100)  # Light red for NPC body
            elif hitbox_name == "feet":
                color = (100, 255, 100)  # Light green for NPC feet
            else:
                color = (255, 255, 100)  # Light yellow for other hitboxes
            
            pygame.draw.rect(screen, color, hitbox_rect, 2)
            
            # Draw hitbox label
            font = pygame.font.Font(None, 16)
            # Add (HIDDEN) indicator if NPC is hidden
            hidden_text = " (HIDDEN)" if npc.hidden else ""
            label = font.render(f"N{npc.npc_id}_{hitbox_name}{hidden_text}", True, color)
            screen.blit(label, (hitbox_x, hitbox_y - 15))
    
    def _draw_gym_hitboxes(self, screen):
        """Draw gym object collision hitboxes"""
        for pos, obj in self.gym_manager.gym_objects.items():
            collision_rect = obj.get_collision_rect()
            if collision_rect:
                screen_rect = self.camera.apply_rect(collision_rect)
                pygame.draw.rect(screen, (255, 0, 0), screen_rect, 2)
                
                center_x = screen_rect.centerx
                center_y = screen_rect.centery
                pygame.draw.circle(screen, (255, 0, 0), (center_x, center_y), 3)
    
    def _draw_interaction_hitboxes(self, screen):
        """Draw gym object interaction hitboxes"""
        for pos, obj in self.gym_manager.gym_objects.items():
            try:
                # Get the object's interaction rectangle
                interaction_rect = obj.get_interaction_rect()
                
                # Apply camera transformation
                screen_rect = self.camera.apply_rect(interaction_rect)
                
                # Draw the interaction hitbox (blue outline)
                pygame.draw.rect(screen, (0, 0, 255), screen_rect, 2)
                
                # Draw interaction hitbox center point
                center_x = screen_rect.centerx
                center_y = screen_rect.centery
                pygame.draw.circle(screen, (0, 0, 255), (center_x, center_y), 3)
                
            except Exception as e:
                pass
    
    def _setup_workout_zones(self):
        """Set up workout zones for the gym"""
        # Define a workout zone in the red outlined area that encompasses
        # the dumbbell racks and gym equipment
        # Based on the image, this covers most of the gym floor
        dumbbell_zone_x = 2 * 16  # Start from column 2 (tile coordinates)
        dumbbell_zone_y = 2 * 16  # Start from row 2 (tile coordinates)
        dumbbell_zone_width = 10 * 16  # 10 tiles wide (reduced by 8 tiles from right)
        dumbbell_zone_height = 6 * 16  # 14 tiles tall (covers the equipment area)
        
        self.workout_zone_manager.add_zone(
            dumbbell_zone_x, 
            dumbbell_zone_y, 
            dumbbell_zone_width, 
            dumbbell_zone_height, 
            "dumbbell"
        )
    

# Import the classes we need
from ..player import Player
from ..game_clock import GameClock
from ..npc_wave_manager import NPCWaveManager
