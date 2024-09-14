import React, { useState } from 'react';
import axios from 'axios';

function ChatAssistant({ selectedText }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    if (input.trim() === '') return;

    const newMessage = { role: 'user', content: input };
    setMessages([...messages, newMessage]);
    setInput('');

    try {
      const response = await axios.post('http://localhost:5000/chat', 
        { message: input, context: selectedText },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      
      const assistantMessage = { role: 'assistant', content: response.data.message };
      setMessages(messages => [...messages, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div className="chat-assistant">
      <h3>Chat Assistant</h3>
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            {message.content}
          </div>
        ))}
      </div>
      <div className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default ChatAssistant;