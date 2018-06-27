import visa
import os
from time import sleep
from HP8508A import HP8508A as HP
from HMCT2240 import HMCT2240 as HMC
from MSL import MSL

'''Configure Gpib'''
# Configures GPIB upon new bus entry
os.system("sudo gpib_config")

'''List resources '''
rm = visa.ResourceManager('@py')
lr = rm.list_resources()
print(lr)

''' Establish communication '''
vvm = HP(rm.open_resource("GPIB0::8::INSTR"))
sg = HMC(rm.open_resource("GPIB0::30::INSTR")) 
msl_x = MSL(rm.open_resource('''Address of msl in x direction '''))
msl_y = MSL(rm.open_resource('''Address of msl in y direction '''))

'''Initialize'''
# Travel direction of x travel stage
direction = "right"
# Initialize VVM
vvm.setTransmission()
vvm.setTriggerBus()
# Initialize SG
sg.setFreq(10e6) ''' Freq is adjustable '''
sg.setPower(-60) ''' Pow is adjustable  '''
sg.on()
# Reset MSL variables
msl_x.Initialize()
msl_y.Initialize()
# Establish data arrays
vvm_data = []
pos_data = []
# Step size in units of motor steps (default microstep resolution: 256,
# steps per revolution: 200 --> 256*200 = 51200 microsteps per revolution)
step = .5 * 51200 / 2 # .5 mm * steps per rev / mm per rev
# Position of MSLs such that WG is in center of beam (from calibration)
pos_x_center = ''' Position of center of beam (x) ''' * 51200 / 2
pos_y_center = ''' Position of center of beam (y)''' *51200 / 2
# Range of travel stage motion
pos_x_max = 25 * 51200 / 2 # 25 mm * 51200 microsteps per rev / 2 mm per rev
pos_y_max = pos_x_max
pos_x_min = -pos_x_max
pos_y_min = pos_x_min


'''Prepare for data'''
# Moves MSLs to position such that WG is in center of beam
msl_x.MoveAbs(pos_x_center)
msl_y.MoveAbs(pos_y_center)
# This sets the position at the center of beam to be the '0' point reference
msl_x.setHome()
msl_y.setHome()
# Moves both travel stages to minimum position
msl_x.MoveAbs(pos_x_min)
msl_y.MoveAbs(pos_y_min)
# Gets initial position
pos_x = msl_x.getPosition()
pos_y = msl_y.getPosition()
# VVM ready to begin collecting data
vvm.trigger()

'''Collect data'''
while pos_y <= pos_y_max:
    # "Direction" is the direction at which the X MSL travels
    # "Direction" gets reversed to maximize speed
    if direction == "right":
        while pos_x <= pos_x_max:
            # Collects VVM and position data
            vvm_data.append(vvm.getTransmission())
            pos_data.append((pos_x,pos_y))
            # X MSL steps relatively
            msl_x.MoveRel(step)
            pos_x = msl_x.getPosition()
        direction = "left"
    elif direction == "left":
        while pos_x >= pos_x_min:
            # Collects VVM and position data
            vvm_data.append(vvm.getTransmission())
            pos_data.append((pos_x,pos_y))
            # X MSL steps relatively in opposite direction (-)
            msl_x.MoveRel(-step)
            pos_x = msl_x.getPosition()
        direction = "right"
    # Y MSL steps relatively 
    msl_y.MoveRel(step)
    pos_y = msl_y.getPosition()

# Displays vvm and position data
print(vvm_data)
print(pos_data)

# Turns signal generator off
sg.off()


