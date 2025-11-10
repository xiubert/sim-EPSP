# Sim-EPSP Stimulus File Generator for Clampex

This Python script generates Clampex 10.7-compatible ATF stimulus files implementing sim-EPSP waveforms with either **fast-rising** or **slow-rising** kinetics as described in https://doi.org/10.1126/science.1061395.

## Two Kinetics Types

### Fast-Rising EPSP (Double Exponential) - DEFAULT
```
y = A1[1 - exp(-t/τrise1)][exp(-t/τdecay1)] + A2[1 - exp(-t/τrise2)][exp(-t/τdecay2)]
```

**Default Parameters:**
- **A1** = 150 pA (fast component amplitude)
- **τrise1** = 0.01 ms (fast rise time - very rapid!)
- **τdecay1** = 1 ms (fast decay time)
- **A2** = 70 pA (slow component amplitude)
- **τrise2** = 3 ms (slow rise time)
- **τdecay2** = 20 ms (slow decay time)

**Characteristics:** Peaks at ~138 pA within 0.0001 s (0.1 ms at 10 kHz sampling) after stimulus onset, mimics fast synaptic events

**Default Delay:** 20 ms (0.020 s) - zero current baseline before stimulus starts

### Slow-Rising EPSP (Single Exponential)
```
y = A[1 - exp(-t/τrise)] × [exp(-t/τdecay)]
```

**Default Parameters:**
- **A** = 150 pA (amplitude)
- **τrise** = 10 ms (rise time)
- **τdecay** = 15 ms (decay time)

**Characteristics:** Peaks at ~49 pA around 0.0092 s (9.2 ms) after stimulus onset, mimics slower synaptic integration

**Default Delay:** 20 ms (0.020 s) - zero current baseline before stimulus starts

## Stimulus Delay Feature

All generated stimuli include a **delay period** before the EPSP waveform begins. This provides:
- A stable baseline for accurate peak detection
- Realistic experimental conditions (no instantaneous onset)
- Time for the recording system to stabilize

**Delay Options:**
1. **Default delay:** 20 ms (0.020 s) - used when no delay option is specified
2. **Custom delay:** Use `--delay X` where X is the delay in seconds (e.g., `--delay 0.015` for 15 ms)
3. **No delay:** Use `--delay 0` to start stimulus immediately
4. **Auto delay:** Use `--auto_delay` to calculate delay as 1/64 of total sweep duration: `(total_samples / 64) × sample_interval`

During the delay period, the current is held at 0 pA. The stimulus onset occurs after the delay period ends.

## Quick Start

### Generate FAST-RISING EPSP (default):
```bash
python generate_sim_epsp.py --kinetics fast --uniform_sampling --sampling_rate 10000
```
**Output files (in `output/` directory):**
- `fast_a1_150pA_a2_70pA_tauRise1_0.01ms_tauDecay1_1ms_tauRise2_3ms_tauDecay2_20ms_delay_20ms_10000Hz.atf` - stimulus file
- `fast_a1_150pA_a2_70pA_tauRise1_0.01ms_tauDecay1_1ms_tauRise2_3ms_tauDecay2_20ms_delay_20ms_10000Hz_plot.png` - visualization

### Generate SLOW-RISING EPSP:
```bash
python generate_sim_epsp.py --kinetics slow --uniform_sampling --sampling_rate 10000
```
**Output files (in `output/` directory):**
- `slow_a_150pA_tauRise_10ms_tauDecay_15ms_delay_20ms_10000Hz.atf` - stimulus file
- `slow_a_150pA_tauRise_10ms_tauDecay_15ms_delay_20ms_10000Hz_plot.png` - visualization

### Custom parameters (filenames reflect your settings):
```bash
python generate_sim_epsp.py --kinetics fast --uniform_sampling --sampling_rate 20000 --A1 200 --A2 100
```
**Output:** `fast_a1_200pA_a2_100pA_tauRise1_0.01ms_tauDecay1_1ms_tauRise2_3ms_tauDecay2_20ms_delay_20ms_20000Hz.atf`

### Specify custom filename:
```bash
python generate_sim_epsp.py --kinetics slow --uniform_sampling --sampling_rate 10000 --output my_custom_name.atf
```

