"""
Constantes e dados do jogo para Ficha RPG Pokémon.
"""
import textwrap

# Configurações
ARQUIVO_SAVE = "ficha_save.json"
ARQUIVO_BACKUP = "ficha_save.backup.json"
VERSAO_SAVE = 2
POINT_BUY_TOTAL = 27
POINT_BUY_MIN = 8
POINT_BUY_MAX = 15

# Valores padrão da ficha
def get_stats_default():
    return {
        "nome": "Treinador", "nivel": "1", "classe": "", "regiao_origem": "", "origem_jornada": "",
        "especializacao": "", "especializacao_2": "", "especializacao_3": "", "hp_atual": "10", "hp_max": "10", "deslocamento": "9m",
        "pokedollars": "0",
        "for": "8", "des": "8", "con": "8", "int": "8", "sab": "8", "car": "8",
        "pokebolas": "5x Pokébolas", "itens_chave": "Licença de Treinador\nPokédex",
        "consumiveis": "1x Poção", "pacote_aventura": "Aventureiro",
        "pokemons": [],
        "pericias_proficientes": ["Adestrar Animais"],
        "talentos": [],
        "tm_escolhido": "",
        "espec_pericia_sombrio": "Furtividade",
        "espec_pericia_alquimista": "Medicina",
        "espec_pericia_esquiador": "Atuação",
        "espec_atributo_artista_marcial": "for",
        "espec_atributo_alpinista": "for",
        "espec_atributo_metalurgico": "for",
        "espec_atributo_jogador_de_equipe": "car"
    }

ESPECIALIZACOES = {
    "Nenhuma": {"desc": "Sem bônus.", "pericias": [], "atributo": None},
    "Guardião dos Pássaros": {"desc": "+1 testes Pokémon Voador. Visão aguçada a longas distâncias.", "pericias": ["Percepção"], "atributo": None},
    "Maníaco por Insetos": {"desc": "+1 testes Pokémon Inseto. Detectar insetos com vantagem.", "pericias": ["Natureza"], "atributo": None},
    "Campista": {"desc": "+1 testes Pokémon Terra. Acampamento rápido com vantagem.", "pericias": ["Sobrevivência"], "atributo": None},
    "Domador de Dragões": {"desc": "+1 testes Pokémon Dragão. Sentir dragões (100m).", "pericias": [], "atributo": "sab"},
    "Engenheiro": {"desc": "+1 testes Pokémon Elétrico. Analisar máquinas com vantagem.", "pericias": [], "atributo": "int"},
    "Piromaníaco": {"desc": "+1 testes Pokémon Fogo. Isqueiro infinito.", "pericias": [], "atributo": "con"},
    "Jardineiro": {"desc": "+1 testes Pokémon Grama. Identificar plantas com vantagem.", "pericias": ["Natureza"], "atributo": None},
    "Artista Marcial": {"desc": "+1 FOR, DES ou CON. +1 testes Pokémon Lutador. Acrobacia com vantagem.", "pericias": [], "atributo_opcoes": ["for", "des", "con"]},
    "Alpinista": {"desc": "+1 FOR, DES ou CON. +1 testes Pokémon Pedra. Escalada fácil em terrenos difíceis.", "pericias": [], "atributo_opcoes": ["for", "des", "con"]},
    "Místico": {"desc": "+1 testes Pokémon Fantasma. Sentir sobrenatural (30m).", "pericias": ["Arcanismo"], "atributo": None},
    "Metalúrgico": {"desc": "+1 FOR ou CON. +1 testes Pokémon Aço. Reduzir dano físico (1d4+CON).", "pericias": [], "atributo_opcoes": ["for", "con"]},
    "Psíquico": {"desc": "+1 testes Pokémon Psíquico. Telepatia com um Pokémon.", "pericias": [], "atributo": "int"},
    "Nadador": {"desc": "+1 testes Pokémon Água. Velocidade de natação igual ao movimento.", "pericias": [], "atributo": "con"},
    "Encantador": {"desc": "+1 testes Pokémon Fada. Vantagem em Persuasão com amigáveis.", "pericias": [], "atributo": "car"},
    "Sombrio": {"desc": "+1 testes Pokémon Sombrio. Escolha: Enganação OU Furtividade.", "pericias_opcoes": ["Enganação", "Furtividade"], "atributo": None},
    "Alquimista": {"desc": "+1 testes Pokémon Venenoso. Criar poção simples (1/descanso). Escolha: Medicina OU Enganação.", "pericias_opcoes": ["Medicina", "Enganação"], "atributo": None},
    "Jogador de Equipe": {"desc": "+1 em qualquer atributo. +1 testes Pokémon Normal. Inspirar aliado (+1d4, 1/descanso).", "pericias": [], "atributo_opcoes": ["for", "des", "con", "int", "sab", "car"]},
    "Esquiador": {"desc": "+1 testes Pokémon Gelo. Mover em gelo com vantagem. Escolha: Atuação OU Persuasão.", "pericias_opcoes": ["Atuação", "Persuasão"], "atributo": None}
}

REGIOES_ORIGEM = {
    "Nenhuma": {"desc": "Sem modificadores.", "bonus": {}, "pericia": None, "habilidade": ""},
    "Kanto": {"desc": "+1 em dois atributos OU +2 em um. Forje seu caminho. Perícia: Investigação. Habilidade: Comece com 1 Talento.", "bonus": {}, "pericia": "Investigação", "habilidade": "Minha Hora de Brilhar: Escolha um Talento para começar o jogo."},
    "Johto": {"desc": "+2 INT, +1 FOR. Imerso na tradição. Perícia: História. Habilidade: Caminho da Serenidade (reroll SAB/CAR saves).", "bonus": {"int": 2, "for": 1}, "pericia": "História", "habilidade": "Caminho da Serenidade: Reroll falhas em testes de resistência de SAB ou CAR (1x/descanso)."},
    "Hoenn": {"desc": "+2 SAB, +1 INT. Viu de tudo. Perícia: Sobrevivência. Habilidade: Escolha ambiente (Costa/Deserto/Floresta/Montanha).", "bonus": {"sab": 2, "int": 1}, "pericia": "Sobrevivência", "habilidade": "Nada Como o Nosso Lar: Escolha Costa (nadar), Deserto (calor), Floresta (esconder), ou Montanha (escalar 3m)."},
    "Sinnoh": {"desc": "+2 CON, +1 FOR. Resistente. Perícia: Atletismo. Habilidade: Proficiência em testes de CON e +2 CA.", "bonus": {"con": 2, "for": 1}, "pericia": "Atletismo", "habilidade": "Corpo e Mente: Proficiência em testes de resistência de CON e +2 na CA."},
    "Unova": {"desc": "+2 DES, +1 SAB. Ritmo acelerado. Perícia: Intuição. Habilidade: Proficiência em 2 perícias à escolha.", "bonus": {"des": 2, "sab": 1}, "pericia": "Intuição", "habilidade": "Pessoa de Muitos Talentos: Ganhe proficiência em 2 perícias de sua escolha."},
    "Kalos": {"desc": "+2 CAR, +1 INT. C'est la vie. Perícia: Persuasão. Habilidade: Reroll 1-2 em perícias/resistências.", "bonus": {"car": 2, "int": 1}, "pericia": "Persuasão", "habilidade": "Bon Chance: Reroll resultados 1-2 em testes de perícia ou resistência."},
    "Alola": {"desc": "+2 INT, +1 CAR. Cultura espiritual. Perícia: Natureza. Habilidade: Vantagem para entender Pokémon.", "bonus": {"int": 2, "car": 1}, "pericia": "Natureza", "habilidade": "Uma Conexão Diferente: Vantagem em testes para entender o que Pokémon estão expressando."},
    "Galar": {"desc": "+2 FOR/DES, +1 DES/FOR (escolha). Boa briga. Perícia: Intimidação. Habilidade: Reação reduz dano (1d12+CON).", "bonus": {"for": 2, "des": 1}, "pericia": "Intimidação", "habilidade": "Minha Mãe Bate Mais Forte: Reação para reduzir dano em 1d12+CON (1x/descanso)."}
}

