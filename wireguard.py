import os
from utils import run_command, generate_keypair
import config
import subprocess

def generate_unique_ip():
    used_ips = set()
    for client in list_clients_with_ips():
        used_ips.add(client["ip"])

    server_ip = "10.80.0.1"

    for i in range(0, 4):  # 3-й октет: 0–3
        for j in range(1, 255):  # 4-й октет: 1–254
            ip = f"10.80.{i}.{j}"
            if ip == server_ip:
                continue  # пропускаем IP сервера
            if ip not in used_ips:
                return ip + "/22"

    raise Exception("No available IPs left in 10.80.0.0/22")

def add_client(name):
    print(f"[DEBUG] Добавление клиента: {name}")
    
    if not os.path.exists(config.CLIENTS_DIR):
        print(f"[DEBUG] Папка {config.CLIENTS_DIR} не существует, создаём...")
        os.makedirs(config.CLIENTS_DIR)

    print("[DEBUG] Генерация ключей клиента...")
    client_private_key, client_public_key = generate_keypair()
    print(f"[DEBUG] PrivateKey: {client_private_key[:10]}..., PublicKey: {client_public_key[:10]}...")

    print("[DEBUG] Генерация PresharedKey...")
    preshared_key = run_command(["wg", "genpsk"])
    print(f"[DEBUG] PresharedKey: {preshared_key[:10]}...")

    print("[DEBUG] Генерация уникального IP-адреса...")
    client_ip = generate_unique_ip()
    print(f"[DEBUG] Назначен IP: {client_ip}")

    print("[DEBUG] Получение публичного ключа сервера...")
    server_public_key = run_command(["wg", "show", config.WG_INTERFACE, "public-key"])
    print(f"[DEBUG] Server PublicKey: {server_public_key[:10]}...")

    client_config = f"""[Interface]
PrivateKey = {client_private_key}
Address = {client_ip}

[Peer]
PublicKey = {server_public_key}
PresharedKey = {preshared_key}
Endpoint = {config.SERVER_HOST}:51830
AllowedIPs = {config.SERVER_IP}/32
PersistentKeepalive = 25
"""

    client_config_path = os.path.join(config.CLIENTS_DIR, f"{name}.conf")
    print(f"[DEBUG] Сохраняем конфигурацию клиента в {client_config_path}")
    with open(client_config_path, "w") as f:
        f.write(client_config)

    print(f"[DEBUG] Добавляем клиента в конфигурацию WireGuard...")

    command = [
        "wg", "set", config.WG_INTERFACE,
        "peer", client_public_key,
        "preshared-key", "/dev/stdin",
        "allowed-ips", client_ip.split('/')[0]
    ]

    print(f"[DEBUG] Команда для добавления клиента:")
    print(f"        wg set {config.WG_INTERFACE} peer {client_public_key}")
    print(f"        preshared-key: (через stdin)")
    print(f"        allowed-ips: {client_ip.split('/')[0]}")

    print(f"[DEBUG] Выполняем команду: {' '.join(command)}")
    result = run_command(command, input_data=preshared_key) 
    print(f"[DEBUG] Результат выполнения wg set: {result}")

    print(f"[DEBUG] Сохраняем конфигурацию WireGuard...")
    save_result = run_command(["wg-quick", "save", config.WG_INTERFACE])
    print(f"[DEBUG] Результат сохранения конфигурации: {save_result}")

    print(f"[DEBUG] Клиент {name} успешно добавлен.")
    return client_config




def list_clients_with_ips():
    clients = []
    for filename in os.listdir(config.CLIENTS_DIR):
        if filename.endswith(".conf"):
            name = filename.replace(".conf", "")
            ip = None
            with open(os.path.join(config.CLIENTS_DIR, filename), "r") as f:
                for line in f:
                    if line.startswith("Address"):
                        ip = line.split(" = ")[1].strip().split("/")[0]
                        break
            clients.append({"name": name, "ip": ip})
    return clients

def delete_client(name):
    client_path = os.path.join(config.CLIENTS_DIR, f"{name}.conf")

    if not os.path.exists(client_path):
        return False

    private_key = None
    with open(client_path, "r") as f:
        for line in f:
            if line.startswith("PrivateKey"):
                private_key = line.split(" = ")[1].strip()
                break

    if private_key:
        public_key = run_command(["wg", "pubkey"], input_data=private_key)
        if public_key:
            run_command(["wg", "set", config.WG_INTERFACE, "peer", public_key, "remove"])

    os.remove(client_path)
    run_command(["wg-quick", "save", config.WG_INTERFACE])

    return True

