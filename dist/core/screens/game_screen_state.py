"""
Game Screen State
Handles the main gameplay screen
"""

import pygame
from .base_screen_state import BaseScreenState
from ..camera import Camera
from ..tile_map import TileMap
from ..star_ui import StarUI
from gym_objects import GymObjectManager
from ..npc import create_npc
from dialogue import DialogueManager, DialogueUI

class GameScreenState(BaseScreenState):
    """Handles the main game screen"""
    
    def __init__(self, audio_system=None):
        super().__init__()
        self.initialized = False
        self.player = None
        self.camera = None
        self.tilemap = None
        self.gym_manager = None
        self.npcs = []
        self.star_ui = None
        self.game_clock = None
        self.npc_wave_manager = None
        self.audio_system = audio_system
        self.current_cursor = "default"
        self.show_paths = False
        
        # Debug system
        self.show_entity_hitboxes = False
        self.show_gym_hitboxes = False
        self.show_interaction_hitboxes = False
        
        # Dialogue system
        self.dialogue_manager = None
        self.dialogue_ui = None
        
    def enter(self):
        """Called when entering the game state"""
        if not self.initialized:
            self._initialize_game()
        pygame.mouse.set_visible(False)
    
    def exit(self):
        """Called when exiting the game state"""
        pygame.mouse.set_visible(True)
    
    def _initialize_game(self):
        """Initialize all game components"""
        # Initialize player
        self.player = Player(320, 208)
        
        # Initialize camera
        self.camera = Camera(1280, 720)
        
        # Initialize tilemap
        self.tilemap = TileMap("tilemap/gym2_Tile Layer 1.csv", "tilemap/gym2_Tile Layer 2.csv")
        self.player.set_tilemap(self.tilemap)
        self.tilemap.player = self.player
        
        # Initialize gym manager
        self.gym_manager = GymObjectManager()
        self.gym_manager.setup_from_tilemap(self.tilemap)
        
        # Set up collision system
        if hasattr(self.player, 'collision_system'):
            self.player.collision_system.set_gym_manager(self.gym_manager)
        
        # Initialize NPCs
        self.npcs = []
        
        # Initialize star UI
        audio_manager = self.audio_system.audio_manager if self.audio_system else None
        self.star_ui = StarUI(x=1200, y=300, max_stars=5, star_size=64, audio_manager=audio_manager)
        
        # Initialize game clock
        self.game_clock = GameClock()
        
        # Initialize NPC wave manager
        self.npc_wave_manager = NPCWaveManager(self.game_clock)
        
        # Initialize dialogue system
        self.dialogue_manager = DialogueManager()
        self.dialogue_ui = DialogueUI(1280, 720)
        self.dialogue_manager.set_dialogue_ui(self.dialogue_ui)
        self.dialogue_manager.set_player(self.player)
        
        self.initialized = True
    
    def update(self, delta_time, events):
        """Update game logic"""
        if not self.initialized:
            return None
        
        # Handle input events
        for event in events:
            if event.type == pygame.KEYDOWN:
                self._handle_key_input(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_input(event)
        
        # Update game components
        self._update_game_components(delta_time)
        
        return None
    
    def _handle_key_input(self, event):
        """Handle keyboard input"""
        # Handle dialogue input first
        if self.dialogue_manager and self.dialogue_manager.handle_input(event):
            return None  # Dialogue handled the input
        
        if event.key == pygame.K_ESCAPE:
            return "Back to Title"
        elif event.key == pygame.K_TAB:
            # Toggle all hitbox visualizations
            self.show_entity_hitboxes = not self.show_entity_hitboxes
            self.show_gym_hitboxes = not self.show_gym_hitboxes
            self.tilemap.toggle_hitbox_debug()
        elif event.key == pygame.K_i:
            # Toggle interaction hitboxes
            self.show_interaction_hitboxes = not self.show_interaction_hitboxes
        elif event.key == pygame.K_p:
            # Toggle NPC path visualization
            self.show_paths = not self.show_paths
            for npc in self.npcs:
                npc.show_paths = self.show_paths
        # Add other key handling here
    
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
        self.camera.follow(self.player)
        self.player.update_stamina(delta_time)
        
        # Update gym objects
        self.gym_manager.update_all(delta_time)
        
        # Update NPCs and remove those that have left the gym
        npcs_to_remove = []
        for npc in self.npcs:
            # Setup chase target for interruption system
            if not npc.chase_target:
                npc.set_chase_target(self.player)
                personality = "extroverted" if npc.is_extroverted() else "introverted"
                print(f"DEBUG: Set chase target for {personality} NPC {npc.npc_id}")
            
            # Check if NPC is ready for dialogue
            if npc.is_chasing_player:
                dialogue_ready = npc.update_chasing(delta_time)
                if dialogue_ready:
                    # Start dialogue with this NPC
                    import random
                    dialogue_type = random.choice(["greeting", "equipment_tip", "form_advice"])
                    self.dialogue_manager.start_dialogue(npc, dialogue_type)
                    print(f"DEBUG: Started dialogue with NPC {npc.npc_id}")
            
            npc.update(delta_time)
            # Check if NPC is ready to be removed (has left the gym)
            if hasattr(npc, 'is_ready_to_remove') and npc.is_ready_to_remove():
                npcs_to_remove.append(npc)
        
        # Remove NPCs that have left the gym
        for npc in npcs_to_remove:
            if hasattr(npc, 'cleanup'):
                npc.cleanup()  # Clean up any resources
            self.npcs.remove(npc)
            print(f"DEBUG: Removed NPC {npc.npc_id} from game")
        
        # Update game clock
        self.game_clock.update(delta_time)
        
        # Update dialogue system
        if self.dialogue_manager:
            self.dialogue_manager.update(delta_time)
        
        # Update cursor based on mouse position
        self._update_cursor()
        
        # Dynamic NPC spawning based on time waves
        current_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
        
        # Check if we should spawn NPCs
        should_spawn, spawn_count = self.npc_wave_manager.should_spawn_npc(current_time, len(self.npcs))
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
                
                # Add to NPCs list
                self.npcs.append(npc)
            
            # Update wave manager
            self.npc_wave_manager.spawn_npcs(current_time, spawn_count)
            
            # Give all NPCs reference to updated list for queue management
            for existing_npc in self.npcs:
                existing_npc.all_npcs = self.npcs
    
    def _handle_left_click(self, mouse_x, mouse_y):
        """Handle left mouse click interactions"""
        # Check if clicking on star UI
        if self.star_ui.handle_click(mouse_x, mouse_y):
            # Star UI handled the click
            return
        
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
                        # Play dumbbell sound effect
                        if self.audio_system:
                            self.audio_system.play_sound("dumbbell")
                        
                        # Reward for returning dumbbells
                        self.star_ui.add_progress(1)
                
                # Try to return weight plates to rack
                if hasattr(obj, 'return_plates_to_rack') and self.player.weight_plate_count > 0:
                    success, message = obj.return_plates_to_rack(self.player)
                    if success:
                        # Play squat rerack sound effect
                        if self.audio_system:
                            self.audio_system.play_sound("squat_rerack")
                        
                        # Reward for returning weight plates
                        self.star_ui.add_progress(1)
    
    def _handle_right_click(self, mouse_x, mouse_y):
        """Handle right mouse click interactions"""
        world_x, world_y = self.camera.reverse_apply_pos(mouse_x, mouse_y)
        tile_x = int(world_x // 16)
        tile_y = int(world_y // 16)
        
        # First check if clicking on a non-checked-in NPC (within range)
        clicked_npc = self._get_npc_at_mouse_position(mouse_x, mouse_y)
        if (clicked_npc and not clicked_npc.checked_in and 
            self.tilemap.is_within_player_range(tile_x, tile_y)):
            # Check in the NPC
            clicked_npc.checked_in = True
            clicked_npc.needs_check_in = False
            
            # Advance queue: move all NPCs behind this one forward
            self._advance_queue_after_checkin(clicked_npc)
            
            # Play scanner sound effect at lower volume
            if self.audio_system:
                # Play scanner sound at lower volume
                scanner_sound = self.audio_system.audio_manager.sound_effects.get("scanner")
                if scanner_sound:
                    original_volume = scanner_sound.get_volume()
                    scanner_sound.set_volume(original_volume * 0.1)  # 10% of normal volume
                    scanner_sound.play()
                    scanner_sound.set_volume(original_volume)  # Restore original volume
            
            # Reward for checking in NPC
            self.star_ui.add_progress(1)
        
        # Then check if clicking on floor dumbbells (within range)
        elif (self.tilemap.is_within_player_range(tile_x, tile_y) and 
              self.gym_manager.pickup_floor_dumbbells(mouse_x, mouse_y, self.camera, self.player, self.tilemap)):
            # Successfully picked up dumbbells
            pass
        
        else:
            # Then check for other interactions using hitbox detection
            obj = self.gym_manager.get_object_at_mouse_position(mouse_x, mouse_y, self.camera)
            if obj and self.tilemap.is_within_player_range(tile_x, tile_y):
                # Check if clicking on floor plates (only when actually on the squat rack)
                if hasattr(obj, 'is_mouse_over_floor_plates') and obj.is_mouse_over_floor_plates(mouse_x, mouse_y, self.camera):
                    if self.gym_manager.pickup_floor_plates(mouse_x, mouse_y, self.camera, self.player, self.tilemap):
                        # Successfully picked up plates
                        pass
                
                # Check for other gym object interactions
                elif hasattr(obj, 'interact'):
                    obj.interact(self.player)
                    # Reward for interaction
                    self.star_ui.add_progress(1)
                
                # Check for cleaning interactions
                elif obj.has_state("dirty"):
                    if self.audio_system:
                        self.audio_system.play_sound("spray_bottle")
                    if hasattr(obj, 'start_cleaning'):
                        obj.start_cleaning()
                        # Reward for cleaning
                        self.star_ui.add_progress(2)
                
                # Check for turning off equipment
                elif hasattr(obj, 'on_but_not_occupied') and obj.on_but_not_occupied:
                    if self.audio_system:
                        self.audio_system.play_sound("machine shutdown")
                    obj.turn_off()
                    # Reward for turning off treadmill
                    self.star_ui.add_progress(1)
    
    def _get_npc_at_mouse_position(self, mouse_x, mouse_y):
        """Get NPC at mouse position"""
        world_x, world_y = self.camera.reverse_apply_pos(mouse_x, mouse_y)
        
        for npc in self.npcs:
            # Check if mouse is over NPC using their rect
            if hasattr(npc, 'rect') and npc.rect.collidepoint(world_x, world_y):
                return npc
        return None
    
    def _advance_queue_after_checkin(self, checked_in_npc):
        """Advance queue after NPC check-in"""
        # Find the position of the checked-in NPC in the queue
        queue_position = checked_in_npc.queue_position
        
        # Move all NPCs behind this one forward
        for npc in self.npcs:
            if (not npc.checked_in and 
                hasattr(npc, 'queue_position') and 
                npc.queue_position > queue_position):
                npc.queue_position -= 1
                
                # Update their target position
                checkin_x = (8 - npc.queue_position) * 16 + 8
                checkin_y = 11 * 16 + 8
                npc.move_to_position(checkin_x, checkin_y)
    
    def _update_cursor(self):
        """Update cursor based on what's under the mouse"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Check if mouse is over star UI
        if self.star_ui.handle_click(mouse_x, mouse_y):
            self.current_cursor = "pointer"
            return
        
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
        
        # Clear screen
        screen.fill("black")
        
        # Draw game components
        self.tilemap.draw_floors_only(screen, self.camera)
        self.tilemap.draw_walls_only(screen, self.camera)
        
        # Draw floor sprites first (behind everything)
        self._draw_floor_sprites(screen)
        
        # Draw all entities with depth sorting
        self._draw_entities_with_depth_sorting(screen)
        
        # Draw UI
        self.star_ui.draw(screen)
        
        # Draw tile highlighting
        self.tilemap.draw_tile_highlight(screen, self.camera)
        
        # Draw game clock
        self._draw_game_clock(screen)
        
        # Draw debug hitboxes
        self._draw_debug_hitboxes(screen)
        
        # Draw dialogue UI
        if self.dialogue_manager:
            self.dialogue_manager.draw(screen)
    
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
        """Draw the game clock"""
        try:
            clock_font = pygame.font.Font("Font/Retro Gaming.ttf", 24)
        except:
            clock_font = pygame.font.Font(None, 24)
        
        clock_text = clock_font.render(self.game_clock.get_time_string(), True, (255, 255, 255))
        clock_rect = clock_text.get_rect()
        clock_rect.topright = (screen.get_width() - 20, 20)
        screen.blit(clock_text, clock_rect)
        
        # Draw NPC count underneath the clock
        npc_count_text = clock_font.render(f"NPCS {len(self.npcs)}/{self.npc_wave_manager.max_total_npcs}", True, (255, 255, 255))
        npc_count_rect = npc_count_text.get_rect()
        npc_count_rect.topright = (screen.get_width() - 20, 50)  # 30 pixels below the clock
        screen.blit(npc_count_text, npc_count_rect)
    
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

# Import the classes we need
from ..player import Player
from ..game_clock import GameClock
from ..npc_wave_manager import NPCWaveManager
