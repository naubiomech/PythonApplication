import tkinter as tk
from tkinter import (BOTH, BOTTOM, DISABLED, StringVar, X, Y)
from async_tkinter_loop import async_handler
import os

# Frame to scan for exoskeleton devices
class ScanWindow(tk.Frame):
    # Initialize class
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller  # Reference to the main application controller

        # Set the disconnection callback
        self.controller.deviceManager.on_disconnect = self.ScanWindow_on_device_disconnected

        # Variables to hold device information
        self.deviceNameText = StringVar(value="Not Connected")  # Default device name text
        self.selected_device_name = None  # Selected device name
        self.selected_device_address = None  # Selected device address

        # UI elements
        self.startTrialButton = None  # Button for starting the trial
        self.connectButton = None  # Connect button
        self.calTorqueButton = None  # Calibrate Torque button
        self.startScanButton = None  # Button for starting the scan
        self.scanning_animation_running = False  # Flag for animation state

        self.create_widgets()  # Create UI elements

    # Create all UI elements
    def create_widgets(self):
        # Title label
        titleLabel = tk.Label(self, text="ExoSkeleton Controller", font=("Arial", 50))
        titleLabel.pack(expand=False, fill=X, ipady=50)

        # Instruction label for scanning
        startScanLabel = tk.Label(self, text="Begin Scanning for Exoskeletons", font=("Arial", 30))
        startScanLabel.pack(expand=False, fill=X, ipady=10)

        # Initial device name display
        deviceNameLabel = tk.Label(self, textvariable=self.deviceNameText, font=("Arial", 20))
        deviceNameLabel.pack(expand=False, pady=10)

        # Button to start scanning for devices
        self.startScanButton = tk.Button(self, height=2, width=10, text="Start Scan",
                                          command=async_handler(self.on_start_scan_button_clicked))
        self.startScanButton.pack(expand=False, fill=Y, ipadx=10, pady=10)

        # Button to load saved device info
        self.loadDeviceButton = tk.Button(self, height=2, width=20, text="Start Scan with Saved Device",
                                           command=async_handler(self.on_load_device_button_clicked))
        self.loadDeviceButton.pack(expand=False, fill=Y, ipadx=10, pady=10)

        # Listbox to display scanned devices
        self.deviceListbox = tk.Listbox(self, font=("Arial", 16), width=50, height=5)
        self.deviceListbox.pack(expand=False, pady=0)
        self.deviceListbox.bind("<<ListboxSelect>>", self.on_device_selected)  # Bind selection event

        # Label for no devices found
        self.noDevicesLabel = tk.Label(self, text="No Devices Found", font=("Arial", 20), fg="red")
        self.noDevicesLabel.pack(expand=True, fill=BOTH, pady=0)

        # Button to start the trial (initially disabled)
        self.startTrialButton = tk.Button(self, text="Start Trial", height=3,
                                           command=async_handler(self.on_start_trial_button_clicked),
                                           state=DISABLED)
        self.startTrialButton.pack(expand=False, fill=BOTH, side=BOTTOM, pady=20, padx=20)

        # Calibrate Torque button
        self.calTorqueButton = tk.Button(self, text="Calibrate Torque",
                                          command=async_handler(self.on_calibrate_torque_button_clicked),
                                          state=DISABLED)
        self.calTorqueButton.pack(expand=False, fill=None, side=BOTTOM, pady=0, padx=0)

        connect_button_frame = tk.Frame(self)
        connect_button_frame.pack(expand=False, pady=5,side=tk.TOP)
        # Connect button
        self.connectButton = tk.Button(connect_button_frame, text="Connect",
                                        command=async_handler(self.on_connect_button_clicked),
                                        state=DISABLED)  # Initially disabled
        self.connectButton.pack(padx=5,side=tk.LEFT)


        # Button to save the selected device
        self.saveDeviceButton = tk.Button(connect_button_frame, text="Save & Connect",
                                           command=async_handler(self.on_save_device_button_clicked),
                                           state=DISABLED)  # Initially disabled
        self.saveDeviceButton.pack(padx=5,side=tk.LEFT)

        # Initially hide the no devices label
        self.noDevicesLabel.pack_forget()

    # Callback for device disconnection
    def ScanWindow_on_device_disconnected(self):
        """Handles disconnection of the device."""
        self.deviceNameText.set("Disconnected After Scan Try Again")  # Update device name text
        self.startTrialButton.config(state=DISABLED)  # Disable Start Trial button
        self.calTorqueButton.config(state=DISABLED)  # Disable Calibrate Torque button
        self.stop_scanning_animation()  # Stop animation on disconnect

    # Save the selected device address to a file
    async def on_save_device_button_clicked(self):
        """Saves the currently selected device to a file."""
        if self.selected_device_address:
            with open("saved_device.txt", "w") as file:
                file.write(self.selected_device_address)
            print(f"Saved device: {self.selected_device_name} - {self.selected_device_address}")

    # Load saved device address from a file and connect to it
    async def on_load_device_button_clicked(self):
        """Loads the saved device from a file and connects to it."""
        if os.path.exists("saved_device.txt"):
            with open("saved_device.txt", "r") as file:
                saved_address = file.read().strip()
                if saved_address:  # Check if the file is not empty
                    self.deviceNameText.set(f"Loading saved device: {saved_address}")
                    self.controller.deviceManager.set_deviceAddress(saved_address)
                    success = await self.controller.deviceManager.scanAndConnect()
                    
                    if success:
                        self.deviceNameText.set(f"Connected: {self.selected_device_name} {saved_address}")
                        self.startTrialButton.config(state="normal")
                        self.calTorqueButton.config(state="normal")
                    else:
                        self.deviceNameText.set("Connection Failed, Please Restart Device")
                else:
                    self.deviceNameText.set("Saved device address is empty.")
        else:
            self.deviceNameText.set("No saved device found.")
    # Async function to handle the start scan button click
    async def on_start_scan_button_clicked(self):
        """Starts scanning for devices when the button is clicked."""
        self.deviceNameText.set("Scanning...")  # Update device name text
        self.start_scanning_animation()  # Start the animation        
        await self.startScanButtonClicked()  # Initiate the scanning process
        self.startScanButton.config(state="normal")  # Re-enable the Start Scan button after scanning
        self.stop_scanning_animation()  # Stop the animation after scanning

    async def on_calibrate_torque_button_clicked(self):
        """Handles the Calibrate Torque button click."""
        await self.controller.trial.calibrate(self.controller.deviceManager)

    async def on_connect_button_clicked(self):
        """Handles the Connect button click."""
        connect_message = f"Connecting to: {self.selected_device_name} {self.selected_device_address}"
        self.deviceNameText.set(connect_message)
        self.controller.deviceManager.set_deviceAddress(self.selected_device_address)  # Set the device address

        # Attempt to connect to the device
        success = await self.controller.deviceManager.scanAndConnect()
        
        if success:
            self.startTrialButton.config(state="normal")  # Enable Start Trial button
            self.calTorqueButton.config(state="normal")   # Enable Calibrate Torque button
            self.deviceNameText.set(f"Connected: {self.selected_device_name} {self.selected_device_address}")
        else:
            self.deviceNameText.set("Connection Failed, Please Restart Device")  # Update text if connection fails

    async def on_start_trial_button_clicked(self):
        """Handles the Start Trial button click."""
        await self.startTrialButtonClicked()  # Initiate the trial process

    async def startScanButtonClicked(self):
        """Starts scanning for devices and updates the UI accordingly."""
        self.reset_elements()

        available_devices = await self.controller.deviceManager.searchDevices()
        self.deviceNameText.set("Scan Complete")

        # Update Listbox with the scanned devices
        self.deviceListbox.delete(0, tk.END)  # Clear the Listbox
        for address, name in available_devices.items():
            self.deviceListbox.insert(tk.END, f"{name} - {address}")

        # Check if there are available devices
        if not available_devices:
            self.deviceNameText.set("No Devices Found")
            self.noDevicesLabel.pack(expand=False, pady=10)  # Show no devices label
        else:
            self.noDevicesLabel.pack_forget()  # Hide no devices label if devices are found

    # Handle device selection from the Listbox
    def on_device_selected(self, event):
        """Handles the selection of a device from the Listbox."""
        selected_index = self.deviceListbox.curselection()
        if selected_index:  # Check if any item is selected
            selected_device_info = self.deviceListbox.get(selected_index)
            self.selected_device_name, self.selected_device_address = selected_device_info.split(" - ")
            self.connectButton.config(state="normal")  # Enable Connect button
            self.saveDeviceButton.config(state="normal")  # Enable Save & Connect button
            print(self.selected_device_name)  # Debug output
        else:
            self.connectButton.config(state=DISABLED)  # Disable Connect button if no selection
            self.saveDeviceButton.config(state=DISABLED)  # Disable Save & Connect button if no selection


    def start_scanning_animation(self):
        """Starts the scanning animation."""
        self.scanning_animation_running = True
        self.animate_scanning_dots(0)

    def stop_scanning_animation(self):
        """Stops the scanning animation."""
        self.scanning_animation_running = False

    def animate_scanning_dots(self, count):
        """Animates the scanning dots to indicate scanning progress."""
        if not self.scanning_animation_running:
            return

        dots = "." * ((count % 3) + 1)  # Cycle through 1 to 3 dots
        self.deviceNameText.set(f"Scanning{dots}")

        # Schedule the next update
        self.after(500, self.animate_scanning_dots, count + 1)

    async def startTrialButtonClicked(self):
        """Switches frame to ActiveTrial and begins the trial."""
        active_trial_frame = self.controller.frames["ActiveTrial"]
        active_trial_frame.disable_interactions()  # Disable buttons in ActiveTrial frame

        # Show ActiveTrial frame
        self.controller.show_frame("ActiveTrial")
        await self.controller.trial.calibrate(self.controller.deviceManager)  # Calibrate devices
        await self.controller.trial.beginTrial(self.controller.deviceManager)  # Begin the trial

        # Starts new selection once Active trial has started
        active_trial_frame.newSelection(self)

    def reset_elements(self):
        """Resets the UI elements to their initial state."""
        self.deviceNameText.set("Not Connected")
        self.deviceListbox.delete(0, tk.END)
        self.selected_device_name = None
        self.selected_device_address = None
        self.startTrialButton.config(state=DISABLED)
        self.calTorqueButton.config(state=DISABLED)
        self.connectButton.config(state=DISABLED)
        self.noDevicesLabel.pack_forget()

    def show(self):
        """Resets elements and shows the frame."""
        self.reset_elements()  # Reset elements when showing the frame
