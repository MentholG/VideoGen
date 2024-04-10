import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom'; // Import useLocation

const baseURL = process.env.REACT_APP_API_URL;

const VideoPage = () => {
  const location = useLocation(); // Access location object
  const taskID = location.state?.taskID; // Access videoSubject from state

  const [videoURL, setVideoURL] = useState('');
  const [isCreating, setIsCreating] = useState(true);


  const generateVideo = async () => {
      // Poll for task completion
      let taskDone = false;
      while (!taskDone) {
        try {
          let response = await fetch(`${baseURL}/api/v1/tasks/${taskID}`, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
            }
          });

          const taskData = await response.json();
          console.log(`[generateVideo] ${JSON.stringify(taskData)}  ${taskData.data.state} === SUCCESS = ${taskData.data.state === 'SUCCESS'} `)
          if (taskData && taskData.status === 200 && taskData.data && taskData.data.state === 'SUCCESS') {
            taskDone = true;
            // Set the video URL here
            const videoUrl = `https://laoguis3-us-east-1.s3.amazonaws.com/videos/${taskID}.mp4`;
            setVideoURL(videoUrl); // Example URL
            console.log(`[generateVideo] isCreating ${isCreating} `)
            setIsCreating(false);
            console.log(`[generateVideo] isCreating ${isCreating} `)
          } else {
            await new Promise(resolve => setTimeout(resolve, 3000)); // Wait before polling again
          }
        }
        catch (error) {
          console.error("Error during video generation:", error);
        }
      }
  };

  useEffect(() => {
    generateVideo();
  }, [generateVideo, taskID]);

  return (
    <div className="VideoPage">
      <header className="header">TwitterCuts</header>
      <div className="flex-container">
        <div className="video-container">
          {isCreating ? (
            <div className="video-creating">Generating video...</div>
          ) : (
            <>
              <video className="video-player" controls>
                <source src={videoURL} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
              {/* Download Button */}
              <a href={videoURL} download={`Video-${taskID}.mp4`} className="download-button">
                Download Video
              </a>
            </>
          )}
          <div className="captions-position">Captions position</div>
        </div>
      </div>
    </div>
  );
};

export default VideoPage;
