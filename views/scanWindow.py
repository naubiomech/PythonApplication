import tkinter as tk
from tkinter import (BOTH, BOTTOM, CENTER, DISABLED, LEFT, RIGHT, TOP,
                     StringVar, X, Y)
from async_tkinter_loop import async_handler

# Frame to scan for exoskeleton devices
class ScanWindow(tk.Frame):
    # Initialize class
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller  # Reference to the main application controller
        self.deviceNameText = StringVar()  # Variable to hold device name text
        self.startTrialButton = None  # Button for starting the trial
        self.calTorqueButton = None
        self.startScanButton = None  # Store reference to Start Scan button

        self.create_widgets()  # Create UI elements

    # Holds all UI elements
    def create_widgets(self):
        # Title label
        titleLabel = tk.Label(self, text="ExoSkeleton Controller", font=("Arial", 50))
        titleLabel.pack(expand=False, fill=X, ipady=50)

        # Instruction label for scanning
        startScanLabel = tk.Label(
            self, text="Begin Scanning for Exoskeletons", font=("Arial", 30)
        )
        startScanLabel.pack(expand=False, fill=X, ipady=10)

        # Initial device name display
        self.deviceNameText.set("Not Connected")
        deviceNameLabel = tk.Label(
            self, textvariable=self.deviceNameText, font=("Arial", 20)
        )
        deviceNameLabel.pack(expand=False, pady=10)

        # Button to start scanning for devices
        self.startScanButton = tk.Button(
            self,
            height=2,
            width=10,
            text="Start Scan",
            command=async_handler(self.on_start_scan_button_clicked),
        )
        self.startScanButton.pack(expand=False, fill=Y, ipadx=40, pady=100)

        # Button to start the trial (initially disabled)
        self.startTrialButton = tk.Button(
            self,
            text="Start Trial",
            height=3,
            command=async_handler(self.on_start_trial_button_clicked),
            state=DISABLED,
        )
        self.startTrialButton.pack(
            expand=False, fill=BOTH, side=BOTTOM, pady=20, padx=20
        )

        # Calibrate Torque
        self.calTorqueButton = tk.Button(
            self,
            text="Calibrate Torque",
            command=async_handler(self.on_calibrate_torque_button_clicked),
            state=DISABLED,
        )
        self.calTorqueButton.pack(expand=False, fill=None, side=BOTTOM, pady=0, padx=0)

    # Async function to handle the start scan button click
    async def on_start_scan_button_clicked(self):
        self.deviceNameText.set("Scanning...")  # Update device name text
        self.startScanButton.config(state=DISABLED)  # Disable the Start Scan button
        await self.startScanButtonClicked()  # Initiate the scanning process
        self.startScanButton.config(state="normal")  # Re-enable the Start Scan button after scanning

    async def on_calibrate_torque_button_clicked(self):
        await self.controller.trial.calibrate(self.controller.deviceManager)

    # Start scanning for exoskeleton devices
    async def startScan(self):
        await self.controller.deviceManager.scanAndConnect()  # Call scan function

    # Start scan and update device name, enable trial button if connected
    async def startScanButtonClicked(self):
        await self.startScan()  # Perform scanning
        self.deviceNameText.set(self.controller.deviceManager.device)  # Update device name
        # Enable the Start Trial button if a device is connected
        if self.deviceNameText.get() != "None":
            self.startTrialButton.config(state="normal")
            self.calTorqueButton.config(state="normal")
        else:
            self.deviceNameText.set("Not Connected. Try Again.")  # Provide feedback if not connected

    # Handle the start trial button click
    async def on_start_trial_button_clicked(self):
        await self.startTrialButtonClicked()  # Initiate the trial process

    # Switch frame to ActiveTrial and begin the trial
    async def startTrialButtonClicked(self):
        # Disable buttons in ActiveTrial frame to prevent system overload
        active_trial_frame = self.controller.frames["ActiveTrial"]
        active_trial_frame.disable_interactions()  # Call method to disable ActiveTrial buttons

        # Show ActiveTrial frame
        self.controller.show_frame("ActiveTrial")
        await self.controller.trial.calibrate(self.controller.deviceManager)  # Calibrate devices
        await self.controller.trial.beginTrial(self.controller.deviceManager)  # Begin the trial

        # Starts new selection once Active trial has started
        active_trial_frame.newSelection(self)

