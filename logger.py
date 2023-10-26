

import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# Create figure for plotting and lists for accumulating the data:
# fig = plt.figure()  # Global
# ax = fig.add_subplot(1, 1, 1)  # (nrows, ncols, index). Global
# xs = [0]  # range(0, 5, 0.1)  # Global
# ys = [0]  # Global


# This function is called periodically from FuncAnimation
# def animate(i, xs, ys):
#
#     # Read data from magnet I-supply and meter
#     mag_ramp_rate = 0.1  # Tesla/second
#     mag = xs[-1] + mag_ramp_rate
#     Vxy = (5**mag - 5**-mag)/(5**mag + 5**-mag)
#
#     # Add x and y to lists
#     # xs.append(dt.datetime.now().strftime('%H:%M:%S'))
#     xs.append(mag)
#     ys.append(Vxy)  # ys.append(temp_c)
#
#     # Limit x and y lists to last 50 items
#     # xs = xs[-50:]
#     # ys = ys[-50:]
#
#     # Draw x and y lists
#     ax.clear()
#     ax.plot(xs, ys)
#
#     # Format plot
#     plt.xticks(ha='center')  # (rotation=45, ha='right') (ha = horizontal alignment)
#     plt.subplots_adjust(bottom=0.30)
#     plt.title(f'Plotting point {i}')
#     plt.ylabel('Vxy')
#     plt.xlabel('B, Tesla')
#
#     if i >= 50:
#         print(f'STOP:i = {i}')
#         return


# Set up plot to call animate() function periodically
# ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), frames=50, interval=500)
# plt.show()

# __________________Alternative example_______________________

fig, ax = plt.subplots()
t = np.linspace(0, 3, 40)
g = -9.81
v0 = 12
z = g * t**2 / 2 + v0 * t

# v02 = 5
# z2 = g/2 * t**2 + v02 * t

scat = ax.scatter(t[0], z[0], c="b", s=1, label=f'v0 = {v0} m/s')
# line2 = ax.plot(t[0], z2[0], label=f'v0 = {v02} m/s')[0]
ax.set(xlim=[0, 3], ylim=[-4, 10], xlabel='Time [s]', ylabel='Z [m]')
ax.legend()


def update(frame):
    # for each frame, update the data stored on each artist.
    x = t[:frame]
    y = z[:frame]
    # update the scatter plot:
    data = np.stack([x, y]).T
    scat.set_offsets(data)  # what does this do?
    # update the line plot:
    # line2.set_xdata(t[:frame])
    # line2.set_ydata(z2[:frame])
    return scat  # , line2


ani = animation.FuncAnimation(fig=fig, func=update, frames=40, interval=30, repeat=False)

plt.show()
