"""
Main Game Module

This module serves as the entry point for the game application. It initializes the game
using a configuration file and starts the game loop. The `Game` class from the `game`
module is responsible for managing the game's state and behavior.

Functions:
    main: Initializes and runs the game.
"""

from game.game import Game

def main() -> None:
    """
    Initializes and runs the game.

    This function creates an instance of the Game class with a specified configuration
    file and starts the game loop by calling the run method.
    """
    game = Game('./game/config/config.json')
    game.run()

if __name__ == '__main__':
    main()
