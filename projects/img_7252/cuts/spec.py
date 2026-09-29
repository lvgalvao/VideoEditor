# Frases do take (tempos no source) e as 3 variações.
PHRASES = {
    "P1": [[0.0, 2.72]],                                   # A primeira forma de aprender... projetos do mundo real
    "P2": [[2.72, 5.85]],                                  # Se você quer aprender Claude Code, vem aí o desafio Claude
    "P3": [[6.08, 8.42]],                                  # Quatro dias, quatro projetos do mundo real
    "P4": [[8.62, 10.0]],                                  # Projetos de todas as áreas
    "P5": [[10.36, 11.68], [11.93, 13.65], [13.88, 16.05]],  # Marketing e vendas, financeiro..., operação e logística
    "P6": [[16.24, 19.47]],                                # Se você quer trabalhar nas principais áreas do mercado de trabalho (sem "seja estar buscando..." — áudio embolado)
    "P7": [[22.64, 26.38]],                                # vão te perguntar como você tem trabalhado com Claude Code
    "P8": [[26.82, 29.2]],                                 # E saber essa habilidade não é mais opcional
    "P9": [[31.62, 32.6]],                                 # Então, venha participar (2º take)
    "P10": [[35.50, 39.28]],                               # Em quatro dias eu vou te ensinar a habilidade mais importante de 2026
    "P10b": [[36.31, 39.28]],                              # Eu vou te ensinar a habilidade mais importante de 2026
    "P11": [[39.66, 42.14]],                               # O ano está acabando...
    "P12": [[42.14, 43.5]],                                # Clica aqui, estou te esperando
}

VARIATIONS = {
    "v1_completa": {
        "phrases": ["P2", "P3", "P4", "P5", "P6", "P7", "P8", "P10", "P11", "P12"],
        "hook": ["O jeito certo de aprender", "CLAUDE CODE"],
    },
    "v2_entrevista": {
        "phrases": ["P6", "P7", "P8", "P2", "P3", "P10b", "P12"],
        "hook": ["Vão te perguntar isso", "NA ENTREVISTA"],
    },
    "v3_direta": {
        "phrases": ["P2", "P3", "P4", "P5", "P8", "P12"],
        "hook": ["Aprenda em 4 dias", "CLAUDE CODE"],
    },
}

FIX = {"Cloud": "Claude", "Cloud.": "Claude.", "Cloud,": "Claude,", "stage,": "estágio,", "Vamos": "Vão"}
