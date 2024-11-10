from game_state import GameState, Position
from search import Searcher, SearchResult
from typing import List, Dict, Tuple, Optional
import time
import ast
import os

def get_test(filename) -> Tuple[List[List[str]], Dict[Position, float]]:
    try:
        with open(filename, 'r') as file:
            weight_line = file.readline().strip()
            weights = {}
            if weight_line:
                weight_list = list(map(float, weight_line.split()))
    
            grid = [list(line.strip()) for line in file if line.strip()]
            weight_index = 0
            for row_idx, row in enumerate(grid):
                for col_idx, cell in enumerate(row):
                    if cell == '$' and weight_index < len(weight_list):
                        weights[Position(row_idx, col_idx)] = weight_list[weight_index]
                        weight_index += 1
            
            return grid, weights
            
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        raise

def write_output(output_file: str, output_for_table: str, output_for_path: str, 
                result: Optional[SearchResult], method_name: str, mode: str = 'a'):
    try:
        output_content = [
            f"{method_name}:\n",
            f"Moves: {len(result.path)}\n" if result else "No solution found\n",
            f"Path: {''.join(result.path)}\n" if result else "",
            f"States explored: {result.explored_states}\n" if result else "",
            f"Time: {result.execution_time:.3f} seconds\n" if result else "",
            f"Memory: {result.memory_used:.2f} MB\n" if result else "",
            f"Path cost: {result.cost:.2f}\n" if result and hasattr(result, 'cost') else "",
            "\n"
        ]

        for file_path in [output_file, output_for_table]:
            with open(file_path, mode, encoding='utf-8') as f:
                f.writelines(output_content)
        
        with open(output_for_path, 'a', encoding='utf-8') as f:
            f.write(f"{''.join(result.path)}\n" if result else f"{method_name}: No solution found\n")

    except Exception as e:
        raise Exception(f"Error writing to files: {str(e)}")
    
def main(selected_map_file, selected_output):
    output_table = "output/output_table.txt" 
    output_path = "output.txt"
    output_file = selected_output
    print(f"Selected Output: {output_file}")
    open(output_file,'w').close()
    open(output_table, 'w').close() 
    open(output_path, 'w').close() 
    
    with open(output_table, 'w', encoding='utf-8') as file:
        file.write("Solutions\n")
        file.write("=" * 50 + "\n\n")


    grid, weights = get_test(selected_map_file)
    print("Initial state:")
    print('\n'.join(''.join(row) for row in grid))
    print(f"\nStone weights: {weights}")

    initial_state = GameState(grid, stone_weights=weights)
    print(initial_state.character_pos)
    searcher = Searcher(initial_state)
    
    search_methods = {
        "DFS": searcher.depth_first_search,
        "BFS": searcher.breadth_first_search,
        "Uniform Cost Search": searcher.uniform_cost_search,
        "A*": searcher.a_star_search
    }
    
    for name, method in search_methods.items():
        result = method()
        write_output(output_file, output_table, output_path, result, name)
        

if __name__ == "__main__":
    main()