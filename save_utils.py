"""
Utilitários de save/load para Ficha RPG Pokémon.
Exportar, importar, backup e migração de versões.
"""
import json
import os
import shutil
from datetime import datetime
from typing import Any, Tuple

from constants import (
    ARQUIVO_SAVE,
    ARQUIVO_BACKUP,
    VERSAO_SAVE,
    get_stats_default,
    CLASSES_TREINADOR,
)


def _migrar_pokemons(pokemons: list) -> list:
    """Migra formato antigo (lista de strings) para novo (lista de dicts)."""
    if not pokemons:
        return []
    if isinstance(pokemons[0], str):
        return [{"nome": p, "hp": "20", "hp_max": "20", "tipo": "Normal", "natureza": "Nenhuma",
                 "habilidade": "", "nivel": "1", "sr": "1", "lealdade": 0} for p in pokemons]
    resultado = []
    for p in pokemons:
        if isinstance(p, dict):
            padrao = {"nome": "?", "hp": "20", "hp_max": "20", "tipo": "Normal", "natureza": "Nenhuma",
                      "habilidade": "", "nivel": "1", "sr": "1", "lealdade": 0}
            padrao.update({k: v for k, v in p.items() if k in padrao or k in ("nome", "hp", "hp_max", "tipo", "natureza", "habilidade", "nivel", "sr", "lealdade")})
            resultado.append(padrao)
        else:
            resultado.append({"nome": str(p), "hp": "20", "hp_max": "20", "tipo": "Normal", "natureza": "Nenhuma",
                              "habilidade": "", "nivel": "1", "sr": "1", "lealdade": 0})
    return resultado


def _garantir_campos_stats(dados: dict) -> dict:
    """Garante que o save tenha todos os campos necessários."""
    padrao = get_stats_default()
    for k, v in padrao.items():
        if k not in dados:
            dados[k] = v
    if "pericias_proficientes" not in dados or not isinstance(dados["pericias_proficientes"], list):
        dados["pericias_proficientes"] = ["Adestrar Animais"]
    if "talentos" not in dados or not isinstance(dados["talentos"], list):
        dados["talentos"] = []
    if "pokemons" not in dados or not isinstance(dados["pokemons"], list):
        dados["pokemons"] = []
    dados["pokemons"] = _migrar_pokemons(dados["pokemons"])
    # Migração: origem de jornada - fichas antigas do executável usavam "origem" ou "origemJornada"
    for chave_antiga in ("origem", "origemJornada"):
        if chave_antiga in dados and dados[chave_antiga]:
            if not dados.get("origem_jornada"):
                dados["origem_jornada"] = dados[chave_antiga]
            break
    # Migração: classes antigas -> novas (livro Pokémon Mundo Perfeito)
    if dados.get("classe") and dados["classe"] not in CLASSES_TREINADOR:
        mapa_antigo = {"Criador": "Criador de Pokémon", "Ranger": "Patrulheiro", "Combatente": "Treinador Ás",
                       "Coordenador": "Versátil", "Pesquisador": "Pesquisador"}
        dados["classe"] = mapa_antigo.get(dados["classe"], "Nenhuma")
    dados["_versao"] = VERSAO_SAVE
    return dados


def criar_backup() -> str | None:
    """Cria backup do save atual. Retorna o caminho do backup ou None."""
    if not os.path.exists(ARQUIVO_SAVE):
        return None
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"ficha_save_backup_{timestamp}.json"
        shutil.copy2(ARQUIVO_SAVE, backup_path)
        return backup_path
    except OSError:
        return None


def carregar(arquivo: str | None = None) -> dict:
    """
    Carrega ficha do arquivo. Se arquivo é None, usa ARQUIVO_SAVE.
    Cria backup antes de sobrescrever (se carregar do arquivo padrão).
    Retorna dict com dados ou stats_default em caso de erro.
    """
    path = arquivo or ARQUIVO_SAVE
    padrao = get_stats_default()

    if not os.path.exists(path):
        return padrao.copy()

    try:
        with open(path, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        if path == ARQUIVO_SAVE:
            criar_backup()
        raise ValueError(f"Arquivo corrompido ou inacessível: {e}") from e

    dados = _garantir_campos_stats(dados)
    padrao.update(dados)
    return padrao


def salvar_em(dados: dict, path: str) -> None:
    """Salva dados em um arquivo específico."""
    dados_copy = {k: v for k, v in dados.items() if not k.startswith("_")}
    dados_copy["_versao"] = VERSAO_SAVE
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dados_copy, f, indent=4, ensure_ascii=False)


def salvar_local(dados: dict) -> None:
    """Salva dados no arquivo padrão (ficha_save.json). Cria backup do arquivo anterior."""
    if os.path.exists(ARQUIVO_SAVE):
        try:
            shutil.copy2(ARQUIVO_SAVE, ARQUIVO_BACKUP)
        except OSError:
            pass
    salvar_em(dados, ARQUIVO_SAVE)


def exportar(dados: dict, caminho_destino: str) -> None:
    """Exporta ficha para o caminho escolhido pelo usuário."""
    salvar_em(dados, caminho_destino)


def importar_de(caminho: str) -> dict:
    """
    Importa ficha de um arquivo JSON.
    Retorna dict com dados validados e migrados.
    """
    return carregar(caminho)


def migrar_ficha(dados: dict) -> dict:
    """Aplica migração a dados de ficha e retorna cópia pronta para uso."""
    return _garantir_campos_stats(dict(dados))


def validar_importacao(caminho: str) -> Tuple[bool, str]:
    """
    Valida se o arquivo é um save válido.
    Retorna (ok, mensagem).
    """
    if not os.path.exists(caminho):
        return False, "Arquivo não encontrado."
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except json.JSONDecodeError:
        return False, "Arquivo não é um JSON válido."
    except OSError:
        return False, "Não foi possível ler o arquivo."
    if not isinstance(dados, dict):
        return False, "Formato inválido: esperado um objeto JSON."
    if "nome" not in dados and "pokemons" not in dados:
        return False, "Parece não ser uma ficha do RPG Pokémon."
    return True, "OK"
