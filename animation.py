import pygame


class Animation:
    def __init__(
            self,
            frames: dict[str, list[pygame.Surface]] | list[pygame.Surface],
            frame_duration_ms: int,
            loop: bool = True,
    ):
        self.frames = frames
        self.frame_duration = frame_duration_ms / 1000.0
        self.loop = loop

        self.current_frame = 0
        self.timer = 0.0
        self.finished = False
        self.direction = "down"

    def set_direction(self, direction: str) -> None:
        if direction != self.direction:
            self.direction = direction
            self.current_frame = 0
            self.timer = 0.0

    def _get_frames(self) -> list[pygame.Surface]:
        if isinstance(self.frames, dict):
            return self.frames.get(self.direction, [])
        return self.frames

    def update(self, dt: float) -> pygame.Surface | None:
        frames = self._get_frames()
        if not frames:
            return None

        if self.finished:
            return frames[-1]

        self.timer += dt
        if self.timer >= self.frame_duration:
            self.timer = 0.0
            self.current_frame += 1
            if self.current_frame >= len(frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(frames) - 1
                    self.finished = True
        return frames[self.current_frame]

    def reset(self) -> None:
        self.current_frame = 0
        self.timer = 0.0
        self.finished = False