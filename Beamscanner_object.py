import visa
import os
import pyoo
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.mlab import griddata
import numpy.polynomial.polynomial as poly
from time import sleep

from HP8508A import HP8508A as HP
from HMCT2240 import HMCT2240 as HMC
from MSL import MSL
from time_plot import time_plot
from y_plot import y_plot
        
        
class Beamscanner:
    def __init__(self):
        
        self.vvm = None
        self.msl_x = None
        self.msl_y = None
        self.sg = None
        
        self.direction = "right"
        self.delay = 0
        
        # Set variables for Signal Generator
        self.freq = 10e6
        self.power = -60
        
        # Establish data arrays
        self.vvm_data = []
        self.pos_data = []
        self.time_data = []

        # Conversion factor from metric to microsteps [microsteps / mm]
        self.conv_factor = 5000
        
        #Step size for data increments
        self.step = int(1 * self.conv_factor) # .5 mm * 5000 microsteps / mm
    
    def initTime(self):
        import time
        start_time = time.time()
        return start_time
    
    def initGPIB(self):
        # Configures GPIB upon new bus entry
        os.system("sudo gpib_config")

        # Lists available resources
        rm = visa.ResourceManager('@py')
        lr = rm.list_resources()
        return rm, lr
    
    def initVVM(self):
        self.vvm.setTransmission()
        self.vvm.setFormatLog()
        self.vvm.setTriggerBus()
        
    def initSG(self):
        self.sg.setFreq(self.freq)
        self.sg.setPower(-60)
        self.sg.on()
    
    def initMSLX(self):
        self.msl_x.zero()
        self.msl_x.hold()
    
    def initMSLY(self):
        self.msl_y.zero()
        self.msl_y.hold()
        
    def setRange(self, range = 25):
        # Range of travel stage motion (50x50mm)
        self.pos_x_max = int(range * self.conv_factor) # 25 mm * 5000 microsteps per mm
        #self.pos_y_max = self.pos_x_max
        self.pos_x_min = -self.pos_x_max
        #self.pos_y_min = self.pos_x_min
        self.pos_y_max = int(range)
        self.pos_y_min = -int(range)
        
        # Limits center position given range of travel
        if self.pos_x_center <= self.pos_x_max or (100*self.conv_factor - self.pos_x_center) <= self.pos_x_max:
            return "****Data range is too large.****\n****Adjust X max range.****\n"
            raise
        elif self.pos_y_center <= self.pos_y_max or (100*self.conv_factor - self.pos_y_center) <= self.pos_y_max:
            return "****Data range is too large.****\n****Adjust Y max range.****\n"
            raise
        else:
            return "Range is sufficient.\n"
    
    """
    def makeScanPts(self, Usize, Vsize, Ustep, Vstep, Uoffset = 0, Voffset = 0):
    """
    def findCenter(self):
        self.pos_x_center = 10 * self.conv_factor
        self.pos_y_center = 10 * self.conv_factor
        return self.pos_x_center, self.pos_y_center
    
    def moveToCenter(self):
        self.msl_x.moveAbs(self.pos_x_center)
        #self.msl_y.moveAbs(self.pos_y_center)
        self.msl_x.hold()
        #self.msl_y.hold()
        self.msl_x.setHome()
        #self.msl_y.setHome()
       
    def initScan(self):
        # Gets initial position
        self.pos_x = int(self.msl_x.getPos())
        #self.pos_y = int(self.msl_y.getPos())
        self.pos_y = int(2)

        # VVM ready to begin collecting data
        self.vvm.trigger()
        
    def scan(self):
        while self.pos_y <= self.pos_y_max:
            # "Direction" is the direction at which the X MSL travels
            # "Direction" gets reversed to maximize speed
            if self.direction == "right":
                while self.pos_x <= self.pos_x_max:
                    # Collects VVM and position data
                    time.sleep(self.delay)
                    self.time_data.append(time.time())
                    trans = self.vvm.getTransmission()
                    self.vvm_data.append(trans)
                    self.pos_data.append((self.pos_x/self.conv_factor,self.pos_y))
                    print("    X: " + str(self.pos_x/self.conv_factor) + ", Y: " + str(self.pos_y))
                    print("    " + str(trans))
                    # X MSL steps relatively, if not in maximum position
                    if self.pos_x != self.pos_x_max:
                        self.msl_x.moveRel(self.step)
                        self.msl_x.hold()
                        self.pos_x = int(self.msl_x.getPos())
                    elif self.pos_x == self.pos_x_max:
                        break
            
                self.direction = "left"
                pass
    
            elif self.direction == "left":
                while self.pos_x >= self.pos_x_min:
                    # Collects VVM and position data
                    time.sleep(self.delay)
                    self.time_data.append(time.time())
                    trans = self.vvm.getTransmission()
                    self.vvm_data.append(trans)
                    self.pos_data.append((self.pos_x/self.conv_factor,self.pos_y))
                    print("    X: " + str(self.pos_x/self.conv_factor) + ", Y: " + str(self.pos_y))
                    print("    " + str(trans))
                    # X MSL steps relatively in opposite direction (-), if not in minimum position
                    if self.pos_x != self.pos_x_min:
                        self.msl_x.moveRel(-self.step)
                        self.msl_x.hold()
                        self.pos_x = int(self.msl_x.getPos())
                    elif self.pos_x == self.pos_x_min:
                        break
                    
                self.direction = "right"
                pass
            
            # Y MSL steps relatively 
            #self.msl_y.moveRel(self.step)
            #self.msl_y.hold()
            #self.pos_y = int(self.msl_y.getPos())
            self.pos_y += 1
            
        self.time_initial = self.time_data[0]
        for i in range(len(self.time_data)):
            self.time_data[i] = self.time_data[i] - self.time_initial
            
    def endSG(self):
        self.sg.off()
    
    def spreadsheet(self, save_name):

        # Creates localhost for libre office
        os.system("soffice --accept='socket,host=localhost,port=2002;urp;' --norestore --nologo --nodefault # --headless")
        # Uses pyoo to open spreadsheet
        desktop = pyoo.Desktop('localhost',2002)
        doc = desktop.create_spreadsheet()
    
        x_data = []
        y_data = []
        amp_data = []
        phase_data = []
    
        for i in range(len(self.pos_data)):
            x_data.append(self.pos_data[i][0])
            y_data.append(self.pos_data[i][1])
    
            if type(self.vvm_data[0]) == tuple:
                amp_data.append(self.vvm_data[i][0])
                phase_data.append(self.vvm_data[i][1])
            
            elif type(vvm_data[0]) == str:
                amp_data.append(float(self.vvm_data[i].split(",")[0]))
                phase_data.append(float(self.vvm_data[i].split(",")[1]))
    
        try:
            # Writes data to spreadsheet
            sheet = doc.sheets[0]
            sheet[0,0:5].values = ["Time (s)","X Position (mm)", "Y Position (mm)", "Amplitude (dB)", "Phase (deg)"]
            sheet[1:len(self.time_data)+1, 0].values = time_data
            sheet[1:len(self.pos_data)+1, 1].values = x_data
            sheet[1:len(self.pos_data)+1, 2].values = y_data
            sheet[1:len(self.pos_data)+1, 3].values = amp_data
            sheet[1:len(self.pos_data)+1, 4].values = phase_data
    
            doc.save('BeamScannerData/' + str(save_name) + '.xlsx')
            doc.close()
    
        except (ValueError, KeyboardInterrupt, RuntimeError):
            doc.close()
            pass
            
            
    def contour_plot(self):
        x_data = []
        y_data = []
        amp_data = []    

        for i in range(len(self.pos_data)):
            x_data.append(self.pos_data[i][0])
            y_data.append(self.pos_data[i][1])
    
            if type(self.vvm_data[0]) == tuple:
                amp_data.append(self.vvm_data[i][0])
        
            elif type(self.vvm_data[0]) == str:
                amp_data.append(float(self.vvm_data[i].split(",")[0]))
    
        pos_x_min = min(x_data)
        pos_x_max = max(x_data)
        pos_y_min = min(y_data)
        pos_y_max = max(y_data)
        
        xi = np.linspace(pos_x_min, pos_x_max, 1000)
        yi = np.linspace(pos_y_min, pos_y_max, 1000)
        zi = griddata(x_data, y_data, amp_data, xi, yi, interp = "linear")

        CS = plt.contour(xi, yi, zi, levels=[-35,-30,-25,-20, -15, -10, -5], colors='black')
        plt.clabel(CS, inline =1)
        plt.xlabel("X Position (mm)")
        plt.ylabel("Y Position (mm)")
        matplotlib.rcParams['contour.negative_linestyle'] = 'solid'
        plt.xlim(pos_x_min, pos_x_max)
        plt.ylim(pos_y_min, pos_y_max)
        plt.title("Amplitude vs. Position")
        plt.show()
    
    def time_plot(self):

        amp_data = []
        phase_data = []
    
        if type(self.vvm_data[0]) == tuple:
            for i in self.vvm_data:
                amp_data.append(i[0])
                phase_data.append(i[1])
        
        elif type(self.vvm_data[0]) == str:
            for i in self.vvm_data:
                amp_data.append(float(i.split(",")[0]))
                phase_data.append(float(i.split(",")[1]))
        
        fig, ax1 = plt.subplots()
    
        ax1.plot(self.time_data, amp_data, 'bD--', label = "Amplitude (dB)")
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Amplitude (dB)', color='b')
        ax1.tick_params('y', colors='b')
        plt.legend(loc = "upper left")
    
        ax2 = ax1.twinx()
        ax2.plot(self.time_data, phase_data, 'r^-', label = "Phase (deg)")
        ax2.set_ylabel('Phase (deg)', color='r')
        ax2.tick_params('y', colors='r')
        plt.legend(loc = "upper right")
        
        fig.tight_layout()
        plt.show()
    
    def y_plot(self):
    
        y_data = []
        amp_data = []
        phase_data = []    

        for i in range(len(self.pos_data)):
            if self.pos_data[i][0] == 0:
                y_data.append(self.pos_data[i][1])
    
                if type(self.vvm_data[0]) == tuple:
                    amp_data.append(self.vvm_data[i][0])
                    phase_data.append(self.vvm_data[i][1])
        
                elif type(self.vvm_data[0]) == str:
                    amp_data.append(float(self.vvm_data[i].split(",")[0]))
                    phase_data.append(float(self.vvm_data[i].split(",")[1]))
            
        fig, ax1 = plt.subplots()
    
        x_new = np.linspace(y_data[0], y_data[-1], num=len(y_data)*10)
    
        coefs_amp = poly.polyfit(y_data, amp_data, 2)    
        fit_amp = poly.polyval(x_new, coefs_amp)
        ax1.plot(y_data, amp_data, 'bD', label = "Amp (meas)")
        ax1.plot(x_new, fit_amp, 'b--', label = "Amp (fitted)")
        ax1.set_xlabel("Y position (mm)")
        ax1.set_ylabel("Amplitude (dB)", color='b')
        ax1.tick_params('y', colors='b')
        ax1.legend(loc = "upper left")
        
        coefs_phase = poly.polyfit(y_data, phase_data, 2)
        fit_phase = poly.polyval(x_new, coefs_phase)
        ax2 = ax1.twinx()
        ax2.plot(y_data, phase_data, 'r^', label = "Phase (meas)")
        ax2.plot(x_new, fit_phase, 'r-', label = "Phase (fitted)")
        ax2.set_ylabel('Phase (deg)', color='r')
        ax2.tick_params('y', colors='r')
        ax2.legend(loc = "upper right")
        
        fig.tight_layout()
        plt.show()
    


