"""
Game Module for Emotion Race
=============================

This module contains the main game logic for the Emotion Race game. It handles
initialization, game loop management, event handling, and rendering of game
elements. The game is built using the Pygame library, and it includes features
such as player movement, obstacle generation, scoring, and game over handling.

Classes:
    - Game: The main class that manages the game state, rendering, and user interactions.

Functions:
    - The Game class includes methods for running the game loop, handling events,
      updating game state, and drawing game elements on the screen.

Usage:
    - This module is intended to be used as part of the Emotion Race game application.
    - It requires a configuration file to set up initial game parameters and assets.

Dependencies:
    - pygame: For game rendering and event handling.
    - pygame_gui: For managing UI elements.
    - json: For loading and saving game configuration and scores.
    - datetime: For timestamping saved scores.
    - sys: For system-specific parameters and functions.
    - time: For handling time-related operations.
    - pandas: For reading and processing stress data from CSV files.
    - helpers (custom module): Utility functions such as loading images and drawing text.
    - menu (custom module): UI management for the game menu.
    - button (custom module): Custom button handling for UI interactions.
    - player (custom module): Player entity and behavior.
    - obstacle (custom module): Obstacle mechanics and behavior.
"""

from datetime import datetime
import json
import sys
import time
import pandas as pd
import pygame
import pygame_gui
from .utils.helpers import load_image, draw_text
from .ui.menu import Menu
from .ui.button import Button
from .core.player import Player
from .core.obstacle import Obstacle

