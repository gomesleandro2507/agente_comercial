"""
Script de Inicialização do Agente Comercial de Inteligência de Mercado.
Compatível com compartilhamento em rede local (Wi-Fi/LAN) e túnel público.

Execução padrão:
    python run.py

Para compartilhar na rede com seus colegas:
    Compartilhe o endereço de IP exibido no terminal!
"""

import os
import sys
import socket
import webbrowser
import uvicorn

# Assegurar suporte a caracteres em terminais Windows (UTF-8)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def get_local_ip():
    """Identifica o IP local na rede Wi-Fi / Ethernet para compartilhamento."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def main():
    local_ip = get_local_ip()
    port = 8000

    print("\n" + "=" * 76)
    print("  [>] AGENTE COMERCIAL DE INTELIGENCIA DE MERCADO - BRASIL")
    print("=" * 76)
    print(f"  * Acesso Local no seu computador:        http://localhost:{port}")
    print(f"  * Compartilhar com colegas na mesma rede: http://{local_ip}:{port}")
    print("=" * 76)
    print("  Dica: Qualquer pessoa conectada ao mesmo Wi-Fi / Rede pode acessar")
    print(f"  diretamente pelo navegador no link: http://{local_ip}:{port}")
    print("  Pressione CTRL+C para encerrar o servidor a qualquer momento.")
    print("=" * 76 + "\n")

    # Abrir navegador automaticamente no computador local
    try:
        webbrowser.open(f"http://localhost:{port}")
    except Exception:
        pass

    # Iniciar servidor Uvicorn ouvindo em 0.0.0.0 para aceitar conexões da rede
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

if __name__ == "__main__":
    main()
