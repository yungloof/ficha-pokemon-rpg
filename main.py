import flet as ft
import math
import random
import copy

from constants import (
    ARQUIVO_SAVE,
    POINT_BUY_TOTAL,
    POINT_BUY_MIN,
    POINT_BUY_MAX,
    get_stats_default,
    ESPECIALIZACOES,
    REGIOES_ORIGEM,
    ORIGENS_JORNADA,
    LISTA_TMS,
    CLASSES_TREINADOR,
    TALENTOS,
    PACOTES_AVENTURA,
    NATUREZAS_POKEMON,
    TIPOS_POKEMON,
    LEALDADE_NIVEIS,
    REGRAS_TEXTO,
    REGRAS_RESUMO,
    CORES_TIPO_POKEMON,
)
from save_utils import carregar, salvar_local, exportar, importar_de, criar_backup, validar_importacao


def _espec_key(nome):
    """Normaliza nome da especialização para chave em stats."""
    return nome.lower().replace(" ", "_").replace("í", "i").replace("ó", "o").replace("ã", "a").replace("ú", "u").replace("ç", "c")


def main(page: ft.Page):
    # --- CONFIGURAÇÃO VISUAL ---
    page.title = "Ficha RPG Pokémon: Versão Oficial"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 520
    page.window_height = 900
    page.window_min_width = 420
    page.window_min_height = 600
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    COR_PRIMARIA = "#00E676"
    COR_SECUNDARIA = "#00B359"
    COR_ACENTO = "#FFD700"
    COR_FUNDO = "#121212"
    COR_CARD = "#1e1e1e"
    COR_CARD_ALT = "#2a2a2a"

    # --- CARREGAR DADOS (constantes vêm de constants.py) ---
    stats_default = get_stats_default()
    stats = stats_default.copy()
    try:
        dados = carregar()
        stats.update(dados)
    except ValueError as err:
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Erro ao carregar: {err}. Usando ficha em branco."), bgcolor="orange")
        page.snack_bar.open = True
    except Exception:
        stats = stats_default.copy()

    # Histórico de rolagens (últimas 15)
    historico_rolagens = []

    def adicionar_historico(tipo: str, resultado: str):
        historico_rolagens.insert(0, {"tipo": tipo, "texto": resultado})
        if len(historico_rolagens) > 15:
            historico_rolagens.pop()

    # Dados do jogo vêm de constants.py (ESPECIALIZACOES, REGIOES_ORIGEM, etc.)

    def salvar():
        stats["nome"] = input_nome.value
        stats["nivel"] = input_nivel.value
        stats["classe"] = dropdown_classe.value
        stats["regiao_origem"] = dropdown_regiao.value
        stats["origem_jornada"] = dropdown_origem_jornada.value
        stats["especializacao"] = dropdown_espec.value
        # Salvar escolhas de especialização (perícias/atributos opcionais)
        espec = dropdown_espec.value
        if espec in ESPECIALIZACOES:
            e = ESPECIALIZACOES[espec]
            if "pericias_opcoes" in e and dropdown_espec_pericia.value:
                stats[f"espec_pericia_{_espec_key(espec)}"] = dropdown_espec_pericia.value
            if "atributo_opcoes" in e and dropdown_espec_atributo.value:
                stats[f"espec_atributo_{_espec_key(espec)}"] = dropdown_espec_atributo.value
        stats["tm_escolhido"] = dropdown_tm.value
        stats["hp_atual"] = hp_atual.value
        stats["hp_max"] = hp_max.value
        stats["deslocamento"] = input_speed.value
        stats["pokedollars"] = input_money.value
        stats["pokebolas"] = input_pokebolas.value
        stats["itens_chave"] = input_chave.value
        stats["consumiveis"] = input_consumiveis.value
        stats["pacote_aventura"] = dropdown_pacote.value

        # Sincronizar perícias dos checkboxes para stats (sempre na hora de salvar)
        pericias_auto = get_pericias_auto()
        talentos_map = {"Acrobata": "Acrobacia", "Dedos Rapidos": "Prestidigitação", "Musculoso": "Atletismo", "Perceptivo": "Percepção", "Sorrateiro": "Furtividade"}
        pericias_talentos = [talentos_map[t] for t in stats.get("talentos", []) if t in talentos_map]
        proficientes = list(set(pericias_auto + pericias_talentos))
        for pericia, itens in ui_pericias.items():
            if itens["check"].value and pericia not in proficientes:
                proficientes.append(pericia)
        stats["pericias_proficientes"] = proficientes

        salvar_local(stats)

    def calc_mod(val):
        try:
            return math.floor((int(val) - 10) / 2)
        except:
            return 0

    def get_level_data(lvl_str):
        try:
            lvl = int(lvl_str)
        except:
            lvl = 1

        prof = 2 + math.floor((lvl - 1) / 4)

        max_sr = 2
        if lvl >= 17:
            max_sr = 15
        elif lvl >= 14:
            max_sr = 14
        elif lvl >= 11:
            max_sr = 12
        elif lvl >= 8:
            max_sr = 10
        elif lvl >= 6:
            max_sr = 8
        elif lvl >= 3:
            max_sr = 5

        slots = 3
        if lvl >= 15:
            slots = 6
        elif lvl >= 10:
            slots = 5
        elif lvl >= 5:
            slots = 4

        return prof, max_sr, slots

    def calcular_hp_sugerido():
        try:
            lvl = int(input_nivel.value)
            con_mod = calc_mod(stats["con"])
            hp = (10 + con_mod) + ((lvl - 1) * (2 + con_mod))

            # Bônus de HP do talento Robusto
            talentos = stats.get("talentos", [])
            if "Robusto" in talentos:
                hp += 2 * lvl

            return max(1, hp)
        except:
            return 10

    def parse_int(valor, default=0):
        try:
            return int(valor)
        except:
            return default

    def stat_cost(valor):
        if valor < POINT_BUY_MIN or valor > POINT_BUY_MAX:
            return None
        if valor <= 13:
            return valor - POINT_BUY_MIN
        return 5 + (valor - 13) * 2

    def get_pericias_auto():
        """Retorna perícias automáticas de especialização, região e origem"""
        pericias = ["Adestrar Animais"]

        # Região de Origem
        regiao = dropdown_regiao.value
        if regiao in REGIOES_ORIGEM and REGIOES_ORIGEM[regiao]["pericia"]:
            pericias.append(REGIOES_ORIGEM[regiao]["pericia"])

        # Especialização
        espec = dropdown_espec.value
        if espec in ESPECIALIZACOES:
            e = ESPECIALIZACOES[espec]
            if "pericias_opcoes" in e:
                key = f"espec_pericia_{_espec_key(espec)}"
                chosen = stats.get(key)
                if chosen and chosen in e["pericias_opcoes"]:
                    pericias.append(chosen)
                else:
                    pericias.append(e["pericias_opcoes"][0])
            else:
                pericias.extend(e.get("pericias", []))

        # Origem de Jornada
        origem = dropdown_origem_jornada.value
        if origem in ORIGENS_JORNADA:
            pericias.extend(ORIGENS_JORNADA[origem]["pericias"])

        return list(set(pericias))

    # --- ATUALIZAÇÃO UI ---
    def atualizar_tudo(e=None):
        # 1. Atributos base e Mods
        talentos_ativos = stats.get("talentos", [])

        for stat, campo in ui_inputs.items():
            stats[stat] = campo.value
            base_val = parse_int(campo.value, 8)

            # Aplicar bônus de região
            regiao = dropdown_regiao.value
            bonus_regiao = 0
            if regiao in REGIOES_ORIGEM:
                bonus_regiao = REGIOES_ORIGEM[regiao]["bonus"].get(stat, 0)

            # Aplicar bônus de especialização
            espec = dropdown_espec.value
            bonus_espec = 0
            if espec in ESPECIALIZACOES:
                e = ESPECIALIZACOES[espec]
                atributo_espec = e.get("atributo")
                if "atributo_opcoes" in e:
                    key = f"espec_atributo_{_espec_key(espec)}"
                    atributo_espec = stats.get(key) or e["atributo_opcoes"][0]
                if atributo_espec == stat:
                    bonus_espec = 1

            # Aplicar bônus de talentos
            bonus_talento = 0
            talentos_bonus = []

            # Talentos que dão +1 em atributos específicos
            if "Acrobata" in talentos_ativos and stat == "des":
                bonus_talento += 1
            if "Atleta" in talentos_ativos and stat in ["for", "des"]:
                bonus_talento += 1
            if "Ator" in talentos_ativos and stat == "car":
                bonus_talento += 1
            if "Dedos Rapidos" in talentos_ativos and stat == "des":
                bonus_talento += 1
            if "Mente Afiada" in talentos_ativos and stat == "int":
                bonus_talento += 1
            if "Musculoso" in talentos_ativos and stat == "for":
                bonus_talento += 1
            if "Observador" in talentos_ativos and stat in ["int", "sab"]:
                bonus_talento += 1
            if "Perceptivo" in talentos_ativos and stat == "sab":
                bonus_talento += 1
            if "Resistente" in talentos_ativos and stat == "con":
                bonus_talento += 1
            if "Sorrateiro" in talentos_ativos and stat == "des":
                bonus_talento += 1
            if "Resiliente" in talentos_ativos:
                bonus_talento += 1

            total_val = base_val + bonus_regiao + bonus_espec + bonus_talento
            mod = calc_mod(total_val)
            ui_mods[stat].value = f"{mod:+d}"

            # Mostrar bônus
            if bonus_regiao > 0 or bonus_espec > 0 or bonus_talento > 0:
                ui_mods[stat].value += f" ({base_val}"
                if bonus_regiao > 0:
                    ui_mods[stat].value += f"+{bonus_regiao}R"
                if bonus_espec > 0:
                    ui_mods[stat].value += f"+{bonus_espec}E"
                if bonus_talento > 0:
                    ui_mods[stat].value += f"+{bonus_talento}T"
                ui_mods[stat].value += ")"

        # 2. Dados de Nível
        prof, max_sr, slots = get_level_data(input_nivel.value)
        ui_prof_bonus.value = f"+{prof}"
        ui_max_sr.value = str(max_sr)
        ui_pokeslots.value = str(slots)

        # 3. Combate e HP Sugerido
        mod_des = calc_mod(parse_int(stats["des"], 8))

        # Bônus de CA de Sinnoh
        bonus_ca = 0
        regiao = dropdown_regiao.value
        if regiao == "Sinnoh":
            bonus_ca = 2

        txt_ca.value = str(10 + mod_des + bonus_ca)

        # Bônus de Iniciativa
        bonus_inic = 0
        if "Alerta" in talentos_ativos:
            bonus_inic = 5

        txt_inic.value = f"{mod_des + bonus_inic:+d}"
        if bonus_inic > 0:
            txt_inic.value += " (Alerta)"

        hp_sug = calcular_hp_sugerido()
        txt_hp_sug.value = f"(Sugerido: {hp_sug})"
        try:
            cur_hp = parse_int(hp_atual.value, 0)
            max_hp = parse_int(hp_max.value, 0)
            if max_hp > 0:
                barra_hp.value = max(0, min(cur_hp, max_hp)) / max_hp
            else:
                barra_hp.value = 0
        except:
            barra_hp.value = 0

        # 4. Especialização
        spec = dropdown_espec.value
        if spec in ESPECIALIZACOES:
            txt_spec_desc.value = ESPECIALIZACOES[spec]["desc"]
            e = ESPECIALIZACOES[spec]
            # Mostrar dropdown de perícia (Sombrio, Alquimista, Esquiador)
            if "pericias_opcoes" in e:
                container_espec_pericia.visible = True
                dropdown_espec_pericia.options = [ft.dropdown.Option(p) for p in e["pericias_opcoes"]]
                key = f"espec_pericia_{_espec_key(spec)}"
                val = stats.get(key) or e["pericias_opcoes"][0]
                if val not in e["pericias_opcoes"]:
                    val = e["pericias_opcoes"][0]
                dropdown_espec_pericia.value = val
            else:
                container_espec_pericia.visible = False
            # Mostrar dropdown de atributo (Artista Marcial, Alpinista, Metalúrgico, Jogador de Equipe)
            if "atributo_opcoes" in e:
                container_espec_atributo.visible = True
                dropdown_espec_atributo.options = [ft.dropdown.Option(key=a, text=ATTR_DISPLAY.get(a, a.upper())) for a in e["atributo_opcoes"]]
                key = f"espec_atributo_{_espec_key(spec)}"
                val = stats.get(key) or e["atributo_opcoes"][0]
                if val not in e["atributo_opcoes"]:
                    val = e["atributo_opcoes"][0]
                dropdown_espec_atributo.value = val
            else:
                container_espec_atributo.visible = False
        else:
            container_espec_pericia.visible = False
            container_espec_atributo.visible = False

        # 5. Região
        regiao = dropdown_regiao.value
        if regiao in REGIOES_ORIGEM:
            txt_regiao_desc.value = REGIOES_ORIGEM[regiao]["desc"]
            if REGIOES_ORIGEM[regiao]["habilidade"]:
                txt_regiao_habilidade.value = "⚡ " + REGIOES_ORIGEM[regiao]["habilidade"]
            else:
                txt_regiao_habilidade.value = ""

        # 6. Origem de Jornada
        origem = dropdown_origem_jornada.value
        if origem in ORIGENS_JORNADA:
            data = ORIGENS_JORNADA[origem]

            # Título e Descrição
            if "titulo" in data and data["titulo"]:
                txt_origem_desc.value = f"\"{data['titulo']}\" - {data['desc']}"
            else:
                txt_origem_desc.value = data["desc"]

            # Habilidade
            if "hab_nome" in data and data["hab_nome"]:
                txt_origem_habilidade.value = f"⭐ {data['hab_nome']}:\n{data['hab_desc']}"
            else:
                txt_origem_habilidade.value = ""

            # Equipamento
            if "equip" in data and data["equip"]:
                txt_origem_equip.value = f"🎁 Bônus: {data['equip']}"
            else:
                txt_origem_equip.value = ""

            # Mostrar TM apenas para Estudioso
            container_tm.visible = (origem == "Estudioso")
        else:
            container_tm.visible = False
            txt_origem_habilidade.value = ""
            txt_origem_equip.value = ""

        # 7. Classe
        classe = dropdown_classe.value
        if classe in CLASSES_TREINADOR:
            c = CLASSES_TREINADOR[classe]
            if isinstance(c, str):
                txt_classe_desc.value = c
            else:
                parts = [c.get("desc", "")]
                if c.get("hab_nome"):
                    parts.append(f"\n⭐ {c['hab_nome']}\n{c.get('hab_desc', '')}")
                txt_classe_desc.value = "\n".join(parts)

        # 8. Pacote de Aventura
        pacote = dropdown_pacote.value
        if pacote in PACOTES_AVENTURA:
            txt_pacote_desc.value = PACOTES_AVENTURA[pacote]

        # 9. Perícias automáticas
        pericias_auto = get_pericias_auto()
        txt_pericias_auto.value = f"Automáticas: {', '.join(pericias_auto)}"

        # 10. Perícias
        # Perícias de talentos
        pericias_talentos = []
        if "Acrobata" in talentos_ativos: pericias_talentos.append("Acrobacia")
        if "Dedos Rapidos" in talentos_ativos: pericias_talentos.append("Prestidigitação")
        if "Musculoso" in talentos_ativos: pericias_talentos.append("Atletismo")
        if "Perceptivo" in talentos_ativos: pericias_talentos.append("Percepção")
        if "Sorrateiro" in talentos_ativos: pericias_talentos.append("Furtividade")

        for pericia, itens in ui_pericias.items():
            check, texto = itens['check'], itens['valor']
            base = calc_mod(parse_int(stats[pericias_map[pericia]], 8))

            # Verificar se é proficiente
            is_proficient = check.value or pericia in pericias_auto or pericia in pericias_talentos

            # Especialista (dobro da proficiência)
            is_expert = False
            if is_proficient:
                if ("Acrobata" in talentos_ativos and pericia == "Acrobacia" and pericia in pericias_auto): is_expert = True
                if ("Dedos Rapidos" in talentos_ativos and pericia == "Prestidigitação" and pericia in pericias_auto): is_expert = True
                if ("Musculoso" in talentos_ativos and pericia == "Atletismo" and pericia in pericias_auto): is_expert = True
                if ("Perceptivo" in talentos_ativos and pericia == "Percepção" and pericia in pericias_auto): is_expert = True
                if ("Sorrateiro" in talentos_ativos and pericia == "Furtividade" and pericia in pericias_auto): is_expert = True

            if is_expert:
                total = base + (prof * 2)
                texto.value = f"{total:+d} ⭐"
            elif is_proficient:
                total = base + prof
                texto.value = f"{total:+d}"
            else:
                total = base
                texto.value = f"{total:+d}"

            texto.color = COR_PRIMARIA if is_proficient else "white"

            # Atualizar lista de proficientes no save
            if check.value and pericia not in stats["pericias_proficientes"]:
                stats["pericias_proficientes"].append(pericia)
            elif not check.value and pericia in stats["pericias_proficientes"] and pericia not in pericias_auto and pericia not in pericias_talentos:
                stats["pericias_proficientes"].remove(pericia)

        # 11. Testes de Resistência
        regiao = dropdown_regiao.value
        for attr, display in [("for", "FOR"), ("des", "DES"), ("con", "CON"), ("int", "INT"), ("sab", "SAB"), ("car", "CAR")]:
            mod = calc_mod(parse_int(stats[attr], 8))
            is_proficient = (attr == "car") or (attr == "con" and regiao == "Sinnoh")
            if is_proficient:
                total = mod + prof
                ui_saves[attr].value = f"{display}: {total:+d} ✓"
                ui_saves[attr].color = COR_PRIMARIA
            else:
                ui_saves[attr].value = f"{display}: {mod:+d}"
                ui_saves[attr].color = "grey"

        update_point_buy_ui()
        salvar()
        render_talentos()
        page.update()

    # --- UI COMPONENTS ---

    # Header melhorado
    input_nome = ft.TextField(
        value=stats["nome"],
        text_size=22,
        width=250,
        border="none",
        hint_text="Nome do Treinador",
        on_change=atualizar_tudo,
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD)
    )

    input_nivel = ft.TextField(
        value=stats["nivel"],
        label="Nível",
        width=90,
        on_change=atualizar_tudo,
        text_align="center",
        border_color=COR_PRIMARIA
    )

    ui_prof_bonus = ft.Text("+2", color=COR_PRIMARIA, weight="bold", size=16)
    ui_max_sr = ft.Text("2", color=COR_PRIMARIA, weight="bold", size=16)
    ui_pokeslots = ft.Text("3", color=COR_PRIMARIA, weight="bold", size=16)

    def info_box(label, value_control, icon=None):
        content = [
            ft.Text(label, size=10, color="grey", weight="bold"),
            value_control
        ]
        if icon:
            content.insert(0, ft.Icon(icon, size=20, color=COR_PRIMARIA))
        return ft.Container(
            content=ft.Column(content, horizontal_alignment="center", spacing=2),
            bgcolor=COR_CARD_ALT,
            padding=10,
            border_radius=10,
            expand=True
        )

    # FilePicker para exportar/importar (API Flet 0.80+: Service, não vai no overlay)
    async def btn_exportar_click(e):
        salvar()
        path = await ft.FilePicker().save_file(
            dialog_title="Exportar ficha",
            file_name=f"ficha_{stats.get('nome', 'treinador').replace(' ', '_')}.json",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"],
        )
        if path:
            try:
                exportar(stats, path)
                page.snack_bar = ft.SnackBar(content=ft.Text("✅ Ficha exportada com sucesso!"), bgcolor=COR_SECUNDARIA)
            except OSError as err:
                page.snack_bar = ft.SnackBar(content=ft.Text(f"❌ Erro ao exportar: {err}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    async def btn_importar_click(e):
        files = await ft.FilePicker().pick_files(
            dialog_title="Importar ficha",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"],
            allow_multiple=False,
        )
        if not files:
            return
        f = files[0]
        path = f.path
        if not path:
            page.snack_bar = ft.SnackBar(content=ft.Text("❌ Não foi possível obter o caminho do arquivo."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return
        ok, msg = validar_importacao(path)
        if not ok:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"❌ {msg}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return
        try:
            dados = importar_de(path)
            stats.clear()
            stats.update(dados)
            input_nome.value = stats["nome"]
            input_nivel.value = stats["nivel"]
            dropdown_classe.value = stats.get("classe") or "Nenhuma"
            dropdown_regiao.value = stats.get("regiao_origem") or "Nenhuma"
            dropdown_origem_jornada.value = stats.get("origem_jornada") or "Nenhuma"
            dropdown_espec.value = stats.get("especializacao") or "Nenhuma"
            dropdown_tm.value = stats.get("tm_escolhido") or ""
            hp_atual.value = stats["hp_atual"]
            hp_max.value = stats["hp_max"]
            input_speed.value = stats.get("deslocamento", "9m")
            input_money.value = stats.get("pokedollars", "0")
            input_pokebolas.value = stats.get("pokebolas", "5x Pokébolas")
            input_chave.value = stats.get("itens_chave", "Licença de Treinador\nPokédex")
            input_consumiveis.value = stats.get("consumiveis", "1x Poção")
            dropdown_pacote.value = stats.get("pacote_aventura") or "Aventureiro"
            for stat, campo in ui_inputs.items():
                if stat in stats:
                    campo.value = stats[stat]
            salvar()
            atualizar_tudo()
            render_pokes()
            render_talentos()
            for pericia, itens in ui_pericias.items():
                itens["check"].value = pericia in stats.get("pericias_proficientes", [])
            page.snack_bar = ft.SnackBar(content=ft.Text("✅ Ficha importada com sucesso!"), bgcolor=COR_SECUNDARIA)
        except (ValueError, OSError) as err:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"❌ Erro ao importar: {err}"), bgcolor="red")
        page.snack_bar.open = True
        page.update()

    card_export_import = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.SAVE, color=COR_ACENTO, size=20),
            ft.Text("Backup da ficha", size=12, weight="bold", color=COR_ACENTO),
            ft.ElevatedButton("Exportar", icon=ft.Icons.UPLOAD, on_click=btn_exportar_click, bgcolor=COR_SECUNDARIA, color="black", height=36),
            ft.ElevatedButton("Importar", icon=ft.Icons.DOWNLOAD, on_click=btn_importar_click, bgcolor=COR_CARD_ALT, color="white", height=36),
        ], spacing=10, wrap=True),
        padding=10,
        bgcolor=COR_CARD,
        border_radius=8,
        margin=ft.Margin(left=10, right=10, bottom=5, top=0)
    )

    header = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CATCHING_POKEMON, size=60, color=COR_PRIMARIA),
                ft.Column([
                    input_nome,
                    ft.Row([
                        input_nivel,
                        info_box("PROF", ui_prof_bonus),
                        info_box("MAX SR", ui_max_sr),
                        info_box("SLOTS", ui_pokeslots),
                    ], spacing=8, expand=True)
                ], spacing=5, expand=True),
            ], alignment="start"),
            card_export_import,
        ], spacing=5),
        padding=15,
        bgcolor=COR_CARD,
        border_radius=10,
        margin=10
    )

    # Região de Origem
    dropdown_regiao = ft.Dropdown(
        options=[ft.dropdown.Option(k) for k in REGIOES_ORIGEM.keys()],
        value=stats.get("regiao_origem") or "Nenhuma",
        text_size=13,
        height=50,
        border_color=COR_SECUNDARIA,
        on_select=atualizar_tudo,
        label="Região de Origem"
    )
    txt_regiao_desc = ft.Text("", size=11, color="grey", italic=True, no_wrap=False)
    txt_regiao_habilidade = ft.Text("", size=10, color=COR_ACENTO, weight="bold", no_wrap=False)

    card_regiao = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.PUBLIC, color=COR_ACENTO, size=20),
                ft.Text("Região de Origem", size=12, weight="bold", color=COR_ACENTO)
            ]),
            dropdown_regiao,
            txt_regiao_desc,
            txt_regiao_habilidade
        ], spacing=5),
        bgcolor=COR_CARD,
        padding=12,
        border_radius=10,
        margin=ft.Margin(left=10, right=10, bottom=5, top=0)
    )

    # --- ORIGEM DE JORNADA ---
    dropdown_origem_jornada = ft.Dropdown(
        options=[ft.dropdown.Option(k) for k in ORIGENS_JORNADA.keys()],
        value=stats.get("origem_jornada") or "Nenhuma",
        text_size=13,
        height=50,
        border_color=COR_SECUNDARIA,
        on_select=atualizar_tudo,
        label="Origem de Jornada"
    )

    txt_origem_desc = ft.Text("", size=11, color="grey", italic=True)
    txt_origem_habilidade = ft.Text("", size=11, color=COR_ACENTO, weight="bold")
    txt_origem_equip = ft.Text("", size=11, color=COR_SECUNDARIA)

    # Dropdown do TM (Estudioso)
    dropdown_tm = ft.Dropdown(
        options=[ft.dropdown.Option(t) for t in LISTA_TMS],
        value=stats.get("tm_escolhido") or "",
        label="Escolha seu TM (Estudioso)",
        on_select=atualizar_tudo,
        text_size=12,
        border_color=COR_ACENTO
    )
    container_tm = ft.Container(content=dropdown_tm, visible=False)

    card_origem_jornada = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.HISTORY_EDU, color=COR_ACENTO, size=20),
                ft.Text("Origem de Jornada", size=12, weight="bold", color=COR_ACENTO)
            ]),
            dropdown_origem_jornada,
            txt_origem_desc,
            ft.Divider(height=5, color="grey"),
            txt_origem_habilidade,
            txt_origem_equip,
            container_tm
        ], spacing=5),
        bgcolor=COR_CARD,
        padding=12,
        border_radius=10,
        margin=ft.Margin(left=10, right=10, bottom=5, top=0)
    )
    # Especialização
    dropdown_espec = ft.Dropdown(
        options=[ft.dropdown.Option(k) for k in ESPECIALIZACOES.keys()],
        value=stats.get("especializacao") or "Nenhuma",
        text_size=13,
        height=50,
        border_color=COR_PRIMARIA,
        on_select=atualizar_tudo,
        label="Especialização"
    )
    txt_spec_desc = ft.Text("", size=11, color="grey", italic=True, no_wrap=False)
    ATTR_DISPLAY = {"for": "FOR", "des": "DES", "con": "CON", "int": "INT", "sab": "SAB", "car": "CAR"}
    dropdown_espec_pericia = ft.Dropdown(
        label="Escolha a perícia",
        text_size=12, height=45, border_color=COR_PRIMARIA,
        on_select=atualizar_tudo
    )
    dropdown_espec_atributo = ft.Dropdown(
        label="Escolha o atributo +1",
        text_size=12, height=45, border_color=COR_PRIMARIA,
        on_select=atualizar_tudo
    )
    container_espec_pericia = ft.Container(content=dropdown_espec_pericia, visible=False)
    container_espec_atributo = ft.Container(content=dropdown_espec_atributo, visible=False)

    card_espec = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.STARS, color=COR_PRIMARIA, size=20),
                ft.Text("Especialização", size=12, weight="bold", color=COR_PRIMARIA)
            ]),
            dropdown_espec,
            txt_spec_desc,
            container_espec_pericia,
            container_espec_atributo
        ], spacing=5),
        bgcolor=COR_CARD,
        padding=12,
        border_radius=10,
        margin=ft.Margin(left=10, right=10, bottom=5, top=0)
    )

    # Classe de Treinador
    dropdown_classe = ft.Dropdown(
        options=[ft.dropdown.Option(k) for k in CLASSES_TREINADOR.keys()],
        value=stats.get("classe") or "Nenhuma",
        text_size=13,
        height=50,
        border_color=COR_SECUNDARIA,
        on_select=atualizar_tudo,
        label="Classe de Treinador (Nível 2+)"
    )
    txt_classe_desc = ft.Text("", size=11, color="grey", italic=True, no_wrap=False)

    card_classe = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SCHOOL, color=COR_SECUNDARIA, size=20),
                ft.Text("Classe de Treinador", size=12, weight="bold", color=COR_SECUNDARIA)
            ]),
            dropdown_classe,
            txt_classe_desc
        ], spacing=5),
        bgcolor=COR_CARD,
        padding=12,
        border_radius=10,
        margin=ft.Margin(left=10, right=10, bottom=10, top=0)
    )

    # Combate
    hp_atual = ft.Text(stats["hp_atual"], size=18, weight="bold")
    hp_max = ft.TextField(value=stats["hp_max"], width=60, text_align="center", on_change=atualizar_tudo)
    txt_hp_sug = ft.Text("", size=10, color="grey")
    barra_hp = ft.ProgressBar(value=1.0, color="#ff5252", bgcolor="#444", height=8, border_radius=4)

    def mudar_hp(d):
        try:
            cur, mx = int(hp_atual.value), int(hp_max.value)
            new = max(0, min(cur + d, mx))
            hp_atual.value = str(new)
            barra_hp.value = new / mx if mx > 0 else 0
            atualizar_tudo()
        except:
            pass

    mudar_hp(0)

    txt_ca = ft.Text("10", size=28, weight="bold", color="black")
    txt_inic = ft.Text("+0", size=20, weight="bold", color="black")
    txt_resultado_inic = ft.Text("", size=11, color=COR_ACENTO, weight="bold")
    input_speed = ft.TextField(value=stats["deslocamento"], width=60, text_align="center", text_size=14, border="none",
                               on_change=atualizar_tudo)

    def rolar_iniciativa(e):
        """Rola d20 + modificador de iniciativa"""
        d20 = random.randint(1, 20)
        mod_str = txt_inic.value
        try:
            modificador = int(mod_str)
        except:
            modificador = 0
        total = d20 + modificador

        if d20 == 20:
            txt_resultado_inic.value = f"🎯 Iniciativa: {d20}{modificador:+d} = {total} (20!)"
            txt_resultado_inic.color = COR_PRIMARIA
        elif d20 == 1:
            txt_resultado_inic.value = f"💥 Iniciativa: {d20}{modificador:+d} = {total} (1...)"
            txt_resultado_inic.color = "red"
        else:
            txt_resultado_inic.value = f"⚡ Iniciativa: {d20}{modificador:+d} = {total}"
            txt_resultado_inic.color = COR_ACENTO
        adicionar_historico("Iniciativa", txt_resultado_inic.value)
        atualizar_historico_display()
        page.update()

    btn_rolar_inic = ft.IconButton(
        icon=ft.Icons.FLASH_ON,
        icon_size=20,
        icon_color="black",
        bgcolor=COR_ACENTO,
        on_click=rolar_iniciativa,
        tooltip="Rolar Iniciativa"
    )

    def card_combat_stat(titulo, conteudo, cor_bg=COR_PRIMARIA, botao=None):
        children = [ft.Text(titulo, color="black" if cor_bg == COR_PRIMARIA else "white", size=11, weight="bold"),
                    conteudo]
        if botao:
            children.append(botao)
        return ft.Container(
            content=ft.Column(
                children,
                horizontal_alignment="center", spacing=3),
            bgcolor=cor_bg,
            padding=10,
            border_radius=12,
            expand=True,
            height=100,
            alignment=ft.Alignment(0, 0)
        )

    # Testes de Resistência
    ui_saves = {}
    txt_resultado_save = ft.Text("", size=13, color=COR_ACENTO, weight="bold")

    def rolar_save(attr_nome):
        """Rola d20 + modificador de resistência"""
        def roll(e):
            d20 = random.randint(1, 20)
            mod_str = ui_saves[attr_nome].value.split(":")[1].strip().replace("✓", "").strip()
            try:
                modificador = int(mod_str)
            except:
                modificador = 0
            total = d20 + modificador

            attr_display = {"for": "FOR", "des": "DES", "con": "CON", "int": "INT", "sab": "SAB", "car": "CAR"}[attr_nome]

            if d20 == 20:
                resultado = f"🎯 Teste de {attr_display}: {d20} + {modificador:+d} = {total} (SUCESSO CRÍTICO!)"
                txt_resultado_save.color = COR_PRIMARIA
            elif d20 == 1:
                resultado = f"💥 Teste de {attr_display}: {d20} + {modificador:+d} = {total} (FALHA CRÍTICA!)"
                txt_resultado_save.color = "red"
            else:
                resultado = f"🎲 Teste de {attr_display}: {d20} + {modificador:+d} = {total}"
                txt_resultado_save.color = COR_ACENTO

            txt_resultado_save.value = resultado
            adicionar_historico(f"Save {attr_display}", resultado)
            atualizar_historico_display()
            page.update()
        return roll

    saves_grid = ft.Column([], spacing=5)
    col_historico = ft.Column([], spacing=2, scroll=ft.ScrollMode.AUTO, height=80)

    def atualizar_historico_display():
        col_historico.controls.clear()
        for h in historico_rolagens[:10]:
            col_historico.controls.append(
                ft.Text(h["texto"], size=10, color="grey", no_wrap=False, overflow=ft.TextOverflow.ELLIPSIS)
            )

    # Roller de dados genérico
    roller_dado = ft.Dropdown(
        options=[ft.dropdown.Option("d4"), ft.dropdown.Option("d6"), ft.dropdown.Option("d8"),
                 ft.dropdown.Option("d10"), ft.dropdown.Option("d12"), ft.dropdown.Option("d20")],
        value="d20", width=80, height=45, border_color=COR_ACENTO,
        label="Dado", tooltip="Tipo de dado"
    )
    roller_mod = ft.TextField(value="0", width=60, text_align="center", border_color=COR_ACENTO,
                              hint_text="Mod", tooltip="Modificador (+ ou -)",
                              input_filter=ft.InputFilter(allow=True, regex_string=r"^-?\d*$"))
    roller_resultado = ft.Text("", size=12, color=COR_ACENTO, weight="bold")

    def rolar_dado_gen(e):
        try:
            dado = roller_dado.value or "d20"
            faces = int(dado[1:])
            mod = int(roller_mod.value or 0)
            r = random.randint(1, faces)
            total = r + mod
            roller_resultado.value = f"🎲 {dado}: {r} + {mod:+d} = {total}"
            adicionar_historico(dado, roller_resultado.value)
            atualizar_historico_display()
            page.update()
        except:
            roller_resultado.value = "Erro"
            page.update()

    for attr in ["for", "des", "con", "int", "sab", "car"]:
        txt_save = ft.Text("", size=11, weight="bold")
        btn_roll_save = ft.IconButton(
            icon=ft.Icons.CASINO,
            icon_size=16,
            icon_color=COR_ACENTO,
            on_click=rolar_save(attr),
            tooltip=f"Rolar resistência"
        )
        ui_saves[attr] = txt_save
        saves_grid.controls.append(
            ft.Row([txt_save, btn_roll_save], alignment="spaceBetween")
        )

    painel_combate = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SPORTS_MMA, color=COR_PRIMARIA, size=20),
                ft.Text("⚔️ Combate", size=14, weight="bold", color=COR_PRIMARIA),
            ]),
            ft.Row([
                card_combat_stat("CA", txt_ca),
                card_combat_stat("INIC.", txt_inic, COR_ACENTO, btn_rolar_inic),
                card_combat_stat("DESL.", input_speed, COR_CARD_ALT),
            ], spacing=10),
            txt_resultado_inic,
            ft.Divider(height=15, color="transparent"),
            ft.Row([
                ft.Icon(ft.Icons.FAVORITE, color="#ff5252", size=20),
                ft.Text("HP", weight="bold", size=13),
                hp_atual,
                ft.Text("/", size=13),
                hp_max,
                txt_hp_sug
            ], alignment="center"),
            barra_hp,
            ft.Row([
                ft.IconButton(ft.Icons.REMOVE, on_click=lambda e: mudar_hp(-1), icon_size=22, bgcolor=COR_CARD_ALT, tooltip="Diminuir HP"),
                ft.IconButton(ft.Icons.ADD, on_click=lambda e: mudar_hp(1), icon_size=22, bgcolor=COR_CARD_ALT, tooltip="Aumentar HP")
            ], alignment="center"),
            ft.Divider(height=10, color="grey"),
            ft.Row([
                ft.Icon(ft.Icons.SHIELD, color=COR_SECUNDARIA, size=18),
                ft.Text("🛡️ Testes de Resistência", size=12, weight="bold"),
            ]),
            saves_grid,
            ft.Divider(color="grey", height=5),
            txt_resultado_save,
            ft.Divider(height=10, color="grey"),
            ft.Row([
                ft.Icon(ft.Icons.CASINO, color=COR_ACENTO, size=18),
                ft.Text("🎲 Roller", size=12, weight="bold"),
            ]),
            ft.Row([
                roller_dado,
                ft.Text("+", size=14),
                roller_mod,
                ft.IconButton(ft.Icons.PLAY_ARROW, icon_color=COR_PRIMARIA, on_click=rolar_dado_gen, tooltip="Rolar dado"),
                roller_resultado
            ], alignment="center", spacing=8),
            ft.Divider(height=5, color="grey"),
            ft.Row([ft.Icon(ft.Icons.HISTORY, size=14, color="grey"), ft.Text("Histórico", size=10, color="grey")]),
            col_historico
        ], spacing=8),
        bgcolor=COR_CARD,
        padding=15,
        border_radius=12,
        margin=10
    )

    # Atributos
    ui_inputs = {}
    ui_mods = {}
    ui_stat_buttons = {}

    def point_buy_total_cost():
        total = 0
        for campo in ui_inputs.values():
            valor = parse_int(campo.value, POINT_BUY_MIN)
            custo = stat_cost(valor)
            if custo is None:
                return None
            total += custo
        return total

    def point_buy_is_valid():
        total = point_buy_total_cost()
        return total is not None and total <= POINT_BUY_TOTAL

    def ajustar_stat(chave, delta):
        if not point_buy_switch.value:
            return
        atual = parse_int(ui_inputs[chave].value, POINT_BUY_MIN)
        novo = atual + delta
        if novo < POINT_BUY_MIN or novo > POINT_BUY_MAX:
            return
        custo_atual = stat_cost(atual)
        custo_novo = stat_cost(novo)
        if custo_atual is None or custo_novo is None:
            return
        total = point_buy_total_cost()
        if total is None:
            return
        if total - custo_atual + custo_novo > POINT_BUY_TOTAL:
            return
        ui_inputs[chave].value = str(novo)
        atualizar_tudo()

    def make_stat(nome, chave, icon):
        inp = ft.TextField(
            value=stats[chave],
            width=50,
            text_align="center",
            on_change=atualizar_tudo,
            border_color=COR_PRIMARIA,
            text_size=16,
            input_filter=ft.NumbersOnlyInputFilter(),
            keyboard_type=ft.KeyboardType.NUMBER
        )
        btn_menos = ft.IconButton(
            ft.Icons.REMOVE_CIRCLE_OUTLINE,
            icon_size=18,
            disabled=True,
            on_click=lambda e, key=chave: ajustar_stat(key, -1),
            icon_color=COR_PRIMARIA
        )
        btn_mais = ft.IconButton(
            ft.Icons.ADD_CIRCLE_OUTLINE,
            icon_size=18,
            disabled=True,
            on_click=lambda e, key=chave: ajustar_stat(key, 1),
            icon_color=COR_PRIMARIA
        )
        ui_inputs[chave] = inp
        ui_mods[chave] = ft.Text("+0", size=11, weight="bold", color=COR_PRIMARIA, text_align="center")
        ui_stat_buttons[chave] = (btn_menos, btn_mais)
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=24, color=COR_PRIMARIA),
                    ft.Text(nome.upper(), color="grey", size=10, weight="bold"),
                    inp,
                    ft.Row([btn_menos, btn_mais], spacing=0, alignment=ft.MainAxisAlignment.CENTER),
                    ui_mods[chave]
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2
            ),
            bgcolor=COR_CARD,
            padding=10,
            border_radius=12,
            width=115,
            height=175,
            alignment=ft.Alignment(0, 0)
        )

    grid_stats = ft.Row([
        make_stat("Força", "for", ft.Icons.FITNESS_CENTER),
        make_stat("Destreza", "des", ft.Icons.DIRECTIONS_RUN),
        make_stat("Const", "con", ft.Icons.FAVORITE),
        make_stat("Intel", "int", ft.Icons.PSYCHOLOGY),
        make_stat("Sabed", "sab", ft.Icons.VISIBILITY),
        make_stat("Carisma", "car", ft.Icons.EMOJI_PEOPLE)
    ], wrap=True, alignment=ft.MainAxisAlignment.CENTER, spacing=10, run_spacing=10)

    def set_point_buy_controls(enabled):
        for campo in ui_inputs.values():
            campo.read_only = enabled
        for btn_menos, btn_mais in ui_stat_buttons.values():
            btn_menos.disabled = not enabled
            btn_mais.disabled = not enabled

    def reset_point_buy(e=None):
        for campo in ui_inputs.values():
            campo.value = str(POINT_BUY_MIN)
        atualizar_tudo()

    def aplicar_hp_sugerido(e=None):
        hp = calcular_hp_sugerido()
        hp_max.value = str(hp)
        hp_atual.value = str(hp)
        barra_hp.value = 1 if hp > 0 else 0
        atualizar_tudo()

    def update_point_buy_ui():
        if point_buy_remaining is None or point_buy_status is None:
            return
        if not point_buy_switch.value:
            point_buy_remaining.value = "Modo criação desligado."
            point_buy_remaining.color = "grey"
            point_buy_status.value = "Ative para distribuir 27 pontos (8-15)."
            return
        total = point_buy_total_cost()
        if total is None:
            point_buy_remaining.value = "Pontos restantes: ?"
            point_buy_remaining.color = "red"
            point_buy_status.value = "Atributos devem ficar entre 8 e 15."
            return
        restante = POINT_BUY_TOTAL - total
        point_buy_remaining.value = f"Pontos restantes: {restante}/{POINT_BUY_TOTAL}"
        if restante < 0:
            point_buy_remaining.color = "red"
            point_buy_status.value = "❌ Excedeu os 27 pontos."
        elif restante == 0:
            point_buy_remaining.color = COR_PRIMARIA
            point_buy_status.value = "✅ Todos os pontos distribuídos!"
        else:
            point_buy_remaining.color = COR_ACENTO
            point_buy_status.value = f"Distribua os {restante} pontos restantes. Valores 14-15 custam 2."

    def toggle_point_buy(e):
        habilitado = point_buy_switch.value
        set_point_buy_controls(habilitado)
        if habilitado and not point_buy_is_valid():
            reset_point_buy()
        update_point_buy_ui()
        page.update()

    point_buy_switch = ft.Switch(label="Modo Criação (Point Buy)", value=False, on_change=toggle_point_buy,
                                  active_color=COR_PRIMARIA)
    point_buy_remaining = ft.Text("Modo criação desligado.", color="grey", size=13, weight="bold")
    point_buy_status = ft.Text("Ative para distribuir 27 pontos (8-15).", size=11, color="grey")
    btn_reset_points = ft.Button("↺ Resetar (8 em todos)", on_click=reset_point_buy, bgcolor=COR_CARD_ALT,
                                         color="white")
    btn_aplicar_hp = ft.Button("❤️ Aplicar HP Sugerido", on_click=aplicar_hp_sugerido, bgcolor=COR_SECUNDARIA,
                                       color="black")

    card_criacao = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.BUILD_CIRCLE, color=COR_ACENTO, size=20),
                ft.Text("Modo Criação", size=12, weight="bold", color=COR_ACENTO)
            ]),
            point_buy_switch,
            point_buy_remaining,
            point_buy_status,
            ft.Row([btn_reset_points, btn_aplicar_hp], spacing=10, wrap=True),
            ft.Divider(color="grey"),
            ft.Text("📖 Regras Básicas", size=11, weight="bold"),
            ft.Text("Dado de Vida: d8 | Teste de Resistência: Carisma ✓", size=10, color="grey")
        ], spacing=8),
        bgcolor=COR_CARD,
        padding=12,
        border_radius=10,
        margin=10
    )

    # Perícias
    pericias_map = {
        "Atletismo": "for", "Acrobacia": "des", "Furtividade": "des", "Prestidigitação": "des",
        "Arcanismo": "int", "História": "int", "Investigação": "int", "Natureza": "int", "Religião": "int",
        "Adestrar Animais": "sab", "Intuição": "sab", "Medicina": "sab", "Percepção": "sab", "Sobrevivência": "sab",
        "Atuação": "car", "Enganação": "car", "Intimidação": "car", "Persuasão": "car"
    }
    ui_pericias = {}
    col_pericias = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=5)

    txt_pericias_auto = ft.Text("", size=11, color=COR_PRIMARIA, weight="bold")
    txt_resultado_pericia = ft.Text("", size=13, color=COR_ACENTO, weight="bold")

    def rolar_pericia(pericia_nome):
        """Rola d20 + modificador da perícia"""
        def roll(e):
            d20 = random.randint(1, 20)
            mod_str = ui_pericias[pericia_nome]['valor'].value
            try:
                modificador = int(mod_str)
            except:
                modificador = 0
            total = d20 + modificador

            # Detectar crítico/falha crítica
            if d20 == 20:
                resultado = f"🎯 {pericia_nome}: {d20} + {modificador:+d} = {total} (CRÍTICO!)"
                txt_resultado_pericia.color = COR_PRIMARIA
            elif d20 == 1:
                resultado = f"💥 {pericia_nome}: {d20} + {modificador:+d} = {total} (FALHA CRÍTICA!)"
                txt_resultado_pericia.color = "red"
            else:
                resultado = f"🎲 {pericia_nome}: {d20} + {modificador:+d} = {total}"
                txt_resultado_pericia.color = COR_ACENTO

            txt_resultado_pericia.value = resultado
            adicionar_historico(pericia_nome, resultado)
            atualizar_historico_display()
            page.update()
        return roll

    for p, atr in pericias_map.items():
        cb = ft.Checkbox(label=p, value=p in stats.get("pericias_proficientes", []), on_change=atualizar_tudo)
        val = ft.Text("+0", width=40, text_align="right", weight="bold")
        btn_roll = ft.IconButton(
            icon=ft.Icons.CASINO,
            icon_size=18,
            icon_color=COR_ACENTO,
            on_click=rolar_pericia(p),
            tooltip=f"Rolar {p}"
        )
        ui_pericias[p] = {'check': cb, 'valor': val, 'roll': btn_roll}
        col_pericias.controls.append(ft.Container(
            content=ft.Row([
                cb,
                ft.Row([
                    ft.Text(atr.upper(), color="grey", size=10, weight="bold"),
                    val,
                    btn_roll
                ], spacing=5)
            ], alignment="spaceBetween"),
            bgcolor=COR_CARD,
            padding=8,
            border_radius=8,
            margin=2,
            border=ft.border.all(1, COR_CARD_ALT)
        ))

    tela_pericias = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CASINO, color=COR_ACENTO, size=24),
                        ft.Text("🎯 Perícias", size=16, weight="bold", color=COR_PRIMARIA),
                    ]),
                    ft.Text("Escolha 2 perícias iniciais (além das automáticas)", size=11, color="grey"),
                    txt_pericias_auto,
                    ft.Divider(color="grey", height=10),
                    txt_resultado_pericia
                ], spacing=5),
                padding=12,
                bgcolor=COR_CARD,
                border_radius=10,
                margin=10
            ),
            col_pericias
        ], scroll=ft.ScrollMode.AUTO),
        expand=True
    )

    # Mochila & Dinheiro
    input_money = ft.TextField(value=stats["pokedollars"], width=120, text_align="right", on_change=atualizar_tudo,
                                text_size=16, border_color=COR_ACENTO)

    def rolar_dinheiro(e):
        if dropdown_origem_jornada.value == "Nobre":
            # Regra: Equipamento inicial inclui valor MÁXIMO (1000 + 100*16)
            total = 2600
            resultado_roll.value = "👑 Nobre: Riqueza Máxima aplicada!"
            resultado_roll.color = COR_ACENTO
        else:
            dados = sum(random.randint(1, 4) for _ in range(4))
            total = 1000 + (100 * dados)
            resultado_roll.value = f"🎲 Rolou: {dados} → Total: {total} ₽"
            resultado_roll.color = "white"

        input_money.value = str(total)
        adicionar_historico("Dinheiro", resultado_roll.value)
        atualizar_historico_display()
        atualizar_tudo()

    resultado_roll = ft.Text("", size=11, color=COR_ACENTO, weight="bold")
    btn_rolar_money = ft.Button("🎲 Rolar Dinheiro Inicial", on_click=rolar_dinheiro, bgcolor=COR_ACENTO,
                                        color="black", height=45)

    # Pacote de Aventura
    dropdown_pacote = ft.Dropdown(
        options=[ft.dropdown.Option(k) for k in PACOTES_AVENTURA.keys()],
        value=stats.get("pacote_aventura") or "Aventureiro",
        text_size=13,
        height=50,
        border_color=COR_SECUNDARIA,
        on_select=atualizar_tudo,
        label="Pacote de Aventura"
    )
    txt_pacote_desc = ft.Text("", size=10, color="grey", italic=True, no_wrap=False)

    input_pokebolas = ft.TextField(value=stats["pokebolas"], label="🔴 Pokébolas", multiline=True, min_lines=2,
                                   on_change=atualizar_tudo, border_color=COR_PRIMARIA)
    input_chave = ft.TextField(value=stats["itens_chave"], label="🔑 Itens Chave", multiline=True, min_lines=2,
                               on_change=atualizar_tudo, border_color=COR_SECUNDARIA)
    input_consumiveis = ft.TextField(value=stats["consumiveis"], label="🧪 Consumíveis", multiline=True, min_lines=2,
                                     on_change=atualizar_tudo, border_color=COR_ACENTO)

    tela_mochila = ft.ListView([
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.MONETIZATION_ON, color=COR_ACENTO, size=30),
                    ft.Text("Pokédollars", weight="bold", size=16),
                ]),
                ft.Row([
                    ft.Text("₽", color=COR_ACENTO, size=24, weight="bold"),
                    input_money
                ], spacing=10, alignment="center"),
                btn_rolar_money,
                resultado_roll,
                ft.Divider(color="grey"),
                ft.Text("📦 Pacote de Aventura", size=14, weight="bold"),
                dropdown_pacote,
                txt_pacote_desc
            ], spacing=10),
            bgcolor=COR_CARD,
            padding=15,
            border_radius=10,
            margin=10
        ),
        ft.Container(
            content=ft.Column([
                input_pokebolas,
                ft.Divider(color="transparent", height=5),
                input_chave,
                ft.Divider(color="transparent", height=5),
                input_consumiveis
            ]),
            padding=10,
            margin=10
        )
    ], padding=5, spacing=10)

    # Pokémons
    lista_pokemons_view = ft.ListView(expand=True, spacing=10, padding=10)
    novo_poke_nome = ft.TextField(hint_text="Nome do Pokémon", expand=True, border_color=COR_PRIMARIA)

    def get_bonus_tipo_pokemon(tipo):
        """Retorna o bônus do treinador para o tipo de Pokémon"""
        espec = dropdown_espec.value
        if espec not in ESPECIALIZACOES:
            return 0
        # Mapear tipos às especializações
        tipo_map = {
            "Voador": "Guardião dos Pássaros",
            "Inseto": "Maníaco por Insetos",
            "Terra": "Campista",
            "Dragão": "Domador de Dragões",
            "Elétrico": "Engenheiro",
            "Fogo": "Piromaníaco",
            "Grama": "Jardineiro",
            "Lutador": "Artista Marcial",
            "Pedra": "Alpinista",
            "Fantasma": "Místico",
            "Aço": "Metalúrgico",
            "Psíquico": "Psíquico",
            "Água": "Nadador",
            "Fada": "Encantador",
            "Sombrio": "Sombrio",
            "Venenoso": "Alquimista",
            "Normal": "Jogador de Equipe",
            "Gelo": "Esquiador"
        }
        if tipo in tipo_map and tipo_map[tipo] == espec:
            return 1
        return 0

    def render_pokes():
        lista_pokemons_view.controls.clear()
        for i, p in enumerate(stats["pokemons"]):
            # Garantir que o Pokémon tem todos os campos
            if "tipo" not in p:
                p["tipo"] = "Normal"
            if "natureza" not in p:
                p["natureza"] = "Nenhuma"
            if "habilidade" not in p:
                p["habilidade"] = ""
            if "nivel" not in p:
                p["nivel"] = "1"
            if "sr" not in p:
                p["sr"] = "1"
            if "lealdade" not in p:
                p["lealdade"] = 0

            try:
                cur, mx = int(p["hp"]), int(p["hp_max"])
            except:
                cur, mx = 20, 20
            pct = cur / mx if mx > 0 else 0

            # Calcular bônus do treinador
            bonus_treinador = get_bonus_tipo_pokemon(p["tipo"])

            # Calcular bônus de lealdade
            lealdade_nivel = int(p.get("lealdade", 0))
            lealdade_info = LEALDADE_NIVEIS[lealdade_nivel]
            nivel_poke = int(p.get("nivel", 1))
            bonus_hp_lealdade = 0
            if lealdade_nivel == 2:
                bonus_hp_lealdade = nivel_poke // 2
            elif lealdade_nivel == 3:
                bonus_hp_lealdade = nivel_poke

            tipo_colors = CORES_TIPO_POKEMON

            def update_poke_hp(e, idx=i, delta=0):
                pk = stats["pokemons"][idx]
                try:
                    pk["hp"] = str(max(0, min(int(pk["hp"]) + delta, int(pk["hp_max"]))))
                    salvar()
                    render_pokes()
                except:
                    pass

            def edit_poke(e, idx=i):
                """Abre diálogo para editar Pokémon"""
                poke = stats["pokemons"][idx]

                dlg_nome = ft.TextField(value=poke["nome"], label="Nome", border_color=COR_PRIMARIA)
                dlg_nivel = ft.TextField(value=poke.get("nivel", "1"), label="Nível", width=100, border_color=COR_PRIMARIA)
                dlg_sr = ft.TextField(value=poke.get("sr", "1"), label="SR", width=100, border_color=COR_SECUNDARIA)
                dlg_hp_max = ft.TextField(value=poke["hp_max"], label="HP Máximo", width=100, border_color=COR_PRIMARIA)
                dlg_tipo = ft.Dropdown(
                    options=[ft.dropdown.Option(t) for t in TIPOS_POKEMON],
                    value=poke.get("tipo", "Normal"),
                    label="Tipo",
                    border_color=COR_ACENTO
                )
                dlg_natureza = ft.Dropdown(
                    options=[ft.dropdown.Option(n) for n in NATUREZAS_POKEMON.keys()],
                    value=poke.get("natureza", "Nenhuma"),
                    label="Natureza",
                    border_color=COR_SECUNDARIA
                )
                dlg_habilidade = ft.TextField(
                    value=poke.get("habilidade", ""),
                    label="Habilidade/Passiva",
                    multiline=True,
                    min_lines=2,
                    border_color=COR_PRIMARIA
                )
                dlg_lealdade = ft.Dropdown(
                    options=[
                        ft.dropdown.Option(
                            key=str(lvl),
                            text=f"{LEALDADE_NIVEIS[lvl]['emoji']} {LEALDADE_NIVEIS[lvl]['nome']} ({lvl:+d})" if lvl != 0 else f"{LEALDADE_NIVEIS[lvl]['emoji']} {LEALDADE_NIVEIS[lvl]['nome']}"
                        )
                        for lvl in range(-3, 4)
                    ],
                    value=str(poke.get("lealdade", 0)),
                    label="Lealdade",
                    border_color=COR_ACENTO
                )

                def salvar_edicao(e):
                    poke["nome"] = dlg_nome.value
                    poke["nivel"] = dlg_nivel.value
                    poke["sr"] = dlg_sr.value
                    poke["hp_max"] = dlg_hp_max.value
                    poke["tipo"] = dlg_tipo.value
                    poke["natureza"] = dlg_natureza.value
                    poke["habilidade"] = dlg_habilidade.value
                    poke["lealdade"] = int(dlg_lealdade.value)
                    salvar()
                    render_pokes()
                    dialog.open = False
                    page.update()

                dialog = ft.AlertDialog(
                    title=ft.Text(f"✏️ Editar: {poke['nome']}", color=COR_PRIMARIA),
                    content=ft.Container(
                        content=ft.Column([
                            dlg_nome,
                            ft.Row([dlg_nivel, dlg_sr, dlg_hp_max], spacing=10),
                            dlg_tipo,
                            dlg_natureza,
                            ft.Text(
                                NATUREZAS_POKEMON.get(dlg_natureza.value, {}).get("desc", ""),
                                size=10,
                                color="grey",
                                italic=True
                            ),
                            dlg_lealdade,
                            ft.Text(
                                LEALDADE_NIVEIS.get(int(dlg_lealdade.value or 0), LEALDADE_NIVEIS[0])["desc"],
                                size=10,
                                color="grey",
                                italic=True
                            ),
                            dlg_habilidade
                        ], tight=True, scroll=ft.ScrollMode.AUTO),
                        width=400,
                        height=550
                    ),
                    actions=[
                        ft.TextButton("Cancelar", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
                        ft.Button("Salvar", on_click=salvar_edicao, bgcolor=COR_PRIMARIA, color="black")
                    ]
                )
                page.overlay.append(dialog)
                dialog.open = True
                page.update()

            def rolar_teste_pokemon(e, idx=i):
                """Rola d20 + bônus do treinador para teste de perícia do Pokémon"""
                d20 = random.randint(1, 20)
                bonus = get_bonus_tipo_pokemon(stats["pokemons"][idx]["tipo"])
                total = d20 + bonus

                if d20 == 20:
                    msg = f"🎯 {p['nome']}: {d20}+{bonus} = {total} (CRÍTICO!)"
                    color = COR_PRIMARIA
                elif d20 == 1:
                    msg = f"💥 {p['nome']}: {d20}+{bonus} = {total} (FALHA!)"
                    color = "red"
                else:
                    msg = f"🎲 {p['nome']}: {d20}+{bonus} = {total}"
                    color = COR_ACENTO

                adicionar_historico(f"Pokémon {p['nome']}", msg)
                atualizar_historico_display()
                # Criar snackbar temporário
                page.overlay.append(ft.SnackBar(
                    content=ft.Text(msg, color=color, weight="bold"),
                    bgcolor=COR_CARD,
                    duration=3000
                ))
                page.overlay[-1].open = True
                page.update()

            card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CATCHING_POKEMON, color=tipo_colors.get(p["tipo"], COR_PRIMARIA), size=24),
                        ft.Column([
                            ft.Text(p["nome"], weight="bold", size=15),
                            ft.Row([
                                ft.Text(f"Nv.{p.get('nivel', '1')}", size=10, color="grey"),
                                ft.Text(f"SR {p.get('sr', '1')}", size=10, color=COR_ACENTO),
                                ft.Container(
                                    content=ft.Text(p["tipo"], size=9, color="white", weight="bold"),
                                    bgcolor=tipo_colors.get(p["tipo"], "#888"),
                                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                    border_radius=5
                                )
                            ], spacing=5)
                        ], spacing=2, expand=True),
                        ft.Row([
                            ft.IconButton(ft.Icons.CASINO, icon_size=20, icon_color=COR_ACENTO,
                                          on_click=lambda e, idx=i: rolar_teste_pokemon(e, idx),
                                          tooltip="Rolar teste de perícia"),
                            ft.IconButton(ft.Icons.EDIT, icon_size=20, icon_color=COR_SECUNDARIA,
                                          on_click=lambda e, idx=i: edit_poke(e, idx),
                                          tooltip="Editar Pokémon"),
                            ft.IconButton(ft.Icons.DELETE, icon_color="red", icon_size=20,
                                          on_click=lambda e, idx=i: del_poke(idx),
                                          tooltip="Remover")
                        ], spacing=0)
                    ]),
                    ft.Container(
                        content=ft.Row([
                            ft.Text(lealdade_info["emoji"], size=14),
                            ft.Text(lealdade_info["nome"], size=10, color=lealdade_info["cor"], weight="bold"),
                            ft.Text(f"Saves {lealdade_info['efeito_saves']:+d}" if lealdade_info['efeito_saves'] != 0 else "Saves +0",
                                    size=9, color="grey")
                        ], spacing=4),
                        bgcolor="#1a1a1a",
                        padding=ft.padding.symmetric(horizontal=6, vertical=3),
                        border_radius=5
                    ),
                    ft.Text(p["natureza"] + " " + NATUREZAS_POKEMON[p["natureza"]]["desc"],
                            size=10, color="grey", italic=True, no_wrap=False) if p["natureza"] != "Nenhuma" else ft.Container(),
                    ft.Text(f"⚡ {p['habilidade']}", size=10, color=COR_PRIMARIA, no_wrap=False) if p["habilidade"] else ft.Container(),
                    ft.Row([
                        ft.Text(f"❤️ {p['hp']}/{p['hp_max']} HP", size=11, color="grey", weight="bold"),
                        ft.Text(f"(+{bonus_hp_lealdade} Lealdade)" if bonus_hp_lealdade > 0 else "",
                                size=9, color=lealdade_info["cor"]) if bonus_hp_lealdade > 0 else ft.Container(),
                        ft.Text(f"+{bonus_treinador} bônus", size=10, color=COR_PRIMARIA,
                                weight="bold") if bonus_treinador > 0 else ft.Container()
                    ], spacing=10),
                    ft.ProgressBar(value=pct, color=tipo_colors.get(p["tipo"], COR_PRIMARIA), bgcolor="#333", height=6,
                                   border_radius=3),
                    # Mostrar informações específicas de lealdade
                    ft.Text(f"⚠️ {lealdade_info['efeito_moves']}", size=9, color="red", italic=True, no_wrap=False) if lealdade_nivel < 0 else ft.Container(),
                    ft.Text(f"✨ +1 Proficiência em 1 perícia adicional", size=9, color=lealdade_info["cor"], italic=True, no_wrap=False) if lealdade_nivel == 2 else ft.Container(),
                    ft.Text(f"✨ +1 Proficiência em 2 perícias adicionais", size=9, color=lealdade_info["cor"], italic=True, no_wrap=False) if lealdade_nivel == 3 else ft.Container(),
                    ft.Row([
                        ft.IconButton(ft.Icons.REMOVE, icon_size=18, bgcolor=COR_CARD_ALT,
                                      on_click=lambda e, idx=i: update_poke_hp(e, idx, -1), tooltip="Reduzir HP"),
                        ft.IconButton(ft.Icons.ADD, icon_size=18, bgcolor=COR_CARD_ALT,
                                      on_click=lambda e, idx=i: update_poke_hp(e, idx, 1), tooltip="Aumentar HP"),
                        ft.Button("Curar", on_click=lambda e, idx=i: (
                            stats["pokemons"][idx].__setitem__("hp", stats["pokemons"][idx]["hp_max"]),
                            salvar(),
                            render_pokes()
                        ), bgcolor=COR_SECUNDARIA, color="black", height=35, tooltip="Restaurar HP máximo")
                    ], alignment="center", spacing=10)
                ], spacing=6),
                bgcolor=COR_CARD,
                padding=12,
                border_radius=10,
                border=ft.border.all(2, tipo_colors.get(p["tipo"], COR_PRIMARIA))
            )
            lista_pokemons_view.controls.append(card)
        page.update()

    def add_poke(e):
        if novo_poke_nome.value:
            stats["pokemons"].append({
                "nome": novo_poke_nome.value,
                "hp": "20",
                "hp_max": "20",
                "tipo": "Normal",
                "natureza": "Nenhuma",
                "habilidade": "",
                "nivel": "1",
                "sr": "1",
                "lealdade": 0
            })
            novo_poke_nome.value = ""
            salvar()
            render_pokes()

    def del_poke(idx):
        stats["pokemons"].pop(idx)
        salvar()
        render_pokes()

    # --- DEFINIÇÃO FALTANTE CORRIGIDA AQUI ---
    tela_pokemon = ft.Column([
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CATCHING_POKEMON, color=COR_PRIMARIA, size=24),
                    ft.Text("⚡ Sua Equipe Pokémon", size=16, weight="bold", color=COR_PRIMARIA),
                ]),
                ft.Text(f"Pokéslots: {len(stats['pokemons'])}/{ui_pokeslots.value if 'ui_pokeslots' in locals() else '3'}",
                        size=11, color="grey"),
                ft.Divider(color="grey", height=10),
                ft.Row([
                    novo_poke_nome,
                    ft.IconButton(ft.Icons.ADD_CIRCLE, on_click=add_poke, icon_color=COR_PRIMARIA, icon_size=30,
                                  tooltip="Adicionar Pokémon")
                ]),
                ft.Text("💡 Clique em EDITAR para configurar tipo, natureza e habilidade", size=10, color="grey",
                        italic=True)
            ], spacing=5),
            padding=12,
            bgcolor=COR_CARD,
            border_radius=10,
            margin=10
        ),
        lista_pokemons_view
    ])

    # --- TALENTOS ---
    lista_talentos_view = ft.ListView(expand=True, spacing=5, padding=10)

    def render_talentos():
        """Renderiza lista de talentos do treinador"""
        lista_talentos_view.controls.clear()
        if "talentos" not in stats:
            stats["talentos"] = []

        for i, talento_nome in enumerate(stats["talentos"]):
            if talento_nome in TALENTOS:
                tal_info = TALENTOS[talento_nome]
                card = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.STAR, color=COR_ACENTO, size=18),
                            ft.Text(talento_nome, weight="bold", size=13, expand=True),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                icon_color="red",
                                icon_size=18,
                                on_click=lambda e, idx=i: remover_talento(idx),
                                tooltip="Remover talento"
                            )
                        ]),
                        ft.Text(f"Tipo: {tal_info['tipo']}", size=10, color="grey", no_wrap=False),
                        ft.Text(f"Pre-req: {tal_info['prereq']}" if tal_info['prereq'] else "Sem prerequisitos", size=9, color="grey", italic=True, no_wrap=False),
                        ft.Text(tal_info["desc"], size=10, color=COR_SECUNDARIA, no_wrap=False)
                    ], spacing=3),
                    bgcolor=COR_CARD,
                    padding=10,
                    border_radius=8,
                    border=ft.Border(left=ft.BorderSide(3, COR_ACENTO))
                )
                lista_talentos_view.controls.append(card)
        page.update()

    def adicionar_talento(e):
        """Dialogo para adicionar talento"""
        talento_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(nome) for nome in sorted(TALENTOS.keys())],
            label="Selecione um Talento",
            border_color=COR_ACENTO,
            width=350
        )

        def mostrar_info(e):
            if talento_dropdown.value and talento_dropdown.value in TALENTOS:
                info = TALENTOS[talento_dropdown.value]
                info_text.value = f"Tipo: {info['tipo']}\nPre-req: {info['prereq'] or 'Nenhum'}\n\n{info['desc']}"
            else:
                info_text.value = "Selecione um talento para ver detalhes"
            page.update()

        talento_dropdown.on_change = mostrar_info

        info_text = ft.Text("Selecione um talento para ver detalhes", size=10, color="grey", no_wrap=False)

        def salvar_talento(e):
            if talento_dropdown.value:
                if talento_dropdown.value not in stats["talentos"]:
                    stats["talentos"].append(talento_dropdown.value)
                    salvar()
                    render_talentos()
                    dialog.open = False
                    page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Adicionar Talento", color=COR_ACENTO),
            content=ft.Container(
                content=ft.Column([
                    talento_dropdown,
                    ft.Divider(color="grey"),
                    info_text
                ], tight=True, scroll=ft.ScrollMode.AUTO),
                width=400,
                height=300
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
                ft.Button("Adicionar", on_click=salvar_talento, bgcolor=COR_ACENTO, color="black")
            ]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def remover_talento(idx):
        stats["talentos"].pop(idx)
        salvar()
        render_talentos()

    card_talentos = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.STAR, color=COR_ACENTO, size=24),
                ft.Text("Talentos", weight="bold", size=16),
                ft.IconButton(
                    ft.Icons.ADD,
                    icon_color=COR_ACENTO,
                    on_click=adicionar_talento,
                    tooltip="Adicionar Talento"
                )
            ], alignment="space_between"),
            ft.Container(
                content=lista_talentos_view,
                height=200
            )
        ]),
        bgcolor=COR_CARD,
        padding=15,
        border_radius=10,
        margin=10
    )

    # Tela de Regras
    tela_regras = ft.Container(
        content=ft.ListView([
            ft.Container(
                content=ft.Markdown(REGRAS_RESUMO, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB),
                bgcolor=COR_CARD,
                padding=12,
                border_radius=10,
                margin=ft.Margin(bottom=10),
                border=ft.border.all(1, COR_PRIMARIA)
            ),
            ft.Markdown(
                REGRAS_TEXTO,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                code_theme="atom-one-dark"
            )
        ], padding=15),
        expand=True
    )

    # --- NAVEGAÇÃO ---
    tela_treinador = ft.Column([
        header,
        ft.Container(height=5),  # Espaçamento
        card_regiao,
        card_origem_jornada,
        card_espec,
        card_classe,
        ft.Divider(color="grey", height=20),
        card_criacao,
        ft.Divider(color="grey", height=20),
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.SPORTS_MMA, color=COR_PRIMARIA, size=20),
                    ft.Text("💪 Atributos", size=14, weight="bold", color=COR_PRIMARIA)
                ], alignment="center"),
                ft.Container(height=5),
                grid_stats
            ]),
            padding=10,
            bgcolor=COR_FUNDO,
            border_radius=10
        ),
        painel_combate,
        card_talentos,
        ft.Container(height=20)  # Espaço no final
    ], scroll=ft.ScrollMode.AUTO, spacing=5)

    conteudo = ft.Container(content=tela_treinador, expand=True)

    def mudar_tela(e):
        idx = e.control.selected_index
        if idx == 0:
            conteudo.content = tela_treinador
        elif idx == 1:
            conteudo.content = tela_pericias
        elif idx == 2:
            conteudo.content = tela_mochila
        elif idx == 3:
            conteudo.content = tela_pokemon
        elif idx == 4:
            conteudo.content = tela_regras
        page.update()

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Treinador"),
            ft.NavigationBarDestination(icon=ft.Icons.EMOJI_EVENTS, label="Perícias"),
            ft.NavigationBarDestination(icon=ft.Icons.BACKPACK, label="Mochila"),
            ft.NavigationBarDestination(icon=ft.Icons.CATCHING_POKEMON, label="Equipe"),
            ft.NavigationBarDestination(icon=ft.Icons.MENU_BOOK, label="Regras"),
        ],
        on_change=mudar_tela,
        bgcolor=COR_CARD,
        indicator_color=COR_PRIMARIA,
        height=65
    )

    # Layout com navegação fixada no bottom
    page.add(
        ft.Column([
            conteudo,
        ], expand=True, scroll=ft.ScrollMode.AUTO),
    )
    page.bottom_appbar = ft.BottomAppBar(
        content=nav_bar,
        bgcolor=COR_FUNDO,
        padding=0
    )
    atualizar_tudo()
    render_pokes()


ft.run(main)