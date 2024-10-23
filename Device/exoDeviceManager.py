import asyncio
import struct
import sys

import numpy as np
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from Device import realTimeProcessor


class ExoDeviceManager:

    def __init__(self,on_disconnect=None):
        self._realTimeProcessor = realTimeProcessor.RealTimeProcessor()
        self.on_disconnect = on_disconnect  # Store the callback

        self.device = None
        self.client = None
        self.services = None
        self.scanResults = None
        self.disconnect_flag = False  # New disconnect flag
        self.characteristics = ""

        # Initialize FSR values
        self.curr_left_fsr_value = 0.25
        self.curr_right_fsr_value = 0.25

        self.device_mac_address = None

        # UUID characteristic
        # Nordic NUS characteristic for TX
        self.UART_TX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
        # Nordic NUS characteristic for RX
        self.UART_RX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
        self.UART_SERVICE_UUID = (
            "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"  # Nordic Service UUID
        )
        
        # Joint dictionary to map menu selection to joint ID
        self.jointDictionary = {
            1: 33.0,
            2: 65.0,
            3: 34.0,
            4: 66.0,
            5: 36.0,
            6: 68.0,
            7: 40.0,
            8: 72.0
        }

        self.isConnected = False

    def set_scan_results(self, scans):
        self.scanResults = scans

    def set_device(self, deviceVal):
        self.device = deviceVal
        #self.device_mac_address = deviceVal.address  # Save the MAC address for future use

    def set_client(self, clientVal):
        self.client = clientVal

    def set_services(self, servicesVal):
        self.services = servicesVal

    async def DataIn(self, sender: BleakGATTCharacteristic, data: bytearray):
        self._realTimeProcessor.processEvent(data)
        await self.MachineLearnerControl()


    async def MachineLearnerControl(self):
        if self._realTimeProcessor._predictor.modelExists: #if the machine model exists
            #print("Model Exists")
            if self._realTimeProcessor._predictor.controlMode==1: #if the mahine learning model authorized control
                #print("Machine Learning Mode Engaged")
                if self._realTimeProcessor._exo_data.Task[-2] != self._realTimeProcessor._predictor.prediction:
                    print("Prediction Changed") 
                    #check to see if current prediction has changed from previous prediction
                    if self._realTimeProcessor._predictor.prediction == 1: #if the state is level, medium stiffness
                        await self.sendStiffness(0.5)
                    elif self._realTimeProcessor._predictor.prediction == 2: #if state is descend, high stiffness (better braking?)
                        await self.sendStiffness(1)
                    elif self._realTimeProcessor._predictor.prediction == 3: #if state is ascend, low stiffness (maximum range of motion?)
                        await self.sendStiffness(0)
                    else:
                        await self.sendStiffness(0.5)
                    
                
            #else:
                #print("Manual Mode")

    def get_char_handle(self, char_UUID):
        return self.services.get_service(self.UART_SERVICE_UUID).get_characteristic(
            char_UUID
        )

    def filterExo(self, device: BLEDevice, adv: AdvertisementData):
        # This assumes that the device includes the Advanced control service in the
        # advertising data. This test may need to be adjusted depending on the
        # actual advertising data supplied by the device.
        if self.UART_SERVICE_UUID.lower() in adv.service_uuids:
            return True

        return False

    # -----------------------------------------------------------------------------

    # Callback function to disconnect exo from system
    def handleDisconnect(self, _: BleakClient):
        print("Disconnecting...")  # Check if this is reached
        if self.on_disconnect:
            print("Calling disconnect callback...")
            self.on_disconnect()
        else:
            print("No disconnect callback assigned.")


    # Command to Exo to get motors on and ready to receive commands
    async def startExoMotors(self):
        await asyncio.sleep(1)
        print("using bleak start\n")
        command = bytearray(b"E")
        char = self.get_char_handle(self.UART_TX_UUID)

        try:
            await self.client.write_gatt_char(char, command, False)
        except Exception as e:
            print(f"An error occurred: {e}")

    # -----------------------------------------------------------------------------

    # Command to calibrate the torque
    async def calibrateTorque(self):
        print("using bleak torque\n")
        command = bytearray(b"H")
        char = self.get_char_handle(self.UART_TX_UUID)

        await self.client.write_gatt_char(char, command, False)

    # -----------------------------------------------------------------------------

    # Command to calibrate FSR sensors
    async def calibrateFSRs(self):
        print("using bleak FSR\n")
        command = bytearray(b"L")
        char = self.get_char_handle(self.UART_TX_UUID)

        await self.client.write_gatt_char(char, command, False)

    # -----------------------------------------------------------------------------

    # Command to turn off motors
    async def motorOff(self):
        command = bytearray(b"w")
        char = self.get_char_handle(self.UART_TX_UUID)

        await self.client.write_gatt_char(char, command, True)

    # -----------------------------------------------------------------------------

    # jointKey, controller, parameter, value):
    async def updateTorqueValues(self, parameter_list):
        totalLoops = 1
        loopCount = 0
        float_values = parameter_list

        # check if bilateral
        if parameter_list[0] is True:
            totalLoops = 2
        # Loop if bilateral mode. No loop otherwise
        while loopCount != totalLoops:

            # Set convert command 'f' into bytearray
            command = b"f"
            char = self.get_char_handle(self.UART_TX_UUID)
            await self.client.write_gatt_char(char, command, False)

            for i in range(1, len(float_values)):
                if i == 1:
                    # check for second loop and if on right side
                    if loopCount == 1 and float_values[1] % 2 == 0:
                        # decriment joint ID by 32 (opposite joint is offset by 32)
                        print(f"joint: {self.jointDictionary[float_values[i]] - 32}")
                        float_bytes = struct.pack(
                            "<d", self.jointDictionary[float_values[i]] - 32
                        )
                    # otherwise check for left side and second loop
                    elif loopCount == 1 and float_values[1] % 2 != 0:
                        # increment joint ID by 32 (opposite joint is offset by 32)
                        print(f"joint: {self.jointDictionary[float_values[i]] + 32}")
                        float_bytes = struct.pack(
                            "<d", self.jointDictionary[float_values[i]] + 32
                        )
                    # otherwise run joint ID that was inputed
                    else:
                        print(f"joint: {self.jointDictionary[float_values[i]]}")
                        float_bytes = struct.pack(
                            "<d", self.jointDictionary[float_values[i]]
                        )
                else:
                    print(float_values[i])
                    float_bytes = struct.pack("<d", float_values[i])
                char = self.get_char_handle(self.UART_TX_UUID)
                await self.client.write_gatt_char(char, float_bytes, False)

            loopCount += 1

    # -----------------------------------------------------------------------------

    async def connect(self, device):
        print(device)

    # Scan for BLE devices
    async def scanAndConnect(self):
        print("using bleak scan\n")
        print("Scanning...")
        # Filter devices for only Exos
        self.set_device(await BleakScanner.find_device_by_filter(self.filterExo))
        print(self.device)
        
        # No devices found from filter
        if self.device is None:
            print("No matching device found.")
            return
        # Set client and diconnect callback
        self.set_client(
            BleakClient(self.device, disconnected_callback=self.handleDisconnect)
        )
        # Connect to Exo
        await self.client.connect()

        self.isConnected = True
        print("is exo connected: " + str(self.isConnected))

        print(self.client)
        # Get list of services from Exo
        self.set_services(await self.client.get_services())
        # Start incoming data stream
        await self.client.start_notify(self.UART_RX_UUID, self.DataIn)

    # -----------------------------------------------------------------------------

    # Send FSR values to Exo
    async def sendFsrValues(self, left_fsr, right_fsr):
        command = bytearray(b"R")  # Command to indicate sending FSR values
        char = self.get_char_handle(self.UART_TX_UUID)
        
        # Update the stored values
        self.curr_left_fsr_value = left_fsr
        self.curr_right_fsr_value = right_fsr

        # Send the command to indicate that we are sending FSR values
        await self.client.write_gatt_char(char, command, False)

        # Pack the left and right FSR values as doubles
        for fsr_value in (left_fsr, right_fsr):  # Loop over both values
            fsr_bytes = struct.pack("<d", fsr_value)  # Pack each value as double
            await self.client.write_gatt_char(char, fsr_bytes, False)
    # -----------------------------------------------------------------------------

    async def sendPresetFsrValues(self):
        await self.sendFsrValues(self.curr_left_fsr_value, self.curr_right_fsr_value)

    # Send stop trial command
    async def stopTrial(self):
        command = bytearray(b"G")
        char = self.get_char_handle(self.UART_TX_UUID)

        await self.client.write_gatt_char(char, command, False)

    # -----------------------------------------------------------------------------

    async def switchToAssist(self):
        command = bytearray(b"c")
        char = self.get_char_handle(self.UART_TX_UUID)

        await self.client.write_gatt_char(char, command, False)
        print("using bleak assist\n")

    # -----------------------------------------------------------------------------

    # Send switch to resist command
    async def switchToResist(self):
        print("using bleak resist\n")
        command = bytearray(b"S")
        char = self.get_char_handle(self.UART_TX_UUID)

        await self.client.write_gatt_char(char, command, False)

    # ----------------------------------------------------------------------------
    
    # Send stiffness values to Exo
    async def sendStiffness(self, stiffness):
        command = bytearray(b"A") #character code, keyed to Arduino software
        char = self.get_char_handle(self.UART_TX_UUID)
        await self.client.write_gatt_char(char, command, False) #send the command code

        stiff_bytes= struct.pack("<d", stiffness)
        await self.client.write_gatt_char(char, stiff_bytes, False) #followed by our data
        print(f"Stiffness is {stiffness}")
   
    # -----------------------------------------------------------------------------
    
    # Send stiffness values to Exo, helper function 
    async def newStiffness(self, stiffnessInput):
        stiffnessVal = float(stiffnessInput.get(1.0, "end-1c"))
        await self.sendStiffness(stiffnessVal) #send the command code
        
    # -----------------------------------------------------------------------------