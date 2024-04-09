import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom'; // Import useLocation

const baseURL = process.env.REACT_APP_API_URL;

const VideoPage = () => {
  const location = useLocation(); // Access location object
  const videoSubject = location.state?.videoSubject; // Access videoSubject from state

  const [videoURL, setVideoURL] = useState('');
  const [isLoading, setIsLoading] = useState(true);


  const generateVideo = async () => {
    setIsLoading(true);
    try {
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
      const createVideoUrl = `http://www.twittercut.com/api/v1/videos`
      console.log(`[generateVideo] createVideoUrl:${createVideoUrl}`)
      let response = await fetch(createVideoUrl, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(postData)
      });

      const data = await response.json();
      if (!response.ok || !data || data.status !== 200 || !data.data || !data.data.task_id) {
        throw new Error('Failed to start video generation');
      }

      // Poll for task completion
      const taskId = data.data.task_id;
      let taskDone = false;
      while (!taskDone) {
        try {
          response = await fetch(`${baseURL}/api/v1/tasks/${taskId}`, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
            }
          });

          const taskData = await response.json();
          console.log(taskData)
          if (taskData && taskData.status === 200 && taskData.data && taskData.data.state === 'SUCCESS') {
            taskDone = true;
            // Set the video URL here
            const videoUrl = `https://laoguis3-us-east-1.s3.amazonaws.com/videos/${taskId}.mp4`;
            setVideoURL(videoUrl); // Example URL
            setIsLoading(false);
          } else {
            await new Promise(resolve => setTimeout(resolve, 3000)); // Wait before polling again
          }
        }
        catch (error) {
          console.error("Error during video generation:", error);
        }
      }
    } catch (error) {
      console.error("Error during video generation:", error);
    }
  };

  useEffect(() => {
    generateVideo();
  }, [generateVideo, videoSubject]);

  return (
    <div className="VideoPage">
      <header className="header">TwitterCuts</header>
      <div className="flex-container">
        <div className="video-container">
          {isLoading ? (
            <div className="video-loading">Generating video...</div>
          ) : (
            <video className="video-player" controls>
              <source src={videoURL} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          )}
          <div className="captions-position">Captions position</div>
        </div>
      </div>
    </div>
  );
};

export default VideoPage;
