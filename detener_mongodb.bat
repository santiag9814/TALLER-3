@echo off
"C:\Program Files\MongoDB\Server\9.0\bin\mongod.exe" --shutdown --config "C:\Users\David\AppData\Local\MongoDB\mongod.cfg"
echo MongoDB detenido.
timeout /t 2 /nobreak >nul
