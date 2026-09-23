import json
from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path

import pygame

from animation import Animation


def get_movement_direction(keys: Sequence[bool]) -> pygame.Vector2:
    move = pygame.Vector2()

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        move.y -= 1
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        move.y += 1
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        move.x -= 1
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        move.x += 1

    if move.length_squared() > 0:
        move.normalize_ip()

    return move


DEFAULT_DIRECTIONS = ("up", "left", "down", "right")


def load_sprite_frames(
        sprite_sheet: pygame.Surface,
        frame_width: int,
        frame_height: int,
        *,
        frame_count: int | None = None,
        rows: int = 1,
        row_names=None,
        scale: int = 1,
        origin: tuple[int, int] = (0, 0),
) -> dict[str, list[pygame.Surface]]:
    sheet_w, sheet_h = sprite_sheet.get_size()
    origin_x, origin_y = origin

    if frame_count is None:
        frame_count = (sheet_w - origin_x) // frame_width

    if row_names is None:
        row_names = DEFAULT_DIRECTIONS[:rows]

    row_names = list(row_names)
    if len(row_names) != rows:
        raise ValueError("Incorrect row names")

    needed_w = origin_x + frame_count * frame_width
    needed_h = origin_y + rows * frame_height

    if sheet_w < needed_w or sheet_h < needed_h:
        raise ValueError("Incorrect source sprite size")

    out_width, out_height = frame_width * scale, frame_height * scale
    result: dict[str, list[pygame.Surface]] = {}

    for row_index, name in enumerate(row_names):
        row_frames = []

        for col_index in range(frame_count):
            rect = pygame.Rect(
                origin_x + col_index * frame_width,
                origin_y + row_index * frame_height,
                frame_width,
                frame_height,
            )
            frame = sprite_sheet.subsurface(rect)
            row_frames.append(pygame.transform.scale(frame, (out_width, out_height)))

        result[name] = row_frames

    return result


@lru_cache(maxsize=None)
def load_sheet(path: str) -> pygame.Surface:
    return pygame.image.load(path).convert_alpha()


def load_animations(manifest_path: str) -> dict[str, Animation]:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))

    animations = {}
    for name, meta in manifest.items():
        sheet = load_sheet(meta["file"])
        frames = load_sprite_frames(
            sheet,
            meta["frame_width"],
            meta["frame_height"],
            frame_count=meta["frame_count"],
            rows=meta["rows"],
        )
        animations[name] = Animation(frames, meta["frame_duration"])

    return animations
