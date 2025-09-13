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
            "greeting": {
                "text": "Yo bro! What's good? How's it going?",
                "responses": [
                    {"text": "Pretty good, thanks!", "next": "positive_response"},
                    {"text": "Eh, could be better...", "next": "encouraging_response"},
                    {"text": "Just getting started here!", "next": "motivational_response"}
                ]
            },
            "positive_response": {
                "text": "Hell yeah bro! That's what I like to hear! Oh I used to bench a lot in high school - those were the days!",
                "responses": [
                    {"text": "Nice! What'd you bench?", "next": "end"},
                    {"text": "Respect!", "next": "end"}
                ]
            },
            "encouraging_response": {
                "text": "Come on bro, we all have those days! Oh yeah bro you gotta pump the muscle for it to grow! No pain, no gain!",
                "responses": [
                    {"text": "You're right, let's go!", "next": "end"},
                    {"text": "Thanks for the motivation!", "next": "end"}
                ]
            },
            "motivational_response": {
                "text": "That's the attitude! Back in my day, we didn't have all these fancy machines - just iron and determination!",
                "responses": [
                    {"text": "Respect the old school!", "next": "end"},
                    {"text": "I'll keep grinding!", "next": "end"}
                ]
            },
            "equipment_tip": {
                "text": "Yo bro, you ever hit the squat rack? That's where the real gains are made! I used to squat 315 back in the day!",
                "responses": [
                    {"text": "Damn, that's impressive!", "next": "end"},
                    {"text": "I'll give it a shot!", "next": "end"},
                    {"text": "Maybe when I'm stronger...", "next": "end"}
                ]
            },
            "form_advice": {
                "text": "Bro, when you do start lifting, keep that back tight! You don't want to end up like me with this bad back from sloppy lifting!",
                "responses": [
                    {"text": "Thanks for looking out!", "next": "end"},
                    {"text": "I'll remember that!", "next": "end"},
                    {"text": "Appreciate the tip!", "next": "end"}
                ]
            }
        }
    
    def start_dialogue(self, npc, dialogue_type="greeting"):
        """Start a dialogue with an NPC"""
        if self.active_dialogue is not None:
            return False  # Already in dialogue
        
        if dialogue_type not in self.dialogue_trees:
            dialogue_type = "greeting"  # Fallback
        
        self.active_dialogue = {
            "npc": npc,
            "current_node": dialogue_type,
            "dialogue_tree": self.dialogue_trees[dialogue_type]
        }
        
        self.talking_npc = npc
        npc.is_talking = True
        npc.locked_in_dialogue = True
        
        # Lock player and NPC in place
        if self.player:
            self.player.locked_in_dialogue = True
            # Set global interruption cooldown to prevent other NPCs from interrupting
            self.player.set_global_interruption_cooldown(45)
        
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
        self.talking_npc = None
    
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
