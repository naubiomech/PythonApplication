import asyncio
import struct
import sys
from Device import realTimeProcessor
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
        self.scanResults = None
        # UUID characteristic 
        self.UART_TX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"                                 #Nordic NUS characteristic for TX
        self.UART_RX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"                                 #Nordic NUS characteristic for RX
        self.UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"                            #Nordic Service UUID
        # Joint dictionary to map menu selection to joint ID
        self.jointDictionary = {
            1 : 33.0,
            2 : 65.0,
            3 : 34.0,
            4 : 66.0,
            5 : 36.0,
            6 : 68.0
        }

        self.isConnected = False

    def set_scan_results(self, scans):
        self.scanResults = scans

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
    
    # Callback function to disconnect exo from system
    def handleDisconnect(self, _: BleakClient):
        self.isConnected = False
        print("Device was disconnected")
        # cancelling all tasks effectively ends the program
        for task in asyncio.all_tasks():
            task.cancel()
    #-----------------------------------------------------------------------------
        
    async def startExoMotors(self):                                                                # Command to Exo to get motors on and ready to receive commands
        await asyncio.sleep(1)
        print("using bleak start\n")
        command = bytearray(b'E')
        char = self.get_char_handle(self.UART_TX_UUID)

        try:
            await self.client.write_gatt_char(char, command, False)
        except Exception as e:
            print(f"An error occurred: {e}")
    #-----------------------------------------------------------------------------
    
    async def calibrateTorque(self):                                                               # Command to calibrate the torque
        print("using bleak torque\n")
        command = bytearray(b'H')
        char = self.get_char_handle(self.UART_TX_UUID)

        await self.client.write_gatt_char(char, command, False)
    #-----------------------------------------------------------------------------
    
    async def calibrateFSRs(self):                                                                 # Command to calibrate FSR sensors
        print("using bleak FSR\n")
        command = bytearray(b'L')
        char = self.get_char_handle(self.UART_TX_UUID)

        await self.client.write_gatt_char(char, command, False)
    #-----------------------------------------------------------------------------
        
    async def motorOff(self):                                                                      # Command to turn off motors 
        command =  bytearray(b'w')
        char = self.get_char_handle(self.UART_TX_UUID)

        await self.client.write_gatt_char(char, command, True)
    #-----------------------------------------------------------------------------

    async def updateTorqueValues(self,parameter_list):                                             #jointKey, controller, parameter, value):

        totalLoops = 1
        loopCount = 0

        #check if bilateral
        if parameter_list[0] == True:
            totalLoops = 2
        while loopCount != totalLoops:                                                             # Loop if bilateral mode. No loop otherwise

            command = b'f'                                                                         # Set convert command 'f' into bytearray
            char = self.get_char_handle(self.UART_TX_UUID)
            await self.client.write_gatt_char(char,command,False)

            float_values = (parameter_list)

            for i in range (1, len(float_values)):
                if i == 1:
                    if loopCount == 1 and float_values[1]%2 == 0:                                   # check for second loop and if on right side
                        float_bytes = struct.pack('<d',self.jointDictionary[float_values[i]]-32)    # decriment joint ID by 32 (opposite joint is offset by 32)
                    elif loopCount == 1 and float_values[1]%2 != 0:                                 # otherwise check for left side and second loop
                        float_bytes = struct.pack('<d',self.jointDictionary[float_values[i]]+32)    # increment joint ID by 32 (opposite joint is offset by 32)
                    else:                                                                           # otherwise run joint ID that was inputed
                        float_bytes = struct.pack('<d',self.jointDictionary[float_values[i]])
                else:
                    float_bytes = struct.pack('<d',float_values[i])
                print(struct.unpack('<d',float_bytes))
                char = self.get_char_handle(self.UART_TX_UUID)
                await self.client.write_gatt_char(char,float_bytes,False)

            loopCount += 1
    #-----------------------------------------------------------------------------

    async def connect(self, device):
        print(device)
    
    async def scanAndConnect(self):                                                                             # Scan for BLE devices
        print("using bleak scan\n")
        print("Scanning...")
        self.set_device(await BleakScanner.find_device_by_filter(self.filterExo))                   # Filter devices for only Exos
        print(self.device)
        if self.device is None:                                                                     # No devices found from filter
            print("No matching device found.")
            return
        self.set_client(BleakClient(self.device, disconnected_callback=self.handleDisconnect))      # Set client and diconnect callback
        await self.client.connect()                                                                 # Connect to Exo

        self.isConnected = True
        print("is exo connected: " + str(self.isConnected))

        print(self.client)
        self.set_services(await self.client.get_services())                                         # Get list of services from Exo
        await self.client.start_notify(self.UART_RX_UUID, self.DataIn)                              # Start incoming data stream
    #-----------------------------------------------------------------------------

    async def sendFsrValues(self, fsrValList):                                                      # Send FSR values to Exo
        command = bytearray(b'R')
        char = self.get_char_handle(self.UART_TX_UUID)

        fsrVals = fsrValList
        for i in range (0, len(fsrVals)):
            fsr_bytes = struct.pack('<d',fsrVals[i])
            char = self.get_char_handle(self.UART_TX_UUID)
            await self.client.write_gatt_char(char,fsr_bytes,False)
    #-----------------------------------------------------------------------------
    
    async def stopTrial(self):                                                                      # Send stop trial command
        command  = bytearray(b'G')
        char = self.get_char_handle(self.UART_TX_UUID)

        await self.client.write_gatt_char(char, command, False)
    #-----------------------------------------------------------------------------

    async def switchToAssist(self):                            
        command = bytearray(b'c')
        char = self.get_char_handle(self.UART_TX_UUID)
        
        await self.client.write_gatt_char(char, command, False)
        print("using bleak assist\n")
    #-----------------------------------------------------------------------------
        
    async def switchToResist(self):                                                                 # Send switch to resist command
        print("using bleak resist\n")
        command = bytearray(b'S')
        char = self.get_char_handle(self.UART_TX_UUID)
        
        await self.client.write_gatt_char(char, command, False)
    #-----------------------------------------------------------------------------
