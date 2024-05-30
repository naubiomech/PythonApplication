import asyncio
import DataToCsv

# Options during trial. Change torque settings or end trial
def trialMenu():
       while True:
        print("""
------------------------
|1. Update Torque      |
|2. End Trial          |
------------------------""")
        option = int(input())
        if option == 1 or option == 2:
            return option
        print("Choose a valid option")

# Options for updating the torque settings 
def updateTorqueMenu():
    print("Run in Bilateral Mode? (y/n): ")     # Choosing yes runs both exo joints with the same settings at once. No only updates selected joint
    bilateralOption = input()
    while True:
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
        if joint >= 1 and joint <= 6:
            break
        print("Choose a valid option")
    print("Enter Controller Number: ")
    controller = float(input())
    print("Enter Parameter: ")
    parameter = float(input())
    print("Enter Value: ")
    value = float(input())

    # check for bilateral                         Type y, Y, or hit enter to select yes for bilateral
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

        await deviceManager.calibrateTorque()
    #-----------------------------------------------------------------------------

    async def beginTrial(self, deviceManager):  # Start trial and send initial torque commands
        print("Starting trial...")
        await asyncio.sleep(1)
        await deviceManager.startExoMotors()    # Sets Exo motors to receive commands
        print("start motors\n")

        await deviceManager.calibrateFSRs()     # Begins Exo calibration 
        print("calibrate fsr\n")
                                                # Send FSR value to Exo FSR
        await deviceManager.sendFsrValues([0.30, 0.30])
    #-----------------------------------------------------------------------------

    async def systemUpdate(self, deviceManager):  # Handles Next Steps After Baseline 

        menuSelection = int(trialMenu())        # Ensure to enter loop at least once
        while menuSelection != 2:               # Keep getting torque values until end trial
            parameter_list = updateTorqueMenu() # Menu for updating torque

            await deviceManager.updateTorqueValues(parameter_list)  # Send torque values to Exo

            menuSelection = int(trialMenu())    # Get trial menu for loop

        # End trial
        await deviceManager.motorOff()          # Turn off motors
        await deviceManager.stopTrial()         # Tell Exo to end trial
        deviceManager.handleDisconnect(deviceManager.client)    # Disconnect from Exo
        self.loadDataToCSV(deviceManager)       # Load data from Exo into CSV 
    #-----------------------------------------------------------------------------

    # Loads exo data into csv
    def loadDataToCSV(self, deviceManager):
        self.csvWriter.writeToCsv(deviceManager._realTimeProcessor._exo_data)