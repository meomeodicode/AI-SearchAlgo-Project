from collections import defaultdict


class GameState(list): 
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
    
    move_mapping = {
        (-1, 0): "u", (1, 0): "d", (0, -1): "l", (0, 1): "r", 
        (-1, 0, "push"): "U", (1, 0, "push"): "D", (0, -1, "push"): "L", (0, 1, "push"): "R"
    }

    def move(self, direction, grid):
        character_pos = self.get_character_pos()
        stones = self.get_stones_pos()
        dx, dy = direction  
        new_character_pos = [character_pos[0] + dx, character_pos[1] + dy]
        if new_character_pos in stones:
            new_stone_pos = [new_character_pos[0] + dx, new_character_pos[1] + dy]
            if not self.is_va(character_pos, new_character_pos, direction, grid, stones):
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
        grid[character_pos[0]][character_pos[1]] = " "  
        grid[new_character_pos[0]][new_character_pos[1]] = "@" 
        return True  

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
    def set_distance():
        distance_to_target = defaultdict(lambda: defaultdict(lambda: float('inf')))
        deadlock = set()
        directions = [(-1,0), (1,0), (0,-1), (0,1)]

        #We find distance with bfs
        tile_queue = queue()
        for target in targets:
            distance_to_target[target][target] = 0
            tile_queue.append(target)
            while tile_queue:
                position = tile_queue.popLeft()






        

