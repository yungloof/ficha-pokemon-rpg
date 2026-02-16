/**
 * Mestre - Dashboard do Narrador
 * Rolagens em tempo real, ferramentas de sessão.
 */
(function () {
  let sessaoCodigo = null;
  let pollInterval = null;
  let iniciativa = [];
  let npcs = [];

  function $(id) {
    return document.getElementById(id);
  }

  function parseIntVal(v, def = 0) {
    const n = parseInt(v, 10);
    return isNaN(n) ? def : n;
  }

  // ========== SESSÃO ==========
  async function criarSessao() {
    const res = await fetch("/api/mestre/session/create", { method: "POST" });
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
    const res = await fetch(`/api/mestre/session/${sessaoCodigo}/rolls?desde=${total}`);
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
    const res = await fetch(`/api/mestre/weather?estacao=${estacao}`);
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
})();
