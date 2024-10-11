import React, { useState, useEffect } from 'react';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import moment from 'moment';
import ChatBot from './Chatbot';
import '../Styles/Dashboard.css'; // Importing the CSS file

// Setup localizer for the calendar
const localizer = momentLocalizer(moment);

// Function to convert the timestamp to 'YYYY-MM-DDTHH:MM:SS' format
// Function to convert the timestamp to 'YYYY-MM-DDTHH:MM:SS' format in local CST timezone
const convertDate = (dateString) => {
  const date = moment.parseZone(dateString); // Parse with the timezone information
  
  const year = date.year();
  const month = String(date.month() + 1).padStart(2, '0'); // month is zero-based
  const day = String(date.date()).padStart(2, '0');
  const hours = String(date.hours()).padStart(2, '0');
  const minutes = String(date.minutes()).padStart(2, '0');
  const seconds = String(date.seconds()).padStart(2, '0');

  // Format to 'YYYY-MM-DDTHH:MM:SS'
  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
};


const Dashboard = () => {
  const [events, setEvents] = useState([]);

  // Fetch tasks from API
  const fetchTasks = async () => {
    try {
      const token = localStorage.getItem('token'); // Get the JWT token from local storage
      const response = await fetch('http://127.0.0.1:5000/tasks', {
        headers: {
          Authorization: `Bearer ${token}`, // Include the token in the Authorization header
        },
      });
      const data = await response.json();

      // Map tasks and format dates
      const formattedEvents = data.map(task => {
        const start = new Date(convertDate(task.reminder_time)); 
        const end = new Date(start); 
        end.setMinutes(start.getMinutes() + 30); // Add 30 minutes to the start time

        return {
          title: task.title,
          start: start,
          end: end
        };
      });

      setEvents(formattedEvents);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  useEffect(() => {
    // Fetch tasks from the API when the component mounts
    const intervalId = setInterval(() => {
      fetchTasks();
    }, 5000);

    return () => clearInterval(intervalId); // Cleanup on unmount
  }, []);

  return (
    <div className="dashboard-container">
      <div className="calendar-section">
        {/* <h2>Dashboard Calendar</h2> */}
        <Calendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          style={{ height: 500, margin: '50px' }}
        />
      </div>
      <div className="chat-section">
        <ChatBot />
      </div>
    </div>
  );
};

export default Dashboard;
