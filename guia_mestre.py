"""
Guia do Mestre - Conteúdo de referência para a Mesa.
"""
MESTRE_GUIA = {
    "encontros": {
        "titulo": "Construindo Encontros",
        "conteudo": """**Pokémon Selvagens**
• Introduza Pokémon de vários níveis; jogadores não sabem o nível até capturar.
• Expedição focada em captura: vários Pokémon de níveis baixos.
• Encontros focados em batalha: Pokémon mais altos, talvez 1–2 acima do nível dos jogadores.
• XP a critério do Mestre (participação ou distribuição igual).

**Batalhas de Treinadores**
• Pokémon inimigos não podem ser capturados.
• Pokémon de Treinadores são geralmente mais fortes; avance como jogadores avançam os seus.
• Considere XP e dinheiro para toda a equipe por derrotar Treinador.

**Iniciando Acima do Nível 1**
• Total de níveis dos Pokémon não pode exceder o mínimo da tabela de experiência.
• Nenhum Pokémon pode ter SR acima do que o Treinador controla.
• Um Pokémon deve ter SR ½ ou menos como inicial.
• Dinheiro inicial = nível × ₽1.500""",
    },
    "tamanho": {
        "titulo": "Tamanho de Criatura",
        "conteudo": """| Categoria | Espaço Ocupado |
|-----------|----------------|
| Miúdo | 1,5 m × 1,5 m |
| Pequeno | 1,5 m × 1,5 m |
| Médio | 1,5 m × 1,5 m |
| Grande | 3 m × 3 m |
| Enorme | 4,5 m × 4,5 m |
| Imenso | 6 m × 6 m ou maior |

**Alcance:** Grande ou menor = 1,5 m; maior que Grande = 3 m.

**Grid:** Cada quadrado = 1,5 m. Deslocamento ÷ 1,5 = quadrados. Movimento diagonal conta.

**Espremendo-se:** Criatura pode passar em espaço uma categoria menor; custa 1,5 m extra/1,5 m, desvantagem em ataques, ataques contra ela com vantagem.""",
    },
    "lendarios": {
        "titulo": "Batalhas contra Lendários/Chefes",
        "conteudo": """**Habilidades Lendárias** (conceda experiência extra):
• **Determinação Lendária** (X/dia): Falhar save → pode optar por ter sucesso.
• **Resiliência Lendária**: Sacrificar ação para remover efeito negativo.
• **Resistência Lendária** (X/dia): Reduzir dano pela metade.
• **Ataque Lendário**: Sacrificar ação agora → dois ataques no próximo turno.
• **Ataque Lendário 2**: Dois ataques por turno.
• **Ataque Lendário 3**: Move característico 2× por turno.
• **Energia Lendária**: Sacrificar ação → recuperar PP de um Move.
• **Energia Lendária 2**: Dobro de PP em cada Move.
• **Destreza Lendária**: Mover sem provocar ataques de oportunidade.
• **Velocidade Lendária** (X/dia): Dobrar deslocamento.
• **Resistência Lendária (HP)**: HP baseado no máximo do dado por nível.
• **Reflexos Lendários**: Duas reações por rodada.
• **Conhecimento Lendário**: Aprender Moves de qualquer nível.
• **Armadura Lendária** (X/dia): Reação +1/+2/+3 CA para fazer ataque falhar.

**Equilibrar:** Duplicar ou triplicar HP do Lendário conforme número de treinadores.

**Combates em níveis altos:** Regra opcional: dobrar dano e cura base para batalhas mais dinâmicas.""",
    },
    "condicoes": {
        "titulo": "Condições (Humanos e Pokémon)",
        "conteudo": """**Resumo:** Agarrado, Amedrontado, Atordoado, Caído, Cego, Confuso, Desanimado, Em Chamas, Enfeitiçado, Enjoado, Envenenado, Exausto (6 níveis), Fascinado, Fraco, Impedido, Incapacitado, Inconsciente, Invisível, Lento, Paralisado, Petrificado, Sangrando, Surdo.

**Exausto:** 1=desvantagem perícias; 2=deslocamento metade; 3=desvantagem ataques/saves; 4=HP max metade; 5=deslocamento 0; 6=morte.

**Caído:** Rastejar ou levantar (metade deslocamento). Desvantagem em ataques. Ataques a 1,5 m = vantagem.

**Inconsciente:** Incapacitado, falha FOR/DES saves, ataques contra = vantagem, ataque a 1,5 m = crítico.""",
    },
    "status_pokemon": {
        "titulo": "Condições de Status (Pokémon)",
        "conteudo": """**Não-voláteis** (1 por vez):
• **Queimado**: Dano corpo a corpo /2; dano = prof no fim do turno.
• **Congelado**: Incapacitado, impedido; save FOR CD 10+prof para libertar; dano fogo cura.
• **Paralisado**: Desvantagem FOR/DES; d4 no turno: 1 = incapacitado até próximo.
• **Envenenado**: Dano = metade do nível no fim do turno.
• **Gravemente Envenenado**: Dano cumulativo.
• **Dormindo**: d6: 1–2 = 1 turno, 3–4 = 2, 5–6 = 3.

**Voláteis:** Atordoado (incapacitado até fim do próximo turno), Confuso (d20 ≤10 Move falha e se fere), Encantado (d20 ≤10 Move falha e incapacitado).

**Período de carência:** Após curar, imune ao mesmo até fim do próximo turno.""",
    },
    "mudancas_status": {
        "titulo": "Mudanças de Status",
        "conteudo": """| Mudança | Efeito (1 estágio) |
|---------|---------------------|
| Ataque | +prof ao dano corpo a corpo |
| Ataque Especial | +prof ao dano à distância |
| Defesa | -prof do dano corpo a corpo |
| Defesa Especial | -prof do dano à distância |
| Velocidade | +1,5 m deslocamento, +prof iniciativa |
| Precisão | +1 ataque e CD |
| Evasão | +1 CA e saves |
| Margem de Crítico | +3 |

Estágios: -6 a +6. Negativos invertem o efeito.

**Opcional – Sem acúmulo:** Cada Move/habilidade produz só os estágios indicados, sem acumular usos repetidos.""",
    },
}
