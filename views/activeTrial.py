import tkinter as tk

import cProfile
import pstats
import io
import time
import tkinter.messagebox as messagebox
import os
import subprocess
import asyncio


from tkinter import (BOTTOM, CENTER, LEFT, RIGHT, TOP, E, IntVar, N, StringVar,
                     W, X, Y, ttk, DISABLED, NORMAL)

from async_tkinter_loop import async_handler
from PIL import ImageTk, Image, ImageEnhance

from Widgets.Charts.chart import BasePlot,BottomPlot, TopPlot
from views import gameSelectMenu  # Import gameSelectMenu


# Active Trial Frame
class ActiveTrial(tk.Frame):
    # Constructor for frame
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.is_plotting = False  # Flag to control if plotting should happen
        self.start_time = None  # Store the start time
        self.elapsed_time = 0  # Store the elapsed time
        self.timer_label = None  # Label for displaying the time
        self.timer_job = None  # Store the timer update job reference

        # Game-related variables
        self.selectGameButton = None
        self.launchGameButton = None
        self.stopGameButton = None
        self.selected_game = None
        self.game_process = None

        # Assistance-related variables
        self.assistanceText = None

        # Sensor dropdown variable
        self.sensor_var = tk.StringVar()
        self.sensor_var.set("Left")  # Default selection

        # Set the disconnection callback
        self.controller.deviceManager.on_disconnect = self.ActiveTrial_on_device_disconnected
        
        # UI elements
        self.fontstyle = 'Segoe UI'

        self.var = IntVar()
        self.chartVar = StringVar()
        self.chartVar.set("Controller")
        self.graphVar = StringVar()
        self.graphVar.set("Both Graphs")  # Default to "Both Graphs"

        self.create_widgets()

    # Frame UI elements
    def create_widgets(self):

        style = ttk.Style()
        style.configure("Custom.TCombobox", font=(self.fontstyle, 16), padding=10)

        # Active Trial title label
        calibrationMenuLabel = ttk.Label(self, text="Active Trial", font=(self.fontstyle, 40))
        calibrationMenuLabel.grid(row=0, column=0, columnspan=8, pady=20)

        # Load and place the smaller image behind the timer and battery
        small_image = Image.open("./Resources/Images/OpenExo.png").convert("RGBA")
        small_image = small_image.resize((int(1736*.075), int(336*.075)))  # Resize the image to a smaller size
        self.small_bg_image = ImageTk.PhotoImage(small_image)

        # Create a Canvas for the smaller image
        small_canvas = tk.Canvas(self, width=int(1736*.075), height=int(336*.075), highlightthickness=0)
        small_canvas.create_image(0, 0, image=self.small_bg_image, anchor="nw")
        small_canvas.grid(row=0, column=4, sticky="ne", padx=5, pady=10)  # Top-right corner

        # Timer label
        self.timer_label = ttk.Label(self, text="Time: 0:00", font=(self.fontstyle, 12))
        self.timer_label.grid(row=0, column=4, pady=(50,0),padx=(0,0),sticky="e")  # Placed above the battery label

        # For battery Label
        batteryPercentLabel = ttk.Label(self, 
            textvariable=self.controller.deviceManager._realTimeProcessor._exo_data.BatteryPercent, 
                font=(self.fontstyle, 12))
        # batteryPercentLabel.pack(side=TOP, anchor=E, pady=0, padx=0)
        batteryPercentLabel.grid(row=0, column=4,padx=(0,0), pady=(10,0),sticky ="e")

        # Create and place the top plot
        self.topPlot = TopPlot(self)
        self.topPlot.canvas.get_tk_widget().grid(row=1, column=1, columnspan=6, sticky="NSEW", pady=5, padx=5)

        # Create and place the bottom plot
        self.bottomPlot = BottomPlot(self)
        self.bottomPlot.canvas.get_tk_widget().grid(row=2, column=1, columnspan=6, sticky="NSEW", pady=5, padx=5)
            
        # Chart selection button
        self.chartButton = ttk.Button(
            self,
            text="Controller",
            command=self.toggle_chart,
            style="Custom.TButton",
        )
        self.chartButton.grid(row=3, column=3, padx=10, pady=10, sticky="E")

        # Buttons at the bottom
        graph_button_frame = ttk.Frame(self)
        graph_button_frame.grid(row=3, column=4, padx=(100,0))

        self.bothGraphsButton = ttk.Button(
            graph_button_frame,
            text="Both Graphs",
            command=lambda: self.set_graph("Both Graphs"),
            style="Custom.TButton",
        )
        self.bothGraphsButton.pack(side = LEFT)

        # Graph selection buttons
        self.topGraphButton = ttk.Button(
            graph_button_frame,
            text="Top Graph",
            command=lambda: self.set_graph("Top Graph"),
            style="Custom.TButton",
        )
        self.topGraphButton.pack(side = LEFT)

        self.bottomGraphButton = ttk.Button(
            graph_button_frame,
            text="Bottom Graph",
            width = 15,
            command=lambda: self.set_graph("Bottom Graph"),
            style="Custom.TButton",
        )
        self.bottomGraphButton.pack(side = LEFT)

        self.currentPlots = [self.topPlot, self.bottomPlot]
        self.plot_update_job = None  # Store the job reference


        # End Trial Button
        endTrialButton = ttk.Button(
            self,
            text="End Trial",
            command=async_handler(self.on_end_trial_button_clicked),
        )
        #endTrialButton.pack(side=LEFT)  # Pack the button next to the title
        endTrialButton.grid(row=0, column=0, pady=10)

        # Buttons at the bottom
        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=0, rowspan=5, pady=125, sticky="NS")

        updateTorqueButton = ttk.Button(
            button_frame,
            text="Update Controller",
            command=self.go_to_update_torque,
        )
        updateTorqueButton.pack(side=TOP, pady=5)

        BioFeedbackButton = ttk.Button(
            button_frame,
            text="Bio Feedback",
            command=self.handle_BioFeedbackButton_button)
        BioFeedbackButton.pack(side=TOP, pady=5)

        MachineLearningButton = ttk.Button(
            button_frame,
            text="Machine Learning",
            command=self.handle_MachineLearning_button)
        MachineLearningButton.pack(side=TOP, pady=5)
        
        # Recalibrate FSRs Button
        self.recalibrateFSRButton = ttk.Button(
            button_frame,
            text="Recalibrate FSRs",
            command=async_handler(self.on_recal_FSR_button_clicked),
        )
        self.recalibrateFSRButton.pack(side=TOP, pady=5)

        # Button for sending preset FSR values
        sendFsrValuesButton = ttk.Button(
            button_frame,
            text="Send Preset FSR Values",
            command=self.create_fsr_input_dialog,
        )
        sendFsrValuesButton.pack(side=TOP, pady=5)

        # Mark Trial Button
        markButton = ttk.Button(
            button_frame,
            textvariable=self.controller.deviceManager._realTimeProcessor._exo_data.MarkLabel,
            command=async_handler(self.on_mark_button_clicked),
        )
        markButton.pack(side=TOP, pady=5)

        # Add game controls
        self.create_game_widgets()

        # Add sensor dropdown
        self.sensorChartDropdown = ttk.Combobox(
            self,
            textvariable=self.sensor_var,
            state="readonly",
            values=["Left", "Right"],
        )
        self.sensorChartDropdown.bind("<<ComboboxSelected>>", self.on_sensor_selection)
        self.sensorChartDropdown.grid(row=3, column=5, padx=10, pady=10)

        # Configure grid weights for centering
        for i in range(7):
            self.grid_rowconfigure(i, weight=1)
        for j in range(9):
            self.grid_columnconfigure(j, weight=1)
    

    def create_game_widgets(self):
        """Create game control buttons."""
        self.controller.virtualController.create()
        game_frame = ttk.Frame(self)
        game_frame.grid(row=4, column=1, columnspan=6, pady=10)

        # Select Game Button
        self.selectGameButton = ttk.Button(
            game_frame,
            text="Select Game",
            command=async_handler(self.select_game),
        )
        self.selectGameButton.pack(side=LEFT, padx=5)

        # Launch Game Button
        self.launchGameButton = ttk.Button(
            game_frame,
            text="Launch Game",
            command=self.launch_game,
            state=DISABLED,
        )
        self.launchGameButton.pack(side=LEFT, padx=5)

        # Stop Game Button
        self.stopGameButton = ttk.Button(
            game_frame,
            text="Stop Game",
            command=self.stop_game,
            state=DISABLED,
        )
        self.stopGameButton.pack(side=LEFT, padx=5)

        # Assistance Controls
        self.assistanceText = ttk.Entry(game_frame, width=10)
        self.assistanceText.pack(side=RIGHT, padx=5)
        self.assistanceText.insert(0, "1.0")  # Default value

        setAssistanceButton = ttk.Button(
            game_frame,
            text="Set Target",
            command=self.setAssistanceButtonClicked,
        )
        setAssistanceButton.pack(side=RIGHT, padx=5)

        addAssistanceButton = ttk.Button(
            game_frame,
            text="+",
            command=self.add_assistance,
        )
        addAssistanceButton.pack(side=RIGHT, padx=5)

        removeAssistanceButton = ttk.Button(
            game_frame,
            text="-",
            command=self.remove_assistance,
        )
        removeAssistanceButton.pack(side=RIGHT, padx=5)

    async def select_game(self):
        # start the game selection process
        await gameSelectMenu.select_game(self)
        # wait for the game selection to be made aka the selected_game variable to be set
        while not self.selected_game:
            await asyncio.sleep(0.1)
        
        # After a selection is made, the launch game button will be enabled
        self.launchGameButton.config(state="normal")
        print(f"Selected game: {self.selected_game}")

    def launch_game(self):
        # Get the selected game path
        game_path = os.path.join(os.getcwd(), "Games", self.selected_game)

        # check if the game is .py or exe 
        with os.scandir(game_path) as entries:
            for entry in entries:
                print(entry.name)
                if entry.name.endswith(".py") and entry.name.startswith(self.selected_game):
                    # add .py to the game path if the game is a python file
                    game_path = os.path.join(game_path, self.selected_game + ".py")

                elif entry.name.endswith(".exe") and entry.name.startswith(self.selected_game):
                    # add .exe to the game path if the game is an executable file
                    game_path = os.path.join(game_path, self.selected_game + ".exe")
                    print(game_path)
        
        print(f"Launching game from {game_path}")
        # Create a virtual controller
        ## self.controller.virtualController.create()  # Start the virtual controller
        
        # try to launch the game
        # check if the game is a python file or an executable
        if game_path.endswith(".py"):
            self.game_process = subprocess.Popen(["python", game_path])  # Open the game as a new process
            print(f"Game launched from {game_path}")

        # check if the game is an executable
        elif game_path.endswith(".exe"):
            self.game_process = subprocess.Popen([game_path])
            print(f"Game launched from {game_path}")

        # if the game is neither a python file nor an executable
        else:
            print(f"Error launching game: {game_path}")
            

        self.stopGameButton.config(state="normal")
        self.launchGameButton.config(state="disabled")
        self.selectGameButton.config(state="disabled")

    def stop_game(self):
        """Stop the running game."""
        if self.game_process:
            self.game_process.kill()
            
            self.game_process = None
            
            # wait for the thread to join
            time.sleep(2)
            
            # Re-enable the buttons
            self.stopGameButton.config(state="disabled")
            self.launchGameButton.config(state="normal")
            self.selectGameButton.config(state="normal")

    def add_assistance(self):
        """Increase assistance level."""
        self.controller.virtualController.addAssistance()

    def remove_assistance(self):
        """Decrease assistance level."""
        self.controller.virtualController.removeAssistance()

    def setAssistanceButtonClicked(self):
        """Set assistance level based on the text box."""
        level = self.assistanceText.get()
        try:
            level = float(level)
            self.controller.virtualController.setAssistanceLevel(level)
        except ValueError:
            print("Invalid assistance level")

    def on_sensor_selection(self, event=None):
        """Handle sensor selection."""
        selected_sensor = self.sensor_var.get()
        self.controller.virtualController.setSensor(selected_sensor)






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
        current_values_label = tk.Label(dialog, text="Current FSR Values:", font=("self.fontstyle", 14))
        current_values_label.pack(pady=5)

        current_left_label = tk.Label(dialog, text=f"Left FSR Value: {left_fsr_value}", font=("self.fontstyle", 12))
        current_left_label.pack(pady=5)

        current_right_label = tk.Label(dialog, text=f"Right FSR Value: {right_fsr_value}", font=("self.fontstyle", 12))
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
            messagebox.showerror("Invalid Input", "Please enter valid numbers for FSR values.")

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
        messagebox.showwarning("Device Disconnected", "Please Reconnect")
        
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

    def startClock(self):
        self.start_time = time.time()  # Record the start time
        self.elapsed_time = 0  # Reset the elapsed time
        self.update_timer()

    def update_timer(self):
        if self.start_time:
            # Calculate the elapsed time
            self.elapsed_time = time.time() - self.start_time
            minutes, seconds = divmod(int(self.elapsed_time), 60)
            self.timer_label.config(text=f"Time: {minutes:02}:{seconds:02}")
            
            # Update the timer every 1000 ms (1 second)
            self.timer_job = self.after(1000, self.update_timer)

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
        self.controller.virtualController.stop()  # Stop the virtual controller
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