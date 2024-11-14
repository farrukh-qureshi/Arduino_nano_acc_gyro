import numpy as np
import matplotlib.pyplot as plt
import pywt
import scipy.signal

# Parameters for signal generation
fs = 1000  # Sampling frequency (samples per second)
t = np.linspace(0, 2, 2 * fs, endpoint=False)  # Time vector for 2 seconds

# Generate a random signal
np.random.seed(0)  # For reproducibility
signal = np.random.randn(len(t))

# Perform Continuous Wavelet Transform (CWT)
scales = np.arange(1, 128)  # Scale range
coefficients, frequencies = pywt.cwt(signal, scales, 'morl', sampling_period=1/fs)

# Plot the signal and its scalogram
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Plot the original signal
ax1.plot(t, signal)
ax1.set_title('Random Signal')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Amplitude')

# Plot the scalogram
im = ax2.imshow(np.abs(coefficients), extent=[0, 2, 1, 128], cmap='jet', aspect='auto',
                vmax=np.max(np.abs(coefficients)), vmin=0)
ax2.set_title('Scalogram (CWT)')
ax2.set_xlabel('Time [s]')
ax2.set_ylabel('Scale')
# fig.colorbar(im, ax=ax2, orientation='vertical', label='Magnitude')

plt.tight_layout()
plt.show()
