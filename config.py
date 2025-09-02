import os

# Основные настройки WireGuard
WG_INTERFACE = "wg0"
CONFIG_DIR = "/etc/wireguard"
CLIENTS_DIR = os.path.join(CONFIG_DIR, "clients")
NETWORK_CIDR = "10.80.0.0/22"
SERVER_IP = "10.80.0.1"
ALLOWED_IPS = "172.26.26.0/24"
SERVER_HOST = "172.26.26.1"

# Настройки авторизации
AUTH_ENABLED = True  # Включить/выключить авторизацию

# Параметры для интеграции с PocketID
CLIENT_ID = os.environ.get("POCKETID_CLIENT_ID", "your_client_id_here")
CLIENT_SECRET = os.environ.get("POCKETID_CLIENT_SECRET", "your_client_secret_here")
REDIRECT_URI = os.environ.get("POCKETID_REDIRECT_URI", "http://localhost:8080/callback")
AUTH_URL = "https://pocketid.ru/oauth/authorize"
TOKEN_URL = "https://pocketid.ru/oauth/token"
USERINFO_URL = "https://pocketid.ru/api/v1/userinfo"