ORIGENS_JORNADA = {
    "Nenhuma": {"titulo": "", "desc": "Sem bônus.", "pericias": [], "equip": "", "hab_nome": "", "hab_desc": ""},
    "Atleta": {"titulo": "O Forte", "desc": "Esportes são o seu ponto forte. Você conhece o terreno como a palma da mão.", "pericias": ["Atletismo", "Sobrevivência"], "equip": "Itens X com valor total de até ₽1.200", "hab_nome": "Espírito Competitivo", "hab_desc": "• Role 2x em Atletismo (correr, escalar, nadar) e escolha o melhor (1/descanso).\n• Ignora penalidades de terreno difícil natural (lama, areia, neve)."},
    "Conhecedor": {"titulo": "O Tranquilo", "desc": "A felicidade e o bem-estar dos Pokémon são mais importantes que batalhas.", "pericias": ["Medicina", "Atuação"], "equip": "Itens de cura com valor total de até ₽1.200", "hab_nome": "Cuidado Natural", "hab_desc": "• Role 2x em Medicina e escolha o melhor (1/descanso).\n• Gastar 10min cuidando restaura PV = (Mod SAB + Nível) e dá vantagem vs Veneno por 24h (1/descanso longo)."},
    "Nobre": {"titulo": "O Esnobe", "desc": "Acostumado ao luxo, você está pronto para ver aonde a estrada o levará.", "pericias": ["História", "Persuasão"], "equip": "Um Item Segurado (Held Item) de até ₽1.200. Começa com Dinheiro Máximo.", "hab_nome": "Presença Aristocrática", "hab_desc": "• Role 2x em Persuasão com autoridades/elite (1/descanso).\n• Discurso de 1min: Até 6 ouvintes ganham vantagem em 1 perícia na próxima hora (1/descanso longo).\n• Encontra recursos de luxo facilmente."},
    "Encrenqueiro": {"titulo": "O Afiado", "desc": "Você sempre parece se meter em confusão. Aprendeu a se virar.", "pericias": ["Prestidigitação", "Furtividade"], "equip": "Uma Pedra de Evolução", "hab_nome": "Fuga Rápida", "hab_desc": "• Role 2x em Enganação ou Prestidigitação para despistar/truques (1/descanso).\n• Vantagem em Prestidigitação para abrir portas/consertar algo simples (1/descanso longo).\n• Conhece rotas seguras, atalhos e áreas menos movimentadas."},
    "Amigo dos Pokémon": {"titulo": "O Selvagem", "desc": "Você é mais próximo da população local de Pokémon do que dos seus colegas.", "pericias": ["Sobrevivência", "Natureza"], "equip": "Berries com valor total de até ₽1.200", "hab_nome": "Andarilho Natural", "hab_desc": "• Memória excelente para mapas e geografia.\n• Encontra comida/água para 6 pessoas na natureza.\n• Pokémon selvagens neutros são amistosos a menos que provocados."},
    "Rival": {"titulo": "O Desafiador", "desc": "Você coloca tudo de si em derrotar seu rival e conquistar emblemas.", "pericias": ["Percepção", "Intimidação"], "equip": "Pokébolas com valor total de até ₽1.200", "hab_nome": "Espírito de Superação", "hab_desc": "• Ao falhar numa meta/perder, ganha vantagem no próximo teste relacionado.\n• Se perder batalha, vantagem no 1º ataque da próxima.\n• Vitórias consecutivas vs Treinadores dão +1 cumulativo (max +3) na Iniciativa."},
    "Estudioso": {"titulo": "O Cérebro", "desc": "Você passou mais tempo lendo sobre Pokémon do que interagindo com eles.", "pericias": ["Investigação", "História"], "equip": "Um TM da lista (escolha abaixo).", "hab_nome": "Análise Estratégica", "hab_desc": "• Ação Bônus: Teste de Investigação (CD 10+Nível Alvo) para descobrir Tipos e Fraquezas/Resistências (Usos: 1+INT mod).\n• 1/descanso longo: Concede vantagem em ataque ou resistência contra o alvo analisado para você ou aliado."}
}

LISTA_TMS = [
    "TM01 - Work Up", "TM04 - Calm Mind", "TM05 - Roar", "TM07 - Hail", "TM11 - Sunny Day",
    "TM12 - Taunt", "TM16 - Light Screen", "TM18 - Rain Dance", "TM20 - Safeguard", "TM32 - Double Team",
    "TM33 - Reflect", "TM37 - Sandstorm", "TM41 - Torment", "TM45 - Attract", "TM63 - Embargo",
    "TM69 - Rock Polish", "TM70 - Aurora Veil", "TM77 - Psych Up", "TM90 - Substitute", "TM92 - Trick Room"
]

