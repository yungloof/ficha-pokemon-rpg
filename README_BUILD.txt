=====================================
COMO GERAR O EXECUTÁVEL (.EXE)
=====================================

MÉTODO 1 - Fácil (Windows):
---------------------------
1. Dê duplo clique em "build.bat"
2. Aguarde a compilação terminar (~30-60 segundos)
3. O executável estará em: dist/FichaPokemonRPG.exe


MÉTODO 2 - Manual:
-----------------
1. Abra o terminal nesta pasta
2. Execute: python build_exe.py
3. O executável estará em: dist/FichaPokemonRPG.exe


MÉTODO 3 - Comando flet direto:
-------------------------------
1. Ative o venv: .venv\Scripts\activate
2. Instale PyInstaller no venv: pip install pyinstaller
3. Execute: flet pack main.py --name=FichaPokemonRPG -y
4. O executável estará em: dist/FichaPokemonRPG.exe


=====================================
DISTRIBUIÇÃO PARA JOGADORES
=====================================

ENVIE O ARQUIVO:
- dist/FichaPokemonRPG.exe

INSTRUÇÕES PARA OS JOGADORES:
1. Baixe o arquivo FichaPokemonRPG.exe
2. Execute diretamente (sem instalação necessária)
3. A ficha será criada automaticamente (ficha_save.json)
4. Todos os dados são salvos localmente
5. Use EXPORTAR para salvar uma cópia da ficha em qualquer pasta
6. Use IMPORTAR para restaurar uma ficha salva (em caso de perda de dados)


=====================================
OBSERVAÇÕES
=====================================

- O executável tem ~78 MB (inclui Python + Flet + todas as dependências)
- Funciona em Windows 10/11 (64-bit)
- Não requer instalação de Python ou qualquer outra dependência
- Cada jogador terá sua própria ficha (ficha_save.json)
- Backup automático: ficha_save.backup.json guarda a versão anterior ao salvar
- Antivírus podem alertar (normal para .exe gerados com PyInstaller)
- IMPORTANTE: O PyInstaller deve estar instalado no venv (.venv) para funcionar


=====================================
TROUBLESHOOTING
=====================================

Se aparecer "No module named 'PyInstaller'":
  .venv\Scripts\pip.exe install pyinstaller

Se aparecer "No module named 'flet'" no EXE:
  Certifique-se de estar usando o comando correto:
  .venv\Scripts\flet.exe pack main.py --name=FichaPokemonRPG -y

Se houver erro ao gerar o .exe:
  .venv\Scripts\pip.exe install --upgrade flet pyinstaller

Para gerar versão de 32-bit:
  Use Python 32-bit para criar o venv e executar o build

Se o antivírus bloquear o EXE:
  Adicione exceção na pasta dist/ ou desative temporariamente
