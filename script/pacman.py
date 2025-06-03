import pygame
from pygame.locals import *
from random import randint
import platform
import asyncio

# Konstanta
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
BLACK = (0, 0, 0)
PACMAN_START_POS = (512, 350)
APPLE_AREA = (100, 950, 200, 600)
ENEMY_AREA = (100, 950, 200, 600)
FPS = 60

class CEvent:
    def on_key_down(self, event):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]: return 'left'
        if keys[K_RIGHT]: return 'right'
        if keys[K_UP]: return 'up'
        if keys[K_DOWN]: return 'down'
        if keys[K_q]: return 'quit'

class GameObject:
    def __init__(self, image_path, pos):
        self.image = pygame.image.load(image_path).convert()
        self.rect = pygame.Rect(*pos, 50, 50)
        self.pos = list(pos)

    def draw(self, surface):
        surface.blit(self.image, self.pos)
        self.rect.topleft = self.pos

    def move(self, dx=0, dy=0):
        self.pos[0] += dx
        self.pos[1] += dy
        self.rect.topleft = self.pos

    def reset_position(self, pos):
        self.pos = list(pos)
        self.rect.topleft = self.pos

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pacman Simplified")
        self.clock = pygame.time.Clock()

        self.event_handler = CEvent()
        self.running = True

        self.font = pygame.font.SysFont('Comic Sans MS', 30)

        self.level = 1
        self.score = 0
        self.score_goal = 100
        self.time_left = 120
        self.lives = 3
        self.game_over = False

        self.pacman_images = {
            'right': pygame.image.load("source/pacman.png").convert(),
            'left': pygame.image.load("source/pacmanL.png").convert(),
            'up': pygame.image.load("source/pacmanUp.png").convert(),
            'down': pygame.image.load("source/pacmanDw.png").convert(),
        }
        self.direction = 'right'

        self.pacman = GameObject("source/pacman.png", PACMAN_START_POS)
        self.apple = GameObject("source/apple.png", self.random_position(APPLE_AREA))
        self.enemy = GameObject("source/enemy.png", self.random_position(ENEMY_AREA))

        self.movement_speed = 8
        self.enemy_speed = 5
        self.last_update = pygame.time.get_ticks()
        self.last_enemy_move = pygame.time.get_ticks()

    def random_position(self, area):
        x = randint(area[0], area[1])
        y = randint(area[2], area[3])
        return x, y

    def handle_event(self, event):
        if event.type == QUIT:
            self.running = False
        elif event.type == KEYDOWN:
            action = self.event_handler.on_key_down(event)
            if action == 'quit':
                self.running = False
            else:
                self.move_pacman(action)

    def move_pacman(self, direction):
        self.direction = direction
        dx = dy = 0
        if direction == 'left': dx = -self.movement_speed
        elif direction == 'right': dx = self.movement_speed
        elif direction == 'up': dy = -self.movement_speed
        elif direction == 'down': dy = self.movement_speed

        new_x = max(30, min(SCREEN_WIDTH - 50, self.pacman.pos[0] + dx))
        new_y = max(60, min(SCREEN_HEIGHT - 50, self.pacman.pos[1] + dy))
        self.pacman.pos = [new_x, new_y]

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Tambahkan key hold support
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.move_pacman('left')
        elif keys[K_RIGHT]:
            self.move_pacman('right')
        elif keys[K_UP]:
            self.move_pacman('up')
        elif keys[K_DOWN]:
            self.move_pacman('down')

        # Timer dan logic lainnya
        if current_time - self.last_update >= 1000:
            self.time_left -= 1
            self.last_update = current_time
            if self.time_left <= 0:
                self.game_over = True

        # Apple collision
        if self.pacman.rect.colliderect(self.apple.rect):
            self.score += 10
            self.apple.reset_position(self.random_position(APPLE_AREA))

        # Enemy collision
        if self.pacman.rect.colliderect(self.enemy.rect):
            self.lives -= 1
            self.pacman.reset_position(PACMAN_START_POS)
            self.enemy.reset_position(self.random_position(ENEMY_AREA))
            if self.lives <= 0:
                self.game_over = True

        # Enemy movement
        if current_time - self.last_enemy_move >= 500:
            dx = self.pacman.pos[0] - self.enemy.pos[0]
            dy = self.pacman.pos[1] - self.enemy.pos[1]
            if abs(dx) > abs(dy):
                self.enemy.move(self.enemy_speed if dx > 0 else -self.enemy_speed, 0)
            else:
                self.enemy.move(0, self.enemy_speed if dy > 0 else -self.enemy_speed)
            self.last_enemy_move = current_time

        # Level up
        if self.score >= self.score_goal:
            self.level += 1
            self.score = 0
            self.score_goal = self.level * 100
            self.time_left = max(60, 120 - self.level * 10)
            self.movement_speed += 1
            self.enemy_speed += 1


    def draw_ui(self):
        texts = [
            (f"Skor: {self.score}/{self.score_goal}", 600),
            (f"Level: {self.level}", 400),
            (f"Waktu: {self.time_left}s", 200),
            (f"Nyawa: {self.lives}", 0),
            ("Tekan 'q' untuk Keluar", 550, 710),
        ]
        for i, (txt, x, *y) in enumerate(texts):
            pos_y = y[0] if y else 0
            self.screen.blit(self.font.render(txt, False, (255, 255, 255)), (x, pos_y))

    def render(self):
        self.screen.fill(BLACK)
        if self.game_over:
            self.screen.blit(self.font.render("Game Over! Press Q to exit", False, (255, 0, 0)), (350, 350))
        else:
            self.apple.draw(self.screen)
            self.enemy.draw(self.screen)
            self.pacman.image = self.pacman_images[self.direction]
            self.pacman.draw(self.screen)
            self.draw_ui()
        pygame.display.flip()

    async def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.update()
            self.render()
            await asyncio.sleep(1 / FPS)
        pygame.quit()

async def main():
    app = App()
    await app.run()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
elif __name__ == '__main__':
    asyncio.run(main())
