# WireGuard Manager

A web-based management interface for WireGuard VPN servers, built with Python Flask. This application allows you to easily create, manage, and configure WireGuard clients through a user-friendly web interface.

![Sofit Logo](static/logo.webp)

## Features

- **Web Interface**: Clean, responsive UI built with Bootstrap for managing WireGuard clients
- **Client Management**: Create, view, delete, suspend, and unsuspend WireGuard clients
- **Automatic Configuration**: Generates complete WireGuard client configuration files
- **IP Management**: Automatically assigns unique IP addresses from the configured subnet
- **Search Functionality**: Easily find clients by name or IP address
- **Pagination**: Handles large numbers of clients with paginated views
- **Configuration Viewing**: View and copy client configurations directly from the web interface
- **API Endpoints**: RESTful API for programmatic client management

## Prerequisites

- Linux server with WireGuard installed
- Python 3.6+
- Flask
- WireGuard tools (`wg`, `wg-quick`)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/niteus-dev/wg-manager.git
   cd wg-manager
   ```

2. Install Python dependencies:
   ```bash
   pip install flask
   ```

3. Ensure WireGuard is installed and configured:
   ```bash
   # Ubuntu/Debian
   apt install wireguard wireguard-tools

   # CentOS/RHEL
   yum install wireguard-tools
   ```

4. Configure WireGuard server (example configuration in `/etc/wireguard/wg0.conf`):
   ```ini
   [Interface]
   Address = 10.80.0.1/22
   ListenPort = 51830
   PrivateKey = YOUR_SERVER_PRIVATE_KEY
   ```

5. Adjust configuration in `config.py` if needed:
   ```python
   WG_INTERFACE = "wg0"           # Your WireGuard interface name
   CONFIG_DIR = "/etc/wireguard"  # WireGuard configuration directory
   CLIENTS_DIR = os.path.join(CONFIG_DIR, "clients")  # Client configs directory
   NETWORK_CIDR = "10.80.0.0/22"  # VPN network range
   SERVER_IP = "10.80.0.1"        # Server IP in VPN network
   ALLOWED_IPS = "172.26.26.0/24" # IPs that clients can access
   SERVER_HOST = "172.26.26.1"    # Public IP/domain of your server
   ```

## Usage

1. Start the application:
   ```bash
   python app.py
   ```

2. Access the web interface at `http://your-server-ip:8080`

3. Create a new client:
   - Enter a client name in the input field
   - Click "Create Client"
   - Download or copy the generated configuration file

4. Manage clients:
   - **View**: Click "View" to see the client configuration
   - **Suspend/Unsuspend**: Toggle the switch to disable/enable a client
   - **Delete**: Click "Delete" to remove a client

## API Endpoints

- `GET /api/clients` - List all clients
- `POST /api/clients` - Create a new client (JSON: `{"name": "client_name"}`)
- `GET /api/client/<client_name>` - Get client configuration
- `POST /api/client/<client_name>/suspend` - Suspend a client
- `POST /api/client/<client_name>/unsuspend` - Unsuspend a client
- `POST /api/client/<client_name>/delete` - Delete a client

## Project Structure

```
wg-manager/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── routes.py           # URL routing and request handling
├── wireguard.py        # WireGuard client management functions
├── utils.py            # Utility functions
├── static/
│   └── logo.webp       # Application logo
└── templates/
    └── index.html      # Main web interface template
```

## Configuration

The application uses the following default configuration in `config.py`:

- **WG_INTERFACE**: `wg0` - WireGuard interface name
- **CONFIG_DIR**: `/etc/wireguard` - WireGuard configuration directory
- **CLIENTS_DIR**: `/etc/wireguard/clients` - Directory for storing client configurations
- **NETWORK_CIDR**: `10.80.0.0/22` - VPN network range (supports up to 1024 clients)
- **SERVER_IP**: `10.80.0.1` - Server IP within the VPN network
- **ALLOWED_IPS**: `172.26.26.0/24` - IPs accessible to VPN clients
- **SERVER_HOST**: `172.26.26.1` - Public IP or domain of your server

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Made with ❤️ at **Sofit**
- Built with [Flask](https://flask.palletsprojects.com/)
- UI powered by [Bootstrap](https://getbootstrap.com/)
