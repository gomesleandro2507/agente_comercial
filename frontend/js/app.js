// Estado global da aplicação
let currentProduct = null;
let currentRecommendations = [];
let allRegionsData = {};

// Presets pré-configurados para testes rápidos
const PRODUCT_PRESETS = {
  agro: {
    name: "AgroVision Telemetria IoT de Silos e Grãos",
    description: "Sistema inteligente de sensores IoT e telemetria para controle em tempo real de umidade, temperatura e prevenção de perdas no escoamento de safras de soja e milho.",
    sector: "Agronegócio",
    ticket: 28000,
    delivery: "Híbrido (Remoto + Implantação Local)",
    sizes: ["Grande Porte", "Corporativo / Muito Grande"],
    regions: ["Centro-Oeste", "Sul", "Nordeste"]
  },
  saude: {
    name: "MedAudit IA - Prontuário & Triagem Preditiva",
    description: "Plataforma de inteligência artificial clínica para redução do tempo de espera em prontos-socorros, auditoria automatizada de faturamento hospitalar e conformidade LGPD.",
    sector: "Saúde",
    ticket: 22000,
    delivery: "Cloud / Remoto",
    sizes: ["Grande Porte", "Corporativo / Muito Grande"],
    regions: ["Nordeste", "Sudeste", "Sul"]
  },
  logistica: {
    name: "RotaSmart - Inteligência em Fretes & Entroncamento",
    description: "Otimizador logístico de rotas pesadas, gestão de janelas de entrega e telemetria de consumo de combustível para frotas rodoviárias e centros de distribuição.",
    sector: "Logística & Transporte",
    ticket: 14000,
    delivery: "Cloud / Remoto",
    sizes: ["Médio Porte", "Grande Porte"],
    regions: ["Nordeste", "Centro-Oeste", "Sudeste"]
  },
  tech: {
    name: "ShieldOps Cloud Security & Observabilidade",
    description: "Solução de monitoramento de microsserviços, combate a vulnerabilidades em tempo real e automação com agentes de IA para times ágeis de tecnologia.",
    sector: "Tecnologia & Software",
    ticket: 9500,
    delivery: "Cloud / Remoto",
    sizes: ["Médio Porte", "Grande Porte"],
    regions: ["Sul", "Sudeste", "Nordeste"]
  }
};

document.addEventListener("DOMContentLoaded", () => {
  initPresets();
  initTabs();
  initForms();
  initChat();
  initModal();
  loadMarketRegions();
  loadHealth();

  // Carrega automaticamente o primeiro preset para demonstração imediata
  applyPreset("agro");
  document.getElementById("btn-analyze").click();
});

// Inicialização de Presets
function initPresets() {
  const select = document.getElementById("preset-select");
  select.addEventListener("change", (e) => {
    const val = e.target.value;
    if (val && PRODUCT_PRESETS[val]) {
      applyPreset(val);
    }
  });
}

function applyPreset(key) {
  const p = PRODUCT_PRESETS[key];
  if (!p) return;

  document.getElementById("product-name").value = p.name;
  document.getElementById("product-desc").value = p.description;
  document.getElementById("product-sector").value = p.sector;
  document.getElementById("product-ticket").value = p.ticket;
  document.getElementById("product-delivery").value = p.delivery;

  // Atualizar checkboxes de porte
  document.querySelectorAll("input[name='company_size']").forEach(cb => {
    cb.checked = p.sizes.includes(cb.value);
  });

  // Atualizar checkboxes de região
  document.querySelectorAll("input[name='target_region']").forEach(cb => {
    cb.checked = p.regions.includes(cb.value);
  });
}

// Navegação por Abas
function initTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(tc => tc.classList.remove("active"));

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-target");
      const targetEl = document.getElementById(targetId);
      if (targetEl) targetEl.classList.add("active");
    });
  });

  // Filtros de Região nos resultados
  const chips = document.querySelectorAll(".filter-chip");
  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      chips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      const filter = chip.getAttribute("data-filter");
      renderRecommendations(filter);
    });
  });
}

