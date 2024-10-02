# OpenPythonAPI
## Overview

This program can be ran via any computer/terminal with python 3.12 installed. Libraries needed can be installed via pip (python's module manager)

Open source Application utilizing the OpenExo API to search, connect to, and controll NAU Biomecatronics Lab's OpenExo systems.

This project uses the MIT License.

The purpose of this project is to provide an open source solution for controlling the OpenExo system that is accessible to anyone and free to modify for their needs.

## Libraries Needed

BLE (Bluetooth Low Energy) is the heart of this project which provides a connection from this API to the exoskeletons. Bleak, a python library is used to handle all BLE operations. To find out more about Bleak click [here](https://bleak.readthedocs.io/en/latest/).

Other libraries that are required include:
 - matplotlib
 - async_tkinter_loop
 - pygame
and others

To install all of the libraries for this program simply run pip install <library name here> 

## Operation of API
### Program control flow
<img src="./prgramflow.png">
This program when starting up creates a window with tkinter. To start scanning for exo-skeletons make sure Bluetooth is enabled on your computer or device. If Bluetooth is not enabled, the program will throw an OS error.

To start the program run the command in any terminal `python3 GUI.py` which is where main() is found and will initialize the windows and frames of the program.

## Video Example



https://github.com/user-attachments/assets/6269629e-252b-4e77-b327-0914770ae9e3

