import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import Search from './components/Search';
import Interests from './components/Interests';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      setIsAuthenticated(true);
    }
  }, [token]);

  const setAuth = (boolean) => {
    setIsAuthenticated(boolean);
  };

  const setAuthToken = (token) => {
    setToken(token);
    localStorage.setItem('token', token);
  };

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route 
            path="/" 
            element={
              !isAuthenticated ? (
                <Login setAuth={setAuth} setAuthToken={setAuthToken} />
              ) : (
                <Navigate to="/dashboard" replace />
              )
            } 
          />
          <Route 
            path="/register" 
            element={
              !isAuthenticated ? (
                <Register setAuth={setAuth} setAuthToken={setAuthToken} />
              ) : (
                <Navigate to="/dashboard" replace />
              )
            } 
          />
          <Route 
            path="/dashboard" 
            element={
              isAuthenticated ? (
                <Dashboard setAuth={setAuth} />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/search" 
            element={
              isAuthenticated ? (
                <Search />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/interests" 
            element={
              isAuthenticated ? (
                <Interests />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;