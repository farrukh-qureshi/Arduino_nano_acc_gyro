import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pywt

df = pd.read_csv('imu_data_20241114_090710.csv')
print(df.head(10))

df['Time'] = pd.to_datetime(df['Time'], unit='s')

# Normalize all data to -1 and 1
for col in df.columns[1:]:
    df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min()) * 2 - 1

initial_time = 0
duration = 60
final_time = initial_time + duration

wavelet = 'morl'  # Choosing a wavelet type
scales = np.arange(1, 128, 0.1)

# Plot only 2 seconds
df = df[df['Time'] >= df['Time'].min() + pd.Timedelta(seconds=initial_time)]
df = df[df['Time'] <= df['Time'].min() + pd.Timedelta(seconds=final_time)]

# Plot X-Accel signal
figure, axis = plt.subplots(2, 1, sharex=True)
axis[0].plot(df['Time'], df['X-Accel'], label='X')
axis[0].legend()
axis[0].set_xlabel('Time (s)')
axis[0].set_ylabel('Acceleration (m/s^2)')
axis[0].set_title('IMU Data')

# Plot X-Accel scalogram
coefficients, frequencies = pywt.cwt(df['X-Accel'], scales, wavelet)

axis[1].imshow(np.abs(coefficients), extent=(df['Time'].min(), df['Time'].max(), scales[0], scales[-1]), aspect='auto', cmap='Reds')
axis[1].set_xlabel('Time (s)')
axis[1].set_ylabel('Scale')
axis[1].set_title('Scalogram of X-Accel')

plt.tight_layout()
plt.show(block=False)

# Plot Y-Accel signal
figure, axis = plt.subplots(2, 1, sharex=True)
axis[0].plot(df['Time'], df['Y-Accel'], label='Y')
axis[0].legend()
axis[0].set_xlabel('Time (s)')
axis[0].set_ylabel('Acceleration (m/s^2)')
axis[0].set_title('IMU Data')

# Plot Y-Accel scalogram
coefficients, frequencies = pywt.cwt(df['Y-Accel'], scales, wavelet)

axis[1].imshow(np.abs(coefficients), extent=(df['Time'].min(), df['Time'].max(), scales[0], scales[-1]), aspect='auto', cmap='Greens')
axis[1].set_xlabel('Time (s)')
axis[1].set_ylabel('Scale')
axis[1].set_title('Scalogram of Y-Accel')

plt.tight_layout()
plt.show(block=False)

# Plot Z-Accel signal
figure, axis = plt.subplots(2, 1, sharex=True)
axis[0].plot(df['Time'], df['Z-Accel'], label='Z')
axis[0].legend()
axis[0].set_xlabel('Time (s)')
axis[0].set_ylabel('Acceleration (m/s^2)')
axis[0].set_title('IMU Data')

# Plot Z-Accel scalogram
coefficients, frequencies = pywt.cwt(df['Z-Accel'], scales, wavelet)

axis[1].imshow(np.abs(coefficients), extent=(df['Time'].min(), df['Time'].max(), scales[0], scales[-1]), aspect='auto', cmap='Blues')
axis[1].set_xlabel('Time (s)')
axis[1].set_ylabel('Scale')
axis[1].set_title('Scalogram of Z-Accel')

plt.tight_layout()
plt.show(block=False)

# Plot all 3 signals
figure, axis = plt.subplots(2, 1, sharex=True)
axis[0].plot(df['Time'], df['X-Accel'], label='X')
axis[0].plot(df['Time'], df['Y-Accel'], label='Y')
axis[0].plot(df['Time'], df['Z-Accel'], label='Z')
axis[0].legend()
axis[0].set_xlabel('Time (s)')
axis[0].set_ylabel('Acceleration (m/s^2)')
axis[0].set_title('IMU Data')

# Plot all 3 spectrograms overlaid
coefficients_x, frequencies_x = pywt.cwt(df['X-Accel'], scales, wavelet)
coefficients_y, frequencies_y = pywt.cwt(df['Y-Accel'], scales, wavelet)
coefficients_z, frequencies_z = pywt.cwt(df['Z-Accel'], scales, wavelet)

# axis[1].imshow(np.abs(coefficients_x + coefficients_y + coefficients_z), extent=(df['Time'].min(), df['Time'].max(), scales[0], scales[-1]), aspect='auto', cmap='inferno')
axis[1].imshow(np.abs(coefficients_x + coefficients_y + coefficients_z), extent=(df['Time'].min(), df['Time'].max(), scales[0], scales[-1]), aspect='auto', cmap='jet', vmin=0, vmax=0.5)
axis[1].set_xlabel('Time (s)')
axis[1].set_ylabel('Scale')
axis[1].set_title('Overlaid Scalograms of X, Y, and Z')

plt.tight_layout()
plt.show()
