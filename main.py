import pygame
import math
from typing import Union, Optional, Tuple, List


# Custom types for type hinting
Number = Union[int, float] # Represents integers and floats
Point = Tuple[Number, Number] # Represents an x, y coordinate


class Colours:
    """Predefined colours for easy reference."""
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    LIGHT_GREY = (211, 211, 211)
    DARK_GRAY = (169, 169, 169)

    RED = (255, 0, 0)
    BLUE = (0, 0, 255)

    LIGHT_RED = (220, 150, 150)
    LIGHT_BLUE = (150, 150, 220)


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
        self.elements = [] # Holds the elements to be drawn on the screen

    def attach(self, element):
        """Attaches an element to the display for rendering."""
        self.elements.append(element)

    def grid(self):
        """Draws a grid on the display."""
        self.screen.fill(Colours.WHITE)
        for x in range(0, self.width, 20):
            pygame.draw.line(self.screen, Colours.LIGHT_GREY, (x, 0), (x, self.height))
            for y in range(0, self.height, 20):
                pygame.draw.line(self.screen, Colours.LIGHT_GREY, (0, y), (self.width, y))

    def update(self):
        """Updates the display by drawing the grid and all the elements."""
        self.grid()
        # Draw all elements onto the screen
        for element in self.elements:
            element.draw(self.screen)
        pygame.display.flip()

    def run(self):
        running = True
        # Main loop that manages events and updates the display
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            # Update the display every frame
            self.update()
            self.clock.tick(60)
        pygame.quit()


class MagnetManager:
    """Manages multiple magnets and their interactions together."""

    def __init__(self, display: Display):
        self.display = display
        self.display.attach(self)
        self.magnets = list()
        self.ferrites = list()

    def attach(self, element):
        """Attaches an element to the manager and the display."""
        if isinstance(element, Magnet):
            self.attach_magnet(element)
        elif isinstance(element, FerriteDipole):
            self.attach_ferrite(element)

    def attach_magnet(self, magnet: 'Magnet'):
        """Attaches a magnet to the manager and the display."""
        self.magnets.append(magnet)
        self.display.attach(magnet)
        # Override the magnet's magnets reference with a reference to the manager's magnets
        magnet.magnets = self.magnets

    def attach_ferrite(self, ferrite: 'FerriteDipole'):
        """Attaches a ferrite dipole to the manager and the display."""
        self.ferrites.append(ferrite)
        self.display.attach(ferrite)

    def draw(self, screen: pygame.Surface):
        """Draws all magnets and their field lines."""
        # Separate magnets that are 'off,' to ignore field lines and collisions
        on_magnets = [magnet for magnet in self.magnets if magnet.strength > 0]
        for magnet in on_magnets:
            magnet.draw_field_lines(screen, on_magnets)


class Magnet:
    """Represents a simple magnet consisting of two point charges."""

    # Resolution for field line calculations
    FIELD_RESOLUTION = 1

    def __init__(
            self,
            position: Point,
            angle: Number = 0,
            strength: Number = 10,
            radius: int = 8,
            separation: int = 40,
            field_lines: int = 12,
            magnets: Optional[List['Magnet']] = None,
        ):
        # List of magnets for field calculations
        self.magnets = magnets or []
        # Add this magnet to the list of magnets for field calculations
        self.magnets.append(self)

        self.x, self.y = position
        self.angle = math.radians(angle)
        self.separation = separation

        # Calculate the positions of the two poles based on the angle and separation
        south_x = self.x + self.separation/2 * math.sin(self.angle)
        south_y = self.y - self.separation/2 * math.cos(self.angle)
        self.south = (south_x, south_y)

        north_x = self.x - self.separation/2 * math.sin(self.angle)
        north_y = self.y + self.separation/2 * math.cos(self.angle)
        self.north = (north_x, north_y)

        self.strength = strength
        self.radius = radius
        self.field_lines = field_lines

    def in_bounds(self, point: Point) -> bool:
        """Checks if a point is within the bounds of the display."""
        return 0 <= point[0] < 400 and 0 <= point[1] < 400

    def near_pole(self, point: Point, magnets: List['Magnet']) -> bool:
        """Checks if a point is near any pole of any of the magnets."""
        for magnet in list(magnets):
            # Subtract a small amount to prevent field lines from stopping just outside the pole
            radius = magnet.radius - 1
            # Check if the point is within the radius of either pole of the magnet
            for pole in [magnet.south, magnet.north]:
                dx = point[0] - pole[0]
                dy = point[1] - pole[1]
                distance_squared = dx**2 + dy**2
                if distance_squared < radius**2:
                    return True
        return False

    def validate_field_position(
            self,
            point: Point,
            magnets: List['Magnet']
        ) -> bool:
        """Checks if a point is valid for drawing a field line (not out of bounds and not near a pole)."""
        return self.in_bounds(point) and not self.near_pole(point, magnets)

    def calculate_field_direction(self, point: Point, magnets: List['Magnet']) -> float:
        """Calculates the direction of the magnetic field strength at a given point due to surrounding magnets."""
        x_component = 0
        y_component = 0
        for magnet in magnets:
            # Calculate the contribution of each pole to the field at the point
            for i, pole in enumerate([magnet.south, magnet.north]):
                dx = point[0] - pole[0]
                dy = point[1] - pole[1]
                distance_squared = dx**2 + dy**2
                if distance_squared == 0:
                    continue # No dividing by zero
                # The strength contribution is positive (attractive) for the north pole and negative (repulsive) for the south pole
                pole_strength = -magnet.strength if i == 0 else magnet.strength
                strength_contribution = pole_strength / distance_squared
                x_component += strength_contribution * (dx / math.sqrt(distance_squared))
                y_component += strength_contribution * (dy / math.sqrt(distance_squared))
        # Calculate the angle of the resulting field vector
        return math.atan2(y_component, x_component)

    def draw_field_lines(self, screen: pygame.Surface, magnets: List['Magnet']):
        """Draws magnetic field lines from the north pole."""
        # Draw field lines from each pole at regular angular intervals
        angle_increment = 2 * math.pi / self.field_lines
        for pole, offset in [(self.north, 0), (self.south, math.pi)]:
            # Start field lines at regular angles around the pole
            for i in range(self.field_lines):
                angle = i * angle_increment
                x = pole[0] + self.radius * math.cos(angle)
                y = pole[1] + self.radius * math.sin(angle)
                points = [(x, y)]
                # Trace the field while still in bounds and not near a pole
                while self.validate_field_position((x, y), magnets):
                    direction = self.calculate_field_direction(points[-1], magnets)
                    direction += offset # Field travels in opposite direction for the south pole
                    x += self.FIELD_RESOLUTION * math.cos(direction)
                    y += self.FIELD_RESOLUTION * math.sin(direction)
                    points.append((x, y))
                # Only draw if there are at least 2 points to form a line
                if len(points) > 1:
                    pygame.draw.lines(screen, Colours.BLACK, False, points, 1)

    def draw(self, screen: pygame.Surface):
        """Draws the magnet as two point charges."""
        if self.strength > 0:
            pygame.draw.circle(screen, Colours.BLUE, self.south, self.radius)
            pygame.draw.circle(screen, Colours.RED, self.north, self.radius)
        else:
            pygame.draw.circle(screen, Colours.DARK_GRAY, self.south, self.radius)
            pygame.draw.circle(screen, Colours.DARK_GRAY, self.north, self.radius)


