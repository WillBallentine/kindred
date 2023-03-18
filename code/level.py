import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic
from pytmx.util_pygame import load_pygame

class Level:
    def __init__(self):

        #get display surface
        self.display_surface = pygame.display.get_surface()

        #sprite groups
        self.all_sprites = CameraGroup()

        self.setup()
        self.overlay = Overlay(self.player)

    def setup(self):
        Generic(pos = (0,0), surf = pygame.image.load('kindred/graphics/world/ground.png').convert_alpha(), group = self.all_sprites, z=layers['ground'])
        self.player = Player((640,360), self.all_sprites)

    def run(self, dt):
        self.display_surface.fill(('black'))
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)

        self.overlay.display()


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()


    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - screen_width / 2
        self.offset.y = player.rect.centery - screen_height / 2

        for layer in layers.values():
            for sprite in self.sprites():
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)