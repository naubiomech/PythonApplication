# Lab of Biomechatronics Open Source Exoskeleton controller program.
# This program can connect to an Arduino Nano BLE 33 and
# controll the exoskeleton by sending commands that the 
# exoskeleon firmware interprets.
# Author: Payton Cox
# Date Created: Jan 2024
# Last updated: May 2024

import asyncio
import os
import exoDeviceManager
import exoTrial

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

# Menu to calibrate the exo before begining trial.
#   The current system does not rely on a user weight 
#   or a predefined torque. If you would like to futher
#   modify this program to do so this is where it should 
#   be added in order to pass the data to the trial
#   class.
def calibrationMenu():
    isKilograms = True
    weight = 1
    isAssist = True
    cls()
    return isKilograms, weight, isAssist
#-----------------------------------------------------------------------------

# Menu for actions to take upon connection
def connectedMenu():
    print("""-------------------------
|1. Start Trial          |
-------------------------""")
    return int(input())

# Display menu and return what is entered
def displayMenu():
    print("""-------------------------
|1. Start Scan          |
|2. End program         |
-------------------------""")
    
    return int(input())
#-----------------------------------------------------------------------------

# Start up menu for UI purposes (Has no affect on the program)
async def startUpMenu():
    cls()
    print("Starting Exoskeleton Controller Program...\n")
    await asyncio.sleep(1)
#-----------------------------------------------------------------------------
       
async def main():
    sleep_between_messages = 0.1
    sages = 0.1

    # Initial display
    await startUpMenu() 

    # Set up Menu
    menuSelection = displayMenu()
    await asyncio.sleep(sleep_between_messages)

    # Run loop until end program is selected
    while menuSelection != 2:

        # Scan and connect to an Exo
        deviceManager = exoDeviceManager.ExoDeviceManager()
        await deviceManager.scanAndConnect()

        # If connection is successful
        if deviceManager.client.is_connected:
            print("Connected!\n")
            connectedMenuSelection = connectedMenu()
            
            if (connectedMenuSelection == 1):           # start calibration                   Currently start trial is the only option for the connectedMenu. If further customization is added
                cls()                                   #                                     simply extend the if statement
                # variables set on function return do not have effect on exo control currently
                isKilograms, weight, isAssistance = calibrationMenu()           
                trial = exoTrial.ExoTrial(isKilograms, weight, isAssistance)
                await trial.calibrate(deviceManager)    # Calibrate exo
                await trial.beginTrial(deviceManager)   # Start trial
                await trial.systemUpdate(deviceManager) # Update exo system after trial begins

        menuSelection = displayMenu()                   # show display menu once trial has ended
        await asyncio.sleep(sleep_between_messages)

    print("Shutting down...")                           # Shutdown
    asyncio.sleep(2)
    cls()
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())