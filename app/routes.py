from flask import request, jsonify, session
from app import app, db, bcrypt
from app.models import *
import speech_recognition as sr
from flask import request, jsonify, session
from app import *
from .llm_utils import process_speech_to_task
from app.models import Task

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the To-Do App API!"}), 200


# Register route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Check if user already exists
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"message": "User already exists"}), 400

    # Hash password and create user
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Find the user by email
    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    # Set session for logged-in user
    session['user_id'] = user.id
    return jsonify({"message": "Login successful"}), 200


# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out"}), 200


# Create a new task
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    reminder_time = data.get('reminder_time')  # Get reminder_time from the request

    new_task = Task(
        title=title, 
        description=description, 
        reminder_time=reminder_time,  # Save reminder_time in the database
        user_id=session['user_id']
    )
    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        "message": "Task created successfully", 
        "task": {
            "id": new_task.id, 
            "title": new_task.title, 
            "reminder_time": new_task.reminder_time
        }
    }), 201


# Get all tasks for the logged-in user
@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "reminder_time": task.reminder_time
    } for task in tasks]), 200


# Update a task
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    task = Task.query.get_or_404(task_id)

    if task.user_id != session['user_id']:
        return jsonify({"message": "You do not have permission to edit this task"}), 403

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)
    task.reminder_time = data.get('reminder_time', task.reminder_time)  # Update reminder_time

    db.session.commit()
    return jsonify({"message": "Task updated successfully"}), 200


# Delete a task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != session['user_id']:
        return jsonify({"message": "You do not have permission to delete this task"}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted successfully"}), 200


# Get a task by ID for the logged-in user
@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task_for_user(task_id):
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    
    if task is None:
        return jsonify({"message": "Task not found or you do not have permission to view this task"}), 404
    
    task_data = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "reminder_time": task.reminder_time
    }
    
    return jsonify(task_data), 200



@app.route('/create-task-from-speech', methods=['POST'])
def create_task_from_speech():
    recognizer = sr.Recognizer()

    # Check if an audio file is provided in the request
    if 'audio' not in request.files:
        return jsonify({"error": "Audio file not provided"}), 400
    
    audio_file = request.files['audio']

    # Convert speech to text
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            speech_text = recognizer.recognize_google(audio_data)  # Or any speech-to-text service
            print(f"Speech Text: {speech_text}")  # Log the speech-to-text output
        except sr.UnknownValueError:
            return jsonify({"error": "Speech could not be understood"}), 400
        except sr.RequestError:
            return jsonify({"error": "Speech service is not available"}), 500

    # Use the LLM to extract task details
    task_details = process_speech_to_task(speech_text)

    if not task_details['title'] and task_details['action_type'] != 'delete':
        return jsonify({"error": "Could not extract task title"}), 400

    # Convert reminder time if available
    reminder_time = None
    if task_details['reminder_time']:
        print(task_details['reminder_time'])
        try:
            reminder_time = datetime.strptime(task_details['reminder_time'], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify({"error": "Invalid reminder time format, expected 'YYYY-MM-DD HH:MM:SS'"}), 400

    action_type = task_details['action_type'].lower()

    # Handle different action types
    if action_type == 'add':
        # Create a new task
        new_task = Task(
            title=task_details['title'],
            description=task_details.get('description'),
            reminder_time=reminder_time,
            user_id=session['user_id']
        )
        db.session.add(new_task)
        db.session.commit()

        return jsonify({
            "message": "Task created successfully",
            "task": {
                "id": new_task.id,
                "title": new_task.title,
                "description": new_task.description,
                "reminder_time": new_task.reminder_time
            }
        }), 201

    elif action_type == 'update':
        # Update an existing task (based on details like title, description)
        task = Task.query.filter_by(user_id=session['user_id'], title=task_details['title']).first()
        if not task:
            return jsonify({"error": "Task not found"}), 404

        task.title = task_details.get('title', task.title)
        task.description = task_details.get('description', task.description)
        task.reminder_time = reminder_time if reminder_time else task.reminder_time

        db.session.commit()
        return jsonify({"message": "Task updated successfully"}), 200

    elif action_type == 'delete':
        # Delete task based on provided details (e.g., title, description)
        task_title = task_details.get('title')
        task_description = task_details.get('description')

        if task_title:
            task = Task.query.filter_by(user_id=session['user_id'], title=task_title).first()
        elif task_description:
            task = Task.query.filter_by(user_id=session['user_id'], description=task_description).first()
        else:
            return jsonify({"error": "No valid details provided to identify the task"}), 400

        if not task:
            return jsonify({"error": "Task not found"}), 404

        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deleted successfully"}), 200

    else:
        return jsonify({"error": "Invalid action type"}), 400
