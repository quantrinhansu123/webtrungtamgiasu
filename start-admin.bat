@echo off
cd /d %~dp0..
pip install -r admin\requirements.txt
python admin\server.py
pause
