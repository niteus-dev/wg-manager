import os

WG_INTERFACE = "wg0"
CONFIG_DIR = "/etc/wireguard"
CLIENTS_DIR = os.path.join(CONFIG_DIR, "clients")
NETWORK_CIDR = "10.80.0.0/22"
SERVER_IP = "10.80.0.1"
ALLOWED_IPS = "172.26.26.0/24"
SERVER_HOST = "172.26.26.1"
