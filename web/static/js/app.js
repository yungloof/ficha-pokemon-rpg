/**
 * Ficha RPG Pokémon - Versão Web
 * Compatível 100% com fichas salvas da versão Flet.
 */
(function () {
  const PERICIAS_MAP = {
    "Atletismo": "for", "Acrobacia": "des", "Furtividade": "des", "Prestidigitação": "des",
    "Arcanismo": "int", "História": "int", "Investigação": "int", "Natureza": "int", "Religião": "int",
    "Adestrar Animais": "sab", "Intuição": "sab", "Medicina": "sab", "Percepção": "sab", "Sobrevivência": "sab",
    "Atuação": "car", "Enganação": "car", "Intimidação": "car", "Persuasão": "car"
  };
  const TALENTOS_PERICIA = { "Acrobata": "Acrobacia", "Dedos Rapidos": "Prestidigitação", "Musculoso": "Atletismo", "Perceptivo": "Percepção", "Sorrateiro": "Furtividade" };
  const ATTR_DISPLAY = { "for": "FOR", "des": "DES", "con": "CON", "int": "INT", "sab": "SAB", "car": "CAR" };

  const SR_OPCOES = [0.125, 0.25, 0.5, 1, 2, 3, 5, 6, 8, 10, 12, 13, 14, 15];
  const MAX_EQUIPE = 6;

  let C = {}; // Constantes (carregadas da API)
  let stats = {};
  let historicoRolagens = [];
  let editingPokeIndex = -1;
  let pokedexCache = null; // Cache do Pokédex para autocomplete
  const POKE_SPRITE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon";

  function getPokeSpriteIndex(nome) {
    if (!pokedexCache || !nome) return null;
    const n = (nome || "").trim();
    const entry = Object.entries(pokedexCache).find(([k]) => k.toLowerCase() === n.toLowerCase());
    return entry ? entry[1]?.index : null;
  }

  function getStatsDefault() {
    return {
      nome: "Treinador", nivel: "1", classe: "", regiao_origem: "", origem_jornada: "",
      especializacao: "", hp_atual: "10", hp_max: "10", deslocamento: "9m",
      pokedollars: "0", for: "8", des: "8", con: "8", int: "8", sab: "8", car: "8",
      pokebolas: "5x Pokébolas", itens_chave: "Licença de Treinador\nPokédex",
      consumiveis: "1x Poção", pacote_aventura: "Aventureiro", pokemons: [],
      pericias_proficientes: ["Adestrar Animais"], talentos: [], tm_escolhido: "",
      especializacao_2: "", especializacao_3: "",
      espec_pericia_sombrio: "Furtividade", espec_pericia_alquimista: "Medicina", espec_pericia_esquiador: "Atuação",
      espec_atributo_artista_marcial: "for", espec_atributo_alpinista: "for", espec_atributo_metalurgico: "for", espec_atributo_jogador_de_equipe: "car"
    };
  }

  function especKey(nome) {
    return (nome || "").toLowerCase().replace(/ /g, "_").replace(/í/g, "i").replace(/ó/g, "o").replace(/ã/g, "a").replace(/ú/g, "u").replace(/ç/g, "c");
  }

  function calcMod(val) {
    const n = parseInt(val, 10);
    return isNaN(n) ? 0 : Math.floor((n - 10) / 2);
  }

  function parseIntVal(v, def = 0) {
    const n = parseInt(v, 10);
    return isNaN(n) ? def : n;
  }

  function statCost(val) {
    if (val < (C.POINT_BUY_MIN || 8) || val > (C.POINT_BUY_MAX || 15)) return null;
    if (val <= 13) return val - (C.POINT_BUY_MIN || 8);
    return 5 + (val - 13) * 2;
  }

  function getLevelData(lvl) {
    lvl = parseIntVal(lvl, 1);
    const prof = 2 + Math.floor((lvl - 1) / 4);
    let maxSr = 2;
    if (lvl >= 17) maxSr = 15;
    else if (lvl >= 14) maxSr = 14;
    else if (lvl >= 11) maxSr = 12;
    else if (lvl >= 8) maxSr = 10;
    else if (lvl >= 6) maxSr = 8;
    else if (lvl >= 3) maxSr = 5;
    let slots = 3;
    if (lvl >= 15) slots = 6;
    else if (lvl >= 10) slots = 5;
    else if (lvl >= 5) slots = 4;
    return { prof, maxSr, slots };
  }

  function getEspecializacoesAtivas() {
    const lvl = parseIntVal(stats.nivel || $("nivel")?.value, 1);
    const list = [$("especializacao")?.value || stats.especializacao || ""];
    if (lvl >= 7) list.push($("especializacao_2")?.value || stats.especializacao_2 || "");
    if (lvl >= 18) list.push($("especializacao_3")?.value || stats.especializacao_3 || "");
    return list.filter(Boolean);
  }
  function getPericiasAuto() {
    const pericias = ["Adestrar Animais"];
    const regiao = $("regiao").value;
    const reg = C.REGIOES_ORIGEM && C.REGIOES_ORIGEM[regiao];
    if (reg && reg.pericia) pericias.push(reg.pericia);
    const especs = getEspecializacoesAtivas();
    especs.forEach(espec => {
      const esp = C.ESPECIALIZACOES && C.ESPECIALIZACOES[espec];
      if (esp) {
        if (esp.pericias_opcoes) {
          const key = `espec_pericia_${especKey(espec)}`;
          const chosen = stats[key];
          pericias.push(chosen && esp.pericias_opcoes.includes(chosen) ? chosen : esp.pericias_opcoes[0]);
        } else if (esp.pericias) pericias.push(...esp.pericias);
      }
    });
    const origem = $("origem_jornada").value;
    const orig = C.ORIGENS_JORNADA && C.ORIGENS_JORNADA[origem];
    if (orig && orig.pericias) pericias.push(...orig.pericias);
    return [...new Set(pericias)];
  }

  const TIPO_ESPEC_MAP = {
    "Voador": "Guardião dos Pássaros", "Inseto": "Maníaco por Insetos", "Terra": "Campista",
    "Dragão": "Domador de Dragões", "Elétrico": "Engenheiro", "Fogo": "Piromaníaco",
    "Grama": "Jardineiro", "Lutador": "Artista Marcial", "Pedra": "Alpinista",
    "Fantasma": "Místico", "Aço": "Metalúrgico", "Psíquico": "Psíquico", "Água": "Nadador",
    "Fada": "Encantador", "Sombrio": "Sombrio", "Venenoso": "Alquimista",
    "Normal": "Jogador de Equipe", "Gelo": "Esquiador"
  };
  function getTiposArray(tipo) {
    if (!tipo) return [];
    return String(tipo).split("/").map(t => t.trim()).filter(Boolean);
  }

  function getBonusTipoPokemon(tipo) {
    const especs = getEspecializacoesAtivas();
    const tipos = getTiposArray(tipo);
    for (const t of tipos) {
      const match = TIPO_ESPEC_MAP[t];
      if (match && especs.includes(match)) return 1;
    }
    return 0;
  }

  function syncStatsFromUI() {
    stats.nome = $("nome").value || "Treinador";
    stats.nivel = $("nivel").value || "1";
    stats.classe = $("classe").value || "";
    stats.regiao_origem = $("regiao").value || "";
    stats.origem_jornada = $("origem_jornada").value || "";
    stats.especializacao = $("especializacao")?.value || "";
    stats.especializacao_2 = $("especializacao_2")?.value || "";
    stats.especializacao_3 = $("especializacao_3")?.value || "";
    stats.tm_escolhido = $("tm").value || "";
    stats.hp_atual = $("hp_atual").value || "10";
    stats.hp_max = $("hp_max").value || "10";
    stats.deslocamento = $("deslocamento").value || "9m";
    stats.pokedollars = $("pokedollars").value || "0";
    stats.pokebolas = $("pokebolas").value || "";
    stats.itens_chave = $("itens_chave").value || "";
    stats.consumiveis = $("consumiveis").value || "";
    stats.pacote_aventura = $("pacote_aventura").value || "Aventureiro";
    ["for", "des", "con", "int", "sab", "car"].forEach(a => { stats[a] = ($(a) && $(a).value) || "8"; });
    const espec = $("especializacao")?.value || stats.especializacao;
    const esp = C.ESPECIALIZACOES && C.ESPECIALIZACOES[espec];
    if (esp) {
      if (esp.pericias_opcoes && $("espec_pericia")) stats[`espec_pericia_${especKey(espec)}`] = $("espec_pericia").value;
      if (esp.atributo_opcoes && $("espec_atributo")) stats[`espec_atributo_${especKey(espec)}`] = $("espec_atributo").value;
    }
    const auto = getPericiasAuto();
    const talentosPer = (stats.talentos || []).map(t => TALENTOS_PERICIA[t]).filter(Boolean);
    let prof = [...new Set([...auto, ...talentosPer])];
    Object.keys(PERICIAS_MAP).forEach(p => {
      const cb = document.querySelector(`[data-pericia="${p}"]`);
      if (cb && cb.checked && !prof.includes(p)) prof.push(p);
    });
    stats.pericias_proficientes = prof;
  }

  function addHistorico(tipo, texto) {
    historicoRolagens.unshift({ tipo, texto });
    if (historicoRolagens.length > 15) historicoRolagens.pop();
    renderHistorico();
  }

  function rollDice(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  let rollAnimating = false;
  let sessaoCodigo = null;
  let sessaoJogador = null;

  function sendRollToMestre(mainNum, msg, tipo) {
    if (!sessaoCodigo) return;
    fetch(`/api/mestre/session/${encodeURIComponent(sessaoCodigo)}/roll`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jogador: sessaoJogador || stats.nome || "Desconhecido",
        tipo: tipo || "Rolagem",
        msg: msg || "",
        mainNum: mainNum,
        ts: new Date().toISOString().slice(11, 19),
      }),
    }).catch(() => {});
  }

  function withRollAnimation(rollFn) {
    if (rollAnimating) return;
    const result = rollFn();
    if (!result) return;
    rollAnimating = true;
    const { mainNum, msg, onComplete, tipo } = result;
    const overlay = document.getElementById("roll-overlay");
    const numEl = overlay?.querySelector(".roll-result-num");
    const msgEl = overlay?.querySelector(".roll-result-msg");
    const spriteEl = overlay?.querySelector(".roll-pokeball-sprite");
    if (!overlay || !numEl) { rollAnimating = false; return; }
    numEl.textContent = "?";
    if (msgEl) msgEl.textContent = "";
    overlay.classList.remove("reveal", "roll-crit", "roll-fumble");
    overlay.classList.toggle("roll-crit", mainNum === 20);
    overlay.classList.toggle("roll-fumble", mainNum === 1);
    overlay.setAttribute("aria-hidden", "false");
    if (spriteEl) {
      spriteEl.style.animation = "none";
      void spriteEl.offsetHeight;
      spriteEl.style.animation = "";
    }
    requestAnimationFrame(() => {
      overlay.classList.remove("roll-overlay-hidden");
    });
    const tReveal = setTimeout(() => {
      numEl.textContent = String(mainNum);
      if (msgEl) msgEl.textContent = (msg || "").replace(/^(🎲|🎯|💥|⚡|👑)\s*/, "");
      overlay.classList.add("reveal");
    }, 1100);
    setTimeout(() => {
      clearTimeout(tReveal);
      overlay.classList.add("roll-overlay-hidden");
      overlay.classList.remove("reveal");
      overlay.setAttribute("aria-hidden", "true");
      rollAnimating = false;
      sendRollToMestre(mainNum, msg, tipo);
      try { onComplete && onComplete(); } catch (e) { console.error(e); }
    }, 3800);
  }

  function $(id) {
    return document.getElementById(id);
  }

  function escapeHtml(s) {
    if (!s) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/\n/g, "<br>");
  }

  function markdownToHtml(md) {
    if (!md) return "";
    const lines = md.split("\n");
    let html = "";
    let inTable = false;
    let tableRows = [];

    function flushTable() {
      if (tableRows.length === 0) return "";
      const [header, ...rows] = tableRows;
      let out = "<table><thead><tr>";
      header.forEach(c => { out += "<th>" + c.trim() + "</th>"; });
      out += "</tr></thead><tbody>";
      rows.forEach(row => {
        out += "<tr>";
        row.forEach(c => { out += "<td>" + c.trim().replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>") + "</td>"; });
        out += "</tr>";
      });
      out += "</tbody></table>";
      return out;
    }

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();
      const isTableRow = /^\|.+\|$/.test(trimmed);
      const isSepRow = isTableRow && !/[a-zA-ZáàâãéèêíìîóòôõúùûçÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ0-9ºª]/.test(trimmed);

      if (isTableRow && isSepRow) continue;

      if (isTableRow && !isSepRow) {
        if (!inTable) {
          html += flushTable();
          tableRows = [];
          inTable = true;
        }
        const cells = line.slice(1, -1).split("|");
        tableRows.push(cells);
      } else {
        if (inTable) {
          html += flushTable();
          tableRows = [];
          inTable = false;
        }
        if (line.startsWith("## ")) {
          html += "<h2>" + line.slice(3).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>") + "</h2>";
        } else if (line.startsWith("# ")) {
          html += "<h2>" + line.slice(2).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>") + "</h2>";
        } else if (line.startsWith("### ")) {
          html += "<h3>" + line.slice(4).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>") + "</h3>";
        } else if (line.startsWith("- ") || line.startsWith("• ")) {
          const bullet = line.startsWith("• ") ? "• " : "- ";
          html += "<ul><li>" + line.slice(bullet.length).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>") + "</li>";
          while (i + 1 < lines.length && (lines[i + 1].startsWith("- ") || lines[i + 1].startsWith("• "))) {
            i++;
            const b = lines[i].startsWith("• ") ? "• " : "- ";
            html += "<li>" + lines[i].slice(b.length).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>") + "</li>";
          }
          html += "</ul>";
        } else if (/^\d+\.\s/.test(line)) {
          html += "<p>" + line.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>") + "</p>";
        } else if (line.trim()) {
          html += "<p>" + line.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>") + "</p>";
        } else {
          html += "<br>";
        }
      }
    }
    if (inTable) html += flushTable();
    return html;
  }

  function showToast(msg, ok = true, isRoll = false) {
    const t = $("toast");
    t.textContent = msg;
    t.className = "toast " + (ok ? "" : "err") + (isRoll ? " roll-result" : "");
    t.classList.remove("hidden");
    setTimeout(() => t.classList.add("hidden"), 4000);
  }

  function renderHistorico() {
    const el = $("historico-list");
    if (!el) return;
    el.innerHTML = historicoRolagens.slice(0, 10).map(h => `<div>${h.texto}</div>`).join("");
  }

  function renderTabs() {
    document.querySelectorAll(".tab").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".tab").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
        btn.classList.add("active");
        const tab = btn.dataset.tab;
        const panel = $("panel-" + tab);
        if (panel) panel.classList.add("active");
      });
    });
  }

  function buildSelect(id, opts, value, onChange) {
    const sel = $(id);
    if (!sel) return;
    sel.innerHTML = opts.map(o => `<option value="${o}">${o}</option>`).join("");
    if (value) sel.value = value;
    sel.onchange = () => { onChange && onChange(); atualizar(); };
  }

  function populateConstants() {
    const r = C.REGIOES_ORIGEM || {};
    buildSelect("regiao", ["Nenhuma", ...Object.keys(r).filter(k => k !== "Nenhuma")], stats.regiao_origem || "Nenhuma");
    const o = C.ORIGENS_JORNADA || {};
    buildSelect("origem_jornada", ["Nenhuma", ...Object.keys(o).filter(k => k !== "Nenhuma")], stats.origem_jornada || "Nenhuma");
    const esp = C.ESPECIALIZACOES || {};
    const espOpts = ["Nenhuma", ...Object.keys(esp).filter(k => k !== "Nenhuma")];
    buildSelect("especializacao", espOpts, stats.especializacao || "Nenhuma");
    buildSelect("especializacao_2", espOpts, stats.especializacao_2 || "Nenhuma");
    buildSelect("especializacao_3", espOpts, stats.especializacao_3 || "Nenhuma");
    const cls = C.CLASSES_TREINADOR || {};
    buildSelect("classe", ["Nenhuma", ...Object.keys(cls).filter(k => k !== "Nenhuma")], stats.classe || "Nenhuma");
    const pac = C.PACOTES_AVENTURA || {};
    buildSelect("pacote_aventura", Object.keys(pac), stats.pacote_aventura || "Aventureiro");
    const tms = C.LISTA_TMS || [];
    buildSelect("tm", [""].concat(tms), stats.tm_escolhido || "");
  }

  function atualizar() {
    syncStatsFromUI();
    const talentos = stats.talentos || [];
    const lvl = parseIntVal(stats.nivel, 1);
    const { prof, maxSr, slots } = getLevelData(stats.nivel);
    $("prof").textContent = "+" + prof;
    $("max_sr").textContent = maxSr;
    $("slots").textContent = slots;

    let modDes = calcMod(stats.des);
    let bonusCa = 0;
    if (stats.regiao_origem === "Sinnoh") bonusCa = 2;
    $("ca").textContent = 10 + modDes + bonusCa;

    let bonusInic = talentos.includes("Alerta") ? 5 : 0;
    $("inic").textContent = (modDes + bonusInic >= 0 ? "+" : "") + (modDes + bonusInic) + (bonusInic ? " (Alerta)" : "");

    const reg = C.REGIOES_ORIGEM && C.REGIOES_ORIGEM[stats.regiao_origem];
    let totalCon = parseIntVal(stats.con, 8);
    try {
      const especsAtivos = getEspecializacoesAtivas();
      let bonusR = (reg && reg.bonus) ? (reg.bonus.con || 0) : 0;
      let bonusE = 0, bonusT = 0;
      (especsAtivos || []).forEach(e => {
        const eSp = C.ESPECIALIZACOES && C.ESPECIALIZACOES[e];
        if (!eSp) return;
        let atrEsp = eSp.atributo;
        if (eSp.atributo_opcoes) atrEsp = stats[`espec_atributo_${especKey(e)}`] || eSp.atributo_opcoes[0];
        if (atrEsp === "con") bonusE++;
      });
      if (talentos.includes("Resistente")) bonusT++;
      if (talentos.includes("Resiliente")) bonusT++;
      totalCon += bonusR + bonusE + bonusT;
    } catch (e) { console.warn("HP calc:", e); }
    const conMod = calcMod(totalCon);
    let hpSug = (10 + conMod) + ((lvl - 1) * (2 + conMod));
    if (talentos.includes("Robusto")) hpSug += 2 * lvl;
    const hpSugEl = $("hp-sug");
    if (hpSugEl) hpSugEl.textContent = `(Sugerido: ${Math.max(1, hpSug)} | DV d8)`;

    const cur = parseIntVal(stats.hp_atual, 0);
    const mx = parseIntVal(stats.hp_max, 1);
    const fill = $("hp-bar-fill");
    if (fill) fill.style.width = mx > 0 ? Math.max(0, Math.min(cur, mx)) / mx * 100 + "%" : "0%";

    // Descrições
    const regiaoDesc = $("regiao-desc");
    const regiaoHab = $("regiao-hab");
    if (regiaoDesc) regiaoDesc.innerHTML = reg ? escapeHtml(reg.desc || "") : "";
    if (regiaoHab) regiaoHab.innerHTML = reg && reg.habilidade ? "⚡ " + escapeHtml(reg.habilidade) : "";

    const orig = C.ORIGENS_JORNADA && C.ORIGENS_JORNADA[stats.origem_jornada];
    if (orig) {
      $("origem-desc").innerHTML = escapeHtml((orig.titulo ? `"${orig.titulo}" - ` : "") + (orig.desc || ""));
      const habText = orig.hab_nome ? `⭐ <strong>${escapeHtml(orig.hab_nome)}</strong><br>${escapeHtml(orig.hab_desc || "")}` : "";
      $("origem-hab").innerHTML = habText;
      $("origem-equip").innerHTML = orig.equip ? "🎁 Bônus: " + escapeHtml(orig.equip) : "";
      $("container-tm").classList.toggle("hidden", stats.origem_jornada !== "Estudioso");
    } else {
      $("origem-desc").innerHTML = $("origem-hab").innerHTML = $("origem-equip").innerHTML = "";
      $("container-tm").classList.add("hidden");
    }
    $("container-espec-2")?.classList.toggle("hidden", lvl < 7);
    $("container-espec-3")?.classList.toggle("hidden", lvl < 18);
    const especs = [stats.especializacao, stats.especializacao_2, stats.especializacao_3].filter(e => e && e !== "Nenhuma");
    const descParts = especs.map(e => C.ESPECIALIZACOES?.[e]?.desc).filter(Boolean);
    $("espec-desc").innerHTML = descParts.length ? descParts.map(d => escapeHtml(d)).join("<br><br>") : "";
    const esp = C.ESPECIALIZACOES && C.ESPECIALIZACOES[stats.especializacao];
    if (esp) {
      $("container-espec-pericia").classList.toggle("hidden", !esp.pericias_opcoes);
      if (esp.pericias_opcoes) {
        const specSel = $("espec_pericia");
        if (specSel) {
          specSel.innerHTML = esp.pericias_opcoes.map(p => `<option value="${p}">${p}</option>`).join("");
          const key = `espec_pericia_${especKey(stats.especializacao)}`;
          specSel.value = stats[key] || esp.pericias_opcoes[0];
          specSel.onchange = () => { stats[key] = specSel.value; atualizar(); };
        }
      }
      $("container-espec-atributo").classList.toggle("hidden", !esp.atributo_opcoes);
      if (esp.atributo_opcoes) {
        const attrSel = $("espec_atributo");
        if (attrSel) {
          attrSel.innerHTML = esp.atributo_opcoes.map(a => `<option value="${a}">${ATTR_DISPLAY[a] || a}</option>`).join("");
          const key = `espec_atributo_${especKey(stats.especializacao)}`;
          attrSel.value = stats[key] || esp.atributo_opcoes[0];
          attrSel.onchange = () => { stats[key] = attrSel.value; atualizar(); };
        }
      }
    }
    const cls = C.CLASSES_TREINADOR && C.CLASSES_TREINADOR[stats.classe];
    const clsStr = typeof cls === "string" ? cls : (cls && cls.desc) || "";
    const clsHabEl = $("classe-hab");
    if (clsHabEl) {
      if (typeof cls === "object" && cls && cls.hab_nome && cls.hab_desc) {
        const items = (cls.hab_desc || "").split(/\n\s*•\s*/).map(s => s.trim().replace(/^•\s*/, "")).filter(Boolean);
        clsHabEl.innerHTML = "⭐ <strong>" + escapeHtml(cls.hab_nome) + "</strong>" +
          (items.length ? items.map(item => `<div class="classe-hab-item">• ${escapeHtml(item)}</div>`).join("") : "");
      } else {
        clsHabEl.innerHTML = "";
      }
    }
    $("classe-desc").innerHTML = escapeHtml(clsStr);
    const pac = C.PACOTES_AVENTURA && C.PACOTES_AVENTURA[stats.pacote_aventura];
    $("pacote-desc").innerHTML = escapeHtml(pac || "");

    // Saves
    const lealdadeNiveis = C.LEALDADE_NIVEIS || {};
    ["for","des","con","int","sab","car"].forEach(attr => {
      const mod = calcMod(stats[attr]);
      const isProf = attr === "car" || (attr === "con" && stats.regiao_origem === "Sinnoh");
      const total = mod + (isProf ? prof : 0);
      const row = document.querySelector(`[data-save="${attr}"]`);
      if (row) {
        row.querySelector(".save-val").textContent = (total >= 0 ? "+" : "") + total + (isProf ? " ✓" : "");
      }
    });

    // Atributos
    const especsAtivos = getEspecializacoesAtivas();
    ["for","des","con","int","sab","car"].forEach(attr => {
      const inp = $(attr);
      if (!inp) return;
      let base = parseIntVal(inp.value, 8);
      let bonusR = 0, bonusE = 0, bonusT = 0;
      if (reg && reg.bonus) bonusR = reg.bonus[attr] || 0;
      especsAtivos.forEach(e => {
        const eSp = C.ESPECIALIZACOES && C.ESPECIALIZACOES[e];
        if (!eSp) return;
        let atrEsp = eSp.atributo;
        if (eSp.atributo_opcoes) atrEsp = stats[`espec_atributo_${especKey(e)}`] || eSp.atributo_opcoes[0];
        if (atrEsp === attr) bonusE++;
      });
      if (talentos.includes("Acrobata") && attr === "des") bonusT++;
      if (talentos.includes("Atleta") && ["for","des"].includes(attr)) bonusT++;
      if (talentos.includes("Ator") && attr === "car") bonusT++;
      if (talentos.includes("Dedos Rapidos") && attr === "des") bonusT++;
      if (talentos.includes("Mente Afiada") && attr === "int") bonusT++;
      if (talentos.includes("Musculoso") && attr === "for") bonusT++;
      if (talentos.includes("Observador") && ["int","sab"].includes(attr)) bonusT++;
      if (talentos.includes("Perceptivo") && attr === "sab") bonusT++;
      if (talentos.includes("Resistente") && attr === "con") bonusT++;
      if (talentos.includes("Sorrateiro") && attr === "des") bonusT++;
      if (talentos.includes("Resiliente")) bonusT++;
      const total = base + bonusR + bonusE + bonusT;
      const modEl = document.querySelector(`[data-mod="${attr}"]`);
      if (modEl) modEl.textContent = (calcMod(total) >= 0 ? "+" : "") + calcMod(total);
      const parts = [];
      if (bonusR) parts.push(`+${bonusR} reg.`);
      if (bonusE) parts.push(`+${bonusE} esp.`);
      if (bonusT) parts.push(`+${bonusT} tal.`);
      const breakdownEl = document.querySelector(`[data-atr-breakdown="${attr}"]`);
      if (breakdownEl) {
        breakdownEl.textContent = parts.length ? `${total} (${base} ${parts.join(" ")})` : "";
        breakdownEl.title = parts.length ? (parts.includes("reg.") ? "Bônus de Região" : "") + (parts.includes("esp.") ? " | Especialização" : "") + (parts.includes("tal.") ? " | Talentos" : "") : "";
      }
    });

    // Perícias
    const auto = getPericiasAuto();
    $("pericias-auto").textContent = "Automáticas: " + [...auto].sort((a, b) => a.localeCompare(b, "pt-BR")).join(", ");
    Object.entries(PERICIAS_MAP).forEach(([per, attr]) => {
      const cb = document.querySelector(`[data-pericia="${per}"]`);
      const valEl = document.querySelector(`[data-pericia-val="${per}"]`);
      if (!cb || !valEl) return;
      const base = calcMod(stats[attr]);
      const perf = cb.checked || auto.includes(per) || TALENTOS_PERICIA[talentos.find(t => TALENTOS_PERICIA[t] === per)];
      const tot = base + (perf ? prof : 0);
      valEl.textContent = (tot >= 0 ? "+" : "") + tot;
    });

    saveToStorage();
  }

  function renderAtributos() {
    const def = getStatsDefault();
    const attrs = ["for","des","con","int","sab","car"];
    const labels = { for: "FOR", des: "DES", con: "CON", int: "INT", sab: "SAB", car: "CAR" };
    const grid = $("atributos-grid");
    grid.innerHTML = attrs.map(a => `
      <div class="atr-box">
        <label>${labels[a]}</label>
        <div class="atr-box-inner">
          <input type="number" id="${a}" value="${stats[a] || def[a] || "8"}" min="8" max="15" data-attr="${a}" />
          <span class="mod" data-mod="${a}">+0</span>
        </div>
        <span class="atr-breakdown" data-atr-breakdown="${a}"></span>
      </div>
    `).join("");
    attrs.forEach(a => {
      const inp = $(a);
      if (inp) inp.oninput = inp.onchange = () => atualizar();
    });
  }

  function renderSaves() {
    const attrs = ["for","des","con","int","sab","car"];
    const disp = { for: "FOR", des: "DES", con: "CON", int: "INT", sab: "SAB", car: "CAR" };
    const grid = $("saves-grid");
    grid.innerHTML = attrs.map(a => `
      <div class="save-row" data-save="${a}">
        <span>${disp[a]}: <span class="save-val">+0</span></span>
        <button type="button" class="btn-roll" data-roll-save="${a}">🎲</button>
      </div>
    `).join("");
    attrs.forEach(a => {
      const btn = document.querySelector(`[data-roll-save="${a}"]`);
      if (btn) btn.onclick = () => rollSave(a);
    });
  }

  function rollSave(attr) {
    withRollAnimation(() => {
      const d20 = rollDice(1, 20);
      const row = document.querySelector(`[data-save="${attr}"]`);
      const modStr = row ? row.querySelector(".save-val").textContent.replace("✓", "").trim() : "+0";
      const mod = parseInt(modStr, 10) || 0;
      const total = d20 + mod;
      const disp = ATTR_DISPLAY[attr] || attr.toUpperCase();
      let msg = `🎲 Teste ${disp}: ${d20} + ${mod >= 0 ? "+" : ""}${mod} = ${total}`;
      if (d20 === 20) msg = `🎯 ${disp}: ${d20}+${mod >= 0 ? "+" : ""}${mod} = ${total} (SUCESSO CRÍTICO!)`;
      else if (d20 === 1) msg = `💥 ${disp}: ${d20}+${mod >= 0 ? "+" : ""}${mod} = ${total} (FALHA CRÍTICA!)`;
      return {
        mainNum: d20,
        msg,
        tipo: "Save " + disp,
        onComplete: () => {
          $("resultado-save").textContent = msg;
          showToast(msg, true, true);
          addHistorico("Save " + disp, msg);
          atualizar();
        }
      };
    });
  }

  function rollInic() {
    withRollAnimation(() => {
      const modStr = $("inic").textContent.replace("(Alerta)", "").trim();
      const mod = parseInt(modStr, 10) || 0;
      const d20 = rollDice(1, 20);
      const total = d20 + mod;
      let msg = `⚡ Iniciativa: ${d20}${mod >= 0 ? "+" : ""}${mod} = ${total}`;
      if (d20 === 20) msg = `🎯 Iniciativa: ${d20}${mod >= 0 ? "+" : ""}${mod} = ${total} (20!)`;
      else if (d20 === 1) msg = `💥 Iniciativa: ${d20}${mod >= 0 ? "+" : ""}${mod} = ${total} (1...)`;
      return {
        mainNum: d20,
        msg,
        tipo: "Iniciativa",
        onComplete: () => {
          $("resultado-inic").textContent = msg;
          showToast(msg, true, true);
          addHistorico("Iniciativa", msg);
          atualizar();
        }
      };
    });
  }

  function rollDinheiro() {
    withRollAnimation(() => {
      let total, msg, mainNum;
      if (stats.origem_jornada === "Nobre") {
        total = 2600;
        mainNum = total;
        msg = "👑 Nobre: Riqueza Máxima aplicada!";
      } else {
        const d = rollDice(1, 4) + rollDice(1, 4) + rollDice(1, 4) + rollDice(1, 4);
        total = 1000 + 100 * d;
        mainNum = total;
        msg = `🎲 Rolou: ${d} → Total: ${total} ₽`;
      }
      return {
        mainNum,
        msg,
        tipo: "Dinheiro",
        onComplete: () => {
          $("pokedollars").value = total;
          $("resultado-dinheiro").textContent = msg;
          addHistorico("Dinheiro", msg);
          atualizar();
        }
      };
    });
  }

  function rollDadoGen() {
    withRollAnimation(() => {
      const sel = $("roller-dado").value || "d20";
      const faces = parseInt(sel.slice(1), 10);
      const mod = parseIntVal($("roller-mod").value, 0);
      const r = rollDice(1, faces);
      const total = r + mod;
      const msg = `🎲 ${sel}: ${r} + ${mod >= 0 ? "+" : ""}${mod} = ${total}`;
      return {
        mainNum: r,
        msg,
        tipo: sel,
        onComplete: () => {
          $("roller-result").textContent = msg;
          showToast(msg, true, true);
          addHistorico(sel, msg);
          atualizar();
        }
      };
    });
  }

  function rollPericia(pericia) {
    withRollAnimation(() => {
      const valEl = document.querySelector(`[data-pericia-val="${pericia}"]`);
      const mod = valEl ? parseIntVal(valEl.textContent, 0) : 0;
      const d20 = rollDice(1, 20);
      const total = d20 + mod;
      let msg = `🎲 ${pericia}: ${d20} + ${mod >= 0 ? "+" : ""}${mod} = ${total}`;
      if (d20 === 20) msg = `🎯 ${pericia}: ${d20}+${mod >= 0 ? "+" : ""}${mod} = ${total} (CRÍTICO!)`;
      else if (d20 === 1) msg = `💥 ${pericia}: ${d20}+${mod >= 0 ? "+" : ""}${mod} = ${total} (FALHA CRÍTICA!)`;
      return {
        mainNum: d20,
        msg,
        tipo: pericia,
        onComplete: () => {
          $("resultado-pericia").textContent = msg;
          showToast(msg, true, true);
          document.querySelectorAll(".pericia-result").forEach(el => el.remove());
          const row = document.querySelector(`[data-roll-per="${pericia}"]`)?.closest(".pericia-row");
          if (row) {
            const resEl = document.createElement("div");
            resEl.className = "pericia-result";
            resEl.textContent = msg;
            row.appendChild(resEl);
          }
          addHistorico(pericia, msg);
          atualizar();
        }
      };
    });
  }

  function renderPericias() {
    const auto = getPericiasAuto();
    const grid = $("pericias-grid");
    grid.innerHTML = Object.entries(PERICIAS_MAP)
      .sort((a, b) => a[0].localeCompare(b[0], "pt-BR"))
      .map(([per, attr]) => `
      <div class="pericia-row">
        <label style="min-width:0;flex:1">
          <input type="checkbox" data-pericia="${per}" ${(stats.pericias_proficientes || []).includes(per) ? "checked" : ""} />
          ${per}
        </label>
        <span>${attr.toUpperCase()}</span>
        <span data-pericia-val="${per}">+0</span>
        <button type="button" class="btn-roll" data-roll-per="${per}" title="Rolar">🎲</button>
      </div>
    `).join("");
    document.querySelectorAll(`[data-pericia]`).forEach(cb => cb.onchange = () => atualizar());
    document.querySelectorAll(`[data-roll-per]`).forEach(btn => {
      btn.onclick = () => rollPericia(btn.dataset.rollPer);
    });
  }

  function renderTalentos() {
    const tals = C.TALENTOS || {};
    stats.talentos = Array.isArray(stats.talentos) ? stats.talentos : [];
    const selected = stats.talentos;
    const selEl = $("talento-select");
    if (selEl) {
      const nomes = Object.keys(tals).sort((a, b) => a.localeCompare(b, "pt-BR"));
      selEl.innerHTML = '<option value="">Escolha um talento...</option>' +
        nomes.map(n => `<option value="${n}">${n} (${(tals[n].tipo || "").trim()})</option>`).join("");
    }
    const chipsEl = $("talentos-selected");
    if (chipsEl) {
      chipsEl.innerHTML = selected.map(nome => {
        const t = tals[nome] || {};
        return `<span class="talento-chip" data-talento="${nome}" title="${escapeHtml((t.desc || "").replace(/"/g, "'"))}">
          ${nome} <button type="button" class="talento-chip-remove" data-talento="${nome}" title="Remover">×</button>
        </span>`;
      }).join("");
      chipsEl.querySelectorAll(".talento-chip-remove").forEach(btn => {
        btn.onclick = (e) => { e.stopPropagation();
          const n = btn.dataset.talento;
          const idx = stats.talentos.indexOf(n);
          if (idx >= 0) { stats.talentos.splice(idx, 1); renderTalentos(); atualizar(); }
        };
      });
    }
    const descEl = $("talentos-desc");
    if (descEl) {
      descEl.innerHTML = selected.length ? selected.map(nome => {
        const t = tals[nome] || {};
        return `<div class="talento-desc-item"><strong>${escapeHtml(nome)}</strong>: ${escapeHtml(t.desc || "")}</div>`;
      }).join("") : "";
    }
  }

  function initTalentosAdd() {
    $("talento-add-btn")?.addEventListener("click", () => {
      const sel = $("talento-select");
      const nome = sel?.value;
      if (!nome || !C.TALENTOS?.[nome]) return;
      if (!stats.talentos.includes(nome)) {
        stats.talentos.push(nome);
        renderTalentos();
        atualizar();
      }
    });
  }

  function renderPokemons() {
    const list = $("lista-pokemons");
    const empty = $("lista-pokemons-empty");
    const slotsEl = $("equipe-slots");
    const pokes = stats.pokemons || [];
    const cores = C.CORES_TIPO_POKEMON || {};
    const lealdadeNiveis = C.LEALDADE_NIVEIS || {};

    if (slotsEl) slotsEl.textContent = pokes.length + "/" + MAX_EQUIPE;

    if (empty) {
      empty.classList.toggle("hidden", pokes.length > 0);
    }
    list.classList.toggle("hidden", pokes.length === 0);

    list.innerHTML = pokes.map((p, i) => {
      p.tipo = p.tipo || "Normal";
      p.natureza = p.natureza || "Nenhuma";
      p.habilidade = p.habilidade || "";
      p.nivel = p.nivel || "1";
      p.sr = p.sr || "1";
      p.lealdade = parseIntVal(p.lealdade, 0);
      const leal = lealdadeNiveis[String(p.lealdade)] || {};
      const tiposArr = getTiposArray(p.tipo);
      const cor1 = cores[tiposArr[0]] || "#888";
      const cor = cor1;
      const cur = parseIntVal(p.hp, 0);
      const mx = parseIntVal(p.hp_max, 1);
      const pct = mx > 0 ? Math.min(1, cur / mx) : 0;
      const bonus = getBonusTipoPokemon(p.tipo);
      const tipoBadges = tiposArr.map(t => `<span class="tipo-badge" style="background:${cores[t] || '#888'}">${escapeHtml(t)}</span>`).join(" ");
      const spriteIndex = getPokeSpriteIndex(p.nome);

      const acStr = p.ac != null && p.ac !== "" ? ` | AC ${p.ac}` : "";
      return `
        <div class="poke-card" style="border-left-color: ${cor}" data-poke-idx="${i}">
          <div class="poke-header">
            <div class="poke-header-left">
              ${spriteIndex != null ? `<img class="poke-sprite" src="${POKE_SPRITE_URL}/${spriteIndex}.png" alt="" />` : ""}
              <div>
                <span class="poke-slot">#${i + 1}</span>
                <span class="poke-nome">${escapeHtml(p.nome || "?")}</span>
                <div class="poke-meta">
                  Nv.${p.nivel} | SR ${p.sr}${acStr}
                  <span class="poke-tipos">${tipoBadges}</span>
                </div>
              </div>
            </div>
            <div class="poke-actions">
              <button type="button" data-roll-poke="${i}" title="Rolar teste" class="icon-btn">Rolar</button>
              <button type="button" data-edit-poke="${i}" title="Editar" class="icon-btn">Editar</button>
              <button type="button" data-del-poke="${i}" title="Remover" class="icon-btn icon-del">Remover</button>
            </div>
          </div>
          <div class="poke-lealdade">${leal.emoji || ""} ${leal.nome || "Neutro"}</div>
          <div class="poke-hp-line"><span class="hp-heart"></span> ${cur}/${mx} HP ${bonus ? `(+${bonus})` : ""}</div>
          <div class="hp-bar"><div class="hp-fill" style="width:${pct * 100}%;background:${cor}"></div></div>
          <div class="poke-hp-ctrl">
            <button type="button" class="btn-sm btn-hp" data-poke-hp="${i}" data-delta="-1">−</button>
            <button type="button" class="btn-sm btn-hp" data-poke-hp="${i}" data-delta="1">+</button>
            <button type="button" class="btn-curar" data-poke-cura="${i}">Curar</button>
          </div>
        </div>
      `;
    }).join("");

    list.querySelectorAll("[data-roll-poke]").forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.dataset.rollPoke, 10);
        const p = stats.pokemons[idx];
        withRollAnimation(() => {
          const bonus = getBonusTipoPokemon(p.tipo);
          const d20 = rollDice(1, 20);
          const total = d20 + bonus;
          let msg = `🎲 ${p.nome}: ${d20}+${bonus} = ${total}`;
          if (d20 === 20) msg = `🎯 ${p.nome}: CRÍTICO!`;
          else if (d20 === 1) msg = `💥 ${p.nome}: FALHA!`;
          return {
            mainNum: d20,
            msg,
            tipo: `Pokémon ${p.nome}`,
            onComplete: () => {
              addHistorico(`Pokémon ${p.nome}`, msg);
              showToast(msg, true, true);
              renderHistorico();
            }
          };
        });
      };
    });
    list.querySelectorAll("[data-edit-poke]").forEach(btn => {
      btn.onclick = () => openEditPoke(parseInt(btn.dataset.editPoke, 10));
    });
    list.querySelectorAll("[data-del-poke]").forEach(btn => {
      btn.onclick = () => {
        stats.pokemons.splice(parseInt(btn.dataset.delPoke, 10), 1);
        renderPokemons();
        atualizar();
      };
    });
    list.querySelectorAll("[data-poke-hp]").forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.dataset.pokeHp, 10);
        const delta = parseInt(btn.dataset.delta, 10);
        const pk = stats.pokemons[idx];
        const cur = parseIntVal(pk.hp, 0);
        const mx = parseIntVal(pk.hp_max, 1);
        pk.hp = String(Math.max(0, Math.min(cur + delta, mx)));
        renderPokemons();
        atualizar();
      };
    });
    list.querySelectorAll("[data-poke-cura]").forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.dataset.pokeCura, 10);
        stats.pokemons[idx].hp = stats.pokemons[idx].hp_max;
        renderPokemons();
        atualizar();
      };
    });
  }

  function openEditPoke(idx) {
    editingPokeIndex = idx;
    const p = stats.pokemons[idx];
    const tiposArr = getTiposArray(p.tipo);
    $("edit-poke-nome").value = p.nome || "";
    $("edit-poke-nivel").value = p.nivel || "1";
    $("edit-poke-hp_max").value = p.hp_max || "20";
    $("edit-poke-ac").value = p.ac != null && p.ac !== "" ? String(p.ac) : "";
    // SR select
    const srSel = $("edit-poke-sr");
    if (srSel) {
      const srVal = parseFloat(p.sr) || 1;
      let opts = SR_OPCOES.map(s => `<option value="${s}">${s}</option>`);
      if (!SR_OPCOES.includes(srVal)) opts.push(`<option value="${srVal}">${srVal}</option>`);
      srSel.innerHTML = opts.join("");
      srSel.value = String(srVal);
    }
    // Tipo primário / secundário
    const tiposOpt = ["Nenhum", ...(C.TIPOS_POKEMON || [])];
    $("edit-poke-tipo").innerHTML = tiposOpt.map(t => `<option value="${t}">${t}</option>`).join("");
    $("edit-poke-tipo2").innerHTML = tiposOpt.map(t => `<option value="${t}">${t}</option>`).join("");
    $("edit-poke-tipo").value = tiposArr[0] || "Normal";
    $("edit-poke-tipo2").value = tiposArr[1] || "Nenhum";
    const nats = C.NATUREZAS_POKEMON || {};
    $("edit-poke-natureza").innerHTML = Object.keys(nats).map(n => `<option value="${n}">${n}</option>`).join("");
    $("edit-poke-natureza").value = p.natureza || "Nenhuma";
    const leal = C.LEALDADE_NIVEIS || {};
    const lealEntries = Object.entries(leal).sort((a, b) => parseInt(a[0], 10) - parseInt(b[0], 10));
    $("edit-poke-lealdade").innerHTML = lealEntries.map(([k, v]) => `<option value="${k}">${v.emoji || ""} ${v.nome || k}</option>`).join("");
    $("edit-poke-lealdade").value = String(p.lealdade || 0);
    $("edit-poke-habilidade").value = p.habilidade || "";
    // Preencher AC do Pokédex se vazio
    const acEl = $("edit-poke-ac");
    if (!acEl.value && p.nome) {
      loadPokedex().then(pokedex => {
        const pd = pokedex[p.nome];
        if (pd && pd.ac != null) acEl.value = String(pd.ac);
      });
    }
    // Carregar habilidades e movimentos do Pokédex
    populateEditPokePokedexData(p.nome);
    $("modal-editar-poke").classList.remove("hidden");
  }

  function populateEditPokePokedexData(nome) {
    const abilitiesWrap = $("edit-poke-habilidades-pokedex");
    const movesWrap = $("edit-poke-moves-wrap");
    const movesEl = $("edit-poke-moves");
    if (!abilitiesWrap || !movesWrap || !movesEl) return;
    abilitiesWrap.classList.add("hidden");
    abilitiesWrap.innerHTML = "";
    movesWrap.classList.add("hidden");
    movesEl.innerHTML = "";
    loadPokedex().then(pokedex => {
      const pd = pokedex[nome];
      if (!pd) return;
      // Habilidades (clique para inserir no campo)
      const habText = $("edit-poke-habilidade");
      const abs = (pd.abilities || []).concat(pd.ability_hidden || []);
      if (abs.length) {
        abilitiesWrap.innerHTML = "<span class='label-chip'>Sugestões:</span> " +
          abs.map(a => `<button type="button" class="chip-ability" data-name="${escapeHtml(a.name)}" title="${escapeHtml((a.desc || "").slice(0,80))}">${escapeHtml(a.name)}</button>`).join(" ");
        abilitiesWrap.classList.remove("hidden");
        abilitiesWrap.querySelectorAll(".chip-ability").forEach(btn => {
          btn.onclick = () => {
            const cur = habText.value.trim();
            const add = btn.dataset.name;
            habText.value = cur ? cur + ", " + add : add;
          };
        });
      }
      // Movimentos
      const parts = [];
      if (pd.moves_starting && pd.moves_starting.length)
        parts.push("<strong>Iniciais:</strong> " + pd.moves_starting.join(", "));
      if (pd.moves_by_level && Object.keys(pd.moves_by_level).length) {
        const byLvl = Object.entries(pd.moves_by_level).sort((a,b) => Number(a[0]) - Number(b[0]));
        parts.push("<strong>Por nível:</strong> " + byLvl.map(([lvl, moves]) => `Nv.${lvl}: ${moves.join(", ")}`).join(" · "));
      }
      if (pd.moves_tm && pd.moves_tm.length)
        parts.push("<strong>TM:</strong> " + pd.moves_tm.slice(0, 24).join(", ") + (pd.moves_tm.length > 24 ? "..." : ""));
      if (pd.moves_egg && pd.moves_egg.length)
        parts.push("<strong>Egg:</strong> " + pd.moves_egg.slice(0, 12).join(", ") + (pd.moves_egg.length > 12 ? "..." : ""));
      if (parts.length) {
        movesEl.innerHTML = parts.map(p => `<div class="moves-row">${p}</div>`).join("");
        movesWrap.classList.remove("hidden");
      }
    });
  }

  function saveEditPoke() {
    if (editingPokeIndex < 0) return;
    const p = stats.pokemons[editingPokeIndex];
    const t1 = $("edit-poke-tipo")?.value || "Normal";
    const t2 = $("edit-poke-tipo2")?.value || "Nenhum";
    p.nome = $("edit-poke-nome").value?.trim() || p.nome;
    p.nivel = $("edit-poke-nivel").value || "1";
    p.sr = $("edit-poke-sr")?.value ?? p.sr;
    const acVal = $("edit-poke-ac")?.value?.trim();
    if (acVal) p.ac = acVal;
    else delete p.ac;
    p.hp_max = $("edit-poke-hp_max").value || "20";
    p.tipo = t2 && t2 !== "Nenhum" ? t1 + "/" + t2 : t1;
    p.natureza = $("edit-poke-natureza").value || "Nenhuma";
    p.lealdade = parseIntVal($("edit-poke-lealdade").value, 0);
    p.habilidade = $("edit-poke-habilidade").value || "";
    $("modal-editar-poke").classList.add("hidden");
    editingPokeIndex = -1;
    renderPokemons();
    atualizar();
  }

  async function loadPokedex() {
    if (pokedexCache) return pokedexCache;
    try {
      const res = await fetch("/api/pokedex");
      const json = await res.json();
      if (json.ok && json.pokedex) {
        pokedexCache = json.pokedex;
        return pokedexCache;
      }
    } catch (e) { /* ignora */ }
    return {};
  }

  function showPokedexSuggestions(query) {
    const ul = $("pokedex-suggestions");
    const inp = $("novo-poke-nome");
    if (!ul || !inp) return;
    const q = (query || inp.value || "").trim().toLowerCase();
    if (!q || q.length < 2) {
      ul.classList.add("hidden");
      ul.innerHTML = "";
      return;
    }
    const pokedex = pokedexCache || {};
    const matches = Object.entries(pokedex)
      .filter(([nome]) => nome.toLowerCase().includes(q))
      .slice(0, 12);
    if (matches.length === 0) {
      ul.classList.add("hidden");
      ul.innerHTML = "";
      return;
    }
    ul.innerHTML = matches.map(([nome, dados]) => {
      const tipos = (dados.tipo || []).join("/");
      const hp = dados.hp != null ? dados.hp : "";
      const ac = dados.ac != null ? dados.ac : "";
      const extra = [ac ? `AC ${ac}` : "", hp ? `HP ${hp}` : ""].filter(Boolean).join(" | ");
      const idx = dados.index;
      const img = idx != null ? `<img class="pokedex-suggest-sprite" src="${POKE_SPRITE_URL}/${idx}.png" alt="" />` : "";
      return `<li data-nome="${escapeHtml(nome)}" data-sr="${dados.sr}" data-tipo="${escapeHtml(tipos)}" data-hp="${hp}" data-ac="${ac}">${img}<span>${escapeHtml(nome)} — SR ${dados.sr} (${escapeHtml(tipos)})${extra ? " · " + extra : ""}</span></li>`;
    }).join("");
    ul.classList.remove("hidden");
    ul.querySelectorAll("li").forEach(li => {
      li.onclick = () => {
        const nome = li.dataset.nome;
        const sr = li.dataset.sr || "1";
        const tipoStr = li.dataset.tipo || "Normal";
        const hpBase = li.dataset.hp ? String(li.dataset.hp) : "20";
        const acBase = li.dataset.ac ? String(li.dataset.ac) : "";
        addPokeFromPokedex(nome, sr, tipoStr, hpBase, acBase);
        inp.value = "";
        ul.classList.add("hidden");
        ul.innerHTML = "";
      };
    });
  }

  function addPokeFromPokedex(nome, sr, tipoStr, hpBase, acBase) {
    stats.pokemons = stats.pokemons || [];
    if (stats.pokemons.length >= MAX_EQUIPE) {
      showToast("Equipe cheia (máx " + MAX_EQUIPE + ")", false);
      return;
    }
    const tipo = (tipoStr || "Normal").replace("/", "/");
    const hpMax = hpBase || "20";
    const pk = { nome, hp: hpMax, hp_max: hpMax, tipo, natureza: "Nenhuma", habilidade: "", nivel: "1", sr: String(sr), lealdade: 0 };
    if (acBase) pk.ac = acBase;
    stats.pokemons.push(pk);
    renderPokemons();
    atualizar();
    saveToStorage();
    showToast(nome + " adicionado", true);
  }

  async function addPoke() {
    const nomeRaw = ($("novo-poke-nome").value || "").trim();
    if (!nomeRaw) return;
    stats.pokemons = stats.pokemons || [];
    if (stats.pokemons.length >= MAX_EQUIPE) {
      showToast("Equipe cheia (máx " + MAX_EQUIPE + ")", false);
      return;
    }
    let tipo = "Normal", sr = "1";
    const pokedex = await loadPokedex();
    const entry = Object.entries(pokedex).find(([k]) => k.toLowerCase() === nomeRaw.toLowerCase());
    let hpMax = "20";
    let acVal = "";
    if (entry) {
      const p = entry[1];
      tipo = (p.tipo && p.tipo.length) ? p.tipo.join("/") : "Normal";
      if (p.sr != null) sr = String(p.sr);
      if (p.hp != null) hpMax = String(p.hp);
      if (p.ac != null) acVal = String(p.ac);
    }
    const nome = nomeRaw.charAt(0).toUpperCase() + nomeRaw.slice(1).toLowerCase();
    const pk = { nome, hp: hpMax, hp_max: hpMax, tipo, natureza: "Nenhuma", habilidade: "", nivel: "1", sr, lealdade: 0 };
    if (acVal) pk.ac = acVal;
    stats.pokemons.push(pk);
    $("novo-poke-nome").value = "";
    $("pokedex-suggestions")?.classList.add("hidden");
    renderPokemons();
    atualizar();
    saveToStorage();
    showToast(nome + " adicionado", true);
  }

  function saveToStorage() {
    try {
      localStorage.setItem("ficha_rpg_pokemon", JSON.stringify(stats));
    } catch (e) {}
  }

  function loadFromStorage() {
    try {
      const s = localStorage.getItem("ficha_rpg_pokemon");
      if (s) return JSON.parse(s);
    } catch (e) {}
    return null;
  }

  function getOrCreateUserId() {
    let id = localStorage.getItem("ficha_user_id");
    if (!id) {
      id = "u" + Math.random().toString(36).slice(2) + Date.now().toString(36);
      localStorage.setItem("ficha_user_id", id);
    }
    return id;
  }

  function exportFicha() {
    syncStatsFromUI();
    const data = { ...stats };
    delete data._versao;
    const blob = new Blob([JSON.stringify(data, null, 4)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `ficha_${(stats.nome || "treinador").replace(/\s/g, "_")}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
    showToast("Ficha exportada!");
  }

  async function importFicha() {
    const inp = $("input-import");
    inp.onchange = async () => {
      const f = inp.files[0];
      if (!f) return;
      try {
        const txt = await f.text();
        const dados = JSON.parse(txt);
        const res = await fetch("/api/import", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(dados)
        });
        const json = await res.json();
        if (!json.ok) throw new Error(json.erro || "Erro ao importar");
        stats = { ...getStatsDefault(), ...json.dados };
        applyStatsToUI();
        renderAtributos();
        renderSaves();
        renderPericias();
        renderTalentos();
        renderPokemons();
        populateConstants();
        atualizar();
        saveToStorage();
        fetch("/api/save_local", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ...stats, _user_id: getOrCreateUserId() })
        }).catch(() => {});
        showToast("Ficha importada com sucesso!");
      } catch (err) {
        showToast(err.message || "Erro ao importar", false);
      }
      inp.value = "";
    };
    inp.click();
  }

  function applyStatsToUI() {
    $("nome").value = stats.nome || "";
    $("nivel").value = stats.nivel || "1";
    $("hp_atual").value = stats.hp_atual || "10";
    $("hp_max").value = stats.hp_max || "10";
    $("deslocamento").value = stats.deslocamento || "9m";
    $("pokedollars").value = stats.pokedollars || "0";
    $("pokebolas").value = stats.pokebolas || "";
    $("itens_chave").value = stats.itens_chave || "";
    $("consumiveis").value = stats.consumiveis || "";
  }

  async function init() {
    loadPokedex().then(() => renderPokemons()); // Sprites da equipe quando pokedex carregar
    const res = await fetch("/api/constants");
    C = await res.json();

    function renderRegras() {
      $("regras-resumo").innerHTML = markdownToHtml(C.REGRAS_RESUMO || "");
      $("regras-texto").innerHTML = markdownToHtml(C.REGRAS_TEXTO || "");
    }
    function highlightInElement(el, term) {
      if (!el || !term || term.length < 2) return;
      const q = term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
      const nodes = [];
      let n;
      while ((n = walker.nextNode())) nodes.push(n);
      nodes.forEach(node => {
        const text = node.textContent;
        if (!text.toLowerCase().includes(term.toLowerCase())) return;
        const parent = node.parentNode;
        if (parent.tagName === "MARK" || parent.tagName === "SCRIPT" || parent.tagName === "STYLE") return;
        const re = new RegExp("(" + q + ")", "gi");
        const frag = document.createDocumentFragment();
        let lastIdx = 0, m;
        while ((m = re.exec(text)) !== null) {
          frag.appendChild(document.createTextNode(text.slice(lastIdx, m.index)));
          const mark = document.createElement("mark");
          mark.className = "search-hit";
          mark.textContent = m[1];
          frag.appendChild(mark);
          lastIdx = m.index + m[1].length;
        }
        frag.appendChild(document.createTextNode(text.slice(lastIdx)));
        parent.replaceChild(frag, node);
      });
    }
    renderRegras();
    let searchCurrentIdx = 0;
    let searchHits = [];

    function updateSearchUI() {
      const nav = $("regras-search-nav");
      const countEl = $("regras-search-count");
      const prevBtn = $("regras-search-prev");
      const nextBtn = $("regras-search-next");
      if (searchHits.length === 0) {
        nav.classList.add("hidden");
        return;
      }
      nav.classList.remove("hidden");
      countEl.textContent = searchHits.length === 1 ? "1 resultado" : `${searchCurrentIdx + 1} de ${searchHits.length}`;
      if (prevBtn) prevBtn.disabled = searchHits.length <= 1;
      if (nextBtn) nextBtn.disabled = searchHits.length <= 1;
      searchHits.forEach((el, i) => el.classList.toggle("search-hit-current", i === searchCurrentIdx));
      searchHits[searchCurrentIdx].scrollIntoView({ behavior: "smooth", block: "center" });
    }

    function doSearch(term) {
      renderRegras();
      searchHits = [];
      searchCurrentIdx = 0;
      if (term.length >= 2) {
        highlightInElement($("regras-resumo"), term);
        highlightInElement($("regras-texto"), term);
        searchHits = Array.from(document.querySelectorAll(".search-hit"));
      }
      updateSearchUI();
    }

    function updateCalcCaptura() {
      const nivelEl = $("calc-nivel");
      const srEl = $("calc-sr");
      const hpEl = $("calc-hp-atual");
      const pokebolaEl = $("calc-pokebola");
      const cdEl = $("calc-cd-val");
      const bonusEl = $("calc-bonus-val");
      if (!nivelEl || !srEl || !hpEl || !pokebolaEl || !cdEl) return;
      const nivel = parseIntVal(nivelEl.value, 1);
      const sr = parseFloat(srEl.value) || 0;
      const hpAtual = parseIntVal(hpEl.value, 0);
      let bonusPokebola = parseIntVal(pokebolaEl.value, 0);
      const opt = pokebolaEl.selectedOptions[0];
      const cond = opt?.dataset?.cond;
      if (cond === "nv5" && nivel > 5) bonusPokebola = 0;
      const srBase = Math.floor(sr);
      const hpTermo = Math.floor(hpAtual / 10);
      const cd = Math.max(1, 10 + srBase + nivel + hpTermo);
      cdEl.textContent = String(cd);
      if (bonusEl) bonusEl.textContent = bonusPokebola >= 999 ? "Automático" : "+" + bonusPokebola;
    }

    ["calc-nivel","calc-sr","calc-hp-atual","calc-pokebola"].forEach(id => {
      const el = $(id);
      if (el) el.oninput = el.onchange = () => updateCalcCaptura();
    });
    updateCalcCaptura();

    const regrasSearch = $("regras-search");
    if (regrasSearch) {
      regrasSearch.oninput = () => doSearch(regrasSearch.value.trim());
      $("regras-search-prev")?.addEventListener("click", () => {
        if (searchHits.length > 1) {
          searchCurrentIdx = (searchCurrentIdx - 1 + searchHits.length) % searchHits.length;
          updateSearchUI();
        }
      });
      $("regras-search-next")?.addEventListener("click", () => {
        if (searchHits.length > 1) {
          searchCurrentIdx = (searchCurrentIdx + 1) % searchHits.length;
          updateSearchUI();
        }
      });
    }

    const userId = getOrCreateUserId();
    try {
      const loadRes = await fetch("/api/load_local?user_id=" + encodeURIComponent(userId));
      const loadJson = await loadRes.json();
      if (loadJson.ok && loadJson.dados) {
        stats = { ...getStatsDefault(), ...loadJson.dados };
      } else {
        const stored = loadFromStorage();
        stats = stored ? { ...getStatsDefault(), ...stored } : getStatsDefault();
      }
    } catch (e) {
      const stored = loadFromStorage();
      stats = stored ? { ...getStatsDefault(), ...stored } : getStatsDefault();
    }

    applyStatsToUI();
    renderTabs();
    populateConstants();
    renderAtributos();
    renderSaves();
    renderPericias();
    renderTalentos();
    initTalentosAdd();
    renderPokemons();

    $("btn-export").onclick = exportFicha;
    $("btn-import").onclick = importFicha;
    $("roll-inic").onclick = rollInic;
    $("roll-dinheiro").onclick = rollDinheiro;
    $("roller-btn").onclick = rollDadoGen;

    $("hp-minus").onclick = () => {
      const cur = parseIntVal($("hp_atual").value, 0);
      const mx = parseIntVal($("hp_max").value, 1);
      $("hp_atual").value = Math.max(0, cur - 1);
      atualizar();
    };
    $("hp-plus").onclick = () => {
      const cur = parseIntVal($("hp_atual").value, 0);
      const mx = parseIntVal($("hp_max").value, 1);
      $("hp_atual").value = Math.min(mx, cur + 1);
      atualizar();
    };

    ["nome","nivel","hp_atual","hp_max","deslocamento","pokedollars","pokebolas","itens_chave","consumiveis"].forEach(id => {
      const el = $(id);
      if (el) el.oninput = el.onchange = () => atualizar();
    });

    $("add-poke").onclick = addPoke;
    const novoPokeInp = $("novo-poke-nome");
    if (novoPokeInp) {
      novoPokeInp.onfocus = () => { loadPokedex().then(() => showPokedexSuggestions()); };
      novoPokeInp.oninput = () => showPokedexSuggestions();
      novoPokeInp.onblur = () => setTimeout(() => $("pokedex-suggestions")?.classList.add("hidden"), 200);
      novoPokeInp.onkeydown = (e) => {
        if (e.key === "Enter") {
          const ul = $("pokedex-suggestions");
          if (ul && !ul.classList.contains("hidden")) {
            const first = ul.querySelector("li");
            if (first) { first.click(); e.preventDefault(); return; }
          }
          addPoke();
          e.preventDefault();
        }
      };
    }
    $("edit-poke-cancel").onclick = () => { $("modal-editar-poke").classList.add("hidden"); editingPokeIndex = -1; };
    $("edit-poke-save").onclick = saveEditPoke;

    setInterval(() => {
      syncStatsFromUI();
      const payload = { ...stats, _user_id: getOrCreateUserId() };
      fetch("/api/save_local", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }).catch(() => {});
    }, 10000);

    atualizar();

    if (sessaoCodigo && sessaoJogador) {
      fetch("/api/mestre/session/" + sessaoCodigo + "/join", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jogador: sessaoJogador || stats.nome || "Jogador", ficha: stats })
      }).catch(() => {});
    }
  }

  (function initSessao() {
    sessaoCodigo = localStorage.getItem("ficha_sessao_codigo") || null;
    sessaoJogador = localStorage.getItem("ficha_sessao_jogador") || null;
    const modal = $("modal-sessao");
    const btnSessao = $("btn-sessao");
    const btnSessaoSair = $("btn-sessao-sair");
    const btnEntrar = $("sessao-entrar");
    const btnSair = $("sessao-sair");
    const btnCancelar = $("sessao-cancelar");

    function fecharModal() {
      modal?.classList.add("hidden");
    }

    function updateSessaoUI() {
      if (sessaoCodigo) {
        if (btnSessao) btnSessao.textContent = "Sessão ✓";
        btnSessaoSair?.classList.remove("hidden");
      } else {
        if (btnSessao) btnSessao.textContent = "Sessão";
        btnSessaoSair?.classList.add("hidden");
      }
    }
    function sairSessao() {
      sessaoCodigo = null;
      sessaoJogador = null;
      localStorage.removeItem("ficha_sessao_codigo");
      localStorage.removeItem("ficha_sessao_jogador");
      modal?.classList.add("hidden");
      updateSessaoUI();
    }

    if (!modal || !btnSessao) return;
    btnSessao.onclick = () => {
      if (sessaoCodigo) {
        $("sessao-codigo").value = sessaoCodigo;
        $("sessao-jogador").value = sessaoJogador || stats.nome || "";
        btnEntrar?.classList.add("hidden");
        btnSair?.classList.remove("hidden");
      } else {
        $("sessao-codigo").value = "";
        $("sessao-jogador").value = stats.nome || "";
        btnEntrar?.classList.remove("hidden");
        btnSair?.classList.add("hidden");
      }
      modal.classList.remove("hidden");
    };
    btnEntrar?.addEventListener("click", async () => {
      const cod = ($("sessao-codigo")?.value || "").trim().toUpperCase();
      const jog = ($("sessao-jogador")?.value || stats.nome || "Jogador").trim();
      if (!cod || cod.length < 4) return;
      sessaoCodigo = cod;
      sessaoJogador = jog;
      localStorage.setItem("ficha_sessao_codigo", cod);
      localStorage.setItem("ficha_sessao_jogador", jog);
      try {
        await fetch("/api/mestre/session/" + cod + "/join", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ jogador: jog, ficha: stats })
        });
      } catch (e) { /* ignora */ }
      modal.classList.add("hidden");
      updateSessaoUI();
    });
    btnCancelar?.addEventListener("click", fecharModal);
    btnSair?.addEventListener("click", sairSessao);
    btnSessaoSair?.addEventListener("click", sairSessao);
    updateSessaoUI();
  })();

  (function initTheme() {
    const VALID_THEMES = ["bulbasaur","pikachu","charmander","squirtle","gastly","mew","umbreon","gengar","pokebola"];
    const THEME_SPRITE = { bulbasaur:1, pikachu:25, charmander:4, squirtle:7, gastly:92, mew:151, umbreon:197, gengar:94, pokebola:0 };
    const saved = localStorage.getItem("ficha_pokemon_theme");
    const theme = VALID_THEMES.includes(saved) ? saved : "bulbasaur";
    document.body.setAttribute("data-theme", theme);
    const sel = $("theme-select");
    const sprEl = $("theme-sprite");
    function updateThemeSprite(t) {
      if (!sprEl) return;
      const idx = THEME_SPRITE[t];
      if (idx && idx > 0) {
        sprEl.src = `${POKE_SPRITE_URL}/${idx}.png`;
        sprEl.style.display = "";
      } else {
        sprEl.src = "";
        sprEl.style.display = "none";
      }
    }
    if (sel) {
      sel.value = theme;
      updateThemeSprite(theme);
      sel.onchange = () => {
        const t = sel.value;
        if (VALID_THEMES.includes(t)) {
          document.body.setAttribute("data-theme", t);
          localStorage.setItem("ficha_pokemon_theme", t);
          updateThemeSprite(t);
        }
      };
    }
  })();

  init();
})();
