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
                "text": "Hey there! How's your workout going?",
                "responses": [
                    {"text": "Great, thanks!", "next": "positive_response"},
                    {"text": "Could be better...", "next": "encouraging_response"},
                    {"text": "Just getting started!", "next": "motivational_response"}
                ]
            },
            "positive_response": {
                "text": "That's awesome! Keep up the great work!",
                "responses": [
                    {"text": "Thanks!", "next": "end"},
                    {"text": "You too!", "next": "end"}
                ]
            },
            "encouraging_response": {
                "text": "Don't worry, everyone has off days. You've got this!",
                "responses": [
                    {"text": "Thanks for the encouragement!", "next": "end"},
                    {"text": "I appreciate it!", "next": "end"}
                ]
            },
            "motivational_response": {
                "text": "That's the spirit! Every expert was once a beginner!",
                "responses": [
                    {"text": "True!", "next": "end"},
                    {"text": "Thanks for the motivation!", "next": "end"}
                ]
            },
            "equipment_tip": {
                "text": "Hey, I noticed you might want to try the squat rack - it's great for building strength!",
                "responses": [
                    {"text": "Thanks for the tip!", "next": "end"},
                    {"text": "I'll check it out!", "next": "end"},
                    {"text": "Maybe later...", "next": "end"}
                ]
            },
            "form_advice": {
                "text": "I saw you working out - make sure to keep your back straight!",
                "responses": [
                    {"text": "Thanks for the advice!", "next": "end"},
                    {"text": "I'll remember that!", "next": "end"},
                    {"text": "Good to know!", "next": "end"}
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
        print(f"DEBUG: NPC {npc.npc_id} locked in dialogue")
        
        # Lock player and NPC in place
        if self.player:
            self.player.locked_in_dialogue = True
        
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
            print(f"DEBUG: NPC {self.talking_npc.npc_id} unlocked from dialogue (45s cooldown)")
        
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
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_ESCAPE]:
                if event.key == pygame.K_1:
                    self.select_response(0)
                elif event.key == pygame.K_2:
                    self.select_response(1)
                elif event.key == pygame.K_3:
                    self.select_response(2)
                elif event.key == pygame.K_ESCAPE:
                    self.end_dialogue()
                return True
        
        return False
