# Query: 
# ContextLines: 1

import sys
import random
import math

# Try to import pygame, if not available, use a simple tkinter-based alternative
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("pygame not found. Install it with: pip install pygame")
    print("Using alternative tkinter-based implementation instead...\n")

if PYGAME_AVAILABLE:
    # Pygame version
    pygame.init()

    SCREEN_WIDTH = 400
    SCREEN_HEIGHT = 600
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    CYAN = (0, 255, 255)

    FPS = 60
    GRAVITY = 0.5
    FLAP_STRENGTH = -12
    PIPE_WIDTH = 80
    PIPE_GAP = 120
    PIPE_SPEED = 5
    PIPE_SPAWN_RATE = 90

    class Bird:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.width = 30
            self.height = 30
            self.velocity = 0
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        def flap(self):
            self.velocity = FLAP_STRENGTH
        
        def update(self):
            self.velocity += GRAVITY
            self.y += self.velocity
            self.rect.y = self.y
        
        def draw(self, surface):
            pygame.draw.circle(surface, YELLOW, (self.x + self.width // 2, self.y + self.height // 2), self.width // 2)
            pygame.draw.circle(surface, BLACK, (self.x + 20, self.y + 15), 3)
        
        def is_off_screen(self):
            return self.y > SCREEN_HEIGHT or self.y < 0

    class Pipe:
        def __init__(self, x):
            self.x = x
            self.width = PIPE_WIDTH
            self.gap = PIPE_GAP
            self.height = PIPE_HEIGHT
            self.gap_y = random.randint(50, SCREEN_HEIGHT - self.gap - 50)
            self.top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
            self.bottom_rect = pygame.Rect(self.x, self.gap_y + self.gap, self.width, self.height - self.gap_y)
            self.passed = False
        
        def update(self):
            self.x -= PIPE_SPEED
            self.top_rect.x = self.x
            self.bottom_rect.x = self.x
        
        def draw(self, surface):
            pygame.draw.rect(surface, GREEN, self.top_rect)
            pygame.draw.rect(surface, GREEN, self.bottom_rect)
        
        def is_off_screen(self):
            return self.x + self.width < 0
        
        def collides_with(self, bird):
            return bird.rect.colliderect(self.top_rect) or bird.rect.colliderect(self.bottom_rect)

    class Game:
        def __init__(self):
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Flappy Bird Clone")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 36)
            self.large_font = pygame.font.Font(None, 72)
            self.reset_game()
        
        def reset_game(self):
            self.bird = Bird(50, SCREEN_HEIGHT // 2)
            self.pipes = []
            self.score = 0
            self.game_over = False
            self.frame_count = 0
        
        def handle_events(self):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game_over:
                            self.reset_game()
                        else:
                            self.bird.flap()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over:
                        self.reset_game()
                    else:
                        self.bird.flap()
            return True
        
        def update(self):
            if self.game_over:
                return
            
            self.frame_count += 1
            self.bird.update()
            
            if self.bird.is_off_screen():
                self.game_over = True
            
            if self.frame_count % PIPE_SPAWN_RATE == 0:
                self.pipes.append(Pipe(SCREEN_WIDTH))
            
            for pipe in self.pipes:
                pipe.update()
                
                if pipe.collides_with(self.bird):
                    self.game_over = True
                
                if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                    pipe.passed = True
                    self.score += 1
            
            self.pipes = [pipe for pipe in self.pipes if not pipe.is_off_screen()]
        
        def draw(self):
            self.screen.fill((135, 206, 235))
            
            for pipe in self.pipes:
                pipe.draw(self.screen)
            
            self.bird.draw(self.screen)
            
            score_text = self.font.render(f"Score: {self.score}", True, BLACK)
            self.screen.blit(score_text, (10, 10))
            
            if self.game_over:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(128)
                overlay.fill(BLACK)
                self.screen.blit(overlay, (0, 0))
                
                game_over_text = self.large_font.render("GAME OVER", True, RED)
                game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
                self.screen.blit(game_over_text, game_over_rect)
                
                final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
                final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(final_score_text, final_score_rect)
                
                restart_text = self.font.render("Press SPACE or CLICK to restart", True, CYAN)
                restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
                self.screen.blit(restart_text, restart_rect)
            
            pygame.display.flip()
        
        def run(self):
            running = True
            while running:
                running = self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(FPS)
            
            pygame.quit()
            sys.exit()

else:
    # Tkinter fallback version (no external dependencies)
    import tkinter as tk
    from tkinter import messagebox

    SCREEN_WIDTH = 400
    SCREEN_HEIGHT = 600
    FPS = 60
    GRAVITY = 0.5
    FLAP_STRENGTH = -10
    PIPE_WIDTH = 80
    PIPE_GAP = 120
    PIPE_SPEED = 5
    PIPE_SPAWN_RATE = 90

    class Bird:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.width = 30
            self.height = 30
            self.velocity = 0
        
        def flap(self):
            self.velocity = FLAP_STRENGTH
        
        def update(self):
            self.velocity += GRAVITY
            self.y += self.velocity
        
        def is_off_screen(self):
            return self.y > SCREEN_HEIGHT or self.y < 0
        
        def collides_with_pipe(self, pipe):
            bird_left = self.x
            bird_right = self.x + self.width
            bird_top = self.y
            bird_bottom = self.y + self.height
            
            # Check top pipe
            if bird_left < pipe.x + pipe.width and bird_right > pipe.x:
                if bird_top < pipe.gap_y:
                    return True
            
            # Check bottom pipe
            if bird_left < pipe.x + pipe.width and bird_right > pipe.x:
                if bird_bottom > pipe.gap_y + pipe.gap:
                    return True
            
            return False

    class Pipe:
        def __init__(self, x):
            self.x = x
            self.width = PIPE_WIDTH
            self.gap = PIPE_GAP
            self.gap_y = random.randint(50, SCREEN_HEIGHT - self.gap - 50)
            self.passed = False
        
        def update(self):
            self.x -= PIPE_SPEED
        
        def is_off_screen(self):
            return self.x + self.width < 0

    class Game:
        def __init__(self):
            self.root = tk.Tk()
            self.root.title("Flappy Bird Clone")
            self.root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")
            self.root.resizable(False, False)
            
            self.canvas = tk.Canvas(self.root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg="lightblue")
            self.canvas.pack()
            
            self.reset_game()
            
            self.root.bind("<space>", self.on_space)
            self.root.bind("<Button-1>", self.on_click)
            
            self.update_game()
        
        def reset_game(self):
            self.bird = Bird(50, SCREEN_HEIGHT // 2)
            self.pipes = []
            self.score = 0
            self.game_over = False
            self.frame_count = 0
        
        def on_space(self, event):
            if self.game_over:
                self.reset_game()
            else:
                self.bird.flap()
        
        def on_click(self, event):
            if self.game_over:
                self.reset_game()
            else:
                self.bird.flap()
        
        def update(self):
            if self.game_over:
                return
            
            self.frame_count += 1
            self.bird.update()
            
            if self.bird.is_off_screen():
                self.game_over = True
            
            if self.frame_count % PIPE_SPAWN_RATE == 0:
                self.pipes.append(Pipe(SCREEN_WIDTH))
            
            for pipe in self.pipes:
                pipe.update()
                
                if self.bird.collides_with_pipe(pipe):
                    self.game_over = True
                
                if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                    pipe.passed = True
                    self.score += 1
            
            self.pipes = [pipe for pipe in self.pipes if not pipe.is_off_screen()]
        
        def draw(self):
            self.canvas.delete("all")
            
            # Draw pipes
            for pipe in self.pipes:
                # Top pipe
                self.canvas.create_rectangle(pipe.x, 0, pipe.x + pipe.width, pipe.gap_y, fill="green")
                # Bottom pipe
                self.canvas.create_rectangle(pipe.x, pipe.gap_y + pipe.gap, pipe.x + pipe.width, SCREEN_HEIGHT, fill="green")
            
            # Draw bird
            self.canvas.create_oval(self.bird.x, self.bird.y, self.bird.x + self.bird.width, 
                                   self.bird.y + self.bird.height, fill="yellow", outline="black")
            # Draw eye
            self.canvas.create_oval(self.bird.x + 20, self.bird.y + 10, self.bird.x + 25, self.bird.y + 15, fill="black")
            
            # Draw score
            self.canvas.create_text(20, 20, text=f"Score: {self.score}", font=("Arial", 20), fill="black", anchor="nw")
            
            # Draw game over screen
            if self.game_over:
                self.canvas.create_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, fill="black", stipple="gray50")
                self.canvas.create_text(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60, text="GAME OVER", 
                                       font=("Arial", 48, "bold"), fill="red")
                self.canvas.create_text(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, text=f"Final Score: {self.score}", 
                                       font=("Arial", 20), fill="white")
                self.canvas.create_text(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60, text="Press SPACE or CLICK to restart", 
                                       font=("Arial", 16), fill="cyan")
        
        def update_game(self):
            self.update()
            self.draw()
            self.root.after(int(1000 / FPS), self.update_game)
        
        def run(self):
            self.root.mainloop()


if __name__ == "__main__":
    game = Game()
    game.run()
