cls
set APP_ENV=prod
echo Avvio backend con APP_ENV=%APP_ENV%
uvicorn backend.main:app --reload
pause