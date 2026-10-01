import pygame
from .player import Player
from .obstacle import Obstacle
from game import obstacle

# Game Engine

WHITE = (255, 255, 255)
BROWN = (120, 80, 40)
DARK_GREEN = (30, 100, 30)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ground_y = height - 40

        self.player = Player(80, self.ground_y)

        self.speed = 6
        self.max_speed = 12
        self.speed_increase_per_frame = 0.003
        

        self.spawn_interval = 70  # frames between obstacle spawns
        self._spawn_timer = 0
        self.obstacles = []

        self.distance = 0
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over = False

    def handle_event(self, event):
        if self.game_over:
            return
        if event.type==pygame.KEYDOWN and event.key in (
            pygame.K_SPACE,
            pygame.K_UP,
            pygame.K_w
        ):
            self.player.jump()

    def handle_input(self):
        # Reserved for continuously-held-key input; this runner only
        # needs an edge-triggered jump, handled in handle_event.
        pass

    def update(self):
        if self.game_over:
            return

        self.speed = min(
        self.speed + self.speed_increase_per_frame,
        self.max_speed)
        self.player.update()

        self._spawn_timer += 1
        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.obstacles.append(Obstacle(self.width, self.ground_y, self.speed))

        for obstacle in self.obstacles:
            previous_x = obstacle.x
            obstacle.move()
            obstacle.speed = self.speed

    # Check the entire horizontal path travelled this frame.
            swept_x = min(previous_x, obstacle.x)
            swept_width = obstacle.width + abs(previous_x - obstacle.x)

            swept_rect = pygame.Rect(
                swept_x,
                obstacle.y,
                swept_width,
                obstacle.height
            )

            if swept_rect.colliderect(self.player.rect()):
                self.game_over = True
                return

        for obstacle in self.obstacles:
            if not obstacle.scored and obstacle.x + obstacle.width < self.player.x:
                obstacle.scored = True
                self.score += 1

        self.obstacles = [o for o in self.obstacles if not o.off_screen()]

        self.distance += self.speed

    def render(self, screen):
        pygame.draw.line(
            screen,
            BROWN,
            (0, self.ground_y),
            (self.width, self.ground_y),
            4
        )

        pygame.draw.rect(screen, WHITE, self.player.rect())

        for obstacle in self.obstacles:
            pygame.draw.rect(screen, DARK_GREEN, obstacle.rect())

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            (0, 0, 0)
        )
        screen.blit(score_text, (10, 10))

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            game_over_font = pygame.font.SysFont("Arial", 60)
            instruction_font = pygame.font.SysFont("Arial", 28)

            game_over_text = game_over_font.render(
                "GAME OVER",
                True,
                WHITE
            )

            final_score_text = self.font.render(
                f"Final Score: {self.score}",
                True,
                WHITE
            )

            instruction_text = instruction_font.render(
                "Press ENTER to continue",
                True,
                WHITE
            )

            screen.blit(
                game_over_text,
                game_over_text.get_rect(
                    center=(self.width // 2, self.height // 2 - 70)
                )
            )
        

            screen.blit(
                final_score_text,
                final_score_text.get_rect(
                    center=(self.width // 2, self.height // 2)
                )
            )
        

            screen.blit(
                instruction_text,
                instruction_text.get_rect(
                    center=(self.width // 2, self.height // 2 + 60)
                )
            )
            

