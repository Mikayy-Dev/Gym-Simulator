import pygame
import time


class NPCHappinessManager:
    def __init__(self, gym_manager, get_management_level_fn=None, x_offset=30, bar_height=300):
        self.gym_manager = gym_manager
        self.get_management_level_fn = get_management_level_fn
        self.current_happiness = 50.0
        self.target_happiness = 50.0
        self.debug = False
        self.debug_interval_sec = 1.0
        self._debug_last_log_ts = 0.0
        self.bar_width = 20
        self.bar_height = bar_height
        self.x_offset = x_offset
        self.background_color = (40, 40, 40)
        self.border_color = (255, 255, 255)
        self.positive_color = (0, 200, 0)
        self.negative_color = (200, 0, 0)
        
        # Load coach_robbie images
        self.coach_images = {}
        try:
            self.coach_images['angry'] = pygame.image.load("Graphics/coach_robbie_angry.png")
            self.coach_images['happy'] = pygame.image.load("Graphics/coach_robbie_happy.png")
            self.coach_images['meh'] = pygame.image.load("Graphics/coach_robbie_meh.png")
        except pygame.error:
            # Fallback if images can't be loaded
            self.coach_images = {}
        
        # Chat log system
        self.chat_log = []
        self.max_log_entries = 5
        try:
            self.font = pygame.font.Font("Font/Retro Gaming.ttf", 16)
        except:
            self.font = pygame.font.Font(None, 16)
        self.chat_log_width = 200
        self.chat_log_height = 120
        
        # Animation system
        self.message_display_time = 5.0  # seconds
        self.fade_duration = 1.0  # seconds
        self.rise_distance = 20  # pixels

    def _get_management_level(self):
        if self.get_management_level_fn:
            try:
                return int(self.get_management_level_fn())
            except Exception:
                return 0
        return 0

    def _add_chat_log_entry(self, message):
        """Add an entry to the chat log"""
        import time
        current_time = time.time()
        self.chat_log.append({
            'message': message,
            'start_time': current_time,
            'y_offset': 0
        })
        
        # Keep only the most recent entries
        if len(self.chat_log) > self.max_log_entries:
            self.chat_log.pop(0)

    def _compute_component_scores(self):
        total = 0
        clean_count = 0
        organized_count = 0

        for _, obj in self.gym_manager.gym_objects.items():
            total += 1
            states = obj.get_states() if hasattr(obj, 'get_states') else set()

            if 'dirty' not in states:
                clean_count += 1

            if 'cluttered' not in states:
                organized_count += 1

        if total == 0:
            return 1.0, 1.0

        cleanliness = clean_count / total
        organization = organized_count / total
        return cleanliness, organization

    def update(self, delta_time):
        cleanliness, organization = self._compute_component_scores()

        # Base happiness starts at 50% and only changes due to events
        # The gym state doesn't automatically affect happiness - only events do
        self.target_happiness = 50.0

        management_level = self._get_management_level()

        now = time.time()
        if self.debug and (now - self._debug_last_log_ts) >= self.debug_interval_sec:
            print(f"HAPPINESS DEBUG | clean={cleanliness:.2f} org={organization:.2f} target={self.target_happiness:.1f} current={self.current_happiness:.1f} mgmt={management_level}")
            self._debug_last_log_ts = now

        # Don't automatically change happiness - only change through events
        # Happiness stays at whatever level it was set to by events
        
        # Update chat log animations
        self._update_chat_log_animations(now)

    def _update_chat_log_animations(self, current_time):
        """Update chat log message animations"""
        messages_to_remove = []
        
        for i, entry in enumerate(self.chat_log):
            elapsed_time = current_time - entry['start_time']
            
            if elapsed_time > self.message_display_time + self.fade_duration:
                # Message has completely faded out, mark for removal
                messages_to_remove.append(i)
            elif elapsed_time > self.message_display_time:
                # Message is in fade-out phase
                fade_progress = (elapsed_time - self.message_display_time) / self.fade_duration
                entry['y_offset'] = int(fade_progress * self.rise_distance)
            else:
                # Message is still in display phase
                entry['y_offset'] = 0
        
        # Remove expired messages (in reverse order to maintain indices)
        for i in reversed(messages_to_remove):
            self.chat_log.pop(i)

    def draw(self, screen, timer_center_x=None, timer_height=None):
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        # Load the original image to get its dimensions
        try:
            happiness_bar_image = pygame.image.load("Graphics/happiness_bar.png")
            original_width = happiness_bar_image.get_width()
            original_height = happiness_bar_image.get_height()
        except pygame.error:
            # Fallback to default dimensions if image can't be loaded
            original_width = self.bar_width
            original_height = self.bar_height

        # Scale factors for overlay
        scale_factor = 3
        scaled_width = original_width * scale_factor
        scaled_height = original_height * scale_factor

        # Align center of happiness bar with center of timer overlay horizontally
        if timer_center_x is not None:
            # Align centers horizontally
            bar_x = timer_center_x - (scaled_width // 2)
        else:
            # Fallback to original positioning
            bar_x = screen_width - self.x_offset - scaled_width
        
        # Position happiness bar below timer overlay
        # Timer overlay is at y=10, so position bar right below it
        if timer_height is not None:
            bar_y = 10 + timer_height + 10  # 10px spacing below timer overlay
        else:
            # Fallback: assume timer overlay height is 200px
            bar_y = 10 + 200 + 10

        # Draw fill (with padding to fit inside overlay)
        if self.current_happiness > 0:
            vertical_padding = 24  # Slightly less vertical padding to make bar taller
            horizontal_padding = 32  # Increased padding to make bar narrower
            available_height = scaled_height - vertical_padding * 2
            fill_height = int((self.current_happiness / 100.0) * available_height)
            fill_y = bar_y + vertical_padding + (available_height - fill_height)
            color = self.positive_color if self.current_happiness >= 50.0 else self.negative_color
            pygame.draw.rect(screen, color, (bar_x + horizontal_padding, fill_y, scaled_width - horizontal_padding * 2, fill_height))

        # Overlay happiness bar image (scaled)
        try:
            happiness_bar_image = pygame.transform.scale(happiness_bar_image, (scaled_width, scaled_height))
            screen.blit(happiness_bar_image, (bar_x, bar_y))
        except pygame.error:
            pass
        
        # Draw coach_robbie graphic based on happiness level
        self._draw_coach_graphic(screen, bar_x, bar_y, scaled_width, scaled_height)
        
        # Draw chat log below happiness bar
        self._draw_chat_log(screen, bar_x, bar_y + scaled_height + 10, scaled_width)

    def _draw_coach_graphic(self, screen, bar_x, bar_y, bar_width, bar_height):
        """Draw coach_robbie graphic based on happiness level"""
        if not self.coach_images:
            return
        
        # Determine which coach image to use based on happiness level
        if self.current_happiness >= 70:
            coach_key = 'happy'
        elif self.current_happiness >= 40:
            coach_key = 'meh'
        else:
            coach_key = 'angry'
        
        if coach_key not in self.coach_images:
            return
        
        # Scale the coach image to be a little bigger
        coach_scale = 0.4
        coach_image = self.coach_images[coach_key]
        scaled_coach = pygame.transform.scale(coach_image, 
                                            (int(coach_image.get_width() * coach_scale), 
                                             int(coach_image.get_height() * coach_scale)))
        
        # Position coach at the base of the happiness bar
        coach_x = bar_x + (bar_width // 2) - (scaled_coach.get_width() // 2)  # Center horizontally with bar
        coach_y = bar_y + bar_height - scaled_coach.get_height() + 70  # Position at base of bar, lowered by 10px
        
        # Draw the coach graphic
        screen.blit(scaled_coach, (coach_x, coach_y))

    def _draw_chat_log(self, screen, x, y, width):
        """Draw the chat log below the happiness bar"""
        if not self.chat_log:
            return
        
        # Draw log entries without background
        line_height = 18
        start_y = y + 5
        screen_width = screen.get_width()
        current_time = time.time()
        
        for i, entry in enumerate(self.chat_log[-self.max_log_entries:]):
            if i * line_height >= self.chat_log_height - 10:
                break
            
            # Calculate alpha for fade effect
            elapsed_time = current_time - entry['start_time']
            alpha = 255
            
            if elapsed_time > self.message_display_time:
                # Message is in fade-out phase
                fade_progress = (elapsed_time - self.message_display_time) / self.fade_duration
                alpha = int(255 * (1.0 - fade_progress))
                alpha = max(0, min(255, alpha))
            
            # Create text surface with alpha
            text_surface = self.font.render(entry['message'], True, (255, 255, 255))
            text_width = text_surface.get_width()
            
            # Apply alpha if fading
            if alpha < 255:
                text_surface.set_alpha(alpha)
            
            # Calculate position with rise animation
            text_x = max(5, min(x + 5, screen_width - text_width - 5))
            text_y = start_y + i * line_height - entry['y_offset']
            
            # Ensure text doesn't go off screen
            text_x = max(5, min(text_x, screen_width - text_width - 5))
            screen.blit(text_surface, (text_x, text_y))

    # --- Event-based penalties (call from NPC behaviors) ---
    def _apply_penalty(self, amount):
        management_level = self._get_management_level()
        scaled = amount * max(0.2, (1.0 - management_level * 0.1))
        if self.debug:
            print(f"HAPPINESS EVENT | penalty={amount:.1f} scaled={scaled:.1f} mgmt={management_level} before={self.current_happiness:.1f}")
        self.current_happiness = max(0.0, self.current_happiness - scaled)
        if self.debug:
            print(f"HAPPINESS EVENT | after={self.current_happiness:.1f}")

    def set_debug(self, enabled: bool, interval_seconds: float = 1.0):
        self.debug = enabled
        self.debug_interval_sec = max(0.1, float(interval_seconds))

    def on_queue_timeout(self):
        # NPC waited too long and left
        self._apply_penalty(5.0)
        self._add_chat_log_entry("Customer left - waited too long")

    def on_dirty_machine_encountered(self):
        # NPC found target machine dirty
        self._apply_penalty(4.0)
        self._add_chat_log_entry("Customer found dirty machine")

    def on_squat_rack_weights_on_floor(self):
        # NPC wants squat rack but plates are on floor
        self._apply_penalty(3.0)
        self._add_chat_log_entry("Weights left on floor")

    def on_treadmill_unattended_running(self):
        # Treadmill is running with no user
        self._apply_penalty(2.5)
        self._add_chat_log_entry("Treadmill left running")

    def on_dumbbell_rack_empty(self):
        # NPC wants dumbbells but rack empty
        self._apply_penalty(3.5)
        self._add_chat_log_entry("Dumbbell rack empty")

    # --- Event-based bonuses (call from positive actions) ---
    def _apply_bonus(self, amount):
        management_level = self._get_management_level()
        scaled = amount * max(0.2, (1.0 - management_level * 0.1))
        if self.debug:
            print(f"HAPPINESS EVENT | bonus={amount:.1f} scaled={scaled:.1f} mgmt={management_level} before={self.current_happiness:.1f}")
        self.current_happiness = min(100.0, self.current_happiness + scaled)
        if self.debug:
            print(f"HAPPINESS EVENT | after={self.current_happiness:.1f}")

    def on_npc_checked_in(self):
        # NPC successfully checked in
        self._apply_bonus(2.0)

    def on_machine_cleaned(self):
        # Player cleaned a machine
        self._apply_bonus(1.5)

    def on_weights_organized(self):
        # Player organized weights (picked up floor plates)
        self._apply_bonus(1.0)

    def on_treadmill_turned_off(self):
        # Player turned off unattended treadmill
        self._apply_bonus(1.5)

    def reset_happiness(self):
        """Reset happiness to starting value"""
        self.current_happiness = 50.0
        self.target_happiness = 50.0


