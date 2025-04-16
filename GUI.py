import tkinter as tk
import platform
from tkinter import messagebox 
from async_tkinter_loop import async_handler, async_mainloop

from Device import exoDeviceManager, exoTrial
from views.activeTrial import ActiveTrial
from views.activeTrialSettings import UpdateTorque
from views.bioFeedback import BioFeedback
from views.machineLearning import MachineLearning
from Games.virtualController import VirtualController, MacSocketController

from views.scanWindow import ScanWindow

class ControllerApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trial = exoTrial.ExoTrial(True, 1, True)
        self.deviceManager = exoDeviceManager.ExoDeviceManager()
        # Initialize the virtual controller, giving it the real time processor and sensor ID
        if platform.system() != "Darwin":
            # Is a windows/linux system
            self.virtualController = VirtualController(self.deviceManager._realTimeProcessor, 1)
        else:
            # Is a macOS system
            self.virtualController = MacSocketController(self.deviceManager._realTimeProcessor, 1)
        self.title("OpenExo GUI V1.01")
        self.geometry("920x720")
        self.minsize(900, 700)

        # Set up a key binding for the Esc key
        self.bind("<Escape>", async_handler(self.on_escape_pressed))

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # Names of each frame goes here
        for F in (ScanWindow, ActiveTrial, UpdateTorque, BioFeedback, MachineLearning):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.current_frame = "ScanWindow"  # Track the current frame
        self.show_frame("ScanWindow")  # Switch to Scan Window Frame

    def show_frame(self, page_name):  # Method to switch frames
        # Stop plot updates for any frame that has ongoing plotting
        for frame_name, frame in self.frames.items():
            if hasattr(frame, "hide"):
                frame.stop_plot_updates()
                print(f"Stopped plot updates for {frame_name}")

        # Get the frame to switch to
        frame = self.frames[page_name]
        self.current_frame = page_name  # Update the current frame

        # Set the new frame to be shown
        frame.tkraise()

        # Additional logic for the ActiveTrial or similar frames that need specific handling
        if hasattr(frame, "show"):
            frame.show()

        # Set the disconnect handler for the new frame
        disconnect_handler_name = f"{page_name}_on_device_disconnected"
        self.deviceManager.on_disconnect = getattr(frame, disconnect_handler_name, None)

    def change_title(self, newName):
        self.title(newName)
    
    async def on_escape_pressed(self, event):
        """Handle Esc key press."""
        if self.current_frame == "ScanWindow":
            self.destroy()  # Close the program
        else:
            # Ask for confirmation
            confirm = messagebox.askyesno(
                "Confirmation",
                "Do you want to navigate back to the Scan Window? The data will be saved."
            )
            if confirm:
                await self.end_trial_and_shutdown()
    

    async def end_trial_and_shutdown(self):
        """Shut down the exoskeleton and navigate to the ScanWindow."""
        try:
            # Shut down the exoskeleton
            await self.deviceManager.motorOff()  # Turn off motors
            await self.deviceManager.stopTrial()  # Stop the trial

            # Save trial data to CSV
            self.trial.loadDataToCSV(self.deviceManager)
            print("Exoskeleton shut down and data saved.")
        except Exception as e:
            print(f"Error during shutdown: {e}")

        # Navigate to ScanWindow
        self.show_frame("ScanWindow")
        
def exec():
    controller = ControllerApp()
    async_mainloop(controller)


if __name__ == "__main__":
    exec()
