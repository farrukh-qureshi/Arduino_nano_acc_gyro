import serial
import numpy as np
import pywt
from collections import deque
from PyQt5 import QtWidgets
import pyqtgraph as pg
from collections import deque


# Serial port configuration
port = '/dev/ttyUSB0'  # Replace 'COM3' with your Arduino's port
baud_rate = 115200
ser = serial.Serial(port, baud_rate)

# Initialize data deque for faster appending and popping
window_size = 1  # seconds
sampling_rate = 100  # Hz
maxlen = int(window_size * sampling_rate)

x_data = deque(maxlen=maxlen)

# Create PyQt application
app = QtWidgets.QApplication([])

# Create a window
win = pg.GraphicsLayoutWidget(show=True, title="Real-time Data Plot")
win.resize(1000, 600)
win.setWindowTitle('PyQtGraph Real-time Plot')

# Enable anti-aliasing for prettier plots
pg.setConfigOptions(antialias=True)

# Time-domain plot
p1 = win.addPlot(title="Time-domain Data")
p1.setLabel('bottom', 'Time', 's')
p1.setLabel('left', 'Acceleration', 'm/s^2')
curve1 = p1.plot(pen='y')

# Scalogram plot
win.nextRow()
p2 = win.addPlot(title="Scalogram")
p2.setLabel('bottom', 'Time', 's')
p2.setLabel('left', 'Scale', 'Hz')
img = pg.ImageItem()
p2.addItem(img)

def update_plot():
    # Read data from Arduino
    line = ser.readline().decode().strip()

    # Check if line is empty
    if not line:
        return

    # Parse data
    try:
        data = [float(x) for x in line.split(',')]
    except ValueError:
        print("Error parsing data:", line)
        return

    # Update data deque
    x_acc = data[0]
    x_data.append(x_acc)

    # Update time-domain plot
    curve1.setData(np.arange(len(x_data)) / sampling_rate, x_data)

    # Calculate the scalogram
    widths = np.arange(1, 50)  # Adjust range as needed
    coefficients, frequencies = pywt.cwt(x_data, widths, 'morl', sampling_period=1 / sampling_rate)
        
    scalogram_abs = np.abs(coefficients)
    img.setImage(scalogram_abs, levels=(0, np.max(scalogram_abs)), lut=pg.colormap.get('inferno').getLookupTable())

    # Scale the image to fit the plot area
    img.setScale(0, 1)

# Timer to repeatedly call update_plot
timer = pg.QtCore.QTimer()
timer.timeout.connect(update_plot)
timer.start(1000 // sampling_rate)

# Start Qt event loop
QtWidgets.QApplication.instance().exec_()

