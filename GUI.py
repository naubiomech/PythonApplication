import os
import asyncio
import threading
from tkinter import *
import tkinter as tk
from tkinter import ttk
from Device import exoDeviceManager

deviceManager = exoDeviceManager.ExoDeviceManager()

async def startScan():
    await deviceManager.scanAndConnect()
#---------------------------------------------------------------------------------------------------------------

class ControllerApp(tk.Tk):                                     # Controller to switch frames 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (ScanWindow, Calibrate, ActiveTrial, UpdateTorque):          # Names of each frame goes here
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("ScanWindow")                           # Switch to Scan Window Frame

    def show_frame(self, page_name):                            # Method to swithc frames
        frame = self.frames[page_name]
        frame.tkraise()
#---------------------------------------------------------------------------------------------------------------

class ScanWindow(tk.Frame):                                     # Main window for the app
    def __init__(self, parent, controller):                     # Frame Constructor
        super().__init__(parent)
        # Initialize variables
        self.controller = controller                            # Controller object to switch frames
        self.deviceNameText = StringVar()                       # String variable for device name text
        self.startTrialButton = None

        # creates page for class
        self.create_widgets()

    def create_widgets(self):                                   # Frame UI elements
        # Title label
        titleLabel = tk.Label(self, text="ExoSkeleton Controller", font=("Arial", 40))
        titleLabel.place(relx=.5, rely=.1, anchor=CENTER)
        # Start Scan label
        startScanLabel = tk.Label(self, text="Begin Scanning for Exoskeletons")
        startScanLabel.place(relx=.5, rely=.35, anchor=CENTER)

        # Start Scan button
        startScanButton = tk.Button(self, text="Start Scan", command=self.on_start_scan_button_clicked)
        startScanButton.place(relx=.5, rely=.45, anchor=CENTER)

        # Device name label
        self.deviceNameText.set("Not Connected")
        deviceNameLabel = tk.Label(self, textvariable=self.deviceNameText)
        deviceNameLabel.place(relx=.5, rely=.60, anchor=CENTER)

        # Start trial button (disabled untill device is scanned and connected)
        self.startTrialButton = tk.Button(self, text="Start Trial", command=lambda: self.controller.show_frame("Calibrate"),
                                     state=DISABLED)
        self.startTrialButton.place(relx=.75, rely=.8,)

    def on_start_scan_button_clicked(self):                     # Initiate scan
        self.deviceNameText.set("Scanning...")
        asyncio.run_coroutine_threadsafe(self.startScanButtonClicked(), asyncio.get_event_loop())

    async def startScanButtonClicked(self):                     # Start scanning and update screen
        await startScan()
        self.deviceNameText.set(deviceManager.device)
        self.startTrialButton.config(state="normal")
#---------------------------------------------------------------------------------------------------------------

class Calibrate(tk.Frame):                                      # Frame to start exo and calibrate
    def __init__(self, parent, controller):                     # Constructor for Frame
        super().__init__(parent)
        # Initialize variables
        self.controller = controller                            # Controller object to switch frames
        
        self.create_widgets()

    def create_widgets(self):                                   # Frame UI elements
        # Back button to go back to Scan Window
        backButton = tk.Button(self, text="Back",
                               command= lambda: self.controller.show_frame("ScanWindow"))
        backButton.place(relx= .05, rely= .05)

        # Calibrate Menu label
        calibrationMenuLabel = tk.Label(self, text="Calibration Menu", font=("Arial", 40))
        calibrationMenuLabel.place(relx= .5, rely= .1, anchor= CENTER)

        # Controller label
        controllerInputLabel = tk.Label(self, text= "Controller", font= ("Arial", 20))
        controllerInput = tk.Text(self, height= 2, width= 10)
        # Parameter Label
        parameterInputLabel = tk.Label(self, text= "Parameter", font= ("Arial", 20))
        parameterInput = tk.Text(self, height= 2, width= 10)
        # Value label
        valueInputLabel = tk.Label(self, text= "Value", font= ("Arial", 20))
        valueInput= tk.Text(self, height= 2, width= 10)

        controllerInputLabel.place(relx= .3, rely= .27)
        controllerInput.place(relx= .5, rely= .3, anchor = CENTER)
        parameterInputLabel.place(relx= .3, rely= .47)
        parameterInput.place(relx= .5, rely= .5, anchor= CENTER)
        valueInputLabel.place(relx= .3, rely= .67)
        valueInput.place(relx= .5, rely= .7, anchor= CENTER)

        # Button to start trial
        startTrialButton = tk.Button(self, text= "Calibrate and Start Trial",
                                     command= lambda: self.controller.show_frame("ActiveTrial"))
        startTrialButton.place(relx= .7, rely= .8,)
