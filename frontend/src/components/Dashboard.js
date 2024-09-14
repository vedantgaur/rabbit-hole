import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Search from './Search';
import Chat from './Chat';

function Dashboard() {
  const [interests, setInterests] = useState([]);

  useEffect(() => {
    fetchInterests();
  }, []);

  const fetchInterests = async () => {
    try {
      const response = await axios.get('http://localhost:8080/interests', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setInterests(response.data.interests);
    } catch (error) {
      console.error('Error fetching interests:', error);
    }
  };

  return (
    <div>
      <h1>Rabbit Hole</h1>
      <div>
        <h2>Your Interests</h2>
        <ul>
          {interests.map((interest, index) => (
            <li key={index}>{interest}</li>
          ))}
        </ul>
      </div>
      <Search interests={interests} setInterests={setInterests} />
      <Chat />
    </div>
  );
}

export default Dashboard;