import pygame
import pygame_gui

class Button:
    def __init__(self, screen, x, y, width, height, text, manager):
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.manager = manager
        self.button = pygame_gui.elements.UIButton(
            relative_rect=self.rect,
            text=text,
            manager=manager
        )
    
    def draw(self):
        # Pas besoin de `blit` ni de `draw`, pygame_gui gère tout cela pour vous.
        # Vous devez mettre à jour et dessiner l'interface.
        self.manager.update(pygame.time.get_ticks())  # Mise à jour de l'interface
        self.manager.draw_ui(self.screen)  # Dessiner l'UI complète
