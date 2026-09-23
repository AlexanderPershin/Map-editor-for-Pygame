import math
from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping, Sequence

import pygame

import utils
from animation import Animation


class Anim(StrEnum):
    IDLE = "idle"
    WALK = "walk"
    RUN = "run"
    JUMP = "jump"
    SLASH = "slash"
    BACKSLASH = "backslash"


class Direction(StrEnum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


@dataclass(frozen=True)
class Input:
    keys: Sequence[bool]
    mouse: Sequence[bool]

    @classmethod
    def capture(cls) -> "Input":
        return cls(pygame.key.get_pressed(), pygame.mouse.get_pressed())

    @property
    def move_dir(self) -> Direction:
        if self.keys[pygame.K_d] or self.keys[pygame.K_RIGHT]:
            return Direction.RIGHT
        if self.keys[pygame.K_a] or self.keys[pygame.K_LEFT]:
            return Direction.LEFT
        if self.keys[pygame.K_s] or self.keys[pygame.K_DOWN]:
            return Direction.DOWN
        if self.keys[pygame.K_w] or self.keys[pygame.K_UP]:
            return Direction.UP
        return Direction.DOWN

    @property
    def running(self) -> bool:
        return self.keys[pygame.K_LSHIFT] or self.keys[pygame.K_RSHIFT]

    @property
    def jump(self) -> bool:
        return self.keys[pygame.K_SPACE]

    @property
    def attack(self) -> bool:
        return self.mouse[0]

    @property
    def backslash(self) -> bool:
        return self.mouse[2]


class Player(pygame.sprite.Sprite):
    FEET_OFFSET = 32
    FEET_SIZE = (24, 12)

    def __init__(
            self,
            pos: pygame.Vector2,
            speed: int,
            animations: Mapping[Anim, Animation],
            collision_rects: Sequence[pygame.Rect] = (),
            gravity: float = 2000.0,
            jump_height: float = 120.0,
            collision_size: tuple[int, int] = FEET_SIZE,
    ) -> None:
        super().__init__()
        self.animations = animations
        self.current_anim = Anim.IDLE
        self.speed = speed
        self.pos = pygame.Vector2(pos)

        self.gravity = gravity
        self.jump_height = jump_height

        self.air_height = 0.0
        self.air_vel = 0.0
        self.airborne = False

        self.collision_rects = list(collision_rects)
        self.collision_size = collision_size

        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt: float, *args, **kwargs) -> None:
        inp = Input.capture()
        move = utils.get_movement_direction(inp.keys)

        self._move(move, inp, dt)
        self._physics(inp, dt)
        self._animate(move, inp, dt)

    def _move(self, move: pygame.Vector2, inp: Input, dt: float) -> None:
        speed = self.speed * 2 if inp.running else self.speed

        self.pos.x += move.x * speed * dt
        self._resolve_collisions("x")

        self.pos.y += move.y * speed * dt
        self._resolve_collisions("y")

    def _collision_rect(self) -> pygame.Rect:
        w, h = self.collision_size
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (round(self.pos.x), round(self.pos.y) + self.FEET_OFFSET)
        return rect

    def _resolve_collisions(self, axis: str) -> None:
        offset = pygame.Vector2(0, self.FEET_OFFSET)
        rect = self._collision_rect()
        for wall in self.collision_rects:
            if not rect.colliderect(wall):
                continue
            feet = pygame.Vector2(self.pos.x, self.pos.y) + offset
            if axis == "x":
                if feet.x < wall.centerx:
                    rect.right = wall.left
                else:
                    rect.left = wall.right
                self.pos.x = rect.centerx
            else:
                if feet.y < wall.centery:
                    rect.bottom = wall.top
                else:
                    rect.top = wall.bottom
                self.pos.y = rect.centery - offset.y

    def _physics(self, inp: Input, dt: float) -> None:
        if inp.jump and not self.airborne:
            self.air_vel = math.sqrt(2.0 * self.gravity * self.jump_height)
            self.airborne = True

        if self.airborne:
            self.air_vel -= self.gravity * dt
            self.air_height += self.air_vel * dt
            if self.air_height <= 0.0:
                self.air_height = 0.0
                self.air_vel = 0.0
                self.airborne = False

    @property
    def depth(self) -> int:
        return int(self.pos.y + self.FEET_OFFSET)

    def _animate(self, move: pygame.Vector2, inp: Input, dt: float) -> None:
        moving = move.length_squared() > 0

        self._play(self._pick_anim(moving, inp))
        if moving:
            self.animations[self.current_anim].set_direction(inp.move_dir.value)

        frame = self.animations[self.current_anim].update(dt)
        if frame is not None:
            self.image = frame
            self.rect = self.image.get_rect(
                center=(self.pos.x, self.pos.y - self.air_height)
            )
            self.mask = pygame.mask.from_surface(self.image)

    def _pick_anim(self, moving: bool, inp: Input) -> Anim:
        if self.airborne:
            return Anim.JUMP
        if inp.backslash:
            return Anim.BACKSLASH
        if inp.attack:
            return Anim.SLASH
        if moving:
            return Anim.RUN if inp.running else Anim.WALK
        return Anim.IDLE

    def _play(self, anim: Anim) -> None:
        if anim != self.current_anim:
            self.animations[anim].reset()
            self.current_anim = anim