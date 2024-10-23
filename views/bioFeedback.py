import tkinter as tk
from tkinter import (BOTTOM, CENTER, LEFT, RIGHT, TOP, E, N, S, IntVar, StringVar, W,
                     X, Y, ttk, simpledialog)
import pygame  # Import pygame for sound
from async_tkinter_loop import async_handler
from Widgets.Charts.chart import FSRPlot

# Initialize Pygame for sound
pygame.mixer.init()

# Load sound file (ensure the path is correct)
# Replace 'notification.wav' with your sound file
notification_sound = pygame.mixer.Sound('notification.wav')

# Biofeedback Frame
class BioFeedback(tk.Frame):
    # Constructor for frame
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller  # Reference to the main application controller
        self.chartVar = StringVar()  # Variable for storing the selected leg
        self.chartVar.set("Left Leg")  # Default selection

        # Set the disconnection callback
        self.controller.deviceManager.on_disconnect = self.BioFeedback_on_device_disconnected

        # Counter variable to track the number of goals reached
        self.counter = 0
        self.counter_var = IntVar(value=self.counter)

        # Target value variable
        self.target_value = None
        self.target_var = StringVar(value="No target set")  # Display the target value

        # Drop down menu for selecting left or right leg
        self.chartDropdown = ttk.Combobox(
            self,
            textvariable=self.chartVar,
            state="readonly",
            values=["Left Leg", "Right Leg"],
        )

        # Back button to return to the Active Trial frame
        backButton = tk.Button(self, text="Back", command=self.handle_back_button)
        backButton.pack(side=TOP, anchor=W, pady=10, padx=10)

        # Biofeedback title label
        calibrationMenuLabel = tk.Label(self, text="Biofeedback", font=("Arial", 40))
        calibrationMenuLabel.pack(side=TOP, anchor=N, pady=20)

        # For battery Label
        batteryPercentLabel = tk.Label(self, 
            textvariable=self.controller.
            deviceManager._realTimeProcessor._exo_data.BatteryPercent, 
                font=("Arial", 12))
        batteryPercentLabel.pack(side=TOP, anchor=E, pady=0, padx=0)

        # Initialize the FSR plot
        self.FSRPlot = FSRPlot(self)
        self.currentPlots = self.FSRPlot  # Current plot reference

        # Bind dropdown selection change to update plots
        self.chartDropdown.bind("<<ComboboxSelected>>", self.newSelection)
        self.chartDropdown.pack()

        self.plot_update_job = None  # Store the job reference for plot updates

        # Label to display targets reached
        self.targets_reached_label = tk.Label(self, text="Targets Reached: 0",
                                               font=("Arial", 20))
        self.targets_reached_label.pack(side=TOP, anchor=CENTER, pady=10)

        # Create the buttons and labels
        self.create_widgets()

    def create_widgets(self):
        # Frame for target value buttons
        target_frame = tk.Frame(self)
        target_frame.pack(side=TOP, anchor=CENTER, pady=10)

        # Button to set target value
        self.target_button = tk.Button(target_frame, text="Set Target Value", 
            command=self.ask_target_value)
        self.target_button.pack(side=LEFT, padx=5)

        # Reset button for target value
        self.reset_button = tk.Button(target_frame, 
            text="Reset Target Value", command=self.reset_target, state="disabled")
        self.reset_button.pack(side=LEFT, padx=5)

        # Label to display the target value
        self.target_label = tk.Label(self, textvariable=self.target_var, font=("Arial", 20))
        self.target_label.pack(side=TOP, anchor=CENTER, pady=10)

        # Frame for advanced buttons
        advanced_frame = tk.Frame(self)
        advanced_frame.pack(side=TOP, anchor=CENTER, pady=10)
        
        # Mark Trial Button
        markButton = tk.Button(
            advanced_frame,
            textvariable=self.controller.deviceManager._realTimeProcessor._exo_data.MarkLabel,
            command=async_handler(self.on_mark_button_clicked),
        )
        markButton.pack(side=LEFT, anchor=CENTER, padx=5)

        # Recalibrate FSRs Button
        self.recalibrateFSRButton = tk.Button(
            advanced_frame,
            text="Recalibrate FSRs",
            command=async_handler(self.on_recal_FSR_button_clicked),
        )
        self.recalibrateFSRButton.pack(side=LEFT, anchor=CENTER, padx=5)

    def ask_target_value(self):
        # Prompt the user for a target value
        user_input = simpledialog.askstring("Input", "Please enter a target value:")
        
        if user_input is not None:
            try:
                # Attempt to convert the input to a float
                self.target_value = float(user_input)
                self.update_target_label()  # Update the label with the new target value
                print(f"Target value set to: {self.target_value}")

                # Enable the reset button
                self.reset_button.config(state="normal")

                # Set the goal in the current plot
                self.currentPlots.set_goal(self.target_value)
                self.update_plots(self.chartVar.get())  # Update the plot with the new goal

            except ValueError:
                print("Invalid input. Please enter a numeric value.")

    def handle_back_button(self):
        # Stops plotting and goes back to Active Trial
        self.stop_plot_updates()  # Stop any ongoing plot updates
        self.controller.show_frame("ActiveTrial")  # Switch to ActiveTrial frame
        active_trial_frame = self.controller.frames["ActiveTrial"]
        active_trial_frame.newSelection(self)  # Start the plotting on active trial

    def newSelection(self, event=None):
        # Determine which plots to show based on user selection
        selection = self.chartVar.get()
        self.update_plots(selection)  # Update the plots based on selection
    
    def reset_background(self):
        self.config(bg="SystemButtonFace")  # Reset to default color

    def reset_target(self):
        # Reset the target value to None and update the UI
        self.target_value = None
        self.update_target_label()  # Update the target label
        self.reset_button.config(state="disabled")  # Disable the reset button
        self.currentPlots.set_goal(None)  # Reset the goal in the current plot

    def stop_plot_updates(self):
        # Stop any ongoing plot updates
        if self.plot_update_job:
            self.after_cancel(self.plot_update_job)
            self.plot_update_job = None

    def update_counter_label(self):
        # Update the counter variable and label when the goal is reached
        self.counter += 1  # Increment the counter
        self.counter_var.set(self.counter)  # Update the IntVar
        self.targets_reached_label.config(text=f"Targets Reached: {self.counter}")  # Update the label
        
        # Play the notification sound
        notification_sound.play()
        # Change background color to indicate success
        self.config(bg="lightgreen")  # Change to light green
        self.after(1000, self.reset_background)  # Reset after 1 second
        
    def update_plots(self, selection):
        # Animate the current plot and schedule the next update
        # Cancel the previous update job if it exists
        if self.plot_update_job:
            self.after_cancel(self.plot_update_job)

        # Animate the current plot
        self.currentPlots.animate(selection)

        # Schedule the next update
        self.plot_update_job = self.after(20, self.update_plots, selection)

    def update_target_label(self):
        # Update the target label with the current target value
        if self.target_value is not None:
            self.target_var.set(f"Target value: {self.target_value}")
        else:
            self.target_var.set("No target set")

    def show(self):
        # Show the current selection in the plots
        self.newSelection()  # Update the plots based on current selection

    async def on_mark_button_clicked(self):
        self.controller.deviceManager._realTimeProcessor._exo_data.MarkVal += 1
        self.controller.deviceManager._realTimeProcessor._exo_data.MarkLabel.set(
            "Mark: " + str(self.controller.
                deviceManager._realTimeProcessor._exo_data.MarkVal))

    # Handle Recalibrate FSRs Button click
    async def on_recal_FSR_button_clicked(self):
        await self.recalibrateFSR()

    # Recalibrate FSRs
    async def recalibrateFSR(self):
        await self.controller.deviceManager.calibrateFSRs()

    def BioFeedback_on_device_disconnected(self):
        tk.messagebox.showwarning("Device Disconnected", "Please Reconnect")
        self.controller.trial.loadDataToCSV(
            self.controller.deviceManager, True
        )  # Load data from Exo into CSV
        self.controller.show_frame("ScanWindow")  # Navigate back to the scan page
            
