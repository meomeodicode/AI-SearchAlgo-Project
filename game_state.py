from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
import logging
from copy import deepcopy
import numpy as np
from scipy.optimize import linear_sum_assignment

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class Position:
    row: int  
    col: int  
    
    def __add__(self, other):
        return Position(self.row + other.row, self.col + other.col)
    
    def to_tuple(self) -> Tuple[int, int]:
        return (self.row, self.col)
    
    def manhattan_distance(self, other: 'Position') -> int:
        return abs(self.row - other.row) + abs(self.col - other.col)

class Direction:
    UP = Position(-1, 0)
    DOWN = Position(1, 0)
    LEFT = Position(0, -1)
    RIGHT = Position(0, 1)
    
    ALL = [UP, DOWN, LEFT, RIGHT]
    
    @staticmethod
    def to_string(direction: Position, is_push: bool = False) -> str:
        mapping = {
            (-1, 0): 'U' if is_push else 'u',
            (1, 0): 'D' if is_push else 'd',
            (0, -1): 'L' if is_push else 'l',
            (0, 1): 'R' if is_push else 'r'
        }
        return mapping.get((direction.row, direction.col), '')

class GameState:
    def __init__(self, grid: List[List[str]], stone_weights: Optional[Dict[Position, float]] = None, parent=None):
        self.grid = [row[:] for row in grid]
        self.height = len(grid)
        self.width = len(grid[0]) if grid else 0
        self.parent = parent
        self.g_cost = 0 if parent is None else parent.g_cost
        self.moves_history = []
        self.move_cost = []
        self.target_found = False
        
        try:
            self.character_pos = self._find_character()
        except ValueError as e:
            logger.error(f"Character position error: {e}")
            logger.error("Grid state:\n" + str(self))
            raise
        
        self.stones = self._find_stones()
        self.stone_targets = self._find_targets()
        self.completed_targets = self._find_completed_targets()
        
        if stone_weights is None:
            self.stone_weights = {stone: 1.0 for stone in self.stones}
        else:
            self.stone_weights = stone_weights.copy() if isinstance(stone_weights, dict) else {
                stone: weight for stone, weight in zip(self.stones, stone_weights)
            }
            
        if parent:
            self.moves_history = parent.moves_history.copy()
            
        logger.debug(f"Found {len(self.stones)} stones and {len(self.stone_targets)} targets")
    
    def _find_character(self) -> Position:
        """Find the character position in the grid. Returns Position(row, col)."""
        for row in range(self.height):
            for col in range(self.width):
                if self.grid[row][col] in ["@", "+"]:
                    return Position(row, col)
        logger.error("Grid state when character not found:\n" + str(self))
        raise ValueError("No character found in grid")
    
    def _find_stones(self) -> List[Position]:
        stones = []
        for row in range(self.height):
            for col in range(self.width):
                if self.grid[row][col] in ["$", "*"]:
                    stones.append(Position(row, col))
        return stones
    
    def _find_targets(self) -> List[Position]:
        targets = []
        for row in range(self.height):
            for col in range(self.width):
                if self.grid[row][col] in [".", "*", "+"]:
                    targets.append(Position(row, col))
        return targets
    
    def _find_completed_targets(self) -> List[Position]:
        """Find all completed targets (stones on targets). Returns list of Position(row, col)."""
        completed = []
        for row in range(self.height):
            for col in range(self.width):
                if self.grid[row][col] == "*":
                    completed.append(Position(row, col))
        return completed
    
    def is_valid_position(self, pos: Position) -> bool:
        return (0 <= pos.row < self.height and 
                0 <= pos.col < self.width and 
                self.grid[pos.row][pos.col] != "#")
    
    def get_cell(self, pos: Position) -> str:
        return self.grid[pos.row][pos.col]
    
    def set_cell(self, pos: Position, value: str):
        self.grid[pos.row][pos.col] = value
    
    def is_stone_at(self, pos: Position) -> bool:
        return self.get_cell(pos) in ["$", "*"]
    
    def is_target_at(self, pos: Position) -> bool:
        return self.get_cell(pos) in [".", "*", "+"]
    
    def try_move(self, direction: Position) -> Optional['GameState']:
        new_pos = self.character_pos + direction
        if not self.is_valid_position(new_pos):
            return None 
            
        new_state = GameState([row[:] for row in self.grid], self.stone_weights, self)
        new_state.target_found = self.target_found
        is_push = self.is_stone_at(new_pos)
        move_cost = self.calculate_move_cost(direction, is_push)
        logger.info(f"Direction: {direction}, Is Push: {is_push}, Move Cost: {move_cost}")

        if is_push:
            push_pos = new_pos + direction
            if not self.is_valid_position(push_pos) or self.is_stone_at(push_pos):
                return None

            if new_pos in self.stone_weights:
                new_state.stone_weights[push_pos] = self.stone_weights[new_pos]
                del new_state.stone_weights[new_pos]

            if self.is_target_at(push_pos):
                new_state.set_cell(push_pos, "*")
                if push_pos not in new_state.completed_targets:
                    new_state.completed_targets.append(push_pos)
            else:
                new_state.set_cell(push_pos, "$")

            new_state.set_cell(new_pos, "+" if self.is_target_at(new_pos) else "@")
            new_state.target_found = self.is_target_at(new_pos)
            new_state.set_cell(self.character_pos, "." if self.target_found else " ")
            
            if new_pos in new_state.completed_targets:
                new_state.completed_targets.remove(new_pos)
            
            new_state.moves_history.append(Direction.to_string(direction, True))
        
        else:
            if self.is_target_at(new_pos):
                new_state.set_cell(new_pos, "+")
                new_state.target_found = True
            else:
                new_state.set_cell(new_pos, "@")
                new_state.target_found = False
            
            new_state.set_cell(self.character_pos, "." if self.target_found else " ")
            new_state.moves_history.append(Direction.to_string(direction, False))
        
        new_state.g_cost = self.g_cost + move_cost
        if not hasattr(new_state, 'move_cost'):
            new_state.move_cost = []
        new_state.move_cost.append(move_cost)
        new_state.character_pos = new_pos
        new_state.stones = new_state._find_stones()
        
        return new_state
  
    def get_successor_states(self) -> List[Tuple['GameState', float]]:
        successors = []
        for direction in Direction.ALL:
            new_state = self.try_move(direction)
            if new_state:
                move_cost = new_state.g_cost - self.g_cost
                successors.append((new_state, move_cost))
        return successors

    
    def is_solved(self) -> bool:
        return len(self.completed_targets) == len(self.stone_targets)

    def calculate_move_cost(self, direction: Position, is_push: bool) -> float:
        base_cost = 1.0
        if is_push:
            stone_pos = self.character_pos + direction
            stone_weight = self.stone_weights.get(stone_pos, 0.0)
            return base_cost + stone_weight 
        return base_cost

    def get_heuristic(self) -> float:
        remaining_stones = [stone for stone in self.stones if stone not in self.completed_targets]
        remaining_targets = [target for target in self.stone_targets if target not in self.completed_targets]
        if not remaining_stones:
            return 0
        distance_matrix = np.zeros((len(remaining_stones), len(remaining_targets)))
        for i, stone in enumerate(remaining_stones):
            stone_weight = self.stone_weights.get(stone,0.0)
            for j, target in enumerate(remaining_targets):
                distance_matrix[i][j] = stone.manhattan_distance(target) * (1+stone_weight)
                
        row_ind, col_ind = linear_sum_assignment(distance_matrix)
        return distance_matrix[row_ind, col_ind].sum()
    
    def get_state_key(self) -> tuple:
        stone_positions = tuple(sorted(stone.to_tuple() for stone in self.stones))
        completed_positions = tuple(sorted(target.to_tuple() for target in self.completed_targets))
        return (self.character_pos.to_tuple(), stone_positions, completed_positions)
    
    def __eq__(self, other):
        if not isinstance(other, GameState):
            return False
        return self.get_state_key() == other.get_state_key()
    
    def __hash__(self):
        return hash(self.get_state_key())
    
    def __str__(self) -> str:
        return '\n'.join(''.join(row) for row in self.grid)

    def get_path(self) -> List[str]:
        """Get the list of moves to reach this state."""
        return self.moves_history