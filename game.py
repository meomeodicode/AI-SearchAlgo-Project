import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen settings
screen_width, screen_height = 500, 500
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Map Selection and Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
HIGHLIGHT = (100, 100, 255)

# Font settings
fontOption = pygame.font.Font(None, 20)
fontGame = pygame.font.Font(None, 36)

waiting = True

# Map files
map_files = [f"input/input-0{i}.txt" for i in range(1, 11)]
option_height = 20
active_dropdown = None
selected_map = None
selected_algorithm = None
selected_output = None

# Button settings for map selection
button1_rect = pygame.Rect(25, 40, 100, option_height)
button2_rect = pygame.Rect(200, 40, 100, option_height)
start_button_rect = pygame.Rect(375, 40, 100, option_height)
start_button_text = "Start"
button1_text = "Select Map"
button2_text = "Select Algo"

# Game states
MAP_SELECTION = "map_selection"
GAME_SCREEN = "game_screen"
current_screen = MAP_SELECTION
map_data = None

# Grid and character settings
cell_size = 30  # Size of each cell in the grid
step_count = 0
path_index = 0
path = []
game_result = None
character_x, character_y = 0, 0

# Colors for different elements
colors = {
    "#": (100, 100, 100),  # Wall - gray
    " ": (200, 200, 200),  # Free space - light gray
    "$": (200, 200, 200),  # Stone - brown
    "@": (255, 0, 0),      # Ares - red
    ".": (173, 216, 230),  # Switch place - light blue
    "*": (165, 42, 42),    # Stone on switch - dark red
    "+": (0, 0, 255),      # Ares on switch - blue
}

# Load images for Ares and rocks
ares_image = pygame.image.load("ngaoda.png")
ares_image = pygame.transform.scale(ares_image, (cell_size, cell_size))

rock_image = pygame.image.load("rock.png")
rock_image = pygame.transform.scale(rock_image, (cell_size, cell_size))

# Modify the load_map function to read rock weights and positions
def load_map(filename):
    global map_data, character_x, character_y, rock_data
    rock_data = {}  # Dictionary to store rock weights with positions as keys
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        # Parse the first line for rock weights
        first_line = lines[0].strip().split()
        for rock_info in first_line:
            pos, weight = rock_info.split(":")
            x, y = map(int, pos.strip("()").split(","))
            rock_data[(x, y)] = float(weight)
        
        # Load the rest of the map data (ignoring the first line)
        map_data = [list(line.strip()) for line in lines[1:]]
        
        # Find initial position of Ares (@)
        for row_index, row in enumerate(map_data):
            if "@" in row:
                character_x = row.index("@") * cell_size
                character_y = row_index * cell_size
                break
        
        print(f"Loaded {filename} successfully!")
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        map_data = []

# Modify the draw_map function to use display_rock_number with weight data
def draw_map():
    # Draw each cell and the corresponding color based on the map data
    for y, row in enumerate(map_data):
        for x, cell in enumerate(row):
            color = colors.get(cell, (255, 255, 255))  # Default to white if not in colors
            pygame.draw.rect(screen, color, (x * cell_size, y * cell_size, cell_size, cell_size))
            if cell == "$":
                screen.blit(rock_image, (x * cell_size, y * cell_size))
                # Display the rock's weight if available in rock_data
                if (x, y) in rock_data:
                    display_rock_number(rock_data[(x, y)], x, y)
    
    # Draw grid lines
    for x in range(0, screen_width, cell_size):
        pygame.draw.line(screen, BLACK, (x, 0), (x, screen_height - 40))
    for y in range(0, screen_height - 40, cell_size):
        pygame.draw.line(screen, BLACK, (0, y), (screen_width, y))

    screen.blit(ares_image, (character_x, character_y))

def load_output():
    strings_list = []
    file_name = "output.txt"
    with open(file_name, "r") as file:
        for line in file:
            strings_list.append(line.strip())
    return strings_list
