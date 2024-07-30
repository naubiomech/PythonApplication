import tkinter as tk
from tkinter import *
from tkinter import ttk

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from async_tkinter_loop import async_handler, async_mainloop
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Device import exoDeviceManager, exoTrial

matplotlib.use("TkAgg")

deviceManager = exoDeviceManager.ExoDeviceManager()
trial = exoTrial.ExoTrial(True, 1, True)

jointMap = {
    "Right hip": 1,
    "Left hip": 2,
    "Right knee": 3,
    "Left knee": 4,
    "Right ankle": 5,
    "Left ankle": 6,
}


async def startScan():
    await deviceManager.scanAndConnect()


class ControllerApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("NAU Lab of Biomechatronics")
        self.geometry("720x420")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # Names of each frame goes here
        for F in (ScanWindow, Calibrate, ActiveTrial, UpdateTorque):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("ScanWindow")  # Switch to Scan Window Frame

    def show_frame(self, page_name):  # Method to switch frames
        frame = self.frames[page_name]
        frame.tkraise()


class ScanWindow(tk.Frame):  # Main window for the app
    def __init__(self, parent, controller):  # Frame Constructor
        super().__init__(parent)
        # Initialize variables
        self.controller = controller  # Controller object to switch frames
        # String variable for device name text
        self.deviceNameText = StringVar()
        self.startTrialButton = None

        # creates page for class
        self.create_widgets()

    def create_widgets(self):  # Frame UI elements
        # Title label
        titleLabel = tk.Label(
            self, text="ExoSkeleton Controller", font=("Arial", 40))
        titleLabel.place(relx=0.5, rely=0.1, anchor=CENTER)
        # Start Scan label
        startScanLabel = tk.Label(self, text="Begin Scanning for Exoskeletons")
        startScanLabel.place(relx=0.5, rely=0.35, anchor=CENTER)

        # Start Scan button
        startScanButton = tk.Button(
            self,
            text="Start Scan",
            command=async_handler(self.on_start_scan_button_clicked),
        )
        startScanButton.place(relx=0.5, rely=0.45, anchor=CENTER)

        # Device name label
        self.deviceNameText.set("Not Connected")
        deviceNameLabel = tk.Label(self, textvariable=self.deviceNameText)
        deviceNameLabel.place(relx=0.5, rely=0.60, anchor=CENTER)

        # Start trial button (disabled until device is scanned and connected)
        self.startTrialButton = tk.Button(
            self,
            text="Start Trial",
            command=lambda: self.controller.show_frame("Calibrate"),
            state=DISABLED,
        )
        self.startTrialButton.place(
            relx=0.75,
            rely=0.8,
        )

    async def on_start_scan_button_clicked(self):  # Initiate scan
        self.deviceNameText.set("Scanning...")
        await self.startScanButtonClicked()

    async def startScanButtonClicked(self):  # Start scanning and update screen
        print("test")
        await startScan()
        self.deviceNameText.set(deviceManager.device)
        self.startTrialButton.config(state="normal")


