import pygame

# Constantes pour les couleurs
BLACK = (0, 0, 0)

def draw_text(screen, text, font, color, x, y, outline_width=2):
    """Draw text on the screen with a black outline."""
    # Créer le texte principal (couleur normale)
    text_surface = font.render(text, True, color)

    # Créer le contour du texte (noir)
    outline_surface = font.render(text, True, BLACK)

    # Dessiner le contour du texte en déplaçant légèrement dans toutes les directions
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            # Ne pas dessiner sur la position centrale
            if dx != 0 or dy != 0:
                screen.blit(outline_surface, (x + dx, y + dy))

    # Dessiner le texte principal au centre
    screen.blit(text_surface, (x, y))

def load_image(image_path, width=0, height=0):
    """Load and scale an image."""
    try:
        image = pygame.image.load(image_path)
    except pygame.error as e:
        print(f"Erreur lors du chargement de l'image {image_path}: {e}")
        return None

    if width != 0 and height != 0:
        size = (width, height)
    elif width != 0:
        size = (width, image.get_height())
    elif height != 0:
        size = (image.get_width(), height)
    else:
        size = image.get_size()

    return pygame.transform.scale(image, size)

def play_music(music_path):
    """Start background music."""
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1, 0.0)
    except pygame.error as e:
        print(f"Erreur lors du chargement de la musique {music_path}: {e}")
