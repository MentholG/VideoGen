import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import loadingGif from './resources/loading.gif'; // Adjust the path to where your GIF is located


const baseURL = process.env.REACT_APP_API_URL;

const VideoPage = () => {
  const location = useLocation();
  const taskID = location.state?.taskID;

  const [videoURL, setVideoURL] = useState('');
  const [isCreating, setIsCreating] = useState(true);
  const [progress, setProgress] = useState(0);
  const progressRef = useRef(progress); // 使用useRef来跟踪progress的当前值

  const generateVideo = async () => {

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
        if (taskData && taskData.status === 200 && taskData.data) {
          if (taskData.data.state === 'SUCCESS') {
            taskDone = true;
            setIsCreating(false);
            setProgress(100);
            setVideoURL(`https://laoguis3-us-east-1.s3.amazonaws.com/videos/${taskID}.mp4`);
          } else if (taskData.data.percentage > progressRef.current) { // 使用progressRef.current来获取当前的progress值
            setProgress(taskData.data.percentage);
            progressRef.current = taskData.data.percentage; // 更新progressRef的当前值
          }
        }
        await new Promise(resolve => setTimeout(resolve, 3000));
      }
      catch (error) {
        console.error("Error during video generation:", error);
      }
    }
  };

  useEffect(() => {
    generateVideo();
  }, [generateVideo]);

  return (
    <div className="VideoPage">
      <header className="header">TwitterCut</header>
      <div className="flex-container">
        <div className="video-container">
        {isCreating ? (
            <>
              <img src={loadingGif} alt="Loading..." className="loading-gif" />
              <div className="progress-bar-background">
                <div className="progress-bar-fill" style={{ width: `${progress}%` }}></div>
              </div>
              <div className="progress-text">Generating video... {progress}%</div>
            </>
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
          {/* <div className="captions-position">Captions position</div> */}
        </div>
      </div>
    </div>
  );
};

export default VideoPage;
