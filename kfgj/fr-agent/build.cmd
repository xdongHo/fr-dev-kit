@echo off
setlocal
rem --- JDK: JDK_HOME/JAVA_HOME env first, then common locations ---
set "JDK=%JDK_HOME%"
if "%JDK%"=="" set "JDK=%JAVA_HOME%"
if "%JDK%"=="" for /d %%D in ("C:\Program Files\Java\jdk*" "C:\Program Files\Amazon Corretto\jdk*" "C:\Program Files\Zulu\zulu-8*") do if exist "%%D\bin\javac.exe" set "JDK=%%D"
if "%JDK%"=="" (
  echo [ERROR] JDK8 not found: set JDK_HOME and retry
  exit /b 1
)
set "JAVAC=%JDK%\bin\javac.exe"
set "JAR=%JDK%\bin\jar.exe"
set "SRC=src"
set "BUILD=build"

if not exist "%BUILD%" mkdir "%BUILD%"

echo Compiling with %JDK% ...
"%JAVAC%" -encoding UTF-8 -d "%BUILD%" %SRC%\FrAgent.java %SRC%\CommandServer.java %SRC%\ExecServer.java %SRC%\EventRecorder.java %SRC%\EventSerializer.java %SRC%\ActionPlayer.java %SRC%\ComponentResolver.java
if errorlevel 1 (echo FAILED & exit /b 1)

echo Packaging...
cd %BUILD%
"%JAR%" cfm ..\fr-agent.jar ..\%SRC%\MANIFEST.MF fr\agent\*.class
cd ..
echo Done: fr-agent.jar