import React, { useState, useEffect } from 'react';
import { Navigate, Route, BrowserRouter as Router, Routes, useLocation } from 'react-router-dom';
import './App.css';
import ChatInterface from './Pages/ChatInterface';
import Footer from './Pages/Footer';
import Header from './Pages/Header';
import MainContent from './Pages/MainContent';
import UploadPDF from './Pages/UploadPDF';
import './animations.css'; // Import custom animations
import Services from './components/Services';
// import axios from 'axios';

const App = () => {
  const location = useLocation();
  const isChatPage = location.pathname === '/chat';
  const [data,setdata] = useState([{}]);

  useEffect( () => {
    fetch("/member").then(
      res =>res.json()
    ).then(
      data =>{
        setdata(data)
        console.log(data)
      }
    )
  },[])

  
  return (
    <div className="overflow-hidden flex flex-col w-screen relative">
      <Header /> {/* Always render Header */}
      
      <Routes>
        <Route path="/" element={<MainContent />} />
        <Route path="/upload" element={<UploadPDF />} />
        <Route path="/chat" element={<ChatInterface />} /> {/* Use ChatInterface component for /chat route */}
        <Route path="*" element={<Navigate to="/" replace />} /> {/* Fallback route */}
        <Route path="/services" element={<Services />} />
      </Routes>

      {!isChatPage && <Footer />} {/* Conditionally render Footer */}
    </div>
  );
};

const AppWrapper = () => (
  <Router>
    <App />
  </Router>
);

export default AppWrapper;
