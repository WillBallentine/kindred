import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from random import randint

class Level:
    def __init__(self):

        #get display surface
        self.display_surface = pygame.display.get_surface()

        #sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)

        #sky
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0,10) > 7
        self.soil_layer.raining = self.raining
        self.sky = Sky()

    def setup(self):
        tmx_data = load_pygame('kindred/data/map.tmx')

        #house
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * tile_size, y* tile_size), surf, self.all_sprites, layers['house bottom'])


        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * tile_size, y* tile_size), surf, self.all_sprites)

        
        #fence
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * tile_size, y* tile_size), surf, [self.all_sprites, self.collision_sprites])

        #water
        water_frames = import_folder('kindred/graphics/water')

        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * tile_size, y* tile_size), water_frames, self.all_sprites)

        #trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites, self.tree_sprites], obj.name, self.player_add)

        #wildflowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

        #collision tiles
        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * tile_size, y* tile_size), pygame.Surface((tile_size, tile_size)), self.collision_sprites)

        # player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.tree_sprites, self.interaction_sprites, self.soil_layer)

            if obj.name == "Bed":
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)


        Generic(pos = (0,0), surf = pygame.image.load('kindred/graphics/world/ground.png').convert_alpha(), groups = self.all_sprites, z=layers['ground'])

    def player_add(self,item):
        if item == 'wood':
            self.player.item_inventory[item] +=2
        if item == 'large wood':
            self.player.item_inventory['wood'] +=4
        if item == 'apple':
            self.player.item_inventory[item] +=1
        if item == 'corn':
            self.player.item_inventory[item] +=1
        if item == 'tomato':
            self.player.item_inventory[item] +=1

    def reset(self):
        
        #plants
        self.soil_layer.update_plants()

        #soil
        self.soil_layer.remove_water()

        self.raining = randint(0,10) > 7
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()

        #apples
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

        #sky
        self.sky.start_color = [255,255,255]

    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type)
                    plant.kill()
                    Particle(plant.rect.topleft, plant.image, self.all_sprites, layers['main'])
                    self.soil_layer.grid[plant.rect.centery // tile_size][plant.rect.centerx // tile_size].remove('P')


    def run(self, dt):
        self.display_surface.fill(('black'))
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)
        self.plant_collision()

        if self.raining:
            self.rain.update()

        #daytime
        self.sky.diaply(dt)

        self.overlay.display()

        if self.player.sleep:
            self.transition.play()


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()


    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - screen_width / 2
        self.offset.y = player.rect.centery - screen_height / 2

        for layer in layers.values():
            for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)


                    #analytics
                    # if sprite == player:
                    #     pygame.draw.rect(self.display_surface, 'red', offset_rect, 5)
                    #     hitbox_rect = player.hitbox.copy()
                    #     hitbox_rect.center = offset_rect.center
                    #     pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 5)
                    #     target_pos = offset_rect.center + player_tool_offset[player.status.split('_')[0]]
                    #     pygame.draw.circle(self.display_surface, 'blue', target_pos, 5)