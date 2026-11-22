RACES_5E = {
    "Enano": {
        "speed": "25 pies",
        "size": "Mediano",
        "ability_bonuses": {"Constitución": 2},
        "languages": ["Común", "Enano"],
        "subraces": {
            "Enano de las Colinas": {
                "ability_bonuses": {"Sabiduría": 1},
                "hp_per_level": 1,
                "traits": [
                    ("Aguante Enano", "Tus puntos de golpe máximos aumentan en 1 en nivel 1 y +1 adicional cada vez que subas de nivel.")
                ]
            },
            "Enano de las Montañas": {
                "ability_bonuses": {"Fuerza": 2},
                "traits": [
                    ("Entrenamiento con Armadura Enana", "Eres competente con armaduras ligeras y medias.")
                ]
            }
        },
        "traits": [
            ("Visión en la Oscuridad", "Puedes ver en luz tenue hasta 60 pies como luz brillante y en oscuridad como luz tenue."),
            ("Resistencia Enana", "Ventaja en salvaciones contra veneno y resistencia al daño de veneno."),
            ("Entrenamiento de Combate Enano", "Competencia con hachas de guerra, hachas de mano, martillos de guerra y martillos ligeros."),
            ("Afinidad con la Piedra", "Doblas tu competencia en Inteligencia (Historia) sobre el origen de trabajos en piedra.")
        ]
    },
    "Elfo": {
        "speed": "30 pies",
        "size": "Mediano",
        "ability_bonuses": {"Destreza": 2},
        "languages": ["Común", "Élfico"],
        "fixed_skills": ["Percepción"],
        "subraces": {
            "Alto Elfo": {
                "ability_bonuses": {"Inteligencia": 1},
                "traits": [
                    ("Entrenamiento con Armas Élficas", "Competencia con espadas cortas, espadas largas, arcos cortos y arcos largos."),
                    ("Truco", "Conoces un truco de la lista de conjuros de mago (aptitud: Inteligencia)."),
                    ("Idioma Adicional", "Puedes hablar, leer y escribir un idioma adicional.")
                ]
            },
            "Elfo de los Bosques": {
                "ability_bonuses": {"Sabiduría": 1},
                "speed": "35 pies",
                "traits": [
                    ("Entrenamiento con Armas Élficas", "Competencia con espadas cortas, espadas largas, arcos cortos y arcos largos."),
                    ("Pies Veloces", "Tu velocidad caminando base aumenta a 35 pies."),
                    ("Máscara de la Naturaleza", "Puedes esconderte estando ligeramente oscuro por follaje, lluvia, nieve o niebla.")
                ]
            },
            "Elfo Oscuro (Drow)": {
                "ability_bonuses": {"Carisma": 1},
                "traits": [
                    ("Visión en la Oscuridad Superior", "Tu Visión en la Oscuridad tiene un radio de 120 pies."),
                    ("Sensibilidad a la Luz Solar", "Desventaja en ataques y Percepción visual bajo luz solar directa."),
                    ("Magia Drow", "Conoces luces danzantes; fuego feérico a nivel 3 y oscuridad a nivel 5 (1/Descanso Largo, aptitud: Carisma)."),
                    ("Entrenamiento con Armas Drow", "Competencia con estoques, espadas cortas y ballestas de mano.")
                ]
            }
        },
        "traits": [
            ("Visión en la Oscuridad", "Alcance de 60 pies."),
            ("Sentidos Agudos", "Competencia en la habilidad Percepción."),
            ("Linaje Feérico", "Ventaja en salvaciones contra ser hechizado y la magia no puede dormirte."),
            ("Trance", "Meditas 4 horas al día para obtener los beneficios de 8 horas de sueño.")
        ]
    },
    "Mediano": {
        "speed": "25 pies",
        "size": "Pequeño",
        "ability_bonuses": {"Destreza": 2},
        "languages": ["Común", "Mediano"],
        "subraces": {
            "Piesligeros": {
                "ability_bonuses": {"Carisma": 1},
                "traits": [
                    ("Sigiloso por Naturaleza", "Puedes esconderte incluso tras una criatura de al menos una categoría de tamaño mayor.")
                ]
            },
            "Fornido": {
                "ability_bonuses": {"Constitución": 1},
                "traits": [
                    ("Resistencia de Fornido", "Ventaja en salvaciones contra veneno y resistencia al daño de veneno.")
                ]
            }
        },
        "traits": [
            ("Afortunado", "Cuando sacas un 1 en ataque, prueba o salvación, vuelves a tirar y usas el nuevo resultado."),
            ("Valiente", "Ventaja en tiradas de salvación para evitar ser asustado."),
            ("Agilidad de Mediano", "Puedes moverte a través del espacio de criaturas de un tamaño mayor que el tuyo.")
        ]
    },
    "Humano": {
        "speed": "30 pies",
        "size": "Mediano",
        "ability_bonuses": {},
        "languages": ["Común"],
        "subraces": {
            "Humano Estándar (+1 a todo)": {
                "ability_bonuses": {
                    "Fuerza": 1, "Destreza": 1, "Constitución": 1,
                    "Inteligencia": 1, "Sabiduría": 1, "Carisma": 1
                },
                "traits": [
                    ("Versatilidad Humana", "Todas tus puntuaciones de característica aumentan en 1.")
                ]
            },
            "Humano Alternativo (+1 a dos, 1 Habilidad, 1 Dote)": {
                "ability_bonuses": {},
                "extra_ability_picks": 2,
                "extra_skill_picks": 1,
                "traits": [
                    ("Atributos Humanos Alternativos", "Aumentas dos características en +1, ganas 1 habilidad y 1 dote a nivel 1.")
                ]
            }
        },
        "traits": [
            ("Idioma Adicional", "Hablas, lees y escribes Común y un idioma adicional a tu elección.")
        ]
    },
    "Dracónido": {
        "speed": "30 pies",
        "size": "Mediano",
        "ability_bonuses": {"Fuerza": 2, "Carisma": 1},
        "languages": ["Común", "Dracónico"],
        "subraces": {
            "Azul (Relámpago - Línea 5x30 pies)": {},
            "Blanco (Frío - Cono 15 pies)": {},
            "Bronce (Relámpago - Línea 5x30 pies)": {},
            "Cobre (Ácido - Línea 5x30 pies)": {},
            "Negro (Ácido - Línea 5x30 pies)": {},
            "Oro (Fuego - Cono 15 pies)": {},
            "Oropel (Fuego - Cono 15 pies)": {},
            "Plata (Frío - Cono 15 pies)": {},
            "Rojo (Fuego - Cono 15 pies)": {},
            "Verde (Veneno - Cono 15 pies)": {}
        },
        "traits": [
            ("Ataque de Aliento", "Acción: 2d6 de daño (3d6 en niv. 6, 4d6 en niv. 11, 5d6 en niv. 16), CD 8 + CON + Comp. (1/Descanso Corto o Largo)."),
            ("Resistencia al Daño", "Resistencia al tipo de daño asociado a tu Linaje Dracónico.")
        ]
    },
    "Gnomo": {
        "speed": "25 pies",
        "size": "Pequeño",
        "ability_bonuses": {"Inteligencia": 2},
        "languages": ["Común", "Gnomo"],
        "subraces": {
            "Gnomo de los Bosques": {
                "ability_bonuses": {"Destreza": 1},
                "traits": [
                    ("Ilusionista Innato", "Conoces el truco ilusión menor (aptitud: Inteligencia)."),
                    ("Hablar con las Bestezuelas", "Comunicas ideas sencillas a bestias Pequeñas o menores.")
                ]
            },
            "Gnomo de las Rocas": {
                "ability_bonuses": {"Constitución": 1},
                "traits": [
                    ("Saber del Artificiero", "Doblas tu competencia en Historia sobre objetos mágicos, alquímicos o tecnológicos."),
                    ("Manitas", "Competencia con herramientas de manitas para construir dispositivos de relojería.")
                ]
            }
        },
        "traits": [
            ("Visión en la Oscuridad", "Alcance de 60 pies."),
            ("Astucia Gnoma", "Ventaja en salvaciones de Inteligencia, Sabiduría y Carisma contra magia.")
        ]
    },
    "Semielfo": {
        "speed": "30 pies",
        "size": "Mediano",
        "ability_bonuses": {"Carisma": 2},
        "extra_ability_picks": 2,
        "extra_skill_picks": 2,
        "languages": ["Común", "Élfico"],
        "subraces": {},
        "traits": [
            ("Visión en la Oscuridad", "Alcance de 60 pies."),
            ("Linaje Feérico", "Ventaja en salvaciones contra ser hechizado y la magia no puede dormirte."),
            ("Versátil con Habilidades", "Ganas competencia en dos habilidades de tu elección.")
        ]
    },
    "Semiorco": {
        "speed": "30 pies",
        "size": "Mediano",
        "ability_bonuses": {"Fuerza": 2, "Constitución": 1},
        "fixed_skills": ["Intimidación"],
        "languages": ["Común", "Orco"],
        "subraces": {},
        "traits": [
            ("Visión en la Oscuridad", "Alcance de 60 pies."),
            ("Amenazador", "Eres competente en la habilidad Intimidación."),
            ("Aguante Incansable", "Cuando caes a 0 PG sin morir instantáneamente, quedas en 1 PG (1/Descanso Largo)."),
            ("Ataques Salvajes", "En un crítico cuerpo a cuerpo, tiras un dado de daño del arma adicional.")
        ]
    },
    "Tiefling": {
        "speed": "30 pies",
        "size": "Mediano",
        "ability_bonuses": {"Carisma": 2, "Inteligencia": 1},
        "languages": ["Común", "Infernal"],
        "subraces": {},
        "traits": [
            ("Visión en la Oscuridad", "Alcance de 60 pies."),
            ("Resistencia Infernal", "Posees resistencia al daño de fuego."),
            ("Linaje Infernal", "Conoces taumaturgia; reprensión infernal (niv. 2) a nivel 3 y oscuridad a nivel 5 (1/Descanso Largo, aptitud: Carisma).")
        ]
    }
}

