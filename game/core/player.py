import pygame
from game.config.settings import GRAVITY, JUMP_STRENGTH, PLAYER_FILE_PATH

class Player:
    def __init__(self, height):
        self.height = height
        self.image = pygame.image.load(PLAYER_FILE_PATH)
        self.image = pygame.transform.scale(self.image, (70, 100)).convert_alpha()
        self.rect = self.image.get_rect(topleft=(20, 20))
        self.hitbox = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)  # Hitbox du joueur
        self.vel_y = 0
        self.on_ground = False
        self.alive = True

    def jump(self):
        if self.on_ground and self.alive:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

    def update(self):
        if self.alive:
            self.vel_y += GRAVITY
            self.rect.y += self.vel_y

            # Empêche le joueur de tomber sous le sol
            if self.rect.y >= self.height - 200:
                self.rect.y = self.height - 200
                self.vel_y = 0
                self.on_ground = True

            # Mise à jour de la hitbox pour suivre le joueur
            self.hitbox.topleft = self.rect.topleft

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
