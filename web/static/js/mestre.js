/**
 * Mestre - Dashboard do Narrador
 * Rolagens em tempo real, ferramentas de sessão.
 * Login: credenciais só no servidor, nunca no frontend.
 */
(function () {
  let sessaoCodigo = null;
  let pollInterval = null;
  let iniciativa = [];
  let npcs = [];
  const CREDS = { credentials: "include" };

  function $(id) {
    return document.getElementById(id);
  }

  function parseIntVal(v, def = 0) {
    const n = parseInt(v, 10);
    return isNaN(n) ? def : n;
  }

  function showLogin() {
    $("mestre-login-wrap")?.classList.remove("hidden");
    $("mestre-dashboard")?.classList.add("hidden");
  }

  function showDashboard() {
    $("mestre-login-wrap")?.classList.add("hidden");
    $("mestre-dashboard")?.classList.remove("hidden");
  }

  async function checkAuth() {
    const res = await fetch("/api/auth/me", CREDS);
    const json = await res.json();
    return json.ok && json.autenticado;
  }

  async function doLogin() {
    const form = $("mestre-login-form");
    const userInput = $("login-user");
    const passInput = $("login-pass");
    const errEl = $("login-err");
    if (!form || !userInput || !passInput) return false;
    errEl.classList.add("hidden");
    errEl.textContent = "";
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: userInput.value.trim(),
        password: passInput.value,
      }),
      credentials: "include",
    });
    const json = await res.json();
    if (json.ok) {
      passInput.value = "";
      return true;
    }
    errEl.textContent = json.erro || "Erro ao entrar";
    errEl.classList.remove("hidden");
    return false;
  }

  async function doLogout() {
    await fetch("/api/auth/logout", { method: "POST", ...CREDS });
    showLogin();
  }

  async function initAuth() {
    const autenticado = await checkAuth();
    if (autenticado) {
      const meRes = await fetch("/api/auth/me", CREDS);
      const me = await meRes.json();
      $("mestre-user").textContent = me.user ? me.user : "";
      showDashboard();
      initDashboard();
      return;
    }
    showLogin();
    $("mestre-login-form")?.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (await doLogin()) {
        initAuth();
      }
    });
  }

  function initDashboard() {
  async function criarSessao() {
    const res = await fetch("/api/mestre/session/create", { method: "POST", ...CREDS });
    const json = await res.json();
    if (!json.ok) return;
    sessaoCodigo = json.codigo;
    $("sessao-codigo").textContent = sessaoCodigo;
    $("sessao-nao-ativa").classList.add("hidden");
    $("sessao-ativa").classList.remove("hidden");
    iniciarPoll();
  }

  function encerrarSessao() {
    sessaoCodigo = null;
    if (pollInterval) {
      clearInterval(pollInterval);
      pollInterval = null;
    }
    $("sessao-nao-ativa").classList.remove("hidden");
    $("sessao-ativa").classList.add("hidden");
    $("rolls-empty").classList.remove("hidden");
    $("rolls-list").classList.add("hidden");
    $("rolls-list").innerHTML = "";
  }

  async function buscarRolls() {
    if (!sessaoCodigo) return;
    const total = $("rolls-list").dataset.total || 0;
    const res = await fetch(`/api/mestre/session/${sessaoCodigo}/rolls?desde=${total}`, CREDS);
    const json = await res.json();
    if (!json.ok || !json.rolls || json.rolls.length === 0) return;
    const ul = $("rolls-list");
    ul.classList.remove("hidden");
    $("rolls-empty").classList.add("hidden");
    json.rolls.forEach(r => {
      const li = document.createElement("li");
      const critClass = r.mainNum === 20 ? " roll-crit" : r.mainNum === 1 ? " roll-fumble" : "";
      li.className = critClass;
      li.innerHTML = `
        <span class="roll-jogador">${escapeHtml(r.jogador)}</span>
        <span class="roll-tipo">${escapeHtml(r.tipo)}</span>
        <span class="roll-msg">${escapeHtml(r.msg)}</span>
        <span class="roll-num">${r.mainNum}</span>
      `;
      ul.appendChild(li);
    });
    ul.dataset.total = json.total;
    ul.scrollTop = ul.scrollHeight;
  }

  function escapeHtml(s) {
    if (!s) return "";
    const div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
  }

  function iniciarPoll() {
    if (pollInterval) return;
    pollInterval = setInterval(buscarRolls, 2000);
  }

  $("btn-criar-sessao")?.addEventListener("click", criarSessao);
  $("btn-encerrar-sessao")?.addEventListener("click", encerrarSessao);

  $("btn-copiar-codigo")?.addEventListener("click", () => {
    if (!sessaoCodigo) return;
    navigator.clipboard.writeText(sessaoCodigo).then(() => {
      const btn = $("btn-copiar-codigo");
      btn.textContent = "Copiado!";
      setTimeout(() => btn.textContent = "Copiar", 1500);
    });
  });

  // ========== CLIMA ==========
  async function rolarClima() {
    const estacao = $("clima-estacao")?.value || "verao";
    const res = await fetch(`/api/mestre/weather?estacao=${estacao}`, CREDS);
    const json = await res.json();
    if (!json.ok) return;
    const el = $("clima-result");
    el.classList.remove("hidden");
    el.innerHTML = `<strong>d100: ${json.d100}</strong> — ${json.clima}<br><small>Moves: ${json.moves}</small>`;
  }

  $("btn-clima")?.addEventListener("click", rolarClima);

  // ========== CD CAPTURA ==========
  function updateCalc() {
    const nivel = parseIntVal($("calc-nivel")?.value, 1);
    const sr = parseFloat($("calc-sr")?.value) || 0;
    const hp = parseIntVal($("calc-hp")?.value, 0);
    const cd = Math.max(1, 10 + Math.floor(sr) + nivel + Math.floor(hp / 10));
    const el = $("calc-cd");
    if (el) el.textContent = String(cd);
  }

  ["calc-nivel","calc-sr","calc-hp"].forEach(id => {
    const el = $(id);
    if (el) el.oninput = el.onchange = () => updateCalc();
  });
  updateCalc();

  // ========== INICIATIVA ==========
  function addIniciativa() {
    const nome = $("inic-nome")?.value?.trim();
    const valor = parseIntVal($("inic-valor")?.value, 0);
    if (!nome) return;
    iniciativa.push({ nome, valor });
    iniciativa.sort((a, b) => b.valor - a.valor);
    $("inic-nome").value = "";
    $("inic-valor").value = "";
    renderIniciativa();
  }

  function removeIniciativa(i) {
    iniciativa.splice(i, 1);
    renderIniciativa();
  }

  function renderIniciativa() {
    const ul = $("iniciativa-lista");
    ul.innerHTML = iniciativa.map((item, i) => `
      <li>
        <span class="inic-num">${item.valor}</span>
        <span class="inic-nome">${escapeHtml(item.nome)}</span>
        <button type="button" class="inic-remove" data-i="${i}" title="Remover">✕</button>
      </li>
    `).join("");
    ul.querySelectorAll(".inic-remove").forEach(btn => {
      btn.onclick = () => removeIniciativa(parseInt(btn.dataset.i, 10));
    });
  }

  $("inic-add")?.addEventListener("click", addIniciativa);
  $("inic-valor")?.addEventListener("keydown", e => { if (e.key === "Enter") addIniciativa(); });
  $("inic-limpar")?.addEventListener("click", () => {
    iniciativa = [];
    renderIniciativa();
  });

  // ========== NPCs ==========
  function addNpc() {
    const nome = $("npc-nome")?.value?.trim();
    const hp = $("npc-hp")?.value?.trim();
    const info = $("npc-info")?.value?.trim();
    if (!nome) return;
    npcs.push({ nome, hp: hp || "—", info: info || "" });
    $("npc-nome").value = "";
    $("npc-hp").value = "";
    $("npc-info").value = "";
    renderNpcs();
  }

  function removeNpc(i) {
    npcs.splice(i, 1);
    renderNpcs();
  }

  function renderNpcs() {
    const ul = $("npc-lista");
    ul.innerHTML = npcs.map((n, i) => `
      <li>
        <span class="npc-nome">${escapeHtml(n.nome)}</span>
        <span class="npc-hp">${escapeHtml(n.hp)}</span>
        <span class="npc-info">${escapeHtml(n.info)}</span>
        <button type="button" class="npc-remove" data-i="${i}" title="Remover">✕</button>
      </li>
    `).join("");
    ul.querySelectorAll(".npc-remove").forEach(btn => {
      btn.onclick = () => removeNpc(parseInt(btn.dataset.i, 10));
    });
  }

  $("npc-add")?.addEventListener("click", addNpc);

  // ========== GUIA DO MESTRE ==========
  function fmt(s) {
    return (s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  }

  async function carregarGuia() {
    const res = await fetch("/api/mestre/guia", CREDS);
    const json = await res.json();
    if (!json.ok || !json.guia) return;
    const container = $("guia-container");
    if (!container) return;
    const ordem = ["encontros", "tamanho", "lendarios", "condicoes", "status_pokemon", "mudancas_status"];
    container.innerHTML = ordem.map(key => {
      const sec = json.guia[key];
      if (!sec) return "";
      const id = "guia-" + key;
      let conteudo = sec.conteudo || "";
      const lin = conteudo.split("\n");
      const frag = [];
      let inT = false;
      let firstRow = true;
      for (const ln of lin) {
        if (/^\|.+\|$/.test(ln.trim())) {
          const cels = ln.split("|").filter(Boolean).map(c => c.trim());
          if (/^[-:\s]+$/.test(cels.join(""))) continue;
          if (!inT) { frag.push("<table class='guia-table'>"); inT = true; firstRow = true; }
          const tag = firstRow ? "th" : "td";
          const prefix = firstRow ? "<thead><tr>" : "<tr>";
          const suffix = firstRow ? "</tr></thead><tbody>" : "</tr>";
          firstRow = false;
          frag.push(prefix + cels.map(c => `<${tag}>${fmt(c)}</${tag}>`).join("") + suffix);
        } else {
          if (inT) { frag.push("</tbody></table>"); inT = false; }
          if (ln.trim()) frag.push(fmt(ln) + "<br>");
        }
      }
      if (inT) frag.push("</tbody></table>");
      const html = frag.join("");
      return `<details class="guia-details" id="${id}">
        <summary class="guia-summary">${escapeHtml(sec.titulo)}</summary>
        <div class="guia-content">${html}</div>
      </details>`;
    }).join("");
  }

  carregarGuia();

  $("btn-logout")?.addEventListener("click", doLogout);
  } // fim initDashboard

  initAuth();
})();
