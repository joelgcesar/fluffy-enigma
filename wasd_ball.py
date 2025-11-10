"""Simple 2D environment for moving a ball with WASD controls.

This module opens a Pygame window where a player can move a ball around the
screen using the WASD keys. The implementation keeps the ball within the window
boundaries and displays on-screen instructions.
"""

import pygame


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BACKGROUND_COLOR = (16, 20, 32)
BALL_COLOR = (224, 96, 128)
INSTRUCTION_COLOR = (220, 220, 220)


class Ball:
    """Represents a controllable ball in the 2D environment."""

    def __init__(self, position: pygame.math.Vector2, radius: int = 24, speed: int = 300) -> None:
        self.position = position
        self.radius = radius
        self.speed = speed

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        """Update the ball position based on pressed keys."""

        direction = pygame.math.Vector2()

        if keys[pygame.K_w]:
            direction.y -= 1
        if keys[pygame.K_s]:
            direction.y += 1
        if keys[pygame.K_a]:
            direction.x -= 1
        if keys[pygame.K_d]:
            direction.x += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.position += direction * self.speed * dt

        self._clamp_to_window()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the ball on the provided surface."""

        pygame.draw.circle(surface, BALL_COLOR, (int(self.position.x), int(self.position.y)), self.radius)

    def _clamp_to_window(self) -> None:
        """Keep the ball inside the window boundaries."""

        min_x = self.radius
        min_y = self.radius
        max_x = WINDOW_WIDTH - self.radius
        max_y = WINDOW_HEIGHT - self.radius

        self.position.x = max(min_x, min(self.position.x, max_x))
        self.position.y = max(min_y, min(self.position.y, max_y))


def draw_instructions(surface: pygame.Surface, font: pygame.font.Font) -> None:
    """Render on-screen instructions for the controls."""

    instructions = [
        "Move the ball with WASD",
        "Press ESC or close the window to exit",
    ]

    y_offset = 16
    for line in instructions:
        text_surface = font.render(line, True, INSTRUCTION_COLOR)
        surface.blit(text_surface, (16, y_offset))
        y_offset += text_surface.get_height() + 4


def main() -> None:
    """Entry point for running the environment."""

    pygame.init()
    pygame.display.set_caption("WASD Ball Environment")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 28)

    ball = Ball(pygame.math.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

    running = True
    while running:
        dt = clock.tick(120) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()
        ball.update(dt, keys)

        screen.fill(BACKGROUND_COLOR)
        ball.draw(screen)
        draw_instructions(screen, font)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
