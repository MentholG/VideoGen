import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import VideoPage from './VideoPage'; // Import your VideoPage component
import './App.css';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/video" element={<VideoPage />} />
      </Routes>
    </Router>
  );
};




const HomePage = () => {
  const navigate = useNavigate();
  const [videoSubject, setVideoSubject] = useState('');  
  
  const handleNextClick = () => {
    navigate('/video', { state: { videoSubject } }); // Navigate to the VideoPage
  };

  

  return (
    <div className="App">
      <div className="min-h-screen flex flex-col bg-purple-900 p-4">
        <header className="header">TwitterCuts</header>
        <div className="flex-container">
          <div className="card">
            <h2 className="card-title">What's your video topic?</h2>
            <div className="input-container">
              <img
                src="https://cdn.builder.io/api/v1/image/assets/TEMP/29c96f2420540d4c1276e8e10c5b87121127a180678200be42ecf2521402b2d1?apiKey=eac82c65d22f4f5384438583257f016b&"
                alt="Video icon"
                className="icon"
              />
              <input
                type="text"
                placeholder="PHhh"
                className="input-box"
                value={videoSubject} // Set the input value to videoSubject
                onChange={(e) => setVideoSubject(e.target.value)} // Update the state on input change
              />
              <button onClick={handleNextClick} className="input-button">
                NEXT
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
