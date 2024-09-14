import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Search from './Search';
import ChatAssistant from './ChatAssistant';
import Interests from './Interests';

function Dashboard({ setAuth }) {
  const [interests, setInterests] = useState([]);
  const [selectedText, setSelectedText] = useState('');

  useEffect(() => {
    fetchInterests();
  }, []);

  const fetchInterests = async () => {
    try {
      const response = await axios.get('http://localhost:5000/interests', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setInterests(response.data.interests);
    } catch (error) {
      console.error('Error fetching interests:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setAuth(false);
  };

  const handleTextSelection = () => {
    const selection = window.getSelection();
    if (selection.toString().length > 0) {
      setSelectedText(selection.toString());
    }
  };

  return (
    <div className="dashboard" onMouseUp={handleTextSelection}>
      <nav>
        <button onClick={handleLogout}>Logout</button>
      </nav>
      <div className="dashboard-content">
        <div className="main-content">
          <Search interests={interests} setInterests={setInterests} />
          <Interests interests={interests} />
        </div>
        <div className="chat-assistant">
          <ChatAssistant selectedText={selectedText} />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