BACKGROUNDS_5E = {
    "Acólito": {
        "skills": ["Perspicacia", "Religión"],
        "tool": "Dos idiomas adicionales",
        "feature": "Refugio del Fiel (Templos de tu fe te brindan curación y sustento modesto)"
    },
    "Animador": {
        "skills": ["Acrobacias", "Interpretación"],
        "tool": "Útiles para disfrazarse, un instrumento musical",
        "feature": "Por Petición Popular (Alojamiento y comida gratis actuando cada noche)"
    },
    "Artesano Gremial": {
        "skills": ["Perspicacia", "Persuasión"],
        "tool": "Herramientas de artesano, un idioma adicional",
        "feature": "Miembro de un Gremio (Apoyo gremial, alojamiento y contactos políticos por 5 po/mes)"
    },
    "Charlatán": {
        "skills": ["Engaño", "Juego de Manos"],
        "tool": "Útiles para disfrazarse, útiles para falsificar",
        "feature": "Identidad Falsa (Segunda identidad documentada y falsificación de documentos)"
    },
    "Criminal": {
        "skills": ["Engaño", "Sigilo"],
        "tool": "Un tipo de juego, herramientas de ladrón",
        "feature": "Contacto Criminal (Enlace de confianza con una red criminal local)"
    },
    "Ermitaño": {
        "skills": ["Medicina", "Religión"],
        "tool": "Útiles de herborista, un idioma adicional",
        "feature": "Descubrimiento (Revelación única hallada durante tu retiro)"
    },
    "Erudito": {
        "skills": ["Conocimiento Arcano", "Historia"],
        "tool": "Dos idiomas adicionales",
        "feature": "Investigador (Sabes en qué biblioteca o con quién encontrar cualquier información)"
    },
    "Héroe del Pueblo": {
        "skills": ["Supervivencia", "Trato con Animales"],
        "tool": "Herramientas de artesano, vehículos terrestres",
        "feature": "Hospitalidad Rural (El pueblo llano te oculta y da refugio)"
    },
    "Huérfano": {
        "skills": ["Juego de Manos", "Sigilo"],
        "tool": "Herramientas de ladrón, útiles para disfrazarse",
        "feature": "Secretos de la Ciudad (Viajas al doble de velocidad dentro de ciudades)"
    },
    "Marinero": {
        "skills": ["Atletismo", "Percepción"],
        "tool": "Herramientas de navegante, vehículos acuáticos",
        "feature": "Pasaje en Barco (Consigues pasaje gratis en barcos para tu grupo)"
    },
    "Noble": {
        "skills": ["Historia", "Persuasión"],
        "tool": "Un tipo de juego, un idioma adicional",
        "feature": "Posición de Privilegio (Bienvenido en alta sociedad y audiencia con nobles)"
    },
    "Salvaje": {
        "skills": ["Atletismo", "Supervivencia"],
        "tool": "Un instrumento musical, un idioma adicional",
        "feature": "Vagabundo (Memoria geográfica y consigues comida/agua diaria para 6 personas)"
    },
    "Soldado": {
        "skills": ["Atletismo", "Intimidación"],
        "tool": "Un tipo de juego, vehículos terrestres",
        "feature": "Rango Militar (Autoridad sobre soldados de menor rango y acceso a campamentos)"
    }
}

HALF_CASTER_SLOTS_5E = {
    1: {},
    2: {1: 2},
    3: {1: 3},
    4: {1: 3},
    5: {1: 4, 2: 2},
    6: {1: 4, 2: 2},
    7: {1: 4, 2: 3},
    8: {1: 4, 2: 3},
    9: {1: 4, 2: 3, 3: 2},
    10: {1: 4, 2: 3, 3: 2},
    11: {1: 4, 2: 3, 3: 3},
    12: {1: 4, 2: 3, 3: 3},
    13: {1: 4, 2: 3, 3: 3, 4: 1},
    14: {1: 4, 2: 3, 3: 3, 4: 1},
    15: {1: 4, 2: 3, 3: 3, 4: 2},
    16: {1: 4, 2: 3, 3: 3, 4: 2},
    17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2}
}

THIRD_CASTER_SLOTS_5E = {
    3: {1: 2}, 4: {1: 3}, 5: {1: 3}, 6: {1: 3},
    7: {1: 4, 2: 2}, 8: {1: 4, 2: 2}, 9: {1: 4, 2: 2},
    10: {1: 4, 2: 3}, 11: {1: 4, 2: 3}, 12: {1: 4, 2: 3},
    13: {1: 4, 2: 3, 3: 2}, 14: {1: 4, 2: 3, 3: 2}, 15: {1: 4, 2: 3, 3: 2},
    16: {1: 4, 2: 3, 3: 3}, 17: {1: 4, 2: 3, 3: 3}, 18: {1: 4, 2: 3, 3: 3},
    19: {1: 4, 2: 3, 3: 3, 4: 1}, 20: {1: 4, 2: 3, 3: 3, 4: 1}
}

FIGHTING_STYLES_5E = [
    "Combate con armas a dos manos",
    "Combate con dos armas",
    "Defensa (+1 CA con armadura)",
    "Duelo (+2 daño a una mano)",
    "Protección (Reacción con escudo a 5 pies)",
    "Tiro con arco (+2 ataque a distancia)"
]

ELD_INVOCATIONS_5E = [
    "Capa de Sombras (Armadura de mago a voluntad)",
    "Descarga Agónica (+CAR al daño de descarga sobrenatural)",
    "Descarga Ahuyentadora (Empuja 10 pies)",
    "Habla Bestial (Hablar con los animales a voluntad)",
    "Influencia Seductora (Competencia en Engaño y Persuasión)",
    "Ladrón de los Cinco Destinos (Perdición 1/DL)",
    "Lanza Sobrenatural (Alcance 300 pies)",
    "Libro de los Secretos Ancestrales (Pacto del Grimorio)",
    "Máscara de los Mil Rostros (Disfrazarse a voluntad)",
    "Mirada de las Dos Mentes",
    "Ojos del Guardián de las Runas (Leer cualquier escrito)",
    "Vigor Infernal (Falsa vida a voluntad)",
    "Visión Sobrenatural (Detectar magia a voluntad)",
    "Visiones Brumosas (Imagen silenciosa a voluntad)",
    "Vista del Diablo (Ver en oscuridad mágica 120 pies)",
    "Voz del Amo de la Cadena (Pacto de la Cadena)",
    "Enfangar la Muerte (Niv. 5)",
    "Filo Sediento (Niv. 5, Pacto del Filo)",
    "Marca del Mal Augurio (Niv. 5)",
    "Uno con las Sombras (Niv. 5)",
    "Escultor de Carne (Niv. 7)",
    "Palabra Aterradora (Niv. 7)",
    "Susurros Embrujados (Niv. 7)",
    "Esbirros del Caos (Niv. 9)",
    "Paso Ascendente (Niv. 9)",
    "Salto Sobrenatural (Niv. 9)",
    "Susurros del Sepulcro (Niv. 9)",
    "Devorador de Vida (Niv. 12, Pacto del Filo)",
    "Cadenas de Carceri (Niv. 15, Pacto de la Cadena)",
    "Maestro de las Formas Innumerables (Niv. 15)",
    "Visión Bruja (Niv. 15)",
    "Visiones de Reinos Remotos (Niv. 15)"
]

