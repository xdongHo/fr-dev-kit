@echo off
setlocal enabledelayedexpansion
rem --- FR_HOME：环境变量优先，其次常见安装位置 ---
set "FR_ROOT=%FR_HOME%"
if "%FR_ROOT%"=="" for /d %%D in ("C:\Program Files\FineReport_10.0" "D:\FineReport_10.0" "C:\FineReport_10.0") do if exist "%%D\bin\designer.bat" set "FR_ROOT=%%D"
if "%FR_ROOT%"=="" (
  echo [ERROR] 未找到 FineReport 安装：设置 FR_HOME 环境变量或改本脚本第 4 行
  exit /b 1
)
cd /d "%FR_ROOT%"
set "FR_HOME=%CD%"
set "JAVA=%FR_HOME%\jre\bin\java.exe"

rem --- JVM options from designer.vmoptions ---
set "OPTS=-Xms3072m -Xmx8192m -XX:+UseG1GC -XX:MaxGCPauseMillis=200 -XX:InitiatingHeapOccupancyPercent=30 -XX:+UseStringDeduplication -XX:MaxMetaspaceSize=512m -Dsun.java2d.d3d=true -Dsun.java2d.ddoffscreen=true -Dsun.java2d.font.renderer=1 -Dawt.useSystemAAFontSettings=on -Dswing.aatext=true -Dfile.encoding=UTF-8"

rem --- ADD AGENT（%~dp0 自适应套件位置） ---
set "AGENT=%~dp0fr-agent.jar"
set "OPTS=%OPTS% -javaagent:%AGENT%"

rem --- classpath ---
set "CP=%FR_HOME%\lib\*;%FR_HOME%\server\lib\*;%FR_HOME%\webapps\webroot\WEB-INF\lib\*;%FR_HOME%\webapps\webroot\WEB-INF\classes;%FR_HOME%\jre\lib\tools.jar"

echo === FR Designer + Agent ===
echo FR: %FR_HOME%
echo Agent: %AGENT%
echo API: http://localhost:18999
echo.

"%JAVA%" %OPTS% -cp "%CP%" com.fr.start.Designer

endlocal
pause