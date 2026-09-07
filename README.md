# 🚀 Agente Comercial Inteligente de Prospecção & Inteligência de Mercado

Agente comercial inteligente capaz de identificar e recomendar os **melhores clientes potenciais** para qualquer produto, considerando rigorosamente as **exigências técnicas e comerciais da solução** e a dinâmica de **oferta e demanda nas diversas regiões e estados do Brasil**.

---

## 🌟 Principais Recursos

1. **Análise Multidimensional de Clientes (Match Score 0 a 100%)**:
   - **Fit do Produto (40%)**: Setor alvo, porte da empresa, compatibilidade de ticket médio e requisitos obrigatórios (ex: modelo Cloud vs suporte presencial).
   - **Oportunidade Regional de Mercado (35%)**: Cruzamento entre o índice de demanda reprimida e saturação de oferta/concorrentes em cada estado/região brasileira (demanda alta + baixa concorrência = maior oportunidade).
   - **Prontidão de Compra & Verba (25%)**: Urgência da dor relatada pelo cliente e capacidade orçamentária.

2. **Persona do Agente Comercial**:
   - Postura executiva, extremamente **educada, cortês e consultiva**.
   - Respeito estrito às exigências do produto.
   - Justificativas detalhadas de por que a região favorece a abordagem e sugestão de primeiro contato.

3. **Inteligência Geográfica Brasileira**:
   - **Centro-Oeste**: Maior ticket médio agro, demanda recorde e baixa oferta de tecnologias especializadas.
   - **Nordeste**: Vanguarda em energias renováveis e polos de saúde/tecnologia em forte expansão.
   - **Sudeste**: Maior volume financeiro, porém com altíssima saturação de concorrentes e guerra de preços.
   - **Sul**: Cooperativismo forte, exigência técnica apurada e alto índice de maturidade de gestão.
   - **Norte**: Demanda reprimida expressiva por conectividade e automação industrial/sustentável.

4. **Interface Web Moderna**:
   - Dashboard com visual refinado, gráficos e barras de oferta x demanda regional.
   - Ranking interativo de clientes com selos de score.
   - Chat integrado para questionar o agente sobre estratégias, objeções e concorrentes.
   - Importação de listas próprias de leads via CSV.

---

## 🛠️ Como Executar

### 1. Iniciar a aplicação
No terminal, execute:

```powershell
.venv\Scripts\python run.py
```

A aplicação abrirá automaticamente no seu navegador no endereço:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🧠 Configuração de IA (Opcional)

O sistema conta com um **motor heurístico consultivo local** de alta qualidade que funciona 100% offline. Caso deseje enriquecer ainda mais o chat com raciocínio generativo via Google Gemini, basta configurar a variável de ambiente:

```powershell
$env:GEMINI_API_KEY="SUA_CHAVE_AQUI"
.venv\Scripts\python run.py
```

---

## 🧪 Testes Automatizados

Para rodar os testes unitários do motor de recomendação e dos indicadores regionais:

```powershell
.venv\Scripts\python -m pytest tests/
```
