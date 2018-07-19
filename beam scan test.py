import visa
import os
import time
from time import sleep
from HP8508A import HP8508A as HP
from HMCT2240 import HMCT2240 as HMC
from MSL import MSL
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
import numpy as np

''' Start '''
print("Starting...")
start_time = time.time()

'''Configure Gpib'''
# Configures GPIB upon new bus entry
os.system("sudo gpib_config")
print("GPIB devices configured.")

'''List resources '''
rm = visa.ResourceManager('@py')
lr = rm.list_resources()
print("Available Resources: "+str(lr))

''' Establish communication '''
vvm = HP(rm.open_resource("GPIB0::8::INSTR"))
#sg = HMC(rm.open_resource("GPIB0::30::INSTR")) 
msl_x = MSL(rm.open_resource("ASRL/dev/ttyUSB0"))
#msl_y = MSL(rm.open_resource('''Address of msl in y direction '''))

'''Initialize'''
print("Preparing for data ...")
# Sets MSL velocities
msl_x.setVelMax(500000)
print(msl_x.getVelMax())

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

# Conversion factor from metric to microsteps [microsteps / mm]
conv_factor = 5000 

#Step size for data increments
step = int(.5 * conv_factor) # .5 mm * 5000 microsteps / mm

# Position of MSLs such that WG is in center of beam (from calibration)
pos_x_center = int(25 * conv_factor)
#pos_y_center = int(''' Position of center of beam (y) ''' * conv_factor

# Range of travel stage motion (50x50mm)
pos_x_max = int(5 * conv_factor) # 25 mm * 5000 microsteps per mm
pos_y_max = int(5)
pos_x_min = -pos_x_max
pos_y_min = -pos_y_max


'''Prepare for data'''
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
print("Collecting data ...")

while pos_y <= pos_y_max:
    # "Direction" is the direction at which the X MSL travels
    # "Direction" gets reversed to maximize speed
    if direction == "right":
        while pos_x <= pos_x_max:
            # Collects VVM and position data
            time.sleep(delay)
            trans = vvm.getTransmission()
            vvm_data.append(trans)
            pos_data.append((pos_x/conv_factor,pos_y))
            print("X: " + str(pos_x/conv_factor) + ", Y: " + str(pos_y))
            print(trans)
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
            trans = vvm.getTransmission()
            vvm_data.append(trans)
            pos_data.append((pos_x/conv_factor,pos_y))
            print("X: " + str(pos_x/conv_factor) + ", Y: " + str(pos_y))
            print(trans)
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
print("Execution time: " + str(time.time() - start_time))

''' Plotting Data '''
print("Plotting data ...")

x_data = []
y_data = []
pow_data = []
phase_data = []

for i in pos_data:
    x_data.append(i[0])
    y_data.append(i[1])
    
if type(vvm_data[0]) == tuple:
    for i in vvm_data:
        pow_data.append(i[0])
        phase_data.append(i[1])
elif type(vvm_data[0]) == str:
    for i in vvm_data:
        pow_data.append(float(i.split(",")[0]))
        phase_data.append(float(i.split(",")[1]))

xi = np.linspace(pos_x_min/conv_factor, pos_x_max/conv_factor, 1000)
yi = np.linspace(pos_y_min, pos_y_max, 1000)
zi = griddata(x_data, y_data, pow_data, xi, yi, interp='linear')

plt.contour(xi, yi, zi, 15, linewidths=0.5, colors='k')
plt.contourf(xi, yi, zi, 15, vmax=zi.max(), vmin=zi.min())
plt.colorbar()
plt.xlabel("X Position (mm)")
plt.ylabel("Y Position (mm)")
plt.xlim(pos_x_min/conv_factor, pos_x_max/conv_factor)
plt.ylim(pos_y_min, pos_y_max)
plt.title("Power vs. Position")
plt.show()

''' End '''
print("End.")
