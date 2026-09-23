import pygame

import utils
from config import Config
from player import Player


class Game:
    def __init__(self, config: Config):
        self.running = False
        self.config = config

    def __enter__(self):
        pygame.mixer.pre_init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=512,
            allowedchanges=pygame.AUDIO_ALLOW_ANY_CHANGE,
        )

        pygame.init()

        pygame.mixer.set_num_channels(16)

        self.screen = pygame.display.set_mode((self.config.window_width, self.config.window_height))

        self.screen_width, self.screen_height = self.screen.get_size()
        self.screen_rect = self.screen.get_rect()

        pygame.display.set_caption("Character Generator")

        self.clock = pygame.time.Clock()

        self._load_font()
        self._load_images()
        self._load_sounds()

        self.all_sprites = pygame.sprite.LayeredUpdates()

        self.player = Player(
            pygame.Vector2(
                self.config.window_width // 2, self.config.window_height // 2
            ),
            300,
            self.player_animations,
        )
        self.all_sprites.add(self.player)

        self.running = True

        return self

    def __exit__(self, *args):
        pygame.quit()

    def _load_font(self) -> None:
        self.font = pygame.font.Font(
            self.config.font_path, self.config.gui_font_size
        )

    def _load_images(self) -> None:
        self.player_animations = utils.load_animations("assets/player_animations.json")

    def _load_sounds(self) -> None:
        pass

    def run(self):
        while self.running:
            self.dt = self.clock.tick(self.config.fps) / 1000
            self.watch_for_events()
            self.update()
            self.draw()

    def watch_for_events(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                case pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

    def update(self):
        self.all_sprites.update(self.dt, target=self.player)

        for s in self.all_sprites:
            self.all_sprites.change_layer(s, s.rect.centery)

    def draw(self):
        self.screen.fill(self.config.bg_color)

        self.all_sprites.draw(self.screen)

        pygame.display.flip()
