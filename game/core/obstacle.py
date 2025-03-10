"""
Obstacle Module

This module defines the Obstacle class for a game, managing the obstacle's attributes,
movements, and interactions within the game environment. The Obstacle class handles
loading the obstacle's image, positioning it randomly on the screen, and updating its
position based on a specified speed. It also includes methods for drawing the obstacle
on the screen and managing its collision detection with other game elements.

Classes:
    Obstacle: Represents an obstacle in the game.

Dependencies:
    pygame: A library used for creating games and multimedia applications in Python.
    random: A module used to generate random numbers for positioning obstacles.
"""

import random
import pygame

class Obstacle(pygame.sprite.Sprite):
    """
    Class representing an obstacle in the game.

    Attributes:
        __height (int): The height of the game screen.
        __x (int): The x-coordinate of the obstacle.
        __speed (int): The speed at which the obstacle moves.
        __obstacle_img (pygame.Surface): The image of the obstacle.
        __rect (pygame.Rect): The rectangle representing the obstacle's position and size.
        __hitbox (pygame.Rect): The hitbox for collision detection.
    """

    def __init__(self, x: int, height: int, speed: int, obstacle_img: pygame.Surface) -> None:
        """
        Initializes the obstacle with the given parameters.

        Args:
            x (int): The initial x-coordinate of the obstacle.
            height (int): The height of the game screen.
            speed (int): The speed at which the obstacle moves.
            obstacle_img (pygame.Surface): The image of the obstacle.
        """
        super().__init__()
        self.__height = height
        self.__speed = speed
        self.__obstacle_img = obstacle_img

        # Use the image size for the rect and hitbox
        y_position = random.choice([self.__height - 150, self.__height - 250])
        self.__rect = self.__obstacle_img.get_rect(topleft=(x, y_position))

        # Smaller hitbox for better collision detection
        self.__hitbox = self.__rect.inflate(-10, -10)

    def update(self) -> None:
        """
        Updates the obstacle's position based on its speed.
        """
        self.__rect.x -= self.__speed
        self.__hitbox.topleft = self.__rect.topleft  # Update the hitbox
        if self.__rect.right < 0:
            self.kill()

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draws the obstacle on the screen.

        Args:
            screen (pygame.Surface): The game screen to draw on.
        """
        screen.blit(self.__obstacle_img, self.__rect.topleft)

    def get_hitbox(self) -> pygame.Rect:
        """
        Gets the obstacle's hitbox.

        Returns:
            pygame.Rect: The obstacle's hitbox.
        """
        return self.__hitbox

    def get_rect(self) -> pygame.Rect:
        """
        Gets the obstacle's rectangle.

        Returns:
            pygame.Rect: The obstacle's rectangle.
        """
        return self.__rect