### Change output directory:
```bash
python generate_sim_epsp.py --kinetics fast --uniform_sampling --sampling_rate 10000 --output_dir my_data
```

### Custom delay before stimulus:
```bash
python generate_sim_epsp.py --kinetics fast --uniform_sampling --sampling_rate 10000 --delay 0.015
```
**Output:** Uses 15 ms delay instead of default 20 ms

### Automatic delay (1/64 of sweep duration):
```bash
python generate_sim_epsp.py --kinetics fast --uniform_sampling --sampling_rate 10000 --auto_delay
```
**Note:** Auto delay calculates delay as `(total_samples / 64) * sample_interval`

## CRITICAL: Clampex Protocol Configuration

⚠️ **The time values in the ATF file are REFERENCE ONLY!** ⚠️

According to the Clampex stimulus file tutorial (page 5):
> "The sampling interval of the episodic protocol and the number of samples per sweep 
> will determine the time base of the stimulus waveform, NOT the time base of the 
> original file."

### Steps to Use the Stimulus File:

1. **Create an Episodic Protocol in Clampex**

2. **Configure the Protocol Tab:**
   - Set **Acquisition Mode** to "Episodic stimulation"
   - Set **Sweeps per run** = 1

3. **Set the Sampling Rate:**

   **If you used --uniform_sampling flag (e.g., 10000 Hz = 10 kHz):**
   - Set **Sampling Interval** = 0.1 ms (for 10000 Hz)
   - Set **Sampling Interval** = 0.05 ms (for 20000 Hz = 20 kHz)
   - The script will tell you the exact values to use

   **If you used variable sampling:**
   - The script calculates an approximate sampling interval
   - OR better: regenerate with `--uniform_sampling` for precise control

4. **Configure Wave 0 Page:**
   - Click the **Waveform** dropdown
   - Select **"Stimulus file"** (NOT "Epochs")
   - Click the **"Stimulus File..."** button
   - Browse and select your .atf file
   - The amplitude is controlled by the ATF data, NOT by the Cmd 0 scale factor

