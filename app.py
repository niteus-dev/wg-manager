from flask import Flask, session
from routes import routes
import config
from flask import render_template
import os


app = Flask(__name__)
app.config.from_object(config)

# Необходимо для работы сессий
app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-here")

# Регистрируем Blueprint
app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
