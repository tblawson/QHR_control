"""
Run_QHR.py
Interact with the QHR magnet (via QHR supply) and a DVM.
Plot V vs B and simultaneously write data to csv files.
"""


import os
import time

import pyvisa as visa
import csv
import datetime as dt
import instrument_control as control
import matplotlib.pyplot as plt
import matplotlib.animation as animation

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
dvm_addr_str = 'GPIB0::25::INSTR'  # control.gpibaddr_num2str('25')
dvm = rm.open_resource(dvm_addr_str)
dvm.timeout = 2000
dvm.read_termination = '\r\n'
dvm.write_termination = '\r\n'
dvm.write('FUNC OHMF,1e5')
dvm.write('OCOMP ON')

# ----------------------------------------------------
# Plotting-related stuff...

times = []  # Ramp timestamps
Bs = []  # B-field
Vs = []  # Vxy


def animate(i, dvm_visa, Bs, Vs):
    if magnet.ramp_finished():
        plt.close()
        return
    t = dt.datetime.now().strftime('%H:%M:%S')
    times.append(t)
    v = dvm_visa.read()
    Vs.append(v)
    field = magnet.get_field()
    Bs.append(field)
    ax.clear()
    ax.plot(Bs, Vs)
    plt.xticks(ha='center')  # (rotation=45, ha='right') (ha = horizontal alignment)
    plt.subplots_adjust(bottom=0.10, left=0.28)
    plt.title(f'Plotting point {i}')
    plt.ylabel('4-terminal resistance, kohm')
    plt.xlabel('B, Tesla')
    return
# ----------------------------------------------------


# ----------------------------------------------------
# Control loop command aliases:
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

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)  # (nrows, ncols, index)

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
        ani = animation.FuncAnimation(fig, animate, fargs=(dvm, Bs, Vs), frames=50, interval=500, repeat=False)
        plt.show()

# END OF CONTROL LOOP -----------------

# Data storage:
t_stamp = dt.datetime.now().strftime('%y%m%d_%H_%M_%S')
data_path = "G:/Shared drives/MSL - Electricity - Ongoing/QHR_CCC/Data_and_Analysis/Python_logging"
name = f"test_{t_stamp}.csv"
filename = os.path.join(data_path, name)

datalines = zip(times, Bs, Vs)
with open(filename, 'w', newline="") as fp:
    writer = csv.writer(fp)
    writer.writerow(['time', 'B', 'V'])  # Headers
    for line in datalines:
        writer.writerow(line)
    writer.writerow(['END', 'END', 'END'])

print('FINISHED.')
