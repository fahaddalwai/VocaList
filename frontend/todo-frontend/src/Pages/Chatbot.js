import React, { useState, useRef, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMicrophone } from '@fortawesome/free-solid-svg-icons';
import '../Styles/Chatbot.css'; // Assuming you have a CSS file for chatbot styling
/* eslint-disable no-unused-expressions */
const ChatBot = ({ onTaskAdded }) => {
    const [isRecording, setIsRecording] = useState(false);
    const [audioBlob, setAudioBlob] = useState(null);
    const [message, setMessage] = useState('');
    const [messageList, setMessageList] = useState([]);
    const [confirmation, setConfirmation] = useState(null);
    const [transcript, setTranscript] = useState(''); // Holds recognized speech in real-time
    const [loading, setLoading] = useState(false); // Loading state for system typing
    const mediaRecorderRef = useRef(null);
    const endOfMessagesRef = useRef(null); // Ref for scrolling to the last message
    let silenceTimeout; // Used to track silence duration
    const isStoppedRef = useRef(false); // Use a ref to track if recording has been stopped

    // Web Speech API - Speech Recognition setup
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = true; // To keep recognizing during pauses
    recognition.interimResults = true; // To show partial results
    recognition.lang = 'en-US'; // Set language to English
    // Function to start and stop recording and recognize speech
    const toggleRecording = async (b) => {
        if (isRecording) {
            setIsRecording(false);
            mediaRecorderRef?.current?.stop();
            recognition.stop(); // Stop recognition when recording stops
            if (mediaRecorderRef.current.stream) {
                mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
            }
            // let messageArr = messageList;
            // if (transcript === '') {
            //     messageArr.push({ 'message': 'Audio captured', 'user': true, 'audio': true });
            // } else {
            //     messageArr.push({ 'message': transcript, 'user': true, 'audio': true });
            // }
            // setMessageList([...messageArr]);
            // setTranscript('');
            // isStoppedRef.current = true; // Set ref to true when stopped
            stopRecording();

        } else {
            setTranscript('');
            isStoppedRef.current = false; // Reset the ref when starting a new recording
            try {
                setIsRecording(true);
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
                recognition.start(); // Start recognizing speech
                recognition.onresult = (event) => {
                    const speechToText = Array.from(event.results)
                        .map((result) => result[0].transcript)
                        .join('');
                    setTranscript(speechToText);
                    // Clear and reset silence timeout when speech is detected
                    clearTimeout(silenceTimeout);
                    silenceTimeout = setTimeout(() => {
                        stopRecording(speechToText);
                        // Stop recording after 3 seconds of silence
                    }, 3000); // 3-second timeout
                };
                setIsRecording(true);
            } catch (err) {
                console.error('Error accessing microphone:', err);
                setMessage('Could not access microphone. Please try again.');
                let messageArr = messageList;
                messageArr.push({ 'message': 'Could not access microphone. Please try again.' });
                setMessageList(messageArr);
            }
        }
    };



    const stopRecording = (speechToText) => {
        if (mediaRecorderRef.current.stream) {
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
        }
        mediaRecorderRef.current?.stop();
        recognition.stop();
        setIsRecording(false);
        if (!isStoppedRef.current) {
            let messageArr = messageList;
            if (transcript === '' && !speechToText) {
                messageArr.push({ 'message': 'Audio captured', 'user': true, 'audio': true });
            } else {
                if (speechToText ) {
                    messageArr.push({ 'message': speechToText, 'user': true, 'audio': true });
                }
                else {
                    messageArr.push({ 'message': transcript, 'user': true, 'audio': true });
                }
            }
            setMessageList([...messageArr]);
            isStoppedRef.current = true; // Update the ref to indicate the recording is stopped
        }
    };
    // recognition.onend = () => {
    //     // If recognition ends (e.g., user stopped talking), start a timeout to stop recording
    //     clearTimeout(silenceTimeout);
    //     silenceTimeout = setTimeout(() => {
    //         stopRecording(); // Stop recording after 3 seconds of silence when recognition ends
    //     }, 3000); // 3-second timeout
    // };
    const submitAudio = async (audioBlob) => {
        if (!audioBlob || audioBlob.size <= 44) {
            setMessage('No audio recorded or audio is too small. Please try again.');
            let messageArr = messageList;
            messageArr.push({ 'message': 'No audio recorded or audio is too small. Please try again.' });
            setMessageList(messageArr);
            return;
        }

        const formData = new FormData();
        formData.append('audio', audioBlob, 'audio.wav');

        const token = localStorage.getItem('token'); // Retrieve token from local storage

        // Show loading dots while waiting for the response
        setLoading(true);

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

                // Stop loading after receiving response
                setLoading(false);

                // Check if all required fields are present only for 'Add' action type
                if (action_type === 'Add' && (!action_type || !title || !reminder_time)) {
                    setMessage('Incomplete details. Please record your task again.');
                    let messageArr = messageList;
                    messageArr.push({ 'message': 'Incomplete details. Please record your task again.' });
                    setMessageList(messageArr);
                    return; // Exit early if details are incomplete
                }

                setConfirmation({ action_type, title, description, reminder_time }); // Set task confirmation

                const confirmationMessage = action_type.toLowerCase() === 'delete'
                    ? `Do you want to ${action_type.toLowerCase()} "${title}" from your list?`
                    : `Do you want to ${action_type.toLowerCase()} "${title}" to your list for ${new Date(reminder_time).toLocaleDateString()} at ${new Date(reminder_time).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                    })}?`;

                let messageArr = messageList;
                messageArr.push({ 'message': confirmationMessage });
                setMessageList(messageArr);
            } else {
                setLoading(false);
                setMessage('Error creating task from speech.');
                let messageArr = messageList;
                messageArr.push({ 'message': "I didn't get that." });
                setMessageList(messageArr);
            }
        } catch (error) {
            setLoading(false);
            console.error('Error submitting audio:', error);
            setMessage('An error occurred while submitting the audio.');
            let messageArr = messageList;
            messageArr.push({ 'message': 'An error occurred while submitting the audio.' });
            setMessageList(messageArr);
        }
    };

    // Function to handle system response delay (loading dots)
    const LoadingDots = () => {
        return (
            <div className="loading-dots">
                <span>.</span>
                <span>.</span>
                <span>.</span>
            </div>
        );
    };

    const handleNo = () => {
        let messageArr = messageList;
        messageArr.push({ 'message': 'No', 'user': true });
        setLoading(true);
        setTimeout(() => {
            messageArr.push({ 'message': 'Okay!😊 You can try again or come back anytime. Take care! 👋' });
            setLoading(false);
        }, 2000);
        setMessageList(messageArr);
        setConfirmation(null);
    };

    const finalizeTaskAction = async () => {
        setConfirmation(null); // Clear confirmation after finalizing
        let messageArr = messageList;
        messageArr.push({ 'message': 'Yes', 'user': true });
        setMessageList(messageArr);
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
                setMessage(`Task ${action_type}d successfully : ${result.message}`);
                let messageArr = messageList;
                if (action_type === 'Add') {
                    setLoading(true);
                    setTimeout(() => {
                        onTaskAdded({ title, reminder_time })
                        messageArr.push({ 'message': "Task added successfully! ✅ You're all set!" });
                        setLoading(false);
                    }, 2000);
                }
                else if (action_type.toLowerCase() === 'delete') {
                    setLoading(true);
                    setTimeout(() => {
                        messageArr.push({ 'message': "Task deleted successfully! 🗑️ It's gone." });
                        setLoading(false);
                    }, 2000);
                }
                else {
                    setLoading(true);
                    setTimeout(() => {
                        messageArr.push({ 'message': "Task updated successfully! ✅ Changes saved." });
                        setLoading(false);
                    }, 2000);
                }

                setMessageList(messageArr);
            } else {
                const errorText = await response.text();
                setMessage(`I couldn't ${action_type.toLowerCase()} the task: ${errorText}`);
                let messageArr = messageList;
                setLoading(true);
                setTimeout(() => {
                    messageArr.push({ 'message': `Sorry, I couldn't ${action_type.toLowerCase()} the task 😔` });
                    setLoading(false);
                }, 2000);
                setMessageList(messageArr);
            }
        } catch (error) {
            console.error('Error finalizing task action:', error);
            setMessage('An error occurred while finalizing the task.');
            let messageArr = messageList;
            messageArr.push({ 'message': 'An error occurred while finalizing the task.' });
            setMessageList(messageArr);
        }
    };

    // Scroll to the bottom when messageList changes
    useEffect(() => {
        if (endOfMessagesRef.current) {
            endOfMessagesRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [isRecording, messageList.length, transcript, confirmation, loading, message]);

    return (
        <div className="chatbot-container">
            <div className="chatbox">
                {messageList.length === 0 && transcript === '' ? <p style={{ margin: "50% 0% 20% 23%", color: "#8B8378" }}>Add/Reschedule/Delete an event</p> : null}
                {messageList.map((msg, index) => (
                    <div key={index} className={`message ${msg.user ? msg.audio && msg.message === "Audio captured" ? 'user-message audio-message' : 'user-message' : 'system-message'}`}>
                        {msg.message}
                    </div>
                ))}
                {transcript && isRecording && (
                    <p className="message user-message">{transcript}</p>
                )}
                {loading && (
                    <div className="message system-message">
                        <LoadingDots /> {/* Show loading dots when system is processing */}
                    </div>
                )}
                {confirmation && (
                    <div className="confirmation-box">
                        <button onClick={finalizeTaskAction} style={{ marginRight: "10px" }}>Yes, Proceed</button>
                        <button onClick={handleNo}>No, Cancel</button>
                    </div>
                )}
                <div ref={endOfMessagesRef} /> {/* This div will act as a scroll target */}
            </div>

            <button className={`record-btn ${isRecording ? 'recording' : ''}`} style={confirmation !== null || loading ? { pointerEvents: "none", background: "lightgray" } : {}} onClick={() => toggleRecording(isRecording)} >
                <FontAwesomeIcon icon={faMicrophone} />
            </button>
        </div>
    );
};

export default ChatBot;


/* eslint-enable no-unused-expressions */