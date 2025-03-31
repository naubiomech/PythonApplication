import tkinter as tk
from tkinter import (BOTH, BOTTOM, CENTER, DISABLED, LEFT, RIGHT, TOP, E, IntVar, N, W,
                     StringVar, X, Y, PhotoImage, ttk)
from async_tkinter_loop import async_handler
import subprocess
import os
import asyncio
from Widgets.Charts.chart import AssistanceAnimator, BottomPlot, TopPlot
from views import gameSelectMenu 


# Active Trial Frame
class ActiveTrial(tk.Frame):
    # Constructor for frame
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.var = IntVar()
        self.chartVar = StringVar()
        self.chartVar.set("Controller")

        self.selectGameButton = None
        self.launchGameButton = None
        self.stopGameButton = None
        self.selected_game = None
        self.game_process = None
        self.sensor_var = tk.StringVar()
        self.sensor_var.set("Left & Right")  # Default selection

        self.chartDropdown = ttk.Combobox(
            self,
            textvariable=self.chartVar,
            state="readonly",
            values=[
                "Controller",
                "Sensor",
            ],
        )

        self.sensorChartDropdown = ttk.Combobox(
            self,
            textvariable=self.sensor_var,
            state="ENABLED",
            values=[
                "Left",
                "Right",
                "Left & Right",
            ],
        )

        # Set window size
        self.controller.geometry("920x820")

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

        self.create_game_widgets()

        self.chartDropdown.bind("<<ComboboxSelected>>", self.newSelection)
        self.chartDropdown.pack(pady=5, padx=5)

        self.sensorChartDropdown.bind("<<ComboboxSelected>>", self.on_sensor_selection)
        # Pack the sensor chart dropdown
        self.sensorChartDropdown.set("Left & Right")  # Set default value
        # Pack the sensor chart dropdown
        self.sensorChartDropdown.pack(pady=5, padx=5)

        self.currentPlots = [self.topPlot, self.bottomPlot]
        self.plot_update_job = None  # Store the job reference

        self.create_widgets()


    # Frame Game UI elements
    def create_game_widgets(self):
        # Create a new frame for the Game section
        game_frame = tk.Frame(self)
        game_frame.pack(side=BOTTOM, pady=7)  # Pack the button frame at the bottom

        # create a divider between the different frames 
        divider = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
        divider.pack(side=BOTTOM, fill=tk.X, padx=5, pady=5)

        # Game Label
        gameLabel = tk.Label(game_frame, text="Game Controls", font=("Arial", 20))
        gameLabel.pack(side=TOP, anchor=N, pady=6)

        # Select Game Button
        self.selectGameButton = tk.Button(
            game_frame,
            text="Select Game",
            height=2,
            width=20,
            command=async_handler(self.selectGame),
        )
        self.selectGameButton.pack(side=LEFT, padx=7)  # Pack the button to the left

        # Stop Game Button
        self.stopGameButton = tk.Button(
            game_frame,
            text="Stop Game",
            height=2,
            width=20,
            command=self.stop_game,
            state=DISABLED,
        )
        self.stopGameButton.pack(side=LEFT, padx=7)  # Pack the button to the left
        # Launch Game Button
        self.launchGameButton = tk.Button(
            game_frame,
            text="Launch Game",
            height=2,
            width=20,
            command=self.launch_game,
            state=DISABLED,
        )
        self.launchGameButton.pack(side=LEFT, padx=7)  # Pack the button to the left

        # add a pad between the buttons
        pad = tk.Label(game_frame, text=" ", font=("Arial", 20))
        pad.pack(side=LEFT, anchor=N, padx=35)

        # Show the amount of assistance
        self.assistanceNumber = AssistanceAnimator(self)

        # TextBox Creation 
        self.assistanceText = tk.Text(game_frame, 
                height = 1, 
                width = 10) 
        
        self.assistanceText.pack(side=RIGHT, padx=3) 
        self.assistanceText.insert("1.0", "1.0")  # Insert default text

        # Create a button that then sets the assistance level to the value input into the assistanceText
        self.setAssistanceButton = tk.Button(
            game_frame,
            text="Set Target",
            height=2,
            width=10,
            command=self.setAssistanceButtonClicked
        )
        self.setAssistanceButton.pack(side=RIGHT, padx=3)

        # Remove Assistance Button
        removeAssistanceGameButton = tk.Button(
            game_frame,
            text="-",
            font=("Arial", 10),
            height=2,
            width=5,
            command=self.remove_assistance
        )
        removeAssistanceGameButton.pack(side=RIGHT, padx=3)

        # Add Assistance Button
        addAssistanceGameButton = tk.Button(
            game_frame,
            text="+",
            font=("Arial", 10),
            height=2,
            width=5,
            command=self.add_assistance
        )
        addAssistanceGameButton.pack(side=RIGHT, padx=3) 


        

    # Frame UI elements
    def create_widgets(self):
        # Update torque button
        button_frame = tk.Frame(self)
        button_frame.pack(side=BOTTOM, pady=7)  # Pack the button frame at the bottom

        updateTorqueButton = tk.Button(
            self,
            text="Update Controller",
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
        endTrialButton.pack(side=LEFT, padx=7)  # Pack the button to the left

        

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
        self.controller.virtualController.stop()
        # Create a virtual controller
        self.controller.virtualController.create()  # Start the virtual controller
        
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


    async def selectGame(self):
        # start the game selection process
        await gameSelectMenu.select_game(self)
        # wait for the game selection to be made aka the selected_game variable to be set
        while not self.selected_game:
            await asyncio.sleep(0.1)
        
        # After a selection is made, the launch game button will be enabled
        self.launchGameButton.config(state="normal")
        print(f"Selected game: {self.selected_game}")


    async def select_game(self):
        """Select a game to play."""
        # Create a new window
        game_window = tk.Toplevel(self)
        game_window.title("Select a Game")
        game_window.geometry("300x200")

        #create a canvas
        canvas = tk.Canvas(game_window, width=300, height=200)
        
        # create a frame
        frame = tk.Frame(canvas)
        vsb = tk.Scrollbar(game_window, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((4,4), window=frame, anchor="nw")


        # Create a label
        game_label = tk.Label(game_window, text="Select a Game", font=("Arial", 20))
        game_label.pack(side=TOP, anchor=N, pady=10)

        # Scan for each game from within the Games folder
        games_folder = os.path.join(os.getcwd(), "Games")
        games = [f for f in os.listdir(games_folder)]

        def select_and_close(game):
            self.selected_game = game
            game_window.destroy()
            self.launchGameButton.config(state="normal")

        for game in games:
            game_button = tk.Button(
                game_window,
                text=game,
                command=lambda g=game: select_and_close(g)
            )
            game_button.pack(pady=5)

        # Create a button to save the selected game
        exit_button = tk.Button(
            game_window,
            text="Exit",
            command=game_window.destroy
        )
        exit_button.pack(pady=10)


    def stop_game(self):
        """Stop the game process."""
        
        if (self.game_process):
            self.game_process.kill()
            self.game_process = None
            self.stopGameButton.config(state="disabled")
            self.launchGameButton.config(state="normal")
            self.selectGameButton.config(state="normal")

        print("Game stopped")

    def add_assistance(self):
        # When called, the goals will be EASIER to reach by the user
        print("Adding assistance")
        self.controller.virtualController.addAssistance()

    def remove_assistance(self):
        # When called, the goals will be HARDER to reach by the user
        print("Removing assistance")
        self.controller.virtualController.removeAssistance()

    def set_assistance(self, level):
        # Update the assistance level based on the slider
        self.controller.virtualController.setAssistanceLevel(level)

    def getAssistanceLevel(self):
        return self.controller.virtualController.getAssistanceLevel()
    
    def setAssistanceButtonClicked(self):
        # Update the assistance level based on the text box
        level = self.assistanceText.get("1.0", "end-1c")
        self.controller.virtualController.setAssistanceLevel(float(level))




    

    def handle_BioFeedbackButton_button(self):
        self.controller.show_frame("BioFeedback")
        bioFeedback_frame = self.controller.frames["BioFeedback"]
        bioFeedback_frame.newSelection(self)

    def handle_MachineLearning_button(self):
        self.controller.show_frame("MachineLearning")
        machineLearning_frame = self.controller.frames["MachineLearning"]
        machineLearning_frame.newSelection(self)

    def newSelection(self, event=None):
        # Disable buttons and dropdown until process complete
        self.disable_interactions()

        # Determine which plots to show
        selection = self.chartVar.get()
        self.update_plots(selection)
    
    def on_sensor_selection(self, event=None):
        # Get the selected sensor from the dropdown
        selected_sensor = self.sensor_var.get()

        # Update the virtual controller with the selected sensor
        self.controller.virtualController.setSensor(selected_sensor)



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
