# instrument_control.py

import time
import datetime as dt
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
DELAY = 0.1


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
        line = self._get_sign_on_msg()
        if 'AMPS' in line:
            self.send_cmd('TESLA ON')  # ensure readings are in Tesla
        # Use this magnet instance to store ALL instrument readings.
        # self.times = []  # Ramp timestamps
        # self.Bs = []  # B-field
        # self.Vs = []  # Vxy
        # Setup plot (used during ramp)
        # self.fig = plt.figure(1)  # open plot 1
        # self.ax = self.fig.add_subplot(1, 1, 1)  # (nrows, ncols, index). Global

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
        time.sleep(DELAY)
        self.instr.write(command)
        time.sleep(DELAY)
        return command

    def read_buffer(self, echo=True):
        self.instr.clear()
        time.sleep(DELAY)
        while True:
            line = self.instr.read()
            if len(line) > 8:
                break
        # self.parse_message(line)
        if echo:
            print(line)
        return line

    @staticmethod
    def parse_message(m):
        """
        Divide magnet messages into header, indicator and argument sections.
        :param m: (string) message.
        :return: tuple of strings: (header, indicator, argument)
        """
        # print(f'Parsing "{m}"')
        header = m[0:8]  # 1st 9 characters
        ind_arg = m[9:-1]  # rest of message is "<indicator>:<argument>"
        indicator, argument = ind_arg.split(':')
        return header, indicator, argument

    def get_field(self):
        """
        Query magnet for an OUTPUT message and extract the field value.
        :return: string
        """
        self.send_cmd('get output', verbose=False)
        self.read_buffer(echo=False)  # Prints (by default) and returns message
        time.sleep(DELAY)
        self.send_cmd('get output', verbose=False)  # Repeat to flush...
        response = self.read_buffer(echo=False)      # ...ramp status msg
        time.sleep(DELAY)
        return self._extract_fieldvalue(response)

    def _extract_fieldvalue(self, s):
        """
        Extract field numeric value <y> from message string of the form:
        'xx:xx:xx OUTPUT: <y> : TESLA @ <z> VOLTS'
        :param s: message (string)
        :return: field in Tesla (float)
        """
        (header, indicator, argument) = self.parse_message(s)
        if indicator == 'OUTPUT' and 'TESLA' in argument:
            try:
                field = argument[0:argument.find(' TESLA')]
                return float(field)
            except ValueError:
                print(f'Magnet response error: {s}')
                return '-x-'
        elif indicator == 'RAMP STATUS':
            return '-END-'

    def ramp_finished(self):
        """
        Determine if the ramp has completed by checking the ramp status.
        :return: boolean
        """
        self.send_cmd('ramp status', verbose=False)
        response = self.read_buffer(echo=False)  # Prints (by default) and returns message
        if 'HOLDING ON TARGET' in response:
            print(f'Ramp finished: {response}')
            return True
        else:
            # print(f'Ramp still running: {response}')
            return False

    def is_ramping(self):
        """
        Determine if the ramp is still underway by checking the ramp status.
        :return: boolean
        """
        self.send_cmd('ramp status', verbose=False)
        response = self.read_buffer(echo=False)  # Prints (by default) and returns message
        if ': RAMPING ' in response:
            return True
        else:
            return False


    # def run_ramp(self, dvm_visa):
    #     """
    #     Acquire and plot data until the magnet stops ramping.
    #     :param dvm_visa: dvm visa instance
    #     :return: Vs, Bs: lists of voltages and field readings
    #     """
    #     fig = plt.figure()
    #     self. ax = fig.add_subplot(1, 1, 1)  # (nrows, ncols, index)
    #     ani = animation.FuncAnimation(fig, self.animate, fargs=(xs, ys), frames=50, interval=1000)
    #     plt.show()
    #     return
    #
    # def animate(i, self):
    #     t = dt.datetime.now().strftime('%H:%M:%S')
    #     self.times.append(t)
    #     v = dvm_visa.read()
    #     self.Vs.append(v)
    #     field = self.get_field()
    #     self.Bs.append(field)
    #     self.ax.clear()
    #     self.ax.plot(Bs, Vs)
    #     plt.xticks(ha='center')  # (rotation=45, ha='right') (ha = horizontal alignment)
    #     plt.subplots_adjust(bottom=0.30)
    #     plt.title(f'Plotting point {i}')
    #     plt.ylabel('Vxy')
    #     plt.xlabel('B, Tesla')
    #     return

    # def run_ramp(self, dvm_visa):
    #     while True:
    #         t = dt.datetime.now().strftime('%H:%M:%S')
    #         self.times.append(t)
    #         v = dvm_visa.read()
    #         self.Vs.append(v)
    #         field = self.get_field()
    #         self.Bs.append(field)
    #         self.plot_data()
    #         print(f'{t}\t{v} V; {field} T')
    #         if self.ramp_finished():
    #             print('BREAKING RAMP LOOP.')
    #             plt.show()  # Steals thread focus!!
    #             break
    #     return

    # def plot_data(self):
    #     self.ax.clear()
    #     self.ax.plot(self.Bs, self.Vs, 'b.')
    #     plt.xticks(ha='center')  # (rotation=45, ha='right') (ha = horizontal alignment)
    #     plt.subplots_adjust(bottom=0.30)
    #     plt.title(f'Vxy vs B-field')
    #     plt.ylabel('Vxy')
    #     plt.xlabel('B, Tesla')


"""
Useful functions _________________________________________
"""


def gpibaddr_str2num(addr_str):  #
    return addr_str[7:addr_str.find('::INSTR')]


def gpibaddr_num2str(addr):
    return f'GPIB0::{addr}::INSTR'
# _____________________________________________________________
