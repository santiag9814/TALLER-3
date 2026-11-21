@echo off
set MONGOSH=C:\Users\David\AppData\Local\MongoDB\mongosh\mongosh-2.14.1-win32-x64\bin\mongosh.exe
if exist "%MONGOSH%" (
    "%MONGOSH%" --quiet --eval "db.getSiblingDB('admin').shutdownServer()" >nul 2>&1
)
powershell -NoProfile -Command "$p = Get-Process mongod -ErrorAction SilentlyContinue; if ($p) { $p | Stop-Process -Force }"
echo MongoDB detenido.
timeout /t 2 /nobreak >nul