// Submissão do Formulário de Produto
function initForms() {
  const form = document.getElementById("product-form");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("btn-analyze");
    const originalText = btn.innerHTML;
    btn.innerHTML = `<span class="spinner"></span> Analisando Demanda no Brasil...`;
    btn.disabled = true;

    const sizes = Array.from(document.querySelectorAll("input[name='company_size']:checked")).map(el => el.value);
    const regions = Array.from(document.querySelectorAll("input[name='target_region']:checked")).map(el => el.value);

    currentProduct = {
      name: document.getElementById("product-name").value,
      description: document.getElementById("product-desc").value,
      target_sectors: [document.getElementById("product-sector").value],
      ticket_price: parseFloat(document.getElementById("product-ticket").value) || 10000,
      delivery_model: document.getElementById("product-delivery").value,
      target_company_sizes: sizes,
      target_regions: regions,
      mandatory_requirements: ["Compatibilidade de porte", "Aderência a modelo " + document.getElementById("product-delivery").value]
    };

    try {
      const response = await fetch("/api/products/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(currentProduct)
      });

      if (!response.ok) throw new Error("Falha na análise comercial");
      const data = await response.json();
      currentRecommendations = data.top_recommendations || [];

      document.getElementById("results-count").textContent = currentRecommendations.length;
      document.getElementById("recommendations-subtitle").textContent = 
        `Classificação ponderada para "${currentProduct.name}" com análise de saturação e demanda por UF.`;

      renderRecommendations("all");

      // Atualizar o chat informando sobre a análise
      addAgentMessage(
        `Prezado(a), concluí a análise de mercado para o produto **${currentProduct.name}**.\n\n` +
        `O algoritmo qualificou **${currentRecommendations.length} clientes prioritários** com alto potencial de conversão. ` +
        `O cliente com maior compatibilidade estratégica foi identificado com Match Score de **${currentRecommendations[0]?.match_score}%**.\n\n` +
        `Fique à vontade para me questionar sobre a dinâmica regional ou solicitar um plano de abordagem personalizada.`
      );
    } catch (err) {
      console.error(err);
      alert("Erro ao realizar análise: " + err.message);
    } finally {
      btn.innerHTML = originalText;
      btn.disabled = false;
    }
  });
}

// Renderização dos Cards de Clientes
function renderRecommendations(filterRegion = "all") {
  const container = document.getElementById("recommendations-list");
  container.innerHTML = "";

  let list = currentRecommendations;
  if (filterRegion !== "all") {
    list = list.filter(r => r.customer.region === filterRegion);
  }

  if (list.length === 0) {
    container.innerHTML = `
      <div class="empty-placeholder">
        <h4>Nenhum cliente qualificado nesta região</h4>
        <p>Tente selecionar "Todas as Regiões" ou expandir a abrangência geográfica do produto.</p>
      </div>
    `;
    return;
  }

  list.forEach((rec, idx) => {
    const isTop1 = idx === 0 && filterRegion === "all";
    const c = rec.customer;
    const b = rec.score_breakdown;

    const card = document.createElement("div");
    card.className = `customer-rec-card ${isTop1 ? "rank-1" : ""}`;

    card.innerHTML = `
      <div class="rec-card-top">
        <div class="client-identity">
          <h4>${idx + 1}º ${c.name}</h4>
          <div class="client-badges-row">
            <span class="badge-tag badge-location">📍 ${c.city} - ${c.state} (${c.region})</span>
            <span class="badge-tag">🏢 ${c.sector}</span>
            <span class="badge-tag">💼 ${c.size}</span>
            ${c.annual_revenue_bracket ? `<span class="badge-tag">💰 ${c.annual_revenue_bracket}</span>` : ""}
            ${c.contact_name ? `<span class="badge-tag badge-contact">Contato identificado</span>` : `<span class="badge-tag badge-contact badge-contact-missing">Sem contato</span>`}
          </div>
        </div>
        <div class="score-badge-circle" title="Score Final Ponderado">
          <span class="score-num">${rec.match_score}%</span>
          <span class="score-label">Match</span>
        </div>
      </div>

      <!-- Barras de Decomposição do Score -->
      <div class="score-breakdown-row">
        <div class="breakdown-item">
          <div class="breakdown-label">Fit do Produto (40%)</div>
          <div class="breakdown-val">${b.product_fit_score}%</div>
        </div>
        <div class="breakdown-item">
          <div class="breakdown-label">Oportunidade Regional (35%)</div>
          <div class="breakdown-val">${b.regional_opportunity_score}%</div>
        </div>
        <div class="breakdown-item">
          <div class="breakdown-label">Prontidão & Verba (25%)</div>
          <div class="breakdown-val">${b.urgency_budget_score}%</div>
        </div>
      </div>

      <!-- Detalhes Estratégicos -->
      <div class="rec-strategic-block">
        ${c.contact_name ? `<div class="contact-highlight"><div class="contact-icon">↗</div><div><span class="detail-title">Decisor sugerido</span><strong>${escapeHtml(c.contact_name)}</strong><span>${escapeHtml(c.contact_role || "Contato comercial")}</span></div></div>` : `<div class="contact-highlight contact-empty"><div class="contact-icon">?</div><div><span class="detail-title">Contato não identificado</span><span>Enriqueça este lead com uma fonte autorizada antes da abordagem.</span></div></div>`}
        <div class="rec-item-detail">
          <span class="detail-title">💡 Diagnóstico Comercial:</span>
          <span>${rec.commercial_recommendation}</span>
        </div>
        <div class="rec-item-detail">
          <span class="detail-title">📈 Oferta x Demanda:</span>
          <span>${rec.regional_context}</span>
        </div>
        <div class="rec-item-detail">
          <span class="detail-title">⚡ Concorrência & Riscos:</span>
          <span>${rec.risk_and_competitor_analysis}</span>
        </div>
        <div class="approach-box">
          <strong>🤝 Sugestão de Abordagem Educada:</strong> ${rec.suggested_approach}
        </div>
      </div>

      <div class="rec-card-actions">
        <button class="btn btn-secondary btn-sm btn-ask-client" data-client="${c.name}">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          Consultar Agente sobre este Cliente
        </button>
      </div>
    `;

    container.appendChild(card);
  });

  // Listener para o botão "Consultar Agente sobre este Cliente"
  document.querySelectorAll(".btn-ask-client").forEach(btn => {
    btn.addEventListener("click", () => {
      const clientName = btn.getAttribute("data-client");
      // Muda para aba de chat
      document.querySelector(".tab-btn[data-target='chat-view']").click();
      const input = document.getElementById("chat-input");
      input.value = `Gostaria de detalhes sobre o cliente "${clientName}": qual é a justificativa de oferta e demanda da região dele e como devo conduzir a primeira reunião?`;
      document.getElementById("btn-send-chat").click();
    });
  });
}

