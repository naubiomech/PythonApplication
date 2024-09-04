import tkinter as tk
from tkinter import (BOTTOM, CENTER, LEFT, RIGHT, TOP, E, IntVar, N, StringVar,
                     W, X, Y, ttk)

from async_tkinter_loop import async_handler

from Widgets.Charts.chart import (LeftStatePlot, LeftTorquePlot,
                                  RightStatePlot, RightTorquePlot)


# Active Trial Frame
class ActiveTrial(tk.Frame):
    # Constructor for frame
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.var = IntVar()
        self.chartVar = StringVar()

        self.chartDropdown = ttk.Combobox(
            self,
            textvariable=self.chartVar,
            state="readonly",
            values=[
                "Torque",
                "State",
            ],
        )
        # Active Trial title label
        calibrationMenuLabel = tk.Label(
            self, text="Active Trial", font=("Arial", 40))
        calibrationMenuLabel.pack(side=TOP, anchor=N, pady=20)

        self.chartDropdown.bind("<<ComboboxSelected>>", self.newSelection)
        self.chartDropdown.pack(side=tk.BOTTOM, anchor=tk.S, pady=10)

        self.leftTorquePlot = LeftTorquePlot(self)
        self.rightTorquePlot = RightTorquePlot(self)
        self.leftStatePlot = LeftStatePlot(self)
        self.rightStatePlot = RightStatePlot(self)

        self.leftStatePlot.canvas.get_tk_widget().pack_forget()
        self.rightStatePlot.canvas.get_tk_widget().pack_forget()

        self.currentPlots = [self.leftTorquePlot, self.rightTorquePlot]

        self.create_widgets()

    # Frame UI elements
    def create_widgets(self):
        # Update torque button
        updateTorqueButton = tk.Button(
            self,
            text="Update Torque",
            height=2,
            width=10,
            command=lambda: self.controller.show_frame("UpdateTorque"),
        )
        updateTorqueButton.pack(side=BOTTOM, anchor=W, padx=7)

        self.chartDropdown.bind("<<ComboSelected>>", self.newSelection)
        self.chartDropdown.pack(side=BOTTOM, anchor=W)

        # End Trial Button
        endTrialButton = tk.Button(
            self,
            text="End Trial",
            height=2,
            width=10,
            command=async_handler(self.on_end_trial_button_clicked),
        )
        endTrialButton.pack(side=BOTTOM, anchor=E, pady=7, padx=7)

    def newSelection(self, event=None):
        # Clear previous plots
        for plot in self.currentPlots:
            plot.canvas.get_tk_widget().pack_forget()
        self.currentPlots = []

        # Determine which plots to show
        selection = self.chartVar.get()
        if selection == "Torque":
            self.currentPlots = [self.leftTorquePlot, self.rightTorquePlot]
        elif selection == "State":
            # Assuming LeftStatePlot and RightStatePlot are defined similarly
            self.currentPlots = [self.leftStatePlot, self.rightStatePlot]

        # Pack the selected plots
        for plot in self.currentPlots:
            plot.canvas.get_tk_widget().pack()

        self.plot_update_flag = True  # Start updating the selected plots
        self.update_plots()

    def update_plots(self):
        if self.plot_update_flag:
            for plot in self.currentPlots:
                plot.animate()
            self.after(20, self.update_plots)  # Re-schedule the update

    def stop_plot_updates(self):
        self.plot_update_flag = False

    def show(self):
        self.newSelection()  # Ensure plots are updated when the frame is shown
        self.tkraise()

    async def on_end_trial_button_clicked(self):
        await self.endTrialButtonClicked()

    async def endTrialButtonClicked(self):
        await self.ShutdownExo()

        self.controller.show_frame("ScanWindow")

    async def ShutdownExo(self):
        # End trial
        await self.controller.deviceManager.motorOff()  # Turn off motors
        await self.controller.deviceManager.stopTrial()  # End trial
        # Disconnect from Exo
        self.controller.trial.loadDataToCSV(
            self.controller.deviceManager
        )  # Load data from Exo into CSV
