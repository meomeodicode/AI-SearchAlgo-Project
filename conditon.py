class condition: 
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