CLASSES_TREINADOR = {
    "Nenhuma": {
        "desc": "Escolha uma classe no nível 2.",
        "hab_nome": "",
        "hab_desc": ""
    },
    "Treinador Ás": {
        "desc": "Seu objetivo é se tornar um dos Treinadores mais fortes do mundo, e você se destaca em batalha.",
        "hab_nome": "Habilidades de Classe",
        "hab_desc": "• Nv 2: Todos os seus Pokémon recebem +1 em rolagens de ataque e dano.\n• Mestre de Batalha (Nv 5): Dados de batalha (d6) = 1 + mod SAB (mín 1). Atribua um dado a um Pokémon para +1 rolagem de ataque ou dano. Repõe em descanso longo.\n• Potencial Máximo (Nv 9): Seus Pokémon ganham +3m deslocamento. +1d6 na iniciativa. Usos = 1 + mod SAB (mín 1) por descanso longo.\n• Troca Rápida (Nv 15): Recolher/liberar Pokémon como ação bônus. Usos = 1 + mod SAB (mín 1) por descanso longo. Pokémon não pode ser trocado até o fim do 1º turno (exceto Volt Switch, U-Turn, etc)."
    },
    "Versátil": {
        "desc": "Você escolhe experimentar uma variedade de habilidades para cuidar de seus Pokémon.",
        "hab_nome": "Habilidades de Classe",
        "hab_desc": "• Nv 2: Selecione uma especialização adicional e duas novas proficiências em perícias.\n• Apoiador (Nv 5): Dados de habilidade (d6) = 1 + mod SAB (mín 1). Adicione a um teste de perícia ou resistência de Pokémon. Repõe em descanso longo.\n• Muitas Faces (Nv 9): Escolha dois recursos de Nv 2 ou um de Nv 5/9 de qualquer outro caminho.\n• Troca de Habilidade (Nv 15): A cada descanso longo, escolha um talento para todos os seus Pokémon conhecerem naquele dia."
    },
    "Mentor Pokémon": {
        "desc": "Você sabe como motivar seus aliados durante um combate.",
        "hab_nome": "Habilidade de Classe",
        "hab_desc": "• Nv 2: Uma vez por descanso curto, use ação bônus para impulsionar todos Pokémon aliados com palavras inspiradoras. Até seu próximo turno: adicione mod CAR (mín 1) a todas as rolagens de ataque OU rolagens de dano OU CA de todos Pokémon aliados."
    },
    "Pokéchef": {
        "desc": "Você se destaca em criar refeições para seus Pokémon, aparentemente do nada.",
        "hab_nome": "Habilidades de Classe",
        "hab_desc": "• Nv 5: \"Guloseima Comestível\" — 2d4+2 HP temporários (ação para dar). Usos = 1 + mod SAB. Repõe em descanso longo. Pode ser item segurável, ativável em combate com ação livre.\n• Tutor Capacitado (Nv 9): TMs podem ser usadas 2x antes de quebrar. Guloseima = 2d8+4 HP.\n• Tutor Mestre (Nv 15): Guloseima = 4d6+6 HP. Ao consumir: Inspiração + 1d6 para perícia ou resistência. 1x/descanso longo: ensinar Tutor Move a um Pokémon (1h de prática)."
    },
    "Enfermeiro": {
        "desc": "Você tem um coração puro e espírito de cura. Quer o melhor para seus Pokémon.",
        "hab_nome": "Habilidades de Classe",
        "hab_desc": "• Nv 2: Proficiência em Medicina (ou especialista se já proficiente). A cada descanso longo ou Centro Pokémon: até 6 Pokémon recebem HP temporário = seu nível.\n• Coração Puro (Nv 5): Reserva de cura = nível x 5. Ação: toque criatura voluntária e restaure HP da reserva. Reabastece em descanso longo.\n• Espírito de Cura (Nv 9): Curativos em Pokémon: role 2x, pegue o maior. 2x/descanso longo: curar 1 HP de Pokémon incapacitado (fora de combate).\n• Alegria (Nv 15): 1x/descanso longo, 1h: efeito como Centro Pokémon. Até 6 Pokémon totalmente curados de ferimentos e condições."
    },
    "Pesquisador": {
        "desc": "Você deseja aprender mais sobre Pokémon e os segredos que eles guardam.",
        "hab_nome": "Habilidades de Classe",
        "hab_desc": "• Nv 2: Escolha Arcanismo, História, Investigação, Natureza ou Religião (proficiente ou especialista). Pokédex revela onde encontrar espécies \"vistas\". Pokémon inicial aprende 1 Move do próximo nível.\n• Analista (Nv 5): Ação bônus, Investigação CD 12 para analisar Pokémon (nível, habilidade, Natureza). Aliados +2 CA e saves vs alvo até fim do combate. 1x/descanso curto.\n• Especialista em Evolução (Nv 9): Ao evoluir, 2 pontos de evolução → 1 talento. Aliado sofre dano de Move: se falhou save, vantagem no próximo vs mesmo Move; se acerto, próximo ataque desse Move com desvantagem. Usos = 1 + mod INT (mín 1)/descanso longo.\n• Professor (Nv 15): Ação bônus: revelar pontos fracos (atributo mais forte e mais fraco). Aliados +2 em ataque, dano e margem de crítico vs alvo. 1x/descanso curto."
    },
    "Colecionador Pokémon": {
        "desc": "Seu fascínio por todos os tipos de Pokémon impulsiona sua necessidade de colecionar todos.",
        "hab_nome": "Habilidades de Classe",
        "hab_desc": "• Nv 2: Especialista em Adestrar Animais (dobra proficiência).\n• Tenho que Pegar Todos (Nv 5): 1x/descanso longo, Adestrar Animais com vantagem em captura. Ao falhar captura, d4: 4 = recupera Pokébola.\n• Especialista em Captura (Nv 9): Pokémon capturados curados e com HP cheio. +mod CAR em captura. A cada 40 espécies na Pokédex, role 2d6 para recompensas (1-6).\n• Ataques Disciplinados (Nv 15): Ao derrubar Pokémon, pode deixar com 1 HP. Ao capturar, reroll Natureza e escolha."
    },
    "Comandante": {
        "desc": "Você comanda seus Pokémon com punho de ferro, exigindo respeito e formando vínculo inquebrável.",
        "hab_nome": "Habilidades de Classe",
        "hab_desc": "• Nv 2: Pokémon inicial Lealdade \"Leal\". Novos Pokémon capturados +1 Lealdade.\n• Líder Inspirador (Nv 5): 10 min de inspiração: até 6 criaturas em 9m recebem HP temp = nível + mod CAR. 1x até descanso curto/longo.\n• Mostre-Me o Que Você Tem (Nv 9): Dano Dobrado: 1x/descanso longo, um Pokémon dobra dados de dano de um Move (antes de rolar). OU Move de Nível Superior: 1x/descanso curto, Pokémon usa Move 1 nível acima. Não combina ambos.\n• Somos Uma Equipe (Nv 15): Ação bônus, frase de comando. Até próximo turno, aliados em 18m: vantagem em ataques; alvos de Moves danosos: desvantagem em saves. Usos = 1 + mod CAR (mín 1)/descanso longo."
    },
    "Patrulheiro": {
        "desc": "Você se sente confortável na natureza e tem incrível respeito pelos Pokémon em habitat natural.",
        "hab_nome": "Habilidades de Classe",
        "hab_desc": "• Nv 2: Proficiência em Natureza e Sobrevivência (ou especialista). Velocidade +3m.\n• Conexão Profunda (Nv 5): Comunicar verbalmente com Pokémon. Informações sobre locais e Pokémon próximos. Tentar persuadir Pokémon a prestar favor.\n• Ligação Forte (Nv 9): Vínculos com até 2 Pokémon por descanso longo. Dobra proficiência em Adestrar Animais para acalmar/conquistar amizade. Assobio chama Pokémon em 200m.\n• Melhores Amigos (Nv 15): Dividir ações padrão com Pokémon. Ação padrão: +2 em acerto e dano do Pokémon."
    },
    "Capanga": {
        "desc": "Seja membro ou aspirante de uma equipe maligna, seu objetivo é derrubar treinadores certinhos e subir nos escalões.",
        "hab_nome": "Habilidades de Classe",
        "hab_desc": "• Nv 2: Reserva de Pontos Sombrios = seu nível. Sabotagem (reação): gaste Pontos Sombrios para diminuir resultado de ataque vs seu Pokémon (ataque falha se assim conseguir). Natural 20 não pode ser diminuído. Repõe em descanso longo.\n• Encrenca em Dobro (Nv 5): Vantagem Sombria: gaste 3 Pontos para vantagem em teste/ataque/save. Inimigo tira 1 natural vs seu Pokémon: recupera 1 Ponto, ataques vs ele com vantagem até próximo turno.\n• Renda-se Agora (Nv 9): Evasão Sinistra (reação): gaste 4 Pontos para adicionar resistência a Move danoso vs seu Pokémon (Vulnerável→Neutro, Neutro→Resistente, Resistente→Imune).\n• Prepare-se para Lutar (Nv 15): Copiar Meowth: gaste 5 Pontos para Pokémon usar Me First."
    },
    "Tático": {
        "desc": "Você tem olho para detalhes e conjunto único de habilidades para batalha.",
        "hab_nome": "Habilidades de Classe",
        "hab_desc": "• Nv 2: Pontos Táticos = nível de Treinador. Quando Pokémon recupera HP (item ou Move), +1d6 por Ponto Tático gasto. Repõe em descanso longo.\n• Golpe Direcionado (Nv 5): Gaste 2 Pontos para rolar dano 2x e pegar o maior.\n• Aumente Suas Defesas (Nv 9): Reação quando seu Pokémon é alvo de Move danoso: gaste Pontos para adicionar à CA ou save do Pokémon.\n• Não Dessa Vez (Nv 15): Após inimigo fazer save vs Move do seu Pokémon: aumente CD em até 5 (1 Ponto por aumento) para causar falha."
    },
    "Guru": {
        "desc": "Você e seus Pokémon estão conectados por mais do que Treinador e fera. Controle total de mente, corpo e espírito.",
        "hab_nome": "Habilidades de Classe",
        "hab_desc": "• Nv 2: Proficiência em Persuasão (ou especialista). Pokémon não controlados começam \"Indiferente\" em vez de \"Desleal\".\n• Mente (Nv 5): Pokémon em save de SAB adiciona seu mod SAB. Vs Confusão: rola 2x, pega melhor.\n• Corpo (Nv 9): Pokémon têm acesso a ambas habilidades passivas (e oculta se obtida). Talento Incansável custa 1 ASI em vez de 2.\n• Espírito (Nv 15): No início do turno, adicione mod SAB a todas rolagens de ataque OU dano do Pokémon até próximo turno. Usos = 1 + mod SAB (mín 1)/descanso longo. Pokémon podem agir de forma autônoma."
    },
    "Criador de Pokémon": {
        "desc": "Seu cuidado e delicadeza com ovos Pokémon fazem os pequenos nascerem mais rapidamente.",
        "hab_nome": "Habilidades de Classe",
        "hab_desc": "• Nv 2: Role 1d100 por hora para incubação. Ao chocar: role IVs (1d20 por atributo: 1=-2, 2-3=-1, 4-17=0, 18-19=+1, 20=+2).\n• Cuidado e Carinho (Nv 5): Incubação: role 2x, pegue maior. Ao chocar: 1d6 para definir atributo herdado. +2 em convencer Pokémon a se reproduzir. Reroll Natureza ao chocar.\n• Boa Genética (Nv 9): Ao chocar: escolha 1 IV máximo OU 1 talento. Brilhante: d100 91+ (1 pai) ou 86+ (ambos).\n• Mestre dos Traços (Nv 15): Ao chocar: escolha Gênero, Natureza e Habilidade. Substitua Egg Moves herdados livremente. Escolha IVs herdados entre pai e mãe."
    }
}

