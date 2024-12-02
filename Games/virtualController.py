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

    def __init__( self, realTimeProcessor, sensorID ):
        
        self._sensorID = sensorID
        self._gamepad = vg.VX360Gamepad()  # Initialize the virtual gamepad
        self._realTimeProcessor = realTimeProcessor
        self._isOn = False
        self.update_thread = None
        print("Virtual controller initialized.", self._realTimeProcessor.getPayloadData())

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

            # Scale the sensor data to the controller trigger inputs (0-255) 
            # NOTE: For demo purposes, we are using the right and left two foot sensor values
            left_sensor = max(0, min(sensor_data[6] * 180, 255))
            right_sensor = max(0, min(sensor_data[7] * 180, 255))
            
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
            time.sleep(0.5)

    
    
        
            

