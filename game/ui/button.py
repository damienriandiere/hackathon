"""
Button Module

This module defines the Button class, which represents a UI button in a game using
the pygame and pygame_gui libraries. The Button class manages the creation, updating,
and drawing of a button on the screen. It utilizes pygame_gui for handling the UI
elements, making it easier to integrate buttons into a pygame application.

Classes:
    Button: Represents a UI button in the game.
"""

import pygame
import pygame_gui

class Button:
    """
    A class representing a UI button in the game.

    Attributes:
        __screen (pygame.Surface): The screen to draw the button on.
        __rect (pygame.Rect): The rectangle representing the button's position and size.
        __text (str): The text displayed on the button.
        __manager (pygame_gui.UIManager): The UI manager handling the button.
        __button (pygame_gui.elements.UIButton): The UI button element.
    """

    def __init__(self, screen : pygame.Surface, x : int, y : int, width : int,
                 height : int, text : str, manager : pygame_gui.UIManager) -> None:
        """
        Initializes the Button with the given parameters.

        Args:
            screen (pygame.Surface): The screen to draw the button on.
            x (int): The x-coordinate of the button's position.
            y (int): The y-coordinate of the button's position.
            width (int): The width of the button.
            height (int): The height of the button.
            text (str): The text displayed on the button.
            manager (pygame_gui.UIManager): The UI manager handling the button.
        """
        self.__screen = screen
        self.__rect = pygame.Rect(x, y, width, height)
        self.__text = text
        self.__manager = manager
        self.__button = pygame_gui.elements.UIButton(
            relative_rect=self.__rect,
            text=self.__text,
            manager=self.__manager
        )

    def draw(self) -> None:
        """
        Updates and draws the button on the screen.

        This method updates the UI manager and draws the entire UI, including the button.
        """
        self.__manager.update(pygame.time.get_ticks())  # Update the UI
        self.__manager.draw_ui(self.__screen)  # Draw the entire UI

    def get_button(self) -> pygame_gui.elements.UIButton:
        """
        Gets the UI button element.

        Returns:
            pygame_gui.elements.UIButton: The UI button element.
        """
        return self.__button