TALENTOS = {
    "Acrobata": {"tipo": "Treinador", "prereq": None, "desc": "+1 DES. Prof. Acrobacia (ou especialista se já proficiente). Ação bônus: teste DES (Acrobacia) CD 15 para terreno difícil não custar movimento extra até fim do turno."},
    "Adepto de Terreno": {"tipo": "Pokemon", "prereq": None, "desc": "Escolha um terreno: Costeiro, Pântano, Floresta, Ártico, Deserto, Pastagem, Colina, Montanha, Subaquático. +2 em jogadas de ataque neste terreno."},
    "Alerta": {"tipo": "Treinador", "prereq": None, "desc": "+5 iniciativa. Não pode ser surpreso enquanto consciente. Inimigos escondidos não ganham vantagem em ataques contra você."},
    "Atacante Bestial": {"tipo": "Pokemon", "prereq": None, "desc": "1x/turno: ao rolar dano de ataque corpo a corpo, pode rolar novamente e usar qualquer valor. Cumulativo com outras fontes de reroll."},
    "Atleta": {"tipo": "Treinador", "prereq": None, "desc": "+1 FOR ou DES. Levantar custa 1,5m. Escalar não custa movimento extra. Salto correndo com 1,5m de ajuste (em vez de 3m)."},
    "Ator": {"tipo": "Treinador", "prereq": None, "desc": "+1 CAR. Vantagem em Atuação e Enganação ao se passar por outra pessoa. Pode imitar voz/sons (ouviu 1 min). Teste SAB (Intuição) vs CAR (Enganação) para detectar."},
    "Controlador de Area": {"tipo": "Pokemon", "prereq": None, "desc": "Moves em área: alcance dobrado. Pode ajustar livremente o tamanho da área, reduzindo até o valor desejado."},
    "Corpo Apto": {"tipo": "Pokemon", "prereq": None, "desc": "Período de Carencia de status estendido por +3 rodadas após ser curado."},
    "Curandeiro": {"tipo": "Treinador", "prereq": None, "desc": "Kit primeiros-socorros: estabilizar restaura 1 HP. Ação: gasta 1 uso do kit para restaurar 1d6+4 + total de DVs da criatura (1x até descanso curto/longo)."},
    "Dedos Rapidos": {"tipo": "Treinador", "prereq": None, "desc": "+1 DES. Prof. Prestidigitação (ou especialista). Ação bônus: teste Prestidigitação para plantar algo em outra pessoa, esconder objeto, tirar algo do bolso."},
    "Disputador": {"tipo": "Treinador", "prereq": None, "desc": "Vantagem em ataques vs criatura agarrada. Ação: imobilizar agarrado (novo teste). Reação: agarrar criatura que tenta sair sem desengajar."},
    "Escultor de Poder": {"tipo": "Pokemon", "prereq": None, "desc": "Moves de área: escolha 1+MOVE aliados no alcance para não receberem dano ou efeito."},
    "Esquivo": {"tipo": "Treinador", "prereq": "DES 13+", "desc": "Esconder em penumbra. Errar ataque à distância não revela posição. Penumbra não impõe desvantagem em Percepção (visão)."},
    "Aumento de CA": {"tipo": "Pokemon", "prereq": None, "desc": "CA +1. Bônus incluído nas evoluções."},
    "Explorador": {"tipo": "Pokemon", "prereq": None, "desc": "Velocidade natação e escalada = maior velocidade. Ignora efeitos especiais do terreno."},
    "Explorador dos Ceus": {"tipo": "Pokemon", "prereq": "Nv 8, voo, pode aprender Fly (TM/Tutor)", "desc": "Aprende Fly permanente. Ignora neblina, ventos, tempestades (não-Moves). Tamanho Médio+: carrega Treinador. Grande+: até 4 criaturas Médio. Não perde senso de direção. Voo 8h sem exaustão."},
    "Explorador dos Mares": {"tipo": "Pokemon", "prereq": "Nv 8, natação, pode aprender Waterfall ou Dive (TM/Tutor)", "desc": "Aprende Waterfall ou Dive permanente. Ignora redemoinhos, tempestades, correntes. Esconder debaixo d'água: velocidade normal. Médio+: carrega Treinador (proteção sufocamento/pressão). Natação 8h sem exaustão. Treinador precisa equipamento mergulho."},
    "Explorador das Profundezas": {"tipo": "Pokemon", "prereq": "Nv 8, escavação, pode aprender Dig ou Strength (TM/Tutor)", "desc": "Aprende Dig ou Strength permanente. Escava qualquer terreno. Esconder no subsolo: velocidade normal. Médio+: carrega Treinador. Cavar 8h sem exaustão. Rochas maciças: FOR CD 15 (falha = dano = nível)."},
    "Explorador de Cavernas": {"tipo": "Treinador", "prereq": None, "desc": "Vantagem em Percepção e Investigação para detectar passagens ocultas, perigos. Vantagem em saves vs desmoronamentos, gases, terrenos perigosos. Resistência a dano de desabamentos. Mapear sem reduzir velocidade."},
    "Incansavel": {"tipo": "Pokemon", "prereq": None, "desc": "+1 PP para cada Move."},
    "Investida Poderosa": {"tipo": "Ambos", "prereq": None, "desc": "Ao usar Disparada: ação bônus para ataque corpo a corpo ou empurrar. Se mover 3m em linha reta antes: +5 dano no ataque OU empurrar 3m."},
    "Mente Afiada": {"tipo": "Treinador", "prereq": None, "desc": "+1 INT. Sabe direção norte. Sabe horas para nascer/pôr do sol. Memória precisa do último mês."},
    "Mestre de Combate a Distancia": {"tipo": "Pokemon", "prereq": None, "desc": "Ignora meia e três quartos cobertura. -5 acerto: +10 dano (1x/Move). Ação movimento: mirar anula desvantagem vs alvo em combate corpo a corpo."},
    "Mestre de Combate Corpo a Corpo": {"tipo": "Pokemon", "prereq": None, "desc": "Vantagem em ataques de oportunidade. -5 acerto: +10 dano se acertar (1x/Move)."},
    "Mestre de Combos": {"tipo": "Pokemon", "prereq": None, "desc": "Moves multi-hit: garantia de acertar pelo menos 2 vezes (mantém d8: 7-8 = +1 ou +2 golpes)."},
    "Mestre do Tipo": {"tipo": "Treinador", "prereq": None, "desc": "Escolha tipo entre Especializações. Pokémon desse tipo: +2 acerto, dano e STAB. Dobra proficiência em captura e localizar Pokémon do tipo. Pokémon do tipo dobram proficiência em perícias."},
    "Mobilidade": {"tipo": "Ambos", "prereq": None, "desc": "+3m deslocamento. Disparada: terreno difícil não custa movimento extra. Ataque corpo a corpo não provoca ataque de oportunidade (acertou ou não)."},
    "Move Extra": {"tipo": "Pokemon", "prereq": None, "desc": "Conhece 5 Moves em vez de 4. Não acumula com Explorador dos Céus/Mares/Profundezas."},
    "Musculoso": {"tipo": "Treinador", "prereq": None, "desc": "+1 FOR. Prof. Atletismo (ou especialista). Conta como tamanho maior para capacidade de carga."},
    "Observador": {"tipo": "Treinador", "prereq": None, "desc": "+1 INT ou SAB. Ler lábios. +5 em Percepção e Investigação passiva."},
    "Pequeno Grande": {"tipo": "Treinador", "prereq": "Nv 8+", "desc": "Pokémon não-finais (ou com evolução possível): tabela Moves da forma final; +3 ASI ao ganhar ASI; +3×nível HP e +2 CA. Perde ao evoluir para estágio final."},
    "Perceptivo": {"tipo": "Treinador", "prereq": None, "desc": "+1 SAB. Prof. Percepção (ou especialista). Penumbra não impõe desvantagem em Percepção se puder ver e ouvir."},
    "Perito": {"tipo": "Treinador", "prereq": None, "desc": "Proficiência em 3 perícias à escolha."},
    "Resiliente": {"tipo": "Ambos", "prereq": None, "desc": "Escolha atributo: +1 valor. Proficiência em saves desse atributo (não acumula se já proficiente)."},
    "Resistente": {"tipo": "Treinador", "prereq": None, "desc": "+1 CON. Rolagem de DV para recuperar HP: mínimo = 2× mod CON (mín 2)."},
    "Robusto": {"tipo": "Ambos", "prereq": None, "desc": "Ao adquirir: HP max +2× nível. Cada nível após: +2 HP max."},
    "Sentinela": {"tipo": "Treinador", "prereq": None, "desc": "Ataque de oportunidade: deslocamento do alvo = 0. Provoca mesmo com Desengajar. Reação (inimigo a 1,5m atacando outro): ataque corpo a corpo no atacante."},
    "Sorrateiro": {"tipo": "Treinador", "prereq": None, "desc": "+1 DES. Prof. Furtividade (ou especialista). Escondido: mover 3m ao ar livre sem revelar se terminar em posição não claramente visível."},
    "Sortudo": {"tipo": "Treinador", "prereq": None, "desc": "3 pontos de sorte. Gastar: rolar d20 extra em teste de perícia ou resistência (pode escolher após rolar). Ou quando ataque é feito contra você: role d20 e escolha qual usar. Recupera após descanso longo."}
}

