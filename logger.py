

# import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
# import tmp102

# Create figure for plotting and lists for accumulating the data:
fig = plt.figure()  # Global
ax = fig.add_subplot(1, 1, 1)  # (nrows, ncols, index). Global
xs = [0]  # Global
ys = [0]  # Global

# Initialize communication with TMP102
# tmp102.init()


# This function is called periodically from FuncAnimation
def animate(i, xs, ys):

    # Read data from magnet I-supply and meter
    mag_ramp_rate = 0.1  # Tesla/second
    mag = xs[-1] + mag_ramp_rate
    Vxy = (5**mag - 5**-mag)/(5**mag + 5**-mag)

    # temp_c = round(tmp102.read_temp(), 2)

    # Add x and y to lists
    # xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    xs.append(mag)
    ys.append(Vxy)  # ys.append(temp_c)

    # Limit x and y lists to last 50 items
    xs = xs[-50:]
    ys = ys[-50:]

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys)

    # Format plot
    plt.xticks(ha='center')  # (rotation=45, ha='right') (ha = horizontal alignment)
    plt.subplots_adjust(bottom=0.30)
    plt.title(f'Plotting point {i}')
    plt.ylabel('Vxy')
    plt.xlabel('B, Tesla')


# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=500)
if len(xs) > 10:
    ani.pause()

plt.pause(100)  # Display plot for 10s.
# plt.show()
