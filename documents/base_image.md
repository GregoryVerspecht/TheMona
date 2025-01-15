# Init setup

## OS Version


## Setup base image (First run)

- Generated with the pi imager 
- custom build

##Parameters

- hostname: the-mona.local
- username: mona
- password: liesa
- ssh: enabled (password enabled)
- DHCP

# Extended setup

See Ansible (ansible-playbook -i ansible/inventory ansible/playbooks/setup-dev.yaml
)

## known problems

- rfkill --> manual action: cli "sudo raspi-config" > options > wlan country > "BE" 