5. **Set Holding Command (Optional):**
   - Use the Real-Time Control panel (RTC) to set holding level
   - For this EPSP, 0 pA is appropriate (it's an excitatory current)

## Usage Examples

### Example 1: Fast-rising EPSP at 10 kHz (default)
```bash
python generate_sim_epsp.py --kinetics fast --uniform_sampling --sampling_rate 10000
```
**Clampex settings:**
- Sampling Interval: 0.1 ms (10 kHz)
- Number of samples: 1200 (200 delay + 1000 stimulus)
- Total duration: 0.12 s (120 ms total: 20 ms delay + 100 ms stimulus)
- **Peak: ~138 pA at 0.0201 s (20.1 ms from sweep start)**

### Example 2: Slow-rising EPSP at 10 kHz
```bash
python generate_sim_epsp.py --kinetics slow --uniform_sampling --sampling_rate 10000
```
**Clampex settings:**
- Sampling Interval: 0.1 ms (10 kHz)
- Number of samples: 1200 (200 delay + 1000 stimulus)
- Total duration: 0.12 s (120 ms total: 20 ms delay + 100 ms stimulus)
- **Peak: ~49 pA at 0.0292 s (29.2 ms from sweep start)**

### Example 3: Higher resolution fast EPSP at 20 kHz
```bash
python generate_sim_epsp.py --kinetics fast --uniform_sampling --sampling_rate 20000 --output high_res.atf
```
**Clampex settings:**
- Sampling Interval: 0.05 ms (20 kHz)
- Number of samples: 2400 (400 delay + 2000 stimulus)
- Total duration: 0.12 s (120 ms total: 20 ms delay + 100 ms stimulus)

### Example 4: Custom slow-rising parameters
```bash
python generate_sim_epsp.py --kinetics slow --uniform_sampling --sampling_rate 10000 \
    --A 200 --tau_rise 8 --tau_decay 12 --output custom_slow.atf
```

### Example 5: Custom fast-rising parameters
```bash
python generate_sim_epsp.py --kinetics fast --uniform_sampling --sampling_rate 10000 \
    --A1 200 --tau_decay1 1.5 --A2 80 --output custom_fast.atf
```

### Example 6: Longer duration with no delay
```bash
python generate_sim_epsp.py --kinetics slow --uniform_sampling --sampling_rate 10000 \
    --duration 0.200 --delay 0 --output long_stimulus.atf
```

### Example 7: Custom delay timing
```bash
python generate_sim_epsp.py --kinetics fast --uniform_sampling --sampling_rate 10000 \
    --delay 0.050 --output delayed_stimulus.atf
```
**Note:** Uses 50 ms delay before stimulus onset

## All Command-Line Options

```
KINETICS TYPE:
--kinetics          Type of EPSP: "fast" or "slow" [default: fast]

FAST-RISING PARAMETERS (--kinetics fast):
--A1                Amplitude of first component (pA) [default: 150.0]
--tau_rise1         Rise time constant of first component (ms) [default: 0.01]
--tau_decay1        Decay time constant of first component (ms) [default: 1.0]
--A2                Amplitude of second component (pA) [default: 70.0]
--tau_rise2         Rise time constant of second component (ms) [default: 3.0]
--tau_decay2        Decay time constant of second component (ms) [default: 20.0]

SLOW-RISING PARAMETERS (--kinetics slow):
--A                 Amplitude (pA) [default: 150.0]
--tau_rise          Rise time constant (ms) [default: 10.0]
--tau_decay         Decay time constant (ms) [default: 15.0]

TIME ARRAY:
--duration          Total duration of stimulus (s) [default: 0.100]
--delay             Delay before stimulus starts (s) [default: 0.020 = 20 ms]
--auto_delay        Automatically calculate delay as (total samples / 64) * sample interval
--uniform_sampling  Use uniform sampling interval (recommended)
--sampling_rate     Sampling rate in Hz (with --uniform_sampling) [default: 10000.0]

OUTPUT:
--output            Output filename (auto-generated if not specified)
--output_dir        Output directory [default: output]
--plot              Output plot filename (auto-generated if not specified)
--no_plot           Skip generating plot
--comment           Comment for ATF file header
```

## Automatic Filename Generation

By default, filenames are automatically generated based on your parameters:

**Fast-rising examples:**
- `fast_a1_150pA_a2_70pA_tauRise1_0.01ms_tauDecay1_1ms_tauRise2_3ms_tauDecay2_20ms_delay_20ms_10000Hz.atf` (default parameters with 20 ms delay, 10 kHz)
- `fast_a1_200pA_a2_100pA_tauRise1_0.01ms_tauDecay1_1ms_tauRise2_3ms_tauDecay2_20ms_delay_20ms_20000Hz.atf` (custom amplitudes with 20 ms delay, 20 kHz)
- `fast_a1_150pA_a2_70pA_tauRise1_0.01ms_tauDecay1_1ms_tauRise2_3ms_tauDecay2_20ms_delay_0ms_10000Hz.atf` (no delay, 10 kHz)

**Slow-rising examples:**
- `slow_a_150pA_tauRise_10ms_tauDecay_15ms_delay_20ms_10000Hz.atf` (default parameters with 20 ms delay, 10 kHz)
- `slow_a_200pA_tauRise_5ms_tauDecay_12ms_delay_20ms_20000Hz.atf` (custom parameters with 20 ms delay, 20 kHz)
- `slow_a_150pA_tauRise_10ms_tauDecay_15ms_delay_50ms_10000Hz.atf` (50 ms delay, 10 kHz)

This makes it easy to organize and identify files by their parameters!

## Plot Output

The script automatically generates a publication-quality plot showing:
- **Upper panel**: Full time course of the stimulus waveform (including delay period)
  - Peak amplitude marked with red dot
  - Parameters displayed in text box (wheat background for fast, light blue for slow)
  - Zero current line for reference
  - Delay period visible as baseline before stimulus onset
- **Lower panel**: Zoomed view of the initial response (first 10 ms after stimulus onset)
  - Shows the rising phase in detail
  - Critical for verifying the kinetics

The plot is saved as a PNG file (300 DPI) and includes all relevant parameters (including delay) for documentation purposes.

## Comparing Fast vs Slow Kinetics

A comparison script (`compare_epsps.py`) is also provided to visualize both kinetics types side-by-side:

```bash
python compare_epsps.py
```

This creates `epsp_comparison.png` showing:
- Fast-rising EPSP with zoom
- Slow-rising EPSP with zoom  
- Direct overlay comparison

**Key Differences:**
- **Fast-rising**: Peaks at ~143 pA in 0.00005 s (0.05 ms), rapid rise and decay
- **Slow-rising**: Peaks at ~49 pA in 0.0092 s (9.2 ms), gradual rise and decay
- **Use fast** for mimicking AMPA-like synaptic currents
- **Use slow** for mimicking slower synaptic integration or NMDA-like kinetics

## Testing the Stimulus File

### Method 1: Feedback Loop (from tutorial)
1. Connect a BNC cable from **Analog Out #0** to **Analog In #0**
2. Configure digitizer to Demo mode
3. Run the protocol
4. You'll see the exact command waveform that will be sent to your amplifier

### Method 2: Waveform Preview
1. In the protocol editor, click **"Update Preview"** button
2. View the waveform shape (note: timing shown may not reflect actual playback)

## Troubleshooting

**Q: The timing is wrong when I play the stimulus**
- A: Check that your protocol's sampling interval matches what the script recommended
- The ATF file time column is just reference data

**Q: The amplitude is wrong**
- A: The amplitude comes from the ATF file data, NOT the Cmd 0 scale factor
- Check that your amplifier scaling is set correctly (e.g., 20 mV/V for voltage clamp)

**Q: I want different timing without regenerating the file**
- A: You can't reliably do this. The number of points is fixed in the ATF file.
- Regenerate with `--uniform_sampling` and your desired `--sampling_rate`

**Q: Should I use uniform or variable sampling?**
- A: **Use uniform sampling** (`--uniform_sampling` flag) for easier Clampex setup
- Variable sampling creates smaller files but requires calculating average sampling rate

**Q: What is the delay for and how do I use it?**
- A: The delay creates a baseline period before the stimulus starts
- Default is 20 ms (0.020 s) of zero current before the EPSP begins
- Use `--delay 0` to disable delay entirely
- Use `--auto_delay` for automatic calculation (1/64 of total sweep duration)
- Delay is included in filename and ATF comment for documentation

## File Format

The ATF (Axon Text File) format is a tab-delimited text file:
- Header lines define metadata
- Column 1: Time (s) - reference only
- Column 2: Current amplitude (pA) - this is what matters!
- Comment line includes all generation parameters for documentation

You can open and edit ATF files in Excel if needed (see tutorial page 7-8).

## Requirements

- Python 3.x
- NumPy (`pip install numpy`)
- Matplotlib (`pip install matplotlib`)

Or install all at once:
```bash
pip install numpy matplotlib
```

## References

- Clampex "Creating and editing a Stimulus File" tutorial
- ATF file format specification
- Double-exponential synaptic current model

## Output

The script provides:
- ✅ ATF file compatible with Clampex 10.7
- ✅ High-quality plot (PNG, 300 DPI) with dual panels
- ✅ Summary statistics (peak current, timing, number of points)
- ✅ Exact Clampex protocol configuration settings
- ✅ Parameter summary for your records

### Example Output Files

**Standard 10 kHz sampling (with default 20 ms delay):**
- `fast_a1_150pA_a2_70pA_tauRise1_0.01ms_tauDecay1_1ms_tauRise2_3ms_tauDecay2_20ms_delay_20ms_10000Hz.atf` - 1200 points, 0.12 s total (20 ms delay + 100 ms stimulus)
- `fast_a1_150pA_a2_70pA_tauRise1_0.01ms_tauDecay1_1ms_tauRise2_3ms_tauDecay2_20ms_delay_20ms_10000Hz_plot.png` - visualization

**High resolution 20 kHz sampling (with default 20 ms delay):**
- `fast_a1_150pA_a2_70pA_tauRise1_0.01ms_tauDecay1_1ms_tauRise2_3ms_tauDecay2_20ms_delay_20ms_20000Hz.atf` - 2400 points, 0.12 s total (20 ms delay + 100 ms stimulus)
- `fast_a1_150pA_a2_70pA_tauRise1_0.01ms_tauDecay1_1ms_tauRise2_3ms_tauDecay2_20ms_delay_20ms_20000Hz_plot.png` - visualization

**Custom parameters:**
- Files include all parameters in the filename for easy identification
- Comment field in ATF file also contains all generation parameters
