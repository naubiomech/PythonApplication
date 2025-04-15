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
WIDTH, HEIGHT = 800, 600
FPS = 60

# colors
WHITE = (255, 255, 255)
GREY = (200, 200, 200)
PURPLE = (119,0,200)
GREEN = (0,255,0)
BLACK = (0,0,0)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Grape Stomp!")

#hard coded results section
results = pygame.Rect(300, 350, 200, 100)

#initialize the step counts for end game display
global total_step_count, full_steps_count

def scale_background(image, screen_width, screen_height):
    #calculate the scaling ratios
    width_ratio = screen_width / image.get_width()
    height_ratio = screen_height / image.get_height()
    #scale the image based on which ratio is larger
    scale = max(width_ratio, height_ratio)
    new_width = int(image.get_width() * scale)
    new_height = int(image.get_height() * scale)
    #rescale the image
    scaled_bg = pygame.transform.scale(image, (new_width, new_height))
    #find the centered position for the background
    bg_x = (screen_width - new_width) // 2
    bg_y = (screen_height - new_height) // 2
    #return the scaled background
    return scaled_bg, (bg_x, bg_y)

#function to update start menu buttons
def update_button_positions(screen_width):
    #button width = 200
    #button height = 100
    #margin = 50
    #calculate the total horizontal space between buttons
    total_buttons_width = 2 * 200 + 50
    #calculate the placement for start
    start_x = (screen_width - total_buttons_width) // 2
    start = pygame.Rect(start_x, 200, 200, 100)
    #calculate the placement for quit
    quit_button = pygame.Rect(start_x + 200 + 50, 200, 200, 100)
    return start, quit_button

#main menu function, should be running for full duration of game behind game screen
def main_menu():
    #set the screen variables as global
    global WIDTH, HEIGHT, screen
    #initialize starting values
    game_running = True
    total_step_count = 0
    full_steps_count = 0

    #get screen diemenstions
    current_width, current_height = screen.get_size()
    start, quit_button = update_button_positions(current_width)

    total_buttons_width = 2 * 200 + 50
    start_x = (current_width - total_buttons_width) // 2
    start = pygame.Rect(start_x, 200, 200, 100)
    quit_button = pygame.Rect(start_x + 200 + 50, 200, 200, 100)
    
    #begin main menu loop
    while game_running:
        for event in pygame.event.get():
            #check for user close window
            if event.type == pygame.QUIT:
                game_running = False

            #check for user resizing
            if event.type == pygame.VIDEORESIZE:
                #reset the screen width and height
                WIDTH, HEIGHT = event.w, event.h
                #reset the screen with new width/height
                start, quit_button = update_button_positions(event.w)
            #check for mouse position
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = event.pos
                #check for which button clicked
                if start.collidepoint(mouse):
                    total_step_count, full_steps_count = game()
                elif quit_button.collidepoint(mouse):
                    game_running = False
                    pygame.quit()
                    sys.exit()

        #display the screen as grey
        screen.fill(GREY)
        text = pygame.font.Font(None, 70)
        complete_text = text.render("Grape Stomp!", True, BLACK)
        #screen.blit(complete_text, (250, 100))        
        screen.blit(complete_text, (WIDTH // 2 - complete_text.get_width() // 2, 100))

        #create the buttons for the start menu
        pygame.draw.rect(screen, PURPLE, start)
        pygame.draw.rect(screen, PURPLE, quit_button)

        #display game controls
        text = pygame.font.Font(None, 30)
        controls_text = text.render("Move your legs to play and fill as many bottles as you can!", True, BLACK)
        screen.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, 350))
        text = pygame.font.Font(None, 30)
        controls_text = text.render('Press "esc" to exit and "p" to pause!', True, BLACK)
        screen.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, 380))

        #display the end game step counts
        if total_step_count > 0:
            #display the results header
            text = pygame.font.Font(None, 40)
            total_steps_results = text.render("Session Results:", True, (0, 0, 0))
            screen.blit(total_steps_results, (125, 460))
            #display the steps
            text = pygame.font.Font(None, 30)
            total_steps_results = text.render(f"Total Steps taken: {total_step_count}", True, (0, 0, 0))
            screen.blit(total_steps_results, (125, 500))
            full_steps_results = text.render(f"Full Steps taken: {full_steps_count}", True, (0, 0, 0))
            screen.blit(full_steps_results, (125, 525))


        #create the start button
        button_text = pygame.font.Font(None, 50)
        start_button_text = button_text.render("Start Game", True, BLACK)
        start_button = start_button_text.get_rect(center=start.center)
        screen.blit(start_button_text, start_button)

        #create the exit button
        exit_button_text = button_text.render(" Exit Game", True, BLACK)
        exit_button = exit_button_text.get_rect(center=quit_button.center)
        screen.blit(exit_button_text, exit_button)

        #check for buttons clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = event.pos

        pygame.display.flip()
        clock.tick(FPS)


