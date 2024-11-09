from typing import List, Optional, Tuple, Set, Dict
from dataclasses import dataclass
from collections import deque
import logging
import heapq
import time
import tracemalloc
from game_state import GameState
from copy import deepcopy
import psutil

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    steps: int
    path: List[str]
    explored_states: int
    execution_time: float
    memory_used: float
    cost: float = 0.0

class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._index = 0

    def push(self, item, priority):
        heapq.heappush(self._queue, (priority, self._index, item))
        self._index += 1

    def pop(self):
        return heapq.heappop(self._queue)[-1]

    def empty(self):
        return len(self._queue) == 0

class Searcher:
    def __init__(self, initial_state: GameState):
        self.initial_state = initial_state

    def _checking_setup(self):
        tracemalloc.start()
        return time.time()

    def _end_profiling(self, start_time: float) -> Tuple[float, float]:
        end_time = time.time()
        memory_used = tracemalloc.get_traced_memory()[1] / (1024 ** 2)
        tracemalloc.stop()
        return end_time - start_time, memory_used

    def breadth_first_search(self) -> Optional[SearchResult]:
        start_time = self._checking_setup()
        frontier = deque([(self.initial_state, [], 0)])  
        explored = set()
        steps = 0

        while frontier:
            current_state, path, current_cost = frontier.popleft()
            if current_state.is_solved():
                exec_time, memory = self._end_profiling(start_time)
                return SearchResult(
                    steps=steps,
                    path=current_state.get_path(),
                    explored_states=len(explored),
                    execution_time=exec_time,
                    memory_used=memory,
                    cost=current_cost  
                )
            
            state_key = current_state.get_state_key()
            if state_key in explored:
                continue
                
            explored.add(state_key)
            
            for successor, move_cost in current_state.get_successor_states():
                if successor.get_state_key() not in explored:
                    steps += 1
                    new_cost = current_cost + move_cost  
                    frontier.append((successor, path + [successor.get_path()[-1]], new_cost))
        
        return None

    def depth_first_search(self) -> Optional[SearchResult]: 
        start_time = self._checking_setup()
        frontier = deque([(self.initial_state, [], 0)]) 
        explored = set()
        steps = 0

        while frontier:
            current_state, path, current_cost = frontier.pop()
            if current_state.is_solved():
                exec_time, memory = self._end_profiling(start_time)
                return SearchResult(
                    steps=steps,
                    path=current_state.get_path(),
                    explored_states=len(explored),
                    execution_time=exec_time,
                    memory_used=memory,
                    cost=current_cost 
                )
            
            state_key = current_state.get_state_key()
            if state_key in explored:
                continue
                
            explored.add(state_key)
            
            for successor, move_cost in current_state.get_successor_states():
                if successor.get_state_key() not in explored:
                    steps += 1
                    new_cost = current_cost + move_cost 
                    frontier.append((successor, path + [successor.get_path()[-1]], new_cost))

        return None
    
    def uniform_cost_search(self) -> Optional[SearchResult]:
        start_time = time.time()
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        frontier = PriorityQueue()
        frontier.push(self.initial_state, 0)
        explored = set()

        g_score = {self.initial_state.get_state_key(): 0}
        came_from = {}
        steps = 0
        
        while not frontier.empty():
            current_state = frontier.pop()
            current_key = current_state.get_state_key()
            logger.debug(f"Current state:\n{current_state}")
            logger.debug(f"Current cost: {g_score[current_key]}")
            
            if current_state.is_solved():
                execution_time = time.time() - start_time
                memory_used = (process.memory_info().rss - initial_memory) / 1024 / 1024 
                
                return SearchResult(
                    steps=steps,
                    path=current_state.get_path(),
                    explored_states=len(explored),
                    execution_time=execution_time,
                    memory_used=memory_used,
                    cost=g_score[current_key]
                )
            
            if current_key in explored:
                continue
                
            explored.add(current_key)
            for successor_state, move_cost in current_state.get_successor_states():
                successor_key = successor_state.get_state_key()
                tentative_g_score = g_score[current_key] + move_cost
                if successor_key not in g_score or tentative_g_score < g_score[successor_key]:
                    came_from[successor_key] = current_state
                    g_score[successor_key] = tentative_g_score
                    frontier.push(successor_state, tentative_g_score)
                    steps += 1
                logger.debug(f"Steps: {steps}, Explored: {len(explored)}")
        return None

        
    def a_star_search(self) -> Optional[SearchResult]:
        start_time = self._checking_setup()
        frontier = PriorityQueue()
        initial_heuristic = self.initial_state.get_heuristic()
        frontier.push(self.initial_state, initial_heuristic)
        explored = set()
        g_score = {self.initial_state.get_state_key(): 0}
        f_score = {self.initial_state.get_state_key(): initial_heuristic}
        steps = 0

        while not frontier.empty():
            current_state = frontier.pop()
            current_heuristic = current_state.get_heuristic()
            current_g_score = g_score[current_state.get_state_key()]
            logger.info(f"Expanding State:\n{current_state}")
            logger.info(f"Current Heuristic: {current_heuristic}, g_score: {current_g_score}, f_score: {current_g_score + current_heuristic}")

            if current_state.is_solved():
                exec_time, memory = self._end_profiling(start_time)
                return SearchResult(
                    steps=steps,
                    path=current_state.get_path(),
                    explored_states=len(explored),
                    execution_time=exec_time,
                    memory_used=memory,
                    cost=current_g_score
                )
            
            state_key = current_state.get_state_key()
            if state_key in explored:
                continue
                
            explored.add(state_key)
            for successor_state, move_cost in current_state.get_successor_states():  
                successor_key = successor_state.get_state_key()
                tentative_g_score = current_g_score + move_cost
                successor_heuristic = successor_state.get_heuristic()
                f_score[successor_key] = tentative_g_score + successor_heuristic
                logger.debug(f"Successor State: {successor_state}")
                logger.debug(f"Successor Heuristic: {successor_heuristic}, Tentative g_score: {tentative_g_score}, f_score: {f_score[successor_key]}")
                
                if successor_key not in g_score or tentative_g_score < g_score[successor_key]:
                    g_score[successor_key] = tentative_g_score
                    frontier.push(successor_state, f_score[successor_key])
                    steps += 1
        
        return None