# Modify move_ares function to update rock positions in rock_data
def move_ares(dx, dy, push=False):
    global character_x, character_y, step_count, rock_data
    grid_x, grid_y = character_x // cell_size, character_y // cell_size
    new_x, new_y = grid_x + dx, grid_y + dy

    if 0 <= new_x < len(map_data[0]) and 0 <= new_y < len(map_data):
        target_cell = map_data[new_y][new_x]
        if push and target_cell == "$":
            rock_new_x, rock_new_y = new_x + dx, new_y + dy
            if 0 <= rock_new_x < len(map_data[0]) and 0 <= rock_new_y < len(map_data):
                rock_target_cell = map_data[rock_new_y][rock_new_x]
                if rock_target_cell in [" ", "."]:
                    # Move the rock in the map_data
                    map_data[new_y][new_x] = " "
                    map_data[rock_new_y][rock_new_x] = "$" if rock_target_cell == " " else "*"
                    
                    # Update the rock's position in rock_data
                    rock_data[(rock_new_x, rock_new_y)] = rock_data.pop((new_x, new_y))
                    
                    # Move Ares
                    map_data[grid_y][grid_x] = " "
                    map_data[new_y][new_x] = "@"
                    character_x, character_y = new_x * cell_size, new_y * cell_size
                    step_count += 1
                    return
        elif target_cell in [" ", "."]:
            map_data[grid_y][grid_x] = " "
            map_data[new_y][new_x] = "@"
            character_x, character_y = new_x * cell_size, new_y * cell_size
            step_count += 1


# Dropdown menu for map selection
def draw_button(rect, text, color):
    pygame.draw.rect(screen, GRAY, rect)
    button_text = fontOption.render(text, True, color)
    screen.blit(button_text, (rect.x + 10, rect.y + 5))

def draw_options(rect, options, selected_index):
    for i, option_text in enumerate(options):
        option_rect = pygame.Rect(rect.x, rect.bottom + i * option_height, rect.width, option_height)
        color = HIGHLIGHT if i == selected_index else GRAY
        pygame.draw.rect(screen, color, option_rect)
        option_text = fontOption.render(option_text, True, BLACK)
        screen.blit(option_text, (option_rect.x + 10, option_rect.y + 5))

def map_selection_screen():
    global active_dropdown, selected_map, selected_output, selected_algorithm, current_screen, path, path_index, step_count, game_result
    screen.fill(WHITE)

    map_button_color = (150, 150, 150) if active_dropdown == "map" else BLACK  # Lighter if active
    algo_button_color = (150, 150, 150) if active_dropdown == "algorithm" else BLACK  # Lighter if active

    # Draw selection buttons
    draw_button(button1_rect, button1_text, map_button_color)
    draw_button(button2_rect, button2_text, algo_button_color)

    # Define options
    Algo = ["DFS", "BFS", "UCS", "A*"]
    Map = ["map 1", "map 2", "map 3", "map 4", "map 5", "map 6", "map 7", "map 8", "map 9", "map 10"]

    # Draw dropdowns based on active dropdown
    if active_dropdown == "map":
        draw_options(button1_rect, Map, selected_map)
    elif active_dropdown == "algorithm":
        draw_options(button2_rect, Algo, selected_algorithm)

    # Display the currently selected map and algorithm
    if selected_map is not None:
        selected_map_text = fontOption.render(f"Selected Map: {Map[selected_map]}", True, BLACK)
        screen.blit(selected_map_text, (25, 5))  # Position below map selection button

    if selected_algorithm is not None:
        selected_algorithm_text = fontOption.render(f"Selected Algorithm: {Algo[selected_algorithm]}", True, BLACK)
        screen.blit(selected_algorithm_text, (200, 5))  # Position below algorithm selection button

    # Draw the Start button
    if selected_map is not None and selected_algorithm is not None:
        # Fully visible button if both map and algorithm are selected
        pygame.draw.rect(screen, HIGHLIGHT, start_button_rect)
        start_text = fontOption.render(start_button_text, True, BLACK)
    else:
        # Faded button if selection is incomplete
        pygame.draw.rect(screen, GRAY, start_button_rect)
        start_text = fontOption.render(start_button_text, True, (150, 150, 150))  # Light gray text for disabled button
    screen.blit(start_text, (start_button_rect.x + 10, start_button_rect.y + 5))

    # Event handling for map selection screen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # Check if "Select Map" button was clicked
            if button1_rect.collidepoint(mouse_pos):
                active_dropdown = "map"  # Toggle dropdown to show map options
            # Check if "Select Algorithm" button was clicked
            elif button2_rect.collidepoint(mouse_pos):
                active_dropdown = "algorithm"  # Toggle dropdown to show algorithm options
            # Check if an option in the dropdown is clicked
            elif active_dropdown == "map":
                for i, map_file in enumerate(Map):
                    option_rect = pygame.Rect(button1_rect.x, button1_rect.bottom + i * option_height, button1_rect.width, option_height)
                    if option_rect.collidepoint(mouse_pos):
                        selected_map = i
                        selected_output = i
                        load_map(map_files[selected_map])  # Load the selected map file
                        active_dropdown = None
            elif active_dropdown == "algorithm":
                for i, algorithm in enumerate(Algo):
                    option_rect = pygame.Rect(button2_rect.x, button2_rect.bottom + i * option_height, button2_rect.width, option_height)
                    if option_rect.collidepoint(mouse_pos):
                        selected_algorithm = i  # Store the selected algorithm
                        print(f"Algorithm selected: {algorithm}")
                        tmp = load_output()
                        path = tmp[selected_algorithm]
                        path_index, step_count = 0, 0
                        game_result = None
                        active_dropdown = None
            # Check if "Start" button is clicked (only if both selections are made)
            elif start_button_rect.collidepoint(mouse_pos):
                if selected_map is not None and selected_algorithm is not None:
                    # Switch to game screen
                    current_screen = GAME_SCREEN
