import serial
import time
import csv
import datetime
import numpy as np

class IMUDataLogger:
    def __init__(self, port='/dev/ttyUSB0', baud_rate=115200, duration=60):
        """
        Initialize the IMU data logger
        
        Args:
            port (str): Serial port
            baud_rate (int): Baud rate
            duration (int): Recording duration in seconds
        """
        self.port = port
        self.baud_rate = baud_rate
        self.duration = duration
        # Corrected signal names order: first 3 are gyro, last 3 are accelerometer
        self.signal_names = ['X-Gyro', 'Y-Gyro', 'Z-Gyro', 'X-Accel', 'Y-Accel', 'Z-Accel']
        self.data = []
        self.timestamps = []
        
    def read_sensor_data(self):
        """Read one line of sensor data and return all six values"""
        try:
            line = self.ser.readline().decode('utf-8').strip()
            values = [float(x) for x in line.split(',')]
            if len(values) == 6:  # Ensure we have all 6 values
                return values  # Values are already in correct order from Arduino
            return None
        except:
            return None
    
    def collect_data(self):
        """Collect data for specified duration"""
        print(f"Starting data collection for {self.duration} seconds...")
        print("Recording format: X-Gyro, Y-Gyro, Z-Gyro, X-Accel, Y-Accel, Z-Accel")
        
        try:
            # Open serial connection
            self.ser = serial.Serial(self.port, self.baud_rate)
            time.sleep(1)  # Wait for connection to stabilize
            
            start_time = time.time()
            sample_count = 0
            
            # Collect data until duration is reached
            while (time.time() - start_time) < self.duration:
                values = self.read_sensor_data()
                
                if values is not None:
                    current_time = time.time() - start_time
                    self.timestamps.append(current_time)
                    self.data.append(values)
                    sample_count += 1
                    
                    # Print progress every second
                    if sample_count % 100 == 0:
                        elapsed = time.time() - start_time
                        print(f"Time elapsed: {elapsed:.1f}s, Samples: {sample_count}")
            
            # Calculate sampling rate
            total_time = time.time() - start_time
            sampling_rate = sample_count / total_time
            print(f"\nData collection complete!")
            print(f"Collected {sample_count} samples in {total_time:.1f} seconds")
            print(f"Average sampling rate: {sampling_rate:.1f} Hz")
            
        except KeyboardInterrupt:
            print("\nData collection interrupted by user")
        finally:
            self.ser.close()
    
    def save_data(self, folder_path='.'):
        """Save collected data to CSV file"""
        if not self.data:
            print("No data to save!")
            return
        
        # Create filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{folder_path}/imu_data_{timestamp}.csv"
        
        # Save data to CSV
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            
            # Write header
            header = ['Time'] + self.signal_names
            writer.writerow(header)
            
            # Write data rows
            for t, values in zip(self.timestamps, self.data):
                row = [f"{t:.3f}"] + [f"{v:.2f}" for v in values]
                writer.writerow(row)
        
        print(f"\nData saved to: {filename}")
        
        # Calculate and save statistics
        stats_filename = f"{folder_path}/imu_stats_{timestamp}.txt"
        self.save_statistics(stats_filename)
    
    def save_statistics(self, filename):
        """Calculate and save basic statistics of the collected data"""
        data_array = np.array(self.data)
        
        with open(filename, 'w') as file:
            file.write("IMU Data Statistics\n")
            file.write("==================\n\n")
            
            # Time statistics
            file.write("Timing Information:\n")
            file.write(f"Total duration: {self.timestamps[-1]:.2f} seconds\n")
            file.write(f"Total samples: {len(self.data)}\n")
            file.write(f"Average sampling rate: {len(self.data)/self.timestamps[-1]:.2f} Hz\n\n")
            
            # Data statistics for each signal
            file.write("Signal Statistics:\n")
            file.write("\nGYROSCOPE DATA:\n")
            for i in range(3):  # First 3 signals are gyro
                signal_data = data_array[:, i]
                file.write(f"\n{self.signal_names[i]}:\n")
                file.write(f"  Mean: {np.mean(signal_data):.2f}\n")
                file.write(f"  Std Dev: {np.std(signal_data):.2f}\n")
                file.write(f"  Min: {np.min(signal_data):.2f}\n")
                file.write(f"  Max: {np.max(signal_data):.2f}\n")
            
            file.write("\nACCELEROMETER DATA:\n")
            for i in range(3, 6):  # Last 3 signals are accelerometer
                signal_data = data_array[:, i]
                file.write(f"\n{self.signal_names[i]}:\n")
                file.write(f"  Mean: {np.mean(signal_data):.2f}\n")
                file.write(f"  Std Dev: {np.std(signal_data):.2f}\n")
                file.write(f"  Min: {np.min(signal_data):.2f}\n")
                file.write(f"  Max: {np.max(signal_data):.2f}\n")
        
        print(f"Statistics saved to: {filename}")

def main():
    # Create and run the data logger
    logger = IMUDataLogger(
        port='/dev/ttyUSB0',    # Change this to match your Arduino's port
        baud_rate=115200,       # Match this with your Arduino's baud rate
        duration=60             # Data collection duration in seconds
    )
    
    # Collect data
    logger.collect_data()
    
    # Save data and statistics
    logger.save_data()

if __name__ == "__main__":
    main()