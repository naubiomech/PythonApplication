import tkinter as tk
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import Data.SaveModelData as saveModelData

from tkinter import (BOTTOM, CENTER, LEFT, RIGHT, TOP, E, N, S, IntVar, StringVar, W,
                     X, Y, ttk)
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
        self.var = IntVar()
        self.chartVar = StringVar()
        self.chartVar.set("Controller")


        #create our model controll names, frequently changed
        self.levelButtonName=StringVar()
        self.descendButtonName=StringVar()
        self.ascendButtonName=StringVar()
        self.modelButtonName=StringVar()
        self.deleteModelButtonName=StringVar()
        self.confirmation=0 #used as a flag to request second confirmation form user to delete model
        self.modelDataWriter = saveModelData.CsvWritter()
        
        self.chartDropdown = ttk.Combobox(
            self,
            textvariable=self.chartVar,
            state="readonly",
            values=[
                "Controller",
                "Sensor",
            ],
        )

        # Back button to return to the Active Trial frame
        backButton = tk.Button(self, text="Back", command=self.handle_back_button)
        backButton.pack(side=TOP, anchor=W, pady=10, padx=10)

        # Active Trial title label
        calibrationMenuLabel = tk.Label(self, text="Machine learning", font=("Arial", 40))
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

        #Define Model Status
        modelStatusLabel = tk.Label(
            self, textvariable=self.controller.deviceManager._realTimeProcessor._predictor.modelStatus, font=("Arial", 12))
        modelStatusLabel.place(relx=0.75, rely=0.55)

        # Update torque button
        updateTorqueButton = tk.Button(
            self,
            text="Update Torque",
            command=self.go_to_update_torque,
        )
        updateTorqueButton.place(relx=0.75, rely=0.35)

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
        #Display Level Step Count 
        lvlstepsLabel = tk.Label(
            self, textvariable=self.controller.deviceManager._realTimeProcessor._predictor.levelStepsLabel, font=("Arial", 12))
        lvlstepsLabel.place(relx=0.7, rely=0.6)

        
        # Descend Trial Button
        self.descendButtonName.set("Collect Descend Data")
        descendTrialButton = tk.Button(
            self,
            textvariable=self.descendButtonName,
            command=async_handler(self.on_descend_trial_button_clicked),
        )
        descendTrialButton.place(relx=0.75, rely=0.65)
        #Display Descend Step Count 
        desstepsLabel = tk.Label(
            self, textvariable=self.controller.deviceManager._realTimeProcessor._predictor.descendStepsLabel, font=("Arial", 12))
        desstepsLabel.place(relx=0.7, rely=0.65)

        
        # Ascend Trial Button
        self.ascendButtonName.set("Collect Ascend Data")
        ascendTrialButton = tk.Button(
            self,
            textvariable=self.ascendButtonName,
            command=async_handler(self.on_ascend_trial_button_clicked),
        )
        ascendTrialButton.place(relx=0.75, rely=0.7)
        ascstepsLabel = tk.Label(
            self, textvariable=self.controller.deviceManager._realTimeProcessor._predictor.ascendStepsLabel, font=("Arial", 12))
        ascstepsLabel.place(relx=0.7, rely=0.7)

        #Create Model Button
        if (self.controller.deviceManager._realTimeProcessor._predictor.modelExists): #if there is no model
            self.modelButtonName.set("Stair Model Active " + str(self.controller.deviceManager._realTimeProcessor._predictor.optimizedscore) +"% Acc") #do nothing and request the user collect data first
        else:
            self.modelButtonName.set("Create Stair Model")
        createModelButton = tk.Button(
            self,
            textvariable=self.modelButtonName,
            command=async_handler(self.on_model_button_clicked),
        )
        createModelButton.place(relx=0.75, rely=0.75)

        #Delete Model Button 
        self.deleteModelButtonName.set("Delete Model")
        deleteModelButton = tk.Button(
            self,
            textvariable=self.deleteModelButtonName,
            command=async_handler(self.on_delete_model_button_clicked),
        )
        deleteModelButton.place(relx=0.1, rely=0.9)

    def go_to_update_torque(self):
        # Set the previous frame to this one
        self.controller.frames["UpdateTorque"].previous_frame = "MachineLearning"
        self.controller.show_frame("UpdateTorque")

    def handle_back_button(self):
        # Stops plotting and goes back to Active Trial
        self.stop_plot_updates()  # Stop any ongoing plot updates
        self.controller.show_frame("ActiveTrial")  # Switch to ActiveTrial frame
        active_trial_frame = self.controller.frames["ActiveTrial"]
        active_trial_frame.newSelection(self)  # Start the plotting on active trial

    def show(self):
        # Show the frame and update plots
        self.newSelection()

    async def on_level_trial_button_clicked(self):
        '''
        If not currently recording data, 
            record and label data as level
        If recording
            end the recording       
        '''
        if self.controller.deviceManager._realTimeProcessor._predictor.state ==0:#if not recording data
            self.controller.deviceManager._realTimeProcessor._predictor.state =1 #record and label as level
            self.levelButtonName.set("End Level Collection")
        elif self.controller.deviceManager._realTimeProcessor._predictor.state ==1: #if recording
            self.controller.deviceManager._realTimeProcessor._predictor.state =0 #stop
            self.levelButtonName.set("Collect Level Data")

    async def on_descend_trial_button_clicked(self):
        if self.controller.deviceManager._realTimeProcessor._predictor.state ==0:#if not recording data
            self.controller.deviceManager._realTimeProcessor._predictor.state =2 #record and label as descend
            self.descendButtonName.set("End Descend Collection")
        elif self.controller.deviceManager._realTimeProcessor._predictor.state ==2: #if recording
            self.controller.deviceManager._realTimeProcessor._predictor.state =0 #stop
            self.descendButtonName.set("Collect Descend Data")

    async def on_ascend_trial_button_clicked(self):
        if self.controller.deviceManager._realTimeProcessor._predictor.state ==0: #if not recording data
            self.controller.deviceManager._realTimeProcessor._predictor.state =3 #record and label as ascend
            self.ascendButtonName.set("End Ascend Collection")
        elif self.controller.deviceManager._realTimeProcessor._predictor.state ==3: #if recording
            self.controller.deviceManager._realTimeProcessor._predictor.state =0 #stop
            self.ascendButtonName.set("Collect Ascend Data")
    
    async def on_model_button_clicked(self):
        if not (self.controller.deviceManager._realTimeProcessor._predictor.modelExists): #if there is no model
            if len(self.controller.deviceManager._realTimeProcessor._predictor.database): #if there is data 
                self.controller.deviceManager._realTimeProcessor._predictor.createModel() #create the model
                self.modelButtonName.set("Stair Model Active " + str(self.controller.deviceManager._realTimeProcessor._predictor.optimizedscore) +"% Acc")
                if self.controller.deviceManager._realTimeProcessor._predictor.database: #if we collected data to generate a mode
                    #save the data, for trouble shooting, replication, or future use
                    self.modelDataWriter.writeToCsv(self.controller.deviceManager._realTimeProcessor._exo_data,self.controller.deviceManager._realTimeProcessor._predictor)
            else:
                self.modelButtonName.set("Collect Level, Descend, Ascend Data First") #do nothing and request the user collect data first
        else:
            self.modelButtonName.set("Stair Model Active " + str(self.controller.deviceManager._realTimeProcessor._predictor.optimizedscore) +"% Acc")
            
    
    async def on_delete_model_button_clicked(self):
        if self.confirmation==0: #flag
            self.deleteModelButtonName.set("Are you Sure?") #ask the user to confirm intentions to delete model
            self.confirmation=self.confirmation+1 
        else:
            self.controller.deviceManager._realTimeProcessor._predictor.deleteModel() #user indicated confirmation, delete model
            self.modelButtonName.set("Create Stair Model") #reset labels and flags
            self.deleteModelButtonName.set("Delete Model")
            self.confirmation=0

    async def on_mark_button_clicked(self):
        self.controller.deviceManager._realTimeProcessor._exo_data.MarkVal += 1
        self.controller.deviceManager._realTimeProcessor._exo_data.MarkLabel.set("Mark: " +str(self.controller.deviceManager._realTimeProcessor._exo_data.MarkVal))

    async def on_recal_FSR_button_clicked(self):
        await self.recalibrateFSR()

    async def recalibrateFSR(self):
        await self.controller.deviceManager.calibrateFSRs()

    async def on_end_trial_button_clicked(self):
        await self.endTrialButtonClicked()

    async def endTrialButtonClicked(self):
        await self.ShutdownExo()
        self.controller.show_frame("ScanWindow")

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

    def newSelection(self, event=None):
        # Disable buttons and dropdown until proccess complete
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

    def stop_plot_updates(self):
        if self.plot_update_job:
            self.after_cancel(self.plot_update_job)
            self.plot_update_job = None

    async def ShutdownExo(self):
        # End trial
        await self.controller.deviceManager.motorOff()  # Turn off motors
        await self.controller.deviceManager.stopTrial()  # End trial
        # Disconnect from Exo
        self.controller.trial.loadDataToCSV(
            self.controller.deviceManager
        )  # Load data from Exo into CSV
