import pygame 

class stones: 
    STONES_IMAGE = ".../Assets/granite.png"
    CELL_SIZE = " "
    def __init__(self, app, pos, weight, cell_size):
        self.app = app
        self.width = 10
        self.grid_pos = [pos[0], pos[1]]
        self.pixel_pos = self.get_current_pixel_pos()
        self.image = pygame.image.load(self.STONES_IMAGE)
        self.image = pygame.transform.scale(self.image, (self.width, self.width))
        self.weight = weight
        self.cell_size = cell_size
    def get_current_pixel(image):
          return [self.grid_pos[0] * cell_size + cell_size // 2 - self.width // 2 + MAP_POS_X,
                self.grid_pos[1] * cell_size + cell_size // 2 - self.width // 2 + MAP_POS_Y]
    def draw(self):
        stones = self.app.screen.blit(self.image, (self.pixel_pos[0], self.pixel_pos[1]))
        pygame.display.update(stones)