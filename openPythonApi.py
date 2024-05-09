# Lab of Biomechatronics Open Source Exoskeleton controller program.
# This program can connect to an Arduino Nano BLE 33 and
# controll the exoskeleton by sending commands that the 
# exoskeleon firmware interprets.
# Author: Payton Cox
# Date Created: Jan 2024
# Last updated: Jan 2024

import asyncio
import os
import sys
import struct
import time
import exoDeviceManager
import exoTrial

# UART88dbb-0055-4623-b92f-e2f0d3189767"
# OPEN_BLE_ID_CHAR_UUID = "ad788dbb-0055-4623-b92f-e2f0d3189768"
# OPEN_BLE_PARAM_CHAR_UUID = "ad788dbb-0055-4623-b92f-e2f0d3189769"
# OPEN_BLE_NODE_CHAR_UUID = "ad788dbb-0055-4623-b92f-e2f0d3189770"
# OPEN_BLE_NODE_COUNT_CHAR_UUID = "ad788dbb-0055-4623-b92f-e2f0d3189771"

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

# Menu to calibrate the exo before begining trial
def calibrationMenu():
    isKilograms = True
    weight = 1
    isAssist = True
#     isKilograms = True
#     print("""Calibration Menu
# ================\n
# Select weight unit
# -------------------------
# |1. Lbs                 |
# |2. Kg                  |
# -------------------------""")
#     weightUnit = int(input())
#     if weightUnit != 2:
#         isKilograms = False

#     print("Enter weight: ")
#     weight = input()

    print("""Enter torque type
-------------------------
|1. Assistance          |
|2. Resistance          |
-------------------------""")
    torqueType = int(input())
    if torqueType != 1:
        isAssist = False
    cls()
    return isKilograms, weight, isAssist
#-----------------------------------------------------------------------------

# Menu for actions to take upon connection
def connectedMenu():
    print("""-------------------------
|1. Calibrate           |
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

    while menuSelection != 2:

        # Scan and connect to an Exo
        deviceManager = exoDeviceManager.ExoDeviceManager()
        await deviceManager.scanAndConnect()

        # If connection is successful
        if deviceManager.client.is_connected:
            print("Connected!\n")
            connectedMenuSelection = connectedMenu()
            
            if (connectedMenuSelection == 1):           # start calibration
                cls()
                isKilograms, weight, isAssistance = calibrationMenu()
                trial = exoTrial.ExoTrial(isKilograms, weight, isAssistance)
                await trial.calibrate(deviceManager)   # Calibrate exo
                await trial.beginTrial(deviceManager)   # start trial
                await trial.systemUpdate(deviceManager)

        menuSelection = displayMenu()
        await asyncio.sleep(sleep_between_messages)

    print("Shutting down...")
    asyncio.sleep(2)
    cls()
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())