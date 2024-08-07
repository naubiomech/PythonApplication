class ChartData:
    def __init__(self):
        self.rightTorque = 0.0
        self.rightState = 0.0
        self.leftTorque = 0.0
        self.leftState = 0.0

    def updateValues(self, rightTorque, rightState, leftTorque, leftState):
        self.rightTorque = rightTorque
        self.rightState = rightState
        self.leftTorque = leftTorque
        self.leftState = leftState
