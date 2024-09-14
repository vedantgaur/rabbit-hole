import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Interests() {
  const [interests, setInterests] = useState([]);
  const [newInterest, setNewInterest] = useState('');

  useEffect(() => {
    fetchInterests();
  }, []);

  const fetchInterests = async () => {
    try {
      const response = await axios.get('http://localhost:5000/get_interests', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setInterests(response.data.interests);
    } catch (error) {
      console.error('Error fetching interests:', error);
    }
  };

  const addInterest = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:5000/add_interest', 
        { topic: newInterest },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      setNewInterest('');
      fetchInterests();
    } catch (error) {
      console.error('Error adding interest:', error);
    }
  };

  return (
    <div>
      <h2>Your Interests</h2>
      <ul>
        {interests.map((interest, index) => (
          <li key={index}>{interest}</li>
        ))}
      </ul>
      <form onSubmit={addInterest}>
        <input
          type="text"
          value={newInterest}
          onChange={(e) => setNewInterest(e.target.value)}
          placeholder="Add new interest"
        />
        <button type="submit">Add Interest</button>
      </form>
    </div>
  );
}

export default Interests;
