@echo off
::NOTE - This script will only work once the installation of the venv is completed using install.sh

:: Get paths to everything
Set virtualEnvironName=Spotify-api-scrapper-venv
Set root_dir=%~dp0

Set executePath="%root_dir%src\main.py
Set virtualEnvironDir="%root_dir%%virtualEnvironName%
Set venvPath=%virtualEnvironDir%\Scripts\python.exe"

echo %venvPath%

echo Starting Program %executePath%"
%venvPath% %executePath%" %*

