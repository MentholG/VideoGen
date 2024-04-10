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


const baseURL = process.env.REACT_APP_API_URL;


const HomePage = () => {
  const navigate = useNavigate();
  const [videoSubject, setVideoSubject] = useState('');  
  
  const handleNextClick = async () => {
    // Initiate video generation and get task_id
    const postData = {
      "video_subject": videoSubject,
      "video_script": "",
      "video_terms": "",
      "video_aspect": "9:16",
      "video_concat_mode": "random",
      "video_clip_duration": 5,
      "video_count": 1,
      "video_language": "",
      "voice_name": "male-en-US-ChristopherNeural",
      "bgm_type": "random",
      "bgm_file": "",
      "bgm_volume": 0.2,
      "subtitle_enabled": true,
      "subtitle_position": "bottom",
      "font_name": "STHeitiMedium.ttc",
      "text_fore_color": "#FFFFFF",
      "text_background_color": "transparent",
      "font_size": 60,
      "stroke_color": "#000000",
      "stroke_width": 1.5,
      "n_threads": 2,
      "paragraph_number": 1
    };
    const createVideoUrl = `${baseURL}/api/v1/videos`
    console.log(`[generateVideo] createVideoUrl:${createVideoUrl}`)

    console.log(`[handleNextClick] ${JSON.stringify(postData)}`)
    let response = await fetch(createVideoUrl, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(postData)
    });

    const data = await response.json();
    console.log(`[handleNextClick] ${JSON.stringify(data)}`)
    if (!response.ok || !data || data.status !== 200 || !data.data || !data.data.task_id) {
      throw new Error('Failed to start video generation');
    }
    const taskID = data.data.task_id
    navigate('/video', { state: { taskID } }); // Navigate to the VideoPage
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
                placeholder="Twitter link"
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
