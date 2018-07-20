"""
from uldaq import (get_daq_device_inventory, DaqDevice, InterfaceType, AiInputMode, Range, AInFlag)

devices = get_daq_device_inventory(InterfaceType.USB)
daq_device = DaqDevice(devices[0])
daq_device.connect()
ai_device = daq_device.get_ai_device()
ai_info = ai_device.get_info()
    
for channel in range(ai_info.get_num_chans()):
    data = ai_device.a_in(channel, AiInputMode.SINGLE_ENDED, Range.BIP10VOLTS, AInFlag.DEFAULT)
    print('Channel', channel, 'Data:', data)


daq_device.disconnect()
daq_device.release()
"""

from __future__ import print_function
from time import sleep
from os import system
from sys import stdout

from uldaq import get_daq_device_inventory, DaqDevice, InterfaceType, AiInputMode, AInFlag


daq_device = None

descriptor_index = 0
range_index = 0
interface_type = InterfaceType.USB
low_channel = 0
high_channel = 7

# Get descriptors for all of the available DAQ devices.
devices = get_daq_device_inventory(interface_type)
number_of_devices = len(devices)
if number_of_devices == 0:
    raise Exception('Error: No DAQ devices found')
print('Found', number_of_devices, 'DAQ device(s):')
for i in range(number_of_devices):
    print('  ', devices[i].product_name, ' (', devices[i].unique_id, ')', sep='')

# Create the DAQ device object associated with the specified descriptor index.
daq_device = DaqDevice(devices[0])
daq_device_2 = DaqDevice(devices[1])

# Get the AiDevice object and verify that it is valid.
ai_device = daq_device.get_ai_device()
ai_device_2 = daq_device_2.get_ai_device()

# Establish a connection to the DAQ device.
descriptor = daq_device.get_descriptor()
descriptor_2 = daq_device_2.get_descriptor()
print('\nConnecting to', descriptor.dev_string, '- please wait...')
daq_device.connect()
print('\nConnecting to', descriptor_2.dev_string, '- please wait...')
daq_device_2.connect()


ai_info = ai_device.get_info()
number_of_channels = ai_info.get_num_chans_by_mode(AiInputMode.SINGLE_ENDED)
ai_info_2 = ai_device_2.get_info()
number_of_channels_2 = ai_info_2.get_num_chans_by_mode(AiInputMode.SINGLE_ENDED)
    
input_mode = AiInputMode.SINGLE_ENDED
input_mode_2 = AiInputMode.SINGLE_ENDED

if high_channel >= number_of_channels:
    high_channel = number_of_channels - 1


ranges = ai_info.get_ranges(input_mode)
ranges_2 = ai_info_2.get_ranges(input_mode_2)
    
if range_index >= len(ranges):
    range_index = len(ranges) - 1
print('\n', descriptor.dev_string, ' ready', sep='')
print('    Function demonstrated: ai_device.a_in()')
print('    Channels: ', low_channel, '-', high_channel)
print('    Input mode: ', input_mode.name)
print('    Range: ', ranges[range_index].name)
print('\n', descriptor_2.dev_string, ' ready', sep='')
print('    Function demonstrated: ai_device.a_in()')
print('    Channels: ', low_channel, '-', high_channel)
print('    Input mode: ', input_mode_2.name)
print('    Range: ', ranges_2[range_index].name)

try:
    input('\nHit ENTER to continue\n')
except (NameError, SyntaxError):
    pass

system('clear')

while True:
    stdout.write('\033[1;1H')
    print('Please enter CTRL + C to terminate the process\n')

    for channel in range(low_channel, high_channel + 1):
        data = ai_device.a_in(channel, input_mode, ranges[range_index], AInFlag.DEFAULT)
        print('Channel(', channel, ') Data: ', '{:.6f}'.format(data), sep='')

    print('\n')
    
    for channel in range(low_channel, high_channel + 1):
        data = ai_device_2.a_in(channel, input_mode_2, ranges_2[range_index], AInFlag.DEFAULT)
        print('Channel(', channel, ') Data: ', '{:.6f}'.format(data), sep='')
    
    sleep(0.1)
    
    if KeyboardInterrupt:
        pass
    


if daq_device.is_connected():
    daq_device.disconnect()
daq_device.release()
if daq_device_2.is_connected():
    daq_device_2.disconnect()
daq_device_2.release()
