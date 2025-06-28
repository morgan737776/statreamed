@echo off
SET url=https://github.com/zackees/python3.10/raw/main/win/python-3.10.10-amd64.exe
SET filename=python-3.10.10-amd64.exe

echo Downloading Python 3.10.10...
powershell -Command "Invoke-WebRequest -Uri '%url%' -OutFile '%filename%'"

echo Installing Python 3.10.10...
%filename% /quiet PrependPath=1
start /wait %filename% /quiet PrependPath=1

echo Installation complete.
