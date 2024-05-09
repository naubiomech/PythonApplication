import asyncio
import struct
import sys
import realTimeProcessor
import numpy as np
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

class ExoDeviceManager() :

    def __init__(self):
        self._realTimeProcessor = realTimeProcessor.RealTimeProcessor()
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

        self.isConnected = False

    def set_device(self, deviceVal):
        self.device = deviceVal

    def set_client(self, clientVal):
        self.client = clientVal
    
    def set_services(self, servicesVal):
        self.services = servicesVal

    async def DataIn(self, sender: BleakGATTCharacteristic, data: bytearray):
        self._realTimeProcessor.processEvent(data)

    def get_char_handle(self, char_UUID):
        return self.services.get_service(self.UART_SERVICE_UUID).get_characteristic(char_UUID)

    def filterExo(self, device: BLEDevice, adv: AdvertisementData):
        # This assumes that the device includes the Advanced control service in the
        # advertising data. This test may need to be adjusted depending on the
        # actual advertising data supplied by the device.
        if self.UART_SERVICE_UUID.lower() in adv.service_uuids:
            return True

        return False
    #-----------------------------------------------------------------------------
    
    def handleDisconnect(self, _: BleakClient):
        self.isConnected = False
        print("is exo connected: " + str(self.isConnected))
        print("Device was disconnected")
        # cancelling all tasks effectively ends the program
        for task in asyncio.all_tasks():
            task.cancel()
    #-----------------------------------------------------------------------------
            
    async def startExoMotors(self):
        await asyncio.sleep(1)
        print("using bleak start\n")
        print("is exo connected: " + str(self.isConnected))
        command = bytearray(b'E')
        print(list(command))
        char = self.get_char_handle(self.UART_TX_UUID)

        try:
            await self.client.write_gatt_char(char, command, False)
        except Exception as e:
            print(f"An error occurred: {e}")
    #-----------------------------------------------------------------------------
    
    async def calibrateTorque(self):              # Command to calibrate the torque
        print("using bleak torque\n")
        print("is exo connected: " + str(self.isConnected))
        command = bytearray(b'H')
        char = self.get_char_handle(self.UART_TX_UUID)

        await self.client.write_gatt_char(char, command, False)
    #-----------------------------------------------------------------------------
    
    async def calibrateFSRs(self):                # Command to calibrate FSR sensors
        print("using bleak FSR\n")
        print("is exo connected: " + str(self.isConnected))
        command = bytearray(b'L')
        char = self.get_char_handle(self.UART_TX_UUID)

        await self.client.write_gatt_char(char, command, False)
    #-----------------------------------------------------------------------------
        
    async def motorOff(self):
        command =  bytearray(b'w')
        char = self.get_char_handle(self.UART_TX_UUID)

        await self.client.write_gatt_char(char, command, True)
    #-----------------------------------------------------------------------------

    async def updateTorqueValues(self,parameter_list): #jointKey, controller, parameter, value):

        totalLoops = 1
        loopCount = 0

        while loopCount != totalLoops:

            command = b'f'
            char = self.get_char_handle(self.UART_TX_UUID)
            await self.client.write_gatt_char(char,command,False)

            float_values = (parameter_list)

            for i in range (0, len(float_values)):
                float_bytes = struct.pack('<d',float_values[i])
                print(struct.unpack('<d',float_bytes))
                char = self.get_char_handle(self.UART_TX_UUID)
                await self.client.write_gatt_char(char,float_bytes,False)

            loopCount += 1
    #-----------------------------------------------------------------------------
            
    # async def setTorque(self, initialTorque):
    #     command = bytearray(b'F')  # send to command to initiate torque update

    #     await self.client.write_gatt_char(self.UART_TX_UUID, command)
    #     await asyncio.sleep(0.1)

    #     for torqueVal in initialTorque:
    #         command = struct.pack('<d',torqueVal) # Set data to be what Exo expects
    #         await self.client.write_gatt_char(self.UART_TX_UUID, command)
    #         await asyncio.sleep(0.2)
    #-----------------------------------------------------------------------------
    
    async def scanAndConnect(self):
        print("using bleak scan\n")
        # print("is exo connected: " + str(self.isConnected))
        print("Scanning...")
        self.set_device(await BleakScanner.find_device_by_filter(self.filterExo))
        print(self.device)
        if self.device is None:
            print("No matching device found, you may need to edit the filter.")
            sys.exit(1)
        self.set_client(BleakClient(self.device, disconnected_callback=self.handleDisconnect))
        await self.client.connect()

        self.isConnected = True
        print("is exo connected: " + str(self.isConnected))

        print(self.client)
        self.set_services(await self.client.get_services())
        await self.client.start_notify(self.UART_RX_UUID, self.DataIn)
    #-----------------------------------------------------------------------------

    async def sendFsrValues(self, fsrValList):
        command = bytearray(b'R')
        char = self.get_char_handle(self.UART_TX_UUID)

        await self.client.write_gatt_char(char, command, False)

        fsrVals = fsrValList
        for i in range (0, len(fsrVals)):
            fsr_bytes = struct.pack('<d',fsrVals[i])
            #print(struct.unpack('<d',fsr_bytes))
            char = self.get_char_handle(self.UART_TX_UUID)
            await self.client.write_gatt_char(char,fsr_bytes,False)

        # command = struct.pack('<dd', 0.12, 0.12)
        # print(struct.unpack('<dd'))
        # await self.client.write_gatt_char(char, command, False)

        # for fsrVal in fsrValList:
        #     print(fsrVal)
        #     command = struct.pack('f', fsrVal) # Set data to be what Exo expects]
        #     await self.client.write_gatt_char(char, command, False)
        #     await asyncio.sleep(0.1)
    #-----------------------------------------------------------------------------
    
    async def stopTrial(self):
        command  = bytearray(b'G')
        char = self.get_char_handle(self.UART_TX_UUID)

        await self.client.write_gatt_char(char, command, False)
    #-----------------------------------------------------------------------------

    async def switchToAssist(self):
        print("is exo connected: " + str(self.isConnected))
        command = bytearray(b'c')
        char = self.get_char_handle(self.UART_TX_UUID)
        
        await self.client.write_gatt_char(char, command, False)
        print("using bleak assist\n")
    #-----------------------------------------------------------------------------
        
    async def switchToResist(self):
        print("using bleak resist\n")
        command = bytearray(b'S')
        char = self.get_char_handle(self.UART_TX_UUID)
        
        await self.client.write_gatt_char(char, command, False)
    #-----------------------------------------------------------------------------