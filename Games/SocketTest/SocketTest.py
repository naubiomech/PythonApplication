import socket
import pygame
import threading

# --- Socket Setup ---
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# Shared variables to store latest values
trigger_values = ["0", "0"]
running = True

# --- Socket Listening Thread ---
def listen_for_data():
    global trigger_values, running
    while running:
        try:
            data, _ = sock.recvfrom(1024)
            decoded = data.decode("utf-8")
            if "," in decoded:
                trigger_values = decoded.strip().split(",")
        except Exception as e:
            print("Socket error:", e)

listener_thread = threading.Thread(target=listen_for_data, daemon=True)
listener_thread.start()

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((400, 200))
pygame.display.set_caption("Trigger Values Viewer")
font = pygame.font.SysFont("Arial", 32)

clock = pygame.time.Clock()

# --- Main Loop ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))  # dark background

    left_text = font.render(f"Left Trigger: {trigger_values[0]}", True, (255, 255, 255))
    right_text = font.render(f"Right Trigger: {trigger_values[1]}", True, (255, 255, 255))

    screen.blit(left_text, (50, 50))
    screen.blit(right_text, (50, 100))

    pygame.display.flip()
    clock.tick(60)

# Cleanup
sock.close()
pygame.quit()
