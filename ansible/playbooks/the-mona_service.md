#Controleer status

systemctl status the-mona


#Draait app?

ps aux | grep app.py


#Service start up enabled?

systemctl is-enabled the-mona


#Bekijk logs
c

##live
journalctl -u the-mona -f


# Virtual env

## Activeer
source /home/mona/the-mona/.venv/bin/activate
## Installeer
pip install -r /home/mona/the-mona/requirements.txt

## indien fout
# Toon de laatste 100 regels log (zonder volgen)
journalctl -u the-mona -n 100 --no-pager

# Wie luistert op 8443?
sudo ss -lntp | grep :8443
sudo kill 554
sudo systemctl restart the-mona
sudo systemctl status the-mona --no-pager
journalctl -u the-mona -n 50 -f