"""
Ficha RPG Pokémon - Versão Web
Flask app com suporte total às fichas salvas (import/export compatível).
Versão Mestre: sessões, rolagens em tempo real, ferramentas de mesa.
"""
import json
import os
import random
import string
from pathlib import Path
from collections import deque

from flask import Flask, render_template, request, jsonify

# Importar do projeto principal para reutilizar lógica
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from constants import get_stats_default
from save_utils import migrar_ficha

app = Flask(__name__, static_folder="static", template_folder="templates")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ARQUIVO_SAVE = PROJECT_ROOT / "ficha_save.json"

# Sessões do Mestre (em memória)
SESSOES = {}
ROLLS_CACHE = {}
MAX_ROLLS_PER_SESSION = 100


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/import", methods=["POST"])
def api_import():
    """Recebe JSON da ficha, aplica migração e retorna dados prontos."""
    try:
        dados = request.get_json()
        if not isinstance(dados, dict):
            return jsonify({"ok": False, "erro": "Formato inválido"}), 400
        if "nome" not in dados and "pokemons" not in dados:
            return jsonify({"ok": False, "erro": "Parece não ser uma ficha do RPG Pokémon"}), 400
        migrado = migrar_ficha(dados)
        return jsonify({"ok": True, "dados": migrado})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 500


@app.route("/api/save_local", methods=["POST"])
def api_save_local():
    """Salva no ficha_save.json (quando rodando localmente)."""
    try:
        dados = request.get_json()
        if not isinstance(dados, dict):
            return jsonify({"ok": False, "erro": "Formato inválido"}), 400
        dados_copy = {k: v for k, v in dados.items() if not str(k).startswith("_")}
        dados_copy["_versao"] = 2
        with open(ARQUIVO_SAVE, "w", encoding="utf-8") as f:
            json.dump(dados_copy, f, indent=4, ensure_ascii=False)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 500


@app.route("/api/load_local")
def api_load_local():
    """Carrega ficha_save.json se existir (rodando localmente)."""
    if not ARQUIVO_SAVE.exists():
        return jsonify({"ok": True, "dados": get_stats_default()})
    try:
        with open(ARQUIVO_SAVE, "r", encoding="utf-8") as f:
            dados = json.load(f)
        migrado = migrar_ficha(dados)
        return jsonify({"ok": True, "dados": migrado})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 500


@app.route("/api/constants")
def api_constants():
    """Retorna todas as constantes do jogo para o frontend."""
    from constants import (
        POINT_BUY_TOTAL, POINT_BUY_MIN, POINT_BUY_MAX,
        ESPECIALIZACOES, REGIOES_ORIGEM, ORIGENS_JORNADA,
        LISTA_TMS, CLASSES_TREINADOR, TALENTOS, PACOTES_AVENTURA,
        NATUREZAS_POKEMON, TIPOS_POKEMON, LEALDADE_NIVEIS,
        REGRAS_TEXTO, REGRAS_RESUMO, CORES_TIPO_POKEMON,
    )
    return jsonify({
        "POINT_BUY_TOTAL": POINT_BUY_TOTAL,
        "POINT_BUY_MIN": POINT_BUY_MIN,
        "POINT_BUY_MAX": POINT_BUY_MAX,
        "ESPECIALIZACOES": ESPECIALIZACOES,
        "REGIOES_ORIGEM": REGIOES_ORIGEM,
        "ORIGENS_JORNADA": ORIGENS_JORNADA,
        "LISTA_TMS": LISTA_TMS,
        "CLASSES_TREINADOR": CLASSES_TREINADOR,
        "TALENTOS": TALENTOS,
        "PACOTES_AVENTURA": PACOTES_AVENTURA,
        "NATUREZAS_POKEMON": NATUREZAS_POKEMON,
        "TIPOS_POKEMON": TIPOS_POKEMON,
        "LEALDADE_NIVEIS": {str(k): v for k, v in LEALDADE_NIVEIS.items()},
        "REGRAS_TEXTO": REGRAS_TEXTO,
        "REGRAS_RESUMO": REGRAS_RESUMO,
        "CORES_TIPO_POKEMON": CORES_TIPO_POKEMON,
    })


# ========== MESTRE ==========
def _gera_codigo():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


@app.route("/mestre")
def mestre_page():
    return render_template("mestre.html")


