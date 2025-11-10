"""A simple Pygame survival game with a spinning rod."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

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
    rod_length: float = 140
    rod_thickness: float = 18
    rod_speed: float = 360  # degrees per second
    brute_spawn_chance: float = 0.15
    brute_spawn_growth: float = 0.035
    powerup_interval: float = 12.0
    extra_rod_duration: float = 10.0


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
        self.hit_radius = 15
        self.health = 1
        self.knockback_timer = 0.0
        self.knockback_velocity = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)

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

    def take_hit(self, impact_vector: pygame.math.Vector2) -> bool:
        self.health -= 1
        return self.health <= 0

    def update(self, dt: float) -> None:
        if self.knockback_timer > 0:
            self.pos += self.knockback_velocity * dt
            self.knockback_timer = max(0.0, self.knockback_timer - dt)
            self.knockback_velocity *= 0.82
        else:
            direction = pygame.math.Vector2(self.target.rect.center) - self.pos
            distance = direction.length()
            if distance:
                direction.scale_to_length(self.speed * dt)
                self.pos += direction

        self.rect.center = (round(self.pos.x), round(self.pos.y))


class BruteZombie(Zombie):
    COLOR = (136, 84, 208)

    def __init__(self, target: Hero) -> None:
        super().__init__(target)
        size = 46
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.COLOR, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=self._spawn_position())
        self.hit_radius = size // 2
        self.pos = pygame.math.Vector2(self.rect.center)
        self.health = 2
        self.knockback_strength = 220
        self.knockback_duration = 0.28

    def take_hit(self, impact_vector: pygame.math.Vector2) -> bool:
        self.health -= 1
        if self.health == 1:
            if impact_vector.length_squared() > 0:
                direction = impact_vector.normalize()
                self.knockback_velocity = direction * self.knockback_strength
                self.knockback_timer = self.knockback_duration
        return self.health <= 0


class Rod:
    def __init__(self, hero: Hero, angle_offset: float = 0.0) -> None:
        self.hero = hero
        self.length = Settings.rod_length
        self.thickness = Settings.rod_thickness
        self.rotation_speed = Settings.rod_speed
        self.angle = angle_offset

    def update(self, dt: float) -> None:
        self.angle = (self.angle + self.rotation_speed * dt) % 360

    def segment(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        radians = math.radians(self.angle)
        start = pygame.math.Vector2(self.hero.rect.center)
        offset = pygame.math.Vector2(math.cos(radians), math.sin(radians)) * self.length
        end = start + offset
        return (start.x, start.y), (end.x, end.y)

    def draw(self, surface: pygame.Surface) -> None:
        start, end = self.segment()
        pygame.draw.line(
            surface,
            BLADE_COLOR,
            (int(start[0]), int(start[1])),
            (int(end[0]), int(end[1])),
            int(self.thickness),
        )


class PowerUp(pygame.sprite.Sprite):
    COLOR = (232, 189, 57)
    SIZE = 24

    def __init__(self) -> None:
        super().__init__()
        self.image = pygame.Surface((self.SIZE, self.SIZE), pygame.SRCALPHA)
        pygame.draw.circle(
            self.image,
            self.COLOR,
            (self.SIZE // 2, self.SIZE // 2),
            self.SIZE // 2,
        )
        padding = 40
        x = random.randrange(padding, WIDTH - padding)
        y = random.randrange(padding, HEIGHT - padding)
        self.rect = self.image.get_rect(center=(x, y))


def draw_hud(screen: pygame.Surface, timer: float, extra_timer: float) -> None:
    font = pygame.font.SysFont("arial", 24)
    seconds = math.floor(timer)
    text = font.render(f"Survived: {seconds}s", True, (200, 200, 200))
    screen.blit(text, (16, 16))

    if extra_timer > 0:
        buff = font.render(
            f"Double rod: {extra_timer:.1f}s", True, (232, 189, 57)
        )
        screen.blit(buff, (16, 48))


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


def spawn_zombie(zombies: pygame.sprite.Group, hero: Hero, survival_time: float) -> None:
    brute_chance = min(
        0.65,
        Settings.brute_spawn_chance + survival_time * Settings.brute_spawn_growth,
    )
    if random.random() < brute_chance:
        zombies.add(BruteZombie(hero))
    else:
        zombies.add(Zombie(hero))


def apply_rod_damage(hero: Hero, rods: List[Rod], zombies: pygame.sprite.Group) -> None:
    if not rods or not zombies:
        return

    hero_center = pygame.math.Vector2(hero.rect.center)
    for rod in rods:
        start_raw, end_raw = rod.segment()
        start = pygame.math.Vector2(start_raw)
        end = pygame.math.Vector2(end_raw)
        segment = end - start
        length_sq = segment.length_squared()
        if length_sq == 0:
            continue

        for zombie in list(zombies):
            zombie_center = pygame.math.Vector2(zombie.rect.center)
            projection = (zombie_center - start).dot(segment) / length_sq
            projection = max(0.0, min(1.0, projection))
            closest = start + segment * projection
            distance = zombie_center.distance_to(closest)
            if distance <= zombie.hit_radius + rod.thickness / 2:
                impact_vector = zombie_center - hero_center
                if zombie.take_hit(impact_vector):
                    zombies.remove(zombie)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rod Survival")
    clock = pygame.time.Clock()

    def reset() -> Tuple[Hero, Rod, pygame.sprite.Group]:
        hero = Hero((WIDTH // 2, HEIGHT // 2))
        rod = Rod(hero)
        zombies = pygame.sprite.Group()
        return hero, rod, zombies

    hero, primary_rod, zombies = reset()
    rods: List[Rod] = [primary_rod]
    bonus_rod: Optional[Rod] = None
    extra_rod_timer = 0.0
    powerup: Optional[PowerUp] = None
    powerup_timer = 0.0
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
                    hero, primary_rod, zombies = reset()
                    rods = [primary_rod]
                    bonus_rod = None
                    powerup = None
                    extra_rod_timer = 0.0
                    powerup_timer = 0.0
                    spawn_timer = 0.0
                    spawn_interval = Settings.spawn_interval
                    survival_time = 0.0
                    game_over = False

        if not game_over:
            survival_time += dt
            hero.handle_input(dt)
            zombies.update(dt)

            if bonus_rod is not None:
                rods = [primary_rod, bonus_rod]
            else:
                rods = [primary_rod]

            for rod in rods:
                rod.update(dt)

            spawn_timer += dt
            if spawn_timer >= spawn_interval:
                spawn_timer = 0.0
                spawn_zombie(zombies, hero, survival_time)
                spawn_interval = max(
                    Settings.spawn_minimum, spawn_interval * Settings.spawn_decay
                )

            if powerup is None:
                powerup_timer += dt
                if powerup_timer >= Settings.powerup_interval:
                    powerup = PowerUp()
                    powerup_timer = 0.0

            if powerup and hero.rect.colliderect(powerup.rect):
                bonus_rod = Rod(hero, (primary_rod.angle + 180.0) % 360)
                extra_rod_timer = Settings.extra_rod_duration
                powerup = None

            if extra_rod_timer > 0:
                extra_rod_timer = max(0.0, extra_rod_timer - dt)
                if extra_rod_timer <= 0:
                    bonus_rod = None

            apply_rod_damage(hero, rods, zombies)

            if pygame.sprite.spritecollideany(hero, zombies):
                game_over = True

        screen.fill(BACKGROUND_COLOR)
        zombies.draw(screen)
        if powerup:
            screen.blit(powerup.image, powerup.rect)
        screen.blit(hero.image, hero.rect)
        for rod in rods:
            rod.draw(screen)

        draw_hud(screen, survival_time, extra_rod_timer)
        if game_over:
            draw_game_over(screen, survival_time)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()