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
   else:
       print(f"Warning: File not found - {frame_path}")

# Load sounds
sound_folder = os.path.join(BASE_DIR, "sounds")
inflate_sound_path = os.path.join(sound_folder, "inflate.wav")
ding_sound_path = os.path.join(sound_folder, "ding.wav")

# Load inflate sound
if os.path.exists(inflate_sound_path):
   inflate_sound = pygame.mixer.Sound(inflate_sound_path)
   inflate_sound.set_volume(0.1)
else:
   inflate_sound = None

# Load ding sound
if os.path.exists(ding_sound_path):
   ding_sound = pygame.mixer.Sound(ding_sound_path)
   ding_sound.set_volume(0.5)
else:
   ding_sound = None

# Load background music
bg_music_path = os.path.join(sound_folder, "background.mp3")
if os.path.exists(bg_music_path):
   pygame.mixer.music.load(bg_music_path)
   pygame.mixer.music.set_volume(0.3)

# Font
font = pygame.font.SysFont(None, 36)
title_font = pygame.font.SysFont(None, 72)

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.is_hovered = False
        
    def draw(self, surface):
        # Draw button
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=15)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=15)
        
        # Render text
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            self.is_hovered = True
        else:
            self.current_color = self.color
            self.is_hovered = False
        return self.is_hovered
        
    def check_click(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

# Game state
game_state = "menu"  # Can be "menu" or "game"
balloon_full = False
balloon_count = 0
balloon_fully_inflated = False

# Animation variables
frame_index = 0
max_frames = len(frames) - 1

# Intensity Bar
intensity = 0
min_threshold = -0.7
intensity_bar_width = 300
intensity_bar_height = 15

# Confetti Variables
confetti_particles = []
congrats_display_timer = 0

# Check for connected joysticks
joystick = None
if pygame.joystick.get_count() > 0:
   joystick = pygame.joystick.Joystick(0)
   joystick.init()

# Trigger Axis Mapping for XBOX type controller
LT_AXIS = 4
RT_AXIS = 5

# Track required trigger
expected_trigger = random.choice(["LEFT", "RIGHT"])

# Create menu buttons
button_width = 200
button_height = 60
play_button = Button(WIDTH // 2 - button_width // 2, HEIGHT // 2 - 20, 
                     button_width, button_height, "PLAY", GREEN, (100, 255, 100))
exit_button = Button(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 60, 
                     button_width, button_height, "EXIT", (255, 100, 100), (255, 150, 150))

# Clock
clock = pygame.time.Clock()

def run_menu():
    global game_state
    
    # Draw menu
    screen.fill(LIGHT_PURPLE)
    
    # Draw title
    title_text = title_font.render("Balloon Blower", True, PURPLE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title_text, title_rect)
    
    # Draw buttons
    play_button.draw(screen)
    exit_button.draw(screen)
    
    # Check button hover
    mouse_pos = pygame.mouse.get_pos()
    play_button.check_hover(mouse_pos)
    exit_button.check_hover(mouse_pos)
    
    # Handle button clicks
    mouse_click = pygame.mouse.get_pressed()[0]
    if play_button.check_click(mouse_pos, mouse_click):
        game_state = "game"
        # Start background music
        pygame.mixer.music.play(-1)
    elif exit_button.check_click(mouse_pos, mouse_click):
        pygame.quit()
        sys.exit()

def run_game():
    global frame_index, intensity, balloon_full, congrats_display_timer
    global balloon_fully_inflated, balloon_count, expected_trigger, game_state
    
    screen.fill(LIGHT_BLUE)

    # Get trigger input
    if joystick and congrats_display_timer == 0:
        lt = joystick.get_axis(LT_AXIS)
        rt = joystick.get_axis(RT_AXIS)

        # Get the current trigger value based on which trigger is expected
        current_trigger = lt if expected_trigger == "LEFT" else rt

        # Handle trigger input
        if current_trigger > min_threshold:  # Trigger is pressed
            # Normalize from -1...1 to 0...100 because controller starts at -1
            normalized_intensity = ((current_trigger + 1) / 2) * 100
            intensity = round(normalized_intensity)
            
            # Calculate frame index
            new_frame_index = min(int((intensity / 100) * max_frames), max_frames)

            # Play inflation sound
            if new_frame_index > frame_index and inflate_sound:
                inflate_sound.play()

            frame_index = new_frame_index

            # Check for balloon completion
            if intensity >= 99 and not balloon_full:
                balloon_full = True
                congrats_display_timer = pygame.time.get_ticks()
                
                if not balloon_fully_inflated and ding_sound:
                    ding_sound.play()
                    balloon_fully_inflated = True

                # Add confetti
                for _ in range(50):
                    confetti_particles.append({
                        "x": random.randint(0, WIDTH),
                        "y": random.randint(0, HEIGHT // 2),
                        "color": random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0)]),
                        "speed": random.uniform(1, 3)
                    })
                balloon_count += 1
        else:  # Trigger is released
            intensity = 0

    # Draw balloon frame
    if frames:
        screen.blit(frames[frame_index], (0, 0))

    # Show balloon counter 
    counter_text = font.render(f"Balloons Blown: {balloon_count}", True, BLACK)
    screen.blit(counter_text, (20, 20))

    # Draw Intensity Bar 
    intensity_bar_x = WIDTH - intensity_bar_width - 20  # 20px padding from right edge
    intensity_bar_y = 20  # 20px padding from top edge
    
    # Draw the bar background and border
    pygame.draw.rect(screen, BLACK, (intensity_bar_x, intensity_bar_y, intensity_bar_width, intensity_bar_height), 2)
    pygame.draw.rect(screen, PURPLE, (intensity_bar_x, intensity_bar_y, (intensity / 100) * intensity_bar_width, intensity_bar_height))

    # Show intensity percentage below the bar
    intensity_text = font.render(f"Intensity: {int(intensity)}%", True, BLACK)
    screen.blit(intensity_text, (intensity_bar_x + (intensity_bar_width - intensity_text.get_width()) // 2, intensity_bar_y + intensity_bar_height + 5))

    # Show trigger instruction 
    text_message = f"Press {expected_trigger} to inflate the balloon!"
    outline_text = font.render(text_message, True, BLACK)
    main_text = font.render(text_message, True, PURPLE)

    # Position for text
    text_x = WIDTH // 2 - outline_text.get_width() // 2
    text_y = HEIGHT - 60

    # Calculate box dimensions 
    padding = 10  
    box_width = outline_text.get_width() + padding * 2
    box_height = outline_text.get_height() + padding * 2
    box_x = text_x - padding
    box_y = text_y - padding

    # Draw text box
    pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height))
    pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 2)

    # Draw text 
    screen.blit(main_text, (text_x, text_y))

    # Handle congrats message and reset
    if congrats_display_timer > 0:
        congrats_text = font.render("Congrats! Balloon Blown!", True, GREEN)
        screen.blit(congrats_text, (WIDTH // 2 - congrats_text.get_width() // 2, HEIGHT // 2))

        if pygame.time.get_ticks() - congrats_display_timer > 1000:
            congrats_display_timer = 0
            balloon_full = False
            frame_index = 0
            intensity = 0
            confetti_particles.clear()
            balloon_fully_inflated = False
            expected_trigger = "RIGHT" if expected_trigger == "LEFT" else "LEFT"

    # Update confetti
    for confetti in confetti_particles:
        pygame.draw.circle(screen, confetti["color"], (int(confetti["x"]), int(confetti["y"])), 5)
        confetti["y"] += confetti["speed"]
    
    # Add back to menu button
    back_button = Button(20, HEIGHT - 60, 100, 40, "Menu", WHITE, (200, 200, 200))
    back_button.draw(screen)
    
    # Check if back button is clicked
    mouse_pos = pygame.mouse.get_pos()
    back_button.check_hover(mouse_pos)
    mouse_click = pygame.mouse.get_pressed()[0]
    if back_button.check_click(mouse_pos, mouse_click):
        # Reset game state and return to menu
        congrats_display_timer = 0
        balloon_full = False
        frame_index = 0
        intensity = 0
        confetti_particles.clear()
        balloon_fully_inflated = False
        expected_trigger = random.choice(["LEFT", "RIGHT"])
        pygame.mixer.music.stop()
        game_state = "menu"

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYAXISMOTION:
            if event.axis in [4, 5]:
                print(f"Axis {event.axis} moved to {event.value:.2f}")
                
    # Run the current game state
    if game_state == "menu":
        run_menu()
    elif game_state == "game":
        run_game()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
