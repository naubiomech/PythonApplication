import pygame
import socket
import json

# Constants
HOST = "localhost"  # Host to connect to (MacSocketController server)
PORT = 9999         # Port to connect to
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BAR_WIDTH = 100
BAR_MAX_HEIGHT = 400
BAR_COLOR_LEFT = (0, 128, 255)
BAR_COLOR_RIGHT = (255, 128, 0)
BACKGROUND_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Socket Test Game")
font = pygame.font.Font(None, 36)

# Connect to the MacSocketController server
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"Connected to MacSocketController at {HOST}:{PORT}")
except Exception as e:
    print(f"Error connecting to MacSocketController: {e}")
    pygame.quit()
    exit()

# Game loop
running = True
left_trigger_value = 0
right_trigger_value = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Receive data from the socket
    try:
        data = client_socket.recv(1024).decode("utf-8").strip()
        if data:
            # Split the data by newlines to handle multiple JSON objects
            messages = data.split("\n")
            for message in messages:
                if message.strip():  # Ignore empty messages
                    payload = json.loads(message)
                    left_trigger_value = payload.get("left_trigger", 0)
                    right_trigger_value = payload.get("right_trigger", 0)
    except Exception as e:
        print(f"Error receiving data: {e}")
        running = False

    # Clear the screen
    screen.fill(BACKGROUND_COLOR)

    # Draw the left bar
    left_bar_height = int((left_trigger_value / 255) * BAR_MAX_HEIGHT)
    pygame.draw.rect(
        screen,
        BAR_COLOR_LEFT,
        (
            SCREEN_WIDTH // 4 - BAR_WIDTH // 2,
            SCREEN_HEIGHT - left_bar_height,
            BAR_WIDTH,
            left_bar_height,
        ),
    )

    # Draw the right bar
    right_bar_height = int((right_trigger_value / 255) * BAR_MAX_HEIGHT)
    pygame.draw.rect(
        screen,
        BAR_COLOR_RIGHT,
        (
            3 * SCREEN_WIDTH // 4 - BAR_WIDTH // 2,
            SCREEN_HEIGHT - right_bar_height,
            BAR_WIDTH,
            right_bar_height,
        ),
    )

    # Display the trigger values
    left_text = font.render(f"Left Trigger: {left_trigger_value}", True, TEXT_COLOR)
    right_text = font.render(f"Right Trigger: {right_trigger_value}", True, TEXT_COLOR)
    screen.blit(left_text, (50, 50))
    screen.blit(right_text, (SCREEN_WIDTH - 300, 50))

    # Update the display
    pygame.display.flip()

# Clean up
client_socket.close()
pygame.quit()