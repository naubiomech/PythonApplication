import pygame
import os
import random
import sys

# Allow joystick events in background
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"

# Initialize Pygame and Joystick Support
pygame.init()
pygame.joystick.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Balloon Blower Game")

# Colors
PURPLE = (68, 26, 134)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = (135, 206, 235)
LIGHT_PURPLE = (220, 208, 255)
DARK_PURPLE = (48, 16, 114)
GRAY = (200, 200, 200)

# Get directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load balloon frames
frames = []
sprite_folder = os.path.join(BASE_DIR, "sprites")
for i in range(1, 9):
    frame_path = os.path.join(sprite_folder, f"Sprite-Balloon{i}.png")
    if os.path.exists(frame_path):
        frame = pygame.image.load(frame_path).convert_alpha()
        frame = pygame.transform.scale(frame, (WIDTH, HEIGHT))
        frames.append(frame)

# Load sounds
sound_folder = os.path.join(BASE_DIR, "sounds")
inflate_sound_path = os.path.join(sound_folder, "inflate.wav")
ding_sound_path = os.path.join(sound_folder, "ding.wav")

inflate_sound = pygame.mixer.Sound(inflate_sound_path) if os.path.exists(inflate_sound_path) else None
ding_sound = pygame.mixer.Sound(ding_sound_path) if os.path.exists(ding_sound_path) else None
if inflate_sound:
    inflate_sound.set_volume(0.1)
if ding_sound:
    ding_sound.set_volume(0.5)

# Load and pause background music immediately (muted by default)
bg_music_path = os.path.join(sound_folder, "background.mp3")
if os.path.exists(bg_music_path):
    pygame.mixer.music.load(bg_music_path)
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.pause()   # Immediately pause music so it's muted on start

# Fonts
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 72)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font_type=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.is_hovered = False
        self.font = font_type if font_type else font

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.current_color = self.hover_color if self.is_hovered else self.color
        return self.is_hovered

    def check_click(self, mouse_pos, just_clicked):
        return self.rect.collidepoint(mouse_pos) and just_clicked

# Game state
game_state = "menu"
balloon_full = False
balloon_count = 0
balloon_fully_inflated = False
is_paused = False
is_muted = True  # Start muted by default (background music & inflate sound)
mouse_was_pressed = False

frame_index = 0
max_frames = len(frames) - 1
intensity = 0
min_threshold = -0.7
intensity_bar_width = 300
intensity_bar_height = 15

confetti_particles = []
congrats_display_timer = 0

# Joystick setup
joystick = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
if joystick:
    joystick.init()
LT_AXIS = 4
RT_AXIS = 5
expected_trigger = "RIGHT"  # Start with LEFT

# Buttons
play_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 60, "PLAY", GREEN, (100, 255, 100))
exit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 60, "EXIT", (255, 100, 100), (255, 150, 150))
settings_buttons = [
    Button(WIDTH - 110, HEIGHT - 50, 90, 30, "Settings", GRAY, (230, 230, 230), small_font),
    Button(WIDTH - 110, HEIGHT - 90, 90, 30, "Pause", GRAY, (230, 230, 230), small_font),
    Button(20, HEIGHT - 50, 90, 30, "Menu", GRAY, (230, 230, 230), small_font)
]
mute_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 30, 200, 50, "Mute Music & Inflate", GRAY, (220, 220, 220))
back_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 40, 200, 50, "Back", GRAY, (220, 220, 220))

clock = pygame.time.Clock()

def run_menu(just_clicked):
    global game_state
    screen.fill(LIGHT_PURPLE)
    title_text = title_font.render("Balloon Blower", True, PURPLE)
    screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3)))
    play_button.draw(screen)
    exit_button.draw(screen)
    mouse_pos = pygame.mouse.get_pos()
    play_button.check_hover(mouse_pos)
    exit_button.check_hover(mouse_pos)
    if play_button.check_click(mouse_pos, just_clicked):
        game_state = "game"
        if not is_muted:
            pygame.mixer.music.unpause()
    elif exit_button.check_click(mouse_pos, just_clicked):
        pygame.quit()
        sys.exit()

def run_settings(just_clicked):
    global game_state, is_muted
    screen.fill(LIGHT_PURPLE)
    title = title_font.render("Settings", True, PURPLE)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 4)))
    mute_button.text = "Unmute Music" if is_muted else "Mute Music"
    mute_button.draw(screen)
    back_button.draw(screen)
    mouse_pos = pygame.mouse.get_pos()
    mute_button.check_hover(mouse_pos)
    back_button.check_hover(mouse_pos)
    if mute_button.check_click(mouse_pos, just_clicked):
        is_muted = not is_muted
        if is_muted:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
    if back_button.check_click(mouse_pos, just_clicked):
        game_state = "game"

