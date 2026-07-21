@echo off
setlocal

echo === Smart Agenda - TEST (DB persistente locale) ===
set "APP_ENV=test"
set "VITE_API_BASE_URL=http://localhost:8000"

echo Backend: APP_ENV=%APP_ENV%
echo Frontend: VITE_API_BASE_URL=%VITE_API_BASE_URL%
echo.

start "Backend (test)" cmd /k "set APP_ENV=test && uvicorn backend.main:app --reload"
pushd frontend
call npm run dev
popd