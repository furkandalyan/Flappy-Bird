import pygame
import sys
import random
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird by Kanka")
clock = pygame.time.Clock()

# renkler
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# fontlar
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)

# klasör yolları
IMAGE_DIR = "pngs"
MUSIC_DIR = "musics"

# görseller
background_image = pygame.image.load(os.path.join(IMAGE_DIR, "background.png"))
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

bird_image = pygame.image.load(os.path.join(IMAGE_DIR, "bird.png")).convert_alpha()
bird_image = pygame.transform.scale(bird_image, (40, 40))

pipe_image = pygame.image.load(os.path.join(IMAGE_DIR, "pipe.png")).convert_alpha()
pipe_image = pygame.transform.scale(pipe_image, (70, 400))

# rakam PNG'leri
digit_images = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(IMAGE_DIR, f"{i}.png")).convert_alpha(),
        (24, 36)
    )
    for i in range(10)
]

# sesler
flap_sound  = pygame.mixer.Sound(os.path.join(MUSIC_DIR, "flap.wav"))
hit_sound   = pygame.mixer.Sound(os.path.join(MUSIC_DIR, "hit.wav"))
point_sound = pygame.mixer.Sound(os.path.join(MUSIC_DIR, "point.wav"))

# skor dosyası
high_score_file = "skor.txt"
if not os.path.exists(high_score_file):
    with open(high_score_file, "w") as f:
        f.write("0")

def load_high_score():
    with open(high_score_file, "r") as f:
        return int(f.read())

def save_high_score(score):
    with open(high_score_file, "w") as f:
        f.write(str(score))

# başlangıç değerleri
bird_x = 100
bird_y = HEIGHT // 2
bird_radius = 20
velocity = 0
gravity = 0.5
jump_power = -10

pipe_width = 70
pipe_gap = 150
pipe_x = WIDTH
pipe_speed = 3

def get_pipe_height():
    return random.randint(100, HEIGHT - pipe_gap - 100)

pipe_height = get_pipe_height()

score = 0
high_score = load_high_score()
game_state = "start"
passed_pipe = False

def reset_game():
    global bird_y, velocity, pipe_x, pipe_height, score, passed_pipe, game_state, high_score
    bird_y = HEIGHT // 2
    velocity = 0
    pipe_x = WIDTH
    pipe_height = get_pipe_height()
    score = 0
    passed_pipe = False
    game_state = "play"
    high_score = load_high_score()

def draw_score_png(score, x_start, y_top):
    for digit in str(score):
        screen.blit(digit_images[int(digit)], (x_start, y_top))
        x_start += 24

running = True
while running:
    screen.blit(background_image, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == "start":
                    reset_game()
                elif game_state == "play":
                    velocity = jump_power
                    flap_sound.play()
                elif game_state == "gameover":
                    reset_game()

    if game_state == "start":
        title      = font.render("Flappy Bird by Furkan", True, BLACK)
        start_text = small_font.render("SPACE ile başla", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 50))
        screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2 + 10))

    elif game_state == "play":
        velocity += gravity
        bird_y   += velocity

        pipe_x -= pipe_speed
        if pipe_x < -pipe_width:
            pipe_x = WIDTH
            pipe_height = get_pipe_height()
            passed_pipe = False

        # geçiş kontrolü
        if pipe_x + pipe_width < bird_x and not passed_pipe:
            score += 1
            passed_pipe = True
            point_sound.play()

        # çarpışma dikdörtgenleri
        bird_rect = pygame.Rect(bird_x - bird_radius,
                                bird_y - bird_radius,
                                bird_radius*2, bird_radius*2)

        top_pipe = pygame.transform.flip(pipe_image, False, True)
        top_pipe_crop = top_pipe.subsurface((0, 400-pipe_height, 70, pipe_height))
        screen.blit(top_pipe_crop, (pipe_x, 0))

        bottom_pipe_crop = pipe_image.subsurface((0, 0, 70, HEIGHT-(pipe_height+pipe_gap)))
        screen.blit(bottom_pipe_crop, (pipe_x, pipe_height + pipe_gap))

        top_pipe_rect = pygame.Rect(pipe_x, 0, pipe_width, pipe_height)
        bottom_pipe_rect = pygame.Rect(pipe_x, pipe_height+pipe_gap, pipe_width, HEIGHT)

        if (bird_rect.colliderect(top_pipe_rect) or
            bird_rect.colliderect(bottom_pipe_rect) or
            bird_y >= HEIGHT - bird_radius or
            bird_y <= bird_radius):
            hit_sound.play()
            game_state = "gameover"
            if score > high_score:
                save_high_score(score)
                high_score = score

        screen.blit(bird_image, (bird_x-20, int(bird_y)-20))
        draw_score_png(score, WIDTH//2 - (len(str(score))*12), 20)

    elif game_state == "gameover":
        over_text     = font.render("GAME OVER", True, RED)
        restart_text  = small_font.render("SPACE ile yeniden başla", True, BLACK)

        label_x       = WIDTH//2 - 100
        score_y       = HEIGHT//2 - 90
        highscore_y   = HEIGHT//2 - 40

        score_text      = small_font.render("Skor:", True, BLACK)
        high_score_text = small_font.render("Yüksek Skor:", True, BLACK)

        screen.blit(score_text,      (label_x, score_y))
        screen.blit(high_score_text, (label_x, highscore_y))

        draw_score_png(score,
                       label_x + score_text.get_width() + 10,
                       score_y - 10)
        draw_score_png(high_score,
                       label_x + high_score_text.get_width() + 10,
                       highscore_y - 10)

        screen.blit(over_text,    (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 + 30))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 70))

    pygame.display.update()
    clock.tick(60)
