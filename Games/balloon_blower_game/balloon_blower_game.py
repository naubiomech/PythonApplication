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

# Get base directory
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
    else:
        print(f"Warning: File not found - {frame_path}")

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

# Load background music and start paused (muted by default)
bg_music_path = os.path.join(sound_folder, "background.mp3")
if os.path.exists(bg_music_path):
    pygame.mixer.music.load(bg_music_path)
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.pause()  # Start muted

# Fonts
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 72)

# Button class 
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font_type=None):

        # Initialize button properties
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.is_hovered = False
        self.font = font_type if font_type else font

    def draw(self, surface):
        # Draw the button rectangle with rounded corners and a border
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)

        # Render and center the text within the button
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        # Check if the mouse is over the button
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.current_color = self.hover_color if self.is_hovered else self.color
        return self.is_hovered

    def check_click(self, mouse_pos, just_clicked):
        # Return True if the button is clicked
        return self.rect.collidepoint(mouse_pos) and just_clicked

# Global variables for game state
game_state = "menu"         # Can be "menu", "game", or "settings"
previous_state = "menu"     # To return from settings to previous state
is_muted = True             # Start with music muted
is_paused = False           # Game pause flag
mouse_was_pressed = False

balloon_full = False
balloon_count = 0
balloon_fully_inflated = False

frame_index = 0
max_frames = len(frames) - 1
intensity = 0
min_threshold = -0.7
intensity_bar_width = 300
intensity_bar_height = 15

confetti_particles = []
congrats_display_timer = 0

# Joystick setup
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
LT_AXIS = 4
RT_AXIS = 5

clock = pygame.time.Clock()


# Menu Screen Buttons (centered)
play_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 80, 200, 60, "PLAY", GREEN, (100, 255, 100))
settings_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 60, "SETTINGS", GRAY, (220, 220, 220))
exit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 60, "EXIT", (255, 100, 100), (255, 150, 150))

# Settings Screen Buttons
mute_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 30, 200, 50, "Mute Music", GRAY, (220, 220, 220))
back_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 40, 200, 50, "Back", GRAY, (220, 220, 220))

# Game Screen Button
game_menu_button = Button(10, HEIGHT - 50, 100, 40, "Menu", GRAY, (220, 220, 220), small_font)
game_settings_button = Button(WIDTH - 110, HEIGHT - 50, 100, 40, "Settings", GRAY, (220, 220, 220), small_font)

# Pause button on game screen (placed above the settings button)
pause_button = Button(WIDTH - 110, HEIGHT - 100, 100, 40, "Pause", GRAY, (220, 220, 220), small_font)

def run_menu(just_clicked):
    global game_state, previous_state
    # Fill the menu background
    screen.fill(LIGHT_PURPLE)

    # Draw the title
    title_text = title_font.render("Balloon Blower", True, PURPLE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 - 40))
    screen.blit(title_text, title_rect)

    # Draw menu buttons
    play_button.draw(screen)
    settings_button.draw(screen)
    exit_button.draw(screen)
    
    mouse_pos = pygame.mouse.get_pos()
    play_button.check_hover(mouse_pos)
    settings_button.check_hover(mouse_pos)
    exit_button.check_hover(mouse_pos)
    
    if play_button.check_click(mouse_pos, just_clicked):
        game_state = "game"
        previous_state = "menu"
        # Unpause background music if not muted
        if not is_muted:
            pygame.mixer.music.unpause()
    elif settings_button.check_click(mouse_pos, just_clicked):
        previous_state = "menu"
        game_state = "settings"
    elif exit_button.check_click(mouse_pos, just_clicked):
        pygame.quit()
        sys.exit()

def run_settings(just_clicked):
    global game_state, is_muted, previous_state
    # Fill the settings background
    screen.fill(LIGHT_PURPLE)
    title_text = title_font.render("Settings", True, PURPLE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_text, title_rect)
    
    # Update the mute button text based on current mute state
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
        game_state = previous_state