@app.route("/api/mestre/session/create", methods=["POST"])
def api_mestre_session_create():
    """Cria uma nova sessão. Retorna session_id e código."""
    codigo = _gera_codigo()
    while codigo in SESSOES:
        codigo = _gera_codigo()
    SESSOES[codigo] = {"created_at": None, "ativo": True}
    ROLLS_CACHE[codigo] = deque(maxlen=MAX_ROLLS_PER_SESSION)
    return jsonify({"ok": True, "codigo": codigo})


@app.route("/api/mestre/session/<codigo>/roll", methods=["POST"])
def api_mestre_session_roll(codigo):
    """Player envia uma rolagem para a sessão."""
    codigo = codigo.upper().strip()
    if codigo not in SESSOES:
        return jsonify({"ok": False, "erro": "Sessão não encontrada"}), 404
    dados = request.get_json()
    if not isinstance(dados, dict):
        return jsonify({"ok": False, "erro": "Dados inválidos"}), 400
    jogador = dados.get("jogador", "Desconhecido")
    tipo = dados.get("tipo", "Rolagem")
    msg = dados.get("msg", "")
    main_num = dados.get("mainNum", 0)
    ts = dados.get("ts", "")
    entrada = {
        "jogador": str(jogador)[:50],
        "tipo": str(tipo)[:80],
        "msg": str(msg)[:200],
        "mainNum": int(main_num) if isinstance(main_num, (int, float)) else main_num,
        "ts": str(ts)[:30],
    }
    ROLLS_CACHE[codigo].append(entrada)
    return jsonify({"ok": True})


@app.route("/api/mestre/session/<codigo>/rolls")
def api_mestre_session_rolls(codigo):
    """Mestre busca rolagens da sessão (polling)."""
    codigo = codigo.upper().strip()
    if codigo not in SESSOES:
        return jsonify({"ok": False, "erro": "Sessão não encontrada"}), 404
    desde = request.args.get("desde", "0")
    try:
        desde_idx = int(desde)
    except ValueError:
        desde_idx = 0
    rolls = list(ROLLS_CACHE[codigo])
    return jsonify({"ok": True, "rolls": rolls[desde_idx:], "total": len(rolls)})


CLIMA_VERAO = [
    (1, 25, "Sol Forte, Calmo", "Grama, Terra, Fogo"),
    (26, 35, "Sol Forte, Ventoso", "Grama, Terra, Fogo, Voador, Dragão, Psíquico"),
    (36, 65, "Nublado, Calmo", "Normal, Pedra, Fada, Lutador, Venenoso"),
    (66, 75, "Nublado, Ventoso", "Normal, Pedra, Fada, Lutador, Venenoso, Voador, Dragão, Psíquico"),
    (76, 80, "Nebuloso", "Sombrio, Fantasma"),
    (81, 90, "Garoa Leve", "Água, Elétrico, Inseto"),
    (91, 99, "Chuva Forte", "Água, Elétrico, Inseto"),
    (100, 100, "Tempestade Perigosa", "Água, Elétrico, Inseto"),
]
CLIMA_INVERNO = [
    (1, 15, "Sol Forte, Calmo", "Grama, Terra, Fogo"),
    (16, 25, "Sol Forte, Ventoso", "Grama, Terra, Fogo, Voador, Dragão, Psíquico"),
    (26, 40, "Nublado, Calmo", "Normal, Pedra, Fada, Lutador, Venenoso"),
    (41, 50, "Nublado, Ventoso", "Normal, Pedra, Fada, Lutador, Venenoso, Voador, Dragão, Psíquico"),
    (51, 60, "Nebuloso", "Sombrio, Fantasma"),
    (61, 70, "Garoa Leve", "Água, Elétrico, Inseto"),
    (71, 80, "Chuva Forte", "Água, Elétrico, Inseto"),
    (81, 90, "Neve Leve", "Gelo, Aço"),
    (91, 99, "Nevasca Forte", "Gelo, Aço"),
    (100, 100, "Tempestade de Neve", "Gelo, Aço"),
]


@app.route("/api/mestre/weather")
def api_mestre_weather():
    """Rola d100 para clima (primavera/verão ou outono/inverno)."""
    estacao = request.args.get("estacao", "verao")
    d100 = random.randint(1, 100)
    climas = CLIMA_VERAO if estacao in ("verao", "primavera", "1", "2") else CLIMA_INVERNO
    clima_nome, clima_moves = "?", ""
    for low, high, nome, moves in climas:
        if low <= d100 <= high:
            clima_nome, clima_moves = nome, moves
            break
    return jsonify({"ok": True, "d100": d100, "clima": clima_nome, "moves": clima_moves})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
