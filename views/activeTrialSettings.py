import tkinter as tk
from tkinter import (BOTTOM, CENTER, LEFT, RIGHT, TOP, E, N, S, StringVar, W,
                     X, Y, ttk)

from async_tkinter_loop import async_handler
from custom_keyboard import CustomKeyboard

jointMap = {
    "Right hip": 1,
    "Left hip": 2,
    "Right knee": 3,
    "Left knee": 4,
    "Right ankle": 5,
    "Left ankle": 6,
    "Right elbow": 7,
    "Left elbow": 8,
}


class UpdateTorque(tk.Frame):  # Frame to start exo and calibrate
    def __init__(self, parent, controller):  # Constructor for Frame
        super().__init__(parent)  # Correctly initialize the tk.Frame part
        # Initialize variables
        self.controller = controller  # Controller object to switch frames
        self.previous_frame = None  # Track the previous frame

        # Set the disconnection callback
        self.controller.deviceManager.on_disconnect = self.UpdateTorque_on_device_disconnected

        self.bilateralButtonVar = StringVar()
        self.bilateralButtonVar.set("Bilateral Mode On")
        self.jointVar = StringVar(value="Select Joint")

        self.isBilateral = True
        self.create_widgets()

    def create_widgets(self):  # Frame UI elements
        # Back button to go back to Scan Window
        backButton = tk.Button(self, text="Back", command=self.handle_back_button)
        backButton.pack(side=TOP, anchor=W, pady=10, padx=10)
        
        # Calibrate Menu label
        calibrationMenuLabel = tk.Label(
            self, text="Update Controller Settings", font=("Arial", 40)
        )
        calibrationMenuLabel.pack(anchor=CENTER, side=TOP, pady=15)

        # Joint select (using tk.OptionMenu)
        joint_options = [
            "Left hip",
            "Left knee",
            "Left ankle",
            "Left elbow",
            "Right hip",
            "Right knee",
            "Right ankle",
            "Right elbow",
        ]
        self.jointVar.set(joint_options[0])  # Default value
        jointSelector = tk.OptionMenu(self, self.jointVar, *joint_options)
        jointSelector.config(font=("Arial", 26), width=20)
        menu = self.nametowidget(jointSelector.menuname)  # Access the menu part of OptionMenu
        menu.config(font=("Arial", 26))  # Larger font for options in the dropdown menu
        jointSelector.pack(pady=5)

        # Controller label
        controllerInputLabel = tk.Label(self, text="Controller", font=("Arial", 20))
        self.controllerInput = tk.Entry(self, font=("Arial", 16))  # Use Entry instead of Text for simpler input
        controllerKeyboardButton = tk.Button(
            self, text="Keyboard", command=lambda: self.open_keyboard(self.controllerInput)
        )        
        
        # Parameter Label
        parameterInputLabel = tk.Label(self, text="Parameter", font=("Arial", 20))
        self.parameterInput = tk.Entry(self, font=("Arial", 16)) 
        parameterKeyboardButton = tk.Button(
                self, text="Keyboard", command=lambda: self.open_keyboard(self.parameterInput)
            )        
        
        # Value label
        valueInputLabel = tk.Label(self, text="Value", font=("Arial", 20))
        self.valueInput = tk.Entry(self, font=("Arial", 16)) 
        valueKeyboardButton = tk.Button(
            self, text="Keyboard", command=lambda: self.open_keyboard(self.valueInput)
        )

        bilateralButton = tk.Button(
            self,
            textvariable=self.bilateralButtonVar,
            height=2,
            width=15,
            command=self.toggleBilateral,
        )
        bilateralButton.pack(pady=5)

        controllerInputLabel.pack(pady=5)
        self.controllerInput.pack(padx=5)
        controllerKeyboardButton.pack( padx=5)
        
        parameterInputLabel.pack(pady=5)
        self.parameterInput.pack(pady=5)
        parameterKeyboardButton.pack(padx=5)

        valueInputLabel.pack(pady=5)
        self.valueInput.pack(pady=5)
        valueKeyboardButton.pack(padx=5)

        # Button to start trial
        updateTorqueButton = tk.Button(
            self,
            text="Update Settings",
            height=2,
            width=10,
            command=async_handler(
                self.on_update_button_clicked,
                self.controllerInput,
                self.parameterInput,
                self.valueInput,
            ),
        )
        updateTorqueButton.pack(side=BOTTOM, fill=X, padx=20, pady=20)

    def open_keyboard(self, target_widget):
        # Create a new Toplevel window for the keyboard
        self.keyboard_window = tk.Toplevel(self)
        self.keyboard_window.title("Custom Keyboard")

        # Create a frame to hold the keyboard and center it
        keyboard_frame = tk.Frame(self.keyboard_window)
        keyboard_frame.pack(expand=True, fill=tk.BOTH, pady=20)

        # Create and pack the custom keyboard inside the Toplevel window
        keyboard = CustomKeyboard(self.keyboard_window, target_widget, on_submit=self.on_keyboard_submit)
        keyboard.pack(fill=tk.BOTH, expand=True)

        # Optionally, add some padding and set a fixed size for the keyboard window
        self.keyboard_window.geometry("200x300")  # Adjust size if needed

    def on_keyboard_submit(self, value):
        # Handle the submitted value when the user presses "Submit" on the virtual keyboard
        print(f"Submitted value: {value}")
        
        # Update the target widget with the submitted value
        if self.controllerInput:
            self.controllerInput.delete(0, tk.END)  # Clear current content in the input field
            self.controllerInput.insert(0, value)  # Insert the new value into the input field
        # Destroy the keyboard window after submitting
        if hasattr(self, 'keyboard_window'):
            self.keyboard_window.destroy()  # Destroy the keyboard window
            
    def handle_back_button(self):
        # Return to the previous frame
        if self.previous_frame:
            self.controller.show_frame(self.previous_frame)
            active_trial_frame = self.controller.frames[self.previous_frame]
            active_trial_frame.newSelection(self)
        else:
            self.controller.show_frame("ActiveTrial")
            active_trial_frame = self.controller.frames["ActiveTrial"]
            active_trial_frame.newSelection(self)
        
    async def on_update_button_clicked(
        self, controllerInput, parameterInput, valueInput,
    ):
        selected_joint = self.jointVar.get()  # Get the selected joint
        joint_id = jointMap[selected_joint]

        await self.UpdateButtonClicked(
            self.isBilateral,
            joint_id,
            controllerInput,
            parameterInput,
            valueInput,
        )

    async def UpdateButtonClicked(
        self, isBilateral, joint, controllerInput, parameterInput, valueInput,
    ):
        controllerVal = float(controllerInput.get())  # Corrected line for Entry widget
        parameterVal = float(parameterInput.get())
        valueVal = float(valueInput.get())

        print(f"bilateral: {isBilateral}")
        print(f"joint: {joint}")
        print(f"controller: {controllerVal}")
        print(f"paramter: {parameterVal}")
        print(f"value: {valueVal}")

        # Set Torque
        await self.controller.deviceManager.updateTorqueValues(
            [isBilateral, joint, controllerVal, parameterVal, valueVal]
        )

        if self.previous_frame:
            self.controller.show_frame(self.previous_frame)
            active_trial_frame = self.controller.frames[self.previous_frame]
            active_trial_frame.newSelection(self)
        else:
            self.controller.show_frame("ActiveTrial")
            active_trial_frame = self.controller.frames["ActiveTrial"]
            active_trial_frame.newSelection(self)

    def newSelection(self, event):
        self.jointVar.set(self.jointSelector.get())

    def UpdateTorque_on_device_disconnected(self):
        tk.messagebox.showwarning("Device Disconnected", "Please Reconnect")
        
        self.controller.trial.loadDataToCSV(
            self.controller.deviceManager, True
        )  # Load data from Exo into CSV
        self.controller.show_frame("ScanWindow")# Navigate back to the scan page
        self.controller.frames["ScanWindow"].show()  # Call show method to reset elements
            

    def toggleBilateral(self):
        if self.isBilateral is True:
            self.isBilateral = False
            self.bilateralButtonVar.set("Bilateral Mode Off")
        else:
            self.isBilateral = True
            self.bilateralButtonVar.set("Bilateral Mode On")