class Calibrate(tk.Frame):  # Frame to start exo and calibrate
    def __init__(self, parent, controller):  # Constructor for Frame
        super().__init__(parent)
        # Initialize variables
        self.controller = controller  # Controller object to switch frames
        self.bilateralButtonVar = StringVar()
        self.bilateralButtonVar.set("Bilateral Mode On")
        self.jointVar = StringVar()

        # Joint select
        self.jointSelector = ttk.Combobox(
            self,
            textvariable=self.jointVar,
            state="readonly",
            values=[
                "Left hip",
                "Left knee",
                "Left ankle",
                "Right hip",
                "Right knee",
                "Right ankle",
            ],
        )

        self.isBilateral = True

        self.create_widgets()

    def create_widgets(self):  # Frame UI elements
        # Back button to go back to Scan Window
        backButton = tk.Button(
            self, text="Back", command=lambda: self.controller.show_frame("ScanWindow")
        )
        backButton.place(relx=0.05, rely=0.05)

        # Calibrate Menu label
        calibrationMenuLabel = tk.Label(
            self, text="Calibration Menu", font=("Arial", 40)
        )
        calibrationMenuLabel.place(relx=0.5, rely=0.1, anchor=CENTER)

        # Controller label
        controllerInputLabel = tk.Label(
            self, text="Controller", font=("Arial", 20))
        controllerInput = tk.Text(self, height=2, width=10)
        # Parameter Label
        parameterInputLabel = tk.Label(
            self, text="Parameter", font=("Arial", 20))
        parameterInput = tk.Text(self, height=2, width=10)
        # Value label
        valueInputLabel = tk.Label(self, text="Value", font=("Arial", 20))
        valueInput = tk.Text(self, height=2, width=10)

        self.jointSelector.bind("<<ComboboxSelected>>", self.newSelection)

        bilateralButton = tk.Button(
            self, textvariable=self.bilateralButtonVar, command=self.toggleBilateral
        )

        # Placing elements onto the frame
        controllerInputLabel.place(relx=0.15, rely=0.27)
        controllerInput.place(relx=0.35, rely=0.3, anchor=CENTER)
        parameterInputLabel.place(relx=0.15, rely=0.47)
        parameterInput.place(relx=0.35, rely=0.5, anchor=CENTER)
        valueInputLabel.place(relx=0.15, rely=0.67)
        valueInput.place(relx=0.35, rely=0.7, anchor=CENTER)
        self.jointSelector.place(relx=0.75, rely=0.30, anchor=CENTER)
        bilateralButton.place(relx=0.75, rely=0.50, anchor=CENTER)

        # Button to start trial
        startTrialButton = tk.Button(
            self,
            text="Calibrate and Start Trial",
            command=async_handler(
                self.on_start_trial_button_clicked,
                controllerInput,
                parameterInput,
                valueInput,
            ),
        )
        startTrialButton.place(relx=0.7, rely=0.8)

    async def on_start_trial_button_clicked(
        self, controllerInput, parameterInput, valueInput
    ):
        print(self.jointVar.get())
        await self.StartTrialButtonClicked(
            self.isBilateral,
            jointMap[self.jointVar.get()],
            controllerInput,
            parameterInput,
            valueInput,
        )

    async def StartTrialButtonClicked(
        self, isBilateral, joint, controllerInput, parameterInput, valueInput
    ):

        controllerVal = float(controllerInput.get(1.0, "end-1c"))
        parameterVal = float(parameterInput.get(1.0, "end-1c"))
        valueVal = float(valueInput.get(1.0, "end-1c"))

        await trial.calibrate(deviceManager)  # Calibrate ExoSkeleton
        # Start Exoskeleton systems and begin trial
        await trial.beginTrial(deviceManager)
        # Set Torque
        await deviceManager.updateTorqueValues(
            [isBilateral, joint, controllerVal, parameterVal, valueVal]
        )

        self.controller.show_frame("ActiveTrial")

    def newSelection(self, event):
        self.jointVar.set(self.jointSelector.get())

    def toggleBilateral(self):
        if self.isBilateral is True:
            self.isBilateral = False
            self.bilateralButtonVar.set("Bilateral Mode Off")
        else:
            self.isBilateral = True
            self.bilateralButtonVar.set("Bilateral Mode On")


class ActiveTrial(tk.Frame):  # Active Trial Frame
    def __init__(self, parent, controller):  # Constructor for frame
        super().__init__(parent)
        self.controller = controller  # Controller object to switch frames

        self.create_widgets()

    def create_widgets(self):  # Frame UI elements
        # Active Trial title label
        calibrationMenuLabel = tk.Label(
            self, text="Active Trial", font=("Arial", 40))
        calibrationMenuLabel.place(relx=0.5, rely=0.1, anchor=CENTER)

        # Update torque button
        updateTorqueButton = tk.Button(
            self,
            text="Update Torque",
            command=lambda: self.controller.show_frame("UpdateTorque"),
        )
        updateTorqueButton.place(relx=0.75, rely=0.35)

        # TODO plotter ########################################################
        fig = plt.figure(figsize=(3, 3))
        plt.ion()
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(np.pi * t)
        plt.plot(t, s)

        canvas = FigureCanvasTkAgg(fig, master=self)
        plot_widget = canvas.get_tk_widget()

        def update():
            s = np.cos(np.pi * t)
            plt.plot(t, s)
            # d[0].set_ydata(s)
            fig.canvas.draw()

        plot_widget.place(relx=0.05, rely=0.15)
        tk.Button(self, text="Update", command=update).place(
            relx=0.9, rely=0.9)

        #######################################################################

        # End Trial Button
        endTrialButton = tk.Button(
            self,
            text="End Trial",
            command=async_handler(self.on_end_trial_button_clicked),
        )
        endTrialButton.place(relx=0.75, rely=0.8)

    async def on_end_trial_button_clicked(self):
        await self.endTrialButtonClicked()

    async def endTrialButtonClicked(self):
        await self.ShutdownExo()

        self.controller.show_frame("ScanWindow")

    async def ShutdownExo(self):
        # End trial
        await deviceManager.motorOff()  # Turn off motors
        await deviceManager.stopTrial()  # Tell Exo to end trial
        # Disconnect from Exo
        trial.loadDataToCSV(deviceManager)  # Load data from Exo into CSV


