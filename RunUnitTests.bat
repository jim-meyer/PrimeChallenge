IF %1.==. GOTO Usage

set REDIS_SERVER_IP=%1
python -m unittest discover -p "*Test.py"
GOTO End

:Usage
Echo "Usage: %0 <IP address of redis server>"

:End
