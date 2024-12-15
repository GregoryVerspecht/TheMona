# Virtualisatie testopstelling

## Dev environment

### Tools

- VMware workstation Pro
- OS: Raspberry Pi OS - Lite (64 Bit) --> geen nood aan desktop versie, kosten wat drukken --> webapp
[Raspberry Pi OS](https://www.raspberrypi.com/software/operating-systems/) (Deze versie is op debian 12 (bookworm))
- Opgesteld op een windows 11 pc


### Aanmaken VM

1. Nieuwe VM aanmaken:
- Open VMware Workstation Pro en kies "Create a New Virtual Machine".
- Selecteer "Typical" voor een eenvoudige setup.

2. OS selecteren:
- Kies "I will install the operating system later".
- Selecteer Linux > Debian 12 64-bit (Raspberry Pi OS is gebaseerd op Debian 12 bookworm).

3. Naam en locatie:
- Geef de VM een naam, bijvoorbeeld: TheMona.
- Kies een opslaglocatie met voldoende ruimte.

4. Hardware configureren:
- CPU: 2 cores.
- RAM: 2 GB (meer als je web- of simulatiefunctionaliteit nodig hebt).
- Disk: 16 GB (dynamisch uitbreidend).
- Netwerkadapter: Kies "Bridged" zodat de VM hetzelfde netwerk gebruikt als je smartphone.

5. OS toevoegen: (Opgepast is geen iso file maar image)
TODO: uitzoeken convertie

- Download de Raspberry Pi OS (64-bit Lite) image.
- Voeg deze toe als opstart-medium in de CD/DVD (SATA)-instellingen.

6. Start de VM:
- Boot vanaf de ISO en volg de installatie-instructies.

