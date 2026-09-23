import pygame


class MapObject(pygame.sprite.Sprite):
    def __init__(
        self,
        image: pygame.Surface,
        draw_rect: pygame.Rect,
        depth_y: int,
    ) -> None:
        super().__init__()
        self.image = image
        self.rect = draw_rect
        self.depth_y = depth_y

    @property
    def depth(self) -> int:
        return self.depth_y