import pygame
import random

class Obstacle:
    def __init__(self, x, height, speed, obstacle_img):
        self.height = height
        self.x = x
        self.speed = speed
        self.obstacle_img = obstacle_img

        # Utiliser la taille de l'image pour le rect et la hitbox
        self.rect = self.obstacle_img.get_rect(topleft=(self.x, random.choice([self.height - 150, self.height - 250])))
        self.hitbox = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)  # Hitbox = taille de l'image

    def update(self):
        self.rect.x -= self.speed
        self.hitbox.topleft = self.rect.topleft # Mise à jour de la hitbox

    def draw(self, screen):
        screen.blit(self.obstacle_img, self.rect.topleft)

    def getSpeed(self) -> int:
        return self.speed
