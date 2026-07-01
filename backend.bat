@echo off
REM Avvio backend dalla ROOT del repository.
REM Imposta l'ambiente: dev | test | prod (default: dev).
if "%APP_ENV%"=="" set APP_ENV=dev
echo Avvio backend con APP_ENV=%APP_ENV%
uvicorn backend.main:app --reload
pause