def get_public_key(private_key):
    """Генерирует PublicKey из PrivateKey."""
    process = subprocess.Popen(["wg", "pubkey"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    public_key, error = process.communicate(input=f"{private_key}\n".encode())
    if process.returncode == 0:
        return public_key.decode().strip()
    else:
        print(f"Error generating PublicKey: {error.decode()}")
        return None

def suspend_client(name):
    """Отключает клиента, удаляя его пир из конфигурации WireGuard и переименовывая его конфигурационный файл."""
    print(f"Suspending client: {name}")
    client_path = os.path.join(config.CLIENTS_DIR, f"{name}.conf")
    suspended_client_path = os.path.join(config.CLIENTS_DIR, f"{name}_suspend.conf")

    if not os.path.exists(client_path):
        print(f"Client config {client_path} not found!")
        return False

    # Отключаем клиента, удаляя его пир из конфигурации WireGuard
    private_key = None
    with open(client_path, "r") as f:
        for line in f:
            if line.startswith("PrivateKey"):
                private_key = line.split(" = ")[1].strip()
                break

    if private_key:
        public_key = get_public_key(private_key)
        if public_key:
            print(f"Generated PublicKey: {public_key}")
            run_command(["wg", "set", config.WG_INTERFACE, "peer", public_key, "remove"])
            run_command(["wg-quick", "save", config.WG_INTERFACE])
            print("Client suspended successfully.")

            # Переименовываем файл конфигурации, добавляя _suspend
            os.rename(client_path, suspended_client_path)
            print(f"Config file renamed to: {suspended_client_path}")
            return True

    print("Failed to get PublicKey!")
    return False
def unsuspend_client(name):
    """Включает клиента, добавляя его пир обратно в конфигурацию WireGuard и переименовывая его конфигурационный файл."""
    print(f"Unsuspending client: {name}")
    suspended_client_path = os.path.join(config.CLIENTS_DIR, f"{name}_suspend.conf")
    client_path = os.path.join(config.CLIENTS_DIR, f"{name}.conf")

    if not os.path.exists(suspended_client_path):
        print(f"Suspended client config {suspended_client_path} not found!")
        return False

    # Включаем клиента, добавляя его пир обратно в конфигурацию WireGuard
    private_key, preshared_key, allowed_ips = None, None, None

    with open(suspended_client_path, "r") as f:
        for line in f:
            if line.startswith("PrivateKey"):
                private_key = line.split(" = ")[1].strip()
            elif line.startswith("PresharedKey"):
                preshared_key = line.split(" = ")[1].strip()
            elif line.startswith("Address"):
                allowed_ips = line.split(" = ")[1].strip().split("/")[0]

    if not private_key:
        print("PrivateKey not found in config!")
        return False

    if not allowed_ips:
        print("AllowedIPs not found in config!")
        return False

    # Генерация публичного ключа на основе приватного
    public_key = get_public_key(private_key)
    if not public_key:
        print("Failed to generate PublicKey!")
        return False

    print(f"Generated PublicKey: {public_key}, AllowedIPs: {allowed_ips}")

    # Формируем команду для добавления пира
    command = ["wg", "set", config.WG_INTERFACE, "peer", public_key, "allowed-ips", allowed_ips]

    if preshared_key:
        print(f"Using PresharedKey")
        # Мы добавляем preshared-key как ввод, а не как часть команды
        command.extend(["preshared-key", "/dev/stdin"])
        print(f"Running command: {' '.join(command)}")
        # Передаем preshared_key через stdin
        result = run_command(command, input_data=preshared_key)
    else:
        print(f"Running command: {' '.join(command)}")
        result = run_command(command)

    # Сохраняем конфигурацию
    run_command(["wg-quick", "save", config.WG_INTERFACE])
    print("Client unsuspended successfully.")

    # Переименовываем файл, убирая _suspend
    os.rename(suspended_client_path, client_path)
    print(f"Config file renamed to: {client_path}")
    return True
