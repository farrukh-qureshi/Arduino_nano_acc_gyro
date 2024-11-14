import serial
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from collections import deque
import time

class MultiAxisScalogram:
    def __init__(self, port='/dev/ttyUSB0', baud_rate=115200, buffer_size=500):
        # Initialize serial connection
        self.ser = serial.Serial(port, baud_rate)
        self.buffer_size = buffer_size
        
        # Create data buffers for all axes
        self.accel_buffers = {
            'x': deque(maxlen=buffer_size),
            'y': deque(maxlen=buffer_size),
            'z': deque(maxlen=buffer_size)
        }
        self.time_buffer = deque(maxlen=buffer_size)
        
        # Setup wavelet parameters
        self.widths = np.arange(1, 31)
        
        # Color maps for each axis
        self.cmaps = {
            'x': plt.cm.Reds,
            'y': plt.cm.Greens,
            'z': plt.cm.Blues
        }
        
        # Initialize plot
        plt.ion()
        self.fig = plt.figure(figsize=(12, 15))
        self.gs = self.fig.add_gridspec(5, 1)
        
        # Create subplots
        self.ax_signals = self.fig.add_subplot(self.gs[0])  # All signals
        self.ax_scalogram_x = self.fig.add_subplot(self.gs[1])  # X scalogram
        self.ax_scalogram_y = self.fig.add_subplot(self.gs[2])  # Y scalogram
        self.ax_scalogram_z = self.fig.add_subplot(self.gs[3])  # Z scalogram
        self.ax_combined = self.fig.add_subplot(self.gs[4])  # Combined scalogram
        
        # Initialize line objects for signals
        self.lines = {
            'x': self.ax_signals.plot([], [], 'r-', label='X-axis')[0],
            'y': self.ax_signals.plot([], [], 'g-', label='Y-axis')[0],
            'z': self.ax_signals.plot([], [], 'b-', label='Z-axis')[0]
        }
        
        # Setup signal plot
        self.ax_signals.set_title('Real-time Acceleration Signals')
        self.ax_signals.set_xlabel('Time (s)')
        self.ax_signals.set_ylabel('Acceleration')
        self.ax_signals.grid(True)
        self.ax_signals.legend()
        
        # Initialize scalogram plots
        self.scalogram_plots = {
            'x': self.ax_scalogram_x.imshow(np.zeros((len(self.widths), buffer_size)), 
                                          aspect='auto', cmap=self.cmaps['x']),
            'y': self.ax_scalogram_y.imshow(np.zeros((len(self.widths), buffer_size)), 
                                          aspect='auto', cmap=self.cmaps['y']),
            'z': self.ax_scalogram_z.imshow(np.zeros((len(self.widths), buffer_size)), 
                                          aspect='auto', cmap=self.cmaps['z'])
        }
        
        # Setup individual scalogram plots
        for ax, axis in zip([self.ax_scalogram_x, self.ax_scalogram_y, self.ax_scalogram_z], 
                          ['X', 'Y', 'Z']):
            ax.set_title(f'{axis}-axis Scalogram')
            ax.set_xlabel('Time')
            ax.set_ylabel('Scale')
            plt.colorbar(self.scalogram_plots[axis.lower()], ax=ax)
        
        # Initialize combined scalogram plot
        self.combined_plot = self.ax_combined.imshow(np.zeros((len(self.widths), buffer_size, 3)), 
                                                   aspect='auto')
        self.ax_combined.set_title('Combined RGB Scalogram')
        self.ax_combined.set_xlabel('Time')
        self.ax_combined.set_ylabel('Scale')
        
        self.fig.tight_layout(pad=2.0)
        self.start_time = time.time()

    def read_sensor_data(self):
        """Read one line of sensor data and extract acceleration values"""
        try:
            line = self.ser.readline().decode('utf-8').strip()
            values = [float(x) for x in line.split(',')]
            return values[0:3]  # Return x, y, z acceleration
        except:
            return None

    def update_scalograms(self):
        """Compute and update all scalograms"""
        if len(self.time_buffer) >= self.buffer_size:
            # Initialize combined RGB array
            combined_cwt = np.zeros((len(self.widths), self.buffer_size, 3))
            
            # Compute CWT for each axis
            for i, axis in enumerate(['x', 'y', 'z']):
                signal_array = np.array(list(self.accel_buffers[axis]))
                cwt = signal.cwt(signal_array, signal.ricker, self.widths)
                cwt_normalized = np.abs(cwt) / np.abs(cwt).max()
                
                # Update individual scalogram
                self.scalogram_plots[axis].set_array(cwt_normalized)
                
                # Add to combined RGB scalogram
                combined_cwt[:, :, i] = cwt_normalized
            
            # Update combined scalogram
            self.combined_plot.set_array(combined_cwt)

    def run(self):
        """Main loop for real-time visualization"""
        try:
            while True:
                # Read sensor data
                accel_data = self.read_sensor_data()
                if accel_data is not None:
                    current_time = time.time() - self.start_time
                    
                    # Update buffers
                    self.time_buffer.append(current_time)
                    for i, axis in enumerate(['x', 'y', 'z']):
                        self.accel_buffers[axis].append(accel_data[i])
                    
                    # Update signal plots
                    for axis in ['x', 'y', 'z']:
                        self.lines[axis].set_data(list(self.time_buffer), 
                                                list(self.accel_buffers[axis]))
                    
                    # Auto-scale signal plot
                    self.ax_signals.relim()
                    self.ax_signals.autoscale_view()
                    
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
    # Create and run the visualization
    visualizer = MultiAxisScalogram(
        port='/dev/ttyUSB0',  # Change this to match your Arduino's port
        baud_rate=115200,     # Match this with your Arduino's baud rate
        buffer_size=250       # Adjust buffer size as needed
    )
    visualizer.run()