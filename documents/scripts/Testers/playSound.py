import subprocess
import os
import sys

# Bluetooth apparaatadres (JBL GO Essential)
DEVICE_ADDRESS = "2C:FD:B4:BE:73:C6"
# Pad naar het geluidsbestand
SOUND_FILE = "./PeppaPigRev02.wav"  # Vervang met jouw bestandspad
SOUND_FILE = "./meow.wav"  # Vervang met jouw bestandspad
# Gewenst volume (tussen 0 en 100)
VOLUME_LEVEL = 35  # Pas het volume aan naar wens

def set_volume(volume):
    if 0 <= volume <= 100:
        print(f"Setting volume to {volume}%...")
        # Verkrijg de sink ID van de Bluetooth speaker
        result = subprocess.run(
            ["pactl", "list", "sinks", "--short"], text=True, capture_output=True
        )
        sinks = result.stdout.splitlines()

        for sink in sinks:
            if "bluez_sink" in sink:
                sink_id = sink.split()[0]
                subprocess.run(["pactl", "set-sink-volume", sink_id, f"{volume}%"], check=True)
                break
    else:
        print("Error: Volume moet tussen 0 en 100 zijn.")
        sys.exit(1)

def connect_bluetooth(device_address):
    print("Starting Bluetooth service...")
    subprocess.run(["sudo", "systemctl", "start", "bluetooth"], check=True)

    print(f"Connecting to {device_address} (JBL GO Essential)...")
    bluetoothctl_commands = f"""
    power on
    agent on
    default-agent
    pair {device_address}
    trust {device_address}
    connect {device_address}
    exit
    """
    try:
        process = subprocess.run(
            ["bluetoothctl"], input=bluetoothctl_commands, text=True, check=True
        )
    except subprocess.CalledProcessError:
        print("Failed to execute Bluetoothctl commands.")
        sys.exit(1)

    # Controleer of de speaker succesvol is verbonden
    try:
        result = subprocess.run(
            ["bluetoothctl", "info", device_address],
            text=True,
            capture_output=True,
            check=True,
        )
        if "Connected: yes" in result.stdout:
            print(f"Bluetooth speaker {device_address} is connected.")
        else:
            print(f"Failed to connect to the Bluetooth speaker {device_address}.")
            sys.exit(1)
    except subprocess.CalledProcessError:
        print("Failed to check Bluetooth connection status.")
        sys.exit(1)

    # Stel PulseAudio sink in
    print("Setting default PulseAudio sink...")
    sink_name = f"bluez_sink.{device_address.replace(':', '_')}.a2dp_sink"
    subprocess.run(["pacmd", "set-default-sink", sink_name], check=True)

    print("JBL GO Essential setup complete.")

def play_sound(sound_file):
    if not os.path.isfile(sound_file):
        print(f"Error: Geluidsbestand '{sound_file}' bestaat niet.")
        sys.exit(1)

    # Afspelen met aplay (voor WAV-bestanden)
    print(f"Playing sound file: {sound_file}")
    try:
        subprocess.run(["aplay", sound_file], check=True)
    except subprocess.CalledProcessError:
        print("Failed to play the sound file.")
        sys.exit(1)

    print("Playback complete.")

if __name__ == "__main__":
    # Zet het volume in
    set_volume(VOLUME_LEVEL)

    # Verbinden met Bluetooth speaker
    connect_bluetooth(DEVICE_ADDRESS)

    # Speel het geluid af
    play_sound(SOUND_FILE)