if __name__ == "__main__":
    print("Starting...\n")
    
    bs = Beamscanner()
    
    start = bs.initTime()
    
    rm, lr = bs.initGPIB()
    print("GPIB devices configured. \nAvailable Resources: "+str(lr))
    
    bs.vvm = HP(rm.open_resource("GPIB0::8::INSTR"))
    #bs.sg = HMC(rm.open_resource("GPIB0::30::INSTR"))
    bs.msl_x = MSL(rm.open_resource("ASRL/dev/ttyUSB0"))
    #bs.msl_y = MSL(rm.open_resource('''''ADDRESS OF MSL IN Y DIRECTION '''''))
    
    # Initializes instruments
    bs.initVVM()
    #bs.initSG()
    bs.initMSLX()
    #bs.initMSLY()

    # MSL velocities
    print("Maximum velocity: " + str(bs.msl_x.getVelMax()))
    #print("Maximum velocity: " + str(bs.msl_y.getVelMax()))
    # VVM data format
    print("VVM format: " + str(bs.vvm.getFormat()) + "\n")

    bs.findCenter()
    range = bs.setRange(2)
    print(range)
    
    print("Preparing for data ...")

    bs.moveToCenter()
    bs.initScan()
 
    print("\nCollecting data ...")
    bs.scan()
    bs.endSG()
    print("\nExecution time: " + str(time.time() - start))
    
    # Writing to spread sheet via function
    print("Writing data to spreadsheet...")
    bs.spreadsheet("objectTest")

    print("Plotting data ...")
    # Plots position vs. amplitude contour plot via function
    bs.contour_plot(pos_data, vvm_data)
    # Plots amplitude and phase vs. time
    bs.time_plot(time_data, vvm_data)
    # Plots amplitude and phase vs. y position for slice at center of beam
    bs.y_plot(pos_data, vvm_data)

    print("\nEnd.")

    