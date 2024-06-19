import asyncio
import threading
from tkinter import *
import tkinter as tk
from tkinter import ttk
from Device import exoDeviceManager

deviceManager = exoDeviceManager.ExoDeviceManager()

async def startScan():
    await deviceManager.scanAndConnect()
#---------------------------------------------------------------------------------------------------------------

class ControllerApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (ScanWindow, Calibrate):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("ScanWindow")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
#---------------------------------------------------------------------------------------------------------------

class ScanWindow(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.deviceNameText = StringVar()
        self.startTrialButton = None

        # creates page for class
        self.create_widgets()

    def create_widgets(self):
        # Title label
        titleLabel = tk.Label(self, text="ExoSkeleton Controller", font=("Arial", 40))
        titleLabel.place(relx=.5, rely=.1, anchor=CENTER)
        # Start Scan label
        startScanLabel = tk.Label(self, text="Begin Scanning for Exoskeletons")
        startScanLabel.place(relx=.5, rely=.35, anchor=CENTER)

        # Start Scan button
        startScanButton = tk.Button(self, text="Start Scan", command=self.on_start_scan_button_clicked)
        startScanButton.place(relx=.5, rely=.45, anchor=CENTER)

        self.deviceNameText.set("Not Connected")
        deviceNameLabel = tk.Label(self, textvariable=self.deviceNameText)
        deviceNameLabel.place(relx=.5, rely=.60, anchor=CENTER)

        self.startTrialButton = tk.Button(self, text="Start Trial", command=lambda: self.controller.show_frame("Calibrate"),
                                     state=DISABLED)
        self.startTrialButton.place(relx=.75, rely=.8,)

    def on_start_scan_button_clicked(self):
        self.deviceNameText.set("Scanning...")
        asyncio.run_coroutine_threadsafe(self.startScanButtonClicked(), asyncio.get_event_loop())

    async def startScanButtonClicked(self):
        await startScan()
        await asyncio.sleep(3)
        self.deviceNameText.set(deviceManager.device)
        self.startTrialButton.config(state="normal") 
#---------------------------------------------------------------------------------------------------------------

class Calibrate(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        backButton = tk.Button(self, text="Back", command= lambda: self.controller.show_frame("ScanWindow"))
        backButton.place(relx=.05, rely=.05)

        calibrationMenuLabel = tk.Label(self, text="Calibration Menu", font=(Arial, 40))
#---------------------------------------------------------------------------------------------------------------

def run_app():
    root = ControllerApp()
    root.title("NAU Biomechatronics Lab")
    root.geometry("724x420")

    loop = asyncio.get_event_loop()
    asyncio_thread = threading.Thread(target=loop.run_forever)
    asyncio_thread.start()

    root.mainloop()
    loop.call_soon_threadsafe(loop.stop)
    asyncio_thread.join()

#---------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    run_app()
# import asynci
