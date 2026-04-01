#!/bin/bash
# Connects JBL on boot, sets PulseAudio default sink, restarts the-mona.
# Waits for BlueZ to be ready, then tries up to 5 times.

MAC="2C:FD:B4:BE:73:C6"
SINK="bluez_sink.2C_FD_B4_BE_73_C6.a2dp_sink"
MAX_ATTEMPTS=5
RETRY_DELAY=8
MONA_UID=$(id -u mona)

export XDG_RUNTIME_DIR=/run/user/${MONA_UID}
export PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native

echo "[bt-connect] Waiting for BlueZ to be ready..."
sleep 10

# Wait until bluetoothctl is responsive
for i in $(seq 1 10); do
    if bluetoothctl show 2>/dev/null | grep -q "Powered: yes"; then
        echo "[bt-connect] BlueZ ready."
        break
    fi
    echo "[bt-connect] BlueZ not ready yet, waiting 3s..."
    sleep 3
done

echo "[bt-connect] Starting JBL connect sequence (max ${MAX_ATTEMPTS} attempts)"

for i in $(seq 1 $MAX_ATTEMPTS); do
    echo "[bt-connect] Attempt ${i}/${MAX_ATTEMPTS}..."

    if bluetoothctl connect "$MAC" 2>&1 | grep -q "Connection successful"; then
        echo "[bt-connect] Connected to JBL!"

        # Wait for PulseAudio to register the A2DP sink
        echo "[bt-connect] Waiting for A2DP sink..."
        sleep 5

        if pactl set-default-sink "$SINK"; then
            echo "[bt-connect] Default audio sink set to JBL"
        else
            echo "[bt-connect] WARNING: Could not set default sink, retrying in 3s..."
            sleep 3
            pactl set-default-sink "$SINK" && echo "[bt-connect] Sink set on retry."
        fi

        echo "[bt-connect] Restarting the-mona service..."
        systemctl restart the-mona

        echo "[bt-connect] Done."
        exit 0
    fi

    echo "[bt-connect] Attempt ${i} failed."
    if [ "$i" -lt "$MAX_ATTEMPTS" ]; then
        echo "[bt-connect] Retrying in ${RETRY_DELAY}s..."
        sleep $RETRY_DELAY
    fi
done

echo "[bt-connect] Could not connect to JBL after ${MAX_ATTEMPTS} attempts. the-mona will use fallback audio."
exit 1
