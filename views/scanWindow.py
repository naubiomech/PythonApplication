import tkinter as tk
from tkinter import (BOTH, BOTTOM, DISABLED, StringVar, X, Y, ttk)
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
        self.scanning_animation_running = False  # Flag for animation state

        self.create_widgets()  # Create UI elements

    # Create all UI elements
    def create_widgets(self):
        # Style configuration
        style = ttk.Style()
        style.configure('TButton', font=('Montserrat', 12), padding=10)
        style.configure('TLabel', font=('Montserrat', 16))
        style.configure('TListbox', font=('Montserrat', 14))

        # Title label
        titleLabel = ttk.Label(self, text="ExoSkeleton Controller", font=("Montserrat", 30))
        titleLabel.grid(row=0, column=0, columnspan=2, pady=20)  # Center title

        # Instruction label for scanning
        startScanLabel = ttk.Label(self, text="Begin Scanning for Exoskeletons")
        startScanLabel.grid(row=1, column=0, columnspan=2, pady=10)  # Center instructions

        # Initial device name display
        deviceNameLabel = ttk.Label(self, textvariable=self.deviceNameText)
        deviceNameLabel.grid(row=2, column=0, columnspan=2, pady=10)  # Center device name

        # Buttons container
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)  # Center button frame

        # Button to start scanning for devices
        self.startScanButton = ttk.Button(button_frame, text="Start Scan",
                                           command=async_handler(self.on_start_scan_button_clicked))
        self.startScanButton.grid(row=0, column=0, padx=5)

        # Button to load saved device info
        self.loadDeviceButton = ttk.Button(button_frame, text="Load Saved Device",
                                            command=async_handler(self.on_load_device_button_clicked))
        self.loadDeviceButton.grid(row=0, column=1, padx=5)

        # Listbox to display scanned devices
        self.deviceListbox = tk.Listbox(self, font=("Montserrat", 14), width=50, height=5)
        self.deviceListbox.grid(row=4, column=0, columnspan=2, pady=5)  # Center Listbox
        self.deviceListbox.bind("<<ListboxSelect>>", self.on_device_selected)  # Bind selection event

        # Action buttons
        action_button_frame = ttk.Frame(self)
        action_button_frame.grid(row=6, column=0, columnspan=2, pady=10)  # Center action button frame

        # Button to start the trial (initially disabled)
        self.startTrialButton = ttk.Button(action_button_frame, text="Start Trial",
                                            command=async_handler(self.on_start_trial_button_clicked),
                                            state=DISABLED)
        self.startTrialButton.grid(row=0, column=0, padx=5)

        # Calibrate Torque button
        self.calTorqueButton = ttk.Button(action_button_frame, text="Calibrate Torque",
                                           command=async_handler(self.on_calibrate_torque_button_clicked),
                                           state=DISABLED)
        self.calTorqueButton.grid(row=0, column=1, padx=5)

        # Connect button
        self.connectButton = ttk.Button(action_button_frame, text="Connect",
                                        command=async_handler(self.on_connect_button_clicked),
                                        state=DISABLED)  # Initially disabled
        self.connectButton.grid(row=0, column=2, padx=5)

        # Button to save the selected device
        self.saveDeviceButton = ttk.Button(action_button_frame, text="Save & Connect",
                                            command=async_handler(self.on_save_device_button_clicked),
                                            state=DISABLED)  # Initially disabled
        self.saveDeviceButton.grid(row=0, column=3, padx=5)

        # Configure grid weights for centering
        for i in range(7):  # Assuming there are 7 rows
            self.grid_rowconfigure(i, weight=1)
        for j in range(2):  # Assuming 2 columns
            self.grid_columnconfigure(j, weight=1)

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
        await self.controller.deviceManager.disconnect()  # Disconnects from any devices

        if self.selected_device_address:
            with open("saved_device.txt", "w") as file:
                file.write(self.selected_device_address)
            print(f"Saved device: {self.selected_device_name} - {self.selected_device_address}")
            
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

    # Load saved device address from a file and connect to it
    async def on_load_device_button_clicked(self):
        """Loads the saved device from a file and connects to it."""
        await self.controller.deviceManager.disconnect()  # Disconnects from any devices

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

    async def on_start_scan_button_clicked(self):
        """Starts scanning for devices when the button is clicked."""
        await self.controller.deviceManager.disconnect()  # Disconnects from any devices
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

    def show(self):
        """Resets elements and shows the frame."""
        self.reset_elements()  # Reset elements when showing the frame
