import React, { useState } from 'react';
import axios from 'axios';

function Search() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState('');
  const [interests, setInterests] = useState([]);

  const handleSearch = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/search', 
        { query },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      setResult(response.data.content);
      setInterests(response.data.interests);
    } catch (error) {
      console.error('Error performing search:', error);
    }
  };

  const handleLinkClick = async (topic) => {
    setQuery(topic);
    await handleSearch({ preventDefault: () => {} });
  };

  const renderContent = (content) => {
    const words = content.split(' ');
    return words.map((word, index) => {
      if (word.startsWith('#')) {
        const topic = word.slice(1);
        return (
          <span key={index}>
            {' '}
            <a href="#" onClick={() => handleLinkClick(topic)}>
              {topic}
            </a>
          </span>
        );
      }
      return ` ${word}`;
    });
  };

  return (
    <div>
      <h2>Personalized Search</h2>
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your search query"
        />
        <button type="submit">Search</button>
      </form>
      {result && (
        <div>
          <h3>Search Result:</h3>
          <p>{renderContent(result)}</p>
        </div>
      )}
      {interests.length > 0 && (
        <div>
          <h3>Your Interests:</h3>
          <ul>
            {interests.map((interest, index) => (
              <li key={index}>{interest}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default Search;
