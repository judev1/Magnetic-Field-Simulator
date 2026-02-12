import pygame


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

    def run(self):
        running = True
        # Main loop that manages events and updates the display
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    # Set up the display
    display = Display(400, 400, "Magnetism Simulation")
    display.run()