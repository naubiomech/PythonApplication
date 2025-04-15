import socket
import time
import threading
from Device import realTimeProcessor  # Ensure correct path
from Games import virtualController  # Import base class

class MacVirtualController(virtualController.VirtualController):
    """
    A subclass of VirtualController for macOS that sends controller input
    values over a socket instead of using vgamepad.
    """

    def __init__(self, realTimeProcessor, sensorID, host='127.0.0.1', port=5005):
        super().__init__(realTimeProcessor, sensorID)
        self.host = host
        self.port = port
        self.sock = None

    def create(self):
        """Set up the socket and start sending sensor data."""
        print("Creating Mac virtual controller...")

    def stop(self):
        """Stop sending data and close the socket."""
        print("Stopping Mac virtual controller...")

    def update_loop(self):
        self._isOn = True
        while self._isOn:
            print("Updating Mac virtual controller...")
            time.sleep(0.01)
