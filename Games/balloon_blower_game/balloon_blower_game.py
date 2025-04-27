import pygame
import os
import random
import sys
import math

# Allow joystick events in background
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"

# Initialize Pygame and Joystick Support
pygame.init()
pygame.joystick.init()

# set sensor
active_trigger = "both"

# Screen setup
DEFAULT_WIDTH, DEFAULT_HEIGHT = 800, 600
screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT), pygame.RESIZABLE)
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
YELLOW = (255, 218, 185)


# Get base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load balloon frames
original_frames = []
sprite_folder = os.path.join(BASE_DIR, "sprites")
for i in range(1, 11):
    frame_path = os.path.join(sprite_folder, f"Sprite-Balloon{i}.png")
    if os.path.exists(frame_path):
        frame = pygame.image.load(frame_path).convert_alpha()
        original_frames.append(frame)
    else:
        print(f"Warning: File not found - {frame_path}")

# Get original dimensions of frames 
if original_frames:
    original_frame_width = original_frames[0].get_width()
    original_frame_height = original_frames[0].get_height()
    original_aspect_ratio = original_frame_width / original_frame_height
else:
    original_aspect_ratio = DEFAULT_WIDTH / DEFAULT_HEIGHT

# Create scaled frames list 
frames = []

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

# Current screen size
WIDTH, HEIGHT = DEFAULT_WIDTH, DEFAULT_HEIGHT

# Button class 
class Button:
    def __init__(self, x_percent, y_percent, width_percent, height_percent, text, color, hover_color, font_type=None):
        # Initialize button properties 
        self.x_percent = x_percent
        self.y_percent = y_percent
        self.width_percent = width_percent
        self.height_percent = height_percent
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.is_hovered = False
        self.font_type = font_type
        self.font = font_type if font_type else font
        
        # Create the initial rect
        self.update_rect(WIDTH, HEIGHT)

    def update_rect(self, screen_width, screen_height):
        # Calculate position and size based on screen dimensions
        x = int(screen_width * self.x_percent)
        y = int(screen_height * self.y_percent)
        width = int(screen_width * self.width_percent)
        height = int(screen_height * self.height_percent)
        self.rect = pygame.Rect(x, y, width, height)
        
        # Update font size based on screen dimensions
        if self.font_type == small_font:
            font_size = int(24 * (screen_height / DEFAULT_HEIGHT))
        else:
            font_size = int(36 * (screen_height / DEFAULT_HEIGHT))
        
        self.font = pygame.font.SysFont(None, max(12, font_size))

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
max_frames = len(original_frames) - 1 
intensity = 0
min_threshold = -0.7
intensity_bar_width_percent = 0.375  # 300/800
intensity_bar_height_percent = 0.025  # 15/600

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

# Menu Screen Buttons 
play_button = Button(0.5 - 0.125, 0.5 - 0.133, 0.25, 0.1, "PLAY", GREEN, (100, 255, 100))
settings_button = Button(0.5 - 0.125, 0.5, 0.25, 0.1, "SETTINGS", GRAY, (220, 220, 220))
exit_button = Button(0.5 - 0.125, 0.5 + 0.133, 0.25, 0.1, "EXIT", (255, 100, 100), (255, 150, 150))

# Settings Screen Buttons
mute_button = Button(0.5 - 0.125, 0.5 - 0.05, 0.25, 0.083, "Mute Music", GRAY, (220, 220, 220))
back_button = Button(0.5 - 0.125, 0.5 + 0.067, 0.25, 0.083, "Back", GRAY, (220, 220, 220))

# Game Screen Button
game_menu_button = Button(0.0125, 1 - 0.083, 0.125, 0.067, "Menu", GRAY, (220, 220, 220), small_font)
game_settings_button = Button(1 - 0.1375, 1 - 0.083, 0.125, 0.067, "Settings", GRAY, (220, 220, 220), small_font)

# Pause button on game screen 
pause_button = Button(1 - 0.1375, 1 - 0.167, 0.125, 0.067, "Pause", GRAY, (220, 220, 220), small_font)

