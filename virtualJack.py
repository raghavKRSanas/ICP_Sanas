import os
import sounddevice as sd
import soundfile as sf
import time

 
def list_sound_devices():
    """
    List all available sound devices along with their device IDs and additional details.
    """
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        print(f"Device {idx}:")
        print(f"    Name: {device['name']}")
        print(f"    Host API: {device['hostapi']}")  # Host API ID
        print(f"    API Name: {sd.query_hostapis(device['hostapi'])['name']}")  # Host API name
        print(f"    Max Input Channels: {device['max_input_channels']}")
        print(f"    Max Output Channels: {device['max_output_channels']}")
        print(f"    Default Sample Rate: {device['default_samplerate']} Hz")
        print(f"    Input: {'Yes' if device['max_input_channels'] > 0 else 'No'}")
        print(f"    Output: {'Yes' if device['max_output_channels'] > 0 else 'No'}")
        print()
        if "Line 1 (Virtual Audio Cable)" in device['name'] and device['max_output_channels']>0:
             return idx


def play_audio_files_to_vac(file_paths, vac_device_id):
    for file_path in file_paths:
        print(f"Playing: {file_path}")
        data, samplerate = sf.read(file_path)
        sd.play(data, samplerate, device=vac_device_id)
        time.sleep(data.shape[0] / samplerate)  # Sleep duration based on audio duration
        sd.stop()  # Stop playback

