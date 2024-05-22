import asyncio
import DataToCsv

def trialMenu():
       print("""
------------------------
|1. Update Torque      |
|2. End Trial          |
------------------------""")
       return input()

def updateTorqueMenu():
    print("Run in Bilateral Mode? (y/n): ")
    bilateralOption = input()
    print("Select Joint")
    print("""------------------
|1. Right Hip    |
|2. Left Hip     |
|3. Right Knee   |
|4. Left Knee    |
|5. Right Ankle  |
|6. Left Ankle   |
------------------""")
    joint = float(input())
    print("Enter Controller Number: ")
    controller = float(input())
    print("Enter Parameter: ")
    parameter = float(input())
    print("Enter Value: ")
    value = float(input())

    # check for bilateral
    if bilateralOption == 'y' or bilateralOption == "Y" or bilateralOption == "":
        isBilateral = True
    else: 
        isBilateral = False    

    return [isBilateral, joint, controller, parameter, value]

def lbsToKilograms(pounds):
    convertionConstant = 0.45359237             # Constant for converting lbs->kg
    return float(pounds) * convertionConstant

class ExoTrial:
    def __init__(self, isKilograms, weight, isAssist):
        self.csvWriter = DataToCsv.CsvWritter()
        self.isKilograms = isKilograms
        if not isKilograms:                     # Convert from lbs->kg if weight is in lbs
            self.weight = lbsToKilograms(weight)
        else:
            self.weight = weight
        self.isAssist = isAssist
    #-----------------------------------------------------------------------------
    
    async def calibrate(self, deviceManager):   # sends start motor command to Exo
        print(self.isKilograms, self.weight, self.isAssist)

        await deviceManager.calibrateTorque()
    #-----------------------------------------------------------------------------

    async def beginTrial(self, deviceManager):  # Start trial and send initial torque commands
        print("Starting trial...")
        await asyncio.sleep(1)
        await deviceManager.startExoMotors()    #
        print("start motors\n")

        await deviceManager.calibrateFSRs()   
        print("calibrate fsr\n")
        
        await deviceManager.sendFsrValues([0.30, 0.30])
    #-----------------------------------------------------------------------------

    async def systemUpdate(self, deviceManager):  # Handles Next Steps After Baseline 

        menuSelection = int(trialMenu())                       # Ensure to enter loop at least once
        while menuSelection != 2:                              # keep getting torque values until end trial
            parameter_list = updateTorqueMenu()

            await deviceManager.updateTorqueValues(parameter_list)

            menuSelection = int(trialMenu())

        await deviceManager.motorOff()
        await deviceManager.stopTrial()
        deviceManager.handleDisconnect(deviceManager.client)
        self.loadDataToCSV(deviceManager)
    #-----------------------------------------------------------------------------

    def loadDataToCSV(self, deviceManager):
        self.csvWriter.writeToCsv(deviceManager._realTimeProcessor._exo_data)