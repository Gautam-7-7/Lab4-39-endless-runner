import pygame
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

        self.player = Player(80, self.ground_y)

        # Difficulty settings
        self.difficulty = "Medium"

        self.speed = 6
        self.max_speed = 12
        self.speed_increase_per_frame = 0.003
        self.spawn_interval = 70

        self._spawn_timer = 0
        self.obstacles = []

        self.distance = 0
        self.score = 0

        self.font = pygame.font.SysFont("Arial", 30)
        self.title_font = pygame.font.SysFont("Arial", 60)
        self.menu_font = pygame.font.SysFont("Arial", 36)

        self.game_over = False
        self.show_menu = False
        self.menu_options = ["Easy", "Medium", "Hard", "Exit"]
        self.selected_option = 0

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        # Game Over screen
        if self.game_over and not self.show_menu:
            if event.key == pygame.K_RETURN:
                self.show_menu = True
            return

        # Difficulty menu
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
                choice = self.menu_options[self.selected_option]

                if choice == "Exit":
                    pygame.event.post(
                        pygame.event.Event(pygame.QUIT)
                    )
                else:
                    self.start_new_game(choice)

            return

        # Normal gameplay
        if event.key in (
            pygame.K_SPACE,
            pygame.K_UP,
            pygame.K_w
        ):
            self.player.jump()

    def handle_input(self):
        pass

    def start_new_game(self, difficulty):
        self.difficulty = difficulty

        # Reset player
        self.player = Player(80, self.ground_y)

        # Reset game state
        self.obstacles = []
        self.score = 0
        self.distance = 0
        self._spawn_timer = 0
        self.game_over = False
        self.show_menu = False

        # Difficulty settings
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

    def update(self):
        if self.game_over or self.show_menu:
            return

        self.speed = min(
            self.speed + self.speed_increase_per_frame,
            self.max_speed
        )

        self.player.update()

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

        for obstacle in self.obstacles:
            previous_x = obstacle.x

            obstacle.move()
            obstacle.speed = self.speed

            # Check the complete path travelled this frame.
            swept_x = min(previous_x, obstacle.x)
            swept_width = (
                obstacle.width
                + abs(previous_x - obstacle.x)
            )

            swept_rect = pygame.Rect(
                swept_x,
                obstacle.y,
                swept_width,
                obstacle.height
            )

            if swept_rect.colliderect(
                self.player.rect()
            ):
                self.game_over = True
                return

        for obstacle in self.obstacles:
            if (
                not obstacle.scored
                and obstacle.x + obstacle.width < self.player.x
            ):
                obstacle.scored = True
                self.score += 1

        self.obstacles = [
            obstacle
            for obstacle in self.obstacles
            if not obstacle.off_screen()
        ]

        self.distance += self.speed

    def render(self, screen):
        # Normal game
        pygame.draw.line(
            screen,
            BROWN,
            (0, self.ground_y),
            (self.width, self.ground_y),
            4
        )

        pygame.draw.rect(
            screen,
            WHITE,
            self.player.rect()
        )

        for obstacle in self.obstacles:
            pygame.draw.rect(
                screen,
                DARK_GREEN,
                obstacle.rect()
            )

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            BLACK
        )
        screen.blit(score_text, (10, 10))

        # Game Over screen
        if self.game_over and not self.show_menu:
            overlay = pygame.Surface(
                (self.width, self.height)
            )
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            game_over_text = self.title_font.render(
                "GAME OVER",
                True,
                WHITE
            )

            final_score_text = self.font.render(
                f"Final Score: {self.score}",
                True,
                WHITE
            )

            instruction_text = self.menu_font.render(
                "Press ENTER to continue",
                True,
                WHITE
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

        # Difficulty menu
        if self.show_menu:
            screen.fill((200, 220, 240))

            title = self.title_font.render(
                "PLAY AGAIN",
                True,
                BLACK
            )

            screen.blit(
                title,
                title.get_rect(
                    center=(self.width // 2, 70)
                )
            )

            for i, option in enumerate(
                self.menu_options
            ):
                if i == self.selected_option:
                    text = self.menu_font.render(
                        "> " + option + " <",
                        True,
                        BLACK
                    )
                else:
                    text = self.menu_font.render(
                        option,
                        True,
                        BLACK
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