// Carregar Painel Regional de Oferta x Demanda
async function loadMarketRegions() {
  try {
    const res = await fetch("/api/market/regions");
    if (!res.ok) return;
    allRegionsData = await res.json();
    const container = document.getElementById("regions-grid");
    container.innerHTML = "";

    const regionKeys = ["Centro-Oeste", "Sul", "Nordeste", "Sudeste", "Norte"];

    regionKeys.forEach(key => {
      const r = allRegionsData[key];
      if (!r) return;

      // Calcular média geral do setor ou padrão
      const card = document.createElement("div");
      card.className = "region-card";

      // Tag de oportunidade
      let tagClass = "tag-med";
      if (r.general_competition_level === "Baixa" || key === "Centro-Oeste") tagClass = "tag-high";
      if (r.general_competition_level === "Muito Alta") tagClass = "tag-comp";

      card.innerHTML = `
        <div class="region-header">
          <span class="region-name">${r.name} (${r.code})</span>
          <span class="region-tag ${tagClass}">Concorrência: ${r.general_competition_level}</span>
        </div>
        <div class="region-metrics-bars">
          <div class="metric-bar-group">
            <div class="metric-label-row">
              <span>Demanda Média</span>
              <strong>${key === "Centro-Oeste" ? "92%" : key === "Sudeste" ? "94%" : key === "Sul" ? "88%" : key === "Nordeste" ? "82%" : "76%"}</strong>
            </div>
            <div class="progress-track">
              <div class="progress-fill fill-demand" style="width: ${key === "Centro-Oeste" ? "92%" : key === "Sudeste" ? "94%" : key === "Sul" ? "88%" : key === "Nordeste" ? "82%" : "76%"}"></div>
            </div>
          </div>
          <div class="metric-bar-group">
            <div class="metric-label-row">
              <span>Oferta Concorrente</span>
              <strong>${key === "Sudeste" ? "90%" : key === "Sul" ? "72%" : key === "Centro-Oeste" ? "52%" : key === "Nordeste" ? "48%" : "35%"}</strong>
            </div>
            <div class="progress-track">
              <div class="progress-fill fill-supply" style="width: ${key === "Sudeste" ? "90%" : key === "Sul" ? "72%" : key === "Centro-Oeste" ? "52%" : key === "Nordeste" ? "48%" : "35%"}"></div>
            </div>
          </div>
        </div>
        <div class="text-muted-xs" style="margin-top: 4px;">
          ${r.strategic_notes}
        </div>
      `;

      container.appendChild(card);
    });
  } catch (err) {
    console.error("Erro ao carregar regiões:", err);
  }
}

