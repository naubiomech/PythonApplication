import tkinter as tk

import cProfile
import pstats
import io
import time
import subprocess
import os

from tkinter import (BOTTOM, CENTER, LEFT, RIGHT, TOP, E, IntVar, N, StringVar,
                     W, X, Y, ttk)

from async_tkinter_loop import async_handler

from Widgets.Charts.chart import BottomPlot, TopPlot

from Games.virtualController import VirtualController



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
        self.plot_update_job = None

        self.create_widgets()
    
    # Launch game function
    def launchPythonGame(self):
        # Define game location
        gamePath = os.path.join(os.getcwd(), "Games", "controller_demo_grape_stomp.py")
        
        # Open game in a separate process to continue the rest of the program
        try:
            # Launch the game as a separate process
            subprocess.Popen(["python", gamePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Game launched successfully in the background.")
        except Exception as e:
            print(f"Failed to launch the game: {e}")

    # Create widgets function
    def create_widgets(self):
        style = ttk.Style()
        style.configure("Custom.TCombobox", font=("Arial", 16), padding=10)

        # Main container for Active Trial elements
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Active Trial title label
        calibrationMenuLabel = ttk.Label(main_frame, text="Active Trial", font=("Arial", 40))
        calibrationMenuLabel.pack(pady=20)

        # Battery percentage label (anchored to the right)
        battery_frame = ttk.Frame(main_frame)
        battery_frame.pack(fill="x", pady=5)
        batteryPercentLabel = ttk.Label(
            battery_frame,
            textvariable=self.controller.deviceManager._realTimeProcessor._exo_data.BatteryPercent,
            font=("Arial", 12),
            anchor="e",
        )
        batteryPercentLabel.pack(side="right")

        # Create and place the top plot
        self.topPlot = TopPlot(main_frame)
        self.topPlot.canvas.get_tk_widget().pack(fill="both", expand=True, pady=5)

        # Create and place the bottom plot
        self.bottomPlot = BottomPlot(main_frame)
        self.bottomPlot.canvas.get_tk_widget().pack(fill="both", expand=True, pady=5)

        # Chart selection button
        self.chartButton = ttk.Button(
            main_frame,
            text="Controller",
            command=self.toggle_chart,
            style="Custom.TButton",
        )
        self.chartButton.pack(pady=10)

        # Graph selection buttons frame
        graph_button_frame = ttk.Frame(main_frame)
        graph_button_frame.pack(pady=10)

        self.bothGraphsButton = ttk.Button(
            graph_button_frame,
            text="Both Graphs",
            command=lambda: self.set_graph("Both Graphs"),
            style="Custom.TButton",
        )
        self.bothGraphsButton.pack(side=LEFT, padx=5)

        self.topGraphButton = ttk.Button(
            graph_button_frame,
            text="Top Graph",
            command=lambda: self.set_graph("Top Graph"),
            style="Custom.TButton",
        )
        self.topGraphButton.pack(side=LEFT, padx=5)

        self.bottomGraphButton = ttk.Button(
            graph_button_frame,
            text="Bottom Graph",
            command=lambda: self.set_graph("Bottom Graph"),
            style="Custom.TButton",
        )
        self.bottomGraphButton.pack(side=LEFT, padx=5)

        # Buttons at the bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=LEFT, fill="y", padx=20, pady=20)

        updateTorqueButton = ttk.Button(
            button_frame,
            text="Update Controller",
            command=self.go_to_update_torque,
        )
        updateTorqueButton.pack(pady=5)

        BioFeedbackButton = ttk.Button(
            button_frame,
            text="Bio Feedback",
            command=self.handle_BioFeedbackButton_button,
        )
        BioFeedbackButton.pack(pady=5)

        MachineLearningButton = ttk.Button(
            button_frame,
            text="Machine Learning",
            command=self.handle_MachineLearning_button,
        )
        MachineLearningButton.pack(pady=5)

        self.recalibrateFSRButton = ttk.Button(
            button_frame,
            text="Recalibrate FSRs",
            command=async_handler(self.on_recal_FSR_button_clicked),
        )
        self.recalibrateFSRButton.pack(pady=5)

        sendFsrValuesButton = ttk.Button(
            button_frame,
            text="Send Preset FSR Values",
            command=self.create_fsr_input_dialog,
        )
        sendFsrValuesButton.pack(pady=5)

        markButton = ttk.Button(
            button_frame,
            textvariable=self.controller.deviceManager._realTimeProcessor._exo_data.MarkLabel,
            command=async_handler(self.on_mark_button_clicked),
        )
        markButton.pack(pady=5)

        endTrialButton = ttk.Button(
            button_frame,
            text="End Trial",
            command=async_handler(self.on_end_trial_button_clicked),
        )
        endTrialButton.pack(pady=5)

        # Launch game button at the bottom
        launchGameButton = ttk.Button(
            main_frame,
            text="Launch Game",
            command=self.launchPythonGame,
        )
        launchGameButton.pack(pady=20)


            
    def toggle_chart(self):
        """Toggle between 'Controller' and 'Sensor' for the chart."""
        current = self.chartVar.get()
        if current == "Controller":
            self.chartVar.set("Sensor")
            self.chartButton.config(text="Sensor")
        else:
            self.chartVar.set("Controller")
            self.chartButton.config(text="Controller")
        self.newSelection()

    def set_graph(self, selection):
        """Set the graph display based on the button clicked."""
        self.graphVar.set(selection)
        self.newSelection()

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
            ttk.messagebox.showerror("Invalid Input", "Please enter valid numbers for FSR values.")

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
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Button) or isinstance(widget, ttk.Combobox):
                widget.config(state='disabled')

    def ActiveTrial_on_device_disconnected(self):
        ttk.messagebox.showwarning("Device Disconnected", "Please Reconnect")
        
        self.controller.trial.loadDataToCSV(
            self.controller.deviceManager, True
        )  # Load data from Exo into CSV
        self.controller.show_frame("ScanWindow")# Navigate back to the scan page
        self.controller.frames["ScanWindow"].show()  # Call show method to reset elements

    def enable_interactions(self):
        try:
            # Enable other widgets
            for widget in self.winfo_children():
                if isinstance(widget, ttk.Button) or isinstance(widget, ttk.Combobox):
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