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
        self.secondY = []

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

    def animate(self):
        raise NotImplementedError("Subclasses should implement this method")

    def update_plot(self, xValues, yValues, secondY, title):
        xValues = xValues[-20:]
        yValues = yValues[-20:]
        secondY = secondY[-20:]

        self.ax.clear()
        self.ax.plot(xValues, yValues)
        self.ax.plot(xValues, secondY)
        self.ax.set_ylim(auto=True)
        self.ax.set_xticks([])
        self.ax.set_title(title)
        
        self.canvas.draw()


class TopPlot(BasePlot):
    def __init__(self, master):
        super().__init__(master, "Left Torque")

    def animate(self, chartSelection):
        topController = None
        title = " "
        if chartSelection == "Controller":
            topController = (
                self.master.controller.deviceManager._realTimeProcessor._chart_data.leftTorque
            )
            topMeasure = (
                self.master.controller.deviceManager._realTimeProcessor._chart_data.leftSet
            )
            title = "Controller"
        elif chartSelection == "Sensor":
            topController = (
                self.master.controller.deviceManager._realTimeProcessor._chart_data.leftState
            )
            topMeasure = (
                self.master.controller.deviceManager._realTimeProcessor._chart_data.leftFsr
            )
            title = "Sensor"
        if topController is None or topMeasure is None:
            topController = 0
            topMeasure = 0

        self.xValues.append(dt.datetime.now())
        self.yValues.append(topController)
        self.secondY.append(topMeasure)

        self.update_plot(self.xValues, self.yValues, self.secondY, title)


class BottomPlot(BasePlot):
    def __init__(self, master):
        super().__init__(master, "Right Torque")

    def animate(self, chartSelection):
        topController = None
        title = " "
        if chartSelection == "Controller":
            topController = (
                self.master.controller.deviceManager._realTimeProcessor._chart_data.rightTorque
            )
            topMeasure = (
                self.master.controller.deviceManager._realTimeProcessor._chart_data.rightSet
            )
            title = "Controller"
        elif chartSelection == "Sensor":
            topController = (
                self.master.controller.deviceManager._realTimeProcessor._chart_data.rightState
            )
            topMeasure = (
                self.master.controller.deviceManager._realTimeProcessor._chart_data.rightFsr
            )
            title = "Sensor"

        if topController is None or topMeasure is None:
            topController = 0
            topMeasure = 0

        self.xValues.append(dt.datetime.now())
        self.yValues.append(topController)
        self.secondY.append(topMeasure)

        self.update_plot(self.xValues, self.yValues, self.secondY, title)

class FSRPlot(BasePlot):
    def __init__(self, master, goal=None):
        super().__init__(master, "Left FSR")
        self.goal = None  # Store the goal value
        self.counter_above_goal = 0  # Initialize the counter
        self.above_goal = False  # Track if currently above the goal

        # Initialize plot lines for FSR and target
        self.line_fsr, = self.ax.plot([], [], label='FSR Value', color='blue')
        self.line_target, = self.ax.plot([], [], label='Target Value', color='red', linestyle='--')

    def set_goal(self, goal):
        self.goal = goal  # Set the new goal

    def animate(self, chartSelection):
        topMeasure  = None

        title = " "
        if chartSelection == "Left Leg":
            topMeasure = (
                self.master.controller.deviceManager._realTimeProcessor._chart_data.leftFsr
            )
            title = "Left Leg"
        elif chartSelection == "Right Leg":
            topMeasure = (
                self.master.controller.deviceManager._realTimeProcessor._chart_data.rightFsr
            )
            title = "Right Leg"

        if topMeasure is None:
            topMeasure = 0

        self.xValues.append(dt.datetime.now())
        self.yValues.append(self.goal)
        self.secondY.append(topMeasure)

        # Check if topMeasure crosses the goal
        if self.goal is not None:
            if topMeasure > self.goal and not self.above_goal:
                self.counter_above_goal += 1  # Increment the counter
                self.above_goal = True  # Set the flag to true
                self.master.update_counter_label()  # Notify BioFeedback to update counter
            elif topMeasure <= self.goal:
                self.above_goal = False  # Reset the flag when it goes below or equal to the goal

        self.update_plot(self.xValues, self.yValues, self.secondY, title)

class AssistanceAnimator(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master

        # set number to be the assistace level held by the master
        # display the number with only 2 decimal places and as a label
        self.label = tk.Label(master, text=str(self.master.getAssistanceLevel()), font=("Arial", 24))
        self.label.pack(pady=20)

        self.animate_number()  # Start the update loop

    def animate_number(self):
        self.label.config(text=str(self.master.getAssistanceLevel()))  # Update the label text
        self.master.after(100, self.animate_number)  # Call the function every 1000 ms (1 sec)