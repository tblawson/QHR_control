"""
Run_QHR.py
Interact with the QHR magnet (via QHR supply) and a DVM.
Plot V vs B and simultaneously write data to csv files.
"""


import os
import pyvisa as visa
import csv
import instrument_control as control

rm = visa.ResourceManager()
print(rm.list_resources())

# Set up magnet as a visa resource:
magnet_addr_str = control.gpibaddr_num2str(input('magnet GPIB addr? > '))
# magnet_addr_str = 'GPIB0::4::INSTR'  # control.gpibaddr_num2str('4')
magnet_interface = rm.open_resource(magnet_addr_str)
magnet_interface.clear()
magnet = control.SMS(magnet_interface)  # Create SMS object called 'magnet'
magnet.show_sign_on_msg()  # Print multi-line message, summarising magnet supply state.

# Set up dvm as a visa resource
# dvm_addr_str = control.gpibaddr_num2str(input('dvm GPIB addr? > '))
dvm_addr_str = 'GPIB0::25::INSTR'  # control.gpibaddr_num2str('25')
dvm = rm.open_resource(dvm_addr_str)
dvm.timeout = 2000
dvm.read_termination = '\r\n'
dvm.write_termination = '\r\n'

QUIT = ['q', 'Q', 'quit', 'Quit', 'QUIT', 'exit', 'Exit', 'EXIT']
RAMP_ALIASES = {'mid': 'ramp mid',
                'max': 'ramp max',
                'zero': 'ramp zero'}
CMD_ALIASES = RAMP_ALIASES | {'stat': 'ramp status', 'out': 'get output'}  # Add 2 extra items

prev_cmd = '*IDN?'  # default command
while True:
    """
    Main control loop
    """
    cmd = input('Enter magnet command (or: "q" to quit; "r" to repeat last cmd)> ')

    # Special control-loop commands:
    if cmd in QUIT:
        break
    if cmd == 'r':  # repeat last command
        cmd = prev_cmd
    prev_cmd = cmd

    if cmd in CMD_ALIASES:
        cmd = CMD_ALIASES[cmd]

    magnet.send_cmd(cmd)
    magnet.read_buffer()  # Prints (by default) and returns message

    if magnet.is_ramping():
        magnet.run_ramp(dvm)  # Loops until ramp ends. Data is in magnet.Bs and magnet.Vs
    # print('\n___________ END OF MAIN LOOP ____________\n')
# END OF LOOP -----------------

# Data storage:
data_path = "G:/Shared drives/MSL - Electricity - Ongoing/QHR_CCC/Data_and_Analysis/Python_logging"
filename = "test.csv"
data_file = os.path.join(data_path, filename)

datalines = zip(magnet.Bs, magnet.Vs)
with open(data_file, w, newline=""):
    writer = csv.writer(data_file)
    for line in datalines:
        writer.writerow(line)

print('FINISHED.')
