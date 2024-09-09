import datetime as dt
import tkinter as tk

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class BasePlot:
    def __init__(self, master, title):
        self.master = master
        self.title = title
        self.figure = plt.Figure(figsize=(7, 2.5))
        self.ax = self.figure.add_subplot(1, 1, 1)
        self.xValues = []
        self.yValues = []

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

    def animate(self):
        raise NotImplementedError("Subclasses should implement this method")

    def update_plot(self, xValues, yValues, title):
        xValues = xValues[-20:]
        yValues = yValues[-20:]

        self.ax.clear()
        self.ax.plot(xValues, yValues)
        self.ax.set_ylim(auto=True)
        self.ax.set_xticks([])

        self.ax.set_title(title)

        self.canvas.draw()


class TopPlot(BasePlot):
    def __init__(self, master):
        super().__init__(master, "Left Torque")

    def animate(self, chartSelection):
        match chartSelection:
            case "Torque":
                leftTorque = (
                    self.master.controller.deviceManager._realTimeProcessor._chart_data.leftTorque
                )
                self.xValues.append(dt.datetime.now())
                self.yValues.append(leftTorque)
                self.update_plot(self.xValues, self.yValues, "Left Torque")

            case "State":
                leftState = (
                    self.master.controller.deviceManager._realTimeProcessor._chart_data.leftState
                )
                self.xValues.append(dt.datetime.now())
                self.yValues.append(leftState)
                self.update_plot(self.xValues, self.yValues, "Left State")


class BottomPlot(BasePlot):
    def __init__(self, master):
        super().__init__(master, "Right Torque")

    def animate(self, chartSelection):
        match chartSelection:
            case "Torque":
                rightTorque = (
                    self.master.controller.deviceManager._realTimeProcessor._chart_data.rightTorque
                )
                self.xValues.append(dt.datetime.now())
                self.yValues.append(rightTorque)
                self.update_plot(self.xValues, self.yValues, "Right Torque")
            case "State":
                rightState = (
                    self.master.controller.deviceManager._realTimeProcessor._chart_data.rightState
                )
                self.xValues.append(dt.datetime.now())
                self.yValues.append(rightState)
                self.update_plot(self.xValues, self.yValues, "Right State")