CLASSES_5E = {
    "Bárbaro": {
        "hit_die": 12,
        "saves": ["Fuerza", "Constitución"],
        "skill_choices_count": 2,
        "skill_pool": ["Atletismo", "Intimidación", "Naturaleza", "Percepción", "Supervivencia", "Trato con Animales"],
        "instruments_count": 0,
        "spellcasting": "none",
        "spell_ability": None,
        "subclass_level": 3,
        "subclasses": ["Senda del Berserker", "Senda del Guerrero Totémico"],
        "cantrips_by_level": {},
        "known_by_level": {},
        "features_by_level": {
            1: [("Furia", "Ventaja en FUE, +2 daño cuerpo a cuerpo (+3 niv. 9, +4 niv. 16), resistencia a daño físico."),
                ("Defensa sin Armadura", "CA = 10 + DES + CON (puedes usar escudo).")],
            2: [("Ataque Temerario", "Ventaja en ataques FUE este turno; los ataques contra ti tienen ventaja."),
                ("Sentir el Peligro", "Ventaja en salvaciones de DES contra efectos que puedas ver.")],
            3: [("Senda Primordial", "Eliges Senda del Berserker o Guerrero Totémico.")],
            4: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            5: [("Ataque Adicional y Movimiento Rápido", "Dos ataques por acción y +10 pies de velocidad sin armadura pesada.")],
            7: [("Instinto Salvaje", "Ventaja en iniciativa y actúas normalmente si estás sorprendido al enfurecerte.")],
            8: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            9: [("Crítico Brutal", "Tiras 1 dado adicional de daño del arma en críticos (2 en niv. 13, 3 en niv. 17).")],
            11: [("Furia Implacable", "Salvación CON CD 10 para quedar en 1 PG mientras estás enfurecido.")],
            15: [("Furia Persistente", "Tu furia solo termina si quedas inconsciente o decides finalizarla.")],
            18: [("Poderío Indómito", "Si una prueba de FUE es inferior a tu puntuación de FUE, usas tu puntuación.")],
            19: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            20: [("Campeón Primordial", "Fuerza y Constitución aumentan en +4 (máximo 24). Furias ilimitadas.")]
        },
        "subclass_features": {
            "Senda del Berserker": {
                3: [("Frenesí", "Un ataque cuerpo a cuerpo como acción adicional cada turno en furia (1 nivel de cansancio al terminar).")],
                6: [("Furia Irracional", "Inmune a ser asustado o hechizado mientras estás enfurecido.")],
                10: [("Presencia Intimidante", "Acción: asusta a una criatura a 30 pies (salvación SAB).")],
                14: [("Represalia", "Reacción: atacas a una criatura a 5 pies que te cause daño.")]
            },
            "Senda del Guerrero Totémico": {
                3: [("Buscador de Espíritus y Espíritu Totémico", "Hablar con los animales y sentidos de la bestia (ritual). Eliges Águila, Lobo u Oso.")],
                6: [("Semblanza de la Bestia", "Poder mágico totémico de Águila, Lobo u Oso.")],
                10: [("Caminante Espiritual", "Lanzas comunión con la naturaleza como ritual.")],
                14: [("Armonía Totémica", "Beneficio superior de Águila, Lobo u Oso.")]
            }
        }
    },
    "Bardo": {
        "hit_die": 8,
        "saves": ["Destreza", "Carisma"],
        "skill_choices_count": 3,
        "skill_pool": [
            "Acrobacias", "Atletismo", "Conocimiento Arcano", "Engaño", "Historia",
            "Interpretación", "Intimidación", "Investigación", "Juego de Manos",
            "Medicina", "Naturaleza", "Percepción", "Perspicacia", "Persuasión",
            "Religión", "Sigilo", "Supervivencia", "Trato con Animales"
        ],
        "instruments_count": 3,
        "spellcasting": "full",
        "spell_ability": "Carisma",
        "subclass_level": 3,
        "subclasses": ["Colegio del Conocimiento", "Colegio del Valor"],
        "cantrips_by_level": {1: 2, 4: 3, 10: 4},
        "known_by_level": {1: 4, 2: 5, 3: 6, 4: 7, 5: 8, 6: 9, 7: 10, 8: 11, 9: 12, 10: 14, 11: 15, 12: 15, 13: 16, 14: 18, 15: 19, 16: 19, 17: 20, 18: 22, 19: 22, 20: 22},
        "features_by_level": {
            1: [("Lanzamiento de Conjuros e Inspiración Bárdica (d6)", "Acción adicional: otorgas 1d6 a un aliado a 60 pies (usos = Mod. CAR por Descanso Largo).")],
            2: [("Aprendiz de Mucho", "Sumas la mitad de tu competencia a pruebas de característica sin competencia."),
                ("Canción de Descanso", "Aliados que gasten Dados de Golpe en Descanso Corto recuperan +1d6 PG (+1d8 niv. 9, +1d10 niv. 13, +1d12 niv. 17).")],
            3: [("Colegio Bárdico y Pericia", "Eliges colegio bárdico y doblas competencia en 2 habilidades.")],
            4: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            5: [("Fuente de Inspiración", "Dado de Inspiración sube a d8 y recuperas usos en Descanso Corto o Largo.")],
            6: [("Contraencantamiento", "Acción: aliados a 30 pies tienen ventaja en salvaciones contra asustado o hechizado.")],
            8: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            10: [("Pericia y Secretos Mágicos", "Dado d10, 2 nuevas pericias y aprendes 2 conjuros de cualquier clase (otros 2 en niv. 14 y 18).")],
            15: [("Inspiración Bárdica (d12)", "Tu dado de Inspiración Bárdica pasa a d12.")],
            19: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            20: [("Inspiración Superior", "Si tiras iniciativa sin usos de Inspiración Bárdica, recuperas 1.")]
        },
        "subclass_features": {
            "Colegio del Conocimiento": {
                3: [("Competencias Adicionales y Palabras Cortantes", "Ganas 3 habilidades. Reacción a 60 pies: restas tu dado de Inspiración a un ataque, prueba o daño enemigo.")],
                6: [("Secretos Mágicos Adicionales", "Aprendes 2 conjuros de cualquier clase (no cuentan contra el límite).")],
                14: [("Habilidad sin Parangón", "Sumas tu dado de Inspiración Bárdica a tus propias pruebas de característica.")]
            },
            "Colegio del Valor": {
                3: [("Competencias Adicionales e Inspiración en Combate", "Armaduras medias, escudos y armas marciales. Aliados pueden sumar Inspiración al daño o CA.")],
                6: [("Ataque Adicional", "Realizas dos ataques al usar la acción de Atacar.")],
                14: [("Magia de Batalla", "Al usar tu acción para lanzar un conjuro de bardo, atacas con arma como acción adicional.")]
            }
        }
    },
    "Brujo": {
        "hit_die": 8,
        "saves": ["Sabiduría", "Carisma"],
        "skill_choices_count": 2,
        "skill_pool": ["Conocimiento Arcano", "Engaño", "Historia", "Intimidación", "Investigación", "Naturaleza", "Religión"],
        "instruments_count": 0,
        "spellcasting": "pact",
        "spell_ability": "Carisma",
        "subclass_level": 1,
        "subclasses": ["El Infernal", "El Primigenio", "El Señor Feérico"],
        "cantrips_by_level": {1: 2, 4: 3, 10: 4},
        "known_by_level": {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 10, 11: 11, 12: 11, 13: 12, 14: 12, 15: 13, 16: 13, 17: 14, 18: 14, 19: 15, 20: 15},
        "features_by_level": {
            1: [("Patrón Sobrenatural y Magia del Pacto", "Espacios de conjuro del mismo nivel recuperables en Descanso Corto o Largo.")],
            2: [("Invocaciones Sobrenaturales", "Obtienes 2 invocaciones (3 niv. 5, 4 niv. 7, 5 niv. 9, 6 niv. 12, 7 niv. 15, 8 niv. 18).")],
            3: [("Beneficio del Pacto", "Eliges Pacto de la Cadena, Pacto del Filo o Pacto del Grimorio.")],
            4: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            11: [("Arcanum Místico", "1 conjuro de niv. 6 sin espacio (1/DL). Añades niv. 7 (13), niv. 8 (15) y niv. 9 (17).")],
            19: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            20: [("Maestro Sobrenatural", "1 minuto suplicando recupera todos tus espacios de Magia del Pacto (1/DL).")]
        },
        "subclass_features": {
            "El Infernal": {
                1: [("Bendición del Oscuro", "Al reducir a un enemigo a 0 PG, ganas PG temporales = Mod. CAR + nivel de brujo.")],
                6: [("La Suerte del Oscuro", "Añades 1d10 a una prueba de característica o salvación (1/DC o DL).")],
                10: [("Resistencia Infernal", "Tras descanso corto o largo eliges resistencia a un tipo de daño.")],
                14: [("Arrastrar por el Infierno", "Al impactar, envías al objetivo a los Planos Inferiores (10d10 psíquico, 1/DL).")]
            },
            "El Primigenio": {
                1: [("Mente Iluminada", "Telepatía a 30 pies con cualquier criatura que entienda al menos un idioma.")],
                6: [("Salvaguarda Entrópica", "Reacción: impones desventaja a un ataque contra ti; si falla, tienes ventaja en tu próximo ataque.")],
                10: [("Escudo Mental", "Tus pensamientos no pueden leerse, resistencia psíquica y reflejas daño psíquico.")],
                14: [("Crear Siervo", "Acción: tocas a un humanoide incapacitado para hechizarlo indefinidamente.")]
            },
            "El Señor Feérico": {
                1: [("Presencia Feérica", "Acción: cubo de 10 pies, salvación SAB o hechizados/asustados hasta tu siguiente turno (1/DC o DL).")],
                6: [("Escape Brumoso", "Reacción al recibir daño: te vuelves invisible y teletransportas hasta 60 pies.")],
                10: [("Defensas Seductoras", "Inmune a ser hechizado; reacción para devolver el intento de hechizo.")],
                14: [("Delirio Oscuro", "Acción a 60 pies: sumes a un objetivo en una ilusión durante 1 minuto (1/DC o DL).")]
            }
        }
    },
    "Clérigo": {
        "hit_die": 8,
        "saves": ["Sabiduría", "Carisma"],
        "skill_choices_count": 2,
        "skill_pool": ["Historia", "Medicina", "Perspicacia", "Persuasión", "Religión"],
        "instruments_count": 0,
        "spellcasting": "full",
        "spell_ability": "Sabiduría",
        "prepared_formula": "level_plus_mod",
        "subclass_level": 1,
        "subclasses": [
            "Dominio del Conocimiento", "Dominio del Engaño", "Dominio de la Guerra",
            "Dominio de la Luz", "Dominio de la Naturaleza", "Dominio de la Tempestad",
            "Dominio de la Vida"
        ],
        "cantrips_by_level": {1: 3, 4: 4, 10: 5},
        "known_by_level": {},
        "features_by_level": {
            1: [("Lanzamiento de Conjuros y Dominio Divino", "Preparas Nivel + Mod. SAB conjuros. Eliges tu Dominio Divino.")],
            2: [("Canalizar Divinidad", "Expulsar Muertos Vivientes (30 pies) y poder de Dominio (1/descanso, 2 en niv. 6, 3 en niv. 18).")],
            4: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            5: [("Destruir Muertos Vivientes", "Destruye muertos vivientes de VD 1/2 (1 en niv. 8, 2 en niv. 11, 3 en niv. 14, 4 en niv. 17).")],
            10: [("Intercesión Divina", "Tira 1d100 <= nivel de clérigo para pedir ayuda a tu deidad (éxito automático en niv. 20).")],
            19: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")]
        },
        "subclass_features": {
            "Dominio de la Vida": {
                1: [("Competencia Adicional y Discípulo de la Vida", "Armaduras pesadas. Tus conjuros de curación sanan +2 + nivel del conjuro adicionales.")],
                2: [("Canalizar Divinidad: Preservar Vida", "Acción: reparte 5 x nivel de clérigo PG entre criaturas a 30 pies (hasta mitad de PG máx.).")],
                6: [("Sanador Bendito", "Al curar a otros con un conjuro, tú recuperas 2 + nivel del conjuro PG.")],
                8: [("Golpe Divino", "+1d8 daño radiante con arma (2d8 en niv. 14).")],
                17: [("Sanación Suprema", "Tus dados de curación por conjuros siempre sacan el máximo.")]
            },
            "Dominio de la Luz": {
                1: [("Truco Adicional y Fulgor Protector", "Truco luz. Reacción a 30 pies: desventaja a un atacante (usos = Mod. SAB).")],
                2: [("Canalizar Divinidad: Resplandor del Amanecer", "Disipa oscuridad a 30 pies y 2d10 + nivel daño radiante (CON mitad).")],
                6: [("Fulgor Mejorado", "Puedes usar Fulgor Protector para proteger a aliados.")],
                8: [("Lanzamiento Potente", "Sumas tu Mod. SAB al daño de tus trucos de clérigo.")],
                17: [("Halo de Luz", "Luz brillante 60 pies; enemigos en ella tienen desventaja contra fuego y radiante.")]
            },
            "Dominio de la Guerra": {
                1: [("Competencias Adicionales y Sacerdote Guerrero", "Armas marciales y armaduras pesadas. Ataque extra como acción adicional (Mod. SAB usos/DL).")],
                2: [("Canalizar Divinidad: Golpe Guiado", "Sumas +10 a tu tirada de ataque.")],
                6: [("Bendición del Dios de la Guerra", "Reacción: sumas +10 al ataque de un aliado a 30 pies.")],
                8: [("Golpe Divino", "+1d8 daño con arma (2d8 en niv. 14).")],
                17: [("Avatar de la Batalla", "Resistencia a daño contundente, cortante y perforante no mágico.")]
            },
            "Dominio de la Tempestad": {
                1: [("Competencias Adicionales e Ira de la Tormenta", "Armas marciales y armaduras pesadas. Reacción: 2d8 relámpago/trueno al ser golpeado a 5 pies.")],
                2: [("Canalizar Divinidad: Ira Destructora", "Haces daño máximo en una tirada de relámpago o trueno.")],
                6: [("Golpe Tempestuoso", "Al causar daño de relámpago a criatura Grande o menor, la empujas 10 pies.")],
                8: [("Golpe Divino", "+1d8 daño de trueno con arma (2d8 en niv. 14).")],
                17: [("Nacido de la Tempestad", "Velocidad volando igual a tu velocidad caminando al aire libre.")]
            },
            "Dominio del Conocimiento": {
                1: [("Bendiciones del Conocimiento", "2 idiomas y doble competencia en 2 de: C. Arcano, Historia, Naturaleza o Religión.")],
                2: [("Canalizar Divinidad: Conocimientos de las Eras", "Competencia en cualquier habilidad o herramienta durante 10 min.")],
                6: [("Canalizar Divinidad: Leer Pensamientos", "Lees pensamientos a 60 pies y puedes lanzar sugestión sin espacio.")],
                8: [("Lanzamiento Potente", "Sumas tu Mod. SAB al daño de tus trucos de clérigo.")],
                17: [("Visiones del Pasado", "Meditas para ver el pasado de un objeto o de una zona de 50 pies.")]
            },
            "Dominio del Engaño": {
                1: [("Bendición del Embaucador", "Acción: tocas a un aliado para darle ventaja en Sigilo durante 1 hora.")],
                2: [("Canalizar Divinidad: Invocar Duplicidad", "Creas un duplicado ilusorio a 30 pies; lanzas conjuros desde él y ganas ventaja.")],
                6: [("Canalizar Divinidad: Capa de Sombras", "Acción: te vuelves invisible hasta tu siguiente turno.")],
                8: [("Golpe Divino", "+1d8 daño de veneno con arma (2d8 en niv. 14).")],
                17: [("Duplicidad Mejorada", "Creas hasta 4 duplicados ilusorios con Invocar Duplicidad.")]
            },
            "Dominio de la Naturaleza": {
                1: [("Acólito de la Naturaleza y Armaduras Pesadas", "1 truco de druida, 1 habilidad natural y competencia con armaduras pesadas.")],
                2: [("Canalizar Divinidad: Hechizar Animales y Plantas", "Hechizas bestias y plantas a 30 pies durante 1 minuto.")],
                6: [("Atenuar Elementos", "Reacción a 30 pies: das resistencia a ácido, frío, fuego, relámpago o trueno.")],
                8: [("Golpe Divino", "+1d8 frío, fuego o relámpago con arma (2d8 en niv. 14).")],
                17: [("Maestro de la Naturaleza", "Acción adicional para dar órdenes a bestias/plantas hechizadas.")]
            }
        }
    },
    "Druida": {
        "hit_die": 8,
        "saves": ["Inteligencia", "Sabiduría"],
        "skill_choices_count": 2,
        "skill_pool": ["Conocimiento Arcano", "Medicina", "Naturaleza", "Percepción", "Perspicacia", "Religión", "Supervivencia", "Trato con Animales"],
        "instruments_count": 0,
        "spellcasting": "full",
        "spell_ability": "Sabiduría",
        "prepared_formula": "level_plus_mod",
        "subclass_level": 2,
        "subclasses": ["Círculo de la Tierra", "Círculo de la Luna"],
        "cantrips_by_level": {1: 2, 4: 3, 10: 4},
        "known_by_level": {},
        "features_by_level": {
            1: [("Druídico y Lanzamiento de Conjuros", "Idioma secreto druídico. Preparas Nivel + Mod. SAB conjuros.")],
            2: [("Forma Salvaje y Círculo Druídico", "2 usos por descanso corto o largo (VD 1/4 niv. 2, 1/2 niv. 4, 1 niv. 8).")],
            4: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            18: [("Cuerpo Atemporal y Conjurar como Bestia", "Envejeces 10 veces más lento y lanzas conjuros sin componente material en Forma Salvaje.")],
            19: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            20: [("Archidruida", "Usos ilimitados de Forma Salvaje.")]
        },
        "subclass_features": {
            "Círculo de la Tierra": {
                2: [("Truco Adicional y Recuperación Natural", "+1 truco de druida y recuperas espacios en descanso corto (hasta mitad de nivel).")],
                6: [("Paso de la Tierra", "Ignoras terreno difícil no mágico y plantas con espinas.")],
                10: [("Protección de la Naturaleza", "Inmune a veneno, enfermedad y a ser hechizado/asustado por elementales o feéricos.")],
                14: [("Santuario de la Naturaleza", "Bestias y plantas deben superar salvación SAB para atacarte.")]
            },
            "Círculo de la Luna": {
                2: [("Forma Salvaje de Combate y Formas del Círculo", "Forma Salvaje como acción adicional, hasta VD 1; gastas espacios para curarte 1d8/nivel.")],
                6: [("Golpe Primordial", "Tus ataques en forma de bestia son mágicos y VD máx. = nivel / 3.")],
                10: [("Forma Salvaje Elemental", "Gastas 2 usos para transformarte en elemental de aire, tierra, fuego o agua.")],
                14: [("Mil Formas", "Lanzas alterar el propio aspecto a voluntad.")]
            }
        }
    },
    "Explorador": {
        "hit_die": 10,
        "saves": ["Fuerza", "Destreza"],
        "skill_choices_count": 3,
        "skill_pool": ["Atletismo", "Investigación", "Naturaleza", "Percepción", "Perspicacia", "Sigilo", "Supervivencia", "Trato con Animales"],
        "instruments_count": 0,
        "spellcasting": "half",
        "spell_ability": "Sabiduría",
        "subclass_level": 3,
        "subclasses": ["Cazador", "Señor de las Bestias"],
        "cantrips_by_level": {},
        "known_by_level": {1: 0, 2: 2, 3: 3, 4: 3, 5: 4, 6: 4, 7: 5, 8: 5, 9: 6, 10: 6, 11: 7, 12: 7, 13: 8, 14: 8, 15: 9, 16: 9, 17: 10, 18: 10, 19: 11, 20: 11},
        "features_by_level": {
            1: [("Enemigo Predilecto y Explorador Nato", "Ventaja para rastrear tu enemigo predilecto y beneficios en tu terreno predilecto.")],
            2: [("Estilo de Combate y Lanzamiento de Conjuros", "Eliges Estilo de Combate y obtienes conjuros de explorador (aptitud: Sabiduría).")],
            3: [("Arquetipo de Explorador y Percepción Primigenia", "Eliges arquetipo y detectas tipos de criaturas a 1 milla (6 en terreno predilecto).")],
            4: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            5: [("Ataque Adicional", "Dos ataques al usar la acción de Atacar.")],
            8: [("Paso de la Tierra", "Ignoras terreno difícil no mágico y plantas no mágicas.")],
            10: [("Esconderse a Plena Vista", "+10 a Sigilo tras 1 min de camuflaje mientras permanezcas quieto.")],
            14: [("Desvanecerse", "Esconderse como acción adicional y no puedes ser rastreado por medios no mágicos.")],
            18: [("Sentidos Salvajes", "Sin desventaja al atacar objetivos que no ves y detectas invisibles a 30 pies.")],
            19: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            20: [("Azote de Enemigos", "1/turno sumas tu Mod. SAB al ataque o daño contra tu enemigo predilecto.")]
        },
        "subclass_features": {
            "Cazador": {
                3: [("El Cazador y la Presa", "Eliges Asesino de Gigantes, Azote de Colosos (+1d8) o Destructor de Hordas.")],
                7: [("Tácticas Defensivas", "Eliges Defensa contra Ataques Múltiples, Escapar de la Horda o Voluntad de Acero.")],
                11: [("Ataque Múltiple", "Eliges Andanada (10 pies) o Ataque Huracanado (5 pies).")],
                15: [("Defensa de Cazador Experto", "Eliges Aguantar la Marea, Esquiva Asombrosa o Evasión.")]
            },
            "Señor de las Bestias": {
                3: [("Compañero del Explorador", "Bestia Mediana o menor de VD 1/4 o inferior que suma tu competencia.")],
                7: [("Entrenamiento Excepcional", "Acción adicional para ordenar Ayudar, Correr o Destrabarse; ataques mágicos.")],
                11: [("Furia Bestial", "Tu compañero animal realiza dos ataques con su acción de Atacar.")],
                15: [("Compartir Conjuros", "Conjuros que te tengan como objetivo afectan a tu bestia a 30 pies.")]
            }
        }
    },
    "Guerrero": {
        "hit_die": 10,
        "saves": ["Fuerza", "Constitución"],
        "skill_choices_count": 2,
        "skill_pool": ["Acrobacias", "Atletismo", "Historia", "Intimidación", "Percepción", "Perspicacia", "Supervivencia", "Trato con Animales"],
        "instruments_count": 0,
        "spellcasting": "none",
        "spell_ability": "Inteligencia",
        "subclass_level": 3,
        "subclasses": ["Campeón", "Maestro del Combate", "Caballero Arcano"],
        "cantrips_by_level": {},
        "known_by_level": {},
        "features_by_level": {
            1: [("Estilo de Combate y Tomar Aliento", "Acción adicional: recuperas 1d10 + nivel de guerrero PG (1/DC o DL).")],
            2: [("Acción Súbita", "Una acción adicional en tu turno (1/DC o DL; 2 usos en niv. 17).")],
            3: [("Arquetipo Marcial", "Eliges Campeón, Maestro del Combate o Caballero Arcano.")],
            4: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            5: [("Ataque Adicional", "2 ataques por acción (3 en niv. 11, 4 en niv. 20).")],
            6: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            9: [("Indómito", "Repites una salvación fallida (1/DL; 2 en niv. 13, 3 en niv. 17).")],
            19: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")]
        },
        "subclass_features": {
            "Campeón": {
                3: [("Crítico Mejorado", "Crítico con 19-20.")],
                7: [("Atleta Sobresaliente", "Mitad de competencia a pruebas de FUE, DES y CON sin competencia.")],
                10: [("Estilo de Combate Adicional", "Eliges un segundo Estilo de Combate.")],
                15: [("Crítico Superior", "Crítico con 18-20.")],
                18: [("Superviviente", "Recuperas 5 + Mod. CON PG al inicio del turno si tienes mitad o menos de PG.")]
            },
            "Maestro del Combate": {
                3: [("Supremacía en Combate y Estudioso de la Guerra", "4 dados de supremacía d8 y 3 maniobras (recuperan en DC/DL).")],
                7: [("Conoce a tu Enemigo", "Evalúas estadísticas de un objetivo observándolo 1 minuto.")],
                10: [("Supremacía Mejorada", "Dados de supremacía pasan a d10 (d12 en niv. 18).")],
                15: [("Incansable", "Recuperas 1 dado de supremacía al tirar iniciativa si no te quedan.")]
            },
            "Caballero Arcano": {
                3: [("Lanzamiento de Conjuros y Vínculo con Arma", "Conjuros de mago (abjuración/evocación, aptitud: INT). Invocas tu arma vinculada.")],
                7: [("Magia de Guerra", "Al lanzar un truco con tu acción, haces un ataque con arma como acción adicional.")],
                10: [("Golpe Sobrenatural", "Objetivo impactado tiene desventaja contra tu siguiente conjuro.")],
                15: [("Carga Arcana", "Te teletransportas hasta 30 pies al usar Acción Súbita.")],
                18: [("Magia de Guerra Mejorada", "Al lanzar cualquier conjuro con tu acción, atacas como acción adicional.")]
            }
        }
    },
    "Hechicero": {
        "hit_die": 6,
        "saves": ["Constitución", "Carisma"],
        "skill_choices_count": 2,
        "skill_pool": ["Conocimiento Arcano", "Engaño", "Intimidación", "Perspicacia", "Persuasión", "Religión"],
        "instruments_count": 0,
        "spellcasting": "full",
        "spell_ability": "Carisma",
        "subclass_level": 1,
        "subclasses": ["Linaje Dracónico", "Magia Salvaje"],
        "cantrips_by_level": {1: 4, 4: 5, 10: 6},
        "known_by_level": {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 11, 11: 12, 12: 12, 13: 13, 14: 13, 15: 14, 16: 14, 17: 15, 18: 15, 19: 15, 20: 15},
        "features_by_level": {
            1: [("Lanzamiento de Conjuros y Origen Mágico", "Eliges Linaje Dracónico o Magia Salvaje.")],
            2: [("Fuente de Magia", "Puntos de Hechicería = tu nivel de hechicero para crear/convertir espacios.")],
            3: [("Metamagia", "Eliges 2 opciones de Metamagia (+1 en niv. 10 y +1 en niv. 17).")],
            4: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            19: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            20: [("Recuperación Mágica", "Recuperas 4 puntos de hechicería en cada Descanso Corto.")]
        },
        "subclass_features": {
            "Linaje Dracónico": {
                1: [("Ancestro Dragón y Resistencia Dracónica", "+1 PG máximo por nivel y CA sin armadura = 13 + DES.")],
                6: [("Afinidad Elemental", "Sumas Mod. CAR al daño de tu elemento y gastas 1 PH para resistencia 1 hora.")],
                14: [("Alas de Dragón", "Acción adicional: despliegas alas con velocidad de vuelo igual a tu velocidad.")],
                18: [("Presencia Dracónica", "Gastas 5 PH: aura de 60 pies que hechiza o asusta.")]
            },
            "Magia Salvaje": {
                1: [("Sobrecarga de Magia Salvaje y Mareas del Caos", "Ganas ventaja en 1 ataque, prueba o salvación; puede activar tabla d100.")],
                6: [("Doblegar la Suerte", "Reacción + 2 PH: sumas o restas 1d4 a una tirada a la vista.")],
                14: [("Caos Controlado", "Tiras dos veces en la tabla de Magia Salvaje y eliges.")],
                18: [("Bombardeo de Conjuros", "Si sacas el máximo en un dado de daño de conjuro, tiras otro dado adicional.")]
            }
        }
    },
    "Mago": {
        "hit_die": 6,
        "saves": ["Inteligencia", "Sabiduría"],
        "skill_choices_count": 2,
        "skill_pool": ["Conocimiento Arcano", "Historia", "Investigación", "Medicina", "Perspicacia", "Religión"],
        "instruments_count": 0,
        "spellcasting": "full",
        "spell_ability": "Inteligencia",
        "prepared_formula": "level_plus_mod",
        "subclass_level": 2,
        "subclasses": [
            "Escuela de Abjuración", "Escuela de Adivinación", "Escuela de Conjuración",
            "Escuela de Encantamiento", "Escuela de Evocación", "Escuela de Ilusionismo",
            "Escuela de Nigromancia", "Escuela de Transmutación"
        ],
        "cantrips_by_level": {1: 3, 4: 4, 10: 5},
        "known_by_level": {},
        "features_by_level": {
            1: [("Libro de Conjuros y Recuperación Arcana", "Preparas Nivel + Mod. INT conjuros. Recuperas espacios en descanso corto (hasta mitad de nivel).")],
            2: [("Tradición Arcana", "Eliges una de las 8 Escuelas de Magia.")],
            4: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            18: [("Maestría sobre Conjuros", "Lanzas 1 conjuro de niv. 1 y 1 de niv. 2 a voluntad.")],
            19: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            20: [("Conjuros Característicos", "2 conjuros de niv. 3 siempre preparados, 1 lanzamiento gratis por descanso corto/largo.")]
        },
        "subclass_features": {
            "Escuela de Abjuración": {
                2: [("Experto en Abjuración y Salvaguarda Arcana", "Barrera mágica con PG = 2 x nivel de mago + Mod. INT.")],
                6: [("Salvaguarda Proyectada", "Reacción: tu salvaguarda absorbe el daño de un aliado a 30 pies.")],
                10: [("Abjuración Mejorada", "Sumas tu competencia a pruebas de contrahechizo y disipar magia.")],
                14: [("Resistencia a Conjuros", "Ventaja en salvaciones contra conjuros y resistencia al daño de conjuros.")]
            },
            "Escuela de Adivinación": {
                2: [("Experto en Adivinación y Presagio", "Tras descanso largo tiras 2d20 para sustituir cualquier tirada a la vista.")],
                6: [("Adivino Avezado", "Al lanzar adivinación de niv. 2+, recuperas un espacio inferior.")],
                10: [("El Tercer Ojo", "Acción: ganas visión oscuridad 60 pies, etérea, leer idiomas o ver invisibilidad.")],
                14: [("Presagio Mayor", "Tiras 3d20 en Presagio en lugar de 2.")]
            },
            "Escuela de Evocación": {
                2: [("Experto en Evocación y Esculpir Conjuros", "Proteges hasta 1 + nivel del conjuro criaturas de tus evocaciones de área.")],
                6: [("Truco Potente", "Tus trucos con salvación hacen mitad de daño incluso si el objetivo la supera.")],
                10: [("Evocación Potenciada", "Sumas Mod. INT a una tirada de daño de tus conjuros de evocación.")],
                14: [("Sobrecanalizar", "Infliges daño máximo en conjuros de mago de nivel 1 a 5.")]
            }
        }
    },
    "Monje": {
        "hit_die": 8,
        "saves": ["Fuerza", "Destreza"],
        "skill_choices_count": 2,
        "skill_pool": ["Acrobacias", "Atletismo", "Historia", "Perspicacia", "Religión", "Sigilo"],
        "instruments_count": 0,
        "spellcasting": "none",
        "spell_ability": "Sabiduría",
        "subclass_level": 3,
        "subclasses": ["Camino de la Mano Abierta", "Camino de la Sombra", "Camino de los Cuatro Elementos"],
        "cantrips_by_level": {},
        "known_by_level": {},
        "features_by_level": {
            1: [("Defensa sin Armadura y Artes Marciales", "CA = 10 + DES + SAB. Daño 1d4 (1d6 niv. 5, 1d8 niv. 11, 1d10 niv. 17) y ataque extra sin armas.")],
            2: [("Ki y Movimiento sin Armadura", "Puntos de ki = nivel (Ráfaga, Defensa Paciente, Paso del Viento). +10 pies velocidad (+15 niv. 6, +20 niv. 10, +25 niv. 14, +30 niv. 18).")],
            3: [("Tradición Monástica y Desviar Proyectiles", "Reacción: reduces daño a distancia en 1d10 + DES + nivel.")],
            4: [("Mejora de Característica y Caída Lenta", "Reduces daño por caída en 5 x nivel de monje.")],
            5: [("Ataque Adicional y Golpe Aturdidor", "2 ataques. Gastas 1 ki al impactar: salvación CON o aturdido.")],
            6: [("Golpes Potenciados con Ki", "Tus ataques sin armas cuentan como mágicos.")],
            7: [("Evasión y Quietud Mental", "Sin daño en salvaciones DES superadas; acción para terminar hechizado/asustado.")],
            10: [("Pureza de Cuerpo", "Inmune a enfermedades y veneno.")],
            14: [("Alma Diamantina", "Competencia en todas las tiradas de salvación y gastas 1 ki para repetir.")],
            18: [("Cuerpo Vacío", "4 ki: invisible y resistencia a todo excepto fuerza 1 min.")],
            19: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            20: [("Yo Perfecto", "Si tiras iniciativa sin ki, recuperas 4 puntos de ki.")]
        },
        "subclass_features": {
            "Camino de la Mano Abierta": {
                3: [("Técnica de la Mano Abierta", "En Ráfaga de Golpes puedes derribar, empujar 15 pies o quitar reacciones.")],
                6: [("Plenitud de Cuerpo", "Acción: recuperas 3 x nivel de monje PG (1/DL).")],
                11: [("Tranquilidad", "Efecto de santuario tras descanso largo.")],
                17: [("Palma Estremecedora", "3 ki: vibraciones letales (salvación CON o 0 PG / 10d10 necrótico).")]
            },
            "Camino de la Sombra": {
                3: [("Artes Sombrías", "2 ki: oscuridad, pasar sin rastro, silencio o visión en la oscuridad; truco ilusión menor.")],
                6: [("Paso entre Sombras", "Acción adicional: teletransporte 60 pies entre sombras con ventaja en tu ataque.")],
                11: [("Capa de Sombras", "Acción: invisible en luz tenue u oscuridad.")],
                17: [("Oportunista", "Reacción: atacas a un enemigo a 5 pies golpeado por otro.")]
            },
            "Camino de los Cuatro Elementos": {
                3: [("Discípulo de los Elementos", "Conoces Armonía con los Elementos y disciplinas elementales gastando ki.")]
            }
        }
    },
    "Paladín": {
        "hit_die": 10,
        "saves": ["Sabiduría", "Carisma"],
        "skill_choices_count": 2,
        "skill_pool": ["Atletismo", "Intimidación", "Medicina", "Perspicacia", "Persuasión", "Religión"],
        "instruments_count": 0,
        "spellcasting": "half",
        "spell_ability": "Carisma",
        "prepared_formula": "half_level_plus_mod",
        "subclass_level": 3,
        "subclasses": ["Juramento de Entrega", "Juramento de los Antiguos", "Juramento de Venganza"],
        "cantrips_by_level": {},
        "known_by_level": {},
        "features_by_level": {
            1: [("Sentidos Divinos e Imponer las Manos", "Detectas celestiales/infernales/muertos vivientes a 60 pies. Reserva de curación = 5 x nivel.")],
            2: [("Estilo de Combate, Lanzamiento de Conjuros y Castigo Divino", "Preparas (Nivel/2) + Mod. CAR conjuros. Gastas espacio al impactar: +2d8 radiante (+1d8/nivel, +1d8 vs infernal/muerto viviente).")],
            3: [("Salud Divina y Juramento Sagrado", "Inmune a enfermedades. Eliges tu Juramento y obtienes Canalizar Divinidad.")],
            4: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            5: [("Ataque Adicional", "Dos ataques al usar la acción de Atacar.")],
            6: [("Aura de Protección", "Tú y aliados a 10 pies (30 pies niv. 18) sumáis tu Mod. CAR a salvaciones.")],
            10: [("Aura de Coraje", "Tú y aliados a 10 pies (30 pies niv. 18) no podéis ser asustados.")],
            11: [("Castigo Divino Mejorado", "+1d8 de daño radiante en todos tus ataques cuerpo a cuerpo.")],
            14: [("Toque Purificador", "Acción: finalizas un conjuro en ti o un aliado (Mod. CAR usos/DL).")],
            19: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")]
        },
        "subclass_features": {
            "Juramento de Entrega": {
                3: [("Canalizar Divinidad", "Arma Sagrada (+CAR al ataque) y Expulsar lo Impío (30 pies).")],
                7: [("Aura de Entrega", "Tú y aliados a 10 pies no podéis ser hechizados.")],
                15: [("Pureza de Espíritu", "Siempre bajo protección contra el bien y el mal.")],
                20: [("Halo Sagrado", "Luz solar 30 pies que inflige 10 daño radiante por turno.")]
            },
            "Juramento de los Antiguos": {
                3: [("Canalizar Divinidad", "Ira de la Naturaleza (apresa a 10 pies) y Expulsar Infieles (feéricos/infernales).")],
                7: [("Aura de Salvaguarda", "Tú y aliados a 10 pies tenéis resistencia al daño de conjuros.")],
                15: [("Centinela Imperecedero", "Al caer a 0 PG quedas en 1 PG (1/DL).")],
                20: [("Campeón Ancestral", "Regeneras 10 PG/turno y lanzas conjuros de paladín como acción adicional.")]
            },
            "Juramento de Venganza": {
                3: [("Canalizar Divinidad", "Abjurar Enemigo (60 pies) y Voto de Enemistad (ventaja en ataques 1 min).")],
                7: [("Vengador Implacable", "Te mueves mitad de velocidad tras acertar un ataque de oportunidad.")],
                15: [("Espíritu Vengativo", "Reacción: atacas al objetivo de tu Voto de Enemistad cuando ataque.")],
                20: [("Ángel Vengador", "Alas (60 pies vuelo) y aura de amenaza de 30 pies durante 1 hora.")]
            }
        }
    },
    "Pícaro": {
        "hit_die": 8,
        "saves": ["Destreza", "Inteligencia"],
        "skill_choices_count": 4,
        "skill_pool": ["Acrobacias", "Atletismo", "Engaño", "Interpretación", "Intimidación", "Investigación", "Juego de Manos", "Percepción", "Perspicacia", "Persuasión", "Sigilo"],
        "instruments_count": 0,
        "spellcasting": "none",
        "spell_ability": "Inteligencia",
        "subclass_level": 3,
        "subclasses": ["Ladrón", "Asesino", "Embaucador Arcano"],
        "cantrips_by_level": {},
        "known_by_level": {},
        "features_by_level": {
            1: [("Pericia, Ataque Furtivo y Jerga de Ladrones", "Doblas competencia en 2 habilidades. Daño furtivo 1d6 (+1d6 cada 2 niveles).")],
            2: [("Acción Astuta", "Correr, Destrabarse o Esconderse como acción adicional.")],
            3: [("Arquetipo de Pícaro", "Eliges Ladrón, Asesino o Embaucador Arcano.")],
            4: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            5: [("Esquiva Asombrosa", "Reacción: reduces a la mitad el daño de un ataque que puedas ver.")],
            6: [("Pericia", "Eliges otras 2 competencias para doblar su bonificador.")],
            7: [("Evasión", "Sin daño al superar salvaciones de DES y mitad al fallar.")],
            11: [("Talentos Fiables", "Mínimo 10 en el d20 en cualquier prueba con competencia.")],
            14: [("Sentir sin Ver", "Detectas criaturas escondidas o invisibles a 10 pies.")],
            15: [("Mente Escurridiza", "Competencia en tiradas de salvación de Sabiduría.")],
            18: [("Elusivo", "Ninguna tirada de ataque contra ti tiene ventaja mientras no estés incapacitado.")],
            19: [("Mejora de Característica", "+2 a una característica, +1 a dos, o una dote.")],
            20: [("Golpe de Suerte", "Conviertes un ataque fallido en impacto o una prueba en 20 (1/DC o DL).")]
        },
        "subclass_features": {
            "Ladrón": {
                3: [("Manos Rápidas y Balconero", "Acción Astuta para Juego de Manos/herramientas/objetos. Trepar sin coste extra.")],
                9: [("Sigilo Supremo", "Ventaja en Sigilo si te mueves mitad o menos de tu velocidad.")],
                13: [("Usar Objetos Mágicos", "Ignoras restricciones de clase, raza y nivel en objetos mágicos.")],
                17: [("Reflejos de Ladrón", "Dos turnos en el primer asalto de combate.")]
            },
            "Asesino": {
                3: [("Competencias Adicionales y Asesinar", "Disfraz y envenenador. Ventaja contra quien no ha actuado; crítico automático a sorprendidos.")],
                9: [("Pericia en Infiltrarse", "Creas identidades falsas creíbles en 7 días por 25 po.")],
                13: [("Impostor", "Imitas habla, caligrafía y gestos tras 3 horas de estudio.")],
                17: [("Golpe Mortal", "Salvación CON o duplicas daño contra criatura sorprendida.")]
            },
            "Embaucador Arcano": {
                3: [("Lanzamiento de Conjuros y Destreza con Mano de Mago", "Conjuros de mago (encantamiento/ilusionismo, INT). Mano de mago invisible y con herramientas.")],
                9: [("Emboscada Mágica", "Estando escondido, objetivos tienen desventaja en salvaciones contra tus conjuros.")],
                13: [("Embaucador Versátil", "Acción adicional: mano de mago da ventaja en ataques a un objetivo a 5 pies.")],
                17: [("Ladrón de Conjuros", "Reacción: anulas y robas un conjuro lanzado contra ti durante 8 horas.")]
            }
        }
    }
}

