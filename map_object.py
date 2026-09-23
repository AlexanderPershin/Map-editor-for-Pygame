import pygame


class MapObject(pygame.sprite.Sprite):
    def __init__(
        self,
        image: pygame.Surface,
    ) -> None:
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
