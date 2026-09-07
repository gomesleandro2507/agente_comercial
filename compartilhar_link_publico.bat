@echo off
title Criar Link Publico na Internet - Agente Comercial
chcp 65001 > nul
echo ======================================================================
echo    GERADOR DE LINK PUBLICO NA INTERNET (HTTPS)
echo ======================================================================
echo.
echo  Este utilitario cria um link publico seguro para que qualquer pessoa,
echo  em qualquer lugar da internet (fora da sua rede), possa acessar o Agente.
echo.
echo  * Certifique-se de que o servidor esta rodando (execute iniciar.bat antes).
echo.
echo  Gerando link publico temporario...
echo ======================================================================
echo.

npx localtunnel --port 8000

pause
