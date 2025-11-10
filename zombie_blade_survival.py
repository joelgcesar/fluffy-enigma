"""A simple Pygame survival game with a spinning blade."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Tuple

import pygame


WIDTH = 900
HEIGHT = 600
BACKGROUND_COLOR = (18, 18, 18)
HERO_COLOR = (240, 240, 240)
ZOMBIE_COLOR = (25, 161, 66)
BLADE_COLOR = (209, 67, 67)


@dataclass
class Settings:
    hero_speed: float = 260
    zombie_speed: float = 100
    spawn_interval: float = 1.6
    spawn_decay: float = 0.985
    spawn_minimum: float = 0.35
    blade_radius: float = 70
    blade_speed: float = 360  # degrees per second


class Hero(pygame.sprite.Sprite):
    def __init__(self, pos: Tuple[float, float]) -> None:
        super().__init__()
        radius = 18
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, HERO_COLOR, (radius, radius), radius)
        self.rect = self.image.get_rect(center=pos)
        self.speed = Settings.hero_speed

    def handle_input(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        move_x = keys[pygame.K_d] - keys[pygame.K_a]
        move_y = keys[pygame.K_s] - keys[pygame.K_w]
        magnitude = math.hypot(move_x, move_y)
        if magnitude:
            move_x /= magnitude
            move_y /= magnitude

        self.rect.x += move_x * self.speed * dt
        self.rect.y += move_y * self.speed * dt
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))


class Zombie(pygame.sprite.Sprite):
    def __init__(self, target: Hero) -> None:
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, ZOMBIE_COLOR, (15, 15), 15)
        self.rect = self.image.get_rect(center=self._spawn_position())
        self.target = target
        self.speed = Settings.zombie_speed

    @staticmethod
    def _spawn_position() -> Tuple[int, int]:
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            return random.randrange(0, WIDTH), -40
        if edge == "bottom":
            return random.randrange(0, WIDTH), HEIGHT + 40
        if edge == "left":
            return -40, random.randrange(0, HEIGHT)
        return WIDTH + 40, random.randrange(0, HEIGHT)

    def update(self, dt: float) -> None:
        direction = (self.target.rect.centerx - self.rect.centerx,
                     self.target.rect.centery - self.rect.centery)
        distance = math.hypot(*direction)
        if distance:
            dx = direction[0] / distance
            dy = direction[1] / distance
            self.rect.x += dx * self.speed * dt
            self.rect.y += dy * self.speed * dt


class Blade(pygame.sprite.Sprite):
    def __init__(self, hero: Hero) -> None:
        super().__init__()
        size = (16, 42)
        self.base_image = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.polygon(
            self.base_image,
            BLADE_COLOR,
            [(size[0] // 2, 0), (0, size[1]), (size[0], size[1])],
        )
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.hero = hero
        self.angle = 0
        self.radius = Settings.blade_radius
        self.rotation_speed = Settings.blade_speed

    def update(self, dt: float) -> None:
        self.angle = (self.angle + self.rotation_speed * dt) % 360
        radians = math.radians(self.angle)
        offset_x = math.cos(radians) * self.radius
        offset_y = math.sin(radians) * self.radius
        center = (self.hero.rect.centerx + offset_x,
                  self.hero.rect.centery + offset_y)
        self.image = pygame.transform.rotate(self.base_image, -self.angle)
        self.rect = self.image.get_rect(center=center)


def draw_hud(screen: pygame.Surface, timer: float) -> None:
    font = pygame.font.SysFont("arial", 24)
    seconds = math.floor(timer)
    text = font.render(f"Survived: {seconds}s", True, (200, 200, 200))
    screen.blit(text, (16, 16))


def draw_game_over(screen: pygame.Surface, timer: float) -> None:
    gothic = pygame.font.SysFont("oldenglishtext", 86)
    if gothic is None:
        gothic = pygame.font.SysFont("arialblack", 86)
    text = gothic.render("YOU DIED", True, (196, 20, 20))
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, rect)

    font = pygame.font.SysFont("arial", 26)
    detail = font.render(
        f"You lasted {timer:.1f} seconds. Press R to restart.", True, (220, 220, 220)
    )
    screen.blit(detail, detail.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80)))


def spawn_zombie(zombies: pygame.sprite.Group, hero: Hero) -> None:
    zombies.add(Zombie(hero))


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Blade Survival")
    clock = pygame.time.Clock()

    def reset() -> Tuple[Hero, Blade, pygame.sprite.Group]:
        hero = Hero((WIDTH // 2, HEIGHT // 2))
        blade = Blade(hero)
        zombies = pygame.sprite.Group()
        return hero, blade, zombies

    hero, blade, zombies = reset()
    spawn_timer = 0.0
    spawn_interval = Settings.spawn_interval
    survival_time = 0.0
    game_over = False

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over and event.key == pygame.K_r:
                    hero, blade, zombies = reset()
                    spawn_timer = 0.0
                    spawn_interval = Settings.spawn_interval
                    survival_time = 0.0
                    game_over = False

        if not game_over:
            survival_time += dt
            hero.handle_input(dt)
            zombies.update(dt)
            blade.update(dt)

            spawn_timer += dt
            if spawn_timer >= spawn_interval:
                spawn_timer = 0.0
                spawn_zombie(zombies, hero)
                spawn_interval = max(Settings.spawn_minimum, spawn_interval * Settings.spawn_decay)

            # collisions
            for zombie in pygame.sprite.spritecollide(blade, zombies, dokill=True):
                del zombie

            if pygame.sprite.spritecollideany(hero, zombies):
                game_over = True

        screen.fill(BACKGROUND_COLOR)
        zombies.draw(screen)
        screen.blit(hero.image, hero.rect)
        screen.blit(blade.image, blade.rect)

        draw_hud(screen, survival_time)
        if game_over:
            draw_game_over(screen, survival_time)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

