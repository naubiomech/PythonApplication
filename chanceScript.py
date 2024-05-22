import asyncio
import sys
import struct
from itertools import count, takewhile
from typing import Iterator
import time

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

UART_TX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e" #Nordic NUS characteristic for TX
UART_RX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e" #Nordic NUS characteristic for RX
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
ADV_CTRL_SERVICE_UUID = "ad788dbb-0055-4623-b92f-e2f0d3189767"
ADV_CTRL_ID_CHAR_UUID = "ad788dbb-0055-4623-b92f-e2f0d3189768"
ADV_CTRL_PARAM_CHAR_UUID = "ad788dbb-0055-4623-b92f-e2f0d3189769"
ADV_CTRL_NODE_CHAR_UUID = "ad788dbb-0055-4623-b92f-e2f0d3189770"
ADV_CTRL_NODE_COUNT_CHAR_UUID = "ad788dbb-0055-4623-b92f-e2f0d3189771"

def match_spark(device: BLEDevice, adv: AdvertisementData):
    # This assumes that the device includes the Advanced control service in the
    # advertising data. This test may need to be adjusted depending on the
    # actual advertising data supplied by the device.
    if UART_SERVICE_UUID.lower() in adv.service_uuids:
        return True

    return False

def handle_disconnect(_: BleakClient):
    print("Device was disconnected, goodbye.")
    # cancelling all tasks effectively ends the program
    for task in asyncio.all_tasks():
        task.cancel()

async def scan_and_connect():
    device = await BleakScanner.find_device_by_filter(match_spark)
    print(device)
    if device is None:
        print("No matching device found, you may need to edit the filter.")
        sys.exit(1)
    client = BleakClient(device, disconnected_callback=handle_disconnect)
    await client.connect()
    services = await client.get_services()
    return device, client, services

def get_char_handle(client, char_UUID):
    return client.services.get_service(ADV_CTRL_SERVICE_UUID).get_characteristic(char_UUID)


async def update_ctrl_id(client, is_left, id):
    char = get_char_handle(client, ADV_CTRL_ID_CHAR_UUID) 
    data = struct.pack('{}B'.format(2), *([is_left, id]))
    await client.write_gatt_char(char, data, response=False)

async def update_param(client, is_left, index, value):
    char = get_char_handle(client, ADV_CTRL_PARAM_CHAR_UUID) 
    data = struct.pack('{}B'.format(2), *([is_left, index])) + struct.pack('f', value)
    await client.write_gatt_char(char, data, response=False)

async def update_node(client, is_left, index, xval, yval):
    char = get_char_handle(client, ADV_CTRL_NODE_CHAR_UUID) 
    data = struct.pack('{}B'.format(2), *([is_left, index])) + struct.pack('ff', xval, yval)
    await client.write_gatt_char(char, data, response=False)

async def update_node_count(client, is_left, count):
    char = get_char_handle(client, ADV_CTRL_NODE_COUNT_CHAR_UUID) 
    data = struct.pack('{}B'.format(2), *([is_left, count]))
    await client.write_gatt_char(char, data, response=False)

async def update_torque_values(client, values):
    data = bytearray(b'F')

    await client.write_gatt_char(UART_TX_UUID, data)
    await asyncio.sleep(0.1)

    for torque in values:
        data = struct.pack('<d',torque) # Needs to be updated to match whatever the Arduino expects
        await client.write_gatt_char(UART_TX_UUID, data)
        await asyncio.sleep(0.1)

async def main():
    sleep_between_messages = 0.1
    device, client, services = await scan_and_connect()
    # # Set the controller for both legs (Defined in ControllerID.h)
    controller = 2 # (0 = None (PJMC), 1 = ZhangCollins, 2 = Generic Spline)
    await update_ctrl_id(client, True, controller) # Left controller 
    time.sleep(sleep_between_messages)
    await update_ctrl_id(client, False, controller) # Right controller 
    time.sleep(sleep_between_messages)

    if controller == 2:
        # Generic Spline controller
        # Set the parameters (# of Interpolation points, Interpolation Method (0 = Smoothstep, 1 = Linear, 2 = Cubic Spline))
        parameter_list = [100, 0]  # (defined in ControllerParameters.h)
        for index, val in enumerate(parameter_list):
            await update_param(client, True, index, val) # Left
            time.sleep(sleep_between_messages)
            await update_param(client, False, index, val) # Right
            time.sleep(sleep_between_messages)

        nodes_x = [15, 20, 40, 45]
        nodes_y = [0, 12, 21, 0]
        assert(len(nodes_x) == len(nodes_y))
        nodes = zip(nodes_x, nodes_y)

        # Set the node count
        await update_node_count(client, True, len(nodes_x))
        time.sleep(sleep_between_messages)
        await update_node_count(client, False, len(nodes_x))
        time.sleep(sleep_between_messages)

        # Set the nodes
        for i, (x, y) in enumerate(nodes):
            await update_node(client, True, i, x, y)
            time.sleep(sleep_between_messages)
            await update_node(client, False, i, x, y)

    elif controller == 1:
        # Zhang Collins controller
        # Set the default parameters (Torque Magnitude, Peak time, rise time, fall time, direction flip (default is PF))
        parameter_list = [10, 30, 10, 5, 0] 
        for index, value in enumerate(parameter_list):
            await update_param(client, True, index, value)
            time.sleep(sleep_between_messages)
            await update_param(client, False, index, value)
            time.sleep(sleep_between_messages)


if __name__ == "__main__":
    asyncio.run(main())