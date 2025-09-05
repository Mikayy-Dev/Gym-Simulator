import heapq
import math
import pygame
from typing import List, Tuple, Optional, Set, Dict, Any

class Node:
    """Represents a node in the pathfinding grid"""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.g_cost = float('inf')  # Distance from start
        self.h_cost = 0  # Heuristic distance to goal
        self.f_cost = float('inf')  # Total cost (g + h)
        self.parent = None
        self.walkable = True
        self.is_goal_area = False  # If this node is near a target object
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))

class GymPathfinder:
    """A* pathfinding specifically adapted for the gym simulation game"""
    
    def __init__(self, tilemap, gym_manager=None, cell_size: int = 16):
        self.tilemap = tilemap
        self.gym_manager = gym_manager
        self.cell_size = cell_size
        
        # Get grid dimensions from tilemap
        self.width = len(tilemap.layer1_tiles[0])
        self.height = len(tilemap.layer1_tiles)
        
        # Initialize grid
        self.grid = [[Node(x, y) for x in range(self.width)] for y in range(self.height)]
        
        # Cache for performance
        self._obstacle_cache = set()
        self._cache_dirty = True
    
    def set_gym_manager(self, gym_manager):
        """Set the gym manager for obstacle detection"""
        self.gym_manager = gym_manager
        self._cache_dirty = True  # Force cache update
    
    def mark_cache_dirty(self):
        """Mark the obstacle cache as dirty to force an update"""
        self._cache_dirty = True
    
    def screen_to_grid(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to grid coordinates, centered on tiles"""
        # Convert to grid coordinates where each grid cell represents a tile center
        # Handle negative coordinates by clamping to valid grid bounds
        grid_x = int(screen_x // self.cell_size)
        grid_y = int(screen_y // self.cell_size)
        
        # Clamp to valid grid bounds
        grid_x = max(0, min(self.width - 1, grid_x))
        grid_y = max(0, min(self.height - 1, grid_y))
        
        return grid_x, grid_y
    
    def grid_to_screen(self, grid_x: int, grid_y: int) -> Tuple[int, int]:
        """Convert grid coordinates to screen coordinates, centered on tiles"""
        # Return the center of the tile (grid cell)
        return grid_x * self.cell_size + self.cell_size // 2, grid_y * self.cell_size + self.cell_size // 2
    
    def update_obstacle_cache(self):
        """Update the obstacle cache from tilemap layers"""
        if not self._cache_dirty:
            return
            
        self._obstacle_cache.clear()
        
        # Reset grid
        for row in self.grid:
            for node in row:
                node.walkable = True
                node.is_goal_area = False
        
        # Add walls from layer1 as obstacles
        for y, row in enumerate(self.tilemap.layer1_tiles):
            for x, tile_id in enumerate(row):
                if self.tilemap.is_collidable(tile_id):
                    # Walls block the entire grid cell
                    self.grid[y][x].walkable = False
                    self._obstacle_cache.add((x, y))
        
        # Add gym objects as obstacles using the new gym manager
        if self.gym_manager:
            for pos, obj in self.gym_manager.get_collision_objects():
                # Get the collision rectangle from the gym object
                collision_rect = obj.get_collision_rect()
                if collision_rect:
                    # Mark the grid cells that overlap with the object
                    # Convert hitbox bounds to grid coordinates
                    start_x = max(0, int(collision_rect.left // self.cell_size))
                    end_x = min(self.width - 1, int(collision_rect.right // self.cell_size))
                    start_y = max(0, int(collision_rect.top // self.cell_size))
                    end_y = min(self.height - 1, int(collision_rect.bottom // self.cell_size))
                    
                    # If the object is occupied (in use), also block tiles around it
                    is_occupied = hasattr(obj, 'occupied') and obj.occupied
                    
                    for grid_x in range(start_x, end_x + 1):
                        for grid_y in range(start_y, end_y + 1):
                            if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
                                self.grid[grid_y][grid_x].walkable = False
                                self._obstacle_cache.add((grid_x, grid_y))
                                
                                # If occupied, also block tiles in front of the bench
                                if is_occupied and hasattr(obj, 'bench_type'):
                                    # Block the tile in front of the bench (where NPCs would stand)
                                    front_tile_x = grid_x
                                    front_tile_y = grid_y + 1  # Tile below the bench
                                    if (0 <= front_tile_x < self.width and 
                                        0 <= front_tile_y < self.height):
                                        self.grid[front_tile_y][front_tile_x].walkable = False
                                        self._obstacle_cache.add((front_tile_x, front_tile_y))
        
        self._cache_dirty = False
    
    def find_accessible_positions_near_object(self, target_object: Any, 
                                            max_distance: int = 3) -> List[Tuple[int, int]]:
        """Find walkable positions near a target object"""
        if not hasattr(target_object, 'rect'):
            return []
        
        self.update_obstacle_cache()
        accessible_positions = []
        
        # Get the object's grid bounds - use actual collision rect if available
        obj_rect = target_object.rect
        
        # If this is a gym object with a real collision rectangle, use that
        if hasattr(target_object, 'get_collision_rect'):
            obj_rect = target_object.get_collision_rect()
        
        center_x = obj_rect.centerx // self.cell_size
        center_y = obj_rect.centery // self.cell_size
        
        # Search in expanding circles around the object
        for distance in range(1, max_distance + 1):
            for dx in range(-distance, distance + 1):
                for dy in range(-distance, distance + 1):
                    # Only check cells at the current distance (outline of square)
                    if abs(dx) != distance and abs(dy) != distance:
                        continue
                    
                    x = center_x + dx
                    y = center_y + dy
                    
                    if (0 <= x < self.width and 0 <= y < self.height and 
                        self.grid[y][x].walkable):
                        accessible_positions.append((x, y))
        
        return accessible_positions
    
    def is_valid(self, x: int, y: int) -> bool:
        """Check if coordinates are valid and walkable"""
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                self.grid[y][x].walkable)
    
    def heuristic(self, node: Node, goal: Node) -> float:
        """Calculate heuristic distance (Manhattan distance)"""
        return abs(node.x - goal.x) + abs(node.y - goal.y)
    
    def get_neighbors(self, node: Node, allow_diagonal: bool = True) -> List[Node]:
        """Get valid neighboring nodes"""
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        if allow_diagonal:
            directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
        
        for dx, dy in directions:
            new_x, new_y = node.x + dx, node.y + dy
            
            if self.is_valid(new_x, new_y):
                neighbor = self.grid[new_y][new_x]
                
                # For diagonal movement, check if path is not blocked
                if allow_diagonal and abs(dx) == 1 and abs(dy) == 1:
                    if (not self.is_valid(node.x + dx, node.y) or 
                        not self.is_valid(node.x, node.y + dy)):
                        continue
                
                neighbors.append(neighbor)
        
        return neighbors
    
    def get_distance(self, node_a: Node, node_b: Node) -> float:
        """Calculate actual distance between two nodes"""
        dx = abs(node_a.x - node_b.x)
        dy = abs(node_a.y - node_b.y)
        return math.sqrt(2) if (dx == 1 and dy == 1) else 1
    
    def reconstruct_path(self, goal_node: Node) -> List[Tuple[int, int]]:
        """Reconstruct the path from goal to start"""
        path = []
        current = goal_node
        
        while current is not None:
            path.append((current.x, current.y))
            current = current.parent
        
        return path[::-1]
    
    def find_path_to_object(self, start_pos: Tuple[int, int], target_object: Any,
                           allow_diagonal: bool = False, 
                           interaction_distance: int = 2) -> Optional[List[Tuple[int, int]]]:
        """
        Find path from start position to near a target object
        
        Args:
            start_pos: (x, y) starting position in screen coordinates
            target_object: Object from layer2 to pathfind towards
            allow_diagonal: Whether to allow diagonal movement
            interaction_distance: How close the NPC needs to get to the object
        
        Returns:
            List of (x, y) grid coordinates representing the path, or None if no path found
        """
        self.update_obstacle_cache()
        
        # Convert start position to grid coordinates
        start_grid = self.screen_to_grid(*start_pos)
        
        # Find accessible positions near the target object
        goal_positions = self.find_accessible_positions_near_object(
            target_object, interaction_distance
        )
        
        if not goal_positions:
            return None
        
        # Try pathfinding to each possible goal position, starting with closest
        target_screen_pos = (target_object.rect.centerx, target_object.rect.centery)
        target_grid_pos = self.screen_to_grid(*target_screen_pos)
        
        # Sort goal positions by distance to start
        goal_positions.sort(key=lambda pos: 
            abs(pos[0] - start_grid[0]) + abs(pos[1] - start_grid[1])
        )
        
        for goal_pos in goal_positions:
            path = self._find_path_internal(start_grid, goal_pos, allow_diagonal)
            if path:
                return path
        
        return None
    
    def find_path(self, start_pos: Tuple[int, int], goal_pos: Tuple[int, int],
                  allow_diagonal: bool = False) -> Optional[List[Tuple[int, int]]]:
        """
        Standard pathfinding between two positions
        
        Args:
            start_pos: (x, y) starting position in screen coordinates
            goal_pos: (x, y) goal position in screen coordinates
            allow_diagonal: Whether to allow diagonal movement
        
        Returns:
            List of (x, y) grid coordinates representing the path, or None if no path found
        """
        self.update_obstacle_cache()
        
        start_grid = self.screen_to_grid(*start_pos)
        goal_grid = self.screen_to_grid(*goal_pos)
        
        return self._find_path_internal(start_grid, goal_grid, allow_diagonal)
    
    def _find_path_internal(self, start: Tuple[int, int], goal: Tuple[int, int], 
                           allow_diagonal: bool = False) -> Optional[List[Tuple[int, int]]]:
        """Internal pathfinding method using grid coordinates"""
        start_x, start_y = start
        goal_x, goal_y = goal
        
        if not self.is_valid(start_x, start_y) or not self.is_valid(goal_x, goal_y):
            return None
        
        # Reset pathfinding data
        for row in self.grid:
            for node in row:
                node.g_cost = float('inf')
                node.h_cost = 0
                node.f_cost = float('inf')
                node.parent = None
        
        start_node = self.grid[start_y][start_x]
        goal_node = self.grid[goal_y][goal_x]
        
        start_node.g_cost = 0
        start_node.h_cost = self.heuristic(start_node, goal_node)
        start_node.f_cost = start_node.g_cost + start_node.h_cost
        
        open_set = [start_node]
        closed_set: Set[Node] = set()
        
        while open_set:
            current_node = heapq.heappop(open_set)
            
            if current_node == goal_node:
                return self.reconstruct_path(goal_node)
            
            closed_set.add(current_node)
            
            for neighbor in self.get_neighbors(current_node, allow_diagonal):
                if neighbor in closed_set:
                    continue
                
                tentative_g_cost = (current_node.g_cost + 
                                  self.get_distance(current_node, neighbor))
                
                if tentative_g_cost < neighbor.g_cost:
                    neighbor.parent = current_node
                    neighbor.g_cost = tentative_g_cost
                    neighbor.h_cost = self.heuristic(neighbor, goal_node)
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    
                    if neighbor not in open_set:
                        heapq.heappush(open_set, neighbor)
        
        return None
    
    def invalidate_cache(self):
        """Call this when objects move or layers change"""
        self._cache_dirty = True
    
    def get_path_in_screen_coordinates(self, grid_path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Convert a grid path to screen coordinates"""
        return [self.grid_to_screen(x, y) for x, y in grid_path] 