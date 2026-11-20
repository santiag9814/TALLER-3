@echo off
powershell -NoProfile -Command "Start-Process -FilePath 'C:\Program Files\MongoDB\Server\9.0\bin\mongod.exe' -ArgumentList '--config','C:\Users\David\AppData\Local\MongoDB\mongod.cfg' -WindowStyle Hidden"
echo MongoDB iniciado en localhost:27017
timeout /t 2 /nobreak >nul
