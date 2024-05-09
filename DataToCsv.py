import csv
from _datetime import datetime

def main():
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
    
    today = datetime.now()
    fileName = today.strftime("%Y-%b-%d-%H:%M:%S")
    fileName += '.csv'
    print("file is: ", fileName)



    with open(fileName, 'w') as csvFile:
        csvwriter = csv.writer(csvFile)

        csvwriter.writerows(fileData)

if __name__ == "__main__":
    main()

