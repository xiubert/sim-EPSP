# Quick Reference Guide - Sim-EPSP Stimulus Generator

## Choose Your Kinetics Type

### FAST-RISING (Double Exponential) - For rapid synaptic events
- Peaks at ~143 pA within 0.05 ms
- Mimics AMPA-like fast synaptic currents
- Uses two exponential components

### SLOW-RISING (Single Exponential) - For slower integration
- Peaks at ~49 pA around 9 ms
- Mimics slower synaptic integration or NMDA-like kinetics
- Uses single exponential component

---

## Most Common Usage

### Fast-Rising EPSP (default):
```bash
python generate_sim_epsp.py --kinetics fast --uniform_sampling --sampling_rate 20
```
**Creates in `output/` directory:**
- `fast_a1_150pA_a2_70pA_20kHz.atf`
- `fast_a1_150pA_a2_70pA_20kHz_plot.png`

### Slow-Rising EPSP:
```bash
python generate_sim_epsp.py --kinetics slow --uniform_sampling --sampling_rate 20
```
**Creates in `output/` directory:**
- `slow_a_150pA_tauRise_10ms_20kHz.atf`
- `slow_a_150pA_tauRise_10ms_20kHz_plot.png`

**Clampex settings (same for both):**
- Sampling Interval: 0.05 ms (20 kHz)
- Number of samples: 2001
- Sweeps per run: 1
- Wave 0: Select "Stimulus file" and load the ATF file from `output/` directory

---

## Common Variations

### Higher resolution
```bash
# Fast-rising at 50 kHz
python generate_sim_epsp.py --kinetics fast --uniform_sampling --sampling_rate 50

# Slow-rising at 50 kHz
python generate_sim_epsp.py --kinetics slow --uniform_sampling --sampling_rate 50
```

### Custom amplitudes

**For fast-rising:**
```bash
python generate_sim_epsp.py --kinetics fast --uniform_sampling --sampling_rate 20 \
    --A1 200 --A2 100
```

**For slow-rising:**
```bash
python generate_sim_epsp.py --kinetics slow --uniform_sampling --sampling_rate 20 \
    --A 200
```

### Custom time constants

**For fast-rising (adjust decay):**
```bash
python generate_sim_epsp.py --kinetics fast --uniform_sampling --sampling_rate 20 \
    --tau_decay1 1.5 --tau_decay2 25
```

**For slow-rising (faster rise):**
```bash
python generate_sim_epsp.py --kinetics slow --uniform_sampling --sampling_rate 20 \
    --tau_rise 5 --tau_decay 10
```

### Longer duration
```bash
python generate_sim_epsp.py --kinetics slow --uniform_sampling --sampling_rate 20 \
    --duration 200
```

---

## Parameter Guide

### Fast-Rising Parameters (--kinetics fast)
| Parameter | Default | Description |
|-----------|---------|-------------|
| --A1 | 150 pA | Fast component amplitude |
| --tau_rise1 | 0.01 ms | Fast rise time (very rapid!) |
| --tau_decay1 | 1 ms | Fast decay time |
| --A2 | 70 pA | Slow component amplitude |
| --tau_rise2 | 3 ms | Slow rise time |
| --tau_decay2 | 20 ms | Slow decay time |

### Slow-Rising Parameters (--kinetics slow)
| Parameter | Default | Description |
|-----------|---------|-------------|
| --A | 150 pA | Amplitude |
| --tau_rise | 10 ms | Rise time constant |
| --tau_decay | 15 ms | Decay time constant |

### General Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| --duration | 100 ms | Total stimulus length |
| --sampling_rate | 20 kHz | Temporal resolution |
| --output | auto-generated | Output filename (descriptive if not specified) |
| --output_dir | output | Directory for output files |

---

## Automatic Filenames

Filenames are auto-generated based on parameters:

### Fast-Rising Examples:
```
fast_a1_150pA_a2_70pA_20kHz.atf         # Default, 20 kHz
fast_a1_200pA_a2_100pA_50kHz.atf        # Custom amps, 50 kHz
fast_a1_150pA_a2_70pA_100kHz.atf        # High sampling rate
```

### Slow-Rising Examples:
```
slow_a_150pA_tauRise_10ms_20kHz.atf     # Default, 20 kHz
slow_a_200pA_tauRise_5ms_50kHz.atf      # Faster rise, 50 kHz
slow_a_100pA_tauRise_15ms_20kHz.atf     # Lower amplitude
```

### Override with custom name:
```bash
python generate_sim_epsp.py --kinetics fast --uniform_sampling --sampling_rate 20 \
    --output my_custom_name.atf
```

---

## Visual Comparison

To see both kinetics types side-by-side:
```bash
python compare_epsps.py
```

This creates `epsp_comparison.png` with:
- Fast-rising: Sharp spike to 143 pA at 0.05 ms
- Slow-rising: Gradual rise to 49 pA at 9.15 ms
- Overlay comparison

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Wrong timing in Clampex | Match protocol sampling interval to script output |
| Wrong amplitude | Amplitude from ATF file, not Cmd 0 scale |
| Need faster/slower rise | Adjust --tau_rise (or --tau_rise1 for fast) |
| Need stronger/weaker | Adjust --A (or --A1, --A2 for fast) |
| Want different kinetics | Switch between --kinetics fast and slow |

---

## When to Use Which

### Use FAST-RISING when:
- Mimicking AMPA receptor currents
- Studying action potential initiation
- Modeling fast synaptic transmission
- Need sub-millisecond precision

### Use SLOW-RISING when:
- Mimicking NMDA receptor kinetics
- Studying synaptic integration
- Modeling dendritic processing
- Examining temporal summation

---

## Key Concept: Time Base

⚠️ **IMPORTANT**: Time values in ATF file are **reference only**!

Actual playback timing controlled by:
1. Clampex protocol's sampling interval
2. Number of data points in ATF file

Formula: `Duration = Sampling_Interval × Number_of_Points`

Always use `--uniform_sampling` for predictable timing!

---

## Quick Help

```bash
# See all options
python generate_sim_epsp.py --help

# Default fast-rising
python generate_sim_epsp.py --kinetics fast --uniform_sampling --sampling_rate 20

# Default slow-rising  
python generate_sim_epsp.py --kinetics slow --uniform_sampling --sampling_rate 20

# Compare both types
python compare_epsps.py
```