PACOTES_AVENTURA = {
    "Aventureiro": "Mochila, Kit de Escalada, Lanterna, Célula de Energia (5), Pederneira e Aço, Ração de Acampamento (10), Cantil, Corda de 30 pés (9m). ₽1.200",
    "Explorador": "Mochila, Saco de Dormir, Kit de Refeição, Lanterna, Célula de Energia (5), Pederneira e Aço, Ração de Acampamento (10), Cantil, Corda de 30 pés (9m). ₽1.200",
    "Socorrista": "Mochila, Kit de Primeiros Socorros, Lanterna, Célula de Energia (5), Cantil, Canivete de Bolso, Casaco Impermeável, Garrafa térmica, Ração de Acampamento (10). ₽1.200",
    "Biólogo": "Mochila, Saco de Dormir, Kit de Jardinagem, Lanterna, Célula de Energia (2), Cantil, Bússola, Canivete de Bolso, Repelente, Pederneira e Aço, Carregador Solar. ₽1.200",
    "Mergulhador": "Mochila, Kit de Mergulho, Respirador, Filtro para Respirador, Lanterna, Célula de Energia (2). ₽1.200"
}

NATUREZAS_POKEMON = {
    "Nenhuma": {"bonus": None, "penalidade": None, "desc": "Sem modificadores", "bonus_val": 0, "pen_val": 0},
    "Arrogante": {"bonus": "for", "penalidade": "des", "desc": "+2 FOR, -2 DES. Confiança em excesso, demonstra orgulho", "bonus_val": 2, "pen_val": -2},
    "Impulsivo": {"bonus": "for", "penalidade": "con", "desc": "+2 FOR, -2 CON. Age sem pensar, confia na força", "bonus_val": 2, "pen_val": -2},
    "Corajoso": {"bonus": "for", "penalidade": "sab", "desc": "+2 FOR, -2 SAB. Enfrenta perigo com bravura", "bonus_val": 2, "pen_val": -2},
    "Sério": {"bonus": "for", "penalidade": "car", "desc": "+2 FOR, -2 CAR. Foco e autocontrole, movimentos precisos", "bonus_val": 2, "pen_val": -2},
    "Determinado": {"bonus": "des", "penalidade": "for", "desc": "+2 DES, -2 FOR. Não desiste fácil, enfrenta desafios", "bonus_val": 2, "pen_val": -2},
    "Apressado": {"bonus": "des", "penalidade": "con", "desc": "+2 DES, -2 CON. Acelerado, impaciente", "bonus_val": 2, "pen_val": -2},
    "Energético": {"bonus": "des", "penalidade": "car", "desc": "+2 DES, -2 CAR. Cheio de energia e entusiasmo", "bonus_val": 2, "pen_val": -2},
    "Curioso": {"bonus": "des", "penalidade": "sab", "desc": "+2 DES, -2 SAB. Explora tudo, se mete em encrencas", "bonus_val": 2, "pen_val": -2},
    "Sereno": {"bonus": "con", "penalidade": "des", "desc": "+2 CON, -2 DES. Mantém calma em situações extremas", "bonus_val": 2, "pen_val": -2},
    "Teimoso": {"bonus": "con", "penalidade": "sab", "desc": "+2 CON, -2 SAB. Insiste à sua maneira, arriscado", "bonus_val": 2, "pen_val": -2},
    "Apático": {"bonus": "con", "penalidade": "car", "desc": "+2 CON, -2 CAR. Prefere ficar sozinho, evita interações", "bonus_val": 2, "pen_val": -2},
    "Preguiçoso": {"bonus": "con", "penalidade": "for", "desc": "+2 CON, -2 FOR. Evita esforços, tende a descansar", "bonus_val": 2, "pen_val": -2},
    "Prudente": {"bonus": "sab", "penalidade": "for", "desc": "+2 SAB, -2 FOR. Avalia riscos antes de agir", "bonus_val": 2, "pen_val": -2},
    "Sábio": {"bonus": "sab", "penalidade": "con", "desc": "+2 SAB, -2 CON. Observa e analisa, aprende com tudo", "bonus_val": 2, "pen_val": -2},
    "Travesso": {"bonus": "sab", "penalidade": "car", "desc": "+2 SAB, -2 CAR. Gosta de brincar e pregar peças", "bonus_val": 2, "pen_val": -2},
    "Alegre": {"bonus": "car", "penalidade": "for", "desc": "+2 CAR, -2 FOR. Espalha felicidade, contagia outros", "bonus_val": 2, "pen_val": -2},
    "Sociável": {"bonus": "car", "penalidade": "des", "desc": "+2 CAR, -2 DES. Interage facilmente, inspira confiança", "bonus_val": 2, "pen_val": -2},
    "Ingênuo": {"bonus": "car", "penalidade": "sab", "desc": "+2 CAR, -2 SAB. Sem malícia, pode ser enganado", "bonus_val": 2, "pen_val": -2},
    "Tímido": {"bonus": "ca", "penalidade": "des", "desc": "+1 CA, -2 DES. Reservado, evita se expor", "bonus_val": 1, "pen_val": -2},
    "Astuto": {"bonus": "ca", "penalidade": "for", "desc": "+1 CA, -2 FOR. Inteligente e estratégico", "bonus_val": 1, "pen_val": -2}
}

TIPOS_POKEMON = [
    "Normal", "Fogo", "Água", "Grama", "Elétrico", "Gelo", "Lutador", "Venenoso",
    "Terra", "Voador", "Psíquico", "Inseto", "Pedra", "Fantasma", "Dragão", "Sombrio", "Aço", "Fada"
]

CORES_TIPO_POKEMON = {
    "Normal": "#A8A878", "Fogo": "#F08030", "Água": "#6890F0", "Grama": "#78C850",
    "Elétrico": "#F8D030", "Gelo": "#98D8D8", "Lutador": "#C03028", "Venenoso": "#A040A0",
    "Terra": "#E0C068", "Voador": "#A890F0", "Psíquico": "#F85888", "Inseto": "#A8B820",
    "Pedra": "#B8A038", "Fantasma": "#705898", "Dragão": "#7038F8", "Sombrio": "#705848",
    "Aço": "#B8B8D0", "Fada": "#EE99AC"
}

REGRAS_RESUMO = """**📋 Resumo de Combate**
• CA = 10 + mod DES (Sinnoh: +2)
• Iniciativa = mod DES (+5 se Alerta)
• Teste de perícia: d20 + mod atributo + prof
• CDs comuns: Fácil 8 | Médio 12 | Difícil 16 | Muito 20
• Crítico: 20 no d20 | Falha crítica: 1 no d20

**❤️ Pontos de Vida (PV)**
• 1º Nível: 10 + mod CON
• Níveis seguintes: 2 + mod CON por nível
• Dado de Vida: d8

**🎣 Captura de Pokémon**
CD = 10 + SR base (arred. ↓) + nível + vida restante ÷ 10 (arred. ↓)
Ex: Pikachu Nv3 SR½ 15/24 HP → 10+0+3+1 = **CD 14**
Vantagem se: envenenado, queimado, paralisado, congelado, dormindo, confuso ou impedido.
"""

