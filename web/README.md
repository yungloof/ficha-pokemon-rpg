# Ficha RPG Pokémon - Versão Web

Versão web do app, compatível **100%** com as fichas salvas pela versão Flet (desktop).

## Como rodar

```bash
# Na pasta do projeto
.venv\Scripts\python.exe web/app.py
# ou
python web/app.py
```

Acesse: **http://127.0.0.1:5000**

---

## 🚀 Jogar com amigos (casas diferentes) – gratuito e fácil

### Opção 1: ngrok (mais rápido)

1. Baixe o ngrok: https://ngrok.com/download
2. Rode o app: `python web/app.py`
3. Em outro terminal: `ngrok http 5000`
4. O ngrok mostra uma URL tipo `https://abc123.ngrok-free.app`
5. Envie essa URL pros seus amigos
6. **Mestre**: acesse a URL + `/mestre` (ex: `https://abc123.ngrok-free.app/mestre`)

⚠️ No plano gratuito a URL muda a cada vez que você reinicia o ngrok. Enquanto o app e o ngrok estiverem rodando, funciona.

---

### Opção 2: Render (URL fixa, sempre online)

1. Crie conta em https://render.com (grátis)
2. No GitHub, coloque o projeto e crie um **Web Service**
3. Configurações:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python web/app.py`
   - **Root Directory**: deixe em branco (ou a raiz do repo)
4. Deploy
5. Render gera uma URL fixa (ex: `https://ficha-pokemon.onrender.com`)

⚠️ No plano gratuito o app “dorme” após ~15 min sem uso. O primeiro acesso depois pode demorar ~30 s para “acordar”.

## Recursos

- ✅ Todas as funções da versão Flet
- ✅ Importar ficha: aceita JSON da versão antiga (migração automática)
- ✅ Exportar ficha: mesmo formato, compatível com a versão Flet
- ✅ Salva em `ficha_save.json` quando rodando localmente
- ✅ LocalStorage: backup automático no navegador
- ✅ Funciona em celular, tablet e desktop

## Migração de fichas

Seus amigos podem:
1. Abrir a versão web
2. Clicar em **Importar**
3. Selecionar o arquivo `ficha_xxx.json` (da versão Flet)
4. A ficha será migrada e carregada

As classes antigas (Criador, Ranger, etc.) são convertidas automaticamente para as do livro (Treinador Ás, Patrulheiro, etc.).
