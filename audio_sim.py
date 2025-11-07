import numpy as np
import sounddevice as sd
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import threading

# Shared data storage for thread-safe access
data_lock = threading.Lock()
bass_history = deque(maxlen=200)
mid_history = deque(maxlen=200)
treble_history = deque(maxlen=200)
beat_flags = deque(maxlen=200)  # Track beats for visualization
recent_bass = deque(maxlen=20)  # Keep last 20 bass values for beat detection
samples_since_last_beat = 0
current_sample = 0
last_beat_sample = -1  # Track when last beat was detected (sample index)
BEAT_COOLDOWN = 15  # Minimum samples between beats (prevents multiple detections per beat)

def analyze_audio(indata, frames, time_info, status):
    global last_beat_sample
    global samples_since_last_beat
    global last_beat_sample
    
    samples = indata[:, 0]
    fft = np.abs(np.fft.rfft(samples))
    freqs = np.fft.rfftfreq(len(samples), 1/44100)

    bass = np.mean(fft[(freqs >= 20) & (freqs < 250)])
    mid = np.mean(fft[(freqs >= 250) & (freqs < 4000)])
    treble = np.mean(fft[(freqs >= 4000) & (freqs < 16000)])
    
    # Simple beat detection: compare current bass to recent average
    with data_lock:
        recent_bass.append(bass)
        current_sample = len(bass_history)  # Current sample index
        
        beat = 0
        if len(recent_bass) >= 5:  # Need at least 5 samples
            recent_avg = np.mean(list(recent_bass)[:-1])  # Average of previous values (not including current)
            # Calculate samples since last beat for display
            samples_since_last_beat = current_sample - last_beat_sample
            # Beat if current bass is 1.5x higher than recent average
            # AND enough time has passed since last beat (cooldown period)
            print(f"""
            ┌─────────────────────────────────────┬──────────────────────┐
            │ Metric                             │ Value                │
            ├─────────────────────────────────────┼──────────────────────┤
            │ Bass                               │ {bass:>18.2f}        │
            │ Recent Average                     │ {recent_avg:>18.2f}        │
            │ Bass > Recent Avg * 1.5            │ {str(bass > recent_avg * 1.5):>18}        │
            │ Samples Since Last Beat            │ {samples_since_last_beat:>18}        │
            │ Cooldown Satisfied                 │ {str(samples_since_last_beat >= BEAT_COOLDOWN):>18}        │
            │ Beat Detected                      │ {beat:>18}        │
            │ Last Beat Sample                   │ {last_beat_sample:>18}        │
            │ Current Sample                     │ {current_sample:>18}        │
            └─────────────────────────────────────┴──────────────────────┘
            """)
            if bass > recent_avg * 1.5:
                if samples_since_last_beat >= BEAT_COOLDOWN:
                    beat = 1
                    print("last beat sample before: {last_beat_sample}")
                    last_beat_sample = current_sample
                    print("last beat sample after: {last_beat_sample}")
        
        # Store values for visualization
        bass_history.append(bass)
        mid_history.append(mid)
        treble_history.append(treble)
        beat_flags.append(beat == 1)

    # print(f"{int(bass):4d},{int(mid):4d},{int(treble):4d},{beat}")

def update_plot(frame):
    with data_lock:
        bass_data = list(bass_history)
        mid_data = list(mid_history)
        treble_data = list(treble_history)
        beats = list(beat_flags)
    
    ax.clear()
    
    if len(bass_data) > 0:
        x = np.arange(len(bass_data))
        ax.plot(x, bass_data, label='Bass', color='blue', linewidth=2)
        ax.plot(x, mid_data, label='Mid', color='green', linewidth=2)
        ax.plot(x, treble_data, label='Treble', color='red', linewidth=2)
        
    ax.set_ylabel('Amplitude')
    ax.set_xlabel('Time (samples)')
    ax.set_title('Real-time Audio Frequency Analysis')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    # Set y-axis limits based on current data
    if bass_data or mid_data or treble_data:
        max_val = max(
            max(bass_data) if bass_data else 0,
            max(mid_data) if mid_data else 0,
            max(treble_data) if treble_data else 0
        )
        ax.set_ylim(0, max_val * 1.1)
        y_max = max_val * 1.1
    else:
        ax.set_ylim(0, 100)
        y_max = 100
    
    # Draw vertical lines for beats (after setting y-axis)
    if len(bass_data) > 0:
        beat_positions = [i for i, is_beat in enumerate(beats) if is_beat]
        if beat_positions:
            ax.vlines(beat_positions, 0, y_max, colors='orange', linestyles='--', 
                     linewidth=2, alpha=0.7, label='Beat')

# Set up the plot
fig, ax = plt.subplots(figsize=(12, 6))
plt.ion()

# Start the animation
ani = animation.FuncAnimation(fig, update_plot, interval=50, blit=False, cache_frame_data=False)
plt.show(block=False)

# Run stream
try:
    with sd.InputStream(callback=analyze_audio, channels=1, samplerate=44100, blocksize=1024):
        while True:
            plt.pause(0.1)
            time.sleep(0.1)
except KeyboardInterrupt:
    print("\nStopping...")
    plt.close()
