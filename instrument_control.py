# instrument_control.py

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
        time.sleep(0.5)
        return command

    def read_buffer(self):
        self.instr.clear()
        time.sleep(0.5)
        while True:
            line = self.instr.read()
            if len(line) > 8:
                break
        (self.header, self.indicator, self.argument) = self.parse_message(line)
        print(f'header = {self.header}')
        print(f'indicator = {self.indicator}')
        print(f'argument = {self.argument}')
        return line

    @staticmethod
    def parse_message(m):
        header = m[0:8]
        ind_arg = m[9:-1]
        indicator, argument = ind_arg.split(':')  # m[9:m[9:-1].find(':')]
        # print(f'header = "{header}"; indicator = "{indicator}"; argument = "{argument}"')
        return header, indicator, argument

    def get_field(self):
        # print(f'___ get_field() ___:')
        self.send_cmd('get output', False)
        self.read_buffer()
        self.send_cmd('get output', True)  # Repeat to flush...
        response = self.read_buffer()      # ...ramp status msg
        # print(f'___ get_field() ___: response="{response}"\n')
        time.sleep(0.5)
        return self._extract_fieldvalue(response)

    @staticmethod
    def _extract_fieldvalue(s):
        """
        Extract field numeric value <y> from message string of the form:
        'xx:xx:xx OUTPUT: <y> : TESLA @ <z> VOLTS'
        :param s: message (string)
        :return: field in Tesla (float)
        """
        # print(f'___ _extract_fieldvalue() ___ from "{s}"')
        field = s[17:s.find(' TESLA')]
        try:
            return float(field)
        except ValueError:
            return '-'
        # if field.isnumeric():
        #     return float(field)
        # else:
        #     return field

    def ramp_finished(self):
        self.send_cmd('ramp status', False)
        response = self.read_buffer()
        if 'HOLDING ON TARGET' in response:
            return True
        else:
            return False

    def is_ramping(self):
        self.send_cmd('ramp status', False)
        response = self.read_buffer()
        if ': RAMPING ' in response:
            return True
        else:
            return False

    def run_ramp(self, dvm_visa, Vs, Bs):
        while True:
            # print(f'## TESTING ## - run_ramp(): Vs={Vs}, Bs={Bs}')
            v = dvm_visa.read()  # query('READ?')
            Vs.append(v)
            field = self.get_field()
            Bs.append(field)
            print(f'{v} V; {field} T')
            if self.ramp_finished():
                print('___ run_ramp() ___ : run_ramp(): BREAKING RAMP LOOP.')
                break
        return Vs, Bs


"""
Useful functions _________________________________________
"""


def gpibaddr_str2num(addr_str):  #
    return addr_str[7:addr_str.find('::INSTR')]


def gpibaddr_num2str(addr):
    return f'GPIB0::{addr}::INSTR'
# _____________________________________________________________


"""
Main script (for testing) _________________________________________
"""
# QUIT = ['q', 'Q', 'quit', 'Quit', 'QUIT', 'exit', 'Exit', 'EXIT']

# rm = visa.ResourceManager()
# print(rm.list_resources())
#
# magnet_addr_str = input('Full GPIB address? > ')
# magnet_interface = rm.open_resource(magnet_addr_str)
# magnet_interface.clear()
# magnet = SMS(magnet_interface)  # Create SMS object called 'magnet'

# magnet.show_sign_on_msg()
#
# print(f'current field = {magnet.get_field()} T')
#
# prev_cmd = cmd = '*IDN?'  # Default command
"""
Control-loop.
"""
# while True:
#     cmd = input('Enter command > ')
#
#     # Special control-loop commands:
#     if cmd in QUIT:
#         break
#     if cmd == 'r':  # repeat last command
#         cmd = prev_cmd
#
#     # Common cmd aliases:
#     if cmd == 'mid':
#         cmd = 'ramp mid'
#     if cmd == 'max':
#         cmd = 'ramp max'
#     if cmd == 'zero':
#         cmd = 'ramp zero'
#     if cmd == 'stat':
#         cmd = 'ramp status'
#     if cmd == 'out':
#         cmd = 'get output'
#
#     magnet.send_cmd(cmd)
#     print(magnet.read_buffer())
#
#     prev_cmd = cmd
#
# print('FINISHED.')
