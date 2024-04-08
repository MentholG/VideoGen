conda activate MoneyPrinterTurbo
nohup python main.py &
nohup sh webui.sh &
cd ./twitter-cut/
nohup npm start &