from flask import Flask
from routes import routes
import config
from flask import render_template


app = Flask(__name__)
app.config.from_object(config)

# Регистрируем Blueprint
app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
