@echo off
c:
cd c:\WinPulsar
call version.bat
cd pulsar-%PULSARVER%
start /b "" cmd /c run.bat ^>run.log 2^>^&1
cd c:\WinPulsar
