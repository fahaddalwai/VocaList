
# VocaList: Speech-Controlled To-Do List

**VocaList** is a voice-activated task management application designed to streamline task creation, updates, and deletions using natural language commands. This README provides detailed instructions on setting up and running the backend and frontend, including database configuration and dependencies.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
    - [Installation](#installation)
    - [Database Configuration](#database-configuration)
    - [Running the Backend](#running-the-backend)
3. [Frontend Setup](#frontend-setup)
    - [Running the Frontend](#running-the-frontend)
4. [Database Schema](#database-schema)
    - [User Table](#user-table)
    - [Task Table](#task-table)
5. [Dependencies](#dependencies)
6. [Project Structure](#project-structure)
7. [Contributing](#contributing)

---

## Prerequisites

Before setting up VocaList, ensure you have the following installed:

1. **Python** (Version 3.8 or above)
2. **MySQL** (Installed and running locally or on a remote server)
3. **Node.js and npm** (For the frontend)
4. **pip** (Python package manager)

---

## Backend Setup

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/nui-todo-llm.git
   cd nui-todo-llm/backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the required Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

### Database Configuration

1. **Open the `app.py` file** located in the `backend` folder.

2. **Update the database connection string** with your own MySQL username and password:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://<username>:<password>@localhost/todo_app"
   ```
   Replace `<username>` and `<password>` with your MySQL credentials.

3. **Create the `todo_app` database** in MySQL:
   ```sql
   CREATE DATABASE todo_app;
   ```

4. **Initialize the database tables:**
   Run the following in a Python shell or script:
   ```python
   from app import db
   db.create_all()
   print("Database tables created successfully!")
   ```

---

### Running the Backend

Run the backend server using the following command:
```bash
python -u "YOUR DIRECTORY\NUI TODO LLM\backend\main.py"
```

The backend will start at [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Frontend Setup

### Running the Frontend

1. **Navigate to the frontend folder:**
   ```bash
   cd ../frontend
   ```

2. **Install the frontend dependencies:**
   ```bash
   npm install
   ```

3. **Start the frontend server:**
   ```bash
   npm run
   ```

The frontend will be accessible at [http://localhost:3000](http://localhost:3000).

---

## Database Schema

### User Table
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"
```
- **Columns**:
  - `id`: Integer, primary key
  - `email`: String (120), unique, required
  - `password`: String (120), required

### Task Table
```python
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    reminder_time = db.Column(db.DateTime, nullable=True)  # New column for reminder time

    def __repr__(self):
        return f"<Task {self.title}>"
```
- **Columns**:
  - `id`: Integer, primary key
  - `user_id`: Foreign key referencing the `User` table
  - `title`: String (255), required
  - `description`: Text, optional
  - `created_at`: DateTime, defaults to current UTC time
  - `completed`: Boolean, defaults to `False`
  - `reminder_time`: DateTime, optional

---

## Dependencies

### Python Dependencies
- Flask==2.3.3  
- Flask-Bcrypt==1.0.1  
- Flask-SQLAlchemy==3.0.5  
- Cohere==4.9.0  
- SpeechRecognition==3.8.1  
- SQLAlchemy==2.0.20  
- PyMySQL==1.1.0  
- python-dotenv==1.0.0  
- flask-cors==3.0.10  

Install these via:
```bash
pip install -r requirements.txt
```

---

## Project Structure

```
nui-todo-llm/
├── backend/
│   ├── app.py            # Main application setup
│   ├── routes.py         # API routes
│   ├── models.py         # SQLAlchemy models
│   ├── requirements.txt  # Backend dependencies
├── frontend/
│   ├── src/              # Frontend source code
│   ├── package.json      # Frontend dependencies
└── README.md             # Project documentation
```

---

## Contributing

1. **Fork the repository.**

2. **Create a new feature branch:**
   ```bash
   git checkout -b feature-branch-name
   ```

3. **Commit your changes:**
   ```bash
   git commit -m "Your descriptive commit message"
   ```

4. **Push to the branch:**
   ```bash
   git push origin feature-branch-name
   ```

5. **Submit a pull request** for review.

---

Feel free to reach out for support or additional documentation needs!

