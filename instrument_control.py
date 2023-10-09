# instrument_control.py

import pyvisa as visa
import time


class SMS:  # Superconducting Magnet Supply
    """
    Class to define operation of a magnet.
    """
    def __init__(self, instr):
        """
        :param instr: a visa I/O object (instrument).
        """
        self.instr = instr
        self.instr.write_termination = '\r'  # '\r\n'
        self.instr.timeout = 2000  # default 2 s timeout
        # print(self.instr.read())
        self._get_sign_on_msg()

    def _get_sign_on_msg(self):
        """
        Retrieve the full sign-on message from the magnet supply.
        This clears the output buffer, ready for further commands.
        :return: last message line (str)
        """
        line_num = 0
        self.msg = ''
        while True:
            line_num += 1
            line = self.instr.read()
            self.msg += f'{line}'
            if line_num > 7 and line[2] == ':':  # line == '\n'
                break
        return line  # final line

    def show_sign_on_msg(self):
        print('SMS SIGN-IN MESSAGE:')
        print('----------------------')
        print(self.msg)
        print('----------------------')

    def send_cmd(self, command, verbose=True):
        if verbose:
            print(f'Sending command "{command}"')
        self.instr.clear()
        time.sleep(0.5)
        self.instr.write(command)
        return command

    def read_buffer(self):
        self.instr.clear()
        time.sleep(0.5)
        while True:
            line = self.instr.read()
            if len(line) > 8:
                break
        return line

    def get_field(self):
        self.send_cmd('tesla on', False)  # Ensure units are Tesla
        self.read_buffer()  # clear output buffer
        self.send_cmd('get output', False)
        response = self.read_buffer()
        return self._extract_fieldvalue(response)

    @staticmethod
    def _extract_fieldvalue(s):
        """
        Extract field numeric value <y> from message string of the form:
        'xx:xx:xx OUTPUT: <y> : TESLA @ <z> VOLTS'
        :param s: message (string)
        :return: field in Tesla (float)
        """
        print(s)
        field = s[17:s.find(' TESLA')]
        return float(field)


"""
Main script (for testing) _________________________________________
"""
QUIT = ['q', 'Q', 'quit', 'Quit', 'QUIT', 'exit', 'Exit', 'EXIT']

rm = visa.ResourceManager()
print(rm.list_resources())

magnet_addr_str = input('Full GPIB address? > ')
magnet_interface = rm.open_resource(magnet_addr_str)
magnet_interface.clear()
magnet = SMS(magnet_interface)  # Create SMS object called 'magnet'

magnet.show_sign_on_msg()

print(f'current field = {magnet.get_field()} T')

prev_cmd = cmd = '*IDN?'  # Default command
"""
Control-loop.
"""
while True:
    cmd = input('Enter command > ')

    # Special control-loop commands:
    if cmd in QUIT:
        break
    if cmd == 'r':  # repeat last command
        cmd = prev_cmd

    # Common cmd aliases:
    if cmd == 'mid':
        cmd = 'ramp mid'
    if cmd == 'max':
        cmd = 'ramp max'
    if cmd == 'zero':
        cmd = 'ramp zero'
    if cmd == 'stat':
        cmd = 'ramp status'
    if cmd == 'out':
        cmd = 'get output'

    magnet.send_cmd(cmd)
    print(magnet.read_buffer())

    prev_cmd = cmd

print('FINISHED.')
