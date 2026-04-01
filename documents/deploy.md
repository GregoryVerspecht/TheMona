# Deploy naar Raspberry Pi

De backend (FastAPI) serveert zowel de API als de gebouwde Astro frontend.
Alles draait op poort **8080**, bereikbaar via `http://192.168.69.69:8080`.

---

## Eerste keer opzetten

### 1. Pi voorbereiden (eenmalig via SSH)

```bash
ssh mona@192.168.69.69

# Gebruiker aanmaken (als nog niet bestaat)
sudo adduser mona

# Mappen aanmaken
mkdir -p /home/mona/the-mona-app/backend
mkdir -p /home/mona/the-mona-app/config
mkdir -p /home/mona/the-mona-app/frontend/dist

# Python
sudo apt install -y python3 python3-venv python3-pip

# Audio (pygame + Bluetooth)
sudo apt install -y libsdl2-mixer-2.0-0 pulseaudio pulseaudio-module-bluetooth
```

### 2. Code kopiëren naar Pi (vanuit Windows)

Vanuit de root van het project (`TheMona/`):
gebruik gitbash terminal in vscode
! Verbonden met de LAN

```bash
scp -r the-mona-app/backend/* mona@the-mona.local:/home/mona/the-mona-app/backend/
scp the-mona-app/requirements.txt mona@the-mona.local:/home/mona/the-mona-app/backend/
scp -r the-mona-app/config/* mona@the-mona.local:/home/mona/the-mona-app/config/
```

> De frontend dist hoef je hier nog niet te kopiëren — die is nog niet gebouwd.

### 3. Python venv aanmaken (eenmalig op de Pi)

```bash
ssh mona@192.168.69.69

cd /home/mona/the-mona-app/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 4. Bluetooth audio instellen (eenmalig op de Pi)

PulseAudio moet de Bluetooth module laden bij opstart:

```bash
# Voeg BT modules toe aan PulseAudio config
echo "load-module module-bluetooth-discover" | sudo tee -a /etc/pulse/default.pa
echo "load-module module-bluetooth-policy"   | sudo tee -a /etc/pulse/default.pa
```

JBL koppelen (eenmalig):

```bash
bluetoothctl
# In de prompt:
#   scan on
#   pair 2C:FD:B4:BE:73:C6
#   trust 2C:FD:B4:BE:73:C6
#   connect 2C:FD:B4:BE:73:C6
#   exit
```

JBL als standaard audio-uitvoer instellen (na elke verbinding):

```bash
pactl set-default-sink bluez_sink.2C_FD_B4_BE_73_C6.a2dp_sink
```

> **Let op:** de default sink reset bij reboot. Zie sectie "Na reboot" onderaan.

### 5. Systemd service aanmaken (eenmalig op de Pi)

```bash
sudo tee /etc/systemd/system/the-mona.service > /dev/null << 'EOF'
[Unit]
Description=The Mona
After=network.target mosquitto.service

[Service]
User=mona
WorkingDirectory=/home/mona/the-mona-app
ExecStart=/home/mona/the-mona-app/backend/.venv/bin/python backend/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable the-mona
```

---

## Elke deploy

### Stap 1 — Frontend bouwen (lokaal)

```bash
cd the-mona-app/frontend
npm run build
```

### Stap 2 — Code kopiëren naar Pi

Vanuit de root van het project (`TheMona/`):

```bash
scp -r the-mona-app/backend/* mona@the-mona.local:/home/mona/the-mona-app/backend/
scp the-mona-app/requirements.txt mona@the-mona.local:/home/mona/the-mona-app/backend/
scp -r the-mona-app/config/* mona@the-mona.local:/home/mona/the-mona-app/config/
scp -r the-mona-app/frontend/dist/* mona@the-mona.local:/home/mona/the-mona-app/frontend/dist/
```

### Stap 3 — Dependencies bijwerken (alleen na requirements.txt wijziging)

```bash
ssh mona@the-mona.local \
  "cd /home/mona/the-mona-app/backend && .venv/bin/pip install -r requirements.txt"
```

### Stap 4 — Service herstarten

```bash
ssh mona@192.168.69.69 "sudo systemctl restart the-mona"
```

---

## Logs bekijken

```bash
ssh mona@192.168.69.69 "journalctl -u the-mona -f"
```

---

## Netwerk

| Situatie | IP |
|---|---|
| Verbonden via Pi hotspot (The-Mona) | `192.168.69.69` |
| Verbonden via thuis-wifi | `192.168.1.12` (zie ansible/inventory/inventory) |

---

## Na reboot: JBL opnieuw verbinden

De Bluetooth verbinding en default sink resetten bij reboot. Voer dit uit na elke reboot:

```bash
bluetoothctl connect 2C:FD:B4:BE:73:C6
pactl set-default-sink bluez_sink.2C_FD_B4_BE_73_C6.a2dp_sink
sudo systemctl restart the-mona
```

---

## Structuur op de Pi

```
/home/mona/the-mona-app/
├── backend/          ← FastAPI app + .venv
│   ├── .venv/
│   ├── main.py
│   ├── requirements.txt
│   └── ...
├── config/           ← config.yaml
└── frontend/
    └── dist/         ← gebouwde Astro site (door FastAPI geserveerd)
```
