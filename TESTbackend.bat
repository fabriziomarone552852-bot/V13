cls
set APP_ENV=test
echo Avvio backend con APP_ENV=%APP_ENV%
uvicorn backend.main:app --reload
pause