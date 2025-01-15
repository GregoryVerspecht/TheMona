#!/bin/bash

# Bluetooth apparaatadres (JBL GO Essential)
DEVICE_ADDRESS="2C:FD:B4:BE:73:C6"

# Start de Bluetooth-service
echo "Starting Bluetooth service..."
sudo systemctl start bluetooth

# Bluetoothctl commando's uitvoeren
echo "Connecting to $DEVICE_ADDRESS (JBL GO Essential)..."
echo -e "power on\nagent on\ndefault-agent\npair $DEVICE_ADDRESS\ntrust $DEVICE_ADDRESS\nconnect $DEVICE_ADDRESS\nexit" | bluetoothctl

# Controleer of de speaker succesvol is verbonden
if bluetoothctl info $DEVICE_ADDRESS | grep -q "Connected: yes"; then
    echo "Bluetooth speaker $DEVICE_ADDRESS is connected."
else
    echo "Failed to connect to the Bluetooth speaker $DEVICE_ADDRESS."
    exit 1
fi

# Stel PulseAudio sink in (voor audio output)
echo "Setting default PulseAudio sink..."
pacmd set-default-sink bluez_sink.$(echo $DEVICE_ADDRESS | tr ':' '_').a2dp_sink

echo "JBL GO Essential setup complete."
