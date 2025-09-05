"""
Entity Manager
Manages all game entities (player, NPCs, etc.)
"""

from typing import List, Dict, Any
from core.player import Player
from core.npc import create_npc

class EntityManager:
    """Manages all game entities"""
    
    def __init__(self):
        self.player = None
        self.npcs = []
        self.entities = {}  # Dictionary for other entities
    
    def initialize_player(self, x: float, y: float) -> Player:
        """Initialize the player entity"""
        self.player = Player(x, y)
        return self.player
    
    def add_npc(self, x: float, y: float, **kwargs) -> Any:
        """Add an NPC to the game"""
        npc = create_npc(x, y, **kwargs)
        self.npcs.append(npc)
        return npc
    
    def remove_npc(self, npc) -> bool:
        """Remove an NPC from the game"""
        if npc in self.npcs:
            npc.cleanup()
            self.npcs.remove(npc)
            return True
        return False
    
    def get_npcs(self) -> List[Any]:
        """Get all NPCs"""
        return self.npcs.copy()
    
    def get_player(self) -> Player:
        """Get the player entity"""
        return self.player
    
    def update(self, delta_time: float):
        """Update all entities"""
        # Update player
        if self.player:
            self.player.update_stamina(delta_time)
        
        # Update NPCs
        for npc in self.npcs:
            npc.update(delta_time)
        
        # Remove NPCs that are ready to be removed
        npcs_to_remove = [npc for npc in self.npcs if npc.is_ready_to_remove()]
        for npc in npcs_to_remove:
            self.remove_npc(npc)
    
    def clear_all(self):
        """Clear all entities"""
        if self.player:
            self.player = None
        
        for npc in self.npcs:
            npc.cleanup()
        self.npcs.clear()
        self.entities.clear()
