from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__, static_folder='static')
CORS(app, supports_credentials=True)

# MySQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://fahad:fahad159@localhost/todo_app"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Secret key for JWT encoding/decoding
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Replace with your actual JWT secret key

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from app import routes  # Import routes after app is initialized
