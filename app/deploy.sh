rsync -avL --progress -e "ssh -i ~/Documents/awsPems/video-gen.pem" \
       ubuntu@ec2-44-203-68-144.compute-1.amazonaws.com:/home/ubuntu/VideoGen/storage/tasks/aa7a7a80-2797-48d5-9665-1e5e6662181c/final-1.mp4 \
       ~/Downloads/