LEALDADE_NIVEIS = {
    -3: {"nome": "Desleal", "emoji": "💔", "cor": "#8B0000", "desc": "Desdém por ser capturado, desobedece ativamente. Antes de ativar Move: rolar >15 no d20 ou falha.", "efeito_saves": -1, "efeito_moves": "Rolar >15 no d20 ou Move falha", "bonus_hp": 0},
    -2: {"nome": "Indiferente", "emoji": "😐", "cor": "#A0522D", "desc": "Não se importa se o treinador ganha ou perde. Antes de ativar Move: rolar >10 no d20 ou falha.", "efeito_saves": -1, "efeito_moves": "Rolar >10 no d20 ou Move falha", "bonus_hp": 0},
    -1: {"nome": "Chateado", "emoji": "😒", "cor": "#CD853F", "desc": "Mantém pequeno rancor. -1 em testes de resistência.", "efeito_saves": -1, "efeito_moves": None, "bonus_hp": 0},
    0: {"nome": "Neutro", "emoji": "😶", "cor": "#808080", "desc": "Age normalmente sem modificadores. Maioria dos recém-capturados começa aqui.", "efeito_saves": 0, "efeito_moves": None, "bonus_hp": 0},
    1: {"nome": "Contente", "emoji": "🙂", "cor": "#90EE90", "desc": "Mostra afeto e respeito. +1 em testes de resistência.", "efeito_saves": 1, "efeito_moves": None, "bonus_hp": 0},
    2: {"nome": "Satisfeito", "emoji": "😊", "cor": "#32CD32", "desc": "Grande confiança. +1 saves, HP max +metade do nível, +1 perícia proficiente (mesma se voltar).", "efeito_saves": 1, "efeito_moves": None, "bonus_hp": "metade do nível (arredondado para cima)", "extra": "+1 perícia proficiente"},
    3: {"nome": "Leal", "emoji": "💚", "cor": "#228B22", "desc": "Vínculo incrível. Como Satisfeito + HP=nível, +1 especialista em perícia proficiente.", "efeito_saves": 1, "efeito_moves": None, "bonus_hp": "igual ao nível", "extra": "+1 perícia proficiente, +1 perícia especialista"}
}

