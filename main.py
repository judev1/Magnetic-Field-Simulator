import pygame


class Colours:
    """Predefined colours for easy reference."""
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    LIGHT_GREY = (211, 211, 211)
    DARK_GRAY = (169, 169, 169)


class Display:
    """Handles the display and rendering of the simulation."""

    def __init__(self, width: int, height: int, title: str = "Display"):
        # Initialise Pygame and set up the display window
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()

    def grid(self):
        """Draws a grid on the display."""
        self.screen.fill(Colours.WHITE)
        for x in range(0, self.width, 20):
            pygame.draw.line(self.screen, Colours.LIGHT_GREY, (x, 0), (x, self.height))
            for y in range(0, self.height, 20):
                pygame.draw.line(self.screen, Colours.LIGHT_GREY, (0, y), (self.width, y))

    def run(self):
        running = True
        # Main loop that manages events and updates the display
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.grid()
            self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    # Set up the display
    display = Display(400, 400, "Magnetism Simulation")
    display.run()