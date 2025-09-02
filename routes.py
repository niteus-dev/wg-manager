from flask import Blueprint, request, jsonify, send_file, render_template, redirect, url_for, session, abort, g
import os
import requests
from urllib.parse import urlencode
from wireguard import add_client, list_clients_with_ips, delete_client, suspend_client, unsuspend_client
import config
import math
from ipaddress import ip_address

routes = Blueprint("routes", __name__)

# Делаем сессию доступной в шаблонах
@routes.context_processor
def inject_session():
    return dict(session=session)

# Middleware для проверки авторизации
@routes.before_request
def check_auth():
    # Если авторизация отключена, пропускаем проверку
    if not config.AUTH_ENABLED:
        return None
    
    # Разрешаем доступ к маршрутам авторизации без проверки
    allowed_routes = ['routes.login', 'routes.callback', 'static']
    if request.endpoint in allowed_routes:
        return None
    
    # Проверяем, авторизован ли пользователь
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    
    return None

# Маршрут для входа через PocketID
@routes.route("/login")
def login():
    # Если авторизация отключена, перенаправляем на главную
    if not config.AUTH_ENABLED:
        return redirect(url_for('routes.index'))
    
    # Формируем параметры для авторизации через PocketID
    params = {
        'client_id': config.CLIENT_ID,
        'redirect_uri': config.REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid profile email'
    }
    
    # Перенаправляем пользователя на страницу авторизации PocketID
    auth_url = f"{config.AUTH_URL}?{urlencode(params)}"
    return redirect(auth_url)

# Маршрут для обработки callback от PocketID
@routes.route("/callback")
def callback():
    # Если авторизация отключена, перенаправляем на главную
    if not config.AUTH_ENABLED:
        return redirect(url_for('routes.index'))
    
    # Получаем код авторизации из параметров запроса
    code = request.args.get('code')
    if not code:
        return "Authorization code not provided", 400
    
    # Обмениваем код на токен доступа
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': config.CLIENT_ID,
        'client_secret': config.CLIENT_SECRET,
        'redirect_uri': config.REDIRECT_URI,
        'code': code
    }
    
    try:
        # Отправляем запрос на получение токена
        token_response = requests.post(config.TOKEN_URL, data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        # Получаем информацию о пользователе
        headers = {'Authorization': f"Bearer {token_info['access_token']}"}
        user_response = requests.get(config.USERINFO_URL, headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # Сохраняем информацию о пользователе в сессии
        session['user'] = {
            'id': user_info.get('sub'),
            'name': user_info.get('name'),
            'email': user_info.get('email')
        }
        
        # Перенаправляем на главную страницу
        return redirect(url_for('routes.index'))
        
    except requests.RequestException as e:
        return f"Error during authentication: {str(e)}", 500
    except KeyError as e:
        return f"Missing data in authentication response: {str(e)}", 500

# Маршрут для выхода
@routes.route("/logout")
def logout():
    # Удаляем информацию о пользователе из сессии
    session.pop('user', None)
    return redirect(url_for('routes.login'))

@routes.route("/", methods=["GET", "POST"])
def index():
    if not os.path.exists(config.CLIENTS_DIR):
        os.makedirs(config.CLIENTS_DIR)

    if request.method == "POST":
        client_name = request.form.get("client_name")
        if client_name:
            add_client(client_name)
            return redirect(url_for("routes.index"))  # Исправлено

    page = request.args.get("page", 1, type=int)
    search_query = request.args.get("search", "").strip().lower()

    clients = list_clients_with_ips()
    if search_query:
        clients = [c for c in clients if search_query in c["name"].lower() or search_query in c["ip"]]
    clients.sort(key=lambda c: ip_address(c["ip"]))

    PER_PAGE = 50
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    paginated_clients = clients[start:end]
    has_next_page = len(clients) > end

    # Новое:
    total_clients = len(clients)
    total_pages = math.ceil(total_clients / PER_PAGE)

    return render_template(
        "index.html",
        clients=paginated_clients,
        page=page,
        has_next_page=has_next_page,
        total_pages=total_pages,  # новое
        search_query=search_query
    )
    

@routes.route("/api/clients", methods=["GET"])
def list_clients():
    return jsonify(list_clients_with_ips())

@routes.route("/api/clients", methods=["POST"])
def create_client():
    name = request.json.get("name")
    if not name:
        return jsonify({"error": "Client name is required"}), 400
    try:
        config_data = add_client(name)
        return jsonify({"message": "Client created", "config": config_data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route("/api/client/<client_name>")
def get_client_config(client_name):
    client_config_path = os.path.join(config.CLIENTS_DIR, f"{client_name}.conf")
    if os.path.exists(client_config_path):
        with open(client_config_path, "r") as f:
            config_data = f.read()
        return jsonify({"name": client_name, "config": config_data})
    return jsonify({"error": "Client not found"}), 404

@routes.route("/client/<client_name>")
def view_client(client_name):
    client_config_path = os.path.join(config.CLIENTS_DIR, f"{client_name}.conf")
    if os.path.exists(client_config_path):
        return send_file(client_config_path, as_attachment=True)
    return "Client not found", 404

@routes.route("/client/<name>/delete", methods=["POST"])
def remove_client(name):
    if delete_client(name):
        return redirect(url_for("routes.index"))  # Исправлено
    return "Client not found", 404

@routes.route("/api/client/<client_name>/suspend", methods=["POST"])
def api_suspend_client(client_name):
    if suspend_client(client_name):
        return jsonify({"message": f"Client {client_name} suspended"}), 200
    return jsonify({"error": "Client not found"}), 404

@routes.route("/api/client/<client_name>/unsuspend", methods=["POST"])
def api_unsuspend_client(client_name):
    if unsuspend_client(client_name):
        return jsonify({"message": f"Client {client_name} unsuspended"}), 200
    return jsonify({"error": "Client not found"}), 404

@routes.route("/api/client/<client_name>/delete", methods=["POST"])
def api_delete_client(client_name):
    if delete_client(client_name):
        return jsonify({"message": f"Client {client_name} deleted"}), 200
    return jsonify({"error": "Client not found"}), 404
