@echo off
echo Starting Nginx HTTPS Proxy...
cd nginx
start nginx.exe
cd ..
echo Nginx started!
echo HTTPS URL: https://localhost
echo To stop: run stop_nginx.bat
pause
