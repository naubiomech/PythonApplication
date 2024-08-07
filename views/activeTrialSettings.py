import tkinter as tk
from tkinter import CENTER, StringVar, ttk

from async_tkinter_loop import async_handler

jointMap = {
    "Right hip": 1,
    "Left hip": 2,
    "Right knee": 3,
    "Left knee": 4,
    "Right ankle": 5,
    "Left ankle": 6,
}


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
            self,
            text="Back",
            command=lambda: self.controller.show_frame("ActiveTrial")
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
            self,
            textvariable=self.bilateralButtonVar,
            command=self.toggleBilateral
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
        await self.controller.deviceManager.updateTorqueValues(
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
