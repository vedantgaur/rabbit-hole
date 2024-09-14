import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Chat() {
  const [message, setMessage] = useState('');
  const [context, setContext] = useState('');
  const [response, setResponse] = useState('');

  useEffect(() => {
    document.addEventListener('mouseup', handleTextSelection);
    return () => {
      document.removeEventListener('mouseup', handleTextSelection);
    };
  }, []);

  const handleTextSelection = () => {
    const selectedText = window.getSelection().toString();
    if (selectedText) {
      setContext(selectedText);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const result = await axios.post('http://localhost:8080/chat', 
        { message, context },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      setResponse(result.data.message);
    } catch (error) {
      console.error('Error in chat:', error);
    }
  };

  return (
    <div>
      <h2>Chat Assistant</h2>
      <form onSubmit={handleSubmit}>
        <textarea
          value={context}
          onChange={(e) => setContext(e.target.value)}
          placeholder="Selected text will appear here"
          readOnly
        />
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Enter your message"
        />
        <button type="submit">Send</button>
      </form>
      {response && (
        <div>
          <h3>Response:</h3>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
}

export default Chat;