@echo off
echo Stopping Nginx...
cd nginx
nginx.exe -s quit
cd ..
echo Nginx stopped!
pause