class Game:
    """
    The main game class that handles the game logic and rendering.
    """

    def __init__(self, config_filepath: str) -> None:
        """
        Initialize the game with the given configuration file path.

        Args:
            config_filepath (str): The path to the configuration file.
        """
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption('Emotion Race')

        self.__screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.__width, self.__height = self.__screen.get_size()

        self.__config_filepath = config_filepath
        with open(config_filepath, 'r', encoding='utf-8') as file:
            self.__config = json.load(file)

        # Load images and initialize game variables
        self.__load_images()
        self.__initialize_game_variables()

    def __load_images(self) -> None:
        """Load all necessary images for the game."""
        self.__logout_img = load_image(self.__config['ui_settings']['logout_file_path'], 40, 40)
        self.__logout_rect = self.__logout_img.get_rect(topright=(self.__width - 10, 10))
        self.__obstacle_img = load_image(self.__config['ui_settings']['obstacle_file_path'], 40, 40)
        self.__background_img = load_image(self.__config['ui_settings']['background_file_path'],
                                           self.__width, self.__height)
        self.__foreground_img = load_image(self.__config['ui_settings']['foreground_file_path'],
                                           self.__width + 6)
        self.__game_over_img = load_image(self.__config['ui_settings']['gameover_file_path'],
                                          self.__width, self.__height)

    def __initialize_game_variables(self) -> None:
        """Initialize game variables and settings."""
        self.__font_filepath = self.__config['ui_settings']['font_file_path']
        self.__font = pygame.font.Font(self.__font_filepath, 16)

        # Initialisation de pygame_gui
        self.__manager = pygame_gui.UIManager((self.__width, self.__height))
        self.__manager.add_font_paths("cybrpnuk", self.__font_filepath)

        self.__background_x1 = 0
        self.__background_x2 = self.__width
        self.__foreground_x1 = 0
        self.__foreground_x2 = self.__width

        self.__score = 0
        self.__speed = self.__config['game_settings']['player_speed_at_beginning']
        self.__player = Player(self.__height, self.__config['ui_settings']['player_file_path'])
        self.__nb_obstacles = self.__config['game_settings']['nb_obstacles']
        self.__min_spacing = 200
        self.__max_spacing = 700
        self.__spacing = self.__min_spacing + (self.__max_spacing
                                               - self.__min_spacing) * (self.__speed / 40)
        self.__obstacles = pygame.sprite.Group()
        self.__obstacles.add(
            Obstacle((self.__width + i * self.__spacing), self.__height, self.__speed,
                     self.__obstacle_img) for i in range(self.__nb_obstacles)
        )

        self.__gravity = self.__config['game_settings']['gravity_min']
        self.__jump_strength = self.__config['game_settings']['jump_strength_min']
        self.__paused = False

        self.__stress_file_path = self.__config['sensors']['stress_file_path']
        self.__stress_state = 'CALM'


    def __monitor_stress(self) -> None:
        """
        Monitors the player's stress level based on the latest recorded state in a CSV file.

        This method reads the stress data file, extracts the last recorded state, 
        and updates the player's stress state accordingly. If the file does not contain 
        at least two lines of data, it waits for more data to be available.

        Raises:
            FileNotFoundError: If the stress data file is not found.
            pd.errors.ParserError: If the file contains invalid data that cannot be parsed.
        """
        try:
            df = pd.read_csv(self.__stress_file_path)

            if len(df) < 2:
                print('Waiting for at least 2 lines in the file...')
                return

            last_state = df.iloc[-1]['State']

            if last_state == 'CALM':
                self.__stress_state = 'CALM'
            elif last_state == 'MODERATE':
                self.__stress_state = 'MODERATE'
            elif last_state == 'STRESSED':
                self.__stress_state = 'STRESSED'
        except FileNotFoundError:
            print(f"Error: The stress data file '{self.__stress_file_path}' was not found.")
        except pd.errors.ParserError:
            print(f"Error: Unable to parse the stress data file '{self.__stress_file_path}'")

    def run(self, restart: bool = False) -> None:
        """
        Run the main game loop.

        Args:
            restart (bool): Whether the game is being restarted.
        """
        self.start_music()
        if not restart:
            self.show_start_screen()
        else:
            self.__initialize_game_variables()

        running = True
        time_counter = 0
        pygame.event.set_allowed([pygame.QUIT,
                                  pygame.KEYDOWN,
                                  pygame.MOUSEBUTTONDOWN,
                                  pygame_gui.UI_BUTTON_PRESSED])
        clock = pygame.time.Clock()

        last_time = time.time()

        while running:
            current_time = time.time()
            elapsed_time = current_time - last_time
            last_time = current_time
            time_counter += elapsed_time

            if time_counter >= 2: #Update every 2 seconds
                self.__monitor_stress()
                time_counter = 0
            self.__handle_events()

            if not self.__paused:
                self.__update_game()
                self.__draw_elements()

            pygame.display.flip()
            clock.tick(60)

    def __handle_events(self) -> None:
        """Handle game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__quit_game()
            elif event.type == pygame.KEYDOWN:
                self.__handle_keydown_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and self.__logout_rect.collidepoint(
                event.pos):
                self.__quit_game()

    def __quit_game(self) -> None:
        """Quit the game safely."""
        pygame.quit()
        sys.exit()

    def __handle_keydown_event(self, event: pygame.event.Event) -> None:
        """
        Handle keydown events.

        Args:
            event (pygame.event.Event): The event to handle.
        """
        if event.key == pygame.K_SPACE and not self.__paused:
            self.__player.jump(self.__jump_strength)
        elif event.key == pygame.K_ESCAPE:
            self.__quit_game()
        elif event.key == pygame.K_p:
            self.toggle_pause()

    def __update_game(self) -> None:
        """Update game state."""
        self.__player.update(self.__gravity)
        if self.__player.is_alive():
            self.__score += 1
            self.__speed = (self.__config['game_settings']['player_speed_at_beginning']
                            + self.__score // 200)
            self.__gravity = min(self.__gravity
                              + 0.001, self.__config['game_settings']['gravity_max'])
            self.__jump_strength = max(self.__config['game_settings']['jump_strength_min']
                                    - self.__score // 200,
                                    self.__config['game_settings']['jump_strength_max'])
            self.__nb_obstacles = min(self.__config['game_settings']['nb_obstacles']
                                      + self.__score // 200, 10)

        self.__update_background()
        self.__update_obstacles()

    def __update_background(self) -> None:
        """Update the background position."""
        for attr in ['_Game__background_x1', '_Game__background_x2']:
            setattr(self, attr,
                    getattr(self, attr) - self.__config['game_settings']['background_speed'])
            if getattr(self, attr) <= -self.__width:
                setattr(self, attr, self.__width)

        for attr in ['_Game__foreground_x1', '_Game__foreground_x2']:
            setattr(self, attr,
                    getattr(self, attr) - self.__config['game_settings']['foreground_speed'])
            if getattr(self, attr) <= -self.__width:
                setattr(self, attr, self.__width)

    def __update_obstacles(self) -> None:
        """Update the obstacles."""
        self.__obstacles = [obstacle for obstacle in
                            self.__obstacles if obstacle.get_rect().x >= -40]

        for obstacle in self.__obstacles:
            obstacle.update()
            if self.__player.get_hitbox().colliderect(obstacle.get_hitbox()):
                self.__player.set_is_alive(False)
                self.game_over()

        if not self.__obstacles:
            self.__generate_obstacles()

    def __generate_obstacles(self) -> None:
        """Generate new obstacles based on the player's speed and score."""
        normalized_speed = min(self.__speed, 20)
        self.__spacing = self.__min_spacing + (self.__max_spacing
                                               - self.__min_spacing) * (normalized_speed / 20)
        self.__nb_obstacles = min(self.__config['game_settings']['nb_obstacles']
                                  + self.__score // 100, 10)

        if not self.__obstacles:
            self.__obstacles = [
                Obstacle(self.__width + i * self.__spacing,
                         self.__height, self.__speed, self.__obstacle_img)
                for i in range(self.__nb_obstacles)
            ]
        else:
            self.__obstacles.add(
                Obstacle(self.__width + i * self.__spacing,
                        self.__height, self.__speed, self.__obstacle_img)
                for i in range(self.__nb_obstacles)
            )

    def __draw_elements(self) -> None:
        """Draw all game elements on the screen."""
        self.__draw_background()
        self.__draw_game_info()
        self.__player.draw(self.__screen)

        for obstacle in self.__obstacles:
            obstacle.draw(self.__screen)

        if self.__paused:
            self.__draw_pause_screen()

        if self.__stress_state != 'CALM':
            if self.__stress_state == 'MODERATE':
                self.__draw_blurred_background(width=200, factor=20)
            elif self.__stress_state == 'STRESSED':
                self.__draw_blurred_background(width=400, factor=50)

        self.__screen.blit(self.__logout_img, self.__logout_rect.topleft)

    def __draw_background(self) -> None:
        """Draw the background and foreground images."""
        self.__screen.blit(self.__background_img,
                           (self.__background_x1, 0))
        self.__screen.blit(self.__background_img,
                           (self.__background_x2, 0))
        self.__screen.blit(self.__foreground_img,
                           (self.__foreground_x1, self.__height - 110))
        self.__screen.blit(self.__foreground_img,
                           (self.__foreground_x2, self.__height - 110))

    def __draw_blurred_background(self, width : int, factor : int) -> None:
        """Draw a blurred background when the player is stressed."""
        blur_area = pygame.Rect(0, 0, width, self.__height)
        sub_surface = self.__screen.subsurface(blur_area).copy()
        small_surface = pygame.transform.smoothscale(sub_surface,
                                                     (sub_surface.get_width() // factor,
                                                      sub_surface.get_height() // factor))
        blurred_sub_surface = pygame.transform.smoothscale(small_surface,
                                                           (sub_surface.get_width(),
                                                            sub_surface.get_height()))
        self.__screen.blit(blurred_sub_surface, blur_area.topleft)

    def __draw_game_info(self) -> None:
        """Draw game information such as score and speed."""
        info_text = f"Score : {self.__score} | Vitesse : {self.__speed} | "
        info_text += f"Gravité : {int(self.__gravity)} | Force de saut : "
        info_text += f"{abs(self.__jump_strength)} | Stress : {self.__stress_state}"
        draw_text(self.__screen, info_text, self.__font, (255, 255, 255), 60, 10)

    def __draw_pause_screen(self) -> None:
        """Draw the pause screen."""
        if pygame.time.get_ticks() // 500 % 2 == 0:  # Clignotement toutes les 500ms
            draw_text(self.__screen, "Pause - Appuyez sur P pour reprendre",
                      self.__font, (255, 255, 255), self.__width // 3, self.__height // 2)
    def start_music(self) -> None:
        """Start the background music."""
        pygame.mixer.music.load(self.__config['ui_settings']['song_file_path'])
        pygame.mixer.music.play(-1, 0.0)

    def show_start_screen(self) -> None:
        """Show the start screen with the main menu."""
        main_menu = Menu(self.__screen, self.__width, self.__height,
                         self.__manager, self.__font_filepath)
        main_menu.show(self.__background_img, pygame.font.Font(self.__font_filepath, 110))

    def toggle_pause(self) -> None:
        """Toggle the pause state of the game."""
        self.__paused = not self.__paused

    def game_over(self) -> None:
        """Handle the game over state and display the game over screen."""
        self.__manager.clear_and_reset()
        self.__screen.blit(self.__game_over_img, (0, 0))
        draw_text(self.__screen, "SCORE : " + str(self.__score),
                  pygame.font.Font(self.__font_filepath, 96), (255, 255, 255),
                  self.__width // 4 + 100, self.__height // 2 + 120)

        button_save = Button(self.__screen, self.__width // 2 - 100, self.__height // 5,
                             200, 50, "Enregistrer mon score", self.__manager)
        button_restart = Button(self.__screen, self.__width // 2 - 100, self.__height // 5 + 60,
                                200, 50, "Recommencer", self.__manager)
        button_quit = Button(self.__screen, self.__width // 2 - 100, self.__height // 5 + 120,
                             200, 50, "Quitter", self.__manager)
        button_save.draw()
        button_restart.draw()
        button_quit.draw()
        pygame.display.update()

        self.__handle_game_over_events(button_save, button_restart, button_quit)

    def __handle_game_over_events(self, button_save: Button,
                                  button_restart: Button,
                                  button_quit: Button) -> None:
        """
        Handle events during the game over screen.

        Args:
            button_save (Button): The save score button.
            button_restart (Button): The restart game button.
            button_quit (Button): The quit game button.
        """
        while True:
            for event in pygame.event.get():
                self.__manager.process_events(event)
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == button_save.get_button():
                        self.save_score()
                        return
                    if event.ui_element == button_restart.get_button():
                        self.restart_game()
                    if event.ui_element == button_quit.get_button():
                        sys.exit()

    def restart_game(self) -> None:
        """Restart the game by creating a new instance and running it."""
        new_game_instance = self.__class__(self.__config_filepath)
        new_game_instance.run(restart=True)

    def save_score(self) -> None:
        """Save the player's score to the leaderboard."""
        player_name = self.get_player_pseudo()
        pygame.display.update()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        scores = self.load_scores()

        new_score = {
            'name': player_name,
            'score': self.__score,
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

    def load_scores(self) -> list:
        """
        Load scores from the leaderboard file.

        Returns:
            list: A list of score dictionaries.
        """
        try:
            with open(self.__config['ui_settings']['leaderboard_file_path'],
                      'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_scores(self, scores: list) -> None:
        """
        Save scores to the leaderboard file.

        Args:
            scores (list): A list of score dictionaries to save.
        """
        with open(self.__config['ui_settings']['leaderboard_file_path'],
                  'w', encoding='utf-8') as f:
            json.dump(scores, f)

    def get_player_pseudo(self) -> str:
        """
        Get the player's pseudo from user input.

        Returns:
            str: The player's pseudo.
        """
        input_box = pygame.Rect(self.__width // 3, self.__height // 2 + 50, 140, 32)
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
                    sys.exit()
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

            self.__manager.clear_and_reset()
            self.__screen.blit(load_image(self.__config['ui_settings']['background_file_path'],
                                          self.__width, self.__height))
            draw_text(self.__screen, "Entrez votre pseudo :", self.__font, (255, 255, 255),
                      self.__width // 3, self.__height // 2)
            txt_surface = self.__font.render(text, True, color)
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            self.__screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(self.__screen, color, input_box, 2)

            pygame.display.update()

        return text

    def show_leaderboard(self, scores: list, player_rank: int) -> None:
        """
        Show the leaderboard with the top scores.

        Args:
            scores (list): A list of score dictionaries.
            player_rank (int): The rank of the player's score.
        """
        self.__manager.clear_and_reset()
        self.__screen.blit(load_image(self.__config['ui_settings']['background_file_path'],
                                      self.__width, self.__height))
        draw_text(self.__screen, "Leaderboard : ", self.__font, (255, 255, 255),
                  self.__width // 3, self.__height // 4)
        for i, score in enumerate(scores[:10]):
            color = (255, 255, 255)
            if i == player_rank:
                color = (255, 215, 0)
            draw_text(self.__screen, f"{i+1}. {score['name']} - {score['score']} - {score['date']}",
                      self.__font, color, self.__width // 3, self.__height // 4 + (i + 1) * 40)
            pygame.display.update()

        button_restart = Button(self.__screen, self.__width // 2 - 100, self.__height // 2 + 250,
                                200, 50, "Recommencer", self.__manager)
        button_quit = Button(self.__screen, self.__width // 2 - 100, self.__height // 2 + 310,
                             200, 50, "Quitter", self.__manager)
        button_restart.draw()
        button_quit.draw()
        pygame.display.update()

        self.__handle_leaderboard_events(button_restart, button_quit)

    def __handle_leaderboard_events(self, button_restart: Button, button_quit: Button) -> None:
        """
        Handle events during the leaderboard screen.

        Args:
            button_restart (Button): The restart game button.
            button_quit (Button): The quit game button.
        """
        while True:
            for event in pygame.event.get():
                self.__manager.process_events(event)
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == button_restart.get_button():
                        self.restart_game()
                    if event.ui_element == button_quit.get_button():
                        sys.exit()
