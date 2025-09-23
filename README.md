# WG Manager с авторизацией через PocketID и Basic Auth для API

Это приложение для управления клиентами WireGuard с возможностью авторизации через PocketID для веб-интерфейса и Basic Auth для API запросов.

## Настройка авторизации

### Включение/выключение авторизации

В файле `config.py` установите параметры:
- `AUTH_ENABLED` - включить/выключить авторизацию через PocketID для веб-интерфейса
- `API_AUTH_ENABLED` - включить/выключить авторизацию для API запросов

### Настройка PocketID

Для работы с PocketID необходимо установить следующие параметры в `config.py`:

```python
# Параметры для интеграции с PocketID
CLIENT_ID = os.environ.get("POCKETID_CLIENT_ID", "your_client_id_here")
CLIENT_SECRET = os.environ.get("POCKETID_CLIENT_SECRET", "your_client_secret_here")
REDIRECT_URI = os.environ.get("POCKETID_REDIRECT_URI", "http://localhost:8080/callback")
AUTH_URL = "https://pocketid.ru/oauth/authorize"
TOKEN_URL = "https://pocketid.ru/oauth/token"
USERINFO_URL = "https://pocketid.ru/api/v1/userinfo"
```

Рекомендуется устанавливать эти параметры через переменные окружения:

```bash
export POCKETID_CLIENT_ID="ваш_client_id"
export POCKETID_CLIENT_SECRET="ваш_client_secret"
export POCKETID_REDIRECT_URI="http://ваш_домен/callback"
export SECRET_KEY="ваш_секретный_ключ_для_сессий"
```

### Настройка Basic Auth для API

Для работы с API необходимо установить следующие параметры в `config.py`:

```python
# Параметры для Basic Auth API
API_USERNAME = os.environ.get("API_USERNAME", "admin")
API_PASSWORD = os.environ.get("API_PASSWORD", "password")
```

Рекомендуется устанавливать эти параметры через переменные окружения:

```bash
export API_USERNAME="ваш_api_пользователь"
export API_PASSWORD="ваш_api_пароль"
```

## Как это работает

### При включенной авторизации (AUTH_ENABLED = True):

1. Все маршруты (кроме `/login`, `/callback` и статических файлов) требуют авторизации
2. При попытке доступа к защищенному маршруту незалогиненный пользователь перенаправляется на `/login`
3. Маршрут `/login` перенаправляет пользователя на страницу авторизации PocketID
4. После успешной авторизации пользователь возвращается на маршрут `/callback`
5. В `/callback` происходит обмен кода авторизации на токен доступа и получение информации о пользователе
6. Информация о пользователе сохраняется в сессии
7. Пользователь перенаправляется на главную страницу
8. При выходе маршрут `/logout` очищает сессию и перенаправляет на страницу входа

### При выключенной авторизации (AUTH_ENABLED = False):

Приложение работает как раньше, без какой-либо проверки авторизации.

## Пример использования

1. Установите параметры авторизации через переменные окружения
2. Установите `AUTH_ENABLED = True` в `config.py`
3. Запустите приложение: `python app.py`
4. Откройте в браузере `http://localhost:8080`
5. Вы будете автоматически перенаправлены на страницу входа
6. Нажмите на кнопку входа через PocketID
7. После успешной авторизации вы попадете на главную страницу приложения

## Использование API с Basic Auth

Для выполнения запросов к API необходимо использовать Basic Auth с настроенными учетными данными:

```bash
# Получение списка клиентов
curl -u admin:password http://localhost:8080/api/clients

# Создание нового клиента
curl -u admin:password -H "Content-Type: application/json" -d '{"name":"newclient"}' http://localhost:8080/api/clients

# Получение конфигурации клиента
curl -u admin:password http://localhost:8080/api/client/client_name

# Отключение клиента
curl -u admin:password -X POST http://localhost:8080/api/client/client_name/suspend

# Включение клиента
curl -u admin:password -X POST http://localhost:8080/api/client/client_name/unsuspend

# Удаление клиента
curl -u admin:password -X POST http://localhost:8080/api/client/client_name/delete
```

Замените `admin:password` на ваши учетные данные, установленные в `API_USERNAME` и `API_PASSWORD`.

## API маршруты

- `GET /` - Главная страница со списком клиентов (требует авторизации если включена)
- `POST /` - Создание нового клиента (требует авторизации если включена)
- `GET /api/clients` - Получение списка клиентов в формате JSON (требует авторизации если включена)
- `POST /api/clients` - Создание нового клиента через API (требует авторизации если включена)
- `GET /api/client/<client_name>` - Получение конфигурации клиента (требует авторизации если включена)
- `GET /client/<client_name>` - Скачивание конфигурационного файла клиента (требует авторизации если включена)
- `POST /client/<name>/delete` - Удаление клиента (требует авторизации если включена)
- `POST /api/client/<client_name>/suspend` - Отключение клиента (требует авторизации если включена)
- `POST /api/client/<client_name>/unsuspend` - Включение клиента (требует авторизации если включена)
- `POST /api/client/<client_name>/delete` - Удаление клиента через API (требует авторизации если включена)
- `GET /login` - Страница входа через PocketID (доступна всегда)
- `GET /callback` - Обработчик ответа от PocketID (доступен всегда)
- `GET /logout` - Выход из системы (требует авторизации если включена)

## Зависимости

Убедитесь, что установлены все необходимые зависимости:

```bash
pip install flask requests
