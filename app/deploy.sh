rsync -avL --progress -e "ssh -i ~/Documents/awsPems/video-gen.pem" \
       ~/Documents/Code/VideoGen \ 
       ubuntu@ec2-44-203-68-144.compute-1.amazonaws.com:~/VideoGen