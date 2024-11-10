import pygame
import sys
from main import main
pygame.init()

screen_width, screen_height = 500, 500
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Map Selection and Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
HIGHLIGHT = (100, 100, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

fontOption = pygame.font.Font(None, 20)
fontGame = pygame.font.Font(None, 30)
fontRock = pygame.font.Font(None, 16)

waiting = True

map_files = [f"input/input-0{i}.txt" for i in range(1, 12)]
output_files = [f"output/output-0{i}.txt" for i in range(1,12)]
option_height = 20
active_dropdown = None
selected_map = None
selected_algorithm = None
selected_output = None
speed_multiplier = 1

button1_rect = pygame.Rect(25, 40, 100, option_height)
button2_rect = pygame.Rect(200, 40, 100, option_height)
start_button_rect = pygame.Rect(375, 40, 100, option_height)
info_button_rect = pygame.Rect(380, screen_height-30, 250, 50)
info_button_text = "Show Output"
start_button_text = "Start"
button1_text = "Select Map"
button2_text = "Select Algo"

MAP_SELECTION = "map_selection"
GAME_SCREEN = "game_screen"
OUTPUT_SCREEN = "output_screen"
current_screen = MAP_SELECTION
map_data = None

cell_size = 30  
step_count = 0
total_cost = 0
path_index = 0
path = []
game_result = None
character_x, character_y = 0, 0

ares_image = pygame.image.load("images/character.png")
ares_image = pygame.transform.scale(ares_image, (cell_size, cell_size))

rock_image = pygame.image.load("images/gold.png")
rock_image = pygame.transform.scale(rock_image, (cell_size*0.6, cell_size*0.6))

floor_image = pygame.image.load("images/grass.jpg") 
floor_image = pygame.transform.scale(floor_image, (cell_size, cell_size))

wall_image = pygame.image.load("images/brickwall.png") 
wall_image = pygame.transform.scale(wall_image, (cell_size, cell_size))

state1_image = pygame.image.load("images/full_chest.png") 
state1_image = pygame.transform.scale(state1_image, (cell_size, cell_size))

state2_image = pygame.image.load("images/empty_chest.png") 
state2_image = pygame.transform.scale(state2_image, (cell_size, cell_size))

special_cells = {}

def load_output(file_name):
    strings_list = []
    with open(file_name, "r") as file:
        for line in file:
            strings_list.append(line.strip())
    return strings_list

def load_map(filename):
    global map_data, character_x, character_y, rock_data, under_ares, special_cells
    rock_data = {}
    special_cells.clear()
    
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()

        weights = list(map(float, lines[0].strip().split()))
        rock_index = 0
        map_data = [list(line.strip()) for line in lines[1:]]
        
        for y, row in enumerate(map_data):
            for x, cell in enumerate(row):
                if cell == "@":
                    character_x, character_y = x * cell_size, y * cell_size
                    under_ares = " "  
                    map_data[y][x] = "@" 
                elif cell == "$":  
                    if rock_index < len(weights):
                        rock_data[(x, y)] = weights[rock_index]
                        rock_index += 1
                    else:
                        print("Warning: Not enough weights provided for all rocks.")
                elif cell == "." or cell == "*":  
                    special_cells[(x, y)] = "."

        # print(f"Loaded {filename} successfully!")
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        map_data = []

def draw_map(sel=False):
    global map_data
    tmp_x, tmp_y = 0, 0

    if sel:
        map_width = len(map_data[0]) * cell_size
        map_height = len(map_data) * cell_size

        tmp_x = (screen_width - map_width) // 2
        tmp_y = (screen_height - map_height) // 2

    for y, row in enumerate(map_data):
        for x, cell in enumerate(row):
            screen.blit(floor_image, (tmp_x + x * cell_size, tmp_y + y * cell_size))
            if cell == "#":
                screen.blit(wall_image, (tmp_x + x * cell_size, tmp_y + y * cell_size))
            elif cell == ".":
                screen.blit(state2_image, (tmp_x + x * cell_size, tmp_y + y * cell_size))
            elif cell == "*":
                screen.blit(state1_image, (tmp_x + x * cell_size, tmp_y + y * cell_size))
            elif cell == "$":
                screen.blit(rock_image, (tmp_x + x * cell_size + 0.2 * cell_size, tmp_y + y * cell_size + 0.2 * cell_size))
                if (x, y) in rock_data:
                    display_rock_number(rock_data[(x, y)], tmp_x/cell_size + x, tmp_y/cell_size + y)

    for x in range(tmp_x, tmp_x + len(map_data[0]) * cell_size, cell_size):
        pygame.draw.line(screen, WHITE, (x, tmp_y), (x, tmp_y + len(map_data) * cell_size))
    for y in range(tmp_y, tmp_y + len(map_data) * cell_size, cell_size):
        pygame.draw.line(screen, WHITE, (tmp_x, y), (tmp_x + len(map_data[0]) * cell_size, y))
    screen.blit(ares_image, (tmp_x + character_x, tmp_y + character_y))

def move_ares(dx, dy, push=False):
    global character_x, character_y, step_count, total_cost, rock_data, under_ares
    grid_x, grid_y = character_x // cell_size, character_y // cell_size
    new_x, new_y = grid_x + dx, grid_y + dy

    if 0 <= new_x < len(map_data[0]) and 0 <= new_y < len(map_data):
        target_cell = map_data[new_y][new_x]

        if push and target_cell in ["$", "*"]:
            rock_new_x, rock_new_y = new_x + dx, new_y + dy
            if 0 <= rock_new_x < len(map_data[0]) and 0 <= rock_new_y < len(map_data):
                rock_target_cell = map_data[rock_new_y][rock_new_x]
                
                if rock_target_cell in [" ", "."]:
                    rock_weight = rock_data.get((new_x, new_y), 1) 
                    move_cost = 1 + rock_weight 
                    total_cost += move_cost  

                    if rock_target_cell == ".":
                        map_data[rock_new_y][rock_new_x] = "*" 
                    else:
                        map_data[rock_new_y][rock_new_x] = "$"  
                        
                    if target_cell == "*":
                        map_data[new_y][new_x] = "."  
                    else:
                        map_data[new_y][new_x] = " " 

                    if (new_x, new_y) in rock_data:
                        rock_data[(rock_new_x, rock_new_y)] = rock_data.pop((new_x, new_y))
                    
                    map_data[grid_y][grid_x] = special_cells.get((grid_x, grid_y), " ")
                    map_data[new_y][new_x] = "@"
                    character_x, character_y = new_x * cell_size, new_y * cell_size
                    step_count += 1
                    return True
                return False
            
        elif target_cell in [" ", "."]:
            move_cost = 1  
            total_cost += move_cost 

            map_data[grid_y][grid_x] = special_cells.get((grid_x, grid_y), " ")
            under_ares = target_cell
            map_data[new_y][new_x] = "@"
            character_x, character_y = new_x * cell_size, new_y * cell_size
            step_count += 1
            return True
    return False

def draw_button(rect, text, color):
    pygame.draw.rect(screen, GRAY, rect)
    button_text = fontOption.render(text, True, color)
    screen.blit(button_text, (rect.x + 10, rect.y + 5))
    pygame.draw.rect(screen, BLACK, rect.inflate(4, 4), 2)

def draw_options(rect, options, selected_index):
    for i, option_text in enumerate(options):
        option_rect = pygame.Rect(rect.x, rect.bottom + i * option_height, rect.width, option_height)
        color = HIGHLIGHT if i == selected_index else GRAY
        pygame.draw.rect(screen, color, option_rect)
        option_text = fontOption.render(option_text, True, BLACK)
        screen.blit(option_text, (option_rect.x + 10, option_rect.y + 5))
        pygame.draw.rect(screen, BLACK, rect.inflate(4, 4), 2)

def display_rock_number(number, rock_x, rock_y):
    pos_x = rock_x * cell_size
    pos_y = rock_y * cell_size
    number_surface = fontRock.render(str(int(number)), True, BLACK) 

    text_rect = number_surface.get_rect(center=(pos_x + cell_size // 2, pos_y + cell_size // 2))
    
    screen.blit(number_surface, text_rect)

def display_step_count():
    step_text = fontGame.render(f"Step: {step_count}", True, (0, 0, 0))
    pygame.draw.line(screen, (0, 0, 0), (0, screen_height - 40), (screen_width, screen_height - 40))
    screen.blit(step_text, (10, screen_height - 30))

def display_total_cost():
    cost_text = fontGame.render(f"Cost: {total_cost:.2f}", True, (0, 0, 0))
    screen.blit(cost_text, (150, screen_height - 30)) 

def display_result():
    if game_result:
        result_text = fontGame.render(f"{game_result}", True, (122, 0, 0) if game_result == "No solution" else (0, 122, 0))
        screen.blit(result_text, (screen_width // 2 - 35, screen_height // 2))

def check_game_result():
    global game_result, path_index, path

    if isinstance(path, str):
        return
    
    if path_index < len(path):
        return

    all_rocks_on_switches = True
    rocks_found = False
    for row in map_data:
        if "$" in row:  
            all_rocks_on_switches = False
            rocks_found = True
            break     
    if not rocks_found or all_rocks_on_switches:
        game_result = "Successful"
    else:
        game_result = "No solution"
    
def load_algorithms_output():
    output_data = {}
    algo_names = ["DFS", "BFS", "UCS", "A*"]

    for algo in algo_names:
        output_data[algo] = {}

    try:
        with open("output\output_table.txt", "r") as file:
            lines = file.readlines()
            current_algo = None

            for line in lines:
                line = line.strip()
                if line.startswith("DFS:"):
                    current_algo = "DFS"
                elif line.startswith("BFS:"):
                    current_algo = "BFS"
                elif line.startswith("Uniform Cost Search:"):
                    current_algo = "UCS"
                elif line.startswith("A*:"):
                    current_algo = "A*"
                elif current_algo:
                    if line.startswith("Moves:"):
                        output_data[current_algo]["Moves"] = line.split(":")[1].strip()
                    elif line.startswith("Time:"):
                        output_data[current_algo]["Time"] = line.split(":")[1].strip()
                    elif line.startswith("Memory:"):
                        output_data[current_algo]["Memory"] = line.split(":")[1].strip()
                    elif line.startswith("Path cost:"):
                        output_data[current_algo]["Path Cost"] = line.split(":")[1].strip()

    except FileNotFoundError:
        print("Error: output\output_table.txt not found.")
    
    return output_data

def map_selection_screen():
    global active_dropdown, selected_map, selected_output, selected_algorithm, current_screen, path, path_index, step_count, game_result
    screen.fill(WHITE)

    if selected_map is not None:
        draw_map(True)

    map_button_color = (150, 150, 150) if active_dropdown == "map" else BLACK  
    algo_button_color = (150, 150, 150) if active_dropdown == "algorithm" else BLACK  

    draw_button(button1_rect, button1_text, map_button_color)
    draw_button(button2_rect, button2_text, algo_button_color)

    Algo = ["DFS", "BFS", "UCS", "A*"]
    Map = ["Map 1", "Map 2", "Map 3", "Map 4", "Map 5", "Map 6", "Map 7", "Map 8", "Map 9", "Map 10", "Map 11"]

    if active_dropdown == "map":
        draw_options(button1_rect, Map, selected_map)
    elif active_dropdown == "algorithm":
        draw_options(button2_rect, Algo, selected_algorithm)

    if selected_map is not None:
        selected_map_text = fontOption.render(f"Selected Map: {Map[selected_map]}", True, BLACK)
        screen.blit(selected_map_text, (25, 5))  

    if selected_algorithm is not None:
        selected_algorithm_text = fontOption.render(f"Selected Algorithm: {Algo[selected_algorithm]}", True, BLACK)
        screen.blit(selected_algorithm_text, (200, 5))  

    if selected_map is not None and selected_algorithm is not None:
        pygame.draw.rect(screen, GRAY, start_button_rect)
        start_text = fontOption.render(start_button_text, True, BLACK)
        pygame.draw.rect(screen, BLACK, start_button_rect.inflate(4, 4), 2)
    else:
        pygame.draw.rect(screen, GRAY, start_button_rect)
        start_text = fontOption.render(start_button_text, True, (150, 150, 150))  
    screen.blit(start_text, (start_button_rect.x + 10, start_button_rect.y + 5))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if button1_rect.collidepoint(mouse_pos):
                active_dropdown = "map"  
            
            elif button2_rect.collidepoint(mouse_pos):
                active_dropdown = "algorithm"  
            elif active_dropdown == "map":
                for i, map_file in enumerate(Map):
                    option_rect = pygame.Rect(button1_rect.x, button1_rect.bottom + i * option_height, button1_rect.width, option_height)
                    if option_rect.collidepoint(mouse_pos):
                        selected_map = i
                        print(f"Map selected: {Map[selected_map]}")
                        selected_output = i
                        selected_algorithm = None
                        load_map(map_files[selected_map]) 
                        main(map_files[selected_map], output_files[selected_output])
                        active_dropdown = None
            elif active_dropdown == "algorithm":
                for i, algorithm in enumerate(Algo):
                    option_rect = pygame.Rect(button2_rect.x, button2_rect.bottom + i * option_height, button2_rect.width, option_height)
                    if option_rect.collidepoint(mouse_pos):
                        selected_algorithm = i
                        print(f"Algorithm selected: {algorithm}")
                        tmp = load_output("output.txt")
                        path = tmp[selected_algorithm]
                        path_index, step_count = 0, 0
                        game_result = None
                        active_dropdown = None
            elif start_button_rect.collidepoint(mouse_pos):
                if selected_map is not None and selected_algorithm is not None:
                    current_screen = GAME_SCREEN

def start_game():
    global path_index, path, waiting, game_result, selected_map, selected_algorithm, selected_output, current_screen, step_count, total_cost, speed_multiplier
    if 'speed_multiplier' not in globals():
        speed_multiplier = 1

    screen.fill(WHITE)
    draw_map()

    button_width = 70  
    button_height = 20  
    output_button_rect = pygame.Rect(390, screen_height - 30, 100, button_height)  
    back_button_rect = pygame.Rect(420, screen_height - 490, button_width, button_height)
    pause_button_rect = pygame.Rect(420, screen_height - 460, button_width, button_height)
    speed_button_rect = pygame.Rect(420, screen_height - 430, button_width, button_height)
    restart_button_rect = pygame.Rect(420, screen_height - 400, button_width, button_height)

    # Show output button
    pygame.draw.rect(screen, GRAY, output_button_rect)
    button_text = fontOption.render("Show Output", True, BLACK)
    text_rect = button_text.get_rect(center=(output_button_rect.centerx, output_button_rect.centery))
    screen.blit(button_text, text_rect)
    pygame.draw.rect(screen, BLACK, output_button_rect.inflate(4, 4), 2)

    # Back button
    pygame.draw.rect(screen, GRAY, back_button_rect)
    back_text = fontOption.render("Back", True, BLACK)
    back_text_rect = back_text.get_rect(center=(back_button_rect.centerx, back_button_rect.centery))
    screen.blit(back_text, back_text_rect)
    pygame.draw.rect(screen, BLACK, back_button_rect.inflate(4, 4), 2)

    # Pause button
    pause_text = "Resume" if waiting else "Pause"
    pygame.draw.rect(screen, GRAY, pause_button_rect)
    pause_button_text = fontOption.render(pause_text, True, BLACK)
    pause_text_rect = pause_button_text.get_rect(center=(pause_button_rect.centerx, pause_button_rect.centery))
    screen.blit(pause_button_text, pause_text_rect)
    pygame.draw.rect(screen, BLACK, pause_button_rect.inflate(4, 4), 2)

    # Speed button
    speed_text = "Speed x10" if speed_multiplier == 1 else "Speed x1"
    pygame.draw.rect(screen, GRAY, speed_button_rect)
    speed_button_text = fontOption.render(speed_text, True, BLACK)
    speed_button_text_rect = speed_button_text.get_rect(center=(speed_button_rect.centerx, speed_button_rect.centery))
    screen.blit(speed_button_text, speed_button_text_rect)
    pygame.draw.rect(screen, BLACK, speed_button_rect.inflate(4, 4), 2)

     # Restart button
    pygame.draw.rect(screen, GRAY, restart_button_rect)
    restart_text = fontOption.render("Restart", True, BLACK)
    restart_text_rect = restart_text.get_rect(center=(restart_button_rect.centerx, restart_button_rect.centery))
    screen.blit(restart_text, restart_text_rect)
    pygame.draw.rect(screen, BLACK, restart_button_rect.inflate(4, 4), 2)

    if waiting:
        text = fontGame.render("Press Enter to start", True, GRAY)
        screen.blit(text, (screen_width // 2 - 100, screen_height // 2))
    
    else:
        if isinstance(path, str) and "No solution" in path:
            game_result = "No solution"
        elif path_index < len(path):
            char = path[path_index]
            move_successful = False
            if char == "u": move_successful = move_ares(0, -1)
            elif char == "d": move_successful = move_ares(0, 1)
            elif char == "l": move_successful = move_ares(-1, 0)
            elif char == "r": move_successful = move_ares(1, 0)
            elif char == "U": move_successful = move_ares(0, -1, push=True)
            elif char == "D": move_successful = move_ares(0, 1, push=True)
            elif char == "L": move_successful = move_ares(-1, 0, push=True)
            elif char == "R": move_successful = move_ares(1, 0, push=True)
            if move_successful:
                path_index += 1
                check_game_result()
        display_step_count()
        display_total_cost()
        display_result()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                waiting = not waiting 
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if output_button_rect.collidepoint(mouse_pos):
                current_screen = OUTPUT_SCREEN
            elif back_button_rect.collidepoint(mouse_pos):
                current_screen = MAP_SELECTION
                load_map(map_files[selected_map]) 
                waiting = True  
                path_index = 0  
                step_count = 0  
                total_cost = 0
                game_result = None
                speed_multiplier = 1
            elif pause_button_rect.collidepoint(mouse_pos):
                waiting = not waiting 
            elif speed_button_rect.collidepoint(mouse_pos):
                speed_multiplier = 10 if speed_multiplier == 1 else 1
            elif restart_button_rect.collidepoint(mouse_pos): 
                load_map(map_files[selected_map]) 
                waiting = True
                path_index = 0
                step_count = 0
                total_cost = 0
                game_result = None
                speed_multiplier = 1

def output_screen():
    """Display the contents of output/output-01.txt in a comparative table format."""
    screen.fill(WHITE)  
    output_data = load_algorithms_output() 

    headers = ["Algorithm", "Moves", "Time", "Memory", "Path Cost"]
    y_offset = 50  
    line_height = 30  

    for idx, header in enumerate(headers):
        text_surface = fontOption.render(header, True, BLACK)
        screen.blit(text_surface, (10 + idx * 100, y_offset)) 
    pygame.draw.line(screen, BLACK, (10, y_offset + line_height-10), (screen_width - 10, y_offset + line_height-10))
    y_offset += line_height  

    for algo in output_data.keys():
        algo_data = output_data[algo]
        screen.blit(fontOption.render(algo, True, BLACK), (20, y_offset)) 
        screen.blit(fontOption.render(algo_data.get("Moves", ""), True, BLACK), (120, y_offset)) 
        screen.blit(fontOption.render(algo_data.get("Time", ""), True, BLACK), (180, y_offset))  
        screen.blit(fontOption.render(algo_data.get("Memory", ""), True, BLACK), (310, y_offset)) 
        screen.blit(fontOption.render(algo_data.get("Path Cost", ""), True, BLACK), (430, y_offset)) 

        pygame.draw.line(screen, BLACK, (10, y_offset + line_height-10), (screen_width - 10, y_offset + line_height-10))

        y_offset += line_height 

    back_button_rect = pygame.Rect(25, screen_height - 40, 100, 30)
    pygame.draw.rect(screen, GRAY, back_button_rect)
    back_text = fontOption.render("Back", True, BLACK) 
    back_text_rect = back_text.get_rect(center=(back_button_rect.centerx, back_button_rect.centery))
    screen.blit(back_text, back_text_rect)
    pygame.draw.rect(screen, BLACK, back_button_rect.inflate(4, 4), 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if back_button_rect.collidepoint(event.pos):
                global current_screen
                current_screen = GAME_SCREEN 

running = True
while running:
    if current_screen == MAP_SELECTION:
        map_selection_screen()
    elif current_screen == GAME_SCREEN:
        start_game()
        pygame.time.Clock().tick(4*speed_multiplier)
    elif current_screen == OUTPUT_SCREEN:
        output_screen()

    pygame.display.flip()