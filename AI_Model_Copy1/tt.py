# import sounddevice as sd
# print(sd.query_devices())

# import sounddevice as sd

# device_id = 9  # Use your device ID
# for samplerate in [16000, 32000, 44100, 48000]:
#     try:
#         with sd.InputStream(samplerate=samplerate, device=device_id, channels=1):
#             print(f"Device {device_id} supports samplerate {samplerate}")
#     except Exception as e:
#         print(f"Device {device_id} does not support samplerate {samplerate}: {e}")

import sounddevice as sd
import numpy as np

def audio_callback(indata, frames, time, status):
    if status:
        print(status, flush=True)
    # Process audio data
    audio_array = np.frombuffer(indata, dtype=np.float32)
    print("Audio Input Detected:", audio_array)

def test_audio_input():
    samplerate = 48000  # Use the correct sample rate
    device_id = 9  # Adjust if necessary

    with sd.InputStream(samplerate=samplerate, device=device_id, channels=1, callback=audio_callback):
        print("Recording... Press Ctrl+C to stop.")
        try:
            while True:
                pass  # Keep the stream open
        except KeyboardInterrupt:
            print("Stopped recording.")

if __name__ == "__main__":
    test_audio_input()


