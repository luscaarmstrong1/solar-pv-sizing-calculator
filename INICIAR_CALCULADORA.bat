@echo off
setlocal
cd /d "%~dp0"
python -c "import streamlit, pandas" 2>nul
if errorlevel 1 (
  echo Instalando dependencias...
  pip install -r requirements.txt
)
start "" http://localhost:8501
streamlit run app.py
