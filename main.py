from game_state import GameState, Position
from search import Searcher, SearchResult
from typing import List, Dict, Tuple, Optional
import time
import ast

def get_test(filename) -> Tuple[List[List[str]], Dict[Position, float]]:
    try:
        with open(filename, 'r') as file:
            weight_line = file.readline().strip()
            weights = {}
            if weight_line:
                for pair in weight_line.split():
                    pos, weight = pair.split(':')
                    col, row = map(int, pos.strip("()").split(','))
                    weights[Position(col,row)] = float(weight)
            
            grid = [list(line.strip()) for line in file if line.strip()]
            
            return grid, weights
            
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        raise

def write_output(output_file: str, output_for_path:str, result: Optional[SearchResult], method_name: str, mode: str = 'a'):
    try:
        with open(output_file, mode, encoding='utf-8') as file:
            file.write(f"{method_name}:\n")
            if result:
                file.write(f"Moves: {len(result.path)}\n")
                file.write(f"Path: {''.join(result.path)}\n")
                file.write(f"States explored: {result.explored_states}\n")
                file.write(f"Time: {result.execution_time:.3f} seconds\n")
                file.write(f"Memory: {result.memory_used:.2f} MB\n")
                if hasattr(result, 'cost'):
                    file.write(f"Path cost: {result.cost:.2f}\n")
            else:
                file.write("No solution found\n")
            file.write("\n") 

            with open(output_for_path, 'a', encoding='utf-8') as path_store:
                if result:
                    path_store.write(f"{''.join(result.path)}\n")
                else:
                    path_store.write(f"{method_name}: No solution found\n")
                
    except Exception as e:
        raise Exception(f"Error writing to {output_file}: {str(e)}")

def main(selected_map_file):
    output_filename = "output/output-01.txt" 
    output_path = "output.txt"

    open(output_filename, 'w').close() 
    open(output_path, 'w').close() 
    
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write("Solutions\n")
        file.write("=" * 50 + "\n\n")


    grid, weights = get_test(selected_map_file)
    print("Initial state:")
    print('\n'.join(''.join(row) for row in grid))
    print(f"\nStone weights: {weights}")

    initial_state = GameState(grid, stone_weights=weights)
    searcher = Searcher(initial_state)
    
    search_methods = {
        "DFS": searcher.depth_first_search,
        "BFS": searcher.breadth_first_search,
        "Uniform Cost Search": searcher.uniform_cost_search,
        "A*": searcher.a_star_search
    }
    
    for name, method in search_methods.items():
        result = method()
        write_output(output_filename, output_path, result, name)
        

if __name__ == "__main__":
    main()