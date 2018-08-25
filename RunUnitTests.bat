IF %1.==. GOTO Usage

set REDIS_SERVER_IP=192.168.1.119
python -m unittest discover -p "*Test.py"
GOTO End

:Usage
Echo "Usage: %0 <IP address of redis server>"

:End
