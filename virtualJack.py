import sounddevice as sd
import soundfile as sf
import allUsage as au
import logging



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


def play_audio_files_to_vac(file_path, vac_device_id):
        data, samplerate = sf.read(file_path)
        #logging.info(f"Started Playing: {file_path}")
        sd.play(data, samplerate, device=vac_device_id)
        duration = data.shape[0] / samplerate
        au.monitor_performance(duration=duration)
        sd.stop()  # Stop playback




