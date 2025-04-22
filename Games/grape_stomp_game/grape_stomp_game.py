#import necessary modules
import pygame
import sys
import os
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"

#initialize pygame
pygame.init()

#controller initialization
pygame.joystick.init()
num_controllers = pygame.joystick.get_count()

#clock initialization
clock = pygame.time.Clock()

#constants
INITIAL_WIDTH, INITIAL_HEIGHT = 800, 600
FPS = 60

# colors
WHITE = (255, 255, 255)
GREY = (200, 200, 200)
PURPLE = (119,0,200)
GREEN = (0,255,0)
BLACK = (0,0,0)

#open the game window
screen = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Grape Stomp!")

#initialize menu button locations
start = pygame.Rect(150, 200, 200, 100)
quit_button = pygame.Rect(450, 200, 200, 100)
results = pygame.Rect(300, 350, 200, 100)

#main menu function, should be running for full duration of game behind game screen
def main_menu():

    #set the screen variables as global
    global screen
    #initialize starting values
    game_running = True
    #initialize the step counts for end game display
    total_step_count = 0
    full_steps_count = 0
    
    #begin main menu loop
    while game_running:

        #set the base surface for screen scaling
        base_surface = pygame.Surface((INITIAL_WIDTH, INITIAL_HEIGHT))
        #set base color
        base_surface.fill(GREY)

        for event in pygame.event.get():
            #check for user close window
            if event.type == pygame.QUIT:
                game_running = False

            #check for user resizing
            if event.type == pygame.VIDEORESIZE:
                #collect the screen data when user resizes window
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            #check for mouse position
            if event.type == pygame.MOUSEBUTTONDOWN:

                #scale mouse positions
                scale_x = screen.get_width() / INITIAL_WIDTH
                scale_y = screen.get_height() / INITIAL_HEIGHT
                #set mouse positions
                mouse_x, mouse_y = event.pos[0] / scale_x, event.pos[1] / scale_y
                #check for user select button
                if start.collidepoint((mouse_x, mouse_y)):
                    #run game
                    total_step_count, full_steps_count = game()
                #otherwise assume user attempting to exit
                elif quit_button.collidepoint((mouse_x, mouse_y)):
                    #stop the game
                    game_running = False
                    #close the window
                    pygame.quit()
                    sys.exit()

        #display game title
        text = pygame.font.Font(None, 70)
        complete_text = text.render("Grape Stomp!", True, BLACK)
        #write title to screen
        base_surface.blit(complete_text, (INITIAL_WIDTH // 2 - complete_text.get_width() // 2, 100))

        #draw the menu buttons
        pygame.draw.rect(base_surface, PURPLE, start)
        pygame.draw.rect(base_surface, PURPLE, quit_button)

        #display game controls
        text = pygame.font.Font(None, 30)
        controls_text = text.render("Move your legs to play and fill as many bottles as you can!", True, BLACK)
        base_surface.blit(controls_text, (125, 350))
        controls_text = text.render('Press "esc" to exit and "p" to pause!', True, BLACK)
        base_surface.blit(controls_text, (225, 380))

        #display the end game step counts
        if total_step_count > 0:
            #display header
            text = pygame.font.Font(None, 40)
            total_steps_results = text.render("Session Results:", True, BLACK)
            base_surface.blit(total_steps_results, (125, 460))
            #display total steps
            text = pygame.font.Font(None, 30)
            total_steps_results = text.render(f"Total Steps taken: {total_step_count}", True, BLACK)
            base_surface.blit(total_steps_results, (125, 500))
            #display the full steps taken
            full_steps_results = text.render(f"Full Steps taken: {full_steps_count}", True, BLACK)
            base_surface.blit(full_steps_results, (125, 525))

        #create the start button
        button_text = pygame.font.Font(None, 50)
        start_button_text = button_text.render("Start Game", True, BLACK)
        #scale button to screen
        base_surface.blit(start_button_text, (start.x + start.width//2 - start_button_text.get_width()//2, 
                                           start.y + start.height//2 - start_button_text.get_height()//2))
        #create the quit button
        exit_button_text = button_text.render(" Exit Game", True, BLACK)
        #scale button to screen
        base_surface.blit(exit_button_text, (quit_button.x + quit_button.width//2 - exit_button_text.get_width()//2, 
                                          quit_button.y + quit_button.height//2 - exit_button_text.get_height()//2))

        #collect the scaled screen data
        stretched_screen = pygame.transform.scale(base_surface, (screen.get_width(), screen.get_height()))
        #display screen
        screen.blit(stretched_screen, (0, 0))

        #update the screen
        pygame.display.flip()
        clock.tick(FPS)


#game loop function
def game():
    #set screen as global
    global screen

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # load the sprite sheet and define frame dimensions
    bg = pygame.image.load(os.path.join(BASE_DIR, "landscape.jpg"))
    sprite_sheet = pygame.image.load(os.path.join(BASE_DIR, "Walk.png"))   
    frame_width = 36  
    frame_height = 48  
    scale_factor = 15

    #load the audio file
    step_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "ding.wav"))

    #set step variables
    total_step_count = 0
    full_steps_count = 0
    prev_total_steps = total_step_count

    #get frames from the sprite sheet
    man_left = sprite_sheet.subsurface((111, 0, frame_width, frame_height))
    scaled_left = pygame.transform.scale(man_left, (frame_width * scale_factor, frame_height * scale_factor))
    man_right = sprite_sheet.subsurface((16, 0, frame_width, frame_height))
    scaled_right = pygame.transform.scale(man_right, (frame_width * scale_factor, frame_height * scale_factor))


    #load the barrel
    barrel = pygame.image.load(os.path.join(BASE_DIR, "Barrel-of-grapes.png") )
    barrel = pygame.transform.scale(barrel, (500, 300))

    #player settings
    player_x = INITIAL_WIDTH // 2 - 330
    player_y = INITIAL_HEIGHT - 645
    player_speed = 2
    font = pygame.font.SysFont(None, 36)

    #jug (juice) progress settings
    JUICE_WIDTH = 75
    JUICE_HEIGHT = 400
    juice_x = INITIAL_WIDTH // 2 + 300
    juice_y = INITIAL_HEIGHT - 500

    #set flag to check if sound has played
    soundFlag = False
    #set a timer for simple display
    timer = 0
    #set a flag to check to skip a loop
    passFlag = False
    #set a flag to check for full step taken
    full_step_flag = False

    #initialize player
    man_sprite = scaled_left
    #controller setup
    if num_controllers > 0:
        #initialize the controller
        cont = pygame.joystick.Joystick(0)
        cont.init()

        #game loop
        running = True
        pause = False
        #initialize juice starting level
        juice_lvl = 0
        #initialize max step threshold
        step_thresh = 0.6
        #initialize display settings
        total_steps_toggle = True
        full_steps_toggle = True 
        #initialize prev steps for left and right
        prev_left = 0.0
        prev_right = 0.0


        #main game loop
        while running:
            #collect the base data
            base_surface = pygame.Surface((INITIAL_WIDTH, INITIAL_HEIGHT))
            #listen for use actions
            for event in pygame.event.get():
                #check for user close window
                if event.type == pygame.QUIT:
                    running = False

                #check for user resizing
                if event.type == pygame.VIDEORESIZE:
                    #collect screen data
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                #check for keyboard input
                if event.type == pygame.KEYDOWN:
                    #keyboard input for pause
                    if event.key == pygame.K_p:
                        pause = not pause

                    #keyboard input to quit game
                    if event.key == pygame.K_ESCAPE:
                        running = False

            #blit the background image
            base_surface.blit(bg, (0, 0))
            #blit the character sprite
            base_surface.blit(man_sprite, (player_x, player_y))
            #blit the barrel
            base_surface.blit(barrel, (-55, 300))
            #draw the bottle
            pygame.draw.rect(base_surface, GREY, (juice_x, juice_y, JUICE_WIDTH, JUICE_HEIGHT), 2)
            fill_height = juice_lvl
            # fill_height = juice_lvl * JUICE_HEIGHT
            fill_y = juice_y + JUICE_HEIGHT - fill_height
            #draw the juice
            pygame.draw.rect(base_surface, PURPLE, (juice_x + 2, fill_y, JUICE_WIDTH - 4, fill_height))

            #calcualte the threshold for full step
            threshold_y = juice_y + JUICE_HEIGHT - (step_thresh * JUICE_HEIGHT)
            #draw the threshold
            pygame.draw.line(base_surface, BLACK, (juice_x, threshold_y), 
                           (juice_x + JUICE_WIDTH, threshold_y), 8)

            #display total steps if toggled (automatically toggled)
            if total_steps_toggle:
                font = pygame.font.Font(None, 36)
                total_steps_text = font.render(f"Total Steps: {total_step_count}", True, BLACK)
                base_surface.blit(total_steps_text, (300, 10))
            #display full steps if toggled (automatically toggled)
            if full_steps_toggle:
                font = pygame.font.Font(None, 36)
                full_steps_text = font.render(f"Full Steps: {full_steps_count}", True, BLACK)
                base_surface.blit(full_steps_text, (300, 35))

            #check if full step conditions have been met
            if(passFlag):
                #check if timer is over
                if timer > 0 and pygame.time.get_ticks() - timer > 1000:
                    #reset threshold flags and timer
                    soundFlag = False
                    timer = 0
                    passFlag = False
                    full_step_flag = False
                
                #show congrats message
                font = pygame.font.Font(None, 36)
                congrats_text = font.render("Bottle Filled!", True, GREEN)
                base_surface.blit(congrats_text, (INITIAL_WIDTH//2 - congrats_text.get_width()//2, 
                                                INITIAL_HEIGHT//2))
                
                #stretch the game screen
                stretched_screen = pygame.transform.scale(base_surface, (screen.get_width(), screen.get_height()))
                screen.blit(stretched_screen, (0, 0))
                #update the screen
                pygame.display.flip()
                clock.tick(FPS)

            #check for game paused
            if pause:
                #initialize input text
                if 'input_text' not in locals():
                    input_text = ""
                    active_box = False
    
                #creat pause menu
                pause_surface = pygame.Surface((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.SRCALPHA)
                pause_surface.fill((200, 200, 200, 128))
    
                #calculate stretch
                scale_x = screen.get_width() / INITIAL_WIDTH
                scale_y = screen.get_height() / INITIAL_HEIGHT
    
                #initialize pause menu items
                input_box = pygame.Rect(175, 250, 300, 40)
                total_steps_box = pygame.Rect(175, 315, 20, 20)
                full_steps_box = pygame.Rect(175, 350, 20, 20)
                settings_rect = pygame.Rect(155, 200, 550, 200)
    
                #listen for user events
                for event in pygame.event.get():
                    #check for user quit
                    if event.type == pygame.QUIT:
                        running = False
                    #check for screen resize
                    if event.type == pygame.VIDEORESIZE:
                        screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    #check for unpause toggle
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_p:
                            pause = False
                        #check for text box
                        if active_box:
                            #listen for user enter
                            if event.key == pygame.K_RETURN:
                                #attempt to reset step threshold
                                try:
                                    step_thresh = float(input_text)
                                    if 0.0 < step_thresh < 1.0:
                                        print(f"Threshold set to: {input_text}")
                                        pause = False
                                    else:
                                        print("ERROR: Please enter threshold between 0 and 1")
                                #otherwise displau error
                                except ValueError:
                                    print("ERROR: Please enter a valid number")
                            #check for user delete text
                            elif event.key == pygame.K_BACKSPACE:
                                input_text = input_text[:-1]
                            #check for user adding to input text
                            else:
                                input_text += event.unicode
                    #check for user click
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = event.pos[0] / scale_x, event.pos[1] / scale_y
                        #check for user select input box
                        if input_box.collidepoint((mouse_x, mouse_y)):
                            active_box = True
                        else:
                            active_box = False
                        #check for total steps toggle
                        if total_steps_box.collidepoint((mouse_x, mouse_y)):
                            total_steps_toggle = not total_steps_toggle
                        #check for full steps toggle
                        elif full_steps_box.collidepoint((mouse_x, mouse_y)):
                            full_steps_toggle = not full_steps_toggle
    
                #display the menu
                pygame.draw.rect(pause_surface, GREY, settings_rect)
                #display pause message
                font_large = pygame.font.Font(None, 60)
                pause_text = font_large.render("PAUSED", True, BLACK)
                pause_surface.blit(pause_text, (INITIAL_WIDTH//2 - pause_text.get_width()//2, 100))
                #display instructions
                pause_instruction = font_large.render('Press "P" to resume', True, BLACK)
                pause_surface.blit(pause_instruction, (INITIAL_WIDTH//2 - pause_instruction.get_width()//2, 150))
                #display input instructuons
                font_small = pygame.font.Font(None, 20)
                instruction_text = font_small.render("Step Threshold (0-1):", True, BLACK)
                pause_surface.blit(instruction_text, (180, 230))
    
                #check for user select the text box
                pygame.draw.rect(pause_surface, WHITE, input_box, border_radius=4)
                if active_box:
                    #highlight the box if selected
                    pygame.draw.rect(pause_surface, PURPLE, input_box, 2, border_radius=4)
    
                #display total steps toggle
                pygame.draw.rect(pause_surface, WHITE, total_steps_box, border_radius=4)
                if total_steps_toggle:
                    #highlight the toggle if selected
                    pygame.draw.rect(pause_surface, PURPLE, total_steps_box, border_radius=4)
                #display total steps toggle
                pygame.draw.rect(pause_surface, WHITE, full_steps_box, border_radius=4)
                if full_steps_toggle:
                    #highlight the toggle if selected
                    pygame.draw.rect(pause_surface, PURPLE, full_steps_box, border_radius=4)
    
                #display total steps label
                total_label = font_small.render("Show total steps", True, BLACK)
                pause_surface.blit(total_label, (200, 315))
                #display full steps label
                full_label = font_small.render("Show full steps", True, BLACK)
                pause_surface.blit(full_label, (200, 350))
    
                #display the user input text
                if input_text:
                    input_surface = pygame.font.Font(None, 36).render(input_text, True, BLACK)
                    pause_surface.blit(input_surface, (input_box.x + 5, input_box.y + 5))
    
                #update the screen base screen
                stretched_screen = pygame.transform.scale(base_surface, (screen.get_width(), screen.get_height()))
                screen.blit(stretched_screen, (0, 0))
                #update the screen with the fully drawn pause menu
                stretched_pause = pygame.transform.scale(pause_surface, (screen.get_width(), screen.get_height()))
                screen.blit(stretched_pause, (0, 0))
                #update the window
                pygame.display.flip()
                clock.tick(FPS)
                #continue looping unless pause untoggled
                continue

            #check for controller input
            l_trig = cont.get_axis(4)
            r_trig = cont.get_axis(5)
            exit_button = cont.get_button(2)

            #check for any controller input
            if((prev_left <= 0 and l_trig > 0) or (prev_right <= 0 and r_trig > 0)):
                #update steo count for user input
                total_step_count += 1            

            #check for increase in step count
            if total_step_count > prev_total_steps:
                #update the sprite if the stepcount goes up
                man_sprite = scaled_right if man_sprite == scaled_left else scaled_left
                #set the new previous steps
                prev_total_steps = total_step_count

            #condition to check for game exit
            elif exit_button:
                running = False

            #set the juice level to the step pressure value
            step = max(l_trig, r_trig)
            juice_lvl = ((step + 1) / 2) * JUICE_HEIGHT
            #juice_lvl = step

            #check for step exceeding the step thresh and no sound played
            if(step >= step_thresh and soundFlag == False):
                #play sound
                step_sound.play()
                #set loop flags to delay game and prevent spammed steps
                soundFlag = True
                passFlag = True
                #set the delay timer
                timer = pygame.time.get_ticks()
                #check for if full steps has been updated
                if(not full_step_flag and full_steps_count + 1 <= total_step_count):
                    #update full steps
                    full_steps_count += 1
                    full_step_flag = True

            #update the prev_steps
            prev_left = l_trig
            prev_right = r_trig

            #display a congrats message if a full step is met
            if timer > 0:
                congrats_text = font.render("Bottle Filled!", True, GREEN)
                #display the message
                screen.blit(congrats_text, (INITIAL_WIDTH // 2 - congrats_text.get_width() // 2, INITIAL_HEIGHT // 2))

            #check for negative step value
            if(step < 0):
                #set the step value to zero for proper display
                step = 0
                #reset the step flag
                full_step_flag = False

            #collect the stretched screen data
            stretched_screen = pygame.transform.scale(base_surface, (screen.get_width(), screen.get_height()))
            #display the screen
            screen.blit(stretched_screen, (0, 0))

            #update screen
            pygame.display.flip()

            #set game clock
            clock.tick(FPS)
    #return step counts for proper display
    return total_step_count, full_steps_count

#call the start menu to start the game
main_menu()
