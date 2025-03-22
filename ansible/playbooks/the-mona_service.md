#Controleer status

systemctl status the-mona


#Draait app?

ps aux | grep app.py


#Service start up enabled?

systemctl is-enabled the-mona


#Bekijk logs
journalctl -u the-mona

##live
journalctl -u the-mona -f


# Virtual env

## Activeer
source /home/mona/the-mona/.venv/bin/activate
## Installeer
pip install -r /home/mona/the-mona/requirements.txt
