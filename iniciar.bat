@echo off
title Plataforma de Agentes
cd /d "%~dp0"
echo Iniciando a Plataforma de Agentes...
echo (feche esta janela para encerrar o servidor)
streamlit run app.py
pause
