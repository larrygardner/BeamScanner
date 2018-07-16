import visa
import os
from HP8508A import HP8508A as HP
from HMCT2240 import HMCT2240 as HMC
from MSL import MSL

'''Configure Gpib'''
# Configures GPIB upon new bus entry
os.system("sudo gpib_config")

'''List resources '''
rm = visa.ResourceManager('@py')
#lr = rm.list_resources()
#print(lr)

''' Establish communication '''
vvm = HP(rm.open_resource("GPIB0::8::INSTR"))
sg = HMC(rm.open_resource("GPIB0::30::INSTR")) 
msl_x = MSL(rm.open_resource("ASRL/dev/ttyUSB0"))
msl_y = MSL(rm.open_resource('''Address of msl in y direction '''))

'''Initialize'''
# Travel direction of x travel stage
direction = "right"

# Initialize VVM
vvm.setTransmission()
vvm.setTriggerBus()

# Initialize SG
sg.setFreq(10e6)
sg.setPower(-60)
sg.on()

# Reset MSL variables
msl_x.zero()
msl_y.zero()

# Establish data arrays
vvm_data = []
pos_data = []

''' '''
'This section converts microstep data into metric data'
# Microstep resolution (default: 250)
ms_res = 250
# Steps per revolution: 200
step_per_rev = 200
#The MSL-100-24 uses a 2mm pitch screw
pitch= 2
#These constants make a step to mm conversion factor of:
conv_factor = ms_res * step_per_rev / pitch #Units: [microsteps / mm]
#Step size for data increments
step = .5 * conv_factor # .5 mm * 5000 microsteps / mm
''' '''

# Position of MSLs such that WG is in center of beam (from calibration)
pos_x_center = ''' Position of center of beam (x) ''' * conv_factor
pos_y_center = ''' Position of center of beam (y) ''' * conv_factor
# Range of travel stage motion (25x25mm)
pos_x_max = int(25 * conv_factor) # 25 mm * 5000 microsteps per mm
pos_y_max = pos_x_max
pos_x_min = -pos_x_max
pos_y_min = pos_x_min


'''Prepare for data'''
# Moves MSLs to position such that WG is in center of beam
msl_x.moveAbs(pos_x_center)
msl_y.moveAbs(pos_y_center)
# This sets the position at the center of beam to be the '0' point reference
msl_x.setHome()
msl_y.setHome()
# Moves both travel stages to minimum position
msl_x.moveAbs(pos_x_min)
msl_y.moveAbs(pos_y_min)
# Gets initial position
pos_x = int(msl_x.getPos())
pos_y = int(msl_y.getPos())
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
            pos_data.append((pos_x/conv_factor,pos_y/conv_factor))
            # X MSL steps relatively, if not in maximum position
            if pos_x != pos_x_max:
                msl_x.moveRel(step)
                msl_x.hold()
                pos_x = int(msl_x.getPos())
                print(pos_x)
            elif pos_x == pos_x_max:
                break
        direction = "left"
        pass
    elif direction == "left":
        while pos_x >= pos_x_min:
            # Collects VVM and position data
            vvm_data.append(vvm.getTransmission())
            pos_data.append((pos_x/conv_factor,pos_y/conv_factor))
            # X MSL steps relatively in opposite direction (-), if not in minimum position
            if pos_x != pos_x_min:
                msl_x.moveRel(-step)
                msl_x.hold()
                pos_x = int(msl_x.getPos())
            elif pos_x == pos_x_min:
                break
        direction = "right"
        pass
    # Y MSL steps relatively 
    msl_y.moveRel(step)
    msl_y.hold()
    pos_y = int(msl_y.getPos())

# Displays vvm and position data
print(vvm_data)
print(pos_data)

# Turns signal generator off
sg.off()


