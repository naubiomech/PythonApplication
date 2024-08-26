import datetime as dt
import tkinter as tk
from tkinter import BOTTOM, CENTER, LEFT, RIGHT, TOP, E, IntVar, X, Y

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from async_tkinter_loop import async_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Widgets.Charts.chart import (LeftStatePlot, LeftTorquePlot,
                                  RightStatePlot, RightTorquePlot)


# Active Trial Frame
class ActiveTrial(tk.Frame):
    # Constructor for frame
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.var = IntVar()
        self.rightTorquePlot = RightTorquePlot(self)
        self.leftTorquePlot = LeftTorquePlot(self)
        #self.rightStatePlot = RightStatePlot(self)
        #self.leftStatePlot = LeftStatePlot(self)

        self.create_widgets()

    # Frame UI elements
    def create_widgets(self):
        # Active Trial title label
        calibrationMenuLabel = tk.Label(self, text="Active Trial", font=("Arial", 40))
        calibrationMenuLabel.pack(side=TOP, pady=20)

        # Update torque button
        updateTorqueButton = tk.Button(
            self,
            text="Update Torque",
            height=2,
            width=10,
            command=lambda: self.controller.show_frame("UpdateTorque"),
        )
        updateTorqueButton.pack(side=LEFT)

        # Radio Button chart selector
        torqueRadioButton = tk.Radiobutton(
            self, text="Torque", variable=self.var, value=1, command=self.selectChart
        )
        torqueRadioButton.pack(side=LEFT)
        stateRadioButton = tk.Radiobutton(
            self, text="State", variable=self.var, value=2, command=self.selectChart
        )
        stateRadioButton.pack(side=LEFT)

        # End Trial Buttuu
        endTrialButton = tk.Button(
            self,
            text="End Trial",
            height=2,
            width=10,
            command=async_handler(self.on_end_trial_button_clicked),
        )
        endTrialButton.pack(side=BOTTOM, anchor=E, pady=7, padx=7)

    def selectChart(self):
        selection = self.var.get()

    #    if selection == 1:
    #
    #    elif selection == 2:
    #         self.leftTorquePlot

    def initialize_left_torque_plot(self):
        fig = plt.Figure()
        self.ax = fig.add_subplot(1, 1, 1)
        self.xValues = []
        self.yValues = []

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        self.ani = animation.FuncAnimation(
            fig,
            self.animateLeftTorque,
            fargs=(self.xValues, self.yValues),
            interval=200,
        )

    def initialize_right_torque_plot(self):
        # plotter ########################################################
        fig = plt.Figure()
        self.ax = fig.add_subplot(1, 1, 1)
        self.xValues = []
        self.yValues = []

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
        self.ani = animation.FuncAnimation(
            fig,
            self.animateRightTorque,
            fargs=(self.xValues, self.yValues),
            interval=200,
        )

    def animateLeftTorque(self, i, xValues, yValues):
        leftTorque = (
            self.controller.deviceManager._realTimeProcessor._chart_data.leftTorque
        )

        xValues.append(dt.datetime.now().strftime("%M:%S"))
        yValues.append(leftTorque)

        # Limit values to 20 items
        xValues = xValues[-20:]
        yValues = yValues[-20:]

        self.ax.clear()
        self.ax.plot(xValues, yValues)

        self.ax.set_title("Left Torque")

    def animateRightTorque(self, i, xValues, yValues):
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

    # def show(self):
    # LeftTorquePlot(self, (0.30, 0.75))
    # RightTorquePlot(self, (0.30, 0.75))
    # self.initialize_right_torque_plot()
    # self.initialize_left_torque_plot()

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
