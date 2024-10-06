from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
CORS(app)

# MySQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Divya%40204@localhost/todo_app"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Secret key for session management
app.config['SECRET_KEY'] = 'a_very_secret_key'

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from app import routes  # Import routes after app is initialized