REGRAS_TEXTO = textwrap.dedent("""\
# Ficha RPG Pokémon - Regras

## Criando seu Treinador
1. **Atributos**: Distribua 27 pontos (mín 8, máx 15)
2. **Especialização**, **Região de Origem**, **Origem de Jornada**
3. **Classe** (Nível 2+), **Equipamento** (Pacote de Aventura)

## Point Buy
Valores 8-13: 1 pt/aumento. 14 e 15: 2 pts cada.

---

## Progressão de Níveis do Treinador
| Nível | Bônus Prof | Características | Pokéslots | Max SR |
|-------|------------|-----------------|-----------|--------|
| 1º | +2 | Pokémon inicial, Especialização | 3 | 2 |
| 2º | +2 | Classe de Treinador | 3 | 2 |
| 3º | +2 | Atualização de Controle (SR) | 3 | 5 |
| 4º | +2 | Incremento no Valor de Atributo | 3 | 5 |
| 5º | +3 | Habilidade da Classe, Pokéslot | 4 | 5 |
| 6º | +3 | Atualização de Controle (SR) | 4 | 8 |
| 7º | +3 | Especialização | 4 | 8 |
| 8º | +3 | Incremento Atributo, Atualização SR | 4 | 10 |
| 9º | +4 | Habilidade da Classe | 4 | 10 |
| 10º | +4 | Rastreador Pokémon, Pokéslot | 5 | 10 |
| 11º | +4 | Aura de Treinador, Atualização SR | 5 | 12 |
| 12º | +4 | Incremento no Valor de Atributo | 5 | 12 |
| 13º | +5 | Determinação do Treinador | 5 | 12 |
| 14º | +5 | Foco de Treinador, Atualização SR | 5 | 14 |
| 15º | +5 | Habilidade da Classe, Pokéslot | 6 | 14 |
| 16º | +5 | Incremento no Valor de Atributo | 6 | 14 |
| 17º | +6 | Atenção Aguçada, Atualização SR | 6 | 15 |
| 18º | +6 | Especialização | 6 | 15 |
| 19º | +6 | Incremento no Valor de Atributo | 6 | 15 |
| 20º | +6 | Treinador Mestre | 6 | 15 |

---

## Lealdade
O vínculo entre Pokémon e Treinador pode aumentar ou diminuir conforme interações. O Mestre determina o nível. Extremos (-3 e +3) são raros.

| Nível | Emoção | Efeito |
|-------|--------|--------|
| -3 | Desleal | Penalidade saves como Chateado/Indiferente. Antes de Move: rolar >15 no d20 ou Move falha. |
| -2 | Indiferente | Penalidade saves como Chateado. Antes de Move: rolar >10 no d20 ou Move falha. |
| -1 | Chateado | -1 em testes de resistência. |
| 0 | Neutro | Sem modificadores. Maioria dos recém-capturados começa aqui. |
| +1 | Contente | +1 em testes de resistência. |
| +2 | Satisfeito | +1 saves, HP max +metade do nível (arred.), +1 perícia proficiente. Se cair e voltar: mesma perícia. |
| +3 | Leal | Como Satisfeito + HP max = nível, +1 especialista em perícia proficiente. Se evoluir e perder a perícia: mantém prof, perde especialista. |

---

## Tipos de Ações
No turno: **1 ação padrão + 1 ação de movimento** (qualquer ordem). Pode trocar padrão por movimento (Disparada). Pode abrir mão das duas para **ação completa**. Ações bônus e reações: 1x/rodada cada. Ações livres: quantas quiser.
- **Ação padrão**: Usar Move, item, Ajudar, Atacar, Desengajar, Esconder, Esquivar, Preparar, Procurar, etc.
- **Ação de movimento**: Deslocar-se (igual ao deslocamento), levantar, pegar item.
- **Ação livre**: Ordem curta, jogar-se no chão, largar item, sacar/guardar Pokébola, abrir porta, pegar poção/berry, etc.
- **Reação**: Em resposta a algo (ex: ataque de oportunidade). 1x até próximo turno.

---

## Ações do Treinador
Em batalha, o Treinador interage com o ambiente, dá comandos e administra melhorias/poções. **Combate físico Treinador vs Treinador é proibido** (penalidade: perder Licença). Treinadores não podem agredir outros Treinadores nem os Pokémon deles em batalha. Em encontros com Pokémon selvagens, tudo é permitido.

---

## Ações em Combate
**Ajudar**: Aliado tem vantagem no próximo teste, ou atacante tem vantagem no 1º ataque vs alvo (se aliado a 1,5m).
**Atacar / Ativar Move**: Golpes físicos, Moves.
**Desengajar**: Movimento não provoca ataques de oportunidade.
**Disparada**: Ganha deslocamento adicional igual ao seu (ex: 9m → 18m no turno).
**Esconder**: Teste Furtividade. Se passar, benefícios de alvo oculto.
**Esquivar**: Até próximo turno: ataques vs você com desvantagem (se puder ver atacante), vantagem em saves DES.
**Preparar**: Defina gatilho e ação. Quando ocorrer, use como reação. Pokémon pode preparar Move (reduz PP); se concentração quebrar, PP perdido.
**Procurar**: Percepção ou Investigação conforme o Mestre.

---

## Recolhendo/Liberando Pokémon
- Treinador deve estar a **18m** para recolher. Pokémon liberado aparece a até **4,5m** do Treinador.
- Ao retornar: concentração termina, Mudanças de Status e bônus de itens anulados. Condições de Status permanecem (pausam contagem).
- Troca antes de desmaio: ação padrão, nova iniciativa na próxima rodada.
- Troca após desmaio: ação livre (se Treinador no alcance), novo Pokémon entra no início da próxima rodada.

---

## Capturando Pokémon
• Pokéslots cheios: escolher Pokémon para enviar ao PC.
• Pokébola destruída em tentativa fracassada.
• Pokémon mantém nível, status não-voláteis e vida atual.
• Recebe XP mínima do nível. Desmaiado não pode ser capturado. Captura concede 1/5 do XP.
• Pokémon amigáveis: Adestrar Animais ou circunstância narrativa (sem Pokébola).

**Arremessar Pokébola** (1 ação, alcance 18m): Teste de Adestrar Animais. Vantagem se envenenado, queimando, paralisado, congelado, dormindo, confuso ou impedido.
**CD** = 10 + SR base (arred. ↓) + nível + vida restante ÷ 10 (arred. ↓). Bônus conforme tipo de Pokébola.

---

## Pescaria – Guia do Velho Pescador

**Varinhas**: Old Rod (SR até 5), Good Rod (SR até 10), Super Rod (SR até 15).

**Tempo**: Role 1d6 × 5 minutos antes de jogar. Máx 3 tentativas no mesmo local por dia.

**Fisgar a Isca** – Teste de Sobrevivência:
| Local | Old Rod | Good Rod | Super Rod |
|-------|---------|----------|-----------|
| Rio | CD 10 | CD 10, vantagem | Pesca garantida |
| Lago | CD 15 | CD 10 | CD 5 |
| Praia | CD 20 | CD 15 | CD 10 |
| Oceano | CD 25 | CD 20 | CD 15 |

Falha: nada mordeu. Sucesso: Pokémon mordeu (Mestre busca adequado ao local). **Acerto Crítico**: Pokémon de sua escolha + só 1 sucesso para puxar.

**Puxar**: 3 testes resistidos de FOR vs Pokémon. Vencer 2 = capturado.

**Combate**: Você age primeiro. Reduza CD da captura: Old Rod -5, Good Rod -10, Super Rod -15.

---

## Realizando Ataque
1. Escolha alvo no alcance. 2. Modificadores (cobertura, vantagem/desvantagem). 3. Jogue ataque; se acertar, jogue dano.
- **20 natural**: Acerto garantido, crítico.
- **1 natural**: Erro garantido. Em save de resistência: 20 = sucesso; 1 = crítico contra o alvo.

---

## Atacantes e Alvos Ocultos
Atacar alvo que não vê: desvantagem (ou alvo tem vantagem em save). Se alvo não vê você: vantagem em ataques. Ao atacar escondido, revela posição.

---

## Ataques
**Corpo a corpo**: Alcance 1,5m (Grande ou menor) ou 3m (maior). Treinador desarmado: 1d4+mod FOR.
**À distância**: Alcance conforme Move. Inimigo adjacente (1,5m): desvantagem.
**Distância em voo**: Maior (altura ou horizontal) + metade da menor. Arredonde para múltiplo de 5.
**Arremesso**: Distância = regras de salto. Criatura consciente: agarrar antes; distância = metade. Dano: 1d6+mod FOR. Fantasma imune (exceto Fantasma/Sombrio).

---

## Ataques de Oportunidade
Quando inimigo sai do alcance: reação, Move corpo a corpo (1 ação). Desengajar ou retornar à Pokébola evita. Teleporte ou movimento forçado não provocam.

---

## Agarrão e Empurrão
**Agarrar**: Teste FOR (Atletismo) vs FOR/DES do alvo. Escapar: ação padrão, FOR ou DES (Acrobacia) vs quem agarra. Fantasma imune (exceto Fantasma/Sombrio).
**Empurrão**: FOR vs FOR/DES do alvo. Derrubar ou empurrar 1,5m.

---

## Combate Submerso
- Sem deslocamento de natação: desvantagem em ataques corpo a corpo e à distância.
- Ataque à distância vs submerso: desvantagem; alvo tem vantagem em save.
- Totalmente imerso: resistência a dano de fogo (vulnerável → normal).

---

## Descanso
**Descanso curto** (30 min): Gastar DVs para recuperar HP (dado + mod CON). Pokémon: sem recuperar PP, não revivem nem curam status.
**Descanso longo** (8h): Recupera todos HP, metade dos DVs. Pokémon: curam status, recuperam PP. 1x a cada 24h, precisa 1+ HP no início.

---

## Despesas de Estilo de Vida

| Estilo | Preço/dia |
|--------|-----------|
| Miserável | ₽10 |
| Pobre | ₽20 |
| Modesto | ₽100 |
| Confortável | ₽200 |
| Rico | ₽400 |
| Aristocrático | A partir de ₽1.000 |

**Hospedagem (por noite)**
| Nível | Preço |
|-------|-------|
| Miserável | ₽7 |
| Pobre | ₽10 |
| Modesta | ₽50 |
| Confortável | ₽80 |
| Rica | ₽200 |
| Aristocrática | ₽400 |

**Refeição diária**
| Nível | Preço |
|-------|-------|
| Miserável | ₽3 |
| Pobre | ₽6 |
| Modesta | ₽30 |
| Confortável | ₽50 |
| Rica | ₽80 |
| Aristocrática | ₽200 |

---

## Clima (d100)

**Primavera/Verão**
| d100 | Clima | Moves Afetados (vantagem dano) |
|------|-------|-------------------------------|
| 1-25 | Sol Forte, Calmo | Grama, Terra, Fogo |
| 26-35 | Sol Forte, Ventoso | Grama, Terra, Fogo, Voador, Dragão, Psíquico |
| 36-65 | Nublado, Calmo | Normal, Pedra, Fada, Lutador, Venenoso |
| 66-75 | Nublado, Ventoso | Normal, Pedra, Fada, Lutador, Venenoso, Voador, Dragão, Psíquico |
| 76-80 | Nebuloso | Sombrio, Fantasma |
| 81-90 | Garoa Leve | Água, Elétrico, Inseto |
| 91-99 | Chuva Forte | Água, Elétrico, Inseto |
| 100 | Tempestade Perigosa | Água, Elétrico, Inseto |

**Outono/Inverno**
| d100 | Clima | Moves Afetados |
|------|-------|----------------|
| 1-15 | Sol Forte, Calmo | Grama, Terra, Fogo |
| 16-25 | Sol Forte, Ventoso | Grama, Terra, Fogo, Voador, Dragão, Psíquico |
| 26-40 | Nublado, Calmo | Normal, Pedra, Fada, Lutador, Venenoso |
| 41-50 | Nublado, Ventoso | Normal, Pedra, Fada, Lutador, Venenoso, Voador, Dragão, Psíquico |
| 51-60 | Nebuloso | Sombrio, Fantasma |
| 61-70 | Garoa Leve | Água, Elétrico, Inseto |
| 71-80 | Chuva Forte | Água, Elétrico, Inseto |
| 81-90 | Neve Leve | Gelo, Aço |
| 91-99 | Nevasca Forte | Gelo, Aço |
| 100 | Tempestade de Neve | Gelo, Aço |

**Granizo e Tempestade de Areia** (natural): Visibilidade reduzida; ataques à distância com desvantagem. Gelo ignora Granizo; Terra/Pedra/Aço ignoram Areia.

---

## Condições (resumo)
Agarrado, Amedrontado, Atordoado, Caído, Cego, Confuso, Desanimado, Em Chamas, Enfeitiçado, Enjoado, Envenenado, Exausto (6 níveis), Fascinado, Fraco, Impedido, Incapacitado, Inconsciente, Invisível, Lento, Paralisado, Petrificado, Sangrando, Surdo.

---

## Condições de Status (Pokémon)
**Não-voláteis** (1 por vez): Queimado (dano corpo a corpo /2; dano = prof no fim do turno). Congelado (incapacitado, impedido; save FOR CD 10+prof para libertar; dano fogo cura). Paralisado (desvantagem FOR/DES; d4 no turno: 1 = incapacitado até próximo). Envenenado (dano = metade do nível no fim do turno). Gravemente Envenenado (dano cumulativo). Dormindo (d6: 1-2 = 1 turno, 3-4 = 2, 5-6 = 3).
**Voláteis**: Atordoado (incapacitado até fim do próximo turno). Confuso (1d4+1 turnos; d20: ≤10 Move falha e se fere). Encantado (d20: ≤10 Move falha e incapacitado).
**Período de carência**: Após curar status, imune ao mesmo até fim do próximo turno.

---

## Mudanças de Status

| Mudança | Efeito (1 estágio) |
|---------|---------------------|
| Ataque | +prof ao dano corpo a corpo |
| Ataque Especial | +prof ao dano à distância |
| Defesa | -prof do dano corpo a corpo |
| Defesa Especial | -prof do dano à distância |
| Velocidade | +1,5m deslocamento, +prof iniciativa |
| Precisão | +1 ataque e CD |
| Evasão | +1 CA e saves |
| Margem de Crítico | +3 |

Estágios: -6 a +6. Negativos invertem o efeito. Opcional: sem acúmulo (apenas 1 fonte) ou acúmulos de fontes diferentes.

---

## Aprimorando seu Pokémon

### XP por Nível
| Nível | XP necessário |
|-------|---------------|
| 2º | 200 |
| 3º | 800 |
| 4º | 2.000 |
| 5º | 6.000 |
| 6º | 12.000 |
| 7º | 20.000 |
| 8º | 30.000 |
| 9º | 44.000 |
| 10º | 62.000 |
| 11º | 82.000 |
| 12º | 104.000 |
| 13º | 128.000 |
| 14º | 158.000 |
| 15º | 194.000 |
| 16º | 234.000 |
| 17º | 278.000 |
| 18º | 326.000 |
| 19º | 382.000 |
| 20º | 450.000 |

### Ganho de Vida
Média do dado (metade+1) + mod CON por nível.

### Progressão de Níveis do Pokémon
| Nível | Bônus Prof | Características | STAB |
|-------|------------|-----------------|------|
| 1º | +2 | — | +0 |
| 2º | +2 | Novo Move | +0 |
| 3º | +2 | Aumento STAB | +1 |
| 4º | +2 | ASI | +1 |
| 5º | +3 | Prof/dano | +1 |
| 6º | +3 | Novo Move | +1 |
| 7º | +3 | STAB | +2 |
| 8º | +3 | ASI | +2 |
| 9º | +4 | Prof | +2 |
| 10º | +4 | Novo Move / Dano | +2 |
| 11º | +4 | STAB | +3 |
| 12º | +4 | ASI | +3 |
| 13º | +5 | Prof | +3 |
| 14º | +5 | Novo Move | +3 |
| 15º | +5 | STAB | +4 |
| 16º | +5 | ASI | +4 |
| 17º | +6 | Prof/dano | +4 |
| 18º | +6 | Novo Move | +4 |
| 19º | +6 | STAB | +5 |
| 20º | +6 | ASI | +5 |

**ASI**: 3 estágios = 2 pts (níveis 4,8,12,16,20). 2 estágios = 3 pts. 1 estágio = 4 pts. Máx 20 antes da Natureza. 2 pts = 1 talento.
**STAB**: Bônus em dano quando Move é do mesmo tipo. Só no 1º golpe em multi-hit.

---

## Evolução
No momento do nível. Passos: 1) Atributos (pontos extras, máx forma evoluída +4 +natureza +ASI anteriores). 2) +2×nível em HP. 3) Novo dado de vida. 4) Nova CA, prof, resistências. 5) Se perder habilidade, trocar por uma da forma evoluída. 6) Mantém Moves; novos vêm da lista do evoluído. 7) Se nível de ASI, adicionar. Pode adiar; uma vez decidido, não evolui até próximo nível.

---

## Experiência do Treinador

| Nível | Níveis Totais |
|-------|---------------|
| 2º | 3 |
| 3º | 6 |
| 4º | 9 |
| 5º | 12 |
| 6º | 20 |
| 7º | 24 |
| 8º | 28 |
| 9º | 32 |
| 10º | 36 |
| 11º | 50 |
| 12º | 55 |
| 13º | 60 |
| 14º | 65 |
| 15º | 70 |
| 16º | 90 |
| 17º | 96 |
| 18º | 102 |
| 19º | 108 |
| 20º | 114 |

Soma dos X Pokémon de maior nível (X = Pokéslots). Pokémon capturado em nível alto é mais fraco que treinado desde baixo.

---

## Apêndice: Experiência Pokémon por Nível e SR

**Tabela 1 – SR 1/8 a 6**

| Nível | 1/8 | 1/4 | 1/2 | 1 | 2 | 3 | 4 | 5 | 6 |
|-------|-----|-----|-----|-----|-----|------|------|------|------|
| 1 | 20 | 40 | 80 | 160 | 360 | 560 | 880 | 1.400 | 1.800 |
| 2 | 40 | 80 | 160 | 360 | 560 | 880 | 1.400 | 1.800 | 2.300 |
| 3 | 80 | 150 | 340 | 530 | 840 | 1.400 | 1.700 | 2.200 | 3.000 |
| 4 | 140 | 320 | 500 | 790 | 1.300 | 1.700 | 2.100 | 2.800 | 3.600 |
| 5 | 360 | 560 | 880 | 1.400 | 1.800 | 2.300 | 3.100 | 4.000 | 4.700 |
| 6 | 530 | 840 | 1.400 | 1.700 | 2.200 | 3.000 | 3.800 | 4.500 | 5.500 |
| 7 | 820 | 1.300 | 1.700 | 2.200 | 2.900 | 3.700 | 4.400 | 5.400 | 6.200 |
| 8 | 1.300 | 1.700 | 2.100 | 2.800 | 3.600 | 4.300 | 5.200 | 6.100 | 7.300 |
| 9 | 1.600 | 2.000 | 2.700 | 3.500 | 4.200 | 5.100 | 5.900 | 7.000 | 8.100 |
| 10 | 2.300 | 3.100 | 4.000 | 4.700 | 5.800 | 6.700 | 8.000 | 9.200 | 10.400 |
| 11 | 3.000 | 3.800 | 4.500 | 5.500 | 6.500 | 7.700 | 8.800 | 10.000 | 10.800 |
| 12 | 3.800 | 4.400 | 5.400 | 6.300 | 7.500 | 8.600 | 9.800 | 10.500 | 11.100 |
| 13 | 4.300 | 5.300 | 6.200 | 7.400 | 8.500 | 9.600 | 10.300 | 10.900 | 11.400 |
| 14 | 5.200 | 6.000 | 7.200 | 8.300 | 9.400 | 10.100 | 10.600 | 11.200 | 11.900 |
| 15 | 5.900 | 7.000 | 8.100 | 9.200 | 9.900 | 10.400 | 10.900 | 11.600 | 12.700 |
| 16 | 6.900 | 7.900 | 8.900 | 9.600 | 10.100 | 10.700 | 11.400 | 12.400 | 13.400 |
| 17 | 9.200 | 10.400 | 11.200 | 11.800 | 12.400 | 13.200 | 14.400 | 15.600 | 16.800 |
| 18 | 10.000 | 10.800 | 11.300 | 11.900 | 12.700 | 13.800 | 15.000 | 16.100 | 17.700 |
| 19 | 10.500 | 11.100 | 11.700 | 12.400 | 13.500 | 14.700 | 15.800 | 17.300 | 18.800 |
| 20 | 10.900 | 11.400 | 12.100 | 13.200 | 14.400 | 15.500 | 16.900 | 18.400 | 19.900 |

**Tabela 2 – SR 7 a 15**

| Nível | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|-------|------|------|------|------|------|------|------|------|------|
| 1 | 2.300 | — | — | — | — | — | — | — | — |
| 2 | 3.100 | — | — | — | — | — | — | — | — |
| 3 | 3.800 | — | — | — | — | — | — | — | — |
| 4 | 4.200 | — | — | — | — | — | — | — | — |
| 5 | 5.800 | 6.700 | 8.000 | 9.200 | 10.400 | — | — | — | — |
| 6 | 6.400 | 7.600 | 8.700 | 9.900 | 10.600 | — | — | — | — |
| 7 | 7.400 | 8.600 | 9.700 | 10.400 | 11.000 | — | — | — | — |
| 8 | 8.400 | 9.500 | 10.200 | 10.700 | 11.300 | 12.200 | 13.400 | — | — |
| 9 | 9.200 | 9.900 | 10.400 | 10.900 | 11.600 | 12.600 | 14.200 | — | — |
| 10 | 11.200 | 11.800 | 12.400 | 13.200 | 14.400 | 15.600 | 16.800 | 18.400 | — |
| 11 | 11.300 | 11.900 | 12.700 | 13.800 | 15.000 | 16.100 | 17.700 | 19.200 | — |
| 12 | 11.700 | 12.400 | 13.500 | 14.700 | 15.800 | 17.300 | 18.800 | 20.300 | — |
| 13 | 12.100 | 13.200 | 14.400 | 15.500 | 16.900 | 18.400 | 19.900 | 21.700 | — |
| 14 | 13.000 | 14.000 | 15.100 | 16.600 | 18.000 | 19.400 | 21.200 | 23.000 | — |
| 15 | 13.700 | 14.800 | 16.200 | 17.600 | 19.000 | 20.800 | 22.500 | 24.600 | 26.800 |
| 16 | 14.400 | 15.800 | 17.200 | 18.600 | 20.300 | 22.000 | 24.100 | 26.100 | 28.200 |
| 17 | 18.400 | 20.000 | 21.600 | 23.600 | 25.600 | 28.000 | 30.400 | 32.800 | 36.000 |
| 18 | 19.200 | 20.700 | 22.700 | 24.600 | 26.900 | 29.200 | 31.500 | 34.600 | 38.400 |
| 19 | 20.300 | 22.200 | 24.100 | 26.300 | 28.600 | 30.800 | 33.800 | 37.600 | 42.300 |
| 20 | 21.700 | 23.600 | 25.800 | 28.000 | 30.200 | 33.100 | 36.800 | 41.400 | 46.000 |
""").strip()
