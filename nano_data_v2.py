import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import time
import numpy as np
import matplotlib.animation as animation
import pywt

# Serial port configuration
port = '/dev/ttyUSB0'  # Replace 'COM3' with your Arduino's port
baud_rate = 115200
ser = serial.Serial(port, baud_rate)

# Initialize data deque for faster appending and popping
window_size = 1  # seconds
sampling_rate = 10 / 1000  # 33 ms per sample
maxlen = int(window_size / sampling_rate)

ax_data, ay_data, az_data = deque(maxlen=maxlen), deque(maxlen=maxlen), deque(maxlen=maxlen)
gx_data, gy_data, gz_data = deque(maxlen=maxlen), deque(maxlen=maxlen), deque(maxlen=maxlen)

# Set up the plot
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
ax1.set_title("Accelerometer Data")
ax1.set_ylim(-32768, 32768)  # MPU6050 output range for accelerometer
ax1.set_xlim(0, maxlen)      # Display last 2 seconds of data
ax2.set_title("Gyroscope Data")
ax2.set_ylim(-32768, 32768)  # MPU6050 output range for gyroscope
ax2.set_xlim(0, maxlen)      # Display last 2 seconds of data
ax3.set_title("Scalogram")

line1, = ax1.plot([], [], label='Ax')
line2, = ax1.plot([], [], label='Ay')
line3, = ax1.plot([], [], label='Az')
line4, = ax2.plot([], [], label='Gx')
line5, = ax2.plot([], [], label='Gy')
line6, = ax2.plot([], [], label='Gz')

ax1.legend(loc="upper right")
ax2.legend(loc="upper right")

# Update function for real-time plotting
def update(frame):
    line = ser.readline().decode('utf-8').strip()
    data = line.split(',')
    
    if len(data) == 6:
        gx, gy, gz, ax, ay, az = map(int, data)
        
        # Append new data to deques
        ax_data.append(ax)
        ay_data.append(ay)
        az_data.append(az)
        gx_data.append(gx)
        gy_data.append(gy)
        gz_data.append(gz)

        # Update line data
        line1.set_data(range(len(ax_data)), ax_data)
        line2.set_data(range(len(ay_data)), ay_data)
        line3.set_data(range(len(az_data)), az_data)
        line4.set_data(range(len(gx_data)), gx_data)
        line5.set_data(range(len(gy_data)), gy_data)
        line6.set_data(range(len(gz_data)), gz_data)

        # Update scalogram every 0.5 seconds
        if frame % int(0.5 / (10 / 1000)) == 0:  # Assuming interval=10ms
            scales = np.arange(1, 128)
            coefficients, freqs = pywt.cwt(np.array(ax_data), scales, 'morl', sampling_period=10)
            img = ax3.imshow(np.abs(coefficients), cmap='inferno', aspect='auto', extent=(0, window_size, 1, 128))
            ax3.set_xlabel("Time (s)")
            ax3.set_ylabel("Scale")
            img.set_clim(vmin=0, vmax=np.max(np.abs(coefficients)))  # Set clim to ensure colorbar is updated

    return line1, line2, line3, line4, line5, line6

# Set up the animation
ani = FuncAnimation(fig, update, interval=10, blit=True, cache_frame_data=False)

plt.tight_layout()
plt.show()


