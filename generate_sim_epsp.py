#!/usr/bin/env python3
"""
Generate Clampex-compatible ATF stimulus file for sim-EPSP waveform.

The sim-EPSP waveform is generated using a double-exponential equation:
y = A1[1 - exp(-t/τrise1)][exp(-t/τdecay1)] + A2[1 - exp(-t/τrise2)][exp(-t/τdecay2)]

where:
    y = amplitude of injected current (pA)
    t = time (s)

Command-line parameters:
    - Sampling rate: Hz (e.g., 10000 for 10 kHz)
    - Duration: seconds (e.g., 0.150 for 150 ms)
    - Tau parameters: milliseconds (e.g., 0.01, 1.0, 3.0, 20.0)
    - Current amplitudes: picoamperes (e.g., 150, 70)

IMPORTANT - Clampex Protocol Configuration:
===========================================
The time base in the ATF file is for REFERENCE ONLY. To properly play back
this stimulus in Clampex, you MUST configure your episodic protocol with:

1. Sampling Interval = 1 / Sampling_Rate
   - For 10000 Hz: 1/10000 = 0.0001 s = 0.1 ms
   - Use --uniform_sampling flag to create evenly-spaced points

2. Sweeps per run = 1 (since ATF file contains one sweep)

3. On the Wave 0 page:
   - Select "Stimulus file" as the waveform source
   - Click "Stimulus File" button and select this ATF file
   - The amplitude is determined by the ATF data, NOT by Cmd 0 scale factor

See page 5 of the Clampex stimulus file tutorial for more details.
"""

import numpy as np
import argparse
import matplotlib
# matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import os


def generate_filename(kinetics, sampling_rate, delay=None, A1=None, A2=None, A=None,
                      tau_rise1=None, tau_rise2=None, tau_rise=None,
                      tau_decay1=None, tau_decay2=None, tau_decay=None):
    """
    Generate a descriptive filename based on parameters.

    Returns both the base filename and the full path with extension.
    """
    # Format delay in ms
    delay_ms = delay * 1000 if delay is not None else 0

    if kinetics == 'fast':
        # Fast-rising: include A1, A2, all time constants, and delay
        base = (f"fast_a1_{int(A1)}pA_a2_{int(A2)}pA_"
                f"tauRise1_{tau_rise1:g}ms_tauDecay1_{tau_decay1:g}ms_"
                f"tauRise2_{tau_rise2:g}ms_tauDecay2_{tau_decay2:g}ms_"
                f"delay_{delay_ms:g}ms_"
                f"{int(sampling_rate)}Hz")
    else:  # slow
        # Slow-rising: include A, all time constants, and delay
        base = (f"slow_a_{int(A)}pA_"
                f"tauRise_{tau_rise:g}ms_tauDecay_{tau_decay:g}ms_"
                f"delay_{delay_ms:g}ms_"
                f"{int(sampling_rate)}Hz")

    return base


def double_exponential(t, A1, tau_rise1, tau_decay1, A2, tau_rise2, tau_decay2):
    """
    Calculate the double-exponential sim-EPSP current (FAST-RISING).

    Parameters:
    -----------
    t : array-like
        Time values in seconds
    A1 : float
        Amplitude of first component (pA)
    tau_rise1 : float
        Rise time constant of first component (s)
    tau_decay1 : float
        Decay time constant of first component (s)
    A2 : float
        Amplitude of second component (pA)
    tau_rise2 : float
        Rise time constant of second component (s)
    tau_decay2 : float
        Decay time constant of second component (s)

    Returns:
    --------
    y : array-like
        Current amplitude at each time point (pA)
    """
    # First component (fast)
    component1 = A1 * (1 - np.exp(-t / tau_rise1)) * np.exp(-t / tau_decay1)

    # Second component (slow)
    component2 = A2 * (1 - np.exp(-t / tau_rise2)) * np.exp(-t / tau_decay2)

    # Total current
    y = component1 + component2

    # Set negative time values to zero (handles delay period)
    y[t < 0] = 0

    return y


