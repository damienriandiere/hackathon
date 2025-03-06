import pygame
from game.game import Game

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    pygame.init()
    main()
