import asyncio

def trialMenu():
       print("""
------------------------
|1. Update Torque      |
|2. Toggle Torque Type |
|3. End Trial          |
------------------------""")
       return input()

def updateTorqueMenu():
    print("Enter Joint Number: ")
    joint = int(input())
    print("Enter Controller Number: ")
    controller = int(input())
    print("Enter Parameter: ")
    parameter = int(input())
    print("Enter Value: ")
    value = int(input())

    return [joint, controller, parameter, value]

def lbsToKilograms(pounds):
    convertionConstant = 0.45359237             # Constant for converting lbs->kg
    return float(pounds) * convertionConstant

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

        #########################################
        if self.isAssist:                       # 
            await deviceManager.switchToAssist()#
        else:                                   # 
            await deviceManager.switchToResist()# Initial Exo Setup
                                                #
        await deviceManager.calibrateTorque()   #
        await deviceManager.setTorque([0,0,0,0])#
        #########################################

        menuSelection = 1                       # Ensure to enter loop at least once
        while menuSelection != 3:               # keep getting torque values until end trial
            if menuSelection == 2:              # If toggle torque was selected
                print("Changing from ")
                if self.isAssist:
                    self.isAssist = False
                    print("Assistance to Ressistance\n")
                    await deviceManager.switchToResist()
                    await asyncio.sleep(1)
                else:
                    self.isAssist = True
                    print("Ressistance to Assistance\n")
                    await deviceManager.switchToAssist()
                    await asyncio.sleep(1)
            
            elif menuSelection == 1:            # If update torque was selected
                
                await deviceManager.updateTorqueValues(updateTorqueMenu())
                print("Updating  torque values...")
                await asyncio.sleep(1)

            menuSelection = int(trialMenu())

        await deviceManager.stopTrial()
    #-----------------------------------------------------------------------------
