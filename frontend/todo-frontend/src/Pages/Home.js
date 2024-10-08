import React from 'react';
import { Link } from 'react-router-dom';
import '../Styles/Home.css';

const Home = () => {
  return (
    <div className="home-container">
      <h1>Welcome to the To-Do List & Reminder App</h1>
      <p>Please log in or sign up to continue.</p>
      <div className="home-buttons">
        <Link to="/login">
          <button className="home-btn">Login</button>
        </Link>
        <Link to="/signup">
          <button className="home-btn">Sign Up</button>
        </Link>
      </div>
    </div>
  );
};

export default Home;