#game loop function
def game():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    #set the screen variables as global
    global WIDTH, HEIGHT, screen

    # load the sprite sheet and define frame dimensions
    original_bg = pygame.image.load(os.path.join(BASE_DIR, "landscape.jpg"))
    bg, bg_pos = scale_background(original_bg, WIDTH, HEIGHT)
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
    player_x = WIDTH // 2 - 330
    player_y = HEIGHT - 645
    player_speed = 2
    font = pygame.font.SysFont(None, 36)

    #jug (juice) progress settings
    JUICE_WIDTH = 75
    JUICE_HEIGHT = 400
    juice_x = WIDTH - JUICE_WIDTH - 40
    juice_y = HEIGHT - 500

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
        cont = pygame.joystick.Joystick(0)
        cont.init()
        #display contoller success
        #print("\nController Successfully Connected!!\n")

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
            for event in pygame.event.get():
                #check for user close window
                if event.type == pygame.QUIT:
                    running = False

                #check for user resizing
                if event.type == pygame.VIDEORESIZE:
                    WIDTH, HEIGHT = event.w, event.h
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                    bg, bg_pos = scale_background(original_bg, WIDTH, HEIGHT)
                    juice_x = WIDTH - JUICE_WIDTH - 20

                    player_x = WIDTH // 2 - 330
                    player_y = HEIGHT - 645

                    #update the menu buttons on screen
                    start_x = (event.w - (2 * 200 + 50)) // 2
                    start = pygame.Rect(start_x, 200, 200, 100)
                    quit_button = pygame.Rect(start_x + 200 + 50, 200, 200, 100)

                #check for keyboard input
                if event.type == pygame.KEYDOWN:
                    #keyboard input for pause
                    if event.key == pygame.K_p:
                        pause = not pause

                    #keyboard input to quit game
                    if event.key == pygame.K_ESCAPE:
                        #get screen diemenstions
                        current_width, current_height = screen.get_size()
                        #reset the screen parameters
                        WIDTH, HEIGHT = current_width, current_height
                        bg, bg_pos = scale_background(original_bg, WIDTH, HEIGHT)
                        #stop the game  
                        running = False

            #check if full step conditions have been met
            if(passFlag):
                #check if the timer is active
                if timer > 0:
                    #check for timer complete
                    if pygame.time.get_ticks() - timer > 1000:
                        #reset step delay conditions
                        soundFlag = False
                        timer = 0
                        passFlag = False
                #skip screen updates while waiting
                continue               

            #check for pause menu
            if pause:
                input_box = pygame.Rect(175, 250, 300, 40)
                total_steps_box = pygame.Rect(175,315, 20, 20)
                full_steps_box = pygame.Rect(175,350, 20, 20)
                active_box = False
                input_text = ""
                #loop while paused
                while pause:
                    #get key events during pause
                    for event in pygame.event.get():
                        #handle OS exit button case
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()
                        
                        #check for click on text box
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            #check for active box
                            if input_box.collidepoint(event.pos):
                                active_box = True

                            #check for total steps toggle
                            elif total_steps_box.collidepoint(event.pos):
                                total_steps_toggle = not total_steps_toggle

                            #check for full step toggle
                            elif full_steps_box.collidepoint(event.pos):
                                full_steps_toggle = not full_steps_toggle

                            #otherwise assume no edit
                            else:
                                active_box = False

                        #handle key presses
                        if event.type == pygame.KEYDOWN and active_box == False:
                            #exit pause if p pressed
                            if event.key == pygame.K_p:
                                pause = False

                        #handle input text for max threshold
                        if event.type == pygame.KEYDOWN and active_box:
                            #check for end pause
                            if event.key == pygame.K_RETURN:
                                #attempt to set the threshold
                                try:
                                    #set the threshold
                                    step_thresh = float(input_text)
                                    #check of the step threshold is an acceptable range
                                    if 0.0 < step_thresh < 1.0:
                                        #display new threshold to console and stop pause
                                        print(f"Threshold set to: {input_text}")
                                        pause = False
                                    #otherwise display error
                                    else:
                                        print("ERROR: Please enter threshold between 0 and 1")
                                        step_thresh = 0.6
                                    
                                #handle non float inputs
                                except ValueError:
                                    #display error
                                    print("ERROR: Please enter threshold between 0 and 1")

                            #handle erasing text in the box
                            elif event.key == pygame.K_BACKSPACE:
                                #remove the last character
                                input_text = input_text[ :-1 ]
                            #otherwise display current input text
                            else:
                                #display text
                                input_text += event.unicode

                    #keep background to not disorient user
                    screen.blit(bg, bg_pos)
                    #display pause message
                    pause_msg = pygame.font.Font(None, 60)
                    pause_text = pause_msg.render("PAUSED", True, BLACK)
                    screen.blit(pause_text, (325, 100))
                    pause_msg = pygame.font.Font(None, 60)
                    pause_text = pause_msg.render('Press "P" to exit pause menu', True, BLACK)
                    screen.blit(pause_text, (120, 150))

                    #display area to edit step settings
                    settings = pygame.Rect(155, 200, 550, 200)
                    pygame.draw.rect(screen, GREY, settings)

                    #display input box instructions
                    instuction_msg = pygame.font.Font(None, 20)
                    instruction_text = instuction_msg.render("Please enter desired step threshold as a decimal between 0 and 1, default is 0.6", True, BLACK)
                    screen.blit(instruction_text, (175, 230))

                    #display total steps instructions
                    total_steps_instuction_msg = pygame.font.Font(None, 20)
                    total_steps_instruction_text = total_steps_instuction_msg.render("Toggle to show total steps taken", True, BLACK)
                    screen.blit(total_steps_instruction_text, (200, 320))

                    #display full steps instructions
                    full_steps_instuction_msg = pygame.font.Font(None, 20)
                    full_steps_instruction_text = full_steps_instuction_msg.render("Toggle to show total full steps taken", True, BLACK)
                    screen.blit(full_steps_instruction_text, (200, 355))                    

                    #display total steps toggle
                    pygame.draw.rect(screen, WHITE, total_steps_box, border_radius=4)
                    #check if total steps is toggled
                    if total_steps_toggle:
                        pygame.draw.rect(screen, PURPLE, total_steps_box, 20, border_radius=4)
                    #otherwise assume untoggled
                    else:
                        pygame.draw.rect(screen, WHITE, total_steps_box, 20, border_radius=4)


                    #display full steps toggle
                    pygame.draw.rect(screen, WHITE, full_steps_box, border_radius=4)
                    #check if box is selected
                    if full_steps_toggle:
                        pygame.draw.rect(screen, PURPLE, full_steps_box, 20, border_radius=4)
                    #otherwise assume untoggled
                    else:
                        pygame.draw.rect(screen, WHITE, full_steps_box, 20, border_radius=4)


                    #create text box for full step threshold
                    pygame.draw.rect(screen, WHITE, input_box, border_radius=4)
                    #check if box is selected
                    if active_box:
                        #display activated input box
                        pygame.draw.rect(screen, PURPLE, input_box, 2, border_radius=4)
                        #otherwise assume not entering threshold
                    else:
                        pygame.draw.rect(screen, BLACK, input_box, 2, border_radius=4)


                    #update display with current input box
                    font = pygame.font.Font(None, 36)
                    input_surface = font.render(input_text, True, BLACK)
                    screen.blit(input_surface, (input_box.x + 5, input_box.y + 5))

                    #update pause menu screen
                    pygame.display.flip()
                    clock.tick(FPS)
                    #keep displaying pause menu until disabled
                    continue

            # step progress bar
            pygame.draw.rect(screen, GREY, (juice_x, juice_y, JUICE_WIDTH, JUICE_HEIGHT),2)
            fill_height = juice_lvl * JUICE_HEIGHT
            fill_y = juice_y + JUICE_HEIGHT - fill_height
            pygame.draw.rect(screen, PURPLE, (juice_x + 2, fill_y, JUICE_WIDTH - 4, fill_height))

            #check for controller input
            l_trig = cont.get_axis(4)
            r_trig = cont.get_axis(5)
            exit_button = cont.get_button(2)

            #check for any controller input
            if (prev_left <= 0.1 and l_trig > 0.1):
                #increment total step count
                total_step_count += 1
                #check if step exceeded the step threshold
                if l_trig >= step_thresh:
                    #increment full step count
                    full_steps_count += 1

            #check for any controller input
            if (prev_right <= 0.1 and r_trig > 0.1):
                #increment total step count
                total_step_count += 1
                #check if step exceeded the step threshold
                if r_trig >= step_thresh:
                    #increment full step count
                    full_steps_count += 1                  

            #check for increase in step count
            if(total_step_count > prev_total_steps):
                #check for sprite left
                if(man_sprite == scaled_left):
                    #set new sprite
                    man_sprite = scaled_right

                #check for sprite right
                elif(man_sprite == scaled_right):
                    #set new sprite
                    man_sprite = scaled_left
                
                #update the new prev_total_steps
                prev_total_steps = total_step_count


            #condition to check for game exit
            elif exit_button:
                running = False

            #set the juice level to the step pressure value
            step = max(l_trig, r_trig)
            juice_lvl = step

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

            #draw juice level in the bottle
            fill_height = juice_lvl * JUICE_HEIGHT
            fill_y = juice_y + JUICE_HEIGHT - fill_height
            pygame.draw.rect(screen, PURPLE, (juice_x + 2, fill_y, JUICE_WIDTH - 4, fill_height))

            #set window background
            screen.blit(bg, (0,0))

            #draw the man stomping
            screen.blit(man_sprite, (player_x, player_y))

            #draw the barrel og grapes
            screen.blit(barrel, (player_x - 130,player_y + 340))
            

            #display total steps if toggled
            if total_steps_toggle:
                total_steps_text = font.render(f"Total Steps taken: {total_step_count}", True, (0, 0, 0))
                screen.blit(total_steps_text, (WIDTH // 2 - total_steps_text.get_width() // 2, 10))

            #display full steps if toggled
            if full_steps_toggle:
                full_steps_text = font.render(f"Full Steps taken: {full_steps_count}", True, (0, 0, 0))
                screen.blit(full_steps_text, (WIDTH // 2 - full_steps_text.get_width() // 2, 35))

            #display a congrats message if a full step is met
            if timer > 0:
                congrats_text = font.render("Keep Stomping!", True, GREEN)
                screen.blit(congrats_text, (WIDTH // 2 - congrats_text.get_width() // 2 + 30, HEIGHT // 2))
        
            #display progress bar (juice)
            pygame.draw.rect(screen, BLACK, (juice_x, juice_y, JUICE_WIDTH, JUICE_HEIGHT),2)
            fill_height = juice_lvl * JUICE_HEIGHT
            fill_y = juice_y + JUICE_HEIGHT - fill_height
            pygame.draw.rect(screen, PURPLE, (juice_x + 2, fill_y, JUICE_WIDTH - 4, fill_height))

            #calculate the threshold y value
            threshold_y = juice_y + JUICE_HEIGHT - (step_thresh * JUICE_HEIGHT)
            pygame.draw.line(screen, BLACK, (juice_x, threshold_y), (juice_x + JUICE_WIDTH, threshold_y), 8)

            #check for negative step value
            if(step < 0):
                #set the step value to zero for proper display
                step = 0
                #reset the step flag
                full_step_flag = False 

            #update screen
            pygame.display.flip()

            #set game clock
            clock.tick(FPS)

    return total_step_count, full_steps_count

#call the start menu to start the game
main_menu()
