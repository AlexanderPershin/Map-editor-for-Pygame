import pygame
import pytmx
from pytmx.util_pygame import load_pygame

import utils
from config import Config
from player import Player
from map_object import MapObject


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

        self.screen = pygame.display.set_mode(
            (self.config.window_width, self.config.window_height)
        )

        self.tmx_data = load_pygame("map/my_map.tmx")

        self.screen_width, self.screen_height = self.screen.get_size()
        self.screen_rect = self.screen.get_rect()

        pygame.display.set_caption("Map editor")
        self.clock = pygame.time.Clock()

        self._load_font()
        self._load_images()
        self._load_sounds()

        self.map_objects, self.collision_rects = self._load_map_objects()

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(*self.map_objects)

        self.player = Player(
            pygame.Vector2(
                self.config.window_width // 2,
                self.config.window_height // 2,
            ),
            300,
            self.player_animations,
            self.collision_rects,
        )
        self.all_sprites.add(self.player)

        self.running = True
        return self

    def __exit__(self, *args):
        pygame.quit()

    def _load_map_objects(
        self,
    ) -> tuple[pygame.sprite.Group, list[pygame.Rect]]:
        things = self.tmx_data.get_layer_by_name("Things")
        masks = self.tmx_data.get_layer_by_name("ObjectMasks")
        collisions = self.tmx_data.get_layer_by_name("Collisions")

        tw = self.tmx_data.tilewidth
        th = self.tmx_data.tileheight

        tiles: dict[tuple[int, int], pygame.Surface] = {}
        if things is not None:
            for x, y, gid in things:
                if gid == 0:
                    continue
                img = self.tmx_data.get_tile_image_by_gid(gid)
                if img is not None:
                    tiles[(x, y)] = img

        collision_rects: list[pygame.Rect] = []
        if collisions is not None:
            for obj in collisions:
                collision_rects.append(pygame.Rect(
                    int(obj.x), int(obj.y), int(obj.width), int(obj.height),
                ))

        map_objects = pygame.sprite.Group()
        if masks is None:
            return map_objects, collision_rects

        for mask_obj in masks:
            mask = pygame.Rect(
                int(mask_obj.x), int(mask_obj.y),
                int(mask_obj.width), int(mask_obj.height),
            )

            gx0 = mask.left // tw
            gx1 = (mask.right - 1) // tw
            gy0 = mask.top // th
            gy1 = (mask.bottom - 1) // th

            cells = [
                (gx, gy)
                for gy in range(gy0, gy1 + 1)
                for gx in range(gx0, gx1 + 1)
                if (gx, gy) in tiles
            ]
            if not cells:
                print(f"[warn] mask без тайлов: {mask}")
                continue

            min_gx = min(c[0] for c in cells)
            max_gx = max(c[0] for c in cells)
            min_gy = min(c[1] for c in cells)
            max_gy = max(c[1] for c in cells)

            w = (max_gx - min_gx + 1) * tw
            h = (max_gy - min_gy + 1) * th
            image = pygame.Surface((w, h), pygame.SRCALPHA)

            for gx, gy in cells:
                image.blit(
                    tiles[(gx, gy)],
                    ((gx - min_gx) * tw, (gy - min_gy) * th),
                )

            draw_rect = pygame.Rect(min_gx * tw, min_gy * th, w, h)

            map_objects.add(
                MapObject(image, draw_rect, depth_y=mask.bottom)
            )

        return map_objects, collision_rects


    def _load_font(self) -> None:
        self.font = pygame.font.Font(
            self.config.font_path, self.config.gui_font_size
        )

    def _load_images(self) -> None:
        self.player_animations = utils.load_animations(
            "assets/player_animations.json"
        )

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

    def draw(self):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                if layer.name == "Things":
                    continue
                for x, y, gid in layer:
                    tile_image = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile_image:
                        self.screen.blit(
                            tile_image,
                            (x * self.tmx_data.tilewidth,
                             y * self.tmx_data.tileheight),
                        )

        drawables = sorted(
            self.all_sprites,
            key=lambda s: getattr(s, "depth", s.rect.bottom),
        )
        for s in drawables:
            self.screen.blit(s.image, s.rect)

        pygame.display.flip()