import pygame
import random
import math

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Cosmic Block Breaker")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
CYAN = (0, 255, 255)
PURPLE = (150, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 150, 0)

clock = pygame.time.Clock()

title_font = pygame.font.SysFont('Arial', 36)
score_font = pygame.font.SysFont('Arial', 24)

paddle_width = 100
paddle_height = 15
paddle_speed = 10
ball_radius = 10
ball_speed_x = 4
ball_speed_y = 4
block_width = 60
block_height = 20
block_margin = 5
score = 0
lives = 3


particles = []

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        self.life = random.randint(20, 40)
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size -= 0.1
        return self.life <= 0 or self.size <= 0
        
    def draw(self, surface):
        if self.size > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

class Star:
    def __init__(self):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.size = random.uniform(0.5, 2)
        self.speed = random.uniform(0.2, 0.8)
        self.brightness = random.randint(100, 255)
        
    def update(self):
        self.y += self.speed
        self.brightness += random.randint(-5, 5)
        self.brightness = max(100, min(255, self.brightness))
        if self.y > screen_height:
            self.y = 0
            self.x = random.randint(0, screen_width)
            
    def draw(self, surface):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size))

stars = [Star() for _ in range(100)]

class Paddle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = paddle_width
        self.image = pygame.Surface((self.width, paddle_height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.create_gradient()
        
    def create_gradient(self):
        for i in range(self.width):
            r = int(0 + (0 - 0) * i / self.width)
            g = int(100 + (255 - 100) * i / self.width)
            b = int(255)
            pygame.draw.line(self.image, (r, g, b), (i, 0), (i, paddle_height))
        
        glow_surf = pygame.Surface((self.width + 10, paddle_height + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (0, 150, 255, 100), (0, 0, self.width + 10, paddle_height + 10), 0, 10)
        self.image.blit(glow_surf, (-5, -5), special_flags=pygame.BLEND_RGBA_ADD)

    def update(self, move_left, move_right):
        if move_left and self.rect.left > 0:
            self.rect.x -= paddle_speed
        if move_right and self.rect.right < screen_width:
            self.rect.x += paddle_speed

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.radius = ball_radius
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.draw_ball()
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, screen_height // 2)
        self.speed_x = ball_speed_x
        self.speed_y = ball_speed_y
        self.true_x = self.rect.x
        self.true_y = self.rect.y
        self.timer = 0
        
    def draw_ball(self):
        pygame.draw.circle(self.image, CYAN, (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.image, WHITE, (self.radius - 2, self.radius - 2), self.radius // 3)
        
    def update(self):
        self.timer += 1
        self.true_x += self.speed_x
        self.true_y += self.speed_y
        self.rect.x = int(self.true_x)
        self.rect.y = int(self.true_y)
        if self.timer % 2 == 0:
            particles.append(Particle(self.rect.centerx, self.rect.centery, CYAN))
        if self.rect.left <= 0 or self.rect.right >= screen_width:
            self.speed_x = -self.speed_x
            for _ in range(10):
                particles.append(Particle(self.rect.centerx, self.rect.centery, CYAN))
            self.speed_x *= 1.01  

        if self.rect.top <= 0:
            self.speed_y = -self.speed_y
            for _ in range(10):
                particles.append(Particle(self.rect.centerx, self.rect.centery, CYAN))
            self.speed_y *= 1.01 
        if self.rect.bottom >= screen_height:
            return True  
        
        return False
    
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, color_index):
        super().__init__()
        self.image = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.color_index = color_index
        self.colors = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE]
        self.color = self.colors[color_index % len(self.colors)]
        
        for i in range(block_width):
            # Gradient within the color family
            r = int(self.color[0] * (0.8 + 0.2 * i / block_width))
            g = int(self.color[1] * (0.8 + 0.2 * i / block_width))
            b = int(self.color[2] * (0.8 + 0.2 * i / block_width))
            pygame.draw.line(self.image, (r, g, b), (i, 0), (i, block_height))
        pygame.draw.rect(self.image, (255, 255, 255, 150), (0, 0, block_width, 3))
        
        glow_surf = pygame.Surface((block_width + 6, block_height + 6), pygame.SRCALPHA)
        r, g, b = self.color
        pygame.draw.rect(glow_surf, (r, g, b, 100), (0, 0, block_width + 6, block_height + 6), 0, 5)
        self.image.blit(glow_surf, (-3, -3), special_flags=pygame.BLEND_RGBA_ADD)
        
    def get_points(self):
        return (self.color_index + 1) * 10
class Bumper(pygame.sprite.Sprite):
    def __init__(self, x, y, radius):
        super().__init__()
        self.radius = radius
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.timer = 0
        self.active = False
        self.draw_bumper()
        
    def draw_bumper(self):
        if self.active:
            pygame.draw.circle(self.image, YELLOW, (self.radius, self.radius), self.radius)
            pygame.draw.circle(self.image, WHITE, (self.radius, self.radius), self.radius - 3)
        else:
            pygame.draw.circle(self.image, ORANGE, (self.radius, self.radius), self.radius)
            pygame.draw.circle(self.image, RED, (self.radius, self.radius), self.radius - 3)
            
    def update(self):
        if self.active:
            self.timer += 1
            if self.timer > 5:
                self.active = False
                self.timer = 0
                self.draw_bumper()
class AIController:
    def __init__(self, ball, paddle, difficulty="medium"):
        self.ball = ball
        self.paddle = paddle
        self.difficulty = difficulty
        self.prediction_accuracy = self.set_difficulty(difficulty)
        self.reaction_delay = 0
        self.move_left = False
        self.move_right = False
        self.target_x = 0
        self.last_decision_time = 0
        
    def set_difficulty(self, difficulty):
        if difficulty == "easy":
            return 0.7 
        elif difficulty == "medium":
            return 0.85  
        elif difficulty == "hard":
            return 0.95  
        else:
            return 0.85  
            
    def predict_ball_position(self):
        if self.ball.speed_y > 0:
            time_to_reach = (self.paddle.rect.top - self.ball.rect.bottom) / self.ball.speed_y
            
            if time_to_reach > 0:
                predicted_x = self.ball.rect.centerx + (self.ball.speed_x * time_to_reach)
                error_margin = random.uniform(-100, 100) * (1 - self.prediction_accuracy)
                predicted_x += error_margin
                predicted_x = max(0, min(predicted_x, screen_width))
                
                return predicted_x
        return self.ball.rect.centerx
    
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_decision_time > 50: 
            self.last_decision_time = current_time
            self.target_x = self.predict_ball_position()
            self.move_left = False
            self.move_right = False
            paddle_center = self.paddle.rect.centerx
            if self.target_x < paddle_center - 10:
                self.move_left = True
            elif self.target_x > paddle_center + 10:
                self.move_right = True
                
            if random.random() > self.prediction_accuracy:
                self.move_left, self.move_right = self.move_right, self.move_left

MENU = 0
MODE_SELECT = 1  
PLAYING = 2
GAME_OVER = 3
LEVEL_COMPLETE = 4
game_state = MENU

HUMAN_MODE = 0
AI_MODE = 1
game_mode = HUMAN_MODE

def create_blocks():
    blocks = pygame.sprite.Group()
    for row in range(5):  
        for col in range(10):  
            block = Block(
                col * (block_width + block_margin) + 50, 
                row * (block_height + block_margin) + 50,
                row  
            )
            blocks.add(block)
    return blocks

def reset_ball():
    ball.rect.center = (screen_width // 2, screen_height // 2)
    ball.true_x = ball.rect.x
    ball.true_y = ball.rect.y
    ball.speed_x = random.choice([-1, 1]) * ball_speed_x
    ball.speed_y = ball_speed_y

def draw_game_background():
    for star in stars:
        star.update()
        star.draw(screen)

def draw_ui():
    score_text = score_font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, 10))
    lives_text = score_font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(lives_text, (screen_width - 120, 10))
    if game_mode == AI_MODE:
        mode_text = score_font.render("AI Mode", True, CYAN)
        screen.blit(mode_text, (screen_width // 2 - mode_text.get_width() // 2, 10))

paddle = Paddle(screen_width // 2, screen_height - 50)
ball = Ball()
ai_controller = AIController(ball, paddle, "medium")
blocks = create_blocks()
bumpers = pygame.sprite.Group()
bumpers.add(Bumper(150, 300, 20))
bumpers.add(Bumper(400, 250, 20))
bumpers.add(Bumper(650, 300, 20))
all_sprites = pygame.sprite.Group()
all_sprites.add(paddle)
all_sprites.add(ball)
running = True
move_left = move_right = False
while running:
    screen.fill((5, 5, 20))
    draw_game_background()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == PLAYING and game_mode == HUMAN_MODE:
                if event.key == pygame.K_LEFT:
                    move_left = True
                if event.key == pygame.K_RIGHT:
                    move_right = True
            if event.key == pygame.K_SPACE:
                if game_state == MENU:
                    game_state = MODE_SELECT
                elif game_state == MODE_SELECT:
                    game_state = PLAYING
                elif game_state == GAME_OVER or game_state == LEVEL_COMPLETE:
                    score = 0
                    lives = 3
                    blocks = create_blocks()
                    reset_ball()
                    game_state = MODE_SELECT
            if game_state == MODE_SELECT:
                if event.key == pygame.K_1:
                    game_mode = HUMAN_MODE
                    game_state = PLAYING
                elif event.key == pygame.K_2:
                    game_mode = AI_MODE
                    game_state = PLAYING
        
        if event.type == pygame.KEYUP and game_mode == HUMAN_MODE:
            if event.key == pygame.K_LEFT:
                move_left = False
            if event.key == pygame.K_RIGHT:
                move_right = False

    if game_state == MENU:
        title = title_font.render("Cosmic Block Breaker", True, CYAN)
        screen.blit(title, (screen_width//2 - title.get_width()//2, 200))
        
        instruction = score_font.render("Press SPACE to start", True, WHITE)
        screen.blit(instruction, (screen_width//2 - instruction.get_width()//2, 300))
        if random.random() < 0.2:
            particles.append(Particle(random.randint(0, screen_width), 
                                     random.randint(0, screen_height),
                                     random.choice([RED, YELLOW, CYAN, PURPLE])))
    
    elif game_state == MODE_SELECT:
        title = title_font.render("SELECT GAME MODE", True, YELLOW)
        screen.blit(title, (screen_width//2 - title.get_width()//2, 150))
        
        human_option = score_font.render("1: Play as Human", True, WHITE)
        screen.blit(human_option, (screen_width//2 - human_option.get_width()//2, 250))
        
        ai_option = score_font.render("2: Let AI Play", True, WHITE)
        screen.blit(ai_option, (screen_width//2 - ai_option.get_width()//2, 300))
        if random.random() < 0.1:
            particles.append(Particle(random.randint(0, screen_width), 
                                     random.randint(0, screen_height),
                                     random.choice([GREEN, CYAN, YELLOW])))
    
    elif game_state == PLAYING:
        if game_mode == HUMAN_MODE:
            paddle.update(move_left, move_right)
        else:  
            ai_controller.update()
            paddle.update(ai_controller.move_left, ai_controller.move_right)
        
        if ball.update():
            lives -= 1
            if lives <= 0:
                game_state = GAME_OVER
            else:
                reset_ball()
        
        if pygame.sprite.collide_rect(ball, paddle):
            ball.speed_y = -abs(ball.speed_y)  
            relative_position = (ball.rect.centerx - paddle.rect.centerx) / (paddle_width / 2)
            
            ball.speed_x = relative_position * 8
            
            for _ in range(10):
                particles.append(Particle(ball.rect.centerx, ball.rect.bottom, CYAN))
        
        for bumper in bumpers:
            
            dx = ball.rect.centerx - bumper.rect.centerx
            dy = ball.rect.centery - bumper.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < ball.radius + bumper.radius:
                angle = math.atan2(dy, dx)
                power = 1.2  
                
                ball.speed_x = math.cos(angle) * 6 * power
                ball.speed_y = math.sin(angle) * 6 * power
                
                bumper.active = True
                bumper.draw_bumper()
                score += 15
                
                for _ in range(15):
                    particles.append(Particle(ball.rect.centerx, ball.rect.centery, YELLOW))
        
        bumpers.update()
        
        block_hits = pygame.sprite.spritecollide(ball, blocks, True)
        
        for block in block_hits:
            score += block.get_points()
            
            for _ in range(15):
                particles.append(Particle(ball.rect.centerx, ball.rect.centery, block.color))
            
            block_center_x = block.rect.x + block_width/2
            block_center_y = block.rect.y + block_height/2
            
            if abs(ball.rect.centery - block_center_y) > abs(ball.rect.centerx - block_center_x):
                ball.speed_y = -ball.speed_y
            else:
                ball.speed_x = -ball.speed_x
        
        max_speed = 15
        if abs(ball.speed_x) > max_speed:
            ball.speed_x = max_speed if ball.speed_x > 0 else -max_speed
        if abs(ball.speed_y) > max_speed:
            ball.speed_y = max_speed if ball.speed_y > 0 else -max_speed
        
        if len(blocks) == 0:
            game_state = LEVEL_COMPLETE
        
        blocks.draw(screen)
        bumpers.draw(screen)
        all_sprites.draw(screen)
        
        if game_mode == AI_MODE:
            pygame.draw.line(screen, GREEN, (ai_controller.target_x, paddle.rect.top - 5),
                          (ai_controller.target_x, paddle.rect.top), 2)
        draw_ui()
    
    elif game_state == GAME_OVER:
        game_over_text = title_font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (screen_width//2 - game_over_text.get_width()//2, 200))
        
        score_text = score_font.render(f"Final Score: {score}", True, WHITE)
        screen.blit(score_text, (screen_width//2 - score_text.get_width()//2, 280))
        
        restart_text = score_font.render("Press SPACE to play again", True, WHITE)
        screen.blit(restart_text, (screen_width//2 - restart_text.get_width()//2, 340))
    
    elif game_state == LEVEL_COMPLETE:
        complete_text = title_font.render("LEVEL COMPLETE!", True, YELLOW)
        screen.blit(complete_text, (screen_width//2 - complete_text.get_width()//2, 200))
        
        score_text = score_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (screen_width//2 - score_text.get_width()//2, 280))
        
        restart_text = score_font.render("Press SPACE to play again", True, WHITE)
        screen.blit(restart_text, (screen_width//2 - restart_text.get_width()//2, 340))
    for particle in particles[:]:
        if particle.update():
            particles.remove(particle)
        else:
            particle.draw(screen)
    if len(particles) > 200:
        particles = particles[-200:]
    pygame.display.flip()
    clock.tick(60)
pygame.quit()