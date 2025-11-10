#!/usr/bin/env python3
"""
Compare fast-rising and slow-rising sim-EPSP waveforms.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Fast-rising (double exponential)
def fast_epsp(t, A1=150, tau_rise1=0.01, tau_decay1=1.0, A2=70, tau_rise2=3.0, tau_decay2=20.0):
    component1 = A1 * (1 - np.exp(-t / tau_rise1)) * np.exp(-t / tau_decay1)
    component2 = A2 * (1 - np.exp(-t / tau_rise2)) * np.exp(-t / tau_decay2)
    y = component1 + component2
    y[t < 0] = 0
    return y

# Slow-rising (single exponential)
def slow_epsp(t, A=150, tau_rise=10.0, tau_decay=15.0):
    y = A * (1 - np.exp(-t / tau_rise)) * np.exp(-t / tau_decay)
    y[t < 0] = 0
    return y

# Generate time arrays
dt = 0.05  # 20 kHz
time = np.arange(0, 100 + dt/2, dt)

# Calculate currents
current_fast = fast_epsp(time)
current_slow = slow_epsp(time)

# Create comparison plot
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

# Fast-rising - full
ax1.plot(time, current_fast, 'b-', linewidth=2, label='Fast-rising')
ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3)
ax1.set_xlabel('Time (ms)', fontsize=11)
ax1.set_ylabel('Current (pA)', fontsize=11)
ax1.set_title('Fast-Rising EPSP (Double Exponential)', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)
peak_idx = np.argmax(current_fast)
ax1.plot(time[peak_idx], current_fast[peak_idx], 'ro', markersize=8)
ax1.text(0.98, 0.95, f'Peak: {current_fast[peak_idx]:.1f} pA\n@ {time[peak_idx]:.3f} ms',
         transform=ax1.transAxes, fontsize=9, va='top', ha='right',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

# Fast-rising - zoomed
ax2.plot(time[time <= 10], current_fast[time <= 10], 'b-', linewidth=2)
ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
ax2.set_xlabel('Time (ms)', fontsize=11)
ax2.set_ylabel('Current (pA)', fontsize=11)
ax2.set_title('Fast-Rising - Zoomed (0-10 ms)', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.plot(time[peak_idx], current_fast[peak_idx], 'ro', markersize=8)

# Slow-rising - full
ax3.plot(time, current_slow, 'g-', linewidth=2, label='Slow-rising')
ax3.axhline(y=0, color='k', linestyle='--', alpha=0.3)
ax3.set_xlabel('Time (ms)', fontsize=11)
ax3.set_ylabel('Current (pA)', fontsize=11)
ax3.set_title('Slow-Rising EPSP (Single Exponential)', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3)
peak_idx_slow = np.argmax(current_slow)
ax3.plot(time[peak_idx_slow], current_slow[peak_idx_slow], 'ro', markersize=8)
ax3.text(0.98, 0.95, f'Peak: {current_slow[peak_idx_slow]:.1f} pA\n@ {time[peak_idx_slow]:.3f} ms',
         transform=ax3.transAxes, fontsize=9, va='top', ha='right',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

# Overlay comparison
ax4.plot(time, current_fast, 'b-', linewidth=2, label='Fast-rising', alpha=0.7)
ax4.plot(time, current_slow, 'g-', linewidth=2, label='Slow-rising', alpha=0.7)
ax4.axhline(y=0, color='k', linestyle='--', alpha=0.3)
ax4.set_xlabel('Time (ms)', fontsize=11)
ax4.set_ylabel('Current (pA)', fontsize=11)
ax4.set_title('Direct Comparison', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.legend(loc='upper right', fontsize=10)
ax4.set_xlim([0, 50])  # Focus on first 50 ms where differences are clear

plt.suptitle('Fast-Rising vs Slow-Rising sim-EPSP Comparison', fontsize=14, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('epsp_comparison.png', dpi=300, bbox_inches='tight')
print("Comparison plot saved: epsp_comparison.png")