#---------------------------------------------------------------------------------------------------------------

class ActiveTrial(tk.Frame):                                    # Active Trial Frame
    def __init__(self, parent, controller):                     # Constructor for frame
        super().__init__(parent)
        self.controller = controller                            # Controller object to switch frames

        self.create_widgets()

    def create_widgets(self):                                   # Frame UI elements
        # Active Trial title label
        calibrationMenuLabel = tk.Label(self, text="Active Trial", font=("Arial", 40))
        calibrationMenuLabel.place(relx= .5, rely= .1, anchor= CENTER)

        # Update torque button
        updateTorqueButton = tk.Button(self, text= "Update Torque",
                                       command= lambda: self.controller.show_frame("UpdateTorque"))
        updateTorqueButton.place(relx= .75, rely= .35)

        #TODO plotter

        # End Trial Button
        endTrialButton = tk.Button(self, text= "End Trial",
                                   command= lambda: self.controller.show_frame("ScanWindow"))
        endTrialButton.place(relx= .75, rely= .8)
#---------------------------------------------------------------------------------------------------------------

class UpdateTorque(tk.Frame):                                   # Frame to start exo and calibrate
    def __init__(self, parent, controller):                     # Constructor for Frame
        super().__init__(parent)
        # Initialize variables
        self.controller = controller                            # Controller object to switch frames
        
        self.create_widgets()

    def create_widgets(self):                                   # Frame UI elements
        # Back button to go back to Scan Window
        backButton = tk.Button(self, text="Back",
                               command= lambda: self.controller.show_frame("ActiveTrial"))
        backButton.place(relx= .05, rely= .05)

        # Calibrate Menu label
        calibrationMenuLabel = tk.Label(self, text="Update Torque Settings", font=("Arial", 40))
        calibrationMenuLabel.place(relx= .5, rely= .1, anchor= CENTER)

        # Controller label
        controllerInputLabel = tk.Label(self, text= "Controller", font= ("Arial", 20))
        controllerInput = tk.Text(self, height= 2, width= 10)
        # Parameter Label
        parameterInputLabel = tk.Label(self, text= "Parameter", font= ("Arial", 20))
        parameterInput = tk.Text(self, height= 2, width= 10)
        # Value label
        valueInputLabel = tk.Label(self, text= "Value", font= ("Arial", 20))
        valueInput= tk.Text(self, height= 2, width= 10)

        controllerInputLabel.place(relx= .3, rely= .27)
        controllerInput.place(relx= .5, rely= .3, anchor = CENTER)
        parameterInputLabel.place(relx= .3, rely= .47)
        parameterInput.place(relx= .5, rely= .5, anchor= CENTER)
        valueInputLabel.place(relx= .3, rely= .67)
        valueInput.place(relx= .5, rely= .7, anchor= CENTER)

        # Button to start trial
        startTrialButton = tk.Button(self, text= "Send Data",)
        startTrialButton.place(relx= .75, rely= .8,)
#---------------------------------------------------------------------------------------------------------------

def run_app():
    root = ControllerApp()
    root.title("NAU Biomechatronics Lab")
    root.geometry("724x420")

    loop = asyncio.get_event_loop()
    asyncio_thread = threading.Thread(target=loop.run_forever)
    asyncio_thread.start()

    root.mainloop()
    loop.call_soon_threadsafe(loop.stop)
    asyncio_thread.join()

#---------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    run_app()
# import asynci