class FerriteDipole:
    """Represents a ferrite dipole that can rotate based on the magnetic field."""

    def __init__(
        self,
        position: tuple[int, int],
        length: int = 80,
        width: int = 5,
    ):
        self.position = position
        self.length = length
        self.width = width
        self.angle = 0
        self.north = (position[0], position[1] - length/2)
        self.south = (position[0], position[1] + length/2)

    def update_moment(self, magnets: List[Magnet]):
        """Updates the moment of the ferrite dipole based on the magnetic field."""
        force_x, force_y = 0, 0
        # Calculate the sum of the forces on the ferrite (moment)
        for r in range(-int(self.length/2), int(self.length/2)+1, 2):
            x = self.position[0] + r * math.cos(math.radians(self.angle))
            y = self.position[1] + r * math.sin(math.radians(self.angle))
            for magnet in magnets:
                for pole in [magnet.south, magnet.north]:
                    strength = magnet.strength if pole == magnet.south else -magnet.strength
                    dx = pole[0] - x
                    dy = pole[1] - y
                    if not dx and not dy:
                        return 0, 0
                    distance = math.sqrt(dx**2 + dy**2)
                    force = strength / distance**2
                    angle = math.atan2(dy, dx)
                    force_x += force * math.cos(angle)
                    force_y += force * math.sin(angle)

        angle = math.atan2(force_y, force_x)
        self.angle = math.degrees(angle)

        # Update the positions of the north and south poles based on the new moment
        self.north = (
            self.position[0] + (self.length/2) * math.cos(angle),
            self.position[1] + (self.length/2) * math.sin(angle),
        )
        self.south = (
            self.position[0] - (self.length/2) * math.cos(angle),
            self.position[1] - (self.length/2) * math.sin(angle),
        )

    def draw(self, window: pygame.Surface):
        """Draws the ferrite dipole as a line between the north and south poles."""
        pygame.draw.line(window, Colours.LIGHT_RED, self.north, self.position, self.width)
        pygame.draw.line(window, Colours.LIGHT_BLUE, self.south, self.position, self.width)


def three_magnet_simulation(display: Display):
    """Simulates the force experienced by a dipole by changing magnet strengths over time."""
    class Animation:
        """Wrapper to animate values via the draw method."""
        def __init__(self, magnets: List[Magnet], dipole: FerriteDipole):
            self.magnets = magnets
            self.dipole = dipole
            self.index = 0
            self.next = 1
        def draw(self, _):
            # Gradually modify the strengths of the magnets
            self.magnets[self.index].strength -= 0.1
            self.magnets[self.next].strength += 0.1
            if self.magnets[self.index].strength <= 0:
                self.magnets[self.index].strength = 0
                self.magnets[self.next].strength = 10
                self.index = self.next
                self.next = (self.next + 1) % len(self.magnets)
            # Update the moments of the ferrite based on the new magnet strengths
            self.dipole.update_moment(self.magnets)
    # Attach magnets and dipoles to the manager
    x_offset = 100 * math.sin(math.radians(120))
    mm = MagnetManager(display)
    mm.attach(Magnet((200, 125), 90))
    mm.attach(Magnet((200 + x_offset, 275), 225))
    mm.attach(Magnet((200 - x_offset, 275), -45, 0))
    mm.attach(FerriteDipole((200, 200)))
    display.attach(Animation(mm.magnets, mm.ferrites[0]))


if __name__ == "__main__":
    # Set up the display
    display = Display(400, 400, "Magnetism Simulation")

    # Set up the three magnet simulation
    three_magnet_simulation(display)

    # Run the display loop
    display.run()