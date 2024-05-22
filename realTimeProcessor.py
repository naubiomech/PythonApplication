import re
import exoData

class RealTimeProcessor():
    def __init__(self):
        self.rawRegexString = r'0-9'
        self._event_count_regex = re.compile("[0-9]+")
        self._start_transmission = False
        self._command = None
        self._num_count = 0
        self._buffer = []
        self._payload= []
        self._result= ''
        self._exo_data = exoData.ExoData()
        self._data_length = None
        self.x_time= 0

    # def processEvent(self, data: bytearray):
    #     dataUnpacked = data.decode('utf-8')     #Decode data from bytearry->String
    #     print(f"data recieved: {dataUnpacked}")
        
    #     if dataUnpacked.__contains__('c'):
    #         dataSplit = dataUnpacked.split('c')
    #         eventData = dataSplit[1]
    #         eventInfo = dataSplit[0]
    #         count = self.event_count_regex.findall(eventInfo)
    #         print(count)
    #         for element in count:
    #             self.dataLength = int(element)
    #         start = eventInfo[0]
    #         cmd = eventInfo[1]
    #         eventWithOutCount = start + cmd + eventData
    #         for char in eventWithOutCount:
    #             if (char == 'S' and  not self._startTransmission):
    #                 self._startTransmission = True
    #                 return
    #             elif self._startTransmission:
    #                 if self.command == '':
    #                     self.command = char
    #                 elif char == 'n':
    #                     self._numCount += 1
    #                     self.result = self.result.join(self.buffer)
    #                     floatParse = float(self.result)
    #                     if floatParse == None:
    #                         return
    #                     else:
    #                         self._payload.add(floatParse / 100.0)
    #                         self.buffer.clear()
    #                         if self._numCount == self.dataLength:
    #                             self.processMessage(self.command, self._payload, self.dataLength)
    #                             self.reset()
    #                         else:
    #                             return
    #                 elif not (self.dataLength == 0):
    #                     self.buffer.append(char)
    #                 else:
    #                     return
    #             else:
    #                 print("unknown command\n")
    def processEvent(self, event):
        dataUnpacked = event.decode('utf-8')     #Decode data from bytearry->String
        if 'c' in dataUnpacked:
            data_split = dataUnpacked.split('c')
            event_data = data_split[1]
            event_info = data_split[0]
            count_match = self._event_count_regex.search(event_info).group()
            self._data_length = int(count_match)
            start = event_info[0]
            cmd = event_info[1]
            event_without_count = f"{start}{cmd}{event_data}"
            for element in event_without_count:
                if element == 'S' and not self._start_transmission:
                    self._start_transmission = True
                    continue
                elif self._start_transmission:
                    if not self._command:
                        self._command = element
                    elif element == 'n':
                        self._num_count += 1
                        result = ''.join(self._buffer)
                        double_parse = tryParseFloat(result)
                        if double_parse is None:
                            continue
                        else:
                            print("here\n")
                            self._payload.append(double_parse / 100.0)
                            self._buffer.clear()
                            if self._num_count == self._data_length:
                                self.processMessage(self._command, self._payload, self._data_length)
                                self._reset()
                            else:
                                continue
                    elif self._data_length != 0:
                        self._buffer.append(element)
                    else:
                        return
                else:
                    return
        else:
            print("Unkown command!\n")


    def set_debug_event_listener(self, on_debug_event):
        self._on_debug_event = on_debug_event

    def processGeneralData(self, payload, datalength):
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


    def processMessage(self, command, payload, dataLength):
        if command == '?':
            print(command)
            self.processGeneralData(payload, dataLength)

    def _reset(self):
        self._start_transmission = False
        self._command = None
        self._data_length = None
        self._num_count = 0
        self._payload.clear()
        self._buffer.clear()

    def UnkownDataCommand(self):
        return "Unkown Command!"
    
def tryParseFloat(stringVal):
    try:
        return float(stringVal)
    except:
        return None