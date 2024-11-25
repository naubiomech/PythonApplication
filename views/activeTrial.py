import tkinter as tk

import cProfile
import pstats
import io
import time

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
        self.is_plotting = False  # Flag to control if plotting should happen

        # Set the disconnection callback
        self.controller.deviceManager.on_disconnect = self.ActiveTrial_on_device_disconnected
        
        self.var = IntVar()
        self.chartVar = StringVar()
        self.chartVar.set("Controller")
        self.graphVar = StringVar()
        self.graphVar.set("Both Graphs")  # Default to "Both Graphs"

        # Create a frame for the dropdowns
        dropdown_frame = tk.Frame(self)

        # Chart selection dropdown
        self.chartDropdown = ttk.Combobox(
            dropdown_frame,
            textvariable=self.chartVar,
            state="readonly",
            values=["Controller", "Sensor"],
        )
        self.chartDropdown.pack(side=LEFT, padx=5)

        # Graph selection dropdown
        self.graphDropdown = ttk.Combobox(
            dropdown_frame,
            textvariable=self.graphVar,
            state="readonly",
            values=["Both Graphs", "Top Graph", "Bottom Graph"],
        )
        self.graphDropdown.pack(side=LEFT, padx=5)

        # Create a frame for the title and end trial button
        title_frame = tk.Frame(self)
        title_frame.pack(side=TOP, pady=10, fill=X)

        # End Trial Button
        endTrialButton = tk.Button(
            title_frame,
            text="End Trial",
            height=2,
            command=async_handler(self.on_end_trial_button_clicked),
        )
        endTrialButton.pack(side=LEFT)  # Pack the button next to the title
        
        # Active Trial title label
        calibrationMenuLabel = tk.Label(title_frame, text="Active Trial", font=("Arial", 40))
        calibrationMenuLabel.pack(side=TOP, anchor=N, fill=X)

        # For battery Label
        batteryPercentLabel = tk.Label(self, 
            textvariable=self.controller.deviceManager._realTimeProcessor._exo_data.BatteryPercent, 
                font=("Arial", 12))
        batteryPercentLabel.pack(side=TOP, anchor=E, pady=0, padx=0)

        self.topPlot = TopPlot(self)
        self.bottomPlot = BottomPlot(self)

        dropdown_frame.pack(side=TOP, pady=10, anchor=CENTER)
        # Bind dropdown selections to their respective methods
        self.chartDropdown.bind("<<ComboboxSelected>>", self.newSelection)
        self.graphDropdown.bind("<<ComboboxSelected>>", self.newSelection)


        self.currentPlots = [self.topPlot, self.bottomPlot]
        self.plot_update_job = None  # Store the job reference

        self.create_widgets()


    # Frame UI elements
    def create_widgets(self):
        # Update torque button
        button_frame = tk.Frame(self)
        button_frame.pack(side=BOTTOM, pady=7, fill=X)  # Pack the button frame at the bottom

        updateTorqueButton = tk.Button(
            self,
            text="Update Controller",
            height=2,
            width=20,
            command=self.go_to_update_torque,
        )
        updateTorqueButton.pack(side=LEFT, padx=7)  # Pack the button to the left

        # Recalibrate FSRs Button
        self.recalibrateFSRButton = tk.Button(
            self,
            text="Recalibrate FSRs",
            height=2,
            width=20,
            command=async_handler(self.on_recal_FSR_button_clicked),
        )
        self.recalibrateFSRButton.pack(side=LEFT, padx=7)

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
        
        # Button for sending preset FSR values
        sendFsrValuesButton = tk.Button(
            self,
            text="Send Preset FSR Values",
            height=2,
            width=20,
            command=self.create_fsr_input_dialog,
        )
        sendFsrValuesButton.pack(side=LEFT, padx=7)

        # Mark Trial Button
        markButton = tk.Button(
            self,
            textvariable=self.controller.deviceManager._realTimeProcessor._exo_data.MarkLabel,
            height=2,
            width=10,
            command=async_handler(self.on_mark_button_clicked),
        )
        markButton.pack(side=LEFT, padx=7)

    def create_fsr_input_dialog(self):
        # Create a new Toplevel window for input
        dialog = tk.Toplevel(self)
        dialog.title("Input FSR Values")

        # Retrieve current FSR values
        left_fsr_value = self.controller.deviceManager.curr_left_fsr_value
        right_fsr_value = self.controller.deviceManager.curr_right_fsr_value

        # Current values labels
        current_values_label = tk.Label(dialog, text="Current FSR Values:", font=("Arial", 14))
        current_values_label.pack(pady=5)

        current_left_label = tk.Label(dialog, text=f"Left FSR Value: {left_fsr_value}", font=("Arial", 12))
        current_left_label.pack(pady=5)

        current_right_label = tk.Label(dialog, text=f"Right FSR Value: {right_fsr_value}", font=("Arial", 12))
        current_right_label.pack(pady=5)

        # Left FSR input
        left_fsr_label = tk.Label(dialog, text="Left FSR Value:")
        left_fsr_label.pack(pady=5)
        left_fsr_entry = tk.Entry(dialog)
        left_fsr_entry.pack(pady=5)

        # Right FSR input
        right_fsr_label = tk.Label(dialog, text="Right FSR Value:")
        right_fsr_label.pack(pady=5)
        right_fsr_entry = tk.Entry(dialog)
        right_fsr_entry.pack(pady=5)

        # Submit button
        submit_button = tk.Button(
            dialog, 
            text="Submit", 
            command=async_handler(lambda: self.submit_fsr_values(left_fsr_entry.get(), right_fsr_entry.get(), dialog))
        )
        submit_button.pack(pady=10)

    async def submit_fsr_values(self, left_value, right_value, dialog):
        # Convert the input values to appropriate types and send them
        try:
            left_value = float(left_value)
            right_value = float(right_value)

            # Clamp values
            left_value = max(0.1, min(left_value, 0.5))
            right_value = max(0.1, min(right_value, 0.5))

            await self.controller.deviceManager.sendFsrValues(left_value, right_value)
            
            dialog.destroy()

        except ValueError:
            # Handle invalid input
            tk.messagebox.showerror("Invalid Input", "Please enter valid numbers for FSR values.")

    def handle_BioFeedbackButton_button(self):
        self.controller.show_frame("BioFeedback")
        bioFeedback_frame = self.controller.frames["BioFeedback"]
        bioFeedback_frame.newSelection(self)

    def handle_MachineLearning_button(self):
        self.controller.show_frame("MachineLearning")
        machineLearning_frame = self.controller.frames["MachineLearning"]
        machineLearning_frame.newSelection(self)

    def newSelection(self, event=None):
        # Disable buttons and dropdown untill proccess complete
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

    def ActiveTrial_on_device_disconnected(self):
        tk.messagebox.showwarning("Device Disconnected", "Please Reconnect")
        
        self.controller.trial.loadDataToCSV(
            self.controller.deviceManager, True
        )  # Load data from Exo into CSV
        self.controller.show_frame("ScanWindow")# Navigate back to the scan page
        self.controller.frames["ScanWindow"].show()  # Call show method to reset elements

    def enable_interactions(self):
        try:
            # Ensure the chartDropdown widget is present and properly initialized
            if self.chartDropdown.winfo_exists():
                self.chartDropdown.config(state='normal')

            # Enable other widgets
            for widget in self.winfo_children():
                if isinstance(widget, tk.Button) or isinstance(widget, ttk.Combobox):
                    widget.config(state='normal')
        except Exception as e:
            print(f"Error in enable_interactions: {e}")

    def go_to_update_torque(self):
        # Set the previous frame to this one
        self.controller.frames["UpdateTorque"].previous_frame = "ActiveTrial"
        self.controller.show_frame("UpdateTorque")

    def update_plots(self, selection):
        # Cancel the previous update job if it exists
        if self.plot_update_job:
            self.after_cancel(self.plot_update_job)
            self.plot_update_job = None

        # Only continue updating plots if the flag is set to True
        if not self.is_plotting:
            return

        # Determine which plots to animate based on the graph selection
        graph_selection = self.graphVar.get()
        plots_to_update = []
        if graph_selection == "Both Graphs":
            plots_to_update = [self.topPlot, self.bottomPlot]
        elif graph_selection == "Top Graph":
            plots_to_update = [self.topPlot]
        elif graph_selection == "Bottom Graph":
            plots_to_update = [self.bottomPlot]

        # Animate the selected plots
        for plot in plots_to_update:
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
        self.is_plotting = False

    def show(self):
        # Show the frame and update plots
        self.is_plotting = True
        self.newSelection()

    def hide(self):
        # This method is called when switching away from this frame
        self.stop_plot_updates()

    # Handle Recalibrate FSRs Button click
    async def on_recal_FSR_button_clicked(self):
        await self.recalibrateFSR()

    # Recalibrate FSRs
    async def recalibrateFSR(self):
        await self.controller.deviceManager.calibrateFSRs()

    async def on_end_trial_button_clicked(self):
        await self.endTrialButtonClicked()

    async def endTrialButtonClicked(self):
        await self.ShutdownExo()
        self.controller.show_frame("ScanWindow")
        self.controller.frames["ScanWindow"].show()  # Call show method to reset elements

    async def ShutdownExo(self):
        # End trial
        await self.controller.deviceManager.motorOff()  # Turn off motors
        await self.controller.deviceManager.stopTrial()  # End trial
        await self.controller.deviceManager.disconnect()
        # Disconnect from Exo
        self.controller.trial.loadDataToCSV(
            self.controller.deviceManager
        )  # Load data from Exo into CSV

    async def on_mark_button_clicked(self):
        self.controller.deviceManager._realTimeProcessor._exo_data.MarkVal += 1
        self.controller.deviceManager._realTimeProcessor._exo_data.MarkLabel.set(
            "Mark: " + str(self.controller.
                deviceManager._realTimeProcessor._exo_data.MarkVal))