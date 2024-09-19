import tkinter as tk
from tkinter import (BOTTOM, CENTER, LEFT, RIGHT, TOP, E, N, S, IntVar, StringVar, W,
                     X, Y, ttk)

from async_tkinter_loop import async_handler

from Widgets.Charts.chart import LeftPlot, RightPlot



class BioFeedback(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.var = IntVar()
        self.chartVar = StringVar()
        self.chartVar.set("Left Leg")

        # Drop down menu for legs
        self.chartDropdown = ttk.Combobox(
            self,
            textvariable=self.chartVar,
            state="readonly",
            values=[
                "Left Leg",
                "Right Leg",
            ],
        )

        self.create_widgets()
        

        # Top label for frame
        calibrationMenuLabel = tk.Label(self, text="Biofeedback", font=("Arial", 40))
        calibrationMenuLabel.pack(side=TOP, anchor=N, pady=20)

        self.leftPlot = LeftPlot(self)
        self.rightPlot = RightPlot(self)

        # Pack only the default plot initially
        self.currentPlots = self.leftPlot
        self.currentPlots.canvas.get_tk_widget().pack(fill=None, expand=True)

        self.chartDropdown.bind("<<ComboboxSelected>>", self.newSelection)
        self.chartDropdown.pack()

        self.plot_update_job = None  # Store the job reference

    def create_widgets(self):
        backButton = tk.Button(self, text="Back", command=self.handle_back_button)
        backButton.pack(side=TOP, anchor=W, pady=10, padx=10)

    def handle_back_button(self):
        self.stop_plot_updates()
        self.controller.show_frame("ActiveTrial")
        active_trial_frame = self.controller.frames["ActiveTrial"]
        active_trial_frame.newSelection(self)

    def on_bio_feedback_button_clicked(self):
        # Show the BioFeedback frame and start plotting
        self.controller.show_frame("BioFeedback")
        bio_feedback_frame = self.controller.frames["BioFeedback"]
        bio_feedback_frame.start_plotting()  # Assuming start_plotting is defined in BioFeedback


    def newSelection(self, event=None):
        selection = self.chartVar.get()
        self.update_plots(selection)

    def update_plots(self, selection):
        
        if self.plot_update_job:
            self.after_cancel(self.plot_update_job)
        
        # Hide the current plot
        self.currentPlots.canvas.get_tk_widget().pack_forget()

        # Update the plot based on the selection
        if selection == "Left Leg":
            self.currentPlots = self.leftPlot
        elif selection == "Right Leg":
            self.currentPlots = self.rightPlot

        # Show the selected plot
        self.currentPlots.canvas.get_tk_widget().pack(fill=None, expand=True)

        # Animate the current plot
        self.currentPlots.animate(selection)

        # Schedule the next update
        self.plot_update_job = self.after(20, self.update_plots, selection)

    def stop_plot_updates(self):
        if self.plot_update_job:
            self.after_cancel(self.plot_update_job)
            self.plot_update_job = None

    def show(self):
        self.newSelection()