SUBCLASS_ALWAYS_PREPARED_5E = {
    "Dominio del Conocimiento": {
        1: ["Identificar", "Orden imperiosa"],
        3: ["Augurio", "Sugestión"],
        5: ["Hablar con los muertos", "Indetectable"],
        7: ["Confusión", "Ojo arcano"],
        9: ["Conocer las leyendas", "Escudriñar"]
    },
    "Dominio del Engaño": {
        1: ["Disfrazarse", "Hechizar persona"],
        3: ["Imagen múltiple", "Pasar sin rastro"],
        5: ["Desplazamiento", "Disipar magia"],
        7: ["Polimorfar", "Puerta dimensional"],
        9: ["Alterar los recuerdos", "Dominar persona"]
    },
    "Dominio de la Guerra": {
        1: ["Escudo de fe", "Favor divino"],
        3: ["Arma espiritual", "Arma mágica"],
        5: ["El manto del cruzado", "Espíritus guardianes"],
        7: ["Libertad de movimiento", "Piel pétrea"],
        9: ["Golpe flamígero", "Inmovilizar monstruo"]
    },
    "Dominio de la Luz": {
        1: ["Fuego feérico", "Manos ardientes"],
        3: ["Esfera de llamas", "Rayo abrasador"],
        5: ["Bola de fuego", "Luz del día"],
        7: ["Guardián de la fe", "Muro de fuego"],
        9: ["Escudriñar", "Golpe flamígero"]
    },
    "Dominio de la Naturaleza": {
        1: ["Encantar animal", "Hablar con los animales"],
        3: ["Crecimiento espinoso", "Piel robliza"],
        5: ["Crecimiento vegetal", "Muro de viento"],
        7: ["Dominar bestia", "Enredadera"],
        9: ["Paso arbóreo", "Plaga de insectos"]
    },
    "Dominio de la Tempestad": {
        1: ["Nube de oscurecimiento", "Ola atronadora"],
        3: ["Hacer añicos", "Ráfaga de viento"],
        5: ["Llamar al relámpago", "Tormenta de aguanieve"],
        7: ["Controlar agua", "Tormenta de hielo"],
        9: ["Ola destructora", "Plaga de insectos"]
    },
    "Dominio de la Vida": {
        1: ["Bendición", "Curar heridas"],
        3: ["Arma espiritual", "Restablecimiento menor"],
        5: ["Revivir", "Señal de esperanza"],
        7: ["Guarda contra la muerte", "Guardián de la fe"],
        9: ["Alzar a los muertos", "Curar heridas en masa"]
    },
    "Juramento de Entrega": {
        3: ["Protección contra el bien y el mal", "Santuario"],
        5: ["Restablecimiento menor", "Zona de la verdad"],
        9: ["Disipar magia", "Señal de esperanza"],
        13: ["Guardián de la fe", "Libertad de movimiento"],
        17: ["Comunión", "Golpe flamígero"]
    },
    "Juramento de los Antiguos": {
        3: ["Golpe apresador", "Hablar con los animales"],
        5: ["Paso brumoso", "Rayo de luna"],
        9: ["Crecimiento vegetal", "Protección contra energía"],
        13: ["Piel pétrea", "Tormenta de hielo"],
        17: ["Comunión con la naturaleza", "Paso arbóreo"]
    },
    "Juramento de Venganza": {
        3: ["Marca del cazador", "Perdición"],
        5: ["Inmovilizar persona", "Paso brumoso"],
        9: ["Acelerar", "Protección contra energía"],
        13: ["Destierro", "Puerta dimensional"],
        17: ["Escudriñar", "Inmovilizar monstruo"]
    }
}

