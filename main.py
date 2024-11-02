from game_state import GameState, Position
from search import Searcher, SearchResult
from typing import List, Dict, Tuple, Optional
import time
import ast


def get_test(filename) -> Tuple[List[List[str]], Dict[Position, float]]:
    """
    Read a Sokoban level from a file.
    First line: row,col:weight pairs separated by spaces (e.g., "1,2:1.0 2,2:2.0")
    Remaining lines: grid using #@$. characters
    """
    try:
        with open(filename, 'r') as file:
            weight_line = file.readline().strip()
            weights = {}
            if weight_line:
                for pair in weight_line.split():
                    pos, weight = pair.split(':')
                    row, col = map(float, pos.strip("()").split(','))
                    weights[Position(row, col)] = float(weight)
            
            grid = [list(line.strip()) for line in file if line.strip()]
            
            return grid, weights
            
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        raise

def write_output(output_file, result: Optional[SearchResult]):
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            if result:
                file.write(f"Solution found:\n")
                file.write(f"Moves: {len(result.path)}\n")
                file.write(f"Path: {''.join(result.path)}\n")
                file.write(f"States explored: {result.explored_states}\n")
                file.write(f"Time: {result.execution_time:.3f} seconds\n")
                file.write(f"Memory: {result.memory_used:.2f} MB\n")
                if hasattr(result, 'cost'):
                    file.write(f"Path cost: {result.cost:.2f}\n")
            else:
                file.write("No solution found\n")
                
    except Exception as e:
        raise Exception(f"Error writing to {output_file}: {str(e)}")



def main():
    grid, weights = get_test("input/input-02.txt")
    print("Initial state:")
    print('\n'.join(''.join(row) for row in grid))
    print(f"\nStone weights: {weights}")
    output_filename = "output\output-01.txt"

    initial_state = GameState(grid, stone_weights=weights)
    searcher = Searcher(initial_state)
    
    search_methods = {
        "DFS": searcher.depth_first_search,
        "BFS": searcher.breadth_first_search,
        "A*": searcher.a_star_search,
        "Uniform Cost Search": searcher.uniform_cost_search
    }
    
    print("\nTesting different search methods:")
    print("-" * 50)
    
    for name, method in search_methods.items():
        print(f"\nTrying {name}...")
        result = method()
        write_output(output_filename, result)
        print(f"Results for {name} written to {output_filename}")
    
    print("\nSearch complete!")

if __name__ == "__main__":
    main()