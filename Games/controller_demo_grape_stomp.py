import pygame
import time

pygame.init()

#controller initialization
pygame.joystick.init()
num_controllers = pygame.joystick.get_count()

#clock initialization
clock = pygame.time.Clock()

#constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# colors
WHITE = (255, 255, 255)
GREY = (200, 200, 200)
PURPLE = (119,0,200)
GREEN = (0,255,0)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grape Stomp!")

# load the sprite sheet and define frame dimensions
bg = pygame.image.load("Games/landscape.jpg")  #CHANGE BACK TO Games/landscape.jpg
sprite_sheet = pygame.image.load("Games/Walk.png") 
frame_width = 36  
frame_height = 48  
scale_factor = 15

#set step variables
step_count = 0
step_goal = 3


#get frames from the sprite sheet
man_left = sprite_sheet.subsurface((111, 0, frame_width, frame_height))
scaled_left = pygame.transform.scale(man_left, (frame_width * scale_factor, frame_height * scale_factor))
man_right = sprite_sheet.subsurface((16, 0, frame_width, frame_height))
scaled_right = pygame.transform.scale(man_right, (frame_width * scale_factor, frame_height * scale_factor))


#load the barrel
barrel = pygame.image.load("Games/Barrel-of-grapes.png")  
barrel = pygame.transform.scale(barrel, (500, 400))

#player settings
player_x = WIDTH // 2 - 330
player_y = HEIGHT - 645
player_speed = 2
font = pygame.font.SysFont(None, 36)

#jug (juice) progress settings
JUICE_WIDTH = 75
JUICE_HEIGHT = 400
juice_x = WIDTH // 2 + 300
juice_y = HEIGHT - 500

#initialize player
man_sprite = scaled_left

#controller setup
if num_controllers > 0:
    cont = pygame.joystick.Joystick(0)
    cont.init()
    #display contoller success
    print("\nGrape Stomper Starting...\n")

    #game loop
    running = True
    while running:
        for event in pygame.event.get():
            #check for user close window
            if event.type == pygame.QUIT:
                running = False

        #calculate total progress
        juice_lvl = step_count / step_goal
        #set initial message
        feedback = None

        #progress bar
        pygame.draw.rect(screen, GREY, (juice_x, juice_y, JUICE_WIDTH, JUICE_HEIGHT),2)
        fill_height = (step_count / 100) * JUICE_HEIGHT
        fill_y = juice_y + JUICE_HEIGHT - fill_height
        pygame.draw.rect(screen, PURPLE, (juice_x + 2, fill_y, JUICE_WIDTH - 4, fill_height))


        #check for controller input
        l_trig = cont.get_axis(4)
        r_trig = cont.get_axis(5)
        exit_button = cont.get_button(2)

        if l_trig > 0.1 and man_sprite != scaled_left and r_trig < 0.1:
            man_sprite = scaled_left
            step_count += 1

        elif r_trig > 0.1 and man_sprite != scaled_right and l_trig < 0.1:
            man_sprite = scaled_right
            step_count += 1

        elif exit_button or step_count == step_goal:
            running = False
        

        #set window background
        screen.blit(bg, (0,0))

        #draw the barrel og grapes
        screen.blit(barrel, (-55,225))

        #draw the man stomping
        screen.blit(man_sprite, (player_x, player_y))

        #display progress in text
        steps_text = font.render(f"Steps taken: {step_count}  Step Goal: {step_goal}", True, (0, 0, 0))
        screen.blit(steps_text, (300, 10))


        #check for one fourth complete
        if 0.24 < juice_lvl < 0.26:
            feedback = "Keep it up!"
            feedback_time = pygame.time.get_ticks() + 3000


        #check for one half complete
        elif 0.49 < juice_lvl < 0.51:
            feedback = "Half way Done!!"
            feedback_time = pygame.time.get_ticks() + 3000


        #check for three fourths complete
        elif 0.74 < juice_lvl < 0.76:
            feedback = "Almost Done!!"
            feedback_time = pygame.time.get_ticks() + 3000
            
        #check for message display settings
        if feedback and pygame.time.get_ticks() < feedback_time:
            text = pygame.font.Font(None, 60)
            complete_text = text.render(feedback, True, GREEN)
            screen.blit(complete_text, (325, 100))
        #otherwise display no message
        else:
            feedback = None
        
        #display progress bar (juice)
        pygame.draw.rect(screen, GREY, (juice_x, juice_y, JUICE_WIDTH, JUICE_HEIGHT),2)
        fill_height = juice_lvl * JUICE_HEIGHT
        fill_y = juice_y + JUICE_HEIGHT - fill_height
        pygame.draw.rect(screen, PURPLE, (juice_x + 2, fill_y, JUICE_WIDTH - 4, fill_height))

        #update screen
        pygame.display.flip()

        #set game clock
        clock.tick(FPS)

#check if goal completed
if step_count == step_goal:
        #display congratulation message for completion
        text = pygame.font.Font(None, 60)
        complete_text = text.render(f"Goal Complete!!", True, GREEN)
        screen.blit(complete_text, (325, 100))
        congrats_text = text.render(f"Nice Work!!", True, GREEN)
        screen.blit(congrats_text, (350, 150))
        pygame.display.flip()
        time.sleep(5)


# Quit Pygame
pygame.quit()