def resize_elements(new_width, new_height):
    global WIDTH, HEIGHT, frames
    
    # Update global dimensions
    WIDTH, HEIGHT = new_width, new_height
    
    # Resize all buttons
    play_button.update_rect(WIDTH, HEIGHT)
    settings_button.update_rect(WIDTH, HEIGHT)
    exit_button.update_rect(WIDTH, HEIGHT)
    mute_button.update_rect(WIDTH, HEIGHT)
    back_button.update_rect(WIDTH, HEIGHT)
    game_menu_button.update_rect(WIDTH, HEIGHT)
    game_settings_button.update_rect(WIDTH, HEIGHT)
    pause_button.update_rect(WIDTH, HEIGHT)
    
    # Resize all frames while preserving aspect ratio
    frames = []
    
    # Calculate the area available for the balloon frame
    frame_max_width = WIDTH
    frame_max_height = HEIGHT
    
    # Calculate dimensions that preserve image ratio
    if frame_max_width / frame_max_height > original_aspect_ratio:
        # Window is wider than the aspect ratio - constrain by height
        frame_height = frame_max_height
        frame_width = int(frame_height * original_aspect_ratio)
    else:
        # Window is taller than the aspect ratio - constrain by width
        frame_width = frame_max_width
        frame_height = int(frame_width / original_aspect_ratio)
    
    # Scale all frames
    for original_frame in original_frames:
        wider_width = int(frame_width * 1.4)  # 40% wider
        scaled_frame = pygame.transform.scale(original_frame, (wider_width, frame_height))
        frames.append(scaled_frame)


# Initial resize
resize_elements(DEFAULT_WIDTH, DEFAULT_HEIGHT)

