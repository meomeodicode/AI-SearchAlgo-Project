from game_state import GameState
from search import Searcher
from typing import List, Dict, Tuple
import time

def create_test_level(level_num: int = 1) -> Tuple[List[List[str]], List[float]]:
    levels = {
        1: ([ # Simple level with two stones
            ["#", "#", "#", "#", "#"],
            ["#", "@", "$", ".", "#"],
            ["#", " ", "$", ".", "#"],
            ["#", "#", "#", "#", "#"]
        ], [1.0, 2.0]),
        
        2: ([ # More complex level with three stones
            ["#", "#", "#", "#", "#", "#", "#"],
            ["#", " ", " ", "@", " ", " ", "#"],
            ["#", " ", "$", "$", "$", " ", "#"],
            ["#", " ", ".", ".", ".", " ", "#"],
            ["#", "#", "#", "#", "#", "#", "#"]
        ], [1.0, 1.5, 2.0]),

        3: ([ # Challenging level with four stones
            ["#", "#", "#", "#", "#", "#", "#"],
            ["#", "@", " ", " ", " ", " ", "#"],
            ["#", " ", "$", "$", " ", " ", "#"],
            ["#", " ", "$", "$", " ", " ", "#"],
            ["#", " ", ".", ".", " ", " ", "#"],
            ["#", " ", ".", ".", " ", " ", "#"],
            ["#", "#", "#", "#", "#", "#", "#"]
        ], [1.0, 1.0, 1.5, 2.0])
    }
    return levels.get(level_num, levels[1])

def main():
    grid, weights = create_test_level(2)
    print("Initial state:")
    print('\n'.join(''.join(row) for row in grid))
    print(f"\nStone weights: {weights}")
    
    initial_state = GameState(grid, stone_weights=weights)
    searcher = Searcher(initial_state)
    
    search_methods = {
        "A*": searcher.a_star_search,
        "Uniform Cost Search": searcher.uniform_cost_search
    }
    
    print("\nTesting different search methods:")
    print("-" * 50)
    
    for name, method in search_methods.items():
        print(f"\nTrying {name}...")
        result = method()
        
        if result:
            print(f"{name} found solution:")
            print(f"- Moves: {len(result.path)}")
            print(f"- Path: {''.join(result.path)}")
            print(f"- States explored: {result.explored_states}")
            print(f"- Time taken: {result.execution_time:.3f} seconds")
            print(f"- Memory used: {result.memory_used:.2f} MB")
            if hasattr(result, 'cost'):
                print(f"- Path cost: {result.cost:.2f}")
        else:
            print(f"{name} failed to find solution")
    
    print("\nSearch complete!")

if __name__ == "__main__":
    main()