def single_exponential(t, A, tau_rise, tau_decay):
    """
    Calculate the single-exponential sim-EPSP current (SLOW-RISING).

    Parameters:
    -----------
    t : array-like
        Time values in seconds
    A : float
        Amplitude (pA)
    tau_rise : float
        Rise time constant (s)
    tau_decay : float
        Decay time constant (s)

    Returns:
    --------
    y : array-like
        Current amplitude at each time point (pA)
    """
    # Single exponential rise and decay
    y = A * (1 - np.exp(-t / tau_rise)) * np.exp(-t / tau_decay)

    # Set negative time values to zero (handles delay period)
    y[t < 0] = 0

    return y


def generate_time_array(duration=1000.0, dt_fine=0.01, dt_coarse=1.0, 
                        fine_duration=10.0):
    """
    Generate a time array with variable resolution.
    
    Parameters:
    -----------
    duration : float
        Total duration of the stimulus (ms)
    dt_fine : float
        Time step for fine resolution period (ms)
    dt_coarse : float
        Time step for coarse resolution period (ms)
    fine_duration : float
        Duration of fine resolution period (ms)
    
    Returns:
    --------
    t : ndarray
        Time array (ms)
    """
    # Fine resolution for the initial period (critical dynamics)
    t_fine = np.arange(0, fine_duration, dt_fine)
    
    # Coarse resolution for the remainder
    t_coarse = np.arange(fine_duration, duration + dt_coarse, dt_coarse)
    
    # Combine and ensure unique values
    t = np.unique(np.concatenate([t_fine, t_coarse]))
    
    return t


def write_atf_file(filename, time, current, comment="Simulated EPSP",
                   kinetics=None, A1=None, A2=None, A=None,
                   tau_rise1=None, tau_rise2=None, tau_rise=None,
                   tau_decay1=None, tau_decay2=None, tau_decay=None,
                   sampling_rate=None, delay=None):
    """
    Write data to Clampex-compatible ATF format.

    Parameters:
    -----------
    filename : str
        Output filename
    time : array-like
        Time values (s)
    current : array-like
        Current values (pA)
    comment : str
        Comment to include in the file header
    kinetics : str, optional
        Type of kinetics ('fast' or 'slow')
    A1, A2, A : float, optional
        Amplitude parameters (pA)
    tau_rise1, tau_rise2, tau_rise : float, optional
        Rise time constants (ms)
    tau_decay1, tau_decay2, tau_decay : float, optional
        Decay time constants (ms)
    sampling_rate : float, optional
        Sampling rate (Hz)
    delay : float, optional
        Delay before stimulus (s)
    """
    with open(filename, 'w') as f:
        # ATF header
        f.write("ATF\t1.0\n")
        f.write("8\t2\n")
        f.write('"AcquisitionMode=Episodic Stimulation"\n')

        # Build detailed comment with all parameters
        detailed_comment = comment
        if kinetics == 'fast' and all(p is not None for p in [A1, A2, tau_rise1, tau_decay1, tau_rise2, tau_decay2]):
            detailed_comment += (f" | A1={A1}pA A2={A2}pA "
                                f"tau_rise1={tau_rise1}ms tau_decay1={tau_decay1}ms "
                                f"tau_rise2={tau_rise2}ms tau_decay2={tau_decay2}ms")
        elif kinetics == 'slow' and all(p is not None for p in [A, tau_rise, tau_decay]):
            detailed_comment += (f" | A={A}pA "
                                f"tau_rise={tau_rise}ms tau_decay={tau_decay}ms")
        if delay is not None:
            detailed_comment += f" | delay={delay*1000}ms"
        if sampling_rate is not None:
            detailed_comment += f" | sampling_rate={sampling_rate}Hz"

        f.write(f'"Comment={detailed_comment}"\n')
        
        # Calculate Y-axis range for display
        y_max = np.max(current)
        y_min = np.min(current)
        y_range = y_max - y_min
        y_top = y_max + 0.1 * y_range
        y_bottom = y_min - 0.1 * y_range
        
        f.write(f'"YTop={y_top:.2f}"\n')
        f.write(f'"YBottom={y_bottom:.2f}"\n')
        # in example from clampex, unsure of meaning
        # f.write('"SyncTimeUnits=5"\n')
        f.write('"SweepStartTimesMS=0.000"\n')
        f.write('"SignalsExported=IN 0"\n')
        f.write('"Signals="\t"IN 0"\n')
        
        # Column headers
        f.write('"Time (s)"\t"IN 0 (pA)"\n')
        
        # Data - use general format 'g' for automatic scientific notation when needed
        for t_val, i_val in zip(time, current):
            f.write(f"{t_val:g}\t{i_val:g}\n")
    
    print(f"ATF file written successfully: {filename}")
    print(f"Duration: {time[-1]:.6f} s")
    print(f"Number of points: {len(time)}")
    print(f"Peak current: {np.max(current):.4f} pA at {time[np.argmax(current)]:.6f} s")


