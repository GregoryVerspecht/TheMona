import subprocess
import sys

# Bluetooth apparaatadres (JBL GO Essential)
DEVICE_ADDRESS = "2C:FD:B4:BE:73:C6"

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
    except subprocess.CalledProcessError as e:
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

if __name__ == "__main__":
    connect_bluetooth(DEVICE_ADDRESS)