class UpdateTorque(tk.Frame):  # Frame to start exo and calibrate
    def __init__(self, parent, controller):  # Constructor for Frame
        super().__init__(parent)  # Correctly initialize the tk.Frame part
        # Initialize variables
        self.controller = controller  # Controller object to switch frames
        self.bilateralButtonVar = StringVar()
        self.bilateralButtonVar.set("Bilateral Mode On")
        self.jointVar = StringVar()

        # Joint select
        self.jointSelector = ttk.Combobox(
            self,
            textvariable=self.jointVar,
            state="readonly",
            values=[
                "Left hip",
                "Left knee",
                "Left ankle",
                "Right hip",
                "Right knee",
                "Right ankle",
            ],
        )

        self.isBilateral = True

        self.create_widgets()

    def create_widgets(self):  # Frame UI elements
        # Back button to go back to Scan Window
        backButton = tk.Button(
            self, text="Back", command=lambda: self.controller.show_frame("ScanWindow")
        )
        backButton.place(relx=0.05, rely=0.05)

        # Calibrate Menu label
        calibrationMenuLabel = tk.Label(
            self, text="Update Torque Settings", font=("Arial", 40)
        )
        calibrationMenuLabel.place(relx=0.5, rely=0.1, anchor=CENTER)

        # Controller label
        controllerInputLabel = tk.Label(
            self, text="Controller", font=("Arial", 20))
        controllerInput = tk.Text(self, height=2, width=10)
        # Parameter Label
        parameterInputLabel = tk.Label(
            self, text="Parameter", font=("Arial", 20))
        parameterInput = tk.Text(self, height=2, width=10)
        # Value label
        valueInputLabel = tk.Label(self, text="Value", font=("Arial", 20))
        valueInput = tk.Text(self, height=2, width=10)

        self.jointSelector.bind("<<ComboboxSelected>>", self.newSelection)

        bilateralButton = tk.Button(
            self, textvariable=self.bilateralButtonVar, command=self.toggleBilateral
        )

        controllerInputLabel.place(relx=0.15, rely=0.27)
        controllerInput.place(relx=0.35, rely=0.3, anchor=CENTER)
        parameterInputLabel.place(relx=0.15, rely=0.47)
        parameterInput.place(relx=0.35, rely=0.5, anchor=CENTER)
        valueInputLabel.place(relx=0.15, rely=0.67)
        valueInput.place(relx=0.35, rely=0.7, anchor=CENTER)
        self.jointSelector.place(relx=0.75, rely=0.30, anchor=CENTER)
        bilateralButton.place(relx=0.75, rely=0.50, anchor=CENTER)

        # Button to start trial
        updateTorqueButton = tk.Button(
            self,
            text="Update Torque",
            command=async_handler(
                self.on_update_button_clicked,
                controllerInput,
                parameterInput,
                valueInput,
            ),
        )
        updateTorqueButton.place(relx=0.7, rely=0.8)

    async def on_update_button_clicked(
        self, controllerInput, parameterInput, valueInput
    ):
        print(self.jointVar.get())
        await self.UpdateButtonClicked(
            self.isBilateral,
            jointMap[self.jointVar.get()],
            controllerInput,
            parameterInput,
            valueInput,
        )

    async def UpdateButtonClicked(
        self, isBilateral, joint, controllerInput, parameterInput, valueInput
    ):

        controllerVal = float(controllerInput.get(1.0, "end-1c"))
        parameterVal = float(parameterInput.get(1.0, "end-1c"))
        valueVal = float(valueInput.get(1.0, "end-1c"))

        # Set Torque
        await deviceManager.updateTorqueValues(
            [isBilateral, joint, controllerVal, parameterVal, valueVal]
        )

        self.controller.show_frame("ActiveTrial")

    def newSelection(self, event):
        self.jointVar.set(self.jointSelector.get())

    def toggleBilateral(self):
        if self.isBilateral is True:
            self.isBilateral = False
            self.bilateralButtonVar.set("Bilateral Mode Off")
        else:
            self.isBilateral = True
            self.bilateralButtonVar.set("Bilateral Mode On")


def exec():
    controller = ControllerApp()
    async_mainloop(controller)


if __name__ == "__main__":
    exec()