def run_game(just_clicked):
    global frame_index, intensity, balloon_full, congrats_display_timer
    global balloon_fully_inflated, balloon_count, game_state, is_paused, confetti_particles

    # Fill the game background (different color if paused)
    screen.fill(LIGHT_BLUE if not is_paused else DARK_PURPLE)
    
    # Update game elements only if not paused
    if not is_paused:
        if joystick and congrats_display_timer == 0:
            lt = joystick.get_axis(LT_AXIS)
            rt = joystick.get_axis(RT_AXIS)
            current_value = None

            # Choose trigger with greater if value if two sensors pressed at same time
            if lt > min_threshold and rt > min_threshold:
                current_value = lt if lt > rt else rt
            
            # Choose left trigger if pressed
            elif lt > min_threshold:
                current_value = lt
            
            # Choose right trigger if pressed
            elif rt > min_threshold:
                current_value = rt

            if current_value is not None:
                normalized_intensity = ((current_value + 1) / 2) * 100
                intensity = round(normalized_intensity)
                new_frame_index = min(int((intensity / 100) * max_frames), max_frames)
                if new_frame_index > frame_index and inflate_sound and not is_muted:
                    inflate_sound.play()
                frame_index = new_frame_index
                if intensity >= 60 and not balloon_full:
                    balloon_full = True
                    congrats_display_timer = pygame.time.get_ticks()
                    if not balloon_fully_inflated and ding_sound:
                        ding_sound.play()
                        balloon_fully_inflated = True
                    for _ in range(50):
                        confetti_particles.append({
                            "x": random.randint(0, WIDTH),
                            "y": random.randint(0, HEIGHT // 2),
                            "color": random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255),
                                                     (255, 255, 0), (255, 165, 0)]),
                            "speed": random.uniform(1, 3)
                        })
                    balloon_count += 1
            else:
                intensity = 0

        # Draw the current balloon frame if available
        if frames:
            screen.blit(frames[frame_index], (0, 0))
        
        # Display balloon count and intensity bar
        counter_text = font.render(f"Balloons Blown: {balloon_count}", True, BLACK)
        screen.blit(counter_text, (20, 20))
        intensity_bar_x = WIDTH - intensity_bar_width - 20
        intensity_bar_y = 20
        pygame.draw.rect(screen, BLACK, (intensity_bar_x, intensity_bar_y, intensity_bar_width, intensity_bar_height), 2)
        pygame.draw.rect(screen, PURPLE, (intensity_bar_x, intensity_bar_y, (intensity / 100) * intensity_bar_width, intensity_bar_height))
        

         # Draw line at 60% threshold
        threshold_x = intensity_bar_x + 0.6 * intensity_bar_width
        pygame.draw.line(screen, GREEN, (threshold_x, intensity_bar_y), (threshold_x, intensity_bar_y + intensity_bar_height), 2)
        intensity_text = font.render(f"Intensity: {int(intensity)}%", True, BLACK)
        screen.blit(intensity_text, (intensity_bar_x + (intensity_bar_width - intensity_text.get_width()) // 2,
                                     intensity_bar_y + intensity_bar_height + 5))
        
        # Display instruction text at the bottom of the game screen
        instruction_text = "Take a step to inflate the balloon!"
        outline_text = font.render(instruction_text, True, BLACK)
        main_text = font.render(instruction_text, True, PURPLE)
        text_x = WIDTH // 2 - outline_text.get_width() // 2
        text_y = HEIGHT - 60
        padding = 10
        pygame.draw.rect(screen, WHITE, (text_x - padding, text_y - padding,
                                           outline_text.get_width() + 2 * padding,
                                           outline_text.get_height() + 2 * padding))
        pygame.draw.rect(screen, BLACK, (text_x - padding, text_y - padding,
                                           outline_text.get_width() + 2 * padding,
                                           outline_text.get_height() + 2 * padding), 2)
        screen.blit(main_text, (text_x, text_y))
        
        # Draw confetti particles
        for confetti in confetti_particles:
            pygame.draw.circle(screen, confetti["color"], (int(confetti["x"]), int(confetti["y"])), 5)
            confetti["y"] += confetti["speed"]
        
        # Display congrats message if a balloon is blown, then reset after a short delay
        if congrats_display_timer > 0:
            congrats_text = font.render("Congrats! Balloon Blown!", True, GREEN)
            screen.blit(congrats_text, (WIDTH // 2 - congrats_text.get_width() // 2, HEIGHT // 2))
            if pygame.time.get_ticks() - congrats_display_timer > 1000:
                congrats_display_timer = 0
                balloon_full = False
                balloon_fully_inflated = False
                frame_index = 0
                intensity = 0
                confetti_particles.clear()
    
    # Draw game screen buttons 
    mouse_pos = pygame.mouse.get_pos()
    game_menu_button.draw(screen)
    game_settings_button.draw(screen)
    game_menu_button.check_hover(mouse_pos)
    game_settings_button.check_hover(mouse_pos)
    
    if game_menu_button.check_click(mouse_pos, just_clicked):
        pygame.mixer.music.stop()
        game_state = "menu"
    if game_settings_button.check_click(mouse_pos, just_clicked):
        previous_state = "game"
        game_state = "settings"
    
    # Draw the pause button 
    pause_button.text = "Resume" if is_paused else "Pause"
    pause_button.draw(screen)
    pause_button.check_hover(mouse_pos)
    if pause_button.check_click(mouse_pos, just_clicked):
        is_paused = not is_paused

    # If the game is paused, show word "Paused"
    if is_paused:
        pause_overlay = title_font.render("Paused", True, WHITE)
        overlay_rect = pause_overlay.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(pause_overlay, overlay_rect)

def main_loop():
    global mouse_was_pressed
    running = True
    while running:
        just_clicked = False
        for event in pygame.event.get():
            # Check for quit event
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

if __name__ == "__main__":
    main_loop()
