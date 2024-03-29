import pygame
from settings import *
from timer import Timer

class Menu:
    def __init__(self, player, toggle_menu):
        
        #general setup
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('kindred/font/LycheeSoda.ttf', 30)

        #options
        self.width = 400
        self.space = 10
        self.padding = 8

        #entires
        self.options = list(self.player.item_inventory.keys()) + list(self.player.seed_inventory.keys())
        self.sell_border = len(self.player.item_inventory.keys()) - 1
        self.setup()

        #movement
        self.index = 0
        self.timer = Timer(200)

    def display_money(self):
        text_surf = self.font.render(f"Riches: ${self.player.money}", False, 'Black')
        text_rect = text_surf.get_rect(midbottom = (screen_width / 2, self.menu_top - 20))

        pygame.draw.rect(self.display_surface, 'White', text_rect.inflate(10, 10), 0, 4)
        self.display_surface.blit(text_surf, text_rect)

    def setup(self):
        self.text_surfs = []
        self.total_height = 0

        for item in self.options:
            text_surf = self.font.render(item, False, 'Black')
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)

        self.total_height += (len(self.text_surfs) - 1) * self.space
        self.menu_top = screen_height / 2 - self.total_height / 2
        self.main_rect = pygame.Rect(screen_width / 2 - self.width / 2, self.menu_top, self.width, self.total_height)

        self.buy_text = self.font.render('Buy', False, 'Black')
        self.sell_text = self.font.render('Sell', False, 'Black')


    def input(self):
        keys = pygame.key.get_pressed()
        self.timer.update()

        if keys[pygame.K_ESCAPE]:
            self.toggle_menu()

        if not self.timer.active:
            if keys[pygame.K_UP]:
                self.index -= 1
                self.timer.activate()

            if keys[pygame.K_DOWN]:
                self.index += 1
                self.timer.activate()

            if keys[pygame.K_SPACE]:
                self.timer.activate()

                current_item = self.options[self.index]

                if self.index <= self.sell_border:
                    if self.player.item_inventory[current_item] > 0:
                        self.player.item_inventory[current_item] -= 1
                        self.player.money += sale_prices[current_item]

                else:
                    seed_price = purchae_prices[current_item]
                    if self.player.money >= seed_price:
                        self.player.money -= seed_price
                        self.player.seed_inventory[current_item] += 1


        if self.index < 0:
            self.index = len(self.options) - 1

        if self.index > len(self.options) - 1:
            self.index = 0

    def show_entry(self, text_surf, amount, top, selected):
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height() + (self.padding * 2))
        pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 4)

        text_rect = text_surf.get_rect(midleft = (self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)

        amount_surf = self.font.render(str(amount), False, 'Black')
        amount_rect = amount_surf.get_rect(midright = (self.main_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)

        if selected:
            pygame.draw.rect(self.display_surface, 'Black', bg_rect, 4, 4)
            if self.index <= self.sell_border:
                self.display_surface.blit(self.sell_text, (self.main_rect.right - 100 - self.sell_text.get_width(), bg_rect.centery - 15))
            else:
                self.display_surface.blit(self.buy_text, (self.main_rect.right - 100 - self.buy_text.get_width(), bg_rect.centery - 15))


    def update(self):
        self.input()
        self.display_money()
        for text_index, text_surf in enumerate(self.text_surfs):
            top = self.main_rect.top + (text_index * (text_surf.get_height() + (self.padding * 2) + self.space))
            amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values())
            amount = amount_list[text_index]
            self.show_entry(text_surf, amount, top, self.index == text_index)