ARMORS_CATALOG_5E = {
    "Sin Armadura (10 + Des)": {"base_ac": 10, "dex_cap": 99, "type": "unarmored", "weight_lb": 0.0, "price": "0 po"},
    "Defensa sin Armadura Bárbaro (10 + Des + Con)": {"base_ac": 10, "dex_cap": 99, "type": "barbarian", "weight_lb": 0.0, "price": "0 po"},
    "Defensa sin Armadura Monje (10 + Des + Sab)": {"base_ac": 10, "dex_cap": 99, "type": "monk", "weight_lb": 0.0, "price": "0 po"},
    "Armadura de Mago / Dracónica (13 + Des)": {"base_ac": 13, "dex_cap": 99, "type": "light", "weight_lb": 0.0, "price": "0 po"},
    "Armadura acolchada (11 + Des)": {"base_ac": 11, "dex_cap": 99, "type": "light", "weight_lb": 8.0, "price": "5 po"},
    "Armadura de cuero (11 + Des)": {"base_ac": 11, "dex_cap": 99, "type": "light", "weight_lb": 10.0, "price": "10 po"},
    "Armadura de cuero tachonado (12 + Des)": {"base_ac": 12, "dex_cap": 99, "type": "light", "weight_lb": 13.0, "price": "45 po"},
    "Armadura de pieles (12 + Des máx. 2)": {"base_ac": 12, "dex_cap": 2, "type": "medium", "weight_lb": 12.0, "price": "10 po"},
    "Camisa de malla (13 + Des máx. 2)": {"base_ac": 13, "dex_cap": 2, "type": "medium", "weight_lb": 20.0, "price": "50 po"},
    "Cota de escamas (14 + Des máx. 2)": {"base_ac": 14, "dex_cap": 2, "type": "medium", "weight_lb": 45.0, "price": "50 po"},
    "Coraza (14 + Des máx. 2)": {"base_ac": 14, "dex_cap": 2, "type": "medium", "weight_lb": 20.0, "price": "400 po"},
    "Media armadura (15 + Des máx. 2)": {"base_ac": 15, "dex_cap": 2, "type": "medium", "weight_lb": 40.0, "price": "750 po"},
    "Cota guarnecida (14 fijo)": {"base_ac": 14, "dex_cap": 0, "type": "heavy", "weight_lb": 40.0, "price": "30 po"},
    "Cota de malla (16 fijo - Fue 13)": {"base_ac": 16, "dex_cap": 0, "type": "heavy", "weight_lb": 55.0, "price": "75 po"},
    "Armadura de bandas (17 fijo - Fue 15)": {"base_ac": 17, "dex_cap": 0, "type": "heavy", "weight_lb": 60.0, "price": "200 po"},
    "Armadura de placas (18 fijo - Fue 15)": {"base_ac": 18, "dex_cap": 0, "type": "heavy", "weight_lb": 65.0, "price": "1500 po"}
}

