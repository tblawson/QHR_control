"""
Run_QHR.py
Interact with the QHR magnet (via QHR supply) and a DVM.
Plot V vs B and simultaneously write data to csv files.
"""


import pyvisa as visa
import csv
import instrument_control as control

rm = visa.ResourceManager()
print(rm.list_resources())

# Set up magnet as a visa resource:
magnet_addr_str = control.gpibaddr_num2str(input('magnet GPIB addr? > '))
magnet_interface = rm.open_resource(magnet_addr_str)
magnet_interface.clear()
magnet = control.SMS(magnet_interface)  # Create SMS object called 'magnet'
magnet.show_sign_on_msg()  # Print multi-line message, summarising magnet supply state.

# Set up dvm as a visa resource
dvm_addr_str = control.gpibaddr_num2str(input('dvm GPIB addr? > '))
dvm = rm.open_resource(dvm_addr_str)

"""
Magnet control-loop 1.
"""
QUIT = ['q', 'Q', 'quit', 'Quit', 'QUIT', 'exit', 'Exit', 'EXIT']
CMD_ALIASES = {'mid': 'ramp mid',
               'max': 'ramp max',
               'zero': 'ramp zero',
               'stat': 'ramp status',
               'out': 'get output'}
prev_cmd = '*IDN?'  # default command
while True:
    """
    Use this control loop as a sandbox to explore magnet functions.
    and set up ramp limits - But NOT for acquiring data.
    """
    cmd = input('Enter command > ')

    # Special control-loop commands:
    if cmd in QUIT:
        break
    if cmd == 'r':  # repeat last command
        cmd = prev_cmd
    prev_cmd = cmd

    if cmd in CMD_ALIASES:
        cmd = CMD_ALIASES[cmd]

    magnet.send_cmd(cmd)
    print(magnet.read_buffer())

# Lists to contain data:
Vs = []
Bs = []

cmd = input('Enter ramp command > ')
if cmd in CMD_ALIASES:
    cmd = CMD_ALIASES[cmd]
magnet.send_cmd(cmd)
print(magnet.read_buffer())

print(f'DVM \tMagnet')

while True:
    V = dvm.read()
    Vs.append(V)
    B = dvm.read()
    Bs.append(B)
    print(f'{V} V\t{B} T')
    if magnet.ramp_finished():
        break

print('FINISHED.')
