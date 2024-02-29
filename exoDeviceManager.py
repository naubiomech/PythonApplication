import asyncio
import struct
import sys
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

class ExoDeviceManager() :

    def __init__(self):
        self.device = None
        self.client = None
        self.services = None
        # UUID characteristic 
        self.UART_TX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e" #Nordic NUS characteristic for TX
        self.UART_RX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e" #Nordic NUS characteristic for RX
        self.UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E" #Nordic Service UUID
        # Joint dictionary
        self.jointDictionary = {
            1 : 33.0,
            2 : 65.0,
            3 : 34.0,
            4 : 66.0,
            5 : 36.0,
            6 : 68.0
        }

    def set_device(self, deviceVal):
        self.device = deviceVal

    def set_client(self, clientVal):
        self.client = clientVal
    
    def set_services(self, servicesVal):
        self.services = servicesVal

    def filterExo(self, device: BLEDevice, adv: AdvertisementData):
        # This assumes that the device includes the Advanced control service in the
        # advertising data. This test may need to be adjusted depending on the
        # actual advertising data supplied by the device.
        if self.UART_SERVICE_UUID.lower() in adv.service_uuids:
            return True

        return False
    #-----------------------------------------------------------------------------
    
    def handleDisconnect(self, _: BleakClient):
        print("Device was disconnected")
        # cancelling all tasks effectively ends the program
        for task in asyncio.all_tasks():
            task.cancel()
    #-----------------------------------------------------------------------------
            
    async def startExoMotors(self):
        command = bytearray(b'E')
        
        await self.client.write_gatt_char(self.UART_TX_UUID, command)
    #-----------------------------------------------------------------------------
    
    async def calibrateTorque(self):              # Command to calibrate the torque
        command = bytearray(b'H')

        await self.client.write_gatt_char(self.UART_TX_UUID, command)

        await asyncio.sleep(0.1)
    #-----------------------------------------------------------------------------
    
    async def calibrateFSRs(self):                # Command to calibrate FSR sensors

        command =  bytearray(b'L')

        await self.client.write_gatt_char(self.UART_TX_UUID, command)
    #-----------------------------------------------------------------------------
        
    async def motorOff(self):
        command =  bytearray(b'w')

        await self.client.write_gatt_char(self.UART_TX_UUID, command)
    #-----------------------------------------------------------------------------

    async def updateTorqueValues(self, jointKey, controller, parameter, value):
        totalLoops = 1
        loopCount = 0

        # if isBilateral:                         # if bilateral mode is on do two loops
        #     totalLoops = 2

        while loopCount != totalLoops:

            # # check if on second loop and if right joint
            # if loopCount == 1 and jointKey == 1 or jointKey == 3 or jointKey == 5:
            #     jointKey += 1                   # shift to left joint
            # # otherwise if on second loop and if left joint
            # elif loopCount == 1 and jointKey == 2 or jointKey == 4 or jointKey == 6:
            #     jointKey -= 1                   # shift to right joint

            command = bytearray(b'f')           # send to command to initiate torque update

            await self.client.write_gatt_char(self.UART_TX_UUID, command)
            await asyncio.sleep(0.1)

            # Pack values into list
            torqueList = [self.jointDictionary[jointKey], controller, parameter, value]

            # for each item in the list write to the exo
            for item in torqueList:
                print(item)
                command = struct.pack('<d', item) # Set data to be what Exo expects]
                print(command)
                await self.client.write_gatt_char(self.UART_TX_UUID, command)
                await asyncio.sleep(0.1)

            loopCount += 1
    #-----------------------------------------------------------------------------
            
    async def setTorque(self, initialTorque):
        command = bytearray(b'F')  # send to command to initiate torque update

        await self.client.write_gatt_char(self.UART_TX_UUID, command)
        await asyncio.sleep(0.1)

        for torqueVal in initialTorque:
            command = struct.pack('<d',torqueVal) # Set data to be what Exo expects
            await self.client.write_gatt_char(self.UART_TX_UUID, command)
            await asyncio.sleep(0.2)
    #-----------------------------------------------------------------------------
    
    async def scanAndConnect(self):
        print("Scanning...")
        self.set_device(await BleakScanner.find_device_by_filter(self.filterExo))
        print(self.device)
        if self.device is None:
            print("No matching device found, you may need to edit the filter.")
            sys.exit(1)
        self.set_client(BleakClient(self.device, disconnected_callback=self.handleDisconnect))
        await self.client.connect()
        print(self.client)
        self.set_services(self.client.services)
    #-----------------------------------------------------------------------------
    
    async def stopTrial(self):
        command  = bytearray(b'G')

        await self.client.write_gatt_char(self.UART_TX_UUID, command)
    
    async def switchToAssist(self):
        command = bytearray(b'c')
        
        await self.client.write_gatt_char(self.UART_TX_UUID, command)
    #-----------------------------------------------------------------------------
        
    async def switchToResist(self):
        command = bytearray(b'S')
        
        await self.client.write_gatt_char(self.UART_TX_UUID, command)
    #-----------------------------------------------------------------------------