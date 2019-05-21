@echo off
set NAME=WinPulsar
set /p URL=<c:\dlurl.txt
set ZIP=%NAME%.zip
if not exist C:\%NAME% mkdir C:\%NAME%
if exist %ZIP% del %ZIP%
%~dp0wget.exe --no-check-certificate %URL%/%ZIP%
%~dp0unzip.exe -o %ZIP% -d C:\%NAME%
if exist %ZIP% del %ZIP%
cd C:\%NAME%
install.bat
