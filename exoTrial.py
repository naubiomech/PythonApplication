import asyncio

def trialMenu():
       print("""
---------------------
|1. Update Torque   |
|2. End Trial       |
---------------------""")
       return input()

def updateTorqueMenu():
    print("Enter Controller Number: ")
    controller = int(input())
    print("Enter Parameter: ")
    parameter = int(input())
    print("Enter Index: ")
    index = int(input())
    print("Enter Value: ")
    value = int(input())

    return [controller, parameter, index, value]

def lbsToKilograms(pounds):
    convertionConstant = 0.45359237             # Constant for converting lbs->kg
    return pounds * convertionConstant

class ExoTrial:
    def __init__(self, isKilograms, weight, isAssist):
        self.isKilograms = isKilograms
        if not isKilograms:                     # Convert from lbs->kg if weight is in lbs
            self.weight = lbsToKilograms(weight)
        else:
            self.weight = weight
        self.isAssist = isAssist
    #-----------------------------------------------------------------------------
    
    async def calibrate(self, deviceManager):   # sends start motor command to Exo
        print(self.isKilograms, self.weight, self.isAssist)
        await deviceManager.startExoMotors()
    #-----------------------------------------------------------------------------

    async def beginTrial(self, deviceManager):  # Start trial and send initial torque commands
        print("Starting trial...")
        await asyncio.sleep(1)

        menuSelection = 1
        while menuSelection == 1:               # keep getting torque values until end trial
            await deviceManager.calibrateTorque()
            if self.isAssist:
                await deviceManager.switchToAssist()
            else:
                await deviceManager.switchToResist()

            await deviceManager.updateTorqueValues(updateTorqueMenu())
            print("Updating  torque values...")
            await asyncio.sleep(1)

            menuSelection = int(trialMenu())

        await deviceManager.stopTrial()
    #-----------------------------------------------------------------------------
