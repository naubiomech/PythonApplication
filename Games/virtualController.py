import socket
import json
import sys
import os
import platform
# Add the parent directory to the system path
if platform.system() != "Darwin":
    # macOS
    import vgamepad as vg
import time
import threading
from Device import realTimeProcessor  # Ensure correct import path

DEBUG = False  # Set to True for debugging output

# Virtual Controller class
class VirtualController:
    """
    A class to represent a virtual controller that maps biofeedback sensor data
    to game controller inputs.
    """
    # used to give/remove user assistance from a researcher when needed, 1.0 is no change at all
    user_target = 1.0
    # the amount of assistance to give or remove
    assistance_diference = 0.05

    

    def __init__( self, realTimeProcessor, sensorID ):
        
        self._sensorID = sensorID
        self._gamepad = None  # Initialize the virtual gamepad
        self._realTimeProcessor = realTimeProcessor
        self._isOn = False
        self.update_thread = None

        # active sensor
        self.sensor = "none"          # used to change the active sensors
        self.sensor_left = 6  # sensor 6 and 7 and the foot sensors 
        self.sensor_right = 7 # and will be the default

        # when the trigger is pulled to the value "target_trigger" 
        # the game will register it as reaching a goal
        self.target_trigger = 155 

        print("Virtual controller initialized.", self._realTimeProcessor.getPayloadData())

    def addAssistance(self):
        """Add assistance to the user."""
        self.user_target += self.assistance_diference
        print("User assistance added." + str(self.user_target))

    def removeAssistance(self):
        """Remove assistance from the user."""
        self.user_target -= self.assistance_diference
        print("User assistance removed." + str(self.user_target))

    def setAssistanceLevel(self, level):
        """Set the user assistance level."""
        self.user_target = level
        print("User assistance level set to: " + str(self.user_target))
        
    def getAssistanceLevel(self):
        """Get the current user assistance level."""
        return self.user_target
    
    def setSensor(self, sensor):
        """Set the active sensor."""
        self.sensor = sensor
        
        case = self.sensor
        if case == "Left":
            # Use the left foot sensor (Left foot)
            self.sensor_left = 7
            self.sensor_right = 7

        elif case == "Right":
            # Use the right foot sensor (Right foot)
            self.sensor_left = 6
            self.sensor_right = 6

        elif case == "Left & Right":
            # Use the third two sensors (index 10 and 11)
            self.sensor_left = 6
            self.sensor_right = 6
            
        else:
            print("Invalid sensor index. Using default sensors.")
            self.sensor_left = 6
            self.sensor_right = 6
            print("No Sensor Changed.")
        print("Sensor set to: " + str(self.sensor))

    
    def stop(self):
        """Stop the virtual controller."""
        if self._isOn:
            self._isOn = False
            self._gamepad.disconnect()
            print("Virtual controller disconnected.")
            self.update_thread.join()
            print("Virtual controller Thread stopped.")
        else:
          print("No existing Virtual controller to stop.")

    def create(self):
        """Create and start the virtual controller."""
        self._gamepad = vg.VX360Gamepad()  # Create a virtual gamepad
        # check if the virtual controller is already running
        if self._isOn:
            print("No new Virtual controller created.")
            raise ValueError("The virtual controller is already running.")
        else:
          self._isOn = True
          print("Virtual controller created.")
          # Start the update loop in a separate thread
          self.update_thread = threading.Thread(target=self.update_loop)
          self.update_thread.daemon = True
          self.update_thread.start()

    
    """Update the virtual controller inputs with the current sensor data."""

    def update_loop(self):
        while self._isOn:
            # Get the sensor data
            sensor_data = self._realTimeProcessor.getPayloadData()  # Use sensor instance method
            if not isinstance(sensor_data, (list, tuple)) or len(sensor_data) < 9:
                time.sleep(0.1)
                continue

            # the user's raw sensor data is normalized to 1.0, so...
            # Scale the sensor data to the controller trigger inputs (0-255) 
            # NOTE : The scalling factor will change based on the user's set goals. 
            #        Games will always require a trigger pull value of 180.


            # Set target can be added by the researcher to make the game easier/harder for the user
            left_sensor = max(0, min((sensor_data[self.sensor_left] / self.user_target ) * self.target_trigger, 255))
            right_sensor = max(0, min((sensor_data[self.sensor_right] / self.user_target ) * self.target_trigger, 255))
            
            # verbose for debugging
            if DEBUG:
                print(f"Left trigger: {left_sensor}, Right trigger: {right_sensor}")
                print(f"left Sensor: {sensor_data[6]}, right sensor: {sensor_data[7]}")

            # Set the trigger inputs based on the scaled sensor data
            self._gamepad.left_trigger(value=int(left_sensor))
            self._gamepad.right_trigger(value=int(right_sensor))

            # Update the controller state
            self._gamepad.update()

            # Wait for 100ms before the next update
            time.sleep(0.01)

    

class MacSocketController(VirtualController):
    """
    A macOS-compatible virtual controller that acts as a server and sends data
    to connected clients over a socket.
    """

    def __init__(self, realTimeProcessor, sensorID, host="localhost", port=9999):
        super().__init__(realTimeProcessor, sensorID)
        self._host = host
        self._port = port
        self._server_socket = None
        self._client_socket = None
        self.server_thread = None  # Thread for running the server

    def create(self):
        """Start the server in a separate thread."""
        if self._isOn:
            print("No new Virtual controller created.")
            raise ValueError("The virtual controller is already running.")

        self._isOn = True
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.daemon = True  # Ensure the thread exits when the main program exits
        self.server_thread.start()
        print("MacSocketController server thread started.")
        
    def run_server(self):
        """Run the socket server to accept client connections."""
        try:
            # Create a server socket
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.bind((self._host, self._port))
            self._server_socket.listen(1)  # Listen for one client
            print(f"Server listening on {self._host}:{self._port}...")

            # Accept a client connection
            self._client_socket, client_address = self._server_socket.accept()
            print(f"Connection established with {client_address}")

            # Start the update loop to send data to the client
            self.update_thread = threading.Thread(target=self.update_loop)
            self.update_thread.daemon = True
            self.update_thread.start()

        except Exception as e:
            print(f"Socket server error: {e}")
            self.stop()

    def stop(self):
        """Stop the controller and close the socket."""
        if self._isOn:
            self._isOn = False
            self.update_thread.join()
            if self._client_socket:
                self._client_socket.close()
            if self._server_socket:
                self._server_socket.close()
            print("MacSocketController stopped.")
        else:
            print("No existing MacSocketController to stop.")

    def update_loop(self):
        """Send sensor data to the connected client."""
        while self._isOn:
            sensor_data = self._realTimeProcessor.getPayloadData()
            if not isinstance(sensor_data, (list, tuple)) or len(sensor_data) < 9:
                time.sleep(0.1)
                continue

            left_sensor = max(0, min((sensor_data[self.sensor_left] / self.user_target) * self.target_trigger, 255))
            right_sensor = max(0, min((sensor_data[self.sensor_right] / self.user_target) * self.target_trigger, 255))

            if DEBUG:
                print(f"Left trigger: {left_sensor}, Right trigger: {right_sensor}")

            # Send the values over the client socket
            try:
                payload = json.dumps({
                    "left_trigger": int(left_sensor),
                    "right_trigger": int(right_sensor)
                }).encode("utf-8")
                self._client_socket.sendall(payload + b"\n")
            except Exception as e:
                print(f"Socket send error: {e}")
                self.stop()
                break

            time.sleep(0.01)

        
            

