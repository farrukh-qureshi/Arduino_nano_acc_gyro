import serial
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from collections import deque
import time

class RealtimeScalogram:
    def __init__(self, port='/dev/ttyUSB0', baud_rate=115200, buffer_size=500, signal_index=0):
        # Initialize serial connection
        self.ser = serial.Serial(port, baud_rate)
        self.buffer_size = buffer_size
        self.signal_index = signal_index  # Index of the signal to plot (0-5)
        self.signal_names = ['X-Accel', 'Y-Accel', 'Z-Accel', 'X-Gyro', 'Y-Gyro', 'Z-Gyro']
        
        # Create data buffers for all signals
        self.signal_buffers = [deque(maxlen=buffer_size) for _ in range(6)]
        self.time_buffer = deque(maxlen=buffer_size)
        
        # Setup wavelet parameters
        self.widths = np.arange(1, 10)  # Scale parameters for CWT
        
        # Initialize plot
        plt.ion()  # Enable interactive mode
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self.fig.tight_layout(pad=3.0)
        
        # Initialize line objects with fixed y-axis limits
        self.line_signal, = self.ax1.plot([], [], 'b-', 
                                        label=f'{self.signal_names[signal_index]}')
        self.ax1.set_title(f'Real-time {self.signal_names[signal_index]}')
        self.ax1.set_xlabel('Time (s)')
        self.ax1.set_ylabel('Magnitude')
        self.ax1.set_ylim(-38000, 38000)  # Set fixed y-axis limits
        self.ax1.grid(True)
        self.ax1.legend()
        
        # Initialize scalogram plot
        self.scalogram_plot = self.ax2.imshow(
            np.zeros((len(self.widths), buffer_size)),
            aspect='auto',
            cmap='Reds',
            extent=[0, buffer_size, 1, len(self.widths)],  # Set extent for proper scaling
            vmin=-38000,  # Set fixed color scale limits
            vmax=38000
        )
        self.ax2.set_title(f'Scalogram (CWT) - {self.signal_names[signal_index]}')
        self.ax2.set_xlabel('Time')
        self.ax2.set_ylabel('Scale')
        # plt.colorbar(self.scalogram_plot, ax=self.ax2)
        
        self.start_time = time.time()

    def read_sensor_data(self):
        """Read one line of sensor data and return all six values"""
        try:
            line = self.ser.readline().decode('utf-8').strip()
            # Parse comma-separated values: ax,ay,az,gx,gy,gz
            values = [float(x) for x in line.split(',')]
            if len(values) == 6:  # Ensure we have all 6 values
                return values
            return None
        except:
            return None

    def update_scalogram(self):
        """Compute and update the scalogram"""
        if len(self.signal_buffers[self.signal_index]) >= self.buffer_size:
            # Compute CWT
            signal_array = np.array(list(self.signal_buffers[self.signal_index]))
            cwt = signal.cwt(signal_array, signal.ricker, self.widths)
            
            # Update scalogram plot with fixed color scale
            self.scalogram_plot.set_array(np.abs(cwt))

    def set_signal_to_plot(self, index):
        """Change which signal to plot"""
        if 0 <= index < 6:
            self.signal_index = index
            # Update plot titles and labels
            self.line_signal.set_label(self.signal_names[index])
            self.ax1.set_title(f'Real-time {self.signal_names[index]}')
            self.ax2.set_title(f'Scalogram (CWT) - {self.signal_names[index]}')
            self.ax1.legend()
            
            # Maintain fixed axis limits
            self.ax1.set_ylim(-38000, 38000)
            self.scalogram_plot.set_clim(vmin=-38000, vmax=38000)

    def run(self):
        """Main loop for real-time visualization"""
        try:
            while True:
                # Read sensor data
                values = self.read_sensor_data()
                if values is not None:
                    current_time = time.time() - self.start_time
                    
                    # Update all buffers
                    for i, value in enumerate(values):
                        self.signal_buffers[i].append(value)
                    self.time_buffer.append(current_time)
                    
                    # Update signal plot for selected signal
                    self.line_signal.set_data(
                        list(self.time_buffer), 
                        list(self.signal_buffers[self.signal_index])
                    )
                    
                    # Update x-axis limits without changing y-axis limits
                    self.ax1.set_xlim(min(self.time_buffer), max(self.time_buffer))
                    
                    # Update scalogram
                    self.update_scalogram()
                    
                    # Refresh display
                    self.fig.canvas.draw()
                    self.fig.canvas.flush_events()
                    
        except KeyboardInterrupt:
            print("Stopping visualization...")
            self.ser.close()
            plt.ioff()
            plt.close()

if __name__ == "__main__":
    # Create and run the visualization
    visualizer = RealtimeScalogram(
        port='/dev/ttyUSB0',  # Change this to match your Arduino's port
        baud_rate=115200,     # Match this with your Arduino's baud rate
        buffer_size=50,       # Adjust buffer size as needed
        signal_index=3        # Initial signal to plot (0=ax, 1=ay, 2=az, 3=gx, 4=gy, 5=gz)
    )
    visualizer.run()