def run_menu(just_clicked):
    global game_state, previous_state
    # Fill the menu background
    screen.fill(LIGHT_PURPLE)

    # Draw the title
    title_size = int(72 * (HEIGHT / DEFAULT_HEIGHT))
    current_title_font = pygame.font.SysFont(None, max(24, title_size))
    title_text = current_title_font.render("Balloon Blower", True, PURPLE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 - int(40 * (HEIGHT / DEFAULT_HEIGHT))))
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
    
    # Use scaled title font
    title_size = int(72 * (HEIGHT / DEFAULT_HEIGHT))
    current_title_font = pygame.font.SysFont(None, max(24, title_size))
    title_text = current_title_font.render("Settings", True, PURPLE)
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
    screen.fill(YELLOW if not is_paused else DARK_PURPLE)
    
    # Update game elements only if not paused
    if not is_paused:
        if joystick:  # Removed the congrats_display_timer == 0 check
            lt = joystick.get_axis(LT_AXIS)
            rt = joystick.get_axis(RT_AXIS)

            # Check which trigger to use based on selected mode
            current_value = None

            if active_trigger == "left" and lt > min_threshold:
                current_value = lt
            elif active_trigger == "right" and rt > min_threshold:
                current_value = rt
            elif active_trigger == "both":
                
                # Use the stronger trigger if both pressed
                if lt > min_threshold and rt > min_threshold:
                    current_value = lt if lt > rt else rt
                elif lt > min_threshold:
                    current_value = lt
                elif rt > min_threshold:
                    current_value = rt


            if current_value is not None:
                normalized_intensity = ((current_value + 1) / 2) * 100
                intensity = round(normalized_intensity)

                if intensity >= 70:
                    new_frame_index = max_frames  # Show final balloon frame (index 9)
                else:
                    new_frame_index = min(int((intensity / 70) * (max_frames)), max_frames - 1)

                if new_frame_index > frame_index and inflate_sound and not is_muted:
                    inflate_sound.play()
                frame_index = new_frame_index

            # Step is strong enough (intensity ≥ 60), mark it as valid
            if intensity >= 60 and not balloon_full:
                balloon_full = True
                balloon_fully_inflated = False  # allow confetti later

            # Step was valid and is now released — trigger balloon
            if balloon_full and intensity < 5 and not balloon_fully_inflated:
                congrats_display_timer = pygame.time.get_ticks()

                # Play ding sound without any connection to the timer
                if ding_sound:
                    ding_sound.play()

                # Show confetti - reduced number of particles for faster performance
                for _ in range(30):  
                    confetti_particles.append({
                        "x": random.randint(0, WIDTH),
                        "y": random.randint(0, HEIGHT // 2),
                        "color": random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255),
                                                (255, 255, 0), (255, 165, 0)]),
                        "speed": random.uniform(2, 4)  # Increased speed to make confetti fall faster
                    })

                balloon_count += 1  # Add to balloon count
                frame_index = 0     # Reset balloon sprite
                intensity = 0       # Reset intensity
                balloon_fully_inflated = True  # Stop duplicate triggers
                balloon_full = False           # Ready for next step

            elif current_value is None:
                intensity = 0

        # Process the congratulations timer separately
        # This only affects the visual display, not the sound
        if congrats_display_timer > 0 and pygame.time.get_ticks() - congrats_display_timer > 500:
            congrats_display_timer = 0
            confetti_particles.clear()

        # Draw the current balloon frame if available, centered on screen
        if frames and frame_index < len(frames):
            frame = frames[frame_index]
            frame_rect = frame.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(frame, frame_rect)
        
        # Use scaled font for all text
        scaled_font_size = int(36 * (HEIGHT / DEFAULT_HEIGHT))
        current_font = pygame.font.SysFont(None, max(12, scaled_font_size))
        
        # Display balloon count
        counter_text = current_font.render(f"Balloons Blown: {balloon_count}", True, BLACK)
        screen.blit(counter_text, (int(20 * (WIDTH / DEFAULT_WIDTH)), int(20 * (HEIGHT / DEFAULT_HEIGHT))))
        
        # Scale intensity bar based on screen size
        intensity_bar_width = int(intensity_bar_width_percent * WIDTH)
        intensity_bar_height = int(intensity_bar_height_percent * HEIGHT)
        intensity_bar_x = WIDTH - intensity_bar_width - int(20 * (WIDTH / DEFAULT_WIDTH))
        intensity_bar_y = int(20 * (HEIGHT / DEFAULT_HEIGHT))
        
        pygame.draw.rect(screen, BLACK, (intensity_bar_x, intensity_bar_y, intensity_bar_width, intensity_bar_height), 2)
        pygame.draw.rect(screen, PURPLE, (intensity_bar_x, intensity_bar_y, (intensity / 100) * intensity_bar_width, intensity_bar_height))
        
        # Calculate percentage (scaled to make 60 = 100%)
        visual_intensity = int((intensity / 60) * 100)
        
        # Display visual intensity percentage
        percent_text = current_font.render(f"Intensity: {visual_intensity}%", True, BLACK)
        screen.blit(percent_text, (intensity_bar_x, intensity_bar_y + intensity_bar_height + 5))

        # Draw line at 60% threshold
        threshold_x = intensity_bar_x + 0.6 * intensity_bar_width
        pygame.draw.line(screen, GREEN, (threshold_x, intensity_bar_y), (threshold_x, intensity_bar_y + intensity_bar_height), 2)

        # Display instruction text at the bottom of the game screen
        instruction_text = "Take a step to inflate the balloon!"
        outline_text = current_font.render(instruction_text, True, BLACK)
        main_text = current_font.render(instruction_text, True, PURPLE)
        text_x = WIDTH // 2 - outline_text.get_width() // 2
        text_y = HEIGHT - int(60 * (HEIGHT / DEFAULT_HEIGHT))
        padding = int(10 * (HEIGHT / DEFAULT_HEIGHT))
        
        pygame.draw.rect(screen, WHITE, (text_x - padding, text_y - padding,
                                         outline_text.get_width() + 2 * padding,
                                         outline_text.get_height() + 2 * padding))
        pygame.draw.rect(screen, BLACK, (text_x - padding, text_y - padding,
                                         outline_text.get_width() + 2 * padding,
                                         outline_text.get_height() + 2 * padding), 2)
        screen.blit(main_text, (text_x, text_y))
        
        # Draw confetti particles
        for confetti in confetti_particles:
            pygame.draw.circle(screen, confetti["color"], (int(confetti["x"]), int(confetti["y"])), 
                               int(5 * (HEIGHT / DEFAULT_HEIGHT)))
            confetti["y"] += confetti["speed"] * (HEIGHT / DEFAULT_HEIGHT)
        
        # Display congrats message if a balloon is blown
        if congrats_display_timer > 0:
            congrats_text = current_font.render("Congrats! Balloon Blown!", True, GREEN)
            screen.blit(congrats_text, (WIDTH // 2 - congrats_text.get_width() // 2, HEIGHT // 2))
    
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
        title_size = int(72 * (HEIGHT / DEFAULT_HEIGHT))
        current_title_font = pygame.font.SysFont(None, max(24, title_size))
        pause_overlay = current_title_font.render("Paused", True, WHITE)
        overlay_rect = pause_overlay.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(pause_overlay, overlay_rect)

def main_loop():
    global mouse_was_pressed, WIDTH, HEIGHT
    running = True
    while running:
        just_clicked = False
        for event in pygame.event.get():
            # Check for quit event
            if event.type == pygame.QUIT:
                running = False
            # Handle window resize events
            elif event.type == pygame.VIDEORESIZE:
                new_width, new_height = event.size
                screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                resize_elements(new_width, new_height)
                
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
