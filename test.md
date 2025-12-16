# 1) virtuele omgeving
if (!(Test-Path ".venv")) {
  py -3.11 -m venv .venv
}

# 2) dependencies
.\venv-the-mona\Scripts\python -m pip install -U pip
.\venv-the-mona\Scripts\pip install -r .\requirements.txt

# 5) start app
.\.venv\Scripts\activate
.\the-mona-app\apps\apps.main

## MQTT
lokaal via mosquitto mqtt
 & "C:\Program Files\mosquitto\mosquitto.exe" -v -c "C:\ZZZ_Projecten\GITHUB\TheMona\the-mona-app\tests\mqtt\mosquitto.conf"
