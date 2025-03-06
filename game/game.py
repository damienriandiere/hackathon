import pygame
import pygame_gui
from .utils.helpers import load_image, draw_text
from .ui.menu import Menu
from .ui.button import Button
from .config.settings import PAUSED, NB_OBSTACLES, SONG_FILE_PATH, GAMEOVER_FILE_PATH, LEADERBOARD_FILE_PATH, FONT_FILE_PATH, PLAYER_SPEED_AT_BEGINNING, BACKGROUND_FILE_PATH, FOREGROUND_FILE_PATH, OBSTACLE_FILE_PATH, LOGOUT_FILE_PATH, BACKGROUND_SPEED, FOREGROUND_SPEED, BLACK, WHITE
from .core.player import Player
from .core.obstacle import Obstacle
import json
from datetime import datetime

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.WIDTH, self.HEIGHT = self.screen.get_size()

        # Initialisation de pygame_gui
        self.manager = pygame_gui.UIManager((self.WIDTH, self.HEIGHT))
        self.manager.add_font_paths("cybrpnuk", FONT_FILE_PATH)

        # Images
        self.logout_img = load_image(LOGOUT_FILE_PATH, 40, 40)
        self.logout_rect = self.logout_img.get_rect(topright=(self.WIDTH - 10, 10))

        # Fonts
        self.font = pygame.font.Font(FONT_FILE_PATH, 16)

        pygame.display.set_caption("Emotion Race")

        # Background and foreground
        self.obstacle_img = load_image(OBSTACLE_FILE_PATH, 40, 40)  # Image 40x40
        self.background_img = load_image(BACKGROUND_FILE_PATH, self.WIDTH, self.HEIGHT)
        self.foreground_img = load_image(FOREGROUND_FILE_PATH, self.WIDTH + 6)
        self.game_over_img = load_image(GAMEOVER_FILE_PATH, self.WIDTH, self.HEIGHT)

        # Game variables
        self.score = 0
        self.speed = PLAYER_SPEED_AT_BEGINNING
        self.player = Player(self.HEIGHT)
        self.nb_obstacles = NB_OBSTACLES
        self.min_spacing = 200  # Distance minimale entre les obstacles
        self.max_spacing = 500  # Distance maximale entre les obstacles
        self.spacing = self.min_spacing + (self.max_spacing - self.min_spacing) * (self.speed / 50)  # Ajustement progressif

        self.obstacles = [
            Obstacle((self.WIDTH + i * self.spacing), self.HEIGHT, self.speed, self.obstacle_img) for i in range(self.nb_obstacles)
        ]

        self.background_x1 = 0
        self.background_x2 = self.WIDTH
        self.foreground_x1 = 0
        self.foreground_x2 = self.WIDTH
        self.time_since_last_toggle = 0
        self.text_visible = True

    def run(self, restart=False):
        self.start_music()
        if not restart:
            self.show_start_screen()

        running = True
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame_gui.UI_BUTTON_PRESSED])
        clock = pygame.time.Clock()

        while running:
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not PAUSED:
                        self.player.jump()
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
                    if event.key == pygame.K_p:
                        self.toggle_pause()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.logout_rect.collidepoint(event.pos):
                        pygame.quit()
                        exit()

            # Mise à jour du jeu uniquement si non en pause
            if not PAUSED:
                self.player.update()
                if self.player.alive:
                    self.score += 1
                    self.speed = PLAYER_SPEED_AT_BEGINNING + self.score // 100
                    self.nb_obstacles = max(NB_OBSTACLES + self.score // 100, 10)

                # Déplacement du décor
                self.background_x1 -= BACKGROUND_SPEED
                self.background_x2 -= BACKGROUND_SPEED
                self.foreground_x1 -= FOREGROUND_SPEED
                self.foreground_x2 -= FOREGROUND_SPEED

                if self.background_x1 <= -self.WIDTH:
                    self.background_x1 = self.WIDTH
                if self.background_x2 <= -self.WIDTH:
                    self.background_x2 = self.WIDTH
                if self.foreground_x1 <= -self.WIDTH:
                    self.foreground_x1 = self.WIDTH
                if self.foreground_x2 <= -self.WIDTH:
                    self.foreground_x2 = self.WIDTH

                # Mise à jour des obstacles
                self.obstacles = [obstacle for obstacle in self.obstacles if obstacle.rect.x >= -40]

                for obstacle in self.obstacles:
                    obstacle.update()
                    if self.player.hitbox.colliderect(obstacle.hitbox):
                        self.player.alive = False
                        self.game_over()

                if len(self.obstacles) == 0:
                    normalized_speed = min(self.speed, 20)  # Empêche des valeurs absurdes
                    self.spacing = self.min_spacing + (self.max_spacing - self.min_spacing) * (normalized_speed / 20)
                    self.nb_obstacles = max(NB_OBSTACLES + self.score // 100, 10)

                    new_obstacles = [
                        Obstacle(self.WIDTH + i * self.spacing, self.HEIGHT, self.speed, self.obstacle_img)
                        for i in range(self.nb_obstacles)
                    ]
                    self.obstacles = new_obstacles

            # Dessin des éléments
            self.screen.blit(self.background_img, (self.background_x1, 0))
            self.screen.blit(self.background_img, (self.background_x2, 0))
            self.screen.blit(self.foreground_img, (self.foreground_x1, self.HEIGHT - 110))
            self.screen.blit(self.foreground_img, (self.foreground_x2, self.HEIGHT - 110))
            self.screen.blit(self.logout_img, self.logout_rect.topleft)

            draw_text(self.screen, f"Score : {self.score}", self.font, WHITE, 60, 10)
            draw_text(self.screen, f"Vitesse : {self.speed}", self.font, WHITE, 60, 40)

            self.player.draw(self.screen)

            for obstacle in self.obstacles:
                obstacle.draw(self.screen)

            if PAUSED:
                self.time_since_last_toggle += 1
                if self.time_since_last_toggle >= 1000:
                    self.time_since_last_toggle = 0
                    self.text_visible = not self.text_visible

                if self.text_visible:
                    draw_text(self.screen, "Pause - Appuyez sur P pour reprendre", self.font, WHITE, self.WIDTH // 3, self.HEIGHT // 2)

            pygame.display.flip()
            clock.tick(60)

    def start_music(self):
        pygame.mixer.music.load(SONG_FILE_PATH)
        pygame.mixer.music.play(-1, 0.0)

    def show_start_screen(self):
        main_menu = Menu(self.screen, self.WIDTH, self.HEIGHT, self.manager)
        main_menu.show(self.background_img, pygame.font.Font(FONT_FILE_PATH, 110))

    def toggle_pause(self):
        global PAUSED
        PAUSED = not PAUSED

    def game_over(self):
        self.manager.clear_and_reset()
        self.screen.blit(self.game_over_img, (0, 0))
        draw_text(self.screen, "SCORE : " + str(self.score), pygame.font.Font(FONT_FILE_PATH, 96), WHITE, self.WIDTH // 4 + 100, self.HEIGHT // 2 + 120)

        button_save = Button(self.screen, self.WIDTH // 2 - 100, self.HEIGHT // 5, 200, 50, "Enregistrer mon score", self.manager)
        button_restart = Button(self.screen, self.WIDTH // 2 - 100, self.HEIGHT // 5 + 60, 200, 50, "Recommencer", self.manager)
        button_quit = Button(self.screen, self.WIDTH // 2 - 100, self.HEIGHT // 5 + 120, 200, 50, "Quitter", self.manager)
        button_save.draw()
        button_restart.draw()
        button_quit.draw()
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                self.manager.process_events(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == button_save.button:
                        self.save_score()
                        return
                    if event.ui_element == button_restart.button:
                        self.restart_game()
                    if event.ui_element == button_quit.button:
                        pygame.quit()
                        exit()

    def restart_game(self):
        # Crée une nouvelle instance du jeu et lance la méthode run
        self.__init__()  # Réinitialiser l'objet du jeu
        self.run(restart=True)  # Lancer la méthode run avec le nouvel objet

    def save_score(self):
        player_name = self.get_player_pseudo()
        pygame.display.update()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        scores = self.load_scores()

        new_score = {
            'name': player_name,
            'score': self.score,
            'date': current_time
        }
        scores.append(new_score)
        scores.sort(key=lambda x: x['score'], reverse=True)

        if len(scores) > 10:
            scores = scores[:10]

        self.save_scores(scores)
        try:
            player_rank = scores.index(new_score)
        except ValueError:
            player_rank = -1
        self.show_leaderboard(scores, player_rank)

    def load_scores(self):
        try:
            with open(LEADERBOARD_FILE_PATH, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_scores(self, scores):
        with open(LEADERBOARD_FILE_PATH, 'w') as f:
            json.dump(scores, f)

    def get_player_pseudo(self):
        input_box = pygame.Rect(self.WIDTH // 3, self.HEIGHT // 2 + 50, 140, 32)
        color_inactive = pygame.Color('black')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = False
        text = ''
        done = False

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        active = not active
                    else:
                        active = False
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN and text.strip():
                            done = True
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode

            self.manager.clear_and_reset()
            self.screen.blit(load_image(BACKGROUND_FILE_PATH, self.WIDTH, self.HEIGHT))
            draw_text(self.screen, "Entrez votre pseudo :", self.font, WHITE, self.WIDTH // 3, self.HEIGHT // 2)
            txt_surface = self.font.render(text, True, color)
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            self.screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(self.screen, color, input_box, 2)

            pygame.display.update()

        return text

    def show_leaderboard(self, scores, player_rank):
        self.manager.clear_and_reset()
        self.screen.blit(load_image(BACKGROUND_FILE_PATH, self.WIDTH, self.HEIGHT))
        # Afficher les 10 premiers scores
        draw_text(self.screen, "Leaderboard : ", self.font, WHITE, self.WIDTH // 3, self.HEIGHT // 4)
        for i, score in enumerate(scores[:10]):
            color = WHITE
            if (i == player_rank):
                # Couleur dorée pour mettre en surbrillance
                color = (255, 215, 0)
            draw_text(self.screen, f"{i+1}. {score['name']} - {score['score']} - {score['date']}", self.font, color,
                                        self.WIDTH // 3, self.HEIGHT // 4 + (i + 1) * 40)
            pygame.display.update()

        button_restart = Button(self.screen, self.WIDTH // 2 - 100, self.HEIGHT // 2 + 250, 200, 50, "Recommencer", self.manager)
        button_quit = Button(self.screen, self.WIDTH // 2 - 100, self.HEIGHT // 2 + 310, 200, 50, "Quitter", self.manager)
        button_restart.draw()
        button_quit.draw()
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                self.manager.process_events(event)
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == button_restart.button:
                        self.restart_game()

                    if event.ui_element == button_quit.button:
                        pygame.quit()
                        exit()
