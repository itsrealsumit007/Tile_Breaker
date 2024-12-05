import pygame
import sys
import random

pygame.init()

width = 800
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Tile Breaker')

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
orange = (255, 165, 0)
purple = (128, 0, 128)
cyan = (0, 255, 255)
pink = (255, 192, 203)

font = pygame.font.Font(None, 36)

paddle_width = 100
paddle_height = 10
paddle_color = blue
paddle_x = (width - paddle_width) // 2
paddle_y = height - 30
paddle_speed = 10

ball_size = 10
ball_color = white
ball_x = width // 2
ball_y = height // 2
ball_speed_x = 4
ball_speed_y = -4

tile_width = 60
tile_height = 20
tiles = []

score = 0
level = 1
lives = 3
power_ups = []
game_state = "menu"
high_score = 0
power_up_types = ["extend", "shrink", "speed_up", "slow_down", "multi_ball"]
balls = []
is_paused = False

def create_tiles():
    global tiles
    tiles = []
    for row in range(5):
        for col in range(10):
            tile = pygame.Rect(
                col * (tile_width + 10) + 35,
                row * (tile_height + 10) + 50,
                tile_width,
                tile_height
            )
            tiles.append(tile)

create_tiles()

def reset_ball():
    global ball_x, ball_y, ball_speed_y
    ball_x = width // 2
    ball_y = height // 2
    ball_speed_y = -4

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def create_power_up(x, y):
    power_up = pygame.Rect(x, y, 20, 20)
    power_ups.append(power_up)

def handle_power_ups():
    global paddle_width
    for power_up in power_ups[:]:
        power_up.y += 5
        if power_up.colliderect(paddle):
            power_ups.remove(power_up)
            power_type = random.choice(power_up_types)
            
            if power_type == "extend":
                paddle_width = min(paddle_width + 20, width // 2)
            elif power_type == "shrink":
                paddle_width = max(paddle_width - 20, 40)
            elif power_type == "speed_up":
                for ball in balls:
                    ball['speed_x'] *= 1.2
                    ball['speed_y'] *= 1.2
            elif power_type == "slow_down":
                for ball in balls:
                    ball['speed_x'] *= 0.8
                    ball['speed_y'] *= 0.8
            elif power_type == "multi_ball":
                new_ball = create_ball()
                new_ball['speed_x'] *= -1
                balls.append(new_ball)
        elif power_up.y > height:
            power_ups.remove(power_up)
        pygame.draw.rect(screen, yellow, power_up)

def create_ball():
    return {
        'rect': pygame.Rect(width // 2, height // 2, ball_size, ball_size),
        'speed_x': ball_speed_x,
        'speed_y': ball_speed_y
    }

def init_game():
    global score, level, lives, paddle_width, balls, tiles, power_ups
    score = 0
    level = 1
    lives = 3
    paddle_width = 100
    balls = [create_ball()]
    power_ups = []
    create_tiles()

def draw_menu():
    screen.fill(black)
    title = pygame.font.Font(None, 74).render('TILE BREAKER', True, cyan)
    title_rect = title.get_rect(center=(width // 2, height // 4))
    screen.blit(title, title_rect)
    
    draw_text('Press ENTER to Start', font, white, screen, width // 2, height // 2)
    draw_text('Press H for Help', font, white, screen, width // 2, height // 2 + 50)
    draw_text(f'High Score: {high_score}', font, yellow, screen, width // 2, height // 2 + 100)

def draw_help():
    screen.fill(black)
    help_texts = [
        "HOW TO PLAY",
        "Use LEFT and RIGHT arrows to move the paddle",
        "Break all tiles to advance to next level",
        "Collect power-ups for special effects:",
        "YELLOW - Extend paddle",
        "RED - Shrink paddle",
        "GREEN - Speed up ball",
        "BLUE - Slow down ball",
        "PURPLE - Multi-ball",
        "",
        "Press ESCAPE to return to menu"
    ]
    
    for i, text in enumerate(help_texts):
        draw_text(text, font, white, screen, width // 2, 100 + i * 40)

playing = True
while playing:
    if game_state == "menu":
        screen.fill(black)
        draw_menu()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = "playing"
                    init_game()
                elif event.key == pygame.K_h:
                    game_state = "help"

    elif game_state == "help":
        draw_help()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = "menu"

    elif game_state == "playing":
        if not is_paused:
            screen.fill(black)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and paddle_x > 0:
                paddle_x -= paddle_speed
            if keys[pygame.K_RIGHT] and paddle_x < width - paddle_width:
                paddle_x += paddle_speed

            for ball in balls:
                ball['rect'].x += ball['speed_x']
                ball['rect'].y += ball['speed_y']

                if ball['rect'].x <= 0 or ball['rect'].x >= width - ball_size:
                    ball['speed_x'] *= -1
                if ball['rect'].y <= 0:
                    ball['speed_y'] *= -1
                if ball['rect'].y >= height:
                    balls.remove(ball)
                    if not balls:
                        lives -= 1
                        if lives > 0:
                            balls.append(create_ball())
                        else:
                            game_state = "game_over"  # Transition to game over screen

            paddle = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)
            for ball in balls:
                if ball['rect'].colliderect(paddle):
                    ball['speed_y'] *= -1

            for tile in tiles[:]:
                for ball in balls:
                    if ball['rect'].colliderect(tile):
                        tiles.remove(tile)
                        score += 10
                        ball['speed_y'] *= -1
                        if random.randint(1, 10) == 1:
                            create_power_up(tile.x + tile_width // 2, tile.y + tile_height // 2)
                        break

            if not tiles:
                level += 1
                ball_speed_x *= 1.1
                ball_speed_y *= 1.1
                create_tiles()
                balls = [create_ball()]

            handle_power_ups()

            pygame.draw.rect(screen, paddle_color, paddle)
            for ball in balls:
                pygame.draw.ellipse(screen, ball_color, ball['rect'])

            for tile in tiles:
                pygame.draw.rect(screen, random.choice([red, green, yellow]), tile)

            draw_text(f'Score: {score}', font, white, screen, width // 8, 20)
            draw_text(f'Level: {level}', font, white, screen, width // 2, 20)
            draw_text(f'Lives: {lives}', font, white, screen, 7 * width // 8, 20)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    is_paused = not is_paused
                elif event.key == pygame.K_ESCAPE:
                    game_state = "menu"

        if is_paused:
            draw_text('PAUSED', font, white, screen, width // 2, height // 2)
            draw_text('Press P to Resume', font, white, screen, width // 2, height // 2 + 50)

    pygame.display.flip()
    pygame.time.Clock().tick(60)

if score > high_score:
    high_score = score

# Game Over Screen
game_over = True
while game_over:
    screen.fill(black)
    draw_text('Game Over', font, red, screen, width // 2, height // 2)
    draw_text(f'Final Score: {score}', font, white, screen, width // 2, height // 2 + 50)
    if score == high_score:
        draw_text('NEW HIGH SCORE!', font, yellow, screen, width // 2, height // 2 + 100)
    draw_text('Press Space to Return to Menu', font, white, screen, width // 2, height // 2 + 150)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_state = "menu"
                game_over = False

pygame.quit()
sys.exit()