// Chat Consultivo
function initChat() {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = input.value.trim();
    if (!query) return;

    addUserMessage(query);
    input.value = "";
    input.focus();

    // Mensagem temporária de processamento
    const loadingId = addAgentLoading();

    try {
      const res = await fetch("/api/agent/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query,
          product: currentProduct
        })
      });

      removeLoading(loadingId);
      if (!res.ok) throw new Error("Erro na comunicação com o agente");
      const data = await res.json();
      addAgentMessage(data.reply);
    } catch (err) {
      removeLoading(loadingId);
      addAgentMessage("Peço escusas, ocorreu uma instabilidade momentânea na conexão. Por gentileza, tente novamente.");
    }
  });

  // Chips de prompt rápido
  document.querySelectorAll(".chip-prompt").forEach(chip => {
    chip.addEventListener("click", () => {
      const prompt = chip.getAttribute("data-prompt");
      input.value = prompt;
      form.dispatchEvent(new Event("submit"));
    });
  });
}

function addUserMessage(text) {
  const container = document.getElementById("chat-messages");
  const msg = document.createElement("div");
  msg.className = "message message-user";
  msg.innerHTML = `
    <div class="message-bubble">${escapeHtml(text)}</div>
    <span class="message-time">Você</span>
  `;
  container.appendChild(msg);
  container.scrollTop = container.scrollHeight;
}

function addAgentMessage(rawMarkdown) {
  const container = document.getElementById("chat-messages");
  const msg = document.createElement("div");
  msg.className = "message message-agent";
  
  // Converte formatação simples de markdown em HTML
  const formattedHtml = formatMarkdown(rawMarkdown);

  msg.innerHTML = `
    <div class="message-bubble">${formattedHtml}</div>
    <span class="message-time">Agente Comercial Especialista</span>
  `;
  container.appendChild(msg);
  container.scrollTop = container.scrollHeight;
}

function addAgentLoading() {
  const container = document.getElementById("chat-messages");
  const msg = document.createElement("div");
  const id = "loading-" + Date.now();
  msg.id = id;
  msg.className = "message message-agent";
  msg.innerHTML = `
    <div class="message-bubble">
      <em>Consultando matriz de mercado e ponderando requisitos...</em>
    </div>
  `;
  container.appendChild(msg);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeLoading(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function formatMarkdown(text) {
  if (!text) return "";
  let html = text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/### (.*?)\n/g, "<h5>$1</h5>")
    .replace(/## (.*?)\n/g, "<h4>$1</h4>")
    .replace(/\n\n/g, "<br><br>")
    .replace(/\n- /g, "<br>• ");
  return html;
}

function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// Modal de Importação de Leads
function initModal() {
  const modal = document.getElementById("modal-import");
  const btnOpen = document.getElementById("btn-import-toggle");
  const btnClose = document.getElementById("btn-close-modal");
  const btnCancel = document.getElementById("btn-cancel-modal");
  const fileInput = document.getElementById("csv-file-input");
  const btnUpload = document.getElementById("btn-do-upload");
  const feedback = document.getElementById("import-feedback");

  btnOpen.addEventListener("click", () => modal.classList.remove("hidden"));
  btnClose.addEventListener("click", () => modal.classList.add("hidden"));
  btnCancel.addEventListener("click", () => modal.classList.add("hidden"));

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      btnUpload.disabled = false;
      feedback.textContent = `Arquivo selecionado: ${fileInput.files[0].name}`;
      feedback.style.color = "#60A5FA";
    }
  });

  btnUpload.addEventListener("click", async () => {
    if (!fileInput.files[0]) return;
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    btnUpload.disabled = true;
    feedback.textContent = "Processando e importando clientes...";

    try {
      const res = await fetch("/api/customers/upload", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Erro no envio");

      feedback.textContent = data.message;
      feedback.style.color = "#34D399";
      document.getElementById("clients-count-badge").textContent = data.total_customers;

      setTimeout(() => {
        modal.classList.add("hidden");
        // Re-executa a análise para refletir a nova base
        document.getElementById("btn-analyze").click();
      }, 1200);
    } catch (err) {
      feedback.textContent = "Falha ao importar: " + err.message;
      feedback.style.color = "#EF4444";
      btnUpload.disabled = false;
    }
  });
}

// Health Check
async function loadHealth() {
  try {
    const res = await fetch("/api/health");
    if (res.ok) {
      const data = await res.json();
      document.getElementById("clients-count-badge").textContent = data.customers_count;
    }
  } catch (err) {
    console.error("Health check error:", err);
  }
}
