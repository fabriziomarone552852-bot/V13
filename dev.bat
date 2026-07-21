@echo off
setlocal

echo === Smart Agenda - DEV (DB volatile locale) ===
set "APP_ENV=dev"
set "VITE_API_BASE_URL=http://localhost:8000"

echo Backend: APP_ENV=%APP_ENV%
echo Frontend: VITE_API_BASE_URL=%VITE_API_BASE_URL%
echo.

start "Backend (dev)" cmd /k "set APP_ENV=dev && uvicorn backend.main:app --reload"
pushd frontend
call npm run dev
popd