// src/components/Search.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import 'katex/dist/katex.min.css';
import { InlineMath, BlockMath } from 'react-katex';
import ManimViewer from './ManimViewer';

function Search({ interests, setInterests }) {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState('');
  const [manimCode, setManimCode] = useState('');
  const [musicSnippet, setMusicSnippet] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:8080/search', 
        { query },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      setResult(response.data.content);
      setInterests(response.data.interests);
      setManimCode(response.data.manim_code || '');
      setMusicSnippet(response.data.music_snippet || '');
    } catch (error) {
      console.error('Error performing search:', error);
    }
  };

  const handleSubtopicClick = (subtopic) => {
    setQuery(subtopic);
    handleSearch({ preventDefault: () => {} });
  };

  const renderContent = (content) => {
    const parts = content.split(/(\$\$.*?\$\$|\$.*?\$|#[^\s]+)/);
    return parts.map((part, index) => {
      if (part.startsWith('$$') && part.endsWith('$$')) {
        return <BlockMath key={index} math={part.slice(2, -2)} />;
      } else if (part.startsWith('$') && part.endsWith('$')) {
        return <InlineMath key={index} math={part.slice(1, -1)} />;
      } else if (part.startsWith('#')) {
        const subtopic = part.slice(1);
        return (
          <a key={index} href="#" onClick={() => handleSubtopicClick(subtopic)}>
            {subtopic}
          </a>
        );
      } else {
        return part;
      }
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
          <div>{renderContent(result)}</div>
        </div>
      )}
      {manimCode && (
        <div>
          <h3>Manim Animation:</h3>
          <ManimViewer code={manimCode} />
        </div>
      )}
      {musicSnippet && (
        <div>
          <h3>Generated Music Snippet:</h3>
          <audio controls src={musicSnippet}></audio>
        </div>
      )}
    </div>
  );
}

export default Search;