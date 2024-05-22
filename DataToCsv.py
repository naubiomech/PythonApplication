import csv
from _datetime import datetime

class CsvWritter():
    def writeToCsv(self, exoData):
        # initialize array for output file
        fileData = []
        # establish field arrays for output file
        tStep = ['TStep']
        rTorque = ['RTorque']
        rSetP = ['RSetP']
        rState = ['RState']
        lTorque = ['LTorque']
        lSetP = ['LSetP']
        LState = ['LState']
        lFsr = ['LFsr']
        rFsr = ['RFsr']

        # append data to field array
        for xt in exoData.tStep:
            tStep.append(xt)
        for rT in exoData.rTorque:
            rTorque.append(rT)
        for rSP in exoData.rSetP:
            rSetP.append(rSP)
        for rS in exoData.rState:
            rState.append(rS)
        for lT in exoData.lTorque:
            lTorque.append(lT)
        for lSP in exoData.lSetP:
            lSetP.append(lSP)
        for lS in exoData.lState:
            LState.append(lS)
        for rF in exoData.rFsr:
            rFsr.append(rF)
        for lF in exoData.lFsr:
            lFsr.append(lF)
        for tS in exoData.tStep:
            tStep.append(tS)

        # add field array with data to output file
        fileData.append(tStep)
        fileData.append(rTorque)
        fileData.append(rSetP)
        fileData.append(rState)
        fileData.append(lTorque)
        fileData.append(lSetP)
        fileData.append(LState)
        fileData.append(lFsr)
        fileData.append(rFsr)

        fileDataTransposed = self.rotateArray(fileData)
        
        today = datetime.now()
        fileName = today.strftime("%Y-%b-%d-%H:%M:%S")
        fileName += '.csv'
        print("file is: ", fileName)

        with open(fileName, 'w') as csvFile:
            csvwriter = csv.writer(csvFile)

            csvwriter.writerows(fileDataTransposed)

    def rotateArray(slef, arrayToFlip):
        return [list(row) for row in zip(*arrayToFlip)]