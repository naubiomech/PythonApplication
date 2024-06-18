import asyncio
from tkinter import *
import tkinter as tk
from tkinter import ttk
from Device import exoDeviceManager

deviceManager = exoDeviceManager.ExoDeviceManager()

async def startScan():
    await deviceManager.scanAndConnect()

#----------------------------------------------------------------------------------------------
class ScanWindow(tk.Frame):
    def __init__(self, window=None):
        super().__init__(window)
        self.window = window
        self.deviceNameText = StringVar()

        # creates page for class
        self.create_widgets()

    def create_widgets(self):
        # Title label
        titleLabel = tk.Label(self.window, 
                              text="ExoSkeleton Controller", 
                              font=("Arial", 40))
        titleLabel.place(relx=.5, 
                         rely=.1, 
                         anchor=CENTER)
        # Start Scan label
        startScanLabel = tk.Label(self.window, 
                                  text="Begin Scanning for Exoskeletons")
        startScanLabel.place(relx=.5, 
                             rely=.35, 
                             anchor=CENTER)

        # Start Scan button
        startScanButton = tk.Button(self.window, 
                                    text="Start Scan", 
                                    command=self.on_start_scan_button_clicked)
        startScanButton.place(relx=.5, 
                              rely=.45, 
                              anchor=CENTER)

        self.deviceNameText.set("Not Connected")
        deviceNameLabel = tk.Label(self.window,
                                   textvariable = self.deviceNameText)
        deviceNameLabel.place(relx = .5,
                              rely = .60,
                              anchor = CENTER)

    def on_start_scan_button_clicked(self):
        self.deviceNameText.set("Scanning...")
        asyncio.create_task(self.startScanButtonClicked())

    async def startScanButtonClicked(self):
        await startScan()
        asyncio.sleep(5)
        self.deviceNameText.set(deviceManager.device)

    async def onConnectButtonClicked(self):
        print(self.foundDeviceList['values'])
        await deviceManager.connect(self.foundDeviceList['values'])
#----------------------------------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()

    # Window settings
    root.title("NAU Biomechatronics Lab")
    root.geometry("724x420")

    # Create and place the ScanWindow frame
    app = ScanWindow(root)

    # Integrate the asyncio event loop with Tkinter's event loop
    async def main():
        while True:
            root.update()
            await asyncio.sleep(0.01)

    asyncio.run(main())
