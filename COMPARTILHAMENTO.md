# 🌐 Guia de Compartilhamento do Agente Comercial

Você pode compartilhar o seu Agente Comercial com colegas de equipe, clientes ou parceiros de **4 formas diferentes**, dependendo da sua necessidade:

---

## ⚡ Opção 1: Compartilhar no mesmo Wi-Fi / Rede da Empresa (Sem instalar nada novo)

Se os seus colegas estiverem no **mesmo ambiente de trabalho ou conectados à mesma rede Wi-Fi/Ethernet**:

1. Inicie a aplicação no seu computador executando:
   ```powershell
   .venv\Scripts\python run.py
   ```
   *(ou dê um duplo clique no arquivo `iniciar.bat`)*

2. O terminal exibirá o seu endereço de rede local, por exemplo:
   ```text
   🌐 Compartilhar com colegas na mesma rede: http://192.168.1.106:8000
   ```

3. **Envie esse endereço para os seus colegas**. Eles podem abrir esse link em qualquer navegador (computador, notebook, tablet ou celular) e usarão a aplicação em tempo real!

---

## 🌍 Opção 2: Compartilhar via Link Público na Internet (Para pessoas fora da sua rede)

Se você precisa enviar um link para alguém que está **em outra cidade, home-office ou no celular 4G/5G**:

1. Mantenha o agente rodando no seu computador (via `iniciar.bat` ou `python run.py`).
2. Abra outro terminal ou dê um duplo clique no arquivo:
   ```text
   compartilhar_link_publico.bat
   ```
   *(ou execute: `npx localtunnel --port 8000`)*

3. O terminal gerará uma URL pública segura com HTTPS, por exemplo:
   ```text
   your url is: https://sharp-falcon-22.loca.lt
   ```

4. **Copie e envie esse link para qualquer pessoa pelo WhatsApp, Teams ou E-mail**. Eles terão acesso direto à interface do Agente Comercial de onde estiverem.

---

## 📁 Opção 3: Enviar o Projeto para outra pessoa rodar no computador dela

Se você deseja enviar os arquivos para outro membro da sua equipe:

1. Compacte a pasta do projeto em um arquivo `.zip` (excluindo a pasta `.venv` para economizar espaço).
2. O seu colega precisará apenas:
   - Ter o Python instalado no computador dele.
   - Extrair a pasta e dar um **duplo clique no arquivo `iniciar.bat`**.
3. O script `iniciar.bat` criará automaticamente o ambiente virtual, instalará as dependências e abrirá a aplicação no navegador dele sem exigir comandos técnicos!

---

## ☁️ Opção 4: Publicar Permanentemente na Nuvem (Sempre online 24/7)

Para que o Agente fique hospedado na internet de forma permanente (sem depender do seu computador ligado):

### Usando Render / Railway / Fly.io (Gratuito / Baixo Custo)
1. Suba este projeto para um repositório no seu **GitHub**.
2. Acesse [render.com](https://render.com) ou [railway.app](https://railway.app).
3. Selecione **"New Web Service"** e conecte seu repositório.
4. O serviço detectará automaticamente o nosso `Dockerfile` já configurado na raiz.
5. Em poucos minutos, você terá um endereço fixo, como:
   `https://agente-comercial.onrender.com`.

### Usando Docker Localmente ou em Servidor VPS
Na pasta do projeto, execute:
```bash
docker compose up -d --build
```
A aplicação iniciará como um contêiner isolado rodando em segundo plano.
