"""
Player Module

This module defines the Player class for a game, managing the player's attributes,
movements, and interactions within the game environment. The Player class handles
loading the player's image, scaling it, and updating the player's position based on
physics such as gravity and jumping mechanics. It also includes methods for drawing
the player on the screen and managing the player's state, such as whether the player
is alive or not.

Classes:
    Player: Represents the player character in the game.

Dependencies:
    pygame: A library used for creating games and multimedia applications in Python.
"""

import pygame

class Player:
    """
    Class representing the player in the game.

    Attributes:
        __height (int): The height of the game screen.
        __image (pygame.Surface): The player's image.
        __rect (pygame.Rect): The player's collision rectangle.
        __hitbox (pygame.Rect): The player's hitbox for collisions.
        __vel_y (int): The player's vertical velocity.
        __on_ground (bool): Indicates if the player is on the ground.
        __alive (bool): Indicates if the player is alive.
    """

    def __init__(self, height: int, player_file_path: str) -> None:
        """
        Initializes the player with the given parameters.

        Args:
            height (int): The height of the game screen.
            player_file_path (str): The path to the player's image file.
        """
        self.__height = height
        self.__image = pygame.transform.scale(pygame.image.load(player_file_path).convert_alpha(),
                                              (70, 100))
        self.__rect = self.__image.get_rect(topleft=(20, 20))
        # Smaller hitbox for better collision detection
        self.__hitbox = self.__rect.inflate(-10, -10)
        self.__vel_y = 0
        self.__on_ground = False
        self.__alive = True

    def jump(self, jump_strength: int) -> None:
        """
        Makes the player jump if they are on the ground and alive.

        Args:
            jump_strength (int): The strength of the jump.
        """
        if self.__on_ground and self.__alive:
            self.__vel_y = jump_strength
            self.__on_ground = False

    def update(self, gravity: int) -> None:
        """
        Updates the player's position based on gravity and velocity.

        Args:
            gravity (int): The gravity affecting the player.
        """
        if self.__alive:
            self.__vel_y += gravity
            self.__rect.y += self.__vel_y

            # Prevent the player from falling below the ground
            if self.__rect.y >= self.__height - 200:
                self.__rect.y = self.__height - 200
                self.__vel_y = 0
                self.__on_ground = True

            # Update the hitbox to follow the player
            self.__hitbox.topleft = self.__rect.topleft

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draws the player on the screen.

        Args:
            screen (pygame.Surface): The game screen to draw on.
        """
        screen.blit(self.__image, self.__rect.topleft)

    def is_alive(self) -> bool:
        """
        Checks if the player is alive.

        Returns:
            bool: True if the player is alive, False otherwise.
        """
        return self.__alive

    def set_is_alive(self, alive: bool) -> None:
        """
        Sets the player's alive status.

        Args:
            alive (bool): The new alive status.
        """
        self.__alive = alive

    def get_hitbox(self) -> pygame.Rect:
        """
        Gets the player's hitbox.

        Returns:
            pygame.Rect: The player's hitbox.
        """
        return self.__hitbox
