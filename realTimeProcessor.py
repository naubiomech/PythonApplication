import re

class RealTimeProcessor():
    def __init__(self):
        self.event_count_regex = re.compile("[0-9]+")
        self._startTransmission = False
        self.command = ''
        self._numCount = 0
        self.buffer = []
        self._payload= []

    def processEvent(self, data: bytearray):
        dataUnpacked = data.decode('utf-8')     #Decode data from bytearry->String
        print(f"data recieved: {dataUnpacked}")
        
        if dataUnpacked.__contains__('c'):
            dataSplit = dataUnpacked.split('c')
            eventData = dataSplit[1]
            eventInfo = dataSplit[0]
            count = self.event_count_regex(eventInfo)
            dataLength = int(count)
            start = eventInfo[0]
            cmd = eventInfo[1]
            eventWithOutCount = start + cmd + eventData
            eventWithOutCountSplit = eventWithOutCount.split('')
            for char in eventWithOutCountSplit:
                if (char == 'S' and  (not self._startTranmission)):
                    self._startTransmission = True
                    return
                elif self._startTransmission:
                    if self.command == '':
                        self.command = char
                    elif char == 'n':
                        self._numCount += 1
                        result = self._buffer.join()
                        floatParse = float(result)
                        if floatParse == None:
                            return
                        else:
                            self._payload.add(floatParse / 100.0)
                            self.buffer.clear()
                            if self._numCount == dataLength:
                                if (self.command == '?'):
                                    self.processMessage(self.command, self._payload, dataLength)
                                    self.reset()
                            else:
                                return
                    elif not (dataLength == 0):
                        self.buffer.append(char)
                    else:
                        return
                else:
                    print("unknown command\n")

    def processGeneralMessage(self, payload, datalength):
        rightTorque = payload[0]
        rightSate = payload[1]
        rightSet = payload[2]
        leftTorque = payload[3]
        leftState = payload[4]
        leftSet = payload[5]
        rightFsr = payload [6] if datalength >= 7 else 0
        leftFsr = payload[7] if datalength >= 8 else 0


    def processMessage(self, command, payload, dataLength):
        if command == '?':
            self.processGeneralData(payload, dataLength)