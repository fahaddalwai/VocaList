import React, { useState, useRef } from 'react';

const ChatBot = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [message, setMessage] = useState('');
  const [confirmation, setConfirmation] = useState(null);
  const mediaRecorderRef = useRef(null);

  // Function to start and stop recording
  const toggleRecording = async () => {
    if (isRecording) {
      setIsRecording(false);
      mediaRecorderRef.current.stop();
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorderRef.current = new MediaRecorder(stream);
        const audioChunks = [];

        mediaRecorderRef.current.ondataavailable = (event) => {
          audioChunks.push(event.data);
        };

        mediaRecorderRef.current.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
          setAudioBlob(audioBlob);
          await submitAudio(audioBlob); // Upload after stopping
        };

        mediaRecorderRef.current.start();
        setIsRecording(true);
      } catch (err) {
        console.error('Error accessing microphone:', err);
        setMessage('Could not access microphone. Please try again.');
      }
    }
  };

  const submitAudio = async (audioBlob) => {
    if (!audioBlob || audioBlob.size <= 44) {
      setMessage('No audio recorded or audio is too small. Please try again.');
      return;
    }
  
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');
  
    // Retrieve the token from local storage
    const token = localStorage.getItem('token');
  
    try {
      const response = await fetch('http://127.0.0.1:5000/create-task-from-speech', {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${token}`, // Include the token in the request header
        },
      });
  
      if (response.ok) {
        const result = await response.json();
        const { action_type, title, description, reminder_time } = result;

        // Set confirmation state with task details
        setConfirmation({ action_type, title, description, reminder_time });
      } else {
        setMessage('Error creating task from speech.');
      }
    } catch (error) {
      console.error('Error submitting audio:', error);
      setMessage('An error occurred while submitting the audio.');
    }
  };

  const finalizeTaskAction = async () => {
    const { action_type, title, description, reminder_time } = confirmation;
    const token = localStorage.getItem('token');
    const endpoint = action_type === 'Add' 
        ? 'tasks' 
        : action_type === 'Update' 
        ? 'tasks/update-by-title' 
        : 'tasks/delete-by-title';

    const method = action_type === 'Add' ? 'POST' : action_type === 'Update' ? 'PUT' : 'DELETE';
    const body = action_type === 'Delete' 
        ? JSON.stringify({ title }) 
        : JSON.stringify({ title, description, reminder_time });

    try {
        const response = await fetch(`http://127.0.0.1:5000/${endpoint}`, {
            method,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body,
        });

        if (response.ok) {
            const result = await response.json();
            setMessage(`Task ${action_type}d successfully: ${result.message}`);
            setConfirmation(null); // Clear confirmation after finalizing
        } else {
            const errorText = await response.text();
            setMessage(`Error ${action_type}ing task: ${errorText}`);
        }
    } catch (error) {
        console.error('Error finalizing task action:', error);
        setMessage('An error occurred while finalizing the task.');
    }
};


  return (
    <div style={{ padding: '20px', width: '40%' }}>
      <h2>Chatbot with Voice Input</h2>

      <button onClick={toggleRecording} style={{ marginBottom: '20px' }}>
        {isRecording ? 'Stop Recording' : 'Record Voice'}
      </button>

      {message && <p>{message}</p>}

      {confirmation && (
        <div>
          <p>Action Type: {confirmation.action_type}</p>
          <p>Title: {confirmation.title}</p>
          <p>Description: {confirmation.description || 'None'}</p>
          <p>Reminder Time: {confirmation.reminder_time || 'None'}</p>
          <button onClick={finalizeTaskAction}>Yes, Proceed</button>
          <button onClick={() => setConfirmation(null)}>No, Cancel</button>
        </div>
      )}
    </div>
  );
};

export default ChatBot;
