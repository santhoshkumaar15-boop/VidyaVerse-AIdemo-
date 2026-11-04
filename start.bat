@echo off
set OPENBLAS_NUM_THREADS=1
set MKL_NUM_THREADS=1
set NUMEXPR_NUM_THREADS=1
set OMP_NUM_THREADS=1
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo Starting VidyaVerse AI...
streamlit run app.py
pause

