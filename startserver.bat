Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Id -eq 19384} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 500
Set-Location "c:\Users\HP\Desktop\StudentWellBeing"
$p = Start-Process -FilePath "python" -ArgumentList "-m","uvicorn","app.main:app","--host","0.0.0.0","--port","8000" -NoNewWindow -RedirectStandardOutput "uvicorn_run.log" -RedirectStandardError "uvicorn_run_err.log" -PassThru
