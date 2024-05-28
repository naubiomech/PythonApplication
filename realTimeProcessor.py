import re
import exoData

class RealTimeProcessor():
    def __init__(self):
        self._event_count_regex = re.compile("[0-9]+")                          # Regular Expression to find any number 1-9
        self._start_transmission = False
        self._command = None
        self._num_count = 0
        self._buffer = []
        self._payload= []
        self._result= ''
        self._exo_data = exoData.ExoData()
        self._data_length = None
        self.x_time= 0

    def processEvent(self, event):
        dataUnpacked = event.decode('utf-8')                                    # Decode data from bytearry->String
        if 'c' in dataUnpacked:                                                 # 'c' acts as a delimiter for data
            data_split = dataUnpacked.split('c')                                # Split data into 2 messages using 'c' as divider
            event_data = data_split[1]                                          # Back half of split holds message data
            event_info = data_split[0]                                          # Front half of split holds message information
            count_match = self._event_count_regex.search(event_info).group()    # Look for data count described in data info
            self._data_length = int(count_match)
            start = event_info[0]                                               # Start of data
            cmd = event_info[1]                                                 # Command the data holds
            event_without_count = f"{start}{cmd}{event_data}"                   # Data without the count
            # Parse the data and handle each part accordingly
            for element in event_without_count:
                if element == 'S' and not self._start_transmission:             # 'S' signifies that start of the message
                    self._start_transmission = True
                    continue                                                    # Keep reading message
                elif self._start_transmission:                                  # if the message has started
                    if not self._command:
                        self._command = element                                 # if command is empty, set command to current element
                    elif element == 'n':                                        
                        self._num_count += 1                                    # Increase the num count of message
                        result = ''.join(self._buffer)                          # Join the buffer to result
                        double_parse = tryParseFloat(result)                    # Parse the result and convert to double if possible, None if not possible
                        if double_parse is None:
                            continue                                            # Keep reading message
                        else:
                            self._payload.append(double_parse / 100.0)          # Add data to payload
                            self._buffer.clear()
                            if self._num_count == self._data_length:            # If the data length is equal to the data count
                                self.processMessage(self._command, self._payload, self._data_length)
                                self._reset()                                   # Reset message variables for a new message
                            else:
                                continue                                        # Keep reading message
                    elif self._data_length != 0:
                        self._buffer.append(element)                            # Add data to buffer
                    else:
                        return
                else:
                    return
        else:
            print("Unkown command!\n")


    def set_debug_event_listener(self, on_debug_event):
        self._on_debug_event = on_debug_event

    def processGeneralData(self, payload, datalength):                          # Place general data derived from message to Exo data
        self.x_time += 1
        rightTorque = payload[0]
        rightSate = payload[1]
        rightSet = payload[2]
        leftTorque = payload[3]
        leftState = payload[4]
        leftSet = payload[5]
        rightFsr = payload [6] if datalength >= 7 else 0
        leftFsr = payload[7] if datalength >= 8 else 0

        print("left torque: ", leftTorque)

        self._exo_data.addDataPoints(self.x_time,
                                    rightTorque,
                                    rightSate,
                                    rightSet, 
                                    leftTorque, 
                                    leftState, 
                                    leftSet, 
                                    rightFsr, 
                                    leftFsr)


    def processMessage(self, command, payload, dataLength):                     # Process message based on command. Only handles general data although other data is comming through
        if command == '?':                                                      # General command
            self.processGeneralData(payload, dataLength)

    def _reset(self):                                                           # Reset message variables
        self._start_transmission = False
        self._command = None
        self._data_length = None
        self._num_count = 0
        self._payload.clear()
        self._buffer.clear()

    def UnkownDataCommand(self):
        return "Unkown Command!"
    
def tryParseFloat(stringVal):                                                   # Try to parse float data from String
    try:
        return float(stringVal)                                                 # If possible, return parsed
    except:
        return None                                                             # If not, return None