WEAPONS_CATALOG_5E = {
    "-- Seleccionar Arma --": {"damage": "", "ability": "Fuerza", "finesse": False, "weight_lb": 0.0, "price": "0 po"},
    "Bastón": {"damage": "1d6/1d8 contundente", "ability": "Fuerza", "finesse": False, "weight_lb": 4.0, "price": "2 pp"},
    "Daga": {"damage": "1d4 perforante (20/60 pies)", "ability": "Destreza", "finesse": True, "weight_lb": 1.0, "price": "2 po"},
    "Garrote": {"damage": "1d4 contundente", "ability": "Fuerza", "finesse": False, "weight_lb": 2.0, "price": "1 pp"},
    "Garrote grande": {"damage": "1d8 contundente", "ability": "Fuerza", "finesse": False, "weight_lb": 10.0, "price": "2 pp"},
    "Hacha de mano": {"damage": "1d6 cortante (20/60 pies)", "ability": "Fuerza", "finesse": False, "weight_lb": 2.0, "price": "5 po"},
    "Hoz": {"damage": "1d4 cortante", "ability": "Fuerza", "finesse": False, "weight_lb": 2.0, "price": "1 po"},
    "Jabalina": {"damage": "1d6 perforante (30/120 pies)", "ability": "Fuerza", "finesse": False, "weight_lb": 2.0, "price": "5 pp"},
    "Lanza": {"damage": "1d6/1d8 perforante (20/60 pies)", "ability": "Fuerza", "finesse": False, "weight_lb": 3.0, "price": "1 po"},
    "Martillo ligero": {"damage": "1d4 contundente (20/60 pies)", "ability": "Fuerza", "finesse": False, "weight_lb": 2.0, "price": "2 po"},
    "Maza": {"damage": "1d6 contundente", "ability": "Fuerza", "finesse": False, "weight_lb": 4.0, "price": "5 po"},
    "Arco corto": {"damage": "1d6 perforante (80/320 pies)", "ability": "Destreza", "finesse": False, "weight_lb": 2.0, "price": "25 po"},
    "Ballesta ligera": {"damage": "1d8 perforante (80/320 pies)", "ability": "Destreza", "finesse": False, "weight_lb": 5.0, "price": "25 po"},
    "Dardo": {"damage": "1d4 perforante (20/60 pies)", "ability": "Destreza", "finesse": True, "weight_lb": 0.25, "price": "5 pc"},
    "Honda": {"damage": "1d4 contundente (30/120 pies)", "ability": "Destreza", "finesse": False, "weight_lb": 0.0, "price": "1 pp"},
    "Alabarda": {"damage": "1d10 cortante (10 pies)", "ability": "Fuerza", "finesse": False, "weight_lb": 6.0, "price": "20 po"},
    "Cimitarra": {"damage": "1d6 cortante", "ability": "Destreza", "finesse": True, "weight_lb": 3.0, "price": "25 po"},
    "Espada corta": {"damage": "1d6 perforante", "ability": "Destreza", "finesse": True, "weight_lb": 2.0, "price": "10 po"},
    "Espada larga": {"damage": "1d8/1d10 cortante", "ability": "Fuerza", "finesse": False, "weight_lb": 3.0, "price": "15 po"},
    "Espadón": {"damage": "2d6 cortante", "ability": "Fuerza", "finesse": False, "weight_lb": 6.0, "price": "50 po"},
    "Estoque": {"damage": "1d8 perforante", "ability": "Destreza", "finesse": True, "weight_lb": 2.0, "price": "25 po"},
    "Flagelo": {"damage": "1d8 contundente", "ability": "Fuerza", "finesse": False, "weight_lb": 2.0, "price": "10 po"},
    "Guja": {"damage": "1d10 cortante (10 pies)", "ability": "Fuerza", "finesse": False, "weight_lb": 6.0, "price": "20 po"},
    "Hacha a dos manos": {"damage": "1d12 cortante", "ability": "Fuerza", "finesse": False, "weight_lb": 7.0, "price": "30 po"},
    "Hacha de guerra": {"damage": "1d8/1d10 cortante", "ability": "Fuerza", "finesse": False, "weight_lb": 4.0, "price": "10 po"},
    "Lanza de caballería": {"damage": "1d12 perforante (10 pies)", "ability": "Fuerza", "finesse": False, "weight_lb": 6.0, "price": "10 po"},
    "Látigo": {"damage": "1d4 cortante (10 pies)", "ability": "Destreza", "finesse": True, "weight_lb": 3.0, "price": "2 po"},
    "Lucero del alba": {"damage": "1d8 perforante", "ability": "Fuerza", "finesse": False, "weight_lb": 4.0, "price": "15 po"},
    "Martillo de guerra": {"damage": "1d8/1d10 contundente", "ability": "Fuerza", "finesse": False, "weight_lb": 2.0, "price": "15 po"},
    "Maza a dos manos": {"damage": "2d6 contundente", "ability": "Fuerza", "finesse": False, "weight_lb": 10.0, "price": "10 po"},
    "Pica": {"damage": "1d10 perforante (10 pies)", "ability": "Fuerza", "finesse": False, "weight_lb": 18.0, "price": "5 po"},
    "Pico de guerra": {"damage": "1d8 perforante", "ability": "Fuerza", "finesse": False, "weight_lb": 2.0, "price": "5 po"},
    "Tridente": {"damage": "1d6/1d8 perforante (20/60 pies)", "ability": "Fuerza", "finesse": False, "weight_lb": 4.0, "price": "5 po"},
    "Arco largo": {"damage": "1d8 perforante (150/600 pies)", "ability": "Destreza", "finesse": False, "weight_lb": 2.0, "price": "50 po"},
    "Ballesta de mano": {"damage": "1d6 perforante (30/120 pies)", "ability": "Destreza", "finesse": False, "weight_lb": 3.0, "price": "75 po"},
    "Ballesta pesada": {"damage": "1d10 perforante (100/400 pies)", "ability": "Destreza", "finesse": False, "weight_lb": 18.0, "price": "50 po"},
    "Cerbatana": {"damage": "1 perforante (25/100 pies)", "ability": "Destreza", "finesse": False, "weight_lb": 1.0, "price": "10 po"},
    "Red": {"damage": "Especial (5/15 pies, apresa)", "ability": "Destreza", "finesse": False, "weight_lb": 3.0, "price": "1 po"}
}

MOUNTS_CAPACITY_LB_5E = {
    "Sin Montura": 0.0,
    "Burro o mula (420 lb - 8 po)": 420.0,
    "Caballo de monta (480 lb - 75 po)": 480.0,
    "Caballo de tiro (540 lb - 50 po)": 540.0,
    "Caballo de guerra (540 lb - 400 po)": 540.0,
    "Camello (480 lb - 50 po)": 480.0,
    "Elefante (1320 lb - 200 po)": 1320.0,
    "Mastín (195 lb - 25 po)": 195.0,
    "Poni (225 lb - 30 po)": 225.0,
    "Carreta tirada (x5 capacidad)": 2100.0,
    "Carro tirado (x5 capacidad)": 2400.0
}