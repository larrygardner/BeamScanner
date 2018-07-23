################################################################
# Download these files from github:                            #
# HP8508A.py , HMCT2240.py and  MSL.py to control instruments  #
# time_plot.py , contour_plot and y_plot.py to make plots      #
# spreadsheet.py to write data to spreadsheet                  #
################################################################

import visa
import os
import time
from time import sleep

from HP8508A import HP8508A as HP
from HMCT2240 import HMCT2240 as HMC
from MSL import MSL

from time_plot import time_plot
from contour_plot import contour_plot
from y_plot import y_plot

from spreadsheet import spreadsheet


''' Start '''
# Input file name for spreadsheet
save_name = "test"

print("Starting...\n")
start_time = time.time()

# Configures GPIB upon new bus entry
os.system("sudo gpib_config")
print("GPIB devices configured.")

# Lists available resources
rm = visa.ResourceManager('@py')
lr = rm.list_resources()
print("Available Resources: "+str(lr))

# Establish communication
vvm = HP(rm.open_resource("GPIB0::8::INSTR"))
#sg = HMC(rm.open_resource("GPIB0::30::INSTR")) 
msl_x = MSL(rm.open_resource("ASRL/dev/ttyUSB0"))
#msl_y = MSL(rm.open_resource('''Address of msl in y direction '''))


'''Initialize'''
# MSL velocities
print("Maximum velocity: "+ str(msl_x.getVelMax()))

# Data format
vvm.setFormatLog()
print("VVM format: " + str(vvm.getFormat()) + "\n")

# Travel direction of x travel stage
direction = "right"

# Sets delay for data points
delay = 0

# Initialize VVM
vvm.setTransmission()
vvm.setTriggerBus()

# Reset MSL variables
msl_x.zero()
msl_x.hold()

# Establish data arrays
vvm_data = []
pos_data = []
time_data = []

# Conversion factor from metric to microsteps [microsteps / mm]
conv_factor = 5000 

#Step size for data increments
step = int(1 * conv_factor) # .5 mm * 5000 microsteps / mm

# Position of MSLs such that WG is in center of beam (from calibration)
pos_x_center = int(20 * conv_factor)
#pos_y_center = int(''' Position of center of beam (y) ''' * conv_factor

# Range of travel stage motion (50x50mm)
pos_x_max = int(1 * conv_factor) # 25 mm * 5000 microsteps per mm
pos_y_max = int(1)
pos_x_min = -pos_x_max
pos_y_min = -pos_y_max

# Limits center position given range of travel
if pos_x_center <= pos_x_max or (100*conv_factor - pos_x_center) <= pos_x_max:
    print("\n****Data range is too large.****\n****Decrease X-Y max range.****\n")
    raise


'''Prepare for data'''
print("Preparing for data ...")

# Moves MSLs to position such that WG is in center of beam
msl_x.moveAbs(pos_x_center)
msl_x.hold()

# This sets the position at the center of beam to be the '0' point reference
msl_x.setHome()

# Moves both travel stages to minimum position
msl_x.moveAbs(pos_x_min)
msl_x.hold()

# Gets initial position
pos_x = int(msl_x.getPos())
pos_y = int(pos_y_min)

# VVM ready to begin collecting data
vvm.trigger()


'''Collect data'''
print("\nCollecting data: ")

while pos_y <= pos_y_max:
    # "Direction" is the direction at which the X MSL travels
    # "Direction" gets reversed to maximize speed
    if direction == "right":
        while pos_x <= pos_x_max:
            # Collects VVM and position data
            time.sleep(delay)
            time_data.append(time.time())
            trans= vvm.getTransmission()
            vvm_data.append(trans)
            pos_data.append((pos_x/conv_factor,pos_y))
            print("    X: " + str(pos_x/conv_factor) + ", Y: " + str(pos_y))
            print("    " + str(trans))
            
            # X MSL steps relatively, if not in maximum position
            if pos_x != pos_x_max:
                msl_x.moveRel(step)
                msl_x.hold()
                pos_x = int(msl_x.getPos())
            elif pos_x == pos_x_max:
                break
        direction = "left"
        pass
        
    elif direction == "left":
        while pos_x >= pos_x_min:
            # Collects VVM and position data
            time.sleep(delay)
            time_data.append(time.time())
            trans = vvm.getTransmission()
            vvm_data.append(trans)
            pos_data.append((pos_x/conv_factor,pos_y))
            print("    X: " + str(pos_x/conv_factor) + ", Y: " + str(pos_y))
            print("    " + str(trans))
            # X MSL steps relatively in opposite direction (-), if not in minimum position
            if pos_x != pos_x_min:
                msl_x.moveRel(-step)
                msl_x.hold()
                pos_x = int(msl_x.getPos())
            elif pos_x == pos_x_min:
                break
        direction = "right"
        pass
    
    pos_y += 1

# Execution time
print("\nExecution time: " + str(time.time() - start_time))

# Adjusts time data
time_initial = time_data[0]
for i in range(len(time_data)):
    time_data[i] = time_data[i] - time_initial

# Writing to spread sheet via function
print("Writing data to spreadsheet...")
spreadsheet(time_data, pos_data, vvm_data, save_name)


''' Plotting Data '''
print("Plotting data ...")

# Plots position vs. amplitude contour plot via function
contour_plot(pos_data, vvm_data)

# Plots amplitude and phase vs. time
time_plot(time_data, vvm_data)

# Plots amplitude and phase vs. y position for slice at center of beam
y_plot(pos_data, vvm_data)


''' End '''
print("\nEnd.")
