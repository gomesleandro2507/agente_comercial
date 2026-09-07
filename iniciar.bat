@echo off
title Agente Comercial de Inteligencia de Mercado
chcp 65001 > nul
echo ======================================================================
echo    INICIANDO O AGENTE COMERCIAL DE INTELIGENCIA DE MERCADO
echo ======================================================================
echo.

IF NOT EXIST ".venv" (
    echo [*] Configurando ambiente virtual Python pela primeira vez...
    python -m venv .venv
    echo [*] Instalando dependencias necessarias...
    .venv\Scripts\pip install -r requirements.txt
    echo [OK] Ambiente configurado com sucesso!
    echo.
)

echo [*] Inicializando o servidor e a interface web...
.venv\Scripts\python run.py

pause
