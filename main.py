import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_scss import Scss
from flask_session import Session

app = Flask(__name__)
app.debug = os.getenv('DEBUG').lower() == 'true'

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
if app.debug:
    app_scss = Scss(app, static_dir='static', asset_dir='assets')
    # change default output css style
    app_scss.compiler.output_style = 'expanded'

app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
app.config['SESSION_FILE_THRESHOLD'] = 100
app.secret_key = 'super secret key'
app.config.from_object(__name__)
Session(app)

from routes.item import item_bp
from routes.employee import employee_bp
from routes.order import order_bp
from routes.firm import firm_bp
from routes.view import view_bp
app.register_blueprint(item_bp, url_prefix='/item')
app.register_blueprint(employee_bp, url_prefix='/employee')
app.register_blueprint(order_bp, url_prefix='/order')
app.register_blueprint(firm_bp, url_prefix='/firm')
app.register_blueprint(view_bp, url_prefix='/')


if __name__ == "__main__":
    app.run(port=80)