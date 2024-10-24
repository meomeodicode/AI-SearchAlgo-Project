from collections import deque
import time
import tracemalloc
from stones import *

def is_valid_move(pos, grid, stones):
        x, y = pos
        if x < 0 or y < 0 or x >= len(grid) or y >= len(grid[0]):
            return False
        if grid[x][y] == '#' or pos in stones:
            return False
        return True
    
def is_valid_push(ares_pos, stone_pos, direction, grid, stones):
        x_stone, y_stone = stone_pos
        x_next = x_stone + direction[0]
        y_next = y_stone + direction[1]
        if (x_next < 0 or x_next >= len(grid) or 
        y_next < 0 or y_next >= len(grid[0]) or 
        grid[x_next][y_next] == '#' or 
        (x_next, y_next) in stones):
            return False
        return True

def is_goal_state(stone_positions, switch_positions):
    return set(stone_positions) == set(switch_positions)

def breadth_first_search(grid, start, stones, switches):
    state = (start, tuple(stones))
    explored = set() 
    frontier = deque([(state, "")])  
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] 
    move_mapping = {
        (-1, 0): "u", (1, 0): "d", (0, -1): "l", (0, 1): "r", 
        (-1, 0, "push"): "U", (1, 0, "push"): "D", (0, -1, "push"): "L", (0, 1, "push"): "R"
    }
    step = 0
    cost = 0
    tracemalloc.start()  
    start_time = time.time() 
    print("BFS")
    while frontier:
        current_state, path = frontier.popleft()  
        char_pos, stone_positions = current_state
        
        if is_goal_state(stone_positions, switches):
            end_time = time.time()
            memory_used = tracemalloc.get_traced_memory()[1] / (1024 ** 2)  
            tracemalloc.stop()
            return step, path, len(explored), end_time - start_time, memory_used

        if current_state in explored:
            continue
        explored.add(current_state)
        for direction in directions:
            new_char_pos = (char_pos[0] + direction[0], char_pos[1] + direction[1])

            if new_char_pos in stone_positions:
                stone_index = stone_positions.index(new_char_pos)
                new_stone_pos = (new_char_pos[0] + direction[0], new_char_pos[1] + direction[1])

                if is_valid_push(char_pos, new_char_pos, direction, grid, stone_positions):
                    new_stone_positions = list(stone_positions)
                    new_stone_positions[stone_index] = new_stone_pos  
                    new_state = (new_char_pos, tuple(new_stone_positions))  
                    new_path = path + move_mapping[(direction[0], direction[1], "push")]
                    frontier.append((new_state, new_path))  

            elif is_valid_move(new_char_pos, grid, stone_positions):
                new_state = (new_char_pos, stone_positions)  
                new_path = path + move_mapping[(direction[0], direction[1])]
                step += 1 
                frontier.append((new_state, new_path))  

    return None, None, None, None
