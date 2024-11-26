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

        # Plot initialization
        self.line1, = self.ax.plot([], [], label='Controller Value', color='blue')
        self.line2, = self.ax.plot([], [], label='Measurement Value', color='red')

        self.ax.set_xticks([])  # Hide x-ticks for simplicity
        self.ax.set_title(title)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid()

    def animate(self):
        raise NotImplementedError("Subclasses should implement this method")

    def update_plot(self, xValues, yValues, secondY, bottomLim, topLim, title):
        max_points = 20  # Keep only the last 20 points
        if len(xValues) > max_points:
            xValues = xValues[-max_points:]
            yValues = yValues[-max_points:]
            secondY = secondY[-max_points:]
        
        # Update line data
        self.line1.set_data(xValues, yValues)
        self.line2.set_data(xValues, secondY)

        # Filter out None values from yValues and secondY
        filtered_y_values = [val for val in yValues if val is not None]
        filtered_second_y = [val for val in secondY if val is not None]

        # Combine filtered values to calculate current data range
        all_y_values = filtered_y_values + filtered_second_y

        # Check if there's valid data to compute min and max
        if all_y_values:
            current_min = min(all_y_values)
            current_max = max(all_y_values)
        else:
            current_min = 0
            current_max = 0
            
        # Check if y-axis limits need to be adjusted
        padding = 0.5  # Padding to add around limits
        if not hasattr(self, 'y_limits'):
            self.y_limits = [bottomLim, topLim]  # Initial fixed limits
            self.reset_counter = 0  # Counter to track data within the initial range
    
        # Adjust limits if data exceeds current range
        limits_updated = False
        if current_min < self.y_limits[0]:
            self.y_limits[0] = current_min - padding
            limits_updated = True
        if current_max > self.y_limits[1]:
            self.y_limits[1] = current_max + padding
            limits_updated = True

        # Reset y_limits if data is within the initial range for consecutive updates
        if not limits_updated and current_min >= -1 and current_max <= 1:
            self.reset_counter += 1
            if self.reset_counter >= 10:  # Number of consecutive updates to confirm reset
                self.y_limits = [bottomLim,topLim]
                self.reset_counter = 0
        else:
            self.reset_counter = 0  # Reset the counter if limits were updated

        # Set x-axis to match the data range and y-axis with adjusted limits
        self.ax.set_xlim([xValues[0], xValues[-1]])
        self.ax.set_ylim(self.y_limits)

        # Draw without clearing axes
        self.canvas.draw_idle()
        self.canvas.flush_events()


class TopPlot(BasePlot):
    def __init__(self, master):
        super().__init__(master, "Left Torque")
    def animate(self, chartSelection):
        topController = None
        title = " "
        bottomLimit = -1
        topLimit = 1
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
            bottomLimit = 0
            topLimit = 1.1

        if topController is None or topMeasure is None:
            topController = 0
            topMeasure = 0

        self.xValues.append(dt.datetime.now())
        self.yValues.append(topController)
        self.secondY.append(topMeasure)

        self.update_plot(self.xValues, self.yValues, self.secondY, bottomLimit,topLimit,title)


class BottomPlot(BasePlot):
    def __init__(self, master):
        super().__init__(master, "Right Torque")

    def animate(self, chartSelection):
        topController = None
        bottomLimit = -1
        topLimit = 1
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
            bottomLimit = 0
            topLimit = 1.1
            title = "Sensor"

        if topController is None or topMeasure is None:
            topController = 0
            topMeasure = 0

        self.xValues.append(dt.datetime.now())
        self.yValues.append(topController)
        self.secondY.append(topMeasure)

        self.update_plot(self.xValues, self.yValues, self.secondY, bottomLimit,topLimit,title)

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
        bottomLimit = 0
        topLimit = 1.1
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

        self.update_plot(self.xValues, self.yValues, self.secondY, bottomLimit , topLimit, title)
