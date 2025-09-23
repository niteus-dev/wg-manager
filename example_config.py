"""
Пример файла конфигурации для wg-manager с авторизацией через PocketID и Basic Auth для API
"""

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
# Установите в False, чтобы отключить авторизацию (приложение будет работать как раньше)
AUTH_ENABLED = True  # Включить/выключить авторизацию через PocketID
API_AUTH_ENABLED = True  # Включить/выключить авторизацию для API

# Параметры для интеграции с PocketID
# Рекомендуется устанавливать через переменные окружения
CLIENT_ID = os.environ.get("POCKETID_CLIENT_ID", "ваш_client_id_здесь")
CLIENT_SECRET = os.environ.get("POCKETID_CLIENT_SECRET", "ваш_client_secret_здесь")
REDIRECT_URI = os.environ.get("POCKETID_REDIRECT_URI", "http://172.26.26.50:8080/callback")
AUTH_URL = "https://pocketid.ru/oauth/authorize"
TOKEN_URL = "https://pocketid.ru/oauth/token"
USERINFO_URL = "https://pocketid.ru/api/v1/userinfo"

# Параметры для Basic Auth API
API_USERNAME = os.environ.get("API_USERNAME", "admin")
API_PASSWORD = os.environ.get("API_PASSWORD", "password")

# Пример установки переменных окружения:
# export POCKETID_CLIENT_ID="ваш_реальный_client_id"
# export POCKETID_CLIENT_SECRET="ваш_реальный_client_secret"
# export POCKETID_REDIRECT_URI="http://ваш_домен:8080/callback"
# export SECRET_KEY="ваш_секретный_ключ_для_сессий"
# export API_USERNAME="ваш_api_пользователь"
# export API_PASSWORD="ваш_api_пароль"
