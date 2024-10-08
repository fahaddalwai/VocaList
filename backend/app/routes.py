import jwt
import datetime

from flask import request, jsonify
from app import app, db, bcrypt
from app.models import User, Task
import speech_recognition as sr
import subprocess
import os
from .llm_utils import process_speech_to_task




# Generate a JWT token for a user
def generate_token(user_id):
    token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expires in 1 hour
    }, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token


# Verify and decode JWT token
def decode_token(token):
    try:
        data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return data['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


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

    # Generate a JWT token
    token = generate_token(user.id)
    return jsonify({"message": "Login successful", "token": token}), 200


# Create a new task
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    reminder_time = data.get('reminder_time')  # Get reminder_time from the request

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Token is missing!"}), 403

    user_id = decode_token(token.split(" ")[1])
    if user_id is None:
        return jsonify({"message": "Token is invalid!"}), 403

    new_task = Task(
        title=title,
        description=description,
        reminder_time=reminder_time,
        user_id=user_id
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
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Token is missing!"}), 403

    user_id = decode_token(token.split(" ")[1])
    if user_id is None:
        return jsonify({"message": "Token is invalid!"}), 403

    tasks = Task.query.filter_by(user_id=user_id).all()
    for task in tasks:
        print(task.created_at)
        print('\n')
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
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Token is missing!"}), 403

    user_id = decode_token(token.split(" ")[1])
    if user_id is None:
        return jsonify({"message": "Token is invalid!"}), 403

    task = Task.query.get_or_404(task_id)

    if task.user_id != user_id:
        return jsonify({"message": "You do not have permission to edit this task"}), 403

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)
    task.reminder_time = data.get('reminder_time', task.reminder_time)  # Update reminder_time

    db.session.commit()
    return jsonify({"message": "Task updated successfully"}), 200

@app.route('/tasks/delete-by-title', methods=['DELETE'])
def delete_task_by_title():
    data = request.get_json()
    title = data.get('title')

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Token is missing!"}), 403

    user_id = decode_token(token.split(" ")[1])
    if user_id is None:
        return jsonify({"message": "Token is invalid!"}), 403

    task = Task.query.filter_by(title=title, user_id=user_id).first()
    if task is None:
        return jsonify({"message": "Task not found or you do not have permission to delete this task"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted successfully"}), 200

@app.route('/tasks/update-by-title', methods=['PUT'])
def update_task_by_title():
    data = request.get_json()
    title = data.get('title')
    new_title = data.get('new_title')
    description = data.get('description')
    reminder_time = data.get('reminder_time')

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Token is missing!"}), 403

    user_id = decode_token(token.split(" ")[1])
    if user_id is None:
        return jsonify({"message": "Token is invalid!"}), 403

    task = Task.query.filter_by(title=title, user_id=user_id).first()
    if task is None:
        return jsonify({"message": "Task not found or you do not have permission to update this task"}), 404

    task.title = new_title if new_title else task.title
    task.description = description if description else task.description
    task.reminder_time = reminder_time if reminder_time else task.reminder_time

    db.session.commit()
    return jsonify({"message": "Task updated successfully"}), 200


# Delete a task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Token is missing!"}), 403

    user_id = decode_token(token.split(" ")[1])
    if user_id is None:
        return jsonify({"message": "Token is invalid!"}), 403

    task = Task.query.get_or_404(task_id)

    if task.user_id != user_id:
        return jsonify({"message": "You do not have permission to delete this task"}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted successfully"}), 200


# Get a task by ID for the logged-in user
@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task_for_user(task_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Token is missing!"}), 403

    user_id = decode_token(token.split(" ")[1])
    if user_id is None:
        return jsonify({"message": "Token is invalid!"}), 403

    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    
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
    original_file_path = 'uploaded_audio.wav'
    converted_file_path = 'converted_audio.wav'
    try:
        if os.path.exists(original_file_path):
            os.remove(original_file_path)

        if os.path.exists(converted_file_path):
            os.remove(converted_file_path)
    except Exception as e:
        print(f"Error deleting previous files: {str(e)}")

    # Save the uploaded file
    audio_file.save(original_file_path)

    # Convert the uploaded file to PCM WAV format using FFmpeg
    try:
        subprocess.run(['ffmpeg', '-i', original_file_path, '-acodec', 'pcm_s16le', '-ar', '16000', converted_file_path], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Failed to convert audio file: {str(e)}"}), 500

    # Process the converted audio file with speech_recognition
    try:
        with sr.AudioFile(converted_file_path) as source:
            audio_data = recognizer.record(source)
            speech_text = recognizer.recognize_google(audio_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Use the LLM to extract task details
    task_details = process_speech_to_task(speech_text)

    if not task_details['title'] and task_details['action_type'] != 'delete':
        return jsonify({"error": "Could not extract task title"}), 400

    # Prepare the confirmation response
    confirmation_message = {
        "action_type": task_details['action_type'],
        "title": task_details['title'],
        "description": task_details.get('description'),
        "reminder_time": task_details['reminder_time'],
        "confirm": "Please confirm the task details by replying with 'yes' or 'no'."
    }

    return jsonify(confirmation_message), 200