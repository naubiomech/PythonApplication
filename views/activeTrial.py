import tkinter as tk
from tkinter import (BOTTOM, CENTER, LEFT, RIGHT, TOP, E, IntVar, N, StringVar,
                     W, X, Y, ttk)

from async_tkinter_loop import async_handler

from Widgets.Charts.chart import BottomPlot, TopPlot


# Active Trial Frame
class ActiveTrial(tk.Frame):
    # Constructor for frame
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.var = IntVar()
        self.chartVar = StringVar()
        self.chartVar.set("Controller")

        self.chartDropdown = ttk.Combobox(
            self,
            textvariable=self.chartVar,
            state="readonly",
            values=[
                "Controller",
                "Sensor",
            ],
        )
        # Active Trial title label
        calibrationMenuLabel = tk.Label(self, text="Active Trial", font=("Arial", 40))
        calibrationMenuLabel.pack(side=TOP, anchor=N, pady=10)

        # For battery Label
        batteryPercentLabel = tk.Label(self, 
            textvariable=self.controller.deviceManager._realTimeProcessor._exo_data.BatteryPercent, 
                font=("Arial", 12))
        batteryPercentLabel.pack(side=TOP, anchor=E, pady=0, padx=0)

        self.topPlot = TopPlot(self)
        self.bottomPlot = BottomPlot(self)

        self.chartDropdown.bind("<<ComboboxSelected>>", self.newSelection)
        self.chartDropdown.pack(pady=10, padx=10)

        self.currentPlots = [self.topPlot, self.bottomPlot]
        self.plot_update_job = None  # Store the job reference

        self.create_widgets()


    # Frame UI elements
    def create_widgets(self):
        # Update torque button
        button_frame = tk.Frame(self)
        button_frame.pack(side=BOTTOM, pady=7)  # Pack the button frame at the bottom

        updateTorqueButton = tk.Button(
            self,
            text="Update Torque",
            height=2,
            width=20,
            command=self.go_to_update_torque,
        )
        updateTorqueButton.pack(side=LEFT, padx=7)  # Pack the button to the left
        
        BioFeedbackButton = tk.Button(
            self,
            text="Bio Feedback",
            height=2,
            width=20,
            command=self.handle_BioFeedbackButton_button)
        BioFeedbackButton.pack(side=LEFT, padx=7)  # Pack the button to the left

        MachineLearningButton = tk.Button(
            self,
            text="Machine Learning",
            height=2,
            width=20,
            command=self.handle_MachineLearning_button)
        MachineLearningButton.pack(side=LEFT, padx=7)  # Pack the button to the left
        
        # End Trial Button
        endTrialButton = tk.Button(
            self,
            text="End Trial",
            height=2,
            width=20,
            command=async_handler(self.on_end_trial_button_clicked),
        )
        endTrialButton.pack(side=RIGHT, padx=7)  # Pack the button to the left

    def handle_BioFeedbackButton_button(self):
        self.controller.show_frame("BioFeedback")
        bioFeedback_frame = self.controller.frames["BioFeedback"]
        bioFeedback_frame.newSelection(self)

    def handle_MachineLearning_button(self):
        self.controller.show_frame("MachineLearning")
        machineLearning_frame = self.controller.frames["MachineLearning"]
        machineLearning_frame.newSelection(self)

    def newSelection(self, event=None):
        # Disable buttons and dropdown untril proccess complete
        self.disable_interactions()

        # Determine which plots to show
        selection = self.chartVar.get()
        self.update_plots(selection)

    def disable_interactions(self):
        # Disable all interactive elements
        self.chartDropdown.config(state='disabled')
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button) or isinstance(widget, ttk.Combobox):
                widget.config(state='disabled')

    def enable_interactions(self):
        # Enable all interactive elements
        self.chartDropdown.config(state='normal')
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button) or isinstance(widget, ttk.Combobox):
                widget.config(state='normal')

    def go_to_update_torque(self):
        # Set the previous frame to this one
        self.controller.frames["UpdateTorque"].previous_frame = "ActiveTrial"
        self.controller.show_frame("UpdateTorque")

    def update_plots(self, selection):
        # Cancel the previous update job if it exists
        if self.plot_update_job:
            self.after_cancel(self.plot_update_job)

        # Animate all current plots
        for plot in self.currentPlots:
            plot.animate(selection)

        # Schedule the next update
        self.plot_update_job = self.after(
            20, self.update_plots, selection
        )  # Schedule with a delay

        # Enable interactions after the first plot update is complete
        self.after(20, self.enable_interactions)

    def stop_plot_updates(self):
        if self.plot_update_job:
            self.after_cancel(self.plot_update_job)
            self.plot_update_job = None

    def show(self):
        # Show the frame and update plots
        self.newSelection()
        
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
