#!/usr/bin/env python3
"""
Compare fast-rising and slow-rising sim-EPSP waveforms.

Units:
- Time: seconds (s)
- Current: picoamperes (pA)
- Tau parameters in function calls: seconds (s)
- Command-line style parameters: milliseconds (ms), converted to s
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Fast-rising (double exponential)
def fast_epsp(t, A1=150, tau_rise1=0.01, tau_decay1=1.0, A2=70, tau_rise2=3.0, tau_decay2=20.0):
    """
    Parameters:
    t: time in seconds
    A1, A2: amplitudes in pA
    tau_rise1, tau_decay1, tau_rise2, tau_decay2: time constants in seconds
    """
    component1 = A1 * (1 - np.exp(-t / tau_rise1)) * np.exp(-t / tau_decay1)
    component2 = A2 * (1 - np.exp(-t / tau_rise2)) * np.exp(-t / tau_decay2)
    y = component1 + component2
    y[t < 0] = 0
    return y

# Slow-rising (single exponential)
def slow_epsp(t, A=150, tau_rise=10.0, tau_decay=15.0):
    """
    Parameters:
    t: time in seconds
    A: amplitude in pA
    tau_rise, tau_decay: time constants in seconds
    """
    y = A * (1 - np.exp(-t / tau_rise)) * np.exp(-t / tau_decay)
    y[t < 0] = 0
    return y

# Generate time arrays (in seconds)
sampling_rate = 20000  # Hz (20 kHz)
dt = 1.0 / sampling_rate  # seconds
duration = 0.100  # seconds (100 ms)
time = np.arange(0, duration, dt)

# Parameters in milliseconds (as used in the paper)
A1_pA = 150
A2_pA = 70
tau_rise1_ms = 0.01
tau_decay1_ms = 1.0
tau_rise2_ms = 3.0
tau_decay2_ms = 20.0

A_slow_pA = 150
tau_rise_slow_ms = 10.0
tau_decay_slow_ms = 15.0

# Calculate currents (converting tau from ms to s)
current_fast = fast_epsp(time,
                        A1=A1_pA, A2=A2_pA,
                        tau_rise1=tau_rise1_ms/1000, tau_decay1=tau_decay1_ms/1000,
                        tau_rise2=tau_rise2_ms/1000, tau_decay2=tau_decay2_ms/1000)
current_slow = slow_epsp(time,
                        A=A_slow_pA,
                        tau_rise=tau_rise_slow_ms/1000, tau_decay=tau_decay_slow_ms/1000)

# Create comparison plot
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

# Fast-rising - full
ax1.plot(time, current_fast, 'b-', linewidth=2, label='Fast-rising')
ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3)
ax1.set_xlabel('Time (s)', fontsize=11)
ax1.set_ylabel('Current (pA)', fontsize=11)
ax1.set_title('Fast-Rising EPSP (Double Exponential)', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)
peak_idx = np.argmax(current_fast)
ax1.plot(time[peak_idx], current_fast[peak_idx], 'ro', markersize=8)
ax1.text(0.98, 0.95, f'Peak: {current_fast[peak_idx]:.1f} pA\n@ {time[peak_idx]:.6f} s',
         transform=ax1.transAxes, fontsize=9, va='top', ha='right',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

# Fast-rising - zoomed (0-0.01 s = 0-10 ms)
zoom_time = 0.01  # 10 ms in seconds
ax2.plot(time[time <= zoom_time], current_fast[time <= zoom_time], 'b-', linewidth=2)
ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
ax2.set_xlabel('Time (s)', fontsize=11)
ax2.set_ylabel('Current (pA)', fontsize=11)
ax2.set_title(f'Fast-Rising - Zoomed (0-{zoom_time*1000:.0f} ms)', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)
if time[peak_idx] <= zoom_time:
    ax2.plot(time[peak_idx], current_fast[peak_idx], 'ro', markersize=8)

# Slow-rising - full
ax3.plot(time, current_slow, 'g-', linewidth=2, label='Slow-rising')
ax3.axhline(y=0, color='k', linestyle='--', alpha=0.3)
ax3.set_xlabel('Time (s)', fontsize=11)
ax3.set_ylabel('Current (pA)', fontsize=11)
ax3.set_title('Slow-Rising EPSP (Single Exponential)', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3)
peak_idx_slow = np.argmax(current_slow)
ax3.plot(time[peak_idx_slow], current_slow[peak_idx_slow], 'ro', markersize=8)
ax3.text(0.98, 0.95, f'Peak: {current_slow[peak_idx_slow]:.1f} pA\n@ {time[peak_idx_slow]:.6f} s',
         transform=ax3.transAxes, fontsize=9, va='top', ha='right',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

# Overlay comparison
ax4.plot(time, current_fast, 'b-', linewidth=2, label='Fast-rising', alpha=0.7)
ax4.plot(time, current_slow, 'g-', linewidth=2, label='Slow-rising', alpha=0.7)
ax4.axhline(y=0, color='k', linestyle='--', alpha=0.3)
ax4.set_xlabel('Time (s)', fontsize=11)
ax4.set_ylabel('Current (pA)', fontsize=11)
ax4.set_title('Direct Comparison', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.legend(loc='upper right', fontsize=10)
ax4.set_xlim([0, 0.050])  # Focus on first 50 ms (0.05 s) where differences are clear

plt.suptitle('Fast-Rising vs Slow-Rising sim-EPSP Comparison', fontsize=14, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('epsp_comparison.png', dpi=300, bbox_inches='tight')
print("Comparison plot saved: epsp_comparison.png")