def plot_stimulus(time, current, output_filename, title="Simulated EPSP Stimulus", 
                  A1=None, tau_rise1=None, tau_decay1=None, 
                  A2=None, tau_rise2=None, tau_decay2=None,
                  A=None, tau_rise=None, tau_decay=None):
    """
    Create and save a plot of the stimulus waveform.
    
    Parameters:
    -----------
    time : array-like
        Time values (ms)
    current : array-like
        Current values (pA)
    output_filename : str
        Output plot filename
    title : str
        Plot title
    A1, tau_rise1, tau_decay1, A2, tau_rise2, tau_decay2 : float, optional
        Parameters for fast-rising (double exponential) to display in the plot
    A, tau_rise, tau_decay : float, optional
        Parameters for slow-rising (single exponential) to display in the plot
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[2, 1])
    
    # Main plot - full time course
    ax1.plot(time, current, 'b-', linewidth=1.5)
    ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3, linewidth=1)
    ax1.set_xlabel('Time (s)', fontsize=12)
    ax1.set_ylabel('Current (pA)', fontsize=12)
    ax1.set_title(title, fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # Mark peak
    peak_idx = np.argmax(current)
    peak_time = time[peak_idx]
    peak_current = current[peak_idx]
    ax1.plot(peak_time, peak_current, 'ro', markersize=8, label=f'Peak: {peak_current:.1f} pA @ {peak_time:.6f} s')
    ax1.legend(loc='upper right', fontsize=10)
    
    # Add parameters text box if provided
    # Check for fast-rising (double exponential) parameters
    if all(p is not None for p in [A1, tau_rise1, tau_decay1, A2, tau_rise2, tau_decay2]):
        param_text = (
            f'Fast-Rising Parameters:\n'
            f'A₁ = {A1} pA, τrise1 = {tau_rise1} ms, τdecay1 = {tau_decay1} ms\n'
            f'A₂ = {A2} pA, τrise2 = {tau_rise2} ms, τdecay2 = {tau_decay2} ms'
        )
        ax1.text(0.98, 0.05, param_text, transform=ax1.transAxes,
                fontsize=9, verticalalignment='bottom', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    # Check for slow-rising (single exponential) parameters
    elif all(p is not None for p in [A, tau_rise, tau_decay]):
        param_text = (
            f'Slow-Rising Parameters:\n'
            f'A = {A} pA\n'
            f'τrise = {tau_rise} ms\n'
            f'τdecay = {tau_decay} ms'
        )
        ax1.text(0.98, 0.05, param_text, transform=ax1.transAxes,
                fontsize=9, verticalalignment='bottom', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    # Zoomed plot - early time course (first 0.01 s or 10% of duration, whichever is larger)
    zoom_duration = max(0.01, time[-1] * 0.1)
    zoom_mask = time <= zoom_duration
    ax2.plot(time[zoom_mask], current[zoom_mask], 'b-', linewidth=1.5)
    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3, linewidth=1)
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Current (pA)', fontsize=12)
    ax2.set_title(f'Zoomed View (0-{zoom_duration:.4f} s)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    # Mark peak on zoomed plot if within range
    if peak_time <= zoom_duration:
        ax2.plot(peak_time, peak_current, 'ro', markersize=8)
    
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Plot saved: {output_filename}")


def main():
    """Main function to generate sim-EPSP stimulus file."""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Generate Clampex ATF stimulus file for sim-EPSP waveform',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Kinetics type selection
    parser.add_argument('--kinetics', type=str, default='fast', choices=['fast', 'slow'],
                        help='Type of EPSP kinetics: "fast" for double-exponential (fast-rising), "slow" for single-exponential (slow-rising)')
    
    # Parameters for the FAST-RISING double-exponential equation
    parser.add_argument('--A1', type=float, default=150.0,
                        help='[FAST] Amplitude of first component (pA)')
    parser.add_argument('--tau_rise1', type=float, default=0.01,
                        help='[FAST] Rise time constant of first component (ms)')
    parser.add_argument('--tau_decay1', type=float, default=1.0,
                        help='[FAST] Decay time constant of first component (ms)')
    parser.add_argument('--A2', type=float, default=70.0,
                        help='[FAST] Amplitude of second component (pA)')
    parser.add_argument('--tau_rise2', type=float, default=3.0,
                        help='[FAST] Rise time constant of second component (ms)')
    parser.add_argument('--tau_decay2', type=float, default=20.0,
                        help='[FAST] Decay time constant of second component (ms)')
    
    # Parameters for the SLOW-RISING single-exponential equation
    parser.add_argument('--A', type=float, default=150.0,
                        help='[SLOW] Amplitude (pA)')
    parser.add_argument('--tau_rise', type=float, default=10.0,
                        help='[SLOW] Rise time constant (ms)')
    parser.add_argument('--tau_decay', type=float, default=15.0,
                        help='[SLOW] Decay time constant (ms)')
    
    # Time array parameters
    parser.add_argument('--duration', type=float, default=0.100,
                        help='Total duration of stimulus (s)')
    parser.add_argument('--delay', type=float, default=0.020,
                        help='Delay before stimulus starts (s) [default: 0.020 = 20 ms]')
    parser.add_argument('--auto_delay', action='store_true',
                        help='Automatically calculate delay as (total samples / 64) * sample interval')
    parser.add_argument('--uniform_sampling', action='store_true',
                        help='Use uniform sampling interval (recommended for Clampex)')
    parser.add_argument('--sampling_rate', type=float, default=10000.0,
                        help='Sampling rate in Hz (only with --uniform_sampling)')
    parser.add_argument('--dt_fine', type=float, default=0.01,
                        help='Time step for fine resolution (ms) (without --uniform_sampling)')
    parser.add_argument('--dt_coarse', type=float, default=1.0,
                        help='Time step for coarse resolution (ms) (without --uniform_sampling)')
    parser.add_argument('--fine_duration', type=float, default=10.0,
                        help='Duration of fine resolution period (ms) (without --uniform_sampling)')
    
    # Output file
    parser.add_argument('--output', type=str, default=None,
                        help='Output filename (if not specified, auto-generates descriptive name)')
    parser.add_argument('--output_dir', type=str, default='output',
                        help='Output directory for generated files')
    parser.add_argument('--plot', type=str, default=None,
                        help='Output plot filename (if not specified, auto-generates based on output filename)')
    parser.add_argument('--no_plot', action='store_true',
                        help='Skip generating plot')
    parser.add_argument('--comment', type=str, 
                        default='Simulated EPSP with fast-rising phase - Double exponential',
                        help='Comment for ATF file header')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        print(f"Created output directory: {args.output_dir}")
    
    # parse units

    # Generate time array
    if args.uniform_sampling:
        # Uniform sampling interval (better for Clampex protocol setup)
        dt = 1.0 / args.sampling_rate  # Sampling rate in Hz, dt in seconds

        # Calculate delay
        if args.auto_delay:
            # Total sweep includes delay + stimulus duration
            total_samples = int((args.delay + args.duration) / dt)
            delay = (total_samples / 64) * dt
            print(f"Auto-calculated delay: {delay:.6f} s ({delay*1000:.3f} ms)")
        else:
            delay = args.delay
            print(f"Using specified delay: {delay:.6f} s ({delay*1000:.3f} ms)")

        # Generate full time array (delay + stimulus)
        total_duration = delay + args.duration
        time = np.arange(0, total_duration, dt)
        print(f"Using uniform sampling: {args.sampling_rate} Hz ({dt:.6f} s interval)")
        print(f"Total duration: {total_duration:.6f} s (delay: {delay*1000:.3f} ms + stimulus: {args.duration*1000:.3f} ms)")
    else:
        # Variable resolution sampling (function generates time in ms, convert to s)
        duration_ms = args.duration * 1000  # Convert duration from s to ms
        time_ms = generate_time_array(
            duration=duration_ms,
            dt_fine=args.dt_fine,
            dt_coarse=args.dt_coarse,
            fine_duration=args.fine_duration
        )
        # Convert time from ms to seconds
        time = time_ms / 1000

        # Calculate delay for variable sampling
        if args.auto_delay:
            dt_avg = time[1] - time[0]  # Approximate dt
            total_samples = len(time)
            delay = (total_samples / 64) * dt_avg
            print(f"Auto-calculated delay: {delay:.6f} s ({delay*1000:.3f} ms)")
        else:
            delay = args.delay
            print(f"Using specified delay: {delay:.6f} s ({delay*1000:.3f} ms)")

        # Add delay by prepending time points
        delay_samples = int(delay / (time[1] - time[0]))
        delay_time = np.linspace(0, delay, delay_samples, endpoint=False)
        time = np.concatenate([delay_time, time + delay])
        print("Using variable resolution sampling")
    
    # Calculate current values based on kinetics type
    print(f"Kinetics type: {args.kinetics.upper()}")

    # Create time array relative to stimulus start (subtract delay)
    time_stimulus = time - delay

    if args.kinetics == 'fast':
        # Fast-rising: double-exponential
        # Convert tau parameters from ms to seconds
        current = double_exponential(
            time_stimulus,
            A1=args.A1,
            tau_rise1=args.tau_rise1 / 1000,
            tau_decay1=args.tau_decay1 / 1000,
            A2=args.A2,
            tau_rise2=args.tau_rise2 / 1000,
            tau_decay2=args.tau_decay2 / 1000
        )
        comment = "Fast-rising sim-EPSP - Double exponential"
        
        # Generate filename if not specified
        if args.output is None:
            base_filename = generate_filename(
                'fast', args.sampling_rate,
                delay=delay,
                A1=args.A1, A2=args.A2,
                tau_rise1=args.tau_rise1, tau_rise2=args.tau_rise2,
                tau_decay1=args.tau_decay1, tau_decay2=args.tau_decay2
            )
            output_file = os.path.join(args.output_dir, base_filename + '.atf')
        else:
            output_file = os.path.join(args.output_dir, args.output)
            base_filename = os.path.splitext(os.path.basename(args.output))[0]
            
    else:  # slow
        # Slow-rising: single-exponential
        # Convert tau parameters from ms to seconds
        current = single_exponential(
            time_stimulus,
            A=args.A,
            tau_rise=args.tau_rise / 1000,
            tau_decay=args.tau_decay / 1000
        )
        comment = "Slow-rising sim-EPSP - Single exponential"
        
        # Generate filename if not specified
        if args.output is None:
            base_filename = generate_filename(
                'slow', args.sampling_rate,
                delay=delay,
                A=args.A,
                tau_rise=args.tau_rise,
                tau_decay=args.tau_decay
            )
            output_file = os.path.join(args.output_dir, base_filename + '.atf')
        else:
            output_file = os.path.join(args.output_dir, args.output)
            base_filename = os.path.splitext(os.path.basename(args.output))[0]
    
    # Write ATF file
    if args.kinetics == 'fast':
        write_atf_file(output_file, time, current,
                      comment=args.comment if args.comment != 'Simulated EPSP with fast-rising phase - Double exponential' else comment,
                      kinetics='fast',
                      A1=args.A1, A2=args.A2,
                      tau_rise1=args.tau_rise1, tau_decay1=args.tau_decay1,
                      tau_rise2=args.tau_rise2, tau_decay2=args.tau_decay2,
                      delay=delay,
                      sampling_rate=args.sampling_rate)
    else:
        write_atf_file(output_file, time, current,
                      comment=args.comment if args.comment != 'Simulated EPSP with fast-rising phase - Double exponential' else comment,
                      kinetics='slow',
                      A=args.A,
                      tau_rise=args.tau_rise, tau_decay=args.tau_decay,
                      delay=delay,
                      sampling_rate=args.sampling_rate)
    
    # Generate plot
    if not args.no_plot:
        if args.plot is None:
            # Auto-generate plot filename
            plot_filename = os.path.join(args.output_dir, base_filename + '_plot.png')
        else:
            plot_filename = os.path.join(args.output_dir, args.plot)
        
        if args.kinetics == 'fast':
            plot_stimulus(
                time, current, plot_filename,
                title="Simulated EPSP - Fast-Rising (Double Exponential)",
                A1=args.A1, tau_rise1=args.tau_rise1, tau_decay1=args.tau_decay1,
                A2=args.A2, tau_rise2=args.tau_rise2, tau_decay2=args.tau_decay2
            )
        else:  # slow
            plot_stimulus(
                time, current, plot_filename,
                title="Simulated EPSP - Slow-Rising (Single Exponential)",
                A=args.A, tau_rise=args.tau_rise, tau_decay=args.tau_decay
            )
    
    # Print summary
    print("\nParameters used:")
    if args.kinetics == 'fast':
        print(f"  Type: Fast-rising (double exponential)")
        print(f"  A1 = {args.A1} pA, τrise1 = {args.tau_rise1} ms, τdecay1 = {args.tau_decay1} ms")
        print(f"  A2 = {args.A2} pA, τrise2 = {args.tau_rise2} ms, τdecay2 = {args.tau_decay2} ms")
    else:
        print(f"  Type: Slow-rising (single exponential)")
        print(f"  A = {args.A} pA, τrise = {args.tau_rise} ms, τdecay = {args.tau_decay} ms")
    
    # Print Clampex configuration instructions
    print("\n" + "="*70)
    print("CLAMPEX PROTOCOL CONFIGURATION")
    print("="*70)
    if args.uniform_sampling:
        print(f"Set your episodic protocol to:")
        print(f"  • Sampling Interval: {1.0/args.sampling_rate*1000:.6f} ms ({args.sampling_rate} Hz)")
        print(f"  • Number of samples: {len(time)}")
        print(f"  • Duration will be: {time[-1]:.6f} s")
    else:
        avg_dt = time[-1] / (len(time) - 1)
        equiv_rate = 1.0 / avg_dt
        print(f"For approximate timing, set your episodic protocol to:")
        print(f"  • Sampling Interval: {avg_dt*1000:.6f} ms (~{equiv_rate:.2f} Hz)")
        print(f"  • Number of samples: {len(time)}")
        print(f"  OR use --uniform_sampling flag for exact timing control")
    print(f"\nSet 'Sweeps per run' = 1")
    print("On Wave 0 page: Select 'Stimulus file' and load this ATF file")
    print("="*70)


if __name__ == "__main__":
    main()
