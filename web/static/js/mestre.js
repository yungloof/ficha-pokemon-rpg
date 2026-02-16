/**
 * Mestre - Dashboard do Narrador
 * Layout limpo, NPCs com treinadores e equipe gerenciável.
 */
(function () {
  let sessaoCodigo = null;
  let pollInterval = null;
  let iniciativa = [];
  let npcs = [];
  let ultimoEncontro = [];
  let iniciativaTurnoAtual = 0;
  let pokedexCache = null;
  let npcsExpandidos = {};
  let treinadorEmEdicao = { nome: "", pokemons: [] };
  const CREDS = { credentials: "include" };

  function $(id) { return document.getElementById(id); }
  function parseIntVal(v, def = 0) {
    const n = parseInt(v, 10);
    return isNaN(n) ? def : n;
  }
  function escapeHtml(s) {
    if (!s) return "";
    const div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
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
      body: JSON.stringify({ username: userInput.value.trim(), password: passInput.value }),
      credentials: "include",
    });
    const json = await res.json();
    if (json.ok) { passInput.value = ""; return true; }
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
      if (await doLogin()) initAuth();
    });
  }

  function initDashboard() {
    // Tabs
    document.querySelectorAll(".mestre-tab").forEach(tab => {
      tab.addEventListener("click", () => {
        document.querySelectorAll(".mestre-tab").forEach(t => t.classList.remove("active"));
        document.querySelectorAll(".mestre-tab-panel").forEach(p => p.classList.remove("active"));
        tab.classList.add("active");
        const panel = $("tab-" + tab.dataset.tab);
        if (panel) panel.classList.add("active");
      });
    });

    // Sessão
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
      if (pollInterval) { clearInterval(pollInterval); pollInterval = null; }
      $("sessao-nao-ativa").classList.remove("hidden");
      $("sessao-ativa").classList.add("hidden");
      $("rolls-empty")?.classList.remove("hidden");
      $("rolls-list")?.classList.add("hidden");
      $("rolls-list").innerHTML = "";
    }
    async function buscarRolls() {
      if (!sessaoCodigo) return;
      const total = $("rolls-list")?.dataset?.total || 0;
      const res = await fetch(`/api/mestre/session/${sessaoCodigo}/rolls?desde=${total}`, CREDS);
      const json = await res.json();
      if (!json.ok || !json.rolls || json.rolls.length === 0) return;
      const ul = $("rolls-list");
      ul.classList.remove("hidden");
      $("rolls-empty")?.classList.add("hidden");
      json.rolls.forEach(r => {
        const li = document.createElement("li");
        li.className = r.mainNum === 20 ? " roll-crit" : r.mainNum === 1 ? " roll-fumble" : "";
        li.innerHTML = `<span class="roll-jogador">${escapeHtml(r.jogador)}</span><span class="roll-tipo">${escapeHtml(r.tipo)}</span><span class="roll-msg">${escapeHtml(r.msg)}</span><span class="roll-num">${r.mainNum}</span>`;
        ul.appendChild(li);
      });
      ul.dataset.total = json.total;
      ul.scrollTop = ul.scrollHeight;
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

    // Clima
    async function rolarClima() {
      const estacao = $("clima-estacao")?.value || "verao";
      const res = await fetch(`/api/mestre/weather?estacao=${estacao}`, CREDS);
      const json = await res.json();
      if (!json.ok) return;
      const el = $("clima-result");
      el.classList.remove("hidden");
      el.textContent = `d100: ${json.d100} — ${json.clima} (${json.moves})`;
    }
    $("btn-clima")?.addEventListener("click", rolarClima);

    // Pokedex
    async function loadPokedex() {
      if (pokedexCache) return pokedexCache;
      const res = await fetch("/api/pokedex", CREDS);
      const json = await res.json();
      if (json.ok && json.pokedex) pokedexCache = json.pokedex;
      return pokedexCache || {};
    }

    // Encontro
    function renderEncounterResult(encontros, showButtons) {
      ultimoEncontro = encontros || [];
      const el = $("encounter-result");
      if (!el) return;
      el.classList.remove("hidden");
      if (!encontros || encontros.length === 0) {
        el.innerHTML = "<span>Nenhum Pokémon.</span>";
        return;
      }
      const html = "<strong>Encontro:</strong><br>" + encontros.map(p => {
        const tipos = (p.tipo || []).join("/");
        const ext = [p.ac != null ? "AC " + p.ac : "", p.hp != null ? "HP " + p.hp : ""].filter(Boolean).join(", ");
        return "• <strong>" + escapeHtml(p.nome) + "</strong> — SR " + p.sr + ", " + escapeHtml(tipos) + (ext ? " (" + ext + ")" : "");
      }).join("<br>");
      const btns = showButtons !== false && ultimoEncontro.length > 0 ? `
        <div class="encounter-actions">
          <button type="button" id="enc-btn-npcs" class="btn-ghost btn-sm">+ NPCs</button>
          <button type="button" id="enc-btn-inic" class="btn-ghost btn-sm">+ Iniciativa</button>
          <button type="button" id="enc-btn-rolar-inic" class="btn-ghost btn-sm">Rolar iniciativa</button>
          <button type="button" id="enc-btn-preparar" class="btn-primary">Preparar combate</button>
        </div>
      ` : "";
      el.innerHTML = html + btns;
      el.querySelector("#enc-btn-npcs")?.addEventListener("click", () => adicionarEncontroComoNpcs());
      el.querySelector("#enc-btn-inic")?.addEventListener("click", () => adicionarEncontroAIniciativa(false));
      el.querySelector("#enc-btn-rolar-inic")?.addEventListener("click", () => adicionarEncontroAIniciativa(true));
      el.querySelector("#enc-btn-preparar")?.addEventListener("click", prepararCombate);
    }
    function adicionarEncontroComoNpcs() {
      ultimoEncontro.forEach(p => {
        const hp = p.hp != null ? p.hp + "/" + p.hp : "?/?";
        const info = [p.tipo?.join("/"), "SR " + p.sr, p.ac != null ? "AC " + p.ac : ""].filter(Boolean).join(", ");
        npcs.push({ tipo: "pokemon", nome: p.nome, hp, info });
      });
      renderNpcs();
    }
    function adicionarEncontroAIniciativa(rolar) {
      ultimoEncontro.forEach(p => {
        const valor = rolar ? Math.floor(Math.random() * 20) + 1 : 0;
        iniciativa.push({ nome: p.nome, valor });
      });
      iniciativa.sort((a, b) => b.valor - a.valor);
      renderIniciativa();
    }
    function prepararCombate() {
      ultimoEncontro.forEach(p => {
        iniciativa.push({ nome: p.nome, valor: Math.floor(Math.random() * 20) + 1 });
        const hp = p.hp != null ? p.hp + "/" + p.hp : "?/?";
        const info = [p.tipo?.join("/"), "SR " + p.sr, p.ac != null ? "AC " + p.ac : ""].filter(Boolean).join(", ");
        npcs.push({ tipo: "pokemon", nome: p.nome, hp, info });
      });
      iniciativa.sort((a, b) => b.valor - a.valor);
      iniciativaTurnoAtual = 0;
      renderIniciativa();
      renderNpcs();
    }
    async function rolarEncontro() {
      const nivel = parseIntVal($("enc-nivel")?.value, 5);
      const srMax = parseFloat($("enc-sr-max")?.value) || 10;
      const tipo = ($("enc-tipo")?.value || "").trim();
      const qty = Math.min(Math.max(parseIntVal($("enc-qty")?.value, 1), 1), 6);
      const params = new URLSearchParams({ nivel, sr_max: srMax, sr_min: 0, qty });
      if (tipo) params.set("tipo", tipo);
      const res = await fetch("/api/pokedex/encounter?" + params, CREDS);
      const json = await res.json();
      if (!json.ok) {
        renderEncounterResult([]);
        $("encounter-result").innerHTML = "<span class='err'>" + escapeHtml(json.erro || "Erro") + "</span>";
        return;
      }
      if (!json.encontros || json.encontros.length === 0) {
        renderEncounterResult([]);
        $("encounter-result").innerHTML = "<span>" + escapeHtml(json.msg || "Nenhum Pokémon encontrado.") + "</span>";
        return;
      }
      renderEncounterResult(json.encontros, true);
      if (json.candidatos) $("encounter-result").appendChild(Object.assign(document.createElement("small"), { textContent: " (" + json.candidatos + " candidatos)" }));
    }
    let encManualLista = [];
    async function abrirEncontroManual() {
      const wrap = $("encounter-manual-wrap");
      const list = $("enc-manual-list");
      if (!wrap || !list) return;
      wrap.classList.toggle("hidden", !wrap.classList.contains("hidden"));
      if (!wrap.classList.contains("hidden")) {
        const nivel = parseIntVal($("enc-nivel")?.value, 5);
        const srMax = parseFloat($("enc-sr-max")?.value) || 10;
        const tipo = ($("enc-tipo")?.value || "").trim();
        const params = new URLSearchParams({ nivel, sr_max: srMax, sr_min: 0, list: "1" });
        if (tipo) params.set("tipo", tipo);
        const res = await fetch("/api/pokedex/encounter?" + params, CREDS);
        const json = await res.json();
        if (!json.ok || !json.encontros) { list.innerHTML = "<p>Erro ao carregar.</p>"; return; }
        encManualLista = json.encontros.slice(0, 80);
        const escolhidos = [];
        list.innerHTML = "<p>Clique para adicionar:</p>" + encManualLista.map((p, i) => {
          const tipos = (p.tipo || []).join("/");
          const ac = p.ac != null ? "AC " + p.ac : "";
          const hp = p.hp != null ? "HP " + p.hp : "";
          return `<button type="button" class="enc-manual-item" data-i="${i}">${escapeHtml(p.nome)} — SR ${p.sr} (${escapeHtml(tipos)}) ${ac} ${hp}</button>`;
        }).join("");
        list.querySelectorAll(".enc-manual-item").forEach(btn => {
          btn.onclick = () => {
            const p = encManualLista[parseInt(btn.dataset.i, 10)];
            if (!p) return;
            escolhidos.push(p);
            ultimoEncontro = [...escolhidos];
            renderEncounterResult(ultimoEncontro, true);
          };
        });
      }
    }
    $("btn-encounter")?.addEventListener("click", rolarEncontro);
    $("btn-encounter-manual")?.addEventListener("click", abrirEncontroManual);

    // CD Captura
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

    // Iniciativa
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
    function removeIniciativa(i) { iniciativa.splice(i, 1); renderIniciativa(); }
    function renderIniciativa() {
      const ul = $("iniciativa-lista");
      ul.innerHTML = iniciativa.map((item, i) => {
        const isTurno = i === iniciativaTurnoAtual;
        const valorStr = item.valor != null && item.valor !== "" ? item.valor : "—";
        return `<li class="${isTurno ? "inic-turno-atual" : ""}"><span class="inic-num">${valorStr}</span><span class="inic-nome">${escapeHtml(item.nome)}</span><button type="button" class="inic-remove" data-i="${i}" title="Remover">✕</button></li>`;
      }).join("");
      ul.querySelectorAll(".inic-remove").forEach(btn => btn.onclick = () => removeIniciativa(parseInt(btn.dataset.i, 10)));
    }
    function rolarIniciativaTodos() {
      iniciativa.forEach(item => {
        if (item.valor === undefined || item.valor === null || item.valor === 0)
          item.valor = Math.floor(Math.random() * 20) + 1;
      });
      iniciativa.sort((a, b) => (b.valor || 0) - (a.valor || 0));
      renderIniciativa();
    }
    async function importarJogadoresIniciativa() {
      if (!sessaoCodigo) return;
      const res = await fetch("/api/mestre/session/" + sessaoCodigo + "/jogadores", CREDS);
      const json = await res.json();
      if (!json.ok || !json.jogadores || json.jogadores.length === 0) return;
      json.jogadores.forEach(j => {
        iniciativa.push({ nome: j.nome || "Jogador", valor: 0 });
        (j.ficha?.pokemons || []).forEach(p => iniciativa.push({ nome: (p.nome || "?") + " (" + (j.nome || "J") + ")", valor: 0 }));
      });
      renderIniciativa();
    }
    function proximoIniciativa() {
      if (iniciativa.length === 0) return;
      iniciativaTurnoAtual = (iniciativaTurnoAtual + 1) % iniciativa.length;
      renderIniciativa();
    }
    $("inic-add")?.addEventListener("click", addIniciativa);
    $("inic-valor")?.addEventListener("keydown", e => { if (e.key === "Enter") addIniciativa(); });
    $("inic-rolar-todos")?.addEventListener("click", rolarIniciativaTodos);
    $("inic-importar-jogadores")?.addEventListener("click", importarJogadoresIniciativa);
    $("inic-proximo")?.addEventListener("click", proximoIniciativa);
    $("inic-limpar")?.addEventListener("click", () => { iniciativa = []; iniciativaTurnoAtual = 0; renderIniciativa(); });

    // NPCs
    function addNpc() {
      const nome = $("npc-nome")?.value?.trim();
      const hp = $("npc-hp")?.value?.trim();
      if (!nome) return;
      npcs.push({ tipo: "pokemon", nome, hp: hp || "—", info: "" });
      $("npc-nome").value = "";
      $("npc-hp").value = "";
      renderNpcs();
    }
    async function addNpcFromPokedex() {
      const inp = $("npc-pokedex-search");
      const nome = inp?.value?.trim();
      if (!nome) return;
      const pokedex = await loadPokedex();
      const entry = Object.entries(pokedex).find(([k]) => k.toLowerCase() === nome.toLowerCase());
      if (!entry) return;
      const [n, p] = entry;
      const hp = p.hp != null ? p.hp + "/" + p.hp : "?/?";
      const info = [(p.tipo || []).join("/"), "SR " + p.sr, p.ac != null ? "AC " + p.ac : ""].filter(Boolean).join(", ");
      npcs.push({ tipo: "pokemon", nome: n, hp, info });
      inp.value = "";
      renderNpcs();
    }
    $("npc-add")?.addEventListener("click", addNpc);
    $("npc-pokedex-search")?.addEventListener("keydown", e => { if (e.key === "Enter") addNpcFromPokedex(); });

    function removeNpc(i) {
      npcs.splice(i, 1);
      const next = {};
      Object.entries(npcsExpandidos).forEach(([k, v]) => {
        const ki = parseInt(k, 10);
        if (ki < i) next[ki] = v;
        else if (ki > i) next[ki - 1] = v;
      });
      npcsExpandidos = next;
      renderNpcs();
    }
    function toggleNpcExpandido(i) {
      npcsExpandidos[i] = !npcsExpandidos[i];
      renderNpcs();
    }
    function updateNpcPokeHp(npcIdx, pokeIdx, delta) {
      const npc = npcs[npcIdx];
      if (!npc || npc.tipo !== "humano" || !npc.pokemons) return;
      const p = npc.pokemons[pokeIdx];
      if (!p) return;
      const cur = parseIntVal(p.hp, 0);
      const mx = parseIntVal(p.hp_max, 1);
      p.hp = String(Math.max(0, Math.min(cur + delta, mx)));
      renderNpcs();
    }
    function curarNpcPoke(npcIdx, pokeIdx) {
      const npc = npcs[npcIdx];
      if (!npc || npc.tipo !== "humano" || !npc.pokemons) return;
      const p = npc.pokemons[pokeIdx];
      if (!p) return;
      p.hp = String(p.hp_max || p.hp);
      renderNpcs();
    }

    function renderNpcs() {
      const container = $("npc-lista");
      container.innerHTML = npcs.map((n, i) => {
        if (n.tipo === "humano") {
          const expandido = npcsExpandidos[i];
          const pokes = n.pokemons || [];
          const totalHp = pokes.reduce((s, p) => s + parseIntVal(p.hp, 0), 0);
          const maxHp = pokes.reduce((s, p) => s + parseIntVal(p.hp_max, 1), 0);
          const hpStr = maxHp > 0 ? totalHp + "/" + maxHp : "—";
          return `
            <div class="npc-treinador">
              <div class="npc-treinador-header" data-i="${i}">
                <span class="npc-nome">${escapeHtml(n.nome)}</span>
                <span class="npc-treinador-badge">Treinador</span>
                <span class="npc-hp">${hpStr} HP</span>
                <button type="button" class="npc-remove" data-i="${i}" title="Remover">✕</button>
              </div>
              ${expandido ? `<div class="npc-treinador-equipe">${pokes.map((p, j) => {
                const cur = parseIntVal(p.hp, 0);
                const mx = parseIntVal(p.hp_max, 1);
                const pct = mx > 0 ? Math.min(1, cur / mx) * 100 : 0;
                return `<div class="poke-mini">
                  <span class="poke-nome">${escapeHtml(p.nome)}</span>
                  <span class="poke-hp">${cur}/${mx}</span>
                  <div class="poke-hp-ctrl">
                    <button type="button" data-npc="${i}" data-poke="${j}" data-delta="-1">−</button>
                    <button type="button" data-npc="${i}" data-poke="${j}" data-delta="1">+</button>
                  </div>
                  <button type="button" class="poke-curar btn-ghost btn-sm" data-npc="${i}" data-poke="${j}">Curar</button>
                </div>`;
              }).join("")}</div>` : ""}
            </div>`;
        }
        return `
          <div class="npc-item">
            <div class="npc-item-header">
              <span class="npc-nome">${escapeHtml(n.nome)}</span>
              <span class="npc-hp">${escapeHtml(n.hp)}</span>
              ${n.info ? `<span class="npc-info" title="${escapeHtml(n.info)}">${escapeHtml(n.info)}</span>` : ""}
              <button type="button" class="npc-remove" data-i="${i}">✕</button>
            </div>
          </div>`;
      }).join("");
      container.querySelectorAll(".npc-treinador-header").forEach(el => {
        const i = parseInt(el.dataset.i, 10);
        if (isNaN(i)) return;
        el.onclick = (e) => { if (!e.target.classList.contains("npc-remove")) toggleNpcExpandido(i); };
      });
      container.querySelectorAll(".npc-remove").forEach(btn => {
        const i = parseInt(btn.dataset.i, 10);
        if (!isNaN(i)) btn.onclick = (e) => { e.stopPropagation(); removeNpc(i); };
      });
      container.querySelectorAll(".poke-hp-ctrl button").forEach(btn => {
        const ni = parseInt(btn.dataset.npc, 10);
        const pi = parseInt(btn.dataset.poke, 10);
        const d = parseInt(btn.dataset.delta, 10);
        btn.onclick = () => updateNpcPokeHp(ni, pi, d);
      });
      container.querySelectorAll(".poke-curar").forEach(btn => {
        const ni = parseInt(btn.dataset.npc, 10);
        const pi = parseInt(btn.dataset.poke, 10);
        btn.onclick = () => curarNpcPoke(ni, pi);
      });
    }

    // Modal Treinador NPC
    function abrirModalTreinador() {
      treinadorEmEdicao = { nome: "", pokemons: [] };
      $("modal-treinador-nome").value = "";
      const preview = $("modal-treinador-equipe");
      if (ultimoEncontro.length > 0) {
        treinadorEmEdicao.pokemons = ultimoEncontro.map(p => ({
          nome: p.nome, hp: String(p.hp || 20), hp_max: String(p.hp || 20), tipo: (p.tipo || []).join("/"), sr: p.sr
        }));
        preview.innerHTML = "<p><strong>Equipe sugerida do encontro:</strong></p><p>" + treinadorEmEdicao.pokemons.map(p => escapeHtml(p.nome) + " (" + p.hp + "/" + p.hp_max + ")").join(", ") + "</p>";
      } else {
        preview.innerHTML = "<p class='treinador-hint'>Role um encontro primeiro, ou adicione Pokémon como NPCs e use + Treinador depois.</p>";
      }
      $("modal-npc-treinador").classList.remove("hidden");
    }
    function fecharModalTreinador() {
      $("modal-npc-treinador").classList.add("hidden");
    }
    function adicionarTreinadorNpc() {
      const nome = $("modal-treinador-nome")?.value?.trim();
      if (!nome) return;
      const pokemons = treinadorEmEdicao.pokemons.length ? treinadorEmEdicao.pokemons : [];
      npcs.push({ tipo: "humano", nome, pokemons });
      npcsExpandidos[npcs.length - 1] = true;
      fecharModalTreinador();
      renderNpcs();
    }
    $("npc-add-treinador")?.addEventListener("click", abrirModalTreinador);
    $("modal-treinador-cancel")?.addEventListener("click", fecharModalTreinador);
    $("modal-treinador-ok")?.addEventListener("click", adicionarTreinadorNpc);

    // Guia
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
        let conteudo = sec.conteudo || "";
        const lin = conteudo.split("\n");
        const frag = [];
        let inT = false, firstRow = true;
        for (const ln of lin) {
          if (/^\|.+\|$/.test(ln.trim())) {
            const cels = ln.split("|").filter(Boolean).map(c => c.trim());
            if (/^[-:\s]+$/.test(cels.join(""))) continue;
            if (!inT) { frag.push("<table class='guia-table'>"); inT = true; firstRow = true; }
            const tag = firstRow ? "th" : "td";
            frag.push((firstRow ? "<thead><tr>" : "<tr>") + cels.map(c => `<${tag}>${fmt(c)}</${tag}>`).join("") + (firstRow ? "</tr></thead><tbody>" : "</tr>"));
            firstRow = false;
          } else {
            if (inT) { frag.push("</tbody></table>"); inT = false; }
            if (ln.trim()) frag.push(fmt(ln) + "<br>");
          }
        }
        if (inT) frag.push("</tbody></table>");
        return `<details class="guia-details"><summary class="guia-summary">${escapeHtml(sec.titulo)}</summary><div class="guia-content">${frag.join("")}</div></details>`;
      }).join("");
    }
    carregarGuia();

    $("btn-logout")?.addEventListener("click", doLogout);
  }

  initAuth();
})();
