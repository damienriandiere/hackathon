"""
Menu Module

This module defines the Menu class for a game, which manages the main menu interface
using the pygame and pygame_gui libraries. The Menu class handles the creation, updating,
and drawing of the menu screen, including buttons for starting the game and quitting.
It utilizes pygame_gui for handling the UI elements and provides a user-friendly interface
for interacting with the game.

Classes:
    Menu: Represents the main menu of the game.
"""

import sys
import pygame
import pygame_gui
from game.utils.helpers import draw_text

class Menu:
    """
    A class representing the main menu of the game.

    Attributes:
        __screen (pygame.Surface): The screen to draw the menu on.
        __width (int): The width of the screen.
        __height (int): The height of the screen.
        __manager (pygame_gui.UIManager): The UI manager handling the menu.
        __font_filepath (str): The file path to the font used in the menu.
        __start_button (pygame_gui.elements.UIButton): The start game button.
        __quit_button (pygame_gui.elements.UIButton): The quit game button.
    """

    def __init__(self, screen : pygame.Surface, width : int, height : int,
                 manager : pygame_gui.UIManager, font_filepath : str) -> None:
        """
        Initializes the Menu with the given parameters.

        Args:
            screen (pygame.Surface): The screen to draw the menu on.
            width (int): The width of the screen.
            height (int): The height of the screen.
            manager (pygame_gui.UIManager): The UI manager handling the menu.
            font_filepath (str): The file path to the font used in the menu.
        """
        self.__screen = screen
        self.__width = width
        self.__height = height
        self.__manager = manager
        self.__font_filepath = font_filepath
        self.__start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.__width // 2 - 200, 5 * (self.__height // 6), 100, 50),
            text="Start Game",
            manager=self.__manager
        )
        self.__quit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.__width // 2 + 100, 5 * (self.__height // 6), 100, 50),
            text="Quit",
            manager=self.__manager
        )

    def show(self, background_img : pygame.Surface, font : pygame.font.Font) -> None:
        """
        Displays the menu on the screen and handles user interactions.

        Args:
            background_img (pygame.Surface): The background image of the menu.
            font (pygame.font.Font): The font used for drawing text.
        """
        self.__screen.blit(background_img, (0, 0))
        running = True
        while running:
            draw_text(self.__screen, "Emotion Race", font, (255, 255, 255),
                      self.__width // 4, self.__height // 15)
            draw_text(self.__screen, (
                "Dans Emotion Race, tu incarnes un ninja légendaire, pris dans une course\n\n"
                "effrénée contre ses propres émotions. Chaque mouvement, chaque action est\n\n"
                "influencé par ton état émotionnel. Si tu laisses le stress t'envahir, ton\n\n"
                "personnage sautera moins haut, et les obstacles deviendront de plus en plus\n\n"
                "nombreux, rendant la course encore plus difficile. La peur, la colère,\n\n"
                "le doute... chaque émotion incontrôlée te ralentit, te rend plus\n\n"
                "vulnérable. Mais si tu parviens à maîtriser tes émotions, tu retrouveras\n\n"
                "ton calme et tu pourras surmonter les défis qui se dressent devant toi.\n\n"
                "Reste calme, surpasse-toi, et gagne la course de ton destin!"
            ), pygame.font.Font(self.__font_filepath, 24), (255, 255, 255),
            self.__width // 7, self.__height // 4)

            for event in pygame.event.get():
                self.__manager.process_events(event)

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.__start_button:
                        running = False  # Go to the game
                    if event.ui_element == self.__quit_button:
                        sys.exit()

            self.__manager.update(1 / 60)
            self.__manager.draw_ui(self.__screen)
            pygame.display.flip()
