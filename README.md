https://github.com/ExistentialAudio/BlackHolehttps://github.com/ExistentialAudio/BlackHole

* brew update
* brew install blackhole-64ch

## How to route sound to Black Hole and Speakers

Step-by-step instructions:

1. Open Audio MIDI Setup
    * Press Cmd + Space (Spotlight)
    * Type "Audio MIDI Setup" and press Enter
2. Create Multi-Output Device
    * Click the + button at the bottom left
    * Select "Create Multi-Output Device"
3. Select both outputs
    * In the right panel, check both:
    * Your speakers/headphones (e.g., "MacBook Pro Speakers", "AirPods", etc.)
    * BlackHole 64ch
4. Set as system output
    * Open System Settings > Sound
    * Under Output, select your new Multi-Output Device (it may be named "Multi-Output Device" or you can rename it)
5. Test it
    * Play some audio (music, video, etc.)
    * You should hear it through your speakers
    * The script should show signal (✓ indicator and RMS > 0.001)

This routes audio to both your speakers and BlackHole, so you can hear it and capture it at the same time.

Note: You can rename the Multi-Output Device in Audio MIDI Setup by double-clicking its name. For example, "Speakers + BlackHole".