import tkinter as tk
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import Data.SaveModelData as saveModelData
from tkinter import (BOTTOM, CENTER, LEFT, RIGHT, TOP, E, N, S, IntVar, StringVar, W, X, Y, ttk)
from async_tkinter_loop import async_handler
from Widgets.Charts.chart import BottomPlot, TopPlot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Biofeedback Frame
class MachineLearning(tk.Frame):
    # Constructor for frame
    def __init__(self, parent, controller):
        super().__init__(parent)
        # Controller object to switch frames
        self.controller = controller
        
        # Set the disconnection callback
        self.controller.deviceManager.on_disconnect = self.MachineLearning_on_device_disconnected

        # Variables to manage states and UI elements
        self.var = IntVar()
        self.chartVar = StringVar()
        self.chartVar.set("Controller")

        # Create StringVars for button names
        self.levelButtonName = StringVar()
        self.descendButtonName = StringVar()
        self.ascendButtonName = StringVar()
        self.modelButtonName = StringVar()
        self.deleteModelButtonName = StringVar()
        
        # Confirmation flag for deleting model
        self.confirmation = 0

        #create our model controll names, frequently changed
        self.levelButtonName=StringVar()
        self.descendButtonName=StringVar()
        self.ascendButtonName=StringVar()
        self.modelButtonName=StringVar()
        self.deleteModelButtonName=StringVar()
        #self.controlModeLabel=StringVar()
        #self.controlMode=0
        self.confirmation=0 #used as a flag to request second confirmation form user to delete model
        self.modelDataWriter = saveModelData.CsvWritter()

        # Dropdown for chart selection
        self.chartDropdown = ttk.Combobox(
            self,
            textvariable=self.chartVar,
            state="readonly",
            values=["Controller", "Sensor"],
        )

        # Back button to return to the Active Trial frame
        backButton = tk.Button(self, text="Back", command=self.handle_back_button)
        backButton.pack(side=TOP, anchor=W, pady=10, padx=10)

        # Title label for the frame
        calibrationMenuLabel = tk.Label(self, text="Machine learning", font=("Arial", 40))
        calibrationMenuLabel.pack(side=TOP, anchor=N, pady=10)

        # Battery status label
        batteryPercentLabel = tk.Label(
            self, 
            textvariable=self.controller.deviceManager._realTimeProcessor._exo_data.BatteryPercent, 
            font=("Arial", 12)
        )
        batteryPercentLabel.pack(side=TOP, anchor=E, pady=0, padx=0)

        # Initialize top and bottom plots
        self.topPlot = TopPlot(self)
        self.bottomPlot = BottomPlot(self)

        # Bind dropdown selection to update function
        self.chartDropdown.bind("<<ComboboxSelected>>", self.newSelection)
        self.chartDropdown.pack(pady=10, padx=10)

        # Store current plots for updating
        self.currentPlots = [self.topPlot, self.bottomPlot]
        self.plot_update_job = None  # Store the job reference

        # Create the UI elements
        self.create_widgets()

    # Frame UI elements
    def create_widgets(self):
        # Model Status Label
        modelStatusLabel = tk.Label(
            self, 
            textvariable=self.controller.deviceManager._realTimeProcessor._predictor.modelStatus, 
            font=("Arial", 12)
        )
        modelStatusLabel.place(relx=0.75, rely=0.55)

        # Update Torque Button
        updateTorqueButton = tk.Button(
            self,
            text="Update Torque",
            command=self.go_to_update_torque,
        )
        updateTorqueButton.place(relx=0.75, rely=0.35)

        # Recalibrate FSRs Button
        self.recalibrateFSRButton = tk.Button(
            self,
            text="Recalibrate FSRs",
            command=async_handler(self.on_recal_FSR_button_clicked),
        )
        self.recalibrateFSRButton.place(relx=0.75, rely=0.40)

        # End Trial Button
        endTrialButton = tk.Button(
            self,
            text="End Trial",
            command=async_handler(self.on_end_trial_button_clicked),
        )
        endTrialButton.place(relx=0.75, rely=0.8)

        # Mark Trial Button
        markButton = tk.Button(
            self,
            textvariable=self.controller.deviceManager._realTimeProcessor._exo_data.MarkLabel,
            command=async_handler(self.on_mark_button_clicked),
        )
        markButton.place(relx=0.85, rely=0.35)
        
        # Level Trial Button
        self.levelButtonName.set("Collect Level Data")
        levelTrialButton = tk.Button(
            self,
            textvariable=self.levelButtonName,
            command=async_handler(self.on_level_trial_button_clicked),
        )
        levelTrialButton.place(relx=0.75, rely=0.6)
        
        # Display Level Step Count
        lvlstepsLabel = tk.Label(
            self, 
            textvariable=self.controller.deviceManager._realTimeProcessor._predictor.levelStepsLabel, 
            font=("Arial", 12)
        )
        lvlstepsLabel.place(relx=0.7, rely=0.6)

        # Descend Trial Button
        self.descendButtonName.set("Collect Descend Data")
        descendTrialButton = tk.Button(
            self,
            textvariable=self.descendButtonName,
            command=async_handler(self.on_descend_trial_button_clicked),
        )
        descendTrialButton.place(relx=0.75, rely=0.65)

        # Display Descend Step Count
        desstepsLabel = tk.Label(
            self, 
            textvariable=self.controller.deviceManager._realTimeProcessor._predictor.descendStepsLabel, 
            font=("Arial", 12)
        )
        desstepsLabel.place(relx=0.7, rely=0.65)

        # Ascend Trial Button
        self.ascendButtonName.set("Collect Ascend Data")
        ascendTrialButton = tk.Button(
            self,
            textvariable=self.ascendButtonName,
            command=async_handler(self.on_ascend_trial_button_clicked),
        )
        ascendTrialButton.place(relx=0.75, rely=0.7)

        # Display Ascend Step Count
        ascstepsLabel = tk.Label(
            self, 
            textvariable=self.controller.deviceManager._realTimeProcessor._predictor.ascendStepsLabel, 
            font=("Arial", 12)
        )
        ascstepsLabel.place(relx=0.7, rely=0.7)

        # Create Model Button
        if self.controller.deviceManager._realTimeProcessor._predictor.modelExists:
            self.modelButtonName.set("Stair Model Active " + str(self.controller.deviceManager._realTimeProcessor._predictor.optimizedscore) + "% Acc")
        else:
            self.modelButtonName.set("Create Stair Model")

        createModelButton = tk.Button(
            self,
            textvariable=self.modelButtonName,
            command=async_handler(self.on_model_button_clicked),
        )
        createModelButton.place(relx=0.75, rely=0.75)

        # Delete Model Button
        self.deleteModelButtonName.set("Delete Model")
        deleteModelButton = tk.Button(
            self,
            textvariable=self.deleteModelButtonName,
            command=async_handler(self.on_delete_model_button_clicked),
        )
        deleteModelButton.place(relx=0.1, rely=0.9)

        stiffnessInput = tk.Text(self, height=2, width=10)
        stiffnessInput.place(relx=0.9, rely=0.65)
        
        updateStiffnessButton = tk.Button(
            self,
            text="Update Stiffness",
            command=async_handler(self.controller.deviceManager.newStiffness,stiffnessInput),
        )
        updateStiffnessButton.place(relx=0.9, rely=0.7)

        self.controller.deviceManager._realTimeProcessor._predictor.controlModeLabel.set("Control Mode: Manual")
        toggleControlButton = tk.Button(
            self,
            textvariable=self.controller.deviceManager._realTimeProcessor._predictor.controlModeLabel,
            command=async_handler(self.on_toggle_control_button_clicked),
        )
        toggleControlButton.place(relx=0.9, rely=0.75)

    # Navigate to the Update Torque frame
    def go_to_update_torque(self):
        self.controller.frames["UpdateTorque"].previous_frame = "MachineLearning"
        self.controller.show_frame("UpdateTorque")

    # Handle back button press
    def handle_back_button(self):
        self.stop_plot_updates()  # Stop ongoing plot updates
        self.controller.show_frame("ActiveTrial")  # Switch to ActiveTrial frame
        active_trial_frame = self.controller.frames["ActiveTrial"]
        active_trial_frame.newSelection(self)  # Start plotting in the active trial

    # Show frame and update plots
    def show(self):
        self.newSelection()

    # Handle Level Trial Button click
    async def on_level_trial_button_clicked(self):
        '''
        If not currently recording data, 
            record and label data as level.
        If recording, end the recording.
        '''
        if self.controller.deviceManager._realTimeProcessor._predictor.state == 0:  # If not recording
            self.controller.deviceManager._realTimeProcessor._predictor.state = 1  # Record as level
            self.levelButtonName.set("End Level Collection")
        elif self.controller.deviceManager._realTimeProcessor._predictor.state == 1:  # If recording
            self.controller.deviceManager._realTimeProcessor._predictor.state = 0  # Stop recording
            self.levelButtonName.set("Collect Level Data")

    # Handle Descend Trial Button click
    async def on_descend_trial_button_clicked(self):
        if self.controller.deviceManager._realTimeProcessor._predictor.state == 0:  # If not recording
            self.controller.deviceManager._realTimeProcessor._predictor.state = 2  # Record as descend
            self.descendButtonName.set("End Descend Collection")
        elif self.controller.deviceManager._realTimeProcessor._predictor.state == 2:  # If recording
            self.controller.deviceManager._realTimeProcessor._predictor.state = 0  # Stop recording
            self.descendButtonName.set("Collect Descend Data")

    # Handle Ascend Trial Button click
    async def on_ascend_trial_button_clicked(self):
        if self.controller.deviceManager._realTimeProcessor._predictor.state == 0:  # If not recording
            self.controller.deviceManager._realTimeProcessor._predictor.state = 3  # Record as ascend
            self.ascendButtonName.set("End Ascend Collection")
        elif self.controller.deviceManager._realTimeProcessor._predictor.state == 3:  # If recording
            self.controller.deviceManager._realTimeProcessor._predictor.state = 0  # Stop recording
            self.ascendButtonName.set("Collect Ascend Data")

    # Handle Model Button click
    async def on_model_button_clicked(self):
        if not self.controller.deviceManager._realTimeProcessor._predictor.modelExists:  # If there is no model
            if len(self.controller.deviceManager._realTimeProcessor._predictor.database):  # If there is data
                self.controller.deviceManager._realTimeProcessor._predictor.createModel()  # Create the model
                self.modelButtonName.set("Stair Model Active " + str(self.controller.deviceManager._realTimeProcessor._predictor.optimizedscore) + "% Acc")
                # Save the data for troubleshooting or future use
                if self.controller.deviceManager._realTimeProcessor._predictor.database:  
                    self.modelDataWriter.writeToCsv(self.controller.deviceManager._realTimeProcessor._exo_data, self.controller.deviceManager._realTimeProcessor._predictor)
            else:
                self.modelButtonName.set("Collect Level, Descend, Ascend Data First")  # Prompt to collect data first
        else:
            self.modelButtonName.set("Stair Model Active " + str(self.controller.deviceManager._realTimeProcessor._predictor.optimizedscore) + "% Acc")

    # Handle Delete Model Button click
    async def on_delete_model_button_clicked(self):
        if self.confirmation == 0:  # Flag for confirmation
            self.deleteModelButtonName.set("Are you Sure?")  # Ask for confirmation
            self.confirmation += 1 
        else:
            self.controller.deviceManager._realTimeProcessor._predictor.deleteModel()  # Delete model
            self.modelButtonName.set("Create Stair Model")  # Reset labels and flags
            self.deleteModelButtonName.set("Delete Model")
            self.confirmation=0
    
    async def toggleControl(self):
        self.controller.deviceManager._realTimeProcessor._predictor.controlMode+=1 #toggle to the next mode
        if self.controller.deviceManager._realTimeProcessor._predictor.controlMode==1: #check new mode
            self.controller.deviceManager._realTimeProcessor._predictor.controlModeLabel.set("Control Mode: Machine Learner") 
        else: #if we exceed total number of modes, return to default
            self.controller.deviceManager._realTimeProcessor._predictor.controlMode=0
            self.controller.deviceManager._realTimeProcessor._predictor.controlModeLabel.set("Control Mode: Manual") 
            

    async def on_toggle_control_button_clicked(self):
        await self.toggleControl()

    # Handle Mark Button click
    async def on_mark_button_clicked(self):
        self.controller.deviceManager._realTimeProcessor._exo_data.MarkVal += 1
        self.controller.deviceManager._realTimeProcessor._exo_data.MarkLabel.set("Mark: " + str(self.controller.deviceManager._realTimeProcessor._exo_data.MarkVal))

    # Handle Recalibrate FSRs Button click
    async def on_recal_FSR_button_clicked(self):
        await self.recalibrateFSR()

    # Recalibrate FSRs
    async def recalibrateFSR(self):
        await self.controller.deviceManager.calibrateFSRs()

    # Handle End Trial Button click
    async def on_end_trial_button_clicked(self):
        await self.endTrialButtonClicked()

    # End Trial Button click functionality
    async def endTrialButtonClicked(self):
        await self.ShutdownExo()
        self.controller.show_frame("ScanWindow")

    # Update plots based on selection
    def update_plots(self, selection):
        # Cancel previous update job if it exists
        if self.plot_update_job:
            self.after_cancel(self.plot_update_job)

        # Animate all current plots
        for plot in self.currentPlots:
            plot.animate(selection)

        # Schedule the next update
        self.plot_update_job = self.after(20, self.update_plots, selection)  # Schedule with a delay
        self.after(20, self.enable_interactions)  # Enable interactions after first update

    # Handle new selection in dropdown
    def newSelection(self, event=None):
        # Disable buttons and dropdown until process completes
        self.disable_interactions()

        # Determine which plots to show
        selection = self.chartVar.get()
        self.update_plots(selection)

    # Disable interactions for buttons and dropdown
    def disable_interactions(self):
        self.chartDropdown.config(state='disabled')
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button) or isinstance(widget, ttk.Combobox):
                widget.config(state='disabled')

    # Enable interactions for buttons and dropdown
    def enable_interactions(self):
        self.chartDropdown.config(state='normal')
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button) or isinstance(widget, ttk.Combobox):
                widget.config(state='normal')

    # Stop plot updates
    def stop_plot_updates(self):
        if self.plot_update_job:
            self.after_cancel(self.plot_update_job)
            self.plot_update_job = None

    # Shutdown the exoskeleton
    async def ShutdownExo(self):
        await self.controller.deviceManager.motorOff()  # Turn off motors
        await self.controller.deviceManager.stopTrial()  # End trial
        # Load data from Exo into CSV
        self.controller.trial.loadDataToCSV(self.controller.deviceManager)

    def MachineLearning_on_device_disconnected(self):
        tk.messagebox.showwarning("Device Disconnected", "Please Reconnect")
        
        self.controller.trial.loadDataToCSV(
            self.controller.deviceManager, True
        )  # Load data from Exo into CSV
        self.controller.show_frame("ScanWindow")# Navigate back to the scan page
        self.controller.frames["ScanWindow"].show()  # Call show method to reset elements
            
