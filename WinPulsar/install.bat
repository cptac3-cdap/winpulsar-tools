@echo on
set /p URL=<c:\dlurl.txt
call version.bat
if not exist C:\Python27 (
  rem wget -O epd-%PYTHONVER%-win-x86_64.msi http://edwardslab.bmcb.georgetown.edu/~nedwards/dropbox/62gQ5fN4MP/epd-%PYTHONVER%-win-x86_64.msi
  rem msiexec /qr /lv*x epd_msi_log.txt /i epd-%PYTHONVER%-win-x86_64.msi TARGETDIR=C:\Python27 ALLUSERS=1
  rem del epd*.msi
  wget --no-check-certificate -O python-%PYTHONVER%.amd64.msi %URL%/python-%PYTHONVER%.amd64.msi
  msiexec /qn /i python-%PYTHONVER%.amd64.msi TARGETDIR=C:\Python27 ALLUSERS=1
  del python*msi
  C:\Python27\python.exe -m pip install --upgrade pip
  C:\Python27\Scripts\pip install --upgrade virtualenv
)
if not exist installers.run (
  installers\2008SP1\vcredist_x86.exe /qb
  installers\2008SP1\vcredist_x64.exe /qb
  installers\2010\vcredist_x86.exe /install /passive /norestart
  installers\2010\vcredist_x64.exe /install /passive /norestart
  installers\2010SP1\vcredist_x86.exe /install /passive /norestart
  installers\2010SP1\vcredist_x64.exe /install /passive /norestart
  installers\2012U4\vcredist_x86.exe /install /passive /norestart
  installers\2012U4\vcredist_x64.exe /install /passive /norestart
  installers\2013\vcredist_x86.exe /install /passive /norestart
  installers\2013\vcredist_x64.exe /install /passive /norestart
  installers\MSFileReader\3.0SP3\MSFileReader_x86_x64.exe /s /f1installers\MSFileReader\3.0SP3\setup.iss
  installers\MSFileReader\3.1SP2\MSFileReader_x64.exe /s /f1installers\MSFileReader\3.1SP2\setup.iss
  type nul >installers.run
)
if not exist local-ipv4.txt (
  wget --no-check-certificate -q -Olocal-ipv4.txt http://169.254.169.254/latest/meta-data/local-ipv4
)
set /p LOCALIP=<local-ipv4.txt
if not exist public-ipv4.txt (
  wget --no-check-certificate -q -Opublic-ipv4.txt http://169.254.169.254/latest/meta-data/public-ipv4
)
set /p PUBLICIP=<public-ipv4.txt
echo %LOCALIP%
echo %PUBLICIP%
set /p AMQPURL=<c:\amqpurl.txt
echo %AMQPURL%
if exist pulsar.zip del pulsar.zip
if not exist pulsar-%PULSARVER% (
  rem rmdir /Q /S pulsar-%PULSARVER%
  wget --no-check-certificate -O pulsar.zip %URL%/pulsar-%PULSARVER%-patched.zip
  unzip pulsar.zip 
  del pulsar.zip
)
cd pulsar-%PULSARVER%
if exist .venv (
  call .venv\Scripts\activate.bat
  @echo on
  ..\unzip.exe -o ..\extra.zip
)
if not exist .venv (
  C:\Python27\Scripts\virtualenv .venv
  call .venv\Scripts\activate.bat
  @echo on
  pip install -r requirements.txt
  pip install pyOpenSSL
  pip install kombu
  pip install amqp==2.1.3
  pip install pycurl
  ..\unzip.exe ..\extra.zip
  rem .venv\Scripts\python.exe ..\replace.py .venv\Lib\site-packages\galaxy\util\path\__init__.py "from grp" "# from grp"
  rem .venv\Scripts\python.exe ..\replace.py .venv\Lib\site-packages\galaxy\util\path\__init__.py "from pwd" "# from pwd"
  .venv\Scripts\python.exe ..\replace.py .venv\Lib\site-packages\paste\httpserver.py "from OpenSSL import SSL" "from OpenSSL import SSL, tsafe"
  .venv\Scripts\python.exe ..\replace.py .venv\Lib\site-packages\paste\httpserver.py "class SSLConnection(SSL.Connection):" "class SSLConnection(tsafe.Connection):"
)
.venv\Scripts\python.exe ..\replace.py server.ini XXXXXX_IPADDRESS_XXXXXXX %LOCALIP%
.venv\scripts\python.exe ..\replace.py app.yml XXXX_NUMBER_OF_CPUS_XXXX %NUMBER_OF_PROCESSORS%
.venv\scripts\python.exe ..\replace.py app.yml XXXX_AMQP_URL_XXXX %AMQPURL%
netsh advfirewall firewall add rule name="Pulsar TCP/8913" dir=in action=allow protocol=TCP localport=8913
call .venv\Scripts\deactivate.bat
