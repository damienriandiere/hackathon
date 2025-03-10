"""
utils.py

This module provides utility functions for the Emotion Race game, including:

- `draw_text`: Draws text on the screen with an outline.
- `load_image`: Loads and resizes images.
- `play_music`: Plays background music in a loop.

Dependencies:
    - pygame: Used for rendering text, loading images, and handling audio.

Usage Example:
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    draw_text(screen, "Hello, World!", font, (255, 255, 255), 100, 100)

    image = load_image("assets/images/player.png", 50, 50)
    if image:
        screen.blit(image, (200, 200))

    play_music("assets/sounds/sound.mp3")

Author: [Damien RIANDIERE]
"""
import pygame

def draw_text(screen: pygame.Surface, text: str, font: pygame.font.Font,
              color: tuple, x: int, y: int, outline_width: int = 2) -> None:
    """
    Draws text on the screen with an outline.

    Args:
        screen (pygame.Surface): The screen to draw on.
        text (str): The text to draw.
        font (pygame.font.Font): The font to use for the text.
        color (tuple): The color of the text (RGB).
        x (int): The x-coordinate of the text's position.
        y (int): The y-coordinate of the text's position.
        outline_width (int): The width of the text outline.
    """
    text_surface = font.render(text, True, color)
    outline_surface = font.render(text, True, (0, 0, 0))  # Black outline

    offsets = [(-outline_width, 0), (outline_width, 0), (0, -outline_width), (0, outline_width)]

    # Draw only in 4 directions (left, right, top, bottom) for efficiency
    for dx, dy in offsets:
        screen.blit(outline_surface, (x + dx, y + dy))

    screen.blit(text_surface, (x, y))  # Main text

def load_image(image_path: str, width: int = 0, height: int = 0) -> pygame.Surface:
    """
    Loads an image from a file and optionally resizes it.

    Args:
        image_path (str): The path to the image file.
        width (int): The desired width of the image (optional).
        height (int): The desired height of the image (optional).

    Returns:
        pygame.Surface: The loaded and resized image, or None if failed.
    """
    try:
        image = pygame.image.load(image_path)
    except (OSError, pygame.error) as e:
        print(f"Erreur lors du chargement de l'image {image_path}: {e}")
        return None

    # Determine the new size
    new_width = width if width else image.get_width()
    new_height = height if height else image.get_height()

    return pygame.transform.scale(image, (new_width, new_height))

def play_music(music_path: str) -> None:
    """
    Plays background music in a loop.

    Args:
        music_path (str): The path to the music file.
    """
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1, 0.0)
    except (OSError, pygame.error) as e:
        print(f"Erreur lors du chargement de la musique {music_path}: {e}")
