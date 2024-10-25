from collections import defaultdict, deque
from typing import List, Dict, Set, Tuple
from scipy.optimize import linear_sum_assignment
import numpy as np

directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
def manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
class GameState(list): 
    def get_character_pos(self):
        for i in range (0,len(self)):
            for j in range(0,len(i)):
                if (self[i][j] == "@"):
                    return [i,j]
                
    def get_stones_pos(self):
        stones = []
        for i in range(0, len(self)):
            for j in range(0, len(self[i]) - 1):
                if self[i][j] == "$":
                    stones.append([i, j])
        return stones
    
    def get_targets_pos(self):
        targets = []
        for i in range(0, len(self)):
            for j in range(0, len(self[i]) - 1):
                if self[i][j] == ".":
                    targets.append([j, i])
        return targets

    def is_corner_deadlock(pos: Tuple[int, int], walls: Set[Tuple[int, int]], max_x: int, max_y: int) -> bool:
        x, y = pos
        if x == 0 or x == max_x - 1 or y == 0 or y == max_y - 1:
            return True 
        
        for i in range(len(directions)):
            dx1, dy1 = directions[i]
            dx2, dy2 = directions[(i + 1) % len(directions)]
            if (x + dx1, y + dy1) in walls and (x + dx2, y + dy2) in walls:
                return True
        return False

    def is_wall_deadlock(pos: Tuple[int, int], walls: Set[Tuple[int, int]], max_x: int, max_y: int) -> bool:
        x, y = pos
        if ((x-1, y) in walls or x-1 < 0) and ((x+1, y) in walls or x+1 >= max_x):
            return True
        if ((x, y-1) in walls or y-1 < 0) and ((x, y+1) in walls or y+1 >= max_y):
            return True
        return False
    
    def is_goal_state(stone_positions, switch_positions):
        return set(stone_positions) == set(switch_positions)
    
    move_mapping = {
        (-1, 0): "u", (1, 0): "d", (0, -1): "l", (0, 1): "r", 
        (-1, 0, "push"): "U", (1, 0, "push"): "D", (0, -1, "push"): "L", (0, 1, "push"): "R"
    }

    def move(self, direction, grid):
        character_pos = self.get_character_pos()
        stones = self.get_stones_pos()
        dx, dy = direction  
        new_character_pos = [character_pos[0] + dx, character_pos[1] + dy]
        #pushing a stone
        if new_character_pos in stones:
            new_stone_pos = [new_character_pos[0] + dx, new_character_pos[1] + dy]
            if not self.is_valid_push(character_pos, new_character_pos, direction, grid, stones):
                return False  
            else:
                stones.remove(new_character_pos)
                stones.append(new_stone_pos)
                grid[new_character_pos[0]][new_character_pos[1]] = "@"
                grid[character_pos[0]][character_pos[1]] = " "
                grid[new_stone_pos[0]][new_stone_pos[1]] = "$"
                return True 
        elif not self.is_valid_move(new_character_pos, grid, stones):
            return False  
        #normal move
        grid[character_pos[0]][character_pos[1]] = " "  
        grid[new_character_pos[0]][new_character_pos[1]] = "@" 
        return True  



    def build_trail(start: Tuple[int, int], walls: Set[Tuple[int, int]], 
                switches: Set[Tuple[int, int]], max_x: int, max_y: int) -> Set[Tuple[int, int]]:
        """Find reachable trails and avoiding deadlock situations"""
        trail = set()
        queue = deque([start])
        visited = {start}
        deadlocks = set()
        for x in range(max_x):
            for y in range(max_y):
                pos = (x, y)
                if pos not in walls and (GameState.is_corner_deadlock(pos, walls, max_x, max_y) or GameState.is_wall_deadlock(pos, walls, max_x, max_y)):
                    deadlocks.add(pos)
        while queue:
            current = queue.popleft()
            if current not in deadlocks or current in switches:
                trail.add(current)
            for dx, dy in directions:
                next_pos = (current[0] + dx, current[1] + dy)
                if (0 <= next_pos[0] < max_x and 0 <= next_pos[1] < max_y and next_pos not in visited and next_pos not in walls):
                    queue.append(next_pos)
                    visited.add(next_pos)
        return trail
        
    def set_distance(trail: Set[Tuple[int, int]], targets: Set[Tuple[int, int]]) -> Tuple[Dict, Set[Tuple[int, int]]]:
        #trail is a set of positions that the player can move to (not wall)
        distance_to_target = defaultdict(dict)
        deadlock = set()
        for target in targets:
            distance_to_target[target][target] = 0
        for target in targets:
            for tile in trail and tile not in targets:
                distance_to_target[target][tile] = manhattan_distance(target,tile)
        return distance_to_target, deadlock

    def get_minimum_cost(stones: List[Tuple[int, int]], 
                        targets: Set[Tuple[int, int]],
                        stone_weights: List[float],
                        distance_to_target: Dict) -> float:
        """    
        Args:
            stones: List of stone positions
            targets: Set of target positions
            stone_weights: List of weights for each stone
            distance_to_target: Precomputed distances to targets
        
        Returns:
            Minimum cost to move stones to targets
        """
        if not stones:
            return 0
        n = len(stones)
        cost_matrix = np.zeros((n, n))
        for i, stone in enumerate(stones):
            for j, target in enumerate(targets):
                cost_matrix[i][j] = distance_to_target[target][stone] * (stone_weights[i] + 1)
            row_ind, col_ind = linear_sum_assignment(cost_matrix)
        
        total_cost = cost_matrix[row_ind, col_ind].sum()
        return total_cost




        

