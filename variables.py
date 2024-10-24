# This is the file to declare the setting variables.
import pygame

# Window
APP_WIDTH, APP_HEIGHT = 610, 680
APP_CAPTION = r"The Rok"
FPS = 60


# Map


# Background



STATE_HOME = "home"
STATE_PLAYING = "playing"
STATE_ABOUT = "about"
STATE_LEVEL = "level"
STATE_SETTING = "setting"
STATE_GAMEOVER = "gameover"
STATE_VICTORY = "victory"


HOME_BG_WIDTH, HOME_BG_HEIGHT = APP_WIDTH, APP_HEIGHT - 410
START_POS = pygame.Rect(150, 325, 300, 50)
SETTING_POS = pygame.Rect(150, 405, 300, 50)
ABOUT_POS = pygame.Rect(150, 485, 300, 50)
EXIT_POS = pygame.Rect(150, 565, 300, 50)

BACK_LEVEL_POS = pygame.Rect(500, 600, 70, 50)
BACK_POS = pygame.Rect(225, 530, 150, 50)
OK_POS = pygame.Rect(255, 620, 100, 50)

ROW_PADDING, COL_PADDING = 50, 60
MAP_WIDTH, MAP_HEIGHT = APP_WIDTH - ROW_PADDING, APP_HEIGHT - COL_PADDING

MAP_POS_X, MAP_POS_Y = ROW_PADDING // 2, COL_PADDING * 2 // 3
SCORE_POS = (30, 10)
READY_POS = (APP_WIDTH // 2, 10)
HOME_RECT = (APP_WIDTH - ROW_PADDING - 20, 10, 40, 20)
SPEED_RECT = (APP_WIDTH - ROW_PADDING - 150, 10, 110, 20)

CELL_SIZE = 20
ROW, COL = MAP_WIDTH // CELL_SIZE, MAP_HEIGHT // CELL_SIZE

SPEED = 250
COIN_IMAGE = r"../Assets/effects/coin.jpg"

COIN_POS = (200, 430)
COIN_WIDTH, COIN_HEIGHT = (200, 200)
GAMEOVER_BACKGROUND_WIDTH, GAMEOVER_BACKGROUND_HEIGHT = HOME_BG_WIDTH, HOME_BG_HEIGHT + 300

VICTORY_WIDTH, VICTORY_HEIGHT = (500, 400)


SCORE_BONUS = 20
SCORE_PENALTY = -1


FONT = r"../Fonts/8514fix.fon"


BACKGROUND_COLOR = (65, 98, 132)
LIGHT_GREY = (170, 170, 170)
DARK_GREY = (75, 75, 75)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
TOMATO = (255, 99, 71)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

PACMAN_IMAGE = r"../Assets/effects/pacman.png"
PACMAN_LEFT = r"../Assets/effects/pacman_left.png"
PACMAN_RIGHT = r"../Assets/effects/pacman_right.png"
PACMAN_DOWN = r"../Assets/effects/pacman_down.png"
PACMAN_UP = r"../Assets/effects/pacman_up.png"

BLACK_BG = r"../Assets/effects/bg.png"

MONSTER_LEFT_IMAGE = r"../Assets/effects/ghost left.png"
MONSTER_RIGHT_IMAGE = r"../Assets/effects/ghost right.png"
MONSTER_UP_IMAGE = r"../Assets/effects/ghost up.png"
MONSTER_DOWN_IMAGE = r"../Assets/effects/ghost down.png"