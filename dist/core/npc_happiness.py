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

    def _get_management_level(self):
        if self.get_management_level_fn:
            try:
                return int(self.get_management_level_fn())
            except Exception:
                return 0
        return 0

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

    def on_dirty_machine_encountered(self):
        # NPC found target machine dirty
        self._apply_penalty(4.0)

    def on_squat_rack_weights_on_floor(self):
        # NPC wants squat rack but plates are on floor
        self._apply_penalty(3.0)

    def on_treadmill_unattended_running(self):
        # Treadmill is running with no user
        self._apply_penalty(2.5)

    def on_dumbbell_rack_empty(self):
        # NPC wants dumbbells but rack empty
        self._apply_penalty(3.5)

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


