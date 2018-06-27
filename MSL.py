import Instrument

class MSL(Instrument.Instrument):
    ''' Class for communicating with a Newmark Systems MSL Linear Stage
        with MDrive Motor'''
    
    def __init__(self, resource, strict=False, idString="..."):
    
        super().__init__(resource, strict, idString)
 
        self.velocity = self.getVelocity()
        self.position = self.getPosition()
        self.param = self.getParam()

    def Initialize(self):
        'Sets all variables to stored values'
        self.write("IP")
    
    def setVelInit(self, vel):
        'Set Initial Velocity'
        self.write("VI=" +str(vel))
        
    def setVelMax(self, vel):
        'Set max velocity'
        self.write("VM="+str(vel))
    
    def getVelocity(self):
        'Returns current velocity'
        self.velocity = self.query("PR V")
        return self.velocity
    
    def setAccel(self, acl):
        'Sets acceleration'
        self.write("A="+str(acl))
        
    def getParam(self):
        'Returns all parameters'
        self.param = self.query("PR AL")
        return self.param
    
    def MoveAbs(self, pos):
        'Moves to an absolute position from 0'
        self.write("MA " + str(pos))
    
    def MoveRel(self, pos):
        'Moves distance from current position'
        self.write("MR " + str(pos))
        
    def Jog(self,input):
        'Enables or disables job function'
        'Input 1 to enable, Input 0 to disable'
        self.write("JE="+str(input))
    
    def setHome(self):
        'Sets current position to home (0 position)'
        self.write("P=0")

    def getPosition(self):
        'Returns position relative to 0'
        self.position = self.query("PR P")
        return self.position
    
    def Hold(self):
        'Holds instruction till motion has stopped'
        self.write("H")
        
    def Calibrate(self):
        'Calibration'
        self.write("SC")
