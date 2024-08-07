import datetime as dt
import tkinter as tk
from tkinter import CENTER

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from async_tkinter_loop import async_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Active Trial Frame
class ActiveTrial(tk.Frame):
    # Constructor for frame
    def __init__(self, parent, controller):
        super().__init__(parent)
        # Controller object to switch frames
        self.controller = controller

        self.create_widgets()

    # Frame UI elements
    def create_widgets(self):
        # Active Trial title label
        calibrationMenuLabel = tk.Label(
            self, text="Active Trial", font=("Arial", 40))
        calibrationMenuLabel.place(relx=0.5, rely=0.1, anchor=CENTER)

        # Update torque button
        updateTorqueButton = tk.Button(
            self,
            text="Update Torque",
            command=lambda: self.controller.show_frame("UpdateTorque"),
        )
        updateTorqueButton.place(relx=0.75, rely=0.35)

        # End Trial Button
        endTrialButton = tk.Button(
            self,
            text="End Trial",
            command=async_handler(self.on_end_trial_button_clicked),
        )
        endTrialButton.place(relx=0.75, rely=0.8)

    def initialize_plot(self):
        # plotter ########################################################
        fig = plt.Figure()
        self.ax = fig.add_subplot(1, 1, 1)
        self.xValues = []
        self.yValues = []

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().place(relx=0.25, rely=0.5, anchor=CENTER)

        self.ani = animation.FuncAnimation(
            fig, self.animate, fargs=(
                self.xValues, self.yValues), interval=200
        )

    def animate(self, i, xValues, yValues):
        rightTorque = (
            self.controller.deviceManager._realTimeProcessor._chart_data.rightTorque
        )

        xValues.append(dt.datetime.now().strftime("%M:%S"))
        yValues.append(rightTorque)

        # Limit values to 20 items
        xValues = xValues[-20:]
        yValues = yValues[-20:]

        self.ax.clear()
        self.ax.plot(xValues, yValues)

        self.ax.set_title("Right Torque")

    def show(self):
        self.initialize_plot()

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
