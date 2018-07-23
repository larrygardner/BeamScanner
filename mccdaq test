####################################################################################
# For use with devices compatible with UL for Linux, as listed here:                #
#   https://www.mccdaq.com/PDFs/Manuals/Linux-hw.pdf                                #
#                                                                                   #
# For python reference:                                                             #
#   https://www.mccdaq.com/PDFs/Manuals/UL-Linux/python/api.html#device-discovery   #
#                                                                                   #
#####################################################################################

''' Program to get a continuous read out of analog data from any number of compatible devices '''
from time import sleep
from os import system
from sys import stdout
import sys

from uldaq import get_daq_device_inventory, DaqDevice, InterfaceType, AiInputMode, AInFlag

def reset_cursor():
    stdout.write('\033[1;1H')
    
daq_device = None

descriptor_index = 0
range_index = 0
interface_type = InterfaceType.USB
low_channel = 0
high_channel = 7
daq_device = {}
ai_device = {}
descriptor = {}
ai_info = {}
number_of_channels = {}
input_mode = {}
ranges = {}

# Get descriptors for all of the available DAQ devices.
devices = get_daq_device_inventory(interface_type)
number_of_devices = len(devices)
if number_of_devices == 0:
    raise Exception('Error: No DAQ devices found')
print('\nFound', number_of_devices, 'DAQ device(s):')

for i in range(number_of_devices):
    print('  ', devices[i].product_name, ' (', devices[i].unique_id, ')', sep='')

    # Create the DAQ device object associated with the specified descriptor index.
    daq_device["daq_device_" + str(i) ] = DaqDevice(devices[i])

    # Get the AiDevice object and verify that it is valid.
    ai_device["ai_device_" + str(i) ] = daq_device["daq_device_" + str(i)].get_ai_device()

    # Establish a connection to the DAQ device.
    descriptor["descriptor_" + str(i)] = daq_device["daq_device_" + str(i)].get_descriptor()
    
print('\n')

for i in range(number_of_devices):   
    print('Connecting to', descriptor["descriptor_" + str(i)].dev_string, '- please wait...')
    daq_device["daq_device_" + str(i)].connect()

    ai_info["ai_info_" + str(i)] = ai_device["ai_device_" + str(i)].get_info()
    number_of_channels["number_of_channels_" + str(i)] = ai_info["ai_info_" + str(i)].get_num_chans_by_mode(AiInputMode.SINGLE_ENDED)
    input_mode["input_mode_" + str(i)] = AiInputMode.SINGLE_ENDED
    ranges["ranges_" + str(i)] = ai_info["ai_info_" + str(i)].get_ranges(input_mode["input_mode_"+str(i)])
   
for i in range(number_of_devices):
    print('\n', descriptor["descriptor_" + str(i)].dev_string, ' ready', sep='')
    print('    Function demonstrated: ai_device.a_in()')
    print('    Channels: ', low_channel, '-', high_channel)
    print('    Input mode: ', input_mode["input_mode_" + str(i)].name)
    print('    Range: ', ranges["ranges_" + str(i)][range_index].name)

try:
    input('\nHit ENTER to continue\n')
except (NameError, SyntaxError):
    pass

system('clear')

try:
    while True:
        reset_cursor()
        print("Please enter CTRL + C to terminate the process\n")
    
        for i in range(len(ai_device)):
            #print(str(descriptor["descriptor_" + str(i)].dev_string) + ":")
            for channel in range(low_channel, high_channel + 1):
                data = ai_device["ai_device_" + str(i)].a_in(channel, input_mode["input_mode_" + str(i)], ranges["ranges_" + str(i)][range_index], AInFlag.DEFAULT)
                print('Channel(', channel, ') Data: ', '{:.6f}'.format(data), sep="")
            print('\n')
        sleep(0.1)
  
except KeyboardInterrupt:
    system("clear")
    pass

for i in range(number_of_devices):
    if daq_device["daq_device_" + str(i)].is_connected():
        daq_device["daq_device_" + str(i)].disconnect()
        daq_device["daq_device_" + str(i)].release()
        print(str(descriptor["descriptor_" + str(i)].dev_string) + " is disconnected.")
