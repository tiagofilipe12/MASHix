from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
print os.path.join(os.path.dirname( __file__ ), '..', 'config_default.py')
app.config.from_pyfile(os.path.join(os.path.dirname( __file__ ), '..', 'config_default.py'))
db = SQLAlchemy(app)

import views, models