def display_rock_number(number, rock_x, rock_y):
    
    # Calculate the position in pixels
    pos_x = rock_x * cell_size
    pos_y = rock_y * cell_size
    
    # Render the number as a text surface
    number_surface = fontOption.render(str(number), True, (0, 0, 0))  # Black color for the number
    
    # Center the text within the cell
    text_rect = number_surface.get_rect(center=(pos_x + cell_size // 2, pos_y + cell_size // 2))
    
    # Blit (draw) the number on the screen
    screen.blit(number_surface, text_rect)

def display_step_count():
    step_text = fontGame.render(f"Step: {step_count}", True, (0, 0, 0))
    pygame.draw.line(screen, (0, 0, 0), (0, screen_height - 40), (screen_width, screen_height - 40))
    screen.blit(step_text, (10, screen_height - 30))

def display_result():
    if game_result:
        result_text = fontGame.render(f"{game_result}", True, (122, 0, 0) if game_result == "Fail" else (0, 122, 0))
        screen.blit(result_text, (screen_width // 2 - 50, screen_height - 30))

def check_game_result():
    global game_result
    game_result = "Successful" if all("$" not in row for row in map_data) else "Fail"

def start_game():
    global path_index, waiting, game_result, selected_map, selected_algorithm, selected_output, current_screen, step_count
    screen.fill((200, 200, 200))
    draw_map()

    # Display waiting message if waiting for Enter to start
    if waiting:
        text = fontGame.render("Press Enter to start", True, (255, 255, 255))
        screen.blit(text, (screen_width // 2 - 100, screen_height // 2))
    else:
        # Process the path if not waiting
        if path_index < len(path):
            char = path[path_index]
            if char == "u": move_ares(0, -1)
            elif char == "d": move_ares(0, 1)
            elif char == "l": move_ares(-1, 0)
            elif char == "r": move_ares(1, 0)
            elif char == "U": move_ares(0, -1, push=True)
            elif char == "D": move_ares(0, 1, push=True)
            elif char == "L": move_ares(-1, 0, push=True)
            elif char == "R": move_ares(1, 0, push=True)
            path_index += 1
        else:
            if game_result is None:
                check_game_result()
        display_step_count()
        display_result()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and waiting:
                waiting = False  # Start the game after Enter is pressed
            elif event.key == pygame.K_ESCAPE:
                # Return to map selection screen if ESC is pressed
                selected_map = None
                selected_algorithm = None
                selected_output = None
                current_screen = MAP_SELECTION
                waiting = True  # Reset waiting state for new game
                path_index = 0  # Reset path index
                step_count = 0  # Reset step count
                game_result = None  # Reset game result


# Main loop
running = True
while running:
    if current_screen == MAP_SELECTION:
        map_selection_screen()
    elif current_screen == GAME_SCREEN:
        start_game()
        pygame.time.Clock().tick(4)

    pygame.display.flip()