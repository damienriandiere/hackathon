import pygame
import pygame_gui
from game.utils.helpers import draw_text
from game.config.settings import WHITE, FONT_FILE_PATH

class Menu:
    def __init__(self, screen, width, height, manager):
        self.screen = screen
        self.WIDTH = width
        self.HEIGHT = height
        self.manager = manager
        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.WIDTH // 2 - 200, 4 * (self.HEIGHT // 5), 100, 50),
            text="Start Game",
            manager=self.manager
        )
        self.quit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.WIDTH // 2 + 100, 4 * (self.HEIGHT // 5), 100, 50),
            text="Quit",
            manager=self.manager
        )

    def show(self, background_img, font):
        self.screen.blit(background_img, (0, 0))
        running = True
        while running:
            draw_text(self.screen, "Emotion Race", font, WHITE, self.WIDTH // 4, self.HEIGHT // 15)
            draw_text(self.screen, "\nDans Emotion Race, tu incarnes un ninja légendaire, pris dans une course effrénée contre \n\n"
                      "ses propres émotions. Chaque mouvement, chaque action est influencé par ton état émotionnel.\n\n"
                      " Si tu laisses le stress t'envahir, ton personnage sautera moins haut, et les obstacles \n\n"
                      "deviendront de plus en plus nombreux, rendant la course encore plus difficile. La peur, \n\n"
                      "la colère, le doute... chaque émotion incontrôlée te ralentit, te rend plus vulnérable. Mais \n\n"
                      "si tu parviens à maîtriser tes émotions, tu retrouveras ton calme et tu pourras surmonter \n\n"
                      "les défis qui se dressent devant toi. Reste calme, surpasse-toi, et gagne la course de ton destin !",
                        pygame.font.Font(FONT_FILE_PATH, 24), WHITE, self.WIDTH // 12, self.HEIGHT // 4)
            for event in pygame.event.get():
                self.manager.process_events(event)

                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.start_button:
                        running = False  # Go to the game
                    if event.ui_element == self.quit_button:
                        pygame.quit()
                        exit()

            self.manager.update(1 / 60)
            self.manager.draw_ui(self.screen)
            pygame.display.flip()
