@echo off
cd /d "%~dp0"
"c:\Users\user\Documents\AgenticAITraining\Vineetha_Varanasi_EY\.venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8517 --server.headless true --server.fileWatcherType none --server.runOnSave false --browser.gatherUsageStats false
pause
