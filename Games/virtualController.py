import vgamepad as vg
import time
import threading
from Device import realTimeProcessor  # Ensure correct import path

# Virtual Controller class
class VirtualController:
    """
    A class to represent a virtual controller that maps biofeedback sensor data
    to game controller inputs.
    """
    # used to give/remove user assistance from a researcher when needed, 1.0 is no change at all
    user_assistance = 1.0
    # the amount of assistance to give or remove
    assistance_diference = 0.05

    

    def __init__( self, realTimeProcessor, sensorID ):
        
        self._sensorID = sensorID
        self._gamepad = None  # Initialize the virtual gamepad
        self._realTimeProcessor = realTimeProcessor
        self._isOn = False
        self.update_thread = None

        # active sensor 
        self.sensor_left = 6 
        self.sensor_right = 7 # sensor 6 and 7 and the foot sensors and will be the default

        print("Virtual controller initialized.", self._realTimeProcessor.getPayloadData())

    def addAssistance(self):
        """Add assistance to the user."""
        self.user_assistance += self.assistance_diference
        print("User assistance added." + str(self.user_assistance))

    def removeAssistance(self):
        """Remove assistance from the user."""
        self.user_assistance -= self.assistance_diference
        print("User assistance removed." + str(self.user_assistance))

    def setAssistanceLevel(self, level):
        """Set the user assistance level."""
        self.user_assistance = level
        print("User assistance level set to: " + str(self.user_assistance))
        
    def getAssistanceLevel(self):
        """Get the current user assistance level."""
        return self.user_assistance
    
    def stop(self):
        """Stop the virtual controller."""
        if self._isOn:
            self._isOn = False
            self.update_thread.join()
            print("Virtual controller stopped.")
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
                print("Invalid sensor data received:", sensor_data)
                time.sleep(0.1)
                continue

            # the user's raw sensor data is normalized to 1.0, so...
            # Scale the sensor data to the controller trigger inputs (0-255) 
            # NOTE : The scalling factor will change based on the user's set goals. 
            #        Games will always require a trigger pull value of 180.
            # NOTE : For demo purposes, we are using the right and left two foot sensor values

            # Assistance can be added by the researcher to make the game easier/harder for the user

            left_sensor = max(0, min(sensor_data[self.sensor_left] * 180 * self.user_assistance, 255))
            right_sensor = max(0, min(sensor_data[self.sensor_right] * 180 * self.user_assistance, 255))
            
            # verbose for debugging
            if True:
                print(f"Left trigger: {left_sensor}, Right trigger: {right_sensor}")
                print(f"left Sensor: {sensor_data[6]}, right sensor: {sensor_data[7]}")

            # Set the trigger inputs based on the scaled sensor data
            self._gamepad.left_trigger(value=int(left_sensor))
            self._gamepad.right_trigger(value=int(right_sensor))

            # Update the controller state
            self._gamepad.update()

            # Wait for 100ms before the next update
            time.sleep(0.001)

    
    
        
            

