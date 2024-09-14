import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [username, setUsername] = useState('');
  const [interest, setInterest] = useState('');
  const [interests, setInterests] = useState([]);

  useEffect(() => {
    if (username) {
      fetchInterests();
    }
  }, [username]);

  const fetchInterests = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/get_interests/${username}`);
      setInterests(response.data.interests);
    } catch (error) {
      console.error('Error fetching interests:', error);
    }
  };

  const addInterest = async () => {
    try {
      await axios.post('http://localhost:5000/add_interest', { username, topic: interest });
      setInterest('');
      fetchInterests();
    } catch (error) {
      console.error('Error adding interest:', error);
    }
  };

  return (
    <div className="App">
      <h1>Personalized Search</h1>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="text"
        placeholder="Add interest"
        value={interest}
        onChange={(e) => setInterest(e.target.value)}
      />
      <button onClick={addInterest}>Add Interest</button>
      <h2>Your Interests:</h2>
      <ul>
        {interests.map((int, index) => (
          <li key={index}>{int}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;