def run_game(just_clicked):
    global frame_index, intensity, balloon_full, congrats_display_timer
    global balloon_fully_inflated, balloon_count, expected_trigger, game_state, is_paused

    # Reset balloon state after celebration ends
    if congrats_display_timer > 0:
        current_time = pygame.time.get_ticks()
        if current_time - congrats_display_timer > 500:
            balloon_full = False
            balloon_fully_inflated = False
            frame_index = 0
            intensity = 0
            congrats_display_timer = 0
            confetti_particles.clear()

            # Alternate expected trigger between LEFT and RIGHT
            expected_trigger = "RIGHT" 

    # Fill background based on pause state
    screen.fill(DARK_PURPLE if is_paused else LIGHT_BLUE)
    
    if frames and not is_paused:
        screen.blit(frames[frame_index], (0, 0))
    
    if not is_paused:
        counter_text = font.render(f"Balloons Blown: {balloon_count}", True, BLACK)
        screen.blit(counter_text, (20, 20))

        # Draw intensity bar
        intensity_bar_x = WIDTH - intensity_bar_width - 20
        intensity_bar_y = 20
        pygame.draw.rect(screen, BLACK, (intensity_bar_x, intensity_bar_y, intensity_bar_width, intensity_bar_height), 2)
        pygame.draw.rect(screen, PURPLE, (intensity_bar_x, intensity_bar_y, (intensity / 100) * intensity_bar_width, intensity_bar_height))
        intensity_text = font.render(f"Intensity: {int(intensity)}%", True, BLACK)
        screen.blit(intensity_text, (
            intensity_bar_x + (intensity_bar_width - intensity_text.get_width()) // 2,
            intensity_bar_y + intensity_bar_height + 5))

        # Instructions
        text_message = f"Press {expected_trigger} to inflate the balloon!"
        outline_text = font.render(text_message, True, BLACK)
        main_text = font.render(text_message, True, PURPLE)
        text_x = WIDTH // 2 - outline_text.get_width() // 2
        text_y = HEIGHT - 60
        padding = 10
        pygame.draw.rect(screen, WHITE, (text_x - padding, text_y - padding,
                                         outline_text.get_width() + 2 * padding, outline_text.get_height() + 2 * padding))
        pygame.draw.rect(screen, BLACK, (text_x - padding, text_y - padding,
                                         outline_text.get_width() + 2 * padding, outline_text.get_height() + 2 * padding), 2)
        screen.blit(main_text, (text_x, text_y))

        # Handle trigger input
        if joystick and congrats_display_timer == 0:
            lt = joystick.get_axis(LT_AXIS)
            current_trigger = lt if expected_trigger == "LEFT" else lt

            # Normalize trigger value (support 0–1 or -1–1 ranges)
            if current_trigger < 0:
                normalized_intensity = ((current_trigger + 1) / 2) * 100
            else:
                normalized_intensity = current_trigger * 100

            if normalized_intensity > 10:  # Minimum threshold to start inflating
                intensity = round(normalized_intensity)
                new_frame_index = min(int((intensity / 100) * max_frames), max_frames)
                if new_frame_index > frame_index and inflate_sound and not is_muted:
                    if not pygame.mixer.get_busy():
                        inflate_sound.play()
                frame_index = new_frame_index
                if intensity >= 99 and not balloon_full:
                    balloon_full = True
                    congrats_display_timer = pygame.time.get_ticks()
                    if not balloon_fully_inflated and ding_sound:
                        ding_sound.play()
                        balloon_fully_inflated = True
                    for _ in range(50):
                        confetti_particles.append({
                            "x": random.randint(0, WIDTH),
                            "y": random.randint(0, HEIGHT // 2),
                            "color": random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0)]),
                            "speed": random.uniform(1, 3)
                        })
                    balloon_count += 1
            else:
                intensity = 0

    # Confetti particles
    for confetti in confetti_particles:
        pygame.draw.circle(screen, confetti["color"], (int(confetti["x"]), int(confetti["y"])), 5)
        confetti["y"] += confetti["speed"]

    # Buttons
    for button in settings_buttons:
        button.draw(screen)
        button.check_hover(pygame.mouse.get_pos())
    mouse_pos = pygame.mouse.get_pos()
    if settings_buttons[0].check_click(mouse_pos, just_clicked):
        game_state = "settings"
    if settings_buttons[1].check_click(mouse_pos, just_clicked):
        is_paused = not is_paused
        settings_buttons[1].text = "Resume" if is_paused else "Pause"
    if settings_buttons[2].check_click(mouse_pos, just_clicked):
        pygame.mixer.music.stop()
        game_state = "menu"
    
    # Draw "Paused" overlay if paused
    if is_paused:
        paused_text = title_font.render("Paused", True, BLACK)
        paused_bg_rect = pygame.Rect(0, 0, paused_text.get_width() + 40, paused_text.get_height() + 20)
        paused_bg_rect.center = (WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(screen, WHITE, paused_bg_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, paused_bg_rect, 2, border_radius=10)
        screen.blit(paused_text, paused_text.get_rect(center=paused_bg_rect.center))

# Main loop
running = True
while running:
    just_clicked = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    mouse_click = pygame.mouse.get_pressed()[0]
    if mouse_click and not mouse_was_pressed:
        just_clicked = True
    mouse_was_pressed = mouse_click
    if game_state == "menu":
        run_menu(just_clicked)
    elif game_state == "game":
        run_game(just_clicked)
    elif game_state == "settings":
        run_settings(just_clicked)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
