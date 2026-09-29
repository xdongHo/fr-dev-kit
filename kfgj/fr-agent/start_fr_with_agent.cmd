@echo off
setlocal enabledelayedexpansion
rem --- FR_HOME: env var first, then common install locations ---
set "FR_ROOT=%FR_HOME%"
if "%FR_ROOT%"=="" for /d %%D in ("C:\Program Files\FineReport_10.0" "D:\FineReport_10.0" "C:\FineReport_10.0") do if exist "%%D\bin\designer.bat" set "FR_ROOT=%%D"
if "%FR_ROOT%"=="" (
  echo [ERROR] FineReport not found: set FR_HOME or edit line 4
  exit /b 1
)
set "FR_HOME=%FR_ROOT%"
set "AGENT=%~dp0fr-agent.jar"
cd /d "%FR_HOME%"

echo Starting FR Designer with Agent (default port 18999/19000)...
echo FR: %FR_HOME%
echo Agent: %AGENT%
echo.
echo For FR11 coexistence, use: python inject_fr11.py --port-base 19100
echo.

"%FR_HOME%\jre\bin\java" ^
  -Xms3072m -Xmx8192m -XX:+UseG1GC ^
  -XX:MaxGCPauseMillis=200 -XX:InitiatingHeapOccupancyPercent=30 ^
  -XX:+UseStringDeduplication -XX:MaxMetaspaceSize=512m ^
  -Dsun.java2d.d3d=true -Dsun.java2d.ddoffscreen=true ^
  -Dawt.useSystemAAFontSettings=on -Dswing.aatext=true ^
  -Dfile.encoding=UTF-8 ^
  -Dfr.agent.http.port=18999 ^
  -Dfr.agent.exec.port=19000 ^
  -javaagent:"%AGENT%" ^
  -classpath "lib\aspectjrt.jar;lib\engine.io-client-0.7.0.jar;lib\fine-report-designer-10.0.jar;lib\json-20090211.jar;lib\jxbrowser-6.23.jar;lib\jxbrowser-7.15.jar;lib\jxbrowser-swing-7.15.jar;lib\jxbrowser-win64-6.23.jar;lib\jxbrowser-win64-7.15.jar;lib\okhttp-3.0.1.jar;lib\okhttp-ws-3.0.1.jar;lib\okio-1.6.0.jar;lib\socket.io-client-0.7.0.jar;server\lib\*;webapps\webroot\WEB-INF\lib\*;webapps\webroot\WEB-INF\classes" ^
  com.fr.start.FineDesigner com.fr.start.MainDesigner

pause