import pygame
from settings import *

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, group, z = layers['main']):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z