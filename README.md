# OpenPythonAPI
## overwiew
Open source API  writen in Python for controlling the Lab's new exo system.

This Project uses the MIT License.

The Purpose of this project is to provide an open source solution for controlling The Biomechatronics Lab's new version of robotic exoskeltons.

## Technical Solutions

BLE (Bluetooth Low Energy) is the heart of this project which provides a connection from this API to the exoskeletons. Bleak, a python library is used to handle all BLE operations. To find out more about Bleak click [here](https://bleak.readthedocs.io/en/latest/).

## Operation of API
This program runs in the command line with the system's keyboard as the input. Ensure Bluetooth is turned on before running the program.

*Start Scan*  will begin a scan of all bluetooth devices that match the exoskeleton's UUID.

Once a trial has begun, program operates under a loop with the option to update torque or end trial. The loop will continue until end trial is selected. Ending a trial generates a csv in the folder where the API is running named with the data and time containing all the exoskeleton data collected during the trial.