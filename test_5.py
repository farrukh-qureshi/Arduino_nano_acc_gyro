import serial
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from collections import deque
import time

class RealtimeRGBScalogram:
    def __init__(self, port='/dev/ttyUSB0', baud_rate=115200, buffer_size=500):
        # Initialize serial connection
        self.ser = serial.Serial(port, baud_rate)
        self.buffer_size = buffer_size
        self.signal_names = ['X-Accel', 'Y-Accel', 'Z-Accel', 'X-Gyro', 'Y-Gyro', 'Z-Gyro']
        
        # Create data buffers for all signals
        self.signal_buffers = [deque(maxlen=buffer_size) for _ in range(6)]
        self.time_buffer = deque(maxlen=buffer_size)
        
        # Setup wavelet parameters
        self.widths = np.arange(1, 31)  # Increased scale range for better visualization
        
        # Initialize plot
        plt.ion()  # Enable interactive mode
        self.fig = plt.figure(figsize=(15, 12))
        self.gs = self.fig.add_gridspec(3, 2, height_ratios=[1, 1, 1])
        
        # Time series plots
        self.ax_signals = self.fig.add_subplot(self.gs[0, :])
        self.ax_individual = [
            self.fig.add_subplot(self.gs[1, 0]),
            self.fig.add_subplot(self.gs[1, 1]),
            self.fig.add_subplot(self.gs[2, 0])
        ]
        self.ax_combined = self.fig.add_subplot(self.gs[2, 1])
        
        self.fig.tight_layout(pad=3.0)
        
        # Initialize time series plots
        self.lines = [
            self.ax_signals.plot([], [], label=name, alpha=0.7)[0]
            for name in self.signal_names[:3]  # Only X, Y, Z signals
        ]
        
        # Setup time series plot
        self.ax_signals.set_title('Real-time Signals')
        self.ax_signals.set_xlabel('Time (s)')
        self.ax_signals.set_ylabel('Magnitude')
        self.ax_signals.set_ylim(-38000, 38000)
        self.ax_signals.grid(True)
        self.ax_signals.legend()
        
        # Initialize individual scalogram plots
        self.scalogram_plots = []
        colors = ['Reds', 'Greens', 'Blues']
        for ax, color, name in zip(self.ax_individual, colors, self.signal_names[:3]):
            plot = ax.imshow(
                np.zeros((len(self.widths), buffer_size)),
                aspect='auto',
                cmap=color,
                extent=[0, buffer_size, 1, len(self.widths)],
                vmin=-38000,
                vmax=38000
            )
            self.scalogram_plots.append(plot)
            ax.set_title(f'Scalogram - {name}')
            ax.set_xlabel('Time')
            ax.set_ylabel('Scale')
        
        # Initialize combined RGB scalogram plot
        self.combined_plot = self.ax_combined.imshow(
            np.zeros((len(self.widths), buffer_size, 3)),
            aspect='auto',
            extent=[0, buffer_size, 1, len(self.widths)]
        )
        self.ax_combined.set_title('Combined RGB Scalogram')
        self.ax_combined.set_xlabel('Time')
        self.ax_combined.set_ylabel('Scale')
        
        self.start_time = time.time()

    def read_sensor_data(self):
        """Read one line of sensor data and return the last 3 values"""
        try:
            line = self.ser.readline().decode('utf-8').strip()
            values = [float(x) for x in line.split(',')]
            if len(values) >= 3:
                return values[-3:]
            return None
        except:
            return None

    def update_scalograms(self):
        """Compute and update all scalograms"""
        if len(self.signal_buffers[0]) >= self.buffer_size:
            # Compute CWT for each signal and update individual plots
            cwts = []
            for i in range(3):  # Only X, Y, Z signals
                signal_array = np.array(list(self.signal_buffers[i]))
                cwt = np.abs(signal.cwt(signal_array, signal.ricker, self.widths))
                cwts.append(cwt)
                self.scalogram_plots[i].set_array(cwt)
            
            # Create combined RGB image
            # Normalize each CWT to [0, 1] range for RGB combination
            rgb_image = np.zeros((len(self.widths), self.buffer_size, 3))
            for i, cwt in enumerate(cwts):
                normalized_cwt = (cwt - cwt.min()) / (cwt.max() - cwt.min())
                rgb_image[:, :, i] = normalized_cwt
            
            # Update combined plot
            self.combined_plot.set_array(rgb_image)

    def run(self):
        """Main loop for real-time visualization"""
        try:
            while True:
                values = self.read_sensor_data()
                if values is not None:
                    current_time = time.time() - self.start_time
                    
                    # Update all buffers
                    for i, value in enumerate(values):
                        self.signal_buffers[i].append(value)
                    self.time_buffer.append(current_time)
                    
                    # Update time series plots
                    for i, line in enumerate(self.lines):
                        line.set_data(
                            list(self.time_buffer),
                            list(self.signal_buffers[i])
                        )
                    
                    # Update x-axis limits
                    self.ax_signals.set_xlim(min(self.time_buffer), max(self.time_buffer))
                    
                    # Update scalograms
                    self.update_scalograms()
                    
                    # Refresh display
                    self.fig.canvas.draw()
                    self.fig.canvas.flush_events()
                    
        except KeyboardInterrupt:
            print("Stopping visualization...")
            self.ser.close()
            plt.ioff()
            plt.close()

if __name__ == "__main__":
    visualizer = RealtimeRGBScalogram(
        port='/dev/ttyUSB0',  # Change this to match your Arduino's port
        baud_rate=115200,     # Match this with your Arduino's baud rate
        buffer_size=50        # Adjust buffer size as needed
    )
    visualizer.run()