import pygame
import random

class DialogueManager:
    """Manages dialogue system including conversations and interruptions"""
    
    def __init__(self):
        self.active_dialogue = None
        self.dialogue_ui = None
        self.player = None
        self.talking_npc = None
        self.dialogue_trees = {}
        self.on_dialogue_started = None
        self.on_dialogue_ended = None
        self._setup_dialogue_trees()
    
    def set_player(self, player):
        """Set reference to player"""
        self.player = player
    
    def set_dialogue_ui(self, dialogue_ui):
        """Set reference to dialogue UI"""
        self.dialogue_ui = dialogue_ui
    
    def _setup_dialogue_trees(self):
        """Setup dialogue trees for different NPCs"""
        self.dialogue_trees = {
            "interruptions": [
                {"text": "Yo, desk bro! Can you check my membership? My gains are time-sensitive."},
                {"text": "Hey, I think my protein shake spilled. Is that on the gym’s hazard protocol?"},
                {"text": "Bro, can you tell me where the squat racks are? My type II fibers are waiting."},
                {"text": "I need a towel. My delts just had a sweat-induced hypertrophy session."},
                {"text": "Is the leg press free? I’m trying to optimize sarcomere lengthening."},
                {"text": "Hey, can you show me how to adjust the dumbbells? I don’t want fascicle microtrauma."},
                {"text": "Can you remind me where the locker room is? My glycogen stores are low."},
                {"text": "Bro, I think the treadmill’s speed is off. My VO2 max calculations are suffering."},
                {"text": "Do you have a foam roller? My fascia is crying in scientific distress."},
                {"text": "Can you spot me real quick? My nervous system needs assistance recruiting fibers."},
                {"text": "Hey, what’s the gym Wi-Fi password? I need to track my macros in real time."},
                {"text": "Bro, do you sell pre-workout? I need my ATP production optimized."},
                {"text": "Is there a clean water fountain? Hydration kinetics are critical."},
                {"text": "Can you reset that machine? My sarcoplasmic reticulum is misaligned."},
                {"text": "Yo, can you check my membership expiration? My hypertrophy window is closing."},
                {"text": "Do you have sticky chalk? My grip is limiting force output."},
                {"text": "Hey, I need a new resistance band. My elastic potential energy is insufficient."},
                {"text": "Bro, can you tell me where the stretching area is? I need fascicle elongation."},
                {"text": "Is it cool if I drop the weights here? I’m working on eccentric overload."},
                {"text": "Can you spot me on the bench? My pectoral myofibrils need supervision."},
                {"text": "Hey, can I swap this machine? My muscle recruitment pattern is suboptimal."},
                {"text": "Bro, can you tell me where the kettlebells are? My posterior chain is calling."},
                {"text": "Do you have a ladder drill setup? I need neuromuscular coordination practice."},
                {"text": "Hey, can you clean this machine? My hygiene-to-hypertrophy ratio is off."},
                {"text": "Yo, can you check if the dumbbells are in order? My bilateral symmetry is at stake."},
                {"text": "Can you bring me a mat? My isometric contractions require a stable surface."},
                {"text": "Bro, I need help calculating my 1RM. My concentric force predictions are off."},
                {"text": "Hey, can you tell me where the pull-up bar is? My scapular retractors are twitching."},
                {"text": "Do you have ankle weights? My lower limb hypertrophy depends on them."},
                {"text": "Yo, can you help me with my warm-up? My tendon elasticity is suboptimal."},
                {"text": "Bro, can you make sure this machine is calibrated? My muscle spindle feedback depends on it."}
            ]
        }
    
    def start_dialogue(self, npc, dialogue_type="interruptions"):
        """Start a dialogue with an NPC"""
        if self.active_dialogue is not None:
            return False  # Already in dialogue
        
        if dialogue_type not in self.dialogue_trees:
            dialogue_type = "interruptions"  # Fallback
        
        selected = self.dialogue_trees[dialogue_type]
        if isinstance(selected, list):
            chosen = random.choice(selected)
            node = {"text": chosen["text"], "responses": [{"text": "Okay.", "next": "end"}]}
        else:
            node = selected

        self.active_dialogue = {
            "npc": npc,
            "current_node": dialogue_type,
            "dialogue_tree": node
        }
        
        self.talking_npc = npc
        npc.is_talking = True
        npc.locked_in_dialogue = True
        
        # Lock player and NPC in place
        if self.player:
            self.player.locked_in_dialogue = True
            # Set global interruption cooldown to prevent other NPCs from interrupting
            self.player.set_global_interruption_cooldown(45)
        
        if callable(self.on_dialogue_started):
            try:
                self.on_dialogue_started(npc)
            except Exception:
                pass
        return True
    
    def end_dialogue(self):
        """End the current dialogue"""
        if self.active_dialogue is None:
            return
        
        # Unlock player and NPC
        if self.player:
            self.player.locked_in_dialogue = False
        
        if self.talking_npc:
            self.talking_npc.is_talking = False
            self.talking_npc.locked_in_dialogue = False
            self.talking_npc.talk_cooldown = self.talking_npc.talk_cooldown_duration
            self.talking_npc.dialogue_cooldown = self.talking_npc.dialogue_cooldown_duration
        
        self.active_dialogue = None
        ended_npc = self.talking_npc
        self.talking_npc = None
        if callable(self.on_dialogue_ended):
            try:
                self.on_dialogue_ended(ended_npc)
            except Exception:
                pass
    
    def get_current_dialogue_text(self):
        """Get the current dialogue text"""
        if not self.active_dialogue:
            return None, []
        
        node = self.active_dialogue["dialogue_tree"]
        return node["text"], node["responses"]
    
    def select_response(self, response_index):
        """Select a response and advance dialogue"""
        if not self.active_dialogue:
            return
        
        node = self.active_dialogue["dialogue_tree"]
        if response_index < len(node["responses"]):
            response = node["responses"][response_index]
            next_node = response["next"]
            
            if next_node == "end":
                self.end_dialogue()
            else:
                # Advance to next dialogue node
                if next_node in self.dialogue_trees:
                    self.active_dialogue["dialogue_tree"] = self.dialogue_trees[next_node]
                else:
                    self.end_dialogue()
    
    def is_dialogue_active(self):
        """Check if dialogue is currently active"""
        return self.active_dialogue is not None
    
    def get_talking_npc(self):
        """Get the NPC currently in dialogue"""
        return self.talking_npc
    
    def update(self, delta_time):
        """Update dialogue system"""
        if self.active_dialogue and self.dialogue_ui:
            self.dialogue_ui.update(delta_time)
    
    def draw(self, screen):
        """Draw dialogue UI"""
        if self.active_dialogue and self.dialogue_ui:
            dialogue_text, responses = self.get_current_dialogue_text()
            self.dialogue_ui.draw(screen, dialogue_text, responses)
    
    def handle_input(self, event):
        """Handle input for dialogue system"""
        if not self.active_dialogue:
            return False
        
        if event.type == pygame.KEYDOWN:
            # Only handle specific dialogue keys
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                if event.key == pygame.K_1:
                    self.select_response(0)
                elif event.key == pygame.K_2:
                    self.select_response(1)
                elif event.key == pygame.K_3:
                    self.select_response(2)
                return True
            elif event.key == pygame.K_ESCAPE:
                # ESC ends dialogue but doesn't consume the event
                self.end_dialogue()
                return False  # Let the game handle ESC for pause
        
        return False
