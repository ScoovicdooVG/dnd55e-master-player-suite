import math

SIZES_55E = ["Diminuto", "Pequeño", "Mediano", "Grande", "Enorme", "Gargantuesco"]

CREATURE_TYPES_55E = [
    "Aberración", "Bestia", "Celestial", "Constructo", "Dragón",
    "Elemental", "Feérico", "Infernal", "Gigante", "Humanoide",
    "Monstruosidad", "Cieno (Ooze)", "Planta", "Muerto viviente"
]

CONDITIONS_55E = [
    "Sin Estado", "Concentración", "Agarrado", "Apresado", "Asustado",
    "Aturdido", "Cegado", "Derribado", "Ensordecido", "Envenenado",
    "Hechizado", "Incapacitado", "Inconsciente", "Invisible",
    "Paralizado", "Petrificado"
]

# Tabla oficial de Valor de Desafío (CR/VD) -> XP y Bono de Competencia
CR_TABLE_55E = {
    "0": (10, 2), "1/8": (25, 2), "1/4": (50, 2), "1/2": (100, 2),
    "1": (200, 2), "2": (450, 2), "3": (700, 2), "4": (1100, 2),
    "5": (1800, 3), "6": (2300, 3), "7": (2900, 3), "8": (3900, 3),
    "9": (5000, 4), "10": (5900, 4), "11": (7200, 4), "12": (8400, 4),
    "13": (10000, 5), "14": (11500, 5), "15": (13000, 5), "16": (15000, 5),
    "17": (18000, 6), "18": (20000, 6), "19": (22000, 6), "20": (25000, 6),
    "21": (33000, 7), "22": (41000, 7), "23": (50000, 7), "24": (62000, 7),
    "25": (75000, 8), "30": (155000, 9)
}

# Plantillas base en Sistema Métrico (Estándar 5.5e)
PRESET_MONSTERS_55E = {
    "Goblin Guerrero": {
        "name": "Goblin Guerrero",
        "size_type_alignment": "Pequeño Feérico (Goblin), Caótico Neutral",
        "armor_class": "15 (Armadura de cuero, Escudo)",
        "hit_points": "10 (3d6)",
        "speed": "9 m",
        "initiative_bonus": 2,
        "challenge_rating": "1/4",
        "statblock": {
            "scores": {"Fuerza": 8, "Destreza": 15, "Constitución": 10, "Inteligencia": 10, "Sabiduría": 8, "Carisma": 8},
            "senses": "Visión en la oscuridad 18 m, Percepción pasiva 9",
            "languages": "Común, Goblin",
            "traits": "• Huida Ágil (Acción Adicional): El goblin puede realizar la acción de Destrabarse o Esconderse en cada uno de sus turnos.",
            "actions": "• Cimitarra: Ataque con arma cuerpo a cuerpo: +4 a impactar, alcance 1,5 m. Impacto: 5 (1d6 + 2) de daño cortante.\n• Arco corto: Ataque a distancia: +4 a impactar, alcance 24/96 m. Impacto: 5 (1d6 + 2) de daño perforante.",
            "bonus_reactions": ""
        }
    },
    "Ogro": {
        "name": "Ogro",
        "size_type_alignment": "Grande Gigante, Caótico Malvado",
        "armor_class": "11 (Armadura de pieles)",
        "hit_points": "68 (8d10 + 24)",
        "speed": "12 m",
        "initiative_bonus": -1,
        "challenge_rating": "2",
        "statblock": {
            "scores": {"Fuerza": 19, "Destreza": 8, "Constitución": 16, "Inteligencia": 5, "Sabiduría": 7, "Carisma": 7},
            "senses": "Visión en la oscuridad 18 m, Percepción pasiva 8",
            "languages": "Común, Gigante",
            "traits": "• Imponente: El ogro tiene ventaja en pruebas de Fuerza para empujar o derribar objetos.",
            "actions": "• Garrote grande: Ataque cuerpo a cuerpo: +6 a impactar, alcance 1,5 m. Impacto: 13 (2d8 + 4) de daño contundente y puede empujar 3 m.\n• Jabalina: Ataque a distancia: +6 a impactar, alcance 9/36 m. Impacto: 11 (2d6 + 4) de daño perforante.",
            "bonus_reactions": ""
        }
    },
    "Contemplador (Beholder)": {
        "name": "Contemplador (Beholder)",
        "size_type_alignment": "Grande Aberración, Legal Malvado",
        "armor_class": "18 (Armadura natural)",
        "hit_points": "190 (20d10 + 80)",
        "speed": "1,5 m, Vuelo 6 m (levitar)",
        "initiative_bonus": 6,
        "challenge_rating": "13",
        "statblock": {
            "scores": {"Fuerza": 10, "Destreza": 14, "Constitución": 18, "Inteligencia": 17, "Sabiduría": 15, "Carisma": 17},
            "senses": "Visión en la oscuridad 36 m, Percepción pasiva 22",
            "languages": "Habla Profunda, Infracomún",
            "traits": "• Cono Antimagia: El ojo central emite un cono antimagia de 45 m. Al inicio de cada turno decide hacia dónde mira.",
            "actions": "• Mordisco: +5 a impactar, alcance 1,5 m. Impacto: 14 (4d6) de daño perforante.\n• Rayos Oculares: Dispara 3 rayos al azar a objetivos que vea a 36 m o menos (1. Hechizar, 2. Paralizante, 3. Miedo, 4. Ralentizador, 5. Enervación, 6. Telequinético, 7. Sueño, 8. Petrificación, 9. Desintegrador, 10. Muerte).",
            "bonus_reactions": "• Acciones Legendarias (3/asalto): Dispara 1 Rayo Ocular al final del turno de otra criatura."
        }
    }
}


class Monster55eRules:
    @staticmethod
    def get_mod(score: int) -> int:
        return math.floor((score - 10) / 2)

    @staticmethod
    def format_mod(mod: int) -> str:
        return f"+{mod}" if mod >= 0 else str(mod)

    @staticmethod
    def get_cr_xp_and_prof(cr_str: str) -> tuple:
        return CR_TABLE_55E.get(cr_str, (100, 2))

    @staticmethod
    def parse_base_hp(hp_str: str) -> int:
        """Extrae el número entero de PG desde cadenas como '68 (8d10 + 24)'."""
        token = hp_str.strip().split(" ")[0]
        return int(token) if token.isdigit() else 15

    @staticmethod
    def parse_base_ac(ac_str: str) -> int:
        token = ac_str.strip().split(" ")[0]
        return int(token) if token.isdigit() else 12