import pygame
import math

class QueueManager:
    """Centralized queue management system for front desk check-ins"""
    
    def __init__(self, front_desk_position, queue_config=None):
        # Front desk position (tile coordinates)
        self.front_desk_x = front_desk_position[0]
        self.front_desk_y = front_desk_position[1]
        
        # Queue configuration
        self.config = queue_config or {
            'max_queue_length': 5,
            'timeout_duration': 15.0,  # seconds
            'queue_spacing': 1,  # tiles between NPCs
            'queue_direction': 'left',  # queue extends left from front desk
            'queue_row': 11  # which row the queue forms in
        }
        
        # Queue state
        self.queue = []  # List of NPCs in queue order
        self.npc_positions = {}  # Track NPC queue positions
        
    def add_npc_to_queue(self, npc):
        """Add an NPC to the end of the queue"""
        if npc in self.queue:
            return False  # Already in queue
            
        # Add to queue
        self.queue.append(npc)
        position = len(self.queue) - 1
        
        # Set NPC queue attributes
        npc.queue_position = position
        npc.queue_start_time = pygame.time.get_ticks() / 1000.0
        npc.has_triggered_queue_timeout = False
        
        # Calculate and set target position
        target_x, target_y = self._calculate_queue_position(position)
        npc.move_to_position(target_x, target_y)
        
        print(f"QUEUE ENTRY | NPC {npc.npc_id} added to queue at position {position}")
        return True
    
    def remove_npc_from_queue(self, npc):
        """Remove an NPC from the queue"""
        if npc not in self.queue:
            return False
            
        position = self.queue.index(npc)
        self.queue.remove(npc)
        
        # Update positions for NPCs behind this one
        self._update_queue_positions_after_removal(position)
        
        print(f"QUEUE EXIT | NPC {npc.npc_id} removed from queue at position {position}")
        return True
    
    def check_in_npc(self, npc):
        """Check in the NPC at the front of the queue"""
        if not self.queue or self.queue[0] != npc:
            return False  # Not at front of queue
            
        # Mark as checked in
        npc.checked_in = True
        npc.needs_check_in = False
        npc.check_in_time = pygame.time.get_ticks() / 1000.0  # Set check-in time for gym timer
        
        # Remove from queue
        self.remove_npc_from_queue(npc)
        
        print(f"QUEUE CHECKIN | NPC {npc.npc_id} checked in")
        return True
    
    def update_queue_timeouts(self, delta_time):
        """Update queue timeouts and remove expired NPCs"""
        current_time = pygame.time.get_ticks() / 1000.0
        expired_npcs = []
        
        for npc in self.queue:
            if not hasattr(npc, 'queue_start_time'):
                continue
                
            wait_time = current_time - npc.queue_start_time
            
            # Debug print every 2 seconds
            if int(wait_time) % 2 == 0 and int(wait_time) != int(wait_time - 0.1):
                print(f"QUEUE DEBUG | NPC {npc.npc_id} at position {npc.queue_position} waiting {wait_time:.1f}s")
            
            if wait_time >= self.config['timeout_duration']:
                expired_npcs.append(npc)
        
        # Remove expired NPCs
        for npc in expired_npcs:
            self._trigger_npc_timeout(npc)
    
    def _trigger_npc_timeout(self, npc):
        """Handle NPC queue timeout"""
        print(f"QUEUE TIMEOUT | NPC {npc.npc_id} waited too long, leaving!")
        
        # Set happiness event flag
        setattr(npc, 'happiness_event_queue_timeout', True)
        
        # Remove from queue
        self.remove_npc_from_queue(npc)
        
        # Make NPC leave using proper departure system
        exit_x = -50
        exit_y = npc.y
        npc.start_departure(exit_x, exit_y)
        
        # Clear any current targeting
        npc.target_object = None
        if hasattr(npc, 'target_front_desk'):
            delattr(npc, 'target_front_desk')
        if hasattr(npc, 'target_object_coords'):
            delattr(npc, 'target_object_coords')
    
    def _calculate_queue_position(self, position):
        """Calculate screen coordinates for a queue position"""
        if self.config['queue_direction'] == 'left':
            # Queue extends left from front desk
            queue_x = (self.front_desk_x - (position + 1) * self.config['queue_spacing']) * 16 + 8
        else:
            # Queue extends right from front desk
            queue_x = (self.front_desk_x + (position + 1) * self.config['queue_spacing']) * 16 + 8
            
        queue_y = self.config['queue_row'] * 16 + 8
        return queue_x, queue_y
    
    def _update_queue_positions_after_removal(self, removed_position):
        """Update positions for NPCs after one is removed"""
        for i, npc in enumerate(self.queue):
            if i >= removed_position:
                # Update position
                old_position = npc.queue_position
                npc.queue_position = i
                
                # Update target position
                target_x, target_y = self._calculate_queue_position(i)
                npc.move_to_position(target_x, target_y)
                
                print(f"QUEUE ADVANCE | NPC {npc.npc_id} moved from position {old_position} to {i}")
    
    def get_queue_length(self):
        """Get current queue length"""
        return len(self.queue)
    
    def is_queue_full(self):
        """Check if queue is at maximum capacity"""
        return len(self.queue) >= self.config['max_queue_length']
    
    def get_front_npc(self):
        """Get the NPC at the front of the queue"""
        return self.queue[0] if self.queue else None
    
    def is_npc_in_queue(self, npc):
        """Check if an NPC is in the queue"""
        return npc in self.queue
    
    def get_npc_queue_position(self, npc):
        """Get an NPC's position in the queue"""
        return self.queue.index(npc) if npc in self.queue else -1
