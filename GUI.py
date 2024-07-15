import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os
import asyncio
from async_tkinter_loop import async_handler, async_mainloop
from tkinter import *
import tkinter as tk
from tkinter import ttk
from Device import exoDeviceManager
from Device import exoTrial

deviceManager = exoDeviceManager.ExoDeviceManager()
trial = exoTrial.ExoTrial(True, 1, True) 

async def startScan():
    await deviceManager.scanAndConnect()
#---------------------------------------------------------------------------------------------------------------

class ControllerApp(tk.Tk):                                     # Controller to switch frames 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("NAU Lab of Biomechatronics")
        self.geometry("720x420")

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
        startScanButton = tk.Button(self, text="Start Scan", 
                                    command=async_handler(self.on_start_scan_button_clicked))
        startScanButton.place(relx=.5, rely=.45, anchor=CENTER)

        # Device name label
        self.deviceNameText.set("Not Connected")
        deviceNameLabel = tk.Label(self, textvariable=self.deviceNameText)
        deviceNameLabel.place(relx=.5, rely=.60, anchor=CENTER)

        # Start trial button (disabled untill device is scanned and connected)
        self.startTrialButton = tk.Button(self, text="Start Trial", 
                                          command=lambda: self.controller.show_frame("Calibrate"),
                                          state=DISABLED)
        self.startTrialButton.place(relx=.75, rely=.8,)

    async def on_start_scan_button_clicked(self):                     # Initiate scan
        self.deviceNameText.set("Scanning...")
        await self.startScanButtonClicked()

    async def startScanButtonClicked(self):                     # Start scanning and update screen
        print("test")
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
                                     command= async_handler(self.on_start_trial_button_clicked,
                                     controllerInput, parameterInput, valueInput))
        startTrialButton.place(relx= .7, rely= .8)
   
    async def on_start_trial_button_clicked(self, controllerInput, parameterInput, valueInput):
        print("test\n")
        await self.StartTrialButtonClicked(controllerInput, parameterInput, valueInput)

    async def StartTrialButtonClicked(self, controllerInput, parameterInput, valueInput):
        controllerVal = controllerInput.get(1.0, "end-1c")      # get input minus enline char from input form
        parameterVal = parameterInput.get(1.0, "end-1c")
        valueVal = valueInput.get(1.0, "end-1c")

        await trial.calibrate()                                 # Calibrate ExoSkeleton
        await trial.beginTrial()                                # Start Exoskeleton systems and begin trial 
        await deviceManager.updateTorqueValues([65.0, controllerVal, parameterVal, valueVal]) # Set Torque

        self.controller.show_frame("ActiveTrial")
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

        #TODO plotter #############################################################
        fig = plt.figure(figsize= (3,3))
        plt.ion()
        t = np.arange(0.0,3.0,0.01)
        s = np.sin(np.pi*t)
        plt.plot(t,s)
        
        canvas = FigureCanvasTkAgg(fig, master=self)
        plot_widget = canvas.get_tk_widget()
        
        def update():
            s = np.cos(np.pi*t)
            plt.plot(t,s)
            #d[0].set_ydata(s)
            fig.canvas.draw()
        
        plot_widget.place(relx=.05, rely=.15)
        tk.Button(self,text="Update",command=update).place(relx=.9, rely=.9)

        ##########################################################################

        # End Trial Button
        endTrialButton = tk.Button(self, text= "End Trial",
                                   command= async_handler(self.on_end_trial_button_clicked))
        endTrialButton.place(relx= .75, rely= .8)

    async def on_end_trial_button_clicked(self):
        await self.endTrialButtonClicked()

    async def endTrialButtonClicked(self):
        await self.ShutdownExo() 

        self.controller.show_frame("ScanWindow")

    async def ShutdownExo(self):
        # End trial
        await deviceManager.motorOff()          # Turn off motors
        await deviceManager.stopTrial()         # Tell Exo to end trial
        deviceManager.handleDisconnect(deviceManager.client)    # Disconnect from Exo
        self.loadDataToCSV(deviceManager)       # Load data from Exo into CSV 

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
        startTrialButton = tk.Button(self, text= "Send Data", 
                                     command= async_handler(self.on_update_torque_button_clicked,
                                     controllerInput, parameterInput, valueInput))
        startTrialButton.place(relx= .75, rely= .8,)

    async def on_update_torque_button_clicked(self, controllerInput, parameterInput, valueInput):
         await self.UpdateTorqueButtonClicked(controllerInput, parameterInput, valueInput)

    async def UpdateTorqueButtonClicked(self, controllerInput, parameterInput, valueInput):
        controllerVal = controllerInput.get(1.0, "end-1c")      # get input minus enline char from input form
        parameterVal = parameterInput.get(1.0, "end-1c")
        valueVal = valueInput.get(1.0, "end-1c")

        await deviceManager.updateTorqueValues([65.0, controllerVal, parameterVal, valueVal]) # Update Torque

        self.controller.show_frame("ActiveTrial")

#---------------------------------------------------------------------------------------------------------------

def exec():
    controller = ControllerApp()
    async_mainloop(controller)
#---------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    exec()
