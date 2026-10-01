import pygame
import math
import array

from .player import Player
from .obstacle import Obstacle


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (120, 80, 40)
DARK_GREEN = (30, 100, 30)


class GameEngine:

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.ground_y = height - 40

        # Player
        self.player = Player(
            80,
            self.ground_y
        )

        # Difficulty
        self.difficulty = "Medium"

        # Medium difficulty defaults
        self.speed = 6
        self.max_speed = 12
        self.speed_increase_per_frame = 0.003

        # Obstacle spawning
        self.spawn_interval = 70
        self._spawn_timer = 0

        self.obstacles = []

        # Score
        self.distance = 0
        self.score = 0

        # Fonts
        self.font = pygame.font.SysFont(
            "Arial",
            30
        )

        self.title_font = pygame.font.SysFont(
            "Arial",
            60
        )

        self.menu_font = pygame.font.SysFont(
            "Arial",
            36
        )

        # Game states
        self.game_over = False
        self.show_menu = False

        # Replay menu
        self.menu_options = [
            "Easy",
            "Medium",
            "Hard",
            "Exit"
        ]

        self.selected_option = 0

        # Sound setup
        self.setup_sounds()

    # -------------------------------------------------
    # SOUND SYSTEM
    # -------------------------------------------------

    def setup_sounds(self):
        """
        Create simple sound effects in memory.
        No external audio files are required.
        """

        self.jump_sound = None
        self.score_sound = None
        self.game_over_sound = None

        try:
            pygame.mixer.init()

            self.jump_sound = self.create_tone(
                frequency=600,
                duration=0.12,
                volume=0.4
            )

            self.score_sound = self.create_tone(
                frequency=900,
                duration=0.10,
                volume=0.4
            )

            self.game_over_sound = self.create_tone(
                frequency=180,
                duration=0.35,
                volume=0.5
            )

        except pygame.error:
            # Game should still work if audio is unavailable.
            self.jump_sound = None
            self.score_sound = None
            self.game_over_sound = None

        self.game_over_sound_played = False

    def create_tone(
        self,
        frequency,
        duration,
        volume
    ):
        """
        Generate a simple sine-wave sound.
        """

        sample_rate = 44100
        sample_count = int(
            sample_rate * duration
        )

        samples = array.array(
            "h"
        )

        for i in range(sample_count):
            value = int(
                32767
                * volume
                * math.sin(
                    2
                    * math.pi
                    * frequency
                    * i
                    / sample_rate
                )
            )

            samples.append(value)

        return pygame.mixer.Sound(
            buffer=samples.tobytes()
        )

    # -------------------------------------------------
    # INPUT
    # -------------------------------------------------

    def handle_event(self, event):

        if event.type != pygame.KEYDOWN:
            return

        # -----------------------------
        # GAME OVER SCREEN
        # -----------------------------

        if self.game_over and not self.show_menu:

            if event.key == pygame.K_RETURN:
                self.show_menu = True

            return

        # -----------------------------
        # REPLAY MENU
        # -----------------------------

        if self.show_menu:

            if event.key == pygame.K_UP:

                self.selected_option = (
                    self.selected_option - 1
                ) % len(self.menu_options)

            elif event.key == pygame.K_DOWN:

                self.selected_option = (
                    self.selected_option + 1
                ) % len(self.menu_options)

            elif event.key == pygame.K_RETURN:

                choice = self.menu_options[
                    self.selected_option
                ]

                if choice == "Exit":

                    pygame.event.post(
                        pygame.event.Event(
                            pygame.QUIT
                        )
                    )

                else:

                    self.start_new_game(
                        choice
                    )

            return

        # -----------------------------
        # NORMAL GAMEPLAY
        # -----------------------------

        if event.key in (
            pygame.K_SPACE,
            pygame.K_UP,
            pygame.K_w
        ):

            self.player.jump()

            # Jump sound
            if self.jump_sound:
                self.jump_sound.play()

    def handle_input(self):
        """
        Reserved for continuously held-key input.
        """

        pass

    # -------------------------------------------------
    # START NEW GAME
    # -------------------------------------------------

    def start_new_game(self, difficulty):

        self.difficulty = difficulty

        # Reset player
        self.player = Player(
            80,
            self.ground_y
        )

        # Clear obstacles
        self.obstacles = []

        # Reset score
        self.score = 0
        self.distance = 0

        # Reset timers
        self._spawn_timer = 0

        # Reset states
        self.game_over = False
        self.show_menu = False

        # Reset game-over sound
        self.game_over_sound_played = False

        # Reset menu
        self.selected_option = 0

        # -----------------------------
        # DIFFICULTY SETTINGS
        # -----------------------------

        if difficulty == "Easy":

            self.speed = 5
            self.max_speed = 8
            self.spawn_interval = 85

        elif difficulty == "Medium":

            self.speed = 6
            self.max_speed = 12
            self.spawn_interval = 70

        elif difficulty == "Hard":

            self.speed = 8
            self.max_speed = 15
            self.spawn_interval = 55

    # -------------------------------------------------
    # UPDATE GAME
    # -------------------------------------------------

    def update(self):

        # Stop gameplay after Game Over
        if self.game_over:
            return

        # Stop gameplay while menu is open
        if self.show_menu:
            return

        # -----------------------------
        # INCREASE SPEED
        # -----------------------------

        self.speed = min(
            self.speed
            + self.speed_increase_per_frame,
            self.max_speed
        )

        # -----------------------------
        # UPDATE PLAYER
        # -----------------------------

        self.player.update()

        # -----------------------------
        # SPAWN OBSTACLES
        # -----------------------------

        self._spawn_timer += 1

        if self._spawn_timer >= self.spawn_interval:

            self._spawn_timer = 0

            self.obstacles.append(
                Obstacle(
                    self.width,
                    self.ground_y,
                    self.speed
                )
            )

        # -----------------------------
        # MOVE + COLLISION
        # -----------------------------

        for obstacle in self.obstacles:

            # Remember old position
            previous_x = obstacle.x

            # Move obstacle
            obstacle.move()

            # Update obstacle speed
            obstacle.speed = self.speed

            # -------------------------
            # SWEPT COLLISION
            # -------------------------

            swept_x = min(
                previous_x,
                obstacle.x
            )

            swept_width = (
                obstacle.width
                + abs(
                    previous_x
                    - obstacle.x
                )
            )

            swept_rect = pygame.Rect(
                swept_x,
                obstacle.y,
                swept_width,
                obstacle.height
            )

            # Check collision
            if swept_rect.colliderect(
                self.player.rect()
            ):

                self.game_over = True

                # Game-over sound
                if not self.game_over_sound_played:

                    if self.game_over_sound:
                        self.game_over_sound.play()

                    self.game_over_sound_played = True

                return

        # -----------------------------
        # SCORE
        # -----------------------------

        for obstacle in self.obstacles:

            if (
                not obstacle.scored
                and obstacle.x
                + obstacle.width
                < self.player.x
            ):

                obstacle.scored = True

                self.score += 1

                # Score sound
                if self.score_sound:
                    self.score_sound.play()

        # -----------------------------
        # REMOVE OLD OBSTACLES
        # -----------------------------

        self.obstacles = [
            obstacle
            for obstacle in self.obstacles
            if not obstacle.off_screen()
        ]

        # Distance
        self.distance += self.speed

    # -------------------------------------------------
    # RENDER
    # -------------------------------------------------

    def render(self, screen):

        # -----------------------------
        # GAMEPLAY
        # -----------------------------

        pygame.draw.line(
            screen,
            BROWN,
            (0, self.ground_y),
            (
                self.width,
                self.ground_y
            ),
            4
        )

        # Player
        pygame.draw.rect(
            screen,
            WHITE,
            self.player.rect()
        )

        # Obstacles
        for obstacle in self.obstacles:

            pygame.draw.rect(
                screen,
                DARK_GREEN,
                obstacle.rect()
            )

        # Score
        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            BLACK
        )

        screen.blit(
            score_text,
            (10, 10)
        )

        # -----------------------------
        # GAME OVER SCREEN
        # -----------------------------

        if (
            self.game_over
            and not self.show_menu
        ):

            overlay = pygame.Surface(
                (
                    self.width,
                    self.height
                )
            )

            overlay.set_alpha(180)
            overlay.fill(BLACK)

            screen.blit(
                overlay,
                (0, 0)
            )

            game_over_text = (
                self.title_font.render(
                    "GAME OVER",
                    True,
                    WHITE
                )
            )

            final_score_text = (
                self.font.render(
                    f"Final Score: {self.score}",
                    True,
                    WHITE
                )
            )

            instruction_text = (
                self.menu_font.render(
                    "Press ENTER to continue",
                    True,
                    WHITE
                )
            )

            screen.blit(
                game_over_text,
                game_over_text.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2 - 70
                    )
                )
            )

            screen.blit(
                final_score_text,
                final_score_text.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2
                    )
                )
            )

            screen.blit(
                instruction_text,
                instruction_text.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2 + 60
                    )
                )
            )

        # -----------------------------
        # REPLAY MENU
        # -----------------------------

        if self.show_menu:

            screen.fill(
                (200, 220, 240)
            )

            title = self.title_font.render(
                "PLAY AGAIN",
                True,
                BLACK
            )

            screen.blit(
                title,
                title.get_rect(
                    center=(
                        self.width // 2,
                        70
                    )
                )
            )

            # Menu options
            for i, option in enumerate(
                self.menu_options
            ):

                if (
                    i
                    == self.selected_option
                ):

                    text = (
                        self.menu_font.render(
                            "> "
                            + option
                            + " <",
                            True,
                            BLACK
                        )
                    )

                else:

                    text = (
                        self.menu_font.render(
                            option,
                            True,
                            BLACK
                        )
                    )

                screen.blit(
                    text,
                    text.get_rect(
                        center=(
                            self.width // 2,
                            140 + i * 55
                        )
                    )
                )

            controls = self.font.render(
                "Use UP/DOWN and ENTER",
                True,
                BLACK
            )

            screen.blit(
                controls,
                controls.get_rect(
                    center=(
                        self.width // 2,
                        self.height - 35
                    )
                )
            )