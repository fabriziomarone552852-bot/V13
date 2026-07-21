@echo off
setlocal

echo === Smart Agenda - PROD (NAS) ===
set "APP_ENV=prod"
set "VITE_API_BASE_URL=http://localhost:8000"

echo Backend: APP_ENV=%APP_ENV%
echo Frontend: VITE_API_BASE_URL=%VITE_API_BASE_URL%
echo.

start "Backend (prod)" cmd /k "set APP_ENV=prod && uvicorn backend.main:app --host 0.0.0.0 --port 8000"

pushd frontend
call npm run dev
popd