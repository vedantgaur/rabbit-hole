import React, { useState } from 'react';
import axios from 'axios';
import 'katex/dist/katex.min.css';
import { InlineMath, BlockMath } from 'react-katex';
import { PrismLight as SyntaxHighlighter } from 'react-syntax-highlighter';
import python from 'react-syntax-highlighter/dist/esm/languages/prism/python';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import ChatAssistant from './ChatAssistant';

SyntaxHighlighter.registerLanguage('python', python);

function Search({ interests, setInterests }) {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState('');
  const [manimCode, setManimCode] = useState('');
  const [musicSnippet, setMusicSnippet] = useState('');
  const [selectedText, setSelectedText] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/search', 
        { query },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      setResult(response.data.content);
      setInterests(response.data.interests);
      
      // Extract Manim code if present
      const manimCodeMatch = response.data.content.match(/Manim Animation Code:\n([\s\S]*)/);
      if (manimCodeMatch) {
        setManimCode(manimCodeMatch[1]);
        setResult(response.data.content.replace(/Manim Animation Code:[\s\S]*/, ''));
      } else {
        setManimCode('');
      }

      // Extract music snippet if present
      const musicSnippetMatch = response.data.content.match(/Music Snippet Generated: (.*)/);
      if (musicSnippetMatch) {
        setMusicSnippet(musicSnippetMatch[1]);
        setResult(response.data.content.replace(/Music Snippet Generated:.*/, ''));
      } else {
        setMusicSnippet('');
      }
    } catch (error) {
      console.error('Error performing search:', error);
    }
  };

  const handleLinkClick = async (topic) => {
    setQuery(topic);
    await handleSearch({ preventDefault: () => {} });
  };

  const handleTextSelection = () => {
    const selection = window.getSelection();
    if (selection.toString().length > 0) {
      setSelectedText(selection.toString());
    }
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

  const renderLatex = (content) => {
    const parts = content.split(/(<latex>.*?<\/latex>)/);
    return parts.map((part, index) => {
      if (part.startsWith('<latex>') && part.endsWith('</latex>')) {
        const latex = part.slice(7, -8);
        return <InlineMath key={index} math={latex} />;
      }
      return part;
    });
  };

  return (
    <div className="search-container">
      <div className="search-results">
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
          <div onMouseUp={handleTextSelection}>
            <h3>Search Result:</h3>
            <p>{renderLatex(renderContent(result))}</p>
          </div>
        )}
        {manimCode && (
          <div>
            <h3>Manim Animation Code:</h3>
            <SyntaxHighlighter language="python" style={tomorrow}>
              {manimCode}
            </SyntaxHighlighter>
          </div>
        )}
        {musicSnippet && (
          <div>
            <h3>Generated Music Snippet:</h3>
            <audio controls src={musicSnippet}></audio>
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
      <div className="chat-assistant-container">
        <ChatAssistant selectedText={selectedText} />
      </div>
    </div>
  );
}

export default Search;
