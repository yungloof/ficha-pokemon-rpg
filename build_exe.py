"""
Script para gerar o executavel da Ficha de Personagem Pokemon RPG
"""
import os
import subprocess
import sys

def build():
    """Gera o executavel usando flet pack (metodo oficial)"""
    print("Gerando executavel da Ficha de Personagem...")
    print("Usando flet pack (metodo oficial do Flet)...\n")

    # Encontrar o executavel flet no venv
    venv_flet = os.path.join(".venv", "Scripts", "flet.exe")
    if os.path.exists(venv_flet):
        flet_cmd = venv_flet
    else:
        flet_cmd = "flet"

    # Comando flet pack (por padrao ja cria arquivo unico)
    cmd = [
        flet_cmd,
        "pack",
        "main.py",
        "--name=FichaPokemonRPG",
        "-y"  # Modo nao-interativo
    ]

    print(f"Executando: {' '.join(cmd)}")
    subprocess.check_call(cmd)

    print("\nExecutavel gerado com sucesso!")
    print("Localizacao: dist/FichaPokemonRPG.exe")
    print("\nInstrucoes:")
    print("  1. Envie o arquivo 'dist/FichaPokemonRPG.exe' para seus jogadores")
    print("  2. Cada jogador pode executar diretamente (sem instalacao)")
    print("  3. O arquivo 'character_data.json' sera criado automaticamente")

if __name__ == "__main__":
    build()
