import pygame
import time
import random
import os
import asyncio
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Astro Dodge")

HIGH_SCORE_FILE = "/Users/bhabishya/newpygame/high_score.txt"

clock = pygame.time.Clock()
BG = pygame.transform.scale(pygame.image.load("stars.png"), (WIDTH, HEIGHT)).convert()

pygame.mixer.music.load("space-ranger-moire-main-version-03-04-10814.mp3")
pygame.mixer.music.set_volume(0.7)
pygame.mixer.music.play(-1)

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_VELOCITY = 5
PLAYER_IMAGE = pygame.image.load("rocket.png")
PLAYER_IMAGE = pygame.transform.scale(PLAYER_IMAGE, (PLAYER_WIDTH, PLAYER_HEIGHT))
PLAYER_MASK = pygame.mask.from_surface(PLAYER_IMAGE)



FONT = pygame.font.SysFont("Orbitron", 50)


if not os.path.exists(HIGH_SCORE_FILE):
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write("0")

STAR_WIDTH = 30
STAR_HEIGHT = 30
STAR_VELOCITY = 3
STAR_IMAGE = pygame.image.load("asteroid.png")
STAR_IMAGE = pygame.transform.scale(STAR_IMAGE, (STAR_WIDTH, STAR_HEIGHT)) 
STAR_MASK = pygame.mask.from_surface(STAR_IMAGE)


def load_high_score():
    with open(HIGH_SCORE_FILE, "r") as file:
        try:
            return int(file.read().strip())
        except ValueError:
            return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write(str(score))

def help(win):
    help_width, help_height = 800, 400
    help_rect = pygame.Rect((WIDTH // 2 - help_width // 2, HEIGHT // 2 - help_height // 2), (help_width, help_height))
    pygame.draw.rect(win, (50, 50, 50), help_rect)
    paused_text = FONT.render("Game Paused", True, "white")
    WIN.blit(paused_text, (WIDTH // 2 - paused_text.get_width() // 2, HEIGHT // 2 - 80))
    resume_text = FONT.render("Press P to Resume", True, "white")
    win.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 20))

    how_to_play_text = FONT.render("Press an arrow key to move in that direction", True, "white")
    win.blit(how_to_play_text, (WIDTH // 2 - how_to_play_text.get_width() // 2, HEIGHT // 2 - 30))

    quit_text = FONT.render("Press Q to Quit", True, "white")
    win.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 60))

    pygame.display.update()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p: 
                    return True  
                if event.key == pygame.K_q:  
                    pygame.quit()
                    quit()

def draw(player, elapsed_time, stars, high_score, bg_y):
    WIN.blit(BG, (0, bg_y))
    WIN.blit(BG, (0, bg_y - HEIGHT)) 
    WIN.blit(PLAYER_IMAGE, (player.x, player.y))
    for star in stars:
        WIN.blit(STAR_IMAGE, (star.x, star.y))  
    time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, "white")
    WIN.blit(time_text, (10, 10))
    high_score_text = FONT.render(f"High Score: {int(high_score)}s", 1, "white")
    WIN.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))
    help_text = FONT.render("?", 1, "white")
    WIN.blit(help_text, (960, 765)) 
    pygame.display.update()

async def main():
    high_score = load_high_score()
    player = pygame.Rect(470, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0
    star_add_increment = 2000
    star_count = 0
    stars = []
    hit = False
    bg_y = 0
    paused = False  

    while True:
        star_count += clock.tick(60)
        elapsed_time = time.time() - start_time

        if star_count > star_add_increment:
            for _ in range(3):
                star_x = random.randint(0, WIDTH - STAR_WIDTH)
                star = pygame.Rect(star_x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT)
                stars.append(star)
            star_add_increment = max(200, star_add_increment - 50)
            star_count = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
           
           
                if 960 <= mouse_pos[0] <= 1000 and 765 <= mouse_pos[1] <= 800:
                    paused = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p: 
                    paused = not paused

        if paused:
            if help(WIN): 
                paused = False 
            continue  

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - PLAYER_VELOCITY >= 0:
            player.x -= PLAYER_VELOCITY
        if keys[pygame.K_RIGHT] and player.x + PLAYER_VELOCITY + player.width <= WIDTH:
            player.x += PLAYER_VELOCITY
        if keys[pygame.K_UP] and player.y - PLAYER_VELOCITY >= 0:
            player.y -= PLAYER_VELOCITY
        if keys[pygame.K_DOWN] and player.y + PLAYER_VELOCITY + player.height <= HEIGHT:
            player.y += PLAYER_VELOCITY

        for star in stars[:]:
            star.y += STAR_VELOCITY
            if star.y > HEIGHT:
                stars.remove(star)
            else:  
                offset = (star.x - player.x, star.y - player.y)
                if PLAYER_MASK.overlap(STAR_MASK, offset): 
                    hit = True
                    break



        if hit:
            if elapsed_time > high_score:
                high_score = elapsed_time
                save_high_score(int(high_score))
            while True:
                lost_text = FONT.render("YOU LOSE!!!", 1, "white")
                WIN.blit(lost_text, (WIDTH // 2 - lost_text.get_width() // 2, HEIGHT // 2 - lost_text.get_height() // 2))
                high_score_text = FONT.render(f"High Score: {int(high_score)}s", 1, "green")
                WIN.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 + 50))
                score_text = FONT.render(f"Your Score: {int(elapsed_time)}s", 1, "orange")
                WIN.blit(score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 + 100))
                restart_font = pygame.font.Font(None, 36)
                restart_text = restart_font.render("Restart", True, "white")
                WIN.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 140))
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if (WIDTH // 2 - restart_text.get_width() // 2 <= mouse_pos[0] <= WIDTH // 2 + restart_text.get_width() // 2 and
                                HEIGHT // 2 + 140 <= mouse_pos[1] <= HEIGHT // 2 + 140 + restart_text.get_height()):
                            await main()
                            return

        bg_y += 1
        if bg_y >= HEIGHT:
            bg_y = 0

        draw(player, elapsed_time, stars, high_score, bg_y)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())
