import math

ABILITIES = ["Fuerza", "Destreza", "Constitución", "Inteligencia", "Sabiduría", "Carisma"]

XP_THRESHOLDS_55E = {
    1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500,
    6: 14000, 7: 23000, 8: 34000, 9: 48000, 10: 64000,
    11: 85000, 12: 100000, 13: 120000, 14: 140000, 15: 165000,
    16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
}

# Tabla oficial "Monturas y otros animales" + Vehículos (Págs. 229-230)
MOUNTS_CAPACITY_KG = {
    "Sin Montura": 0.0,
    "Mula (210 kg - 8 po)": 210.0,
    "Caballo de monta (240 kg - 75 po)": 240.0,
    "Caballo de tiro (270 kg - 50 po)": 270.0,
    "Caballo de guerra (270 kg - 400 po)": 270.0,
    "Camello (225 kg - 50 po)": 225.0,
    "Elefante (660 kg - 200 po)": 660.0,
    "Mastín (97,5 kg - 25 po)": 97.5,
    "Poni (112,5 kg - 30 po)": 112.5,
    "Carreta tirada (x5 capacidad)": 1050.0,
    "Carro tirado (x5 capacidad)": 1200.0,
    "Carro de guerra": 1350.0,
    "Carruaje": 1350.0,
    "Trineo": 1050.0
}

# Propiedades de Maestría exactas del Manual del Jugador en Español (Pág. 214)
WEAPON_MASTERIES_55E = {
    "Ninguna": "Sin propiedad de maestría asignada.",
    "Debilitar": "Si aciertas a una criatura, tendrá desventaja en su próxima tirada de ataque antes del principio de tu siguiente turno.",
    "Derribar": "Si aciertas, la criatura debe superar una salvación de CON (CD 8 + Mod. ataque + Comp.) o tendrá el estado de derribada.",
    "Empujar": "Si aciertas, puedes empujar a la criatura hasta 3 m respecto a ti en línea recta si es Grande o más pequeña.",
    "Hender": "Si aciertas cuerpo a cuerpo, puedes hacer un ataque extra contra una 2da criatura a 1,5 m de la primera (sin sumar mod. al daño).",
    "Mellar": "Cuando hagas el ataque extra de la propiedad 'ligera', puedes hacerlo como parte de la acción de atacar en vez de como acción adicional (1/turno).",
    "Molestar": "Si aciertas y causas daño, tendrás ventaja en tu siguiente tirada de ataque contra esa criatura antes del final de tu siguiente turno.",
    "Ralentizar": "Si aciertas y causas daño, reduces la velocidad de la criatura en 3 m hasta el principio de tu siguiente turno (máx. 3 m).",
    "Rozar": "Si tu tirada de ataque falla, causas daño igual al modificador por característica usado para el ataque."
}

# Tabla oficial "Armaduras" (Pág. 219)
ARMORS_CATALOG_55E = {
    "Sin Armadura (10 + Des)": {"base_ac": 10, "dex_cap": 99, "type": "unarmored", "weight_kg": 0.0, "price": "0 po", "stealth": "", "str_req": 0},
    "Defensa sin Armadura Bárbaro (10 + Des + Con)": {"base_ac": 10, "dex_cap": 99, "type": "barbarian", "weight_kg": 0.0, "price": "0 po", "stealth": "", "str_req": 0},
    "Defensa sin Armadura Monje (10 + Des + Sab)": {"base_ac": 10, "dex_cap": 99, "type": "monk", "weight_kg": 0.0, "price": "0 po", "stealth": "", "str_req": 0},
    "Gracia Deslumbrante Bardo Danza (10 + Des + Car)": {"base_ac": 10, "dex_cap": 99, "type": "bard_dance", "weight_kg": 0.0, "price": "0 po", "stealth": "", "str_req": 0},
    "Armadura de Mago / Dracónica (13 + Des)": {"base_ac": 13, "dex_cap": 99, "type": "light", "weight_kg": 0.0, "price": "0 po", "stealth": "", "str_req": 0},
    # Armaduras ligeras
    "Armadura acolchada (11 + Des)": {"base_ac": 11, "dex_cap": 99, "type": "light", "weight_kg": 4.0, "price": "5 po", "stealth": "Desventaja", "str_req": 0},
    "Armadura de cuero (11 + Des)": {"base_ac": 11, "dex_cap": 99, "type": "light", "weight_kg": 5.0, "price": "10 po", "stealth": "", "str_req": 0},
    "Armadura de cuero tachonado (12 + Des)": {"base_ac": 12, "dex_cap": 99, "type": "light", "weight_kg": 6.5, "price": "45 po", "stealth": "", "str_req": 0},
    # Armaduras medias
    "Armadura de pieles (12 + Des máx. 2)": {"base_ac": 12, "dex_cap": 2, "type": "medium", "weight_kg": 6.0, "price": "10 po", "stealth": "", "str_req": 0},
    "Camisa de malla (13 + Des máx. 2)": {"base_ac": 13, "dex_cap": 2, "type": "medium", "weight_kg": 10.0, "price": "50 po", "stealth": "", "str_req": 0},
    "Cota de escamas (14 + Des máx. 2)": {"base_ac": 14, "dex_cap": 2, "type": "medium", "weight_kg": 22.5, "price": "50 po", "stealth": "Desventaja", "str_req": 0},
    "Coraza (14 + Des máx. 2)": {"base_ac": 14, "dex_cap": 2, "type": "medium", "weight_kg": 10.0, "price": "400 po", "stealth": "", "str_req": 0},
    "Media armadura (15 + Des máx. 2)": {"base_ac": 15, "dex_cap": 2, "type": "medium", "weight_kg": 20.0, "price": "750 po", "stealth": "Desventaja", "str_req": 0},
    # Armaduras pesadas
    "Cota guarnecida (14 fijo)": {"base_ac": 14, "dex_cap": 0, "type": "heavy", "weight_kg": 20.0, "price": "30 po", "stealth": "Desventaja", "str_req": 0},
    "Cota de malla (16 fijo - Fue 13)": {"base_ac": 16, "dex_cap": 0, "type": "heavy", "weight_kg": 27.5, "price": "75 po", "stealth": "Desventaja", "str_req": 13},
    "Armadura de bandas (17 fijo - Fue 15)": {"base_ac": 17, "dex_cap": 0, "type": "heavy", "weight_kg": 30.0, "price": "200 po", "stealth": "Desventaja", "str_req": 15},
    "Armadura de placas (18 fijo - Fue 15)": {"base_ac": 18, "dex_cap": 0, "type": "heavy", "weight_kg": 32.5, "price": "1500 po", "stealth": "Desventaja", "str_req": 15},
}

# Tabla oficial "Armas" completa (Pág. 215 - Las 38 armas del manual)
WEAPONS_CATALOG_55E = {
    "-- Seleccionar Arma --": {"damage": "", "ability": "Fuerza", "finesse": False, "mastery": "Ninguna", "weight_kg": 0.0, "price": "0 po", "props": ""},
    # Armas cuerpo a cuerpo sencillas
    "Bastón": {"damage": "1d6/1d8 contundente", "ability": "Fuerza", "finesse": False, "mastery": "Derribar", "weight_kg": 2.0, "price": "2 pp", "props": "Versátil (1d8)"},
    "Daga": {"damage": "1d4 perforante", "ability": "Destreza", "finesse": True, "mastery": "Mellar", "weight_kg": 0.5, "price": "2 po", "props": "Arrojadiza (6/18), ligera, sutil"},
    "Garrote": {"damage": "1d4 contundente", "ability": "Fuerza", "finesse": False, "mastery": "Ralentizar", "weight_kg": 1.0, "price": "1 pp", "props": "Ligera"},
    "Garrote grande": {"damage": "1d8 contundente", "ability": "Fuerza", "finesse": False, "mastery": "Empujar", "weight_kg": 5.0, "price": "2 pp", "props": "A dos manos"},
    "Hacha de mano": {"damage": "1d6 cortante", "ability": "Fuerza", "finesse": False, "mastery": "Molestar", "weight_kg": 1.0, "price": "5 po", "props": "Arrojadiza (6/18), ligera"},
    "Hoz": {"damage": "1d4 cortante", "ability": "Fuerza", "finesse": False, "mastery": "Mellar", "weight_kg": 1.0, "price": "1 po", "props": "Ligera"},
    "Jabalina": {"damage": "1d6 perforante", "ability": "Fuerza", "finesse": False, "mastery": "Ralentizar", "weight_kg": 1.0, "price": "5 pp", "props": "Arrojadiza (9/36)"},
    "Lanza": {"damage": "1d6/1d8 perforante", "ability": "Fuerza", "finesse": False, "mastery": "Debilitar", "weight_kg": 1.5, "price": "1 po", "props": "Arrojadiza (6/18), versátil (1d8)"},
    "Martillo ligero": {"damage": "1d4 contundente", "ability": "Fuerza", "finesse": False, "mastery": "Mellar", "weight_kg": 1.0, "price": "2 po", "props": "Arrojadiza (6/18), ligera"},
    "Maza": {"damage": "1d6 contundente", "ability": "Fuerza", "finesse": False, "mastery": "Debilitar", "weight_kg": 2.0, "price": "5 po", "props": "—"},
    # Armas a distancia sencillas
    "Arco corto": {"damage": "1d6 perforante (24/96 m)", "ability": "Destreza", "finesse": False, "mastery": "Molestar", "weight_kg": 1.0, "price": "25 po", "props": "A dos manos, munición (24/96; flecha)"},
    "Ballesta ligera": {"damage": "1d8 perforante (24/96 m)", "ability": "Destreza", "finesse": False, "mastery": "Ralentizar", "weight_kg": 2.5, "price": "25 po", "props": "A dos manos, munición (24/96; virote), recarga"},
    "Dardo": {"damage": "1d4 perforante (6/18 m)", "ability": "Destreza", "finesse": True, "mastery": "Molestar", "weight_kg": 0.125, "price": "5 pc", "props": "Arrojadiza (6/18), sutil"},
    "Honda": {"damage": "1d4 contundente (9/36 m)", "ability": "Destreza", "finesse": False, "mastery": "Ralentizar", "weight_kg": 0.0, "price": "1 pp", "props": "Munición (9/36; proyectil)"},
    # Armas cuerpo a cuerpo marciales
    "Alabarda": {"damage": "1d10 cortante", "ability": "Fuerza", "finesse": False, "mastery": "Hender", "weight_kg": 3.0, "price": "20 po", "props": "A dos manos, gran alcance (+1,5 m), pesada"},
    "Cimitarra": {"damage": "1d6 cortante", "ability": "Destreza", "finesse": True, "mastery": "Mellar", "weight_kg": 1.5, "price": "25 po", "props": "Ligera, sutil"},
    "Espada corta": {"damage": "1d6 perforante", "ability": "Destreza", "finesse": True, "mastery": "Molestar", "weight_kg": 1.0, "price": "10 po", "props": "Ligera, sutil"},
    "Espada larga": {"damage": "1d8/1d10 cortante", "ability": "Fuerza", "finesse": False, "mastery": "Debilitar", "weight_kg": 1.5, "price": "15 po", "props": "Versátil (1d10)"},
    "Espadón": {"damage": "2d6 cortante", "ability": "Fuerza", "finesse": False, "mastery": "Rozar", "weight_kg": 3.0, "price": "50 po", "props": "A dos manos, pesada"},
    "Estoque": {"damage": "1d8 perforante", "ability": "Destreza", "finesse": True, "mastery": "Molestar", "weight_kg": 1.0, "price": "25 po", "props": "Sutil"},
    "Guja": {"damage": "1d10 cortante", "ability": "Fuerza", "finesse": False, "mastery": "Rozar", "weight_kg": 3.0, "price": "20 po", "props": "A dos manos, gran alcance (+1,5 m), pesada"},
    "Hacha a dos manos": {"damage": "1d12 cortante", "ability": "Fuerza", "finesse": False, "mastery": "Hender", "weight_kg": 3.5, "price": "30 po", "props": "A dos manos, pesada"},
    "Hacha de guerra": {"damage": "1d8/1d10 cortante", "ability": "Fuerza", "finesse": False, "mastery": "Derribar", "weight_kg": 2.0, "price": "10 po", "props": "Versátil (1d10)"},
    "Lanza de caballería": {"damage": "1d10 perforante", "ability": "Fuerza", "finesse": False, "mastery": "Derribar", "weight_kg": 3.0, "price": "10 po", "props": "A dos manos (salvo montado), gran alcance, pesada"},
    "Látigo": {"damage": "1d4 cortante", "ability": "Destreza", "finesse": True, "mastery": "Ralentizar", "weight_kg": 1.5, "price": "2 po", "props": "Gran alcance (+1,5 m), sutil"},
    "Lucero del alba": {"damage": "1d8 perforante", "ability": "Fuerza", "finesse": False, "mastery": "Debilitar", "weight_kg": 2.0, "price": "15 po", "props": "—"},
    "Mangual": {"damage": "1d8 contundente", "ability": "Fuerza", "finesse": False, "mastery": "Debilitar", "weight_kg": 1.0, "price": "10 po", "props": "—"},
    "Martillo de guerra": {"damage": "1d8/1d10 contundente", "ability": "Fuerza", "finesse": False, "mastery": "Empujar", "weight_kg": 2.5, "price": "15 po", "props": "Versátil (1d10)"},
    "Maza a dos manos": {"damage": "2d6 contundente", "ability": "Fuerza", "finesse": False, "mastery": "Derribar", "weight_kg": 5.0, "price": "10 po", "props": "A dos manos, pesada"},
    "Pica": {"damage": "1d10 perforante", "ability": "Fuerza", "finesse": False, "mastery": "Empujar", "weight_kg": 9.0, "price": "5 po", "props": "A dos manos, gran alcance (+1,5 m), pesada"},
    "Pico de guerra": {"damage": "1d8/1d10 perforante", "ability": "Fuerza", "finesse": False, "mastery": "Debilitar", "weight_kg": 1.0, "price": "5 po", "props": "Versátil (1d10)"},
    "Tridente": {"damage": "1d8/1d10 perforante", "ability": "Fuerza", "finesse": False, "mastery": "Derribar", "weight_kg": 2.0, "price": "5 po", "props": "Arrojadiza (6/18), versátil (1d10)"},
    # Armas a distancia marciales
    "Arco largo": {"damage": "1d8 perforante (45/180 m)", "ability": "Destreza", "finesse": False, "mastery": "Ralentizar", "weight_kg": 1.0, "price": "50 po", "props": "A dos manos, munición (45/180; flecha), pesada"},
    "Ballesta de mano": {"damage": "1d6 perforante (9/36 m)", "ability": "Destreza", "finesse": False, "mastery": "Molestar", "weight_kg": 1.5, "price": "75 po", "props": "Ligera, munición (9/36; virote), recarga"},
    "Ballesta pesada": {"damage": "1d10 perforante (30/120 m)", "ability": "Destreza", "finesse": False, "mastery": "Empujar", "weight_kg": 9.0, "price": "50 po", "props": "A dos manos, munición (30/120; virote), pesada, recarga"},
    "Cerbatana": {"damage": "1 perforante (7,5/30 m)", "ability": "Destreza", "finesse": False, "mastery": "Molestar", "weight_kg": 0.5, "price": "10 po", "props": "Munición (7,5/30; dardo), recarga"},
    "Mosquete": {"damage": "1d12 perforante (12/36 m)", "ability": "Destreza", "finesse": False, "mastery": "Ralentizar", "weight_kg": 5.0, "price": "500 po", "props": "A dos manos, munición (12/36; bala), recarga"},
    "Pistola": {"damage": "1d10 perforante (9/27 m)", "ability": "Destreza", "finesse": False, "mastery": "Molestar", "weight_kg": 1.5, "price": "250 po", "props": "Munición (9/27; bala), recarga"}
}

# Contenido oficial de los 7 Paquetes de Equipo (Págs. 226-227) para auto-desempaquetar en contenedor
PACK_CONTENTS_55E = {
    "Paquete de artista": {
        "container": {"name": "Mochila (Paquete de artista)", "weight_kg": 2.5, "max_capacity_kg": 15.0},
        "items": [
            {"name": "Campana", "qty": 1, "weight_kg": 0.0},
            {"name": "Cantimplora", "qty": 1, "weight_kg": 2.5},
            {"name": "Disfraz", "qty": 3, "weight_kg": 2.0},
            {"name": "Espejo", "qty": 1, "weight_kg": 0.25},
            {"name": "Aceite (frasco)", "qty": 8, "weight_kg": 0.5},
            {"name": "Linterna de ojo de buey", "qty": 1, "weight_kg": 1.0},
            {"name": "Petate", "qty": 1, "weight_kg": 3.5},
            {"name": "Raciones (día)", "qty": 9, "weight_kg": 1.0},
            {"name": "Yesquero", "qty": 1, "weight_kg": 0.5},
        ]
    },
    "Paquete de diplomático": {
        "container": {"name": "Cofre (Paquete de diplomático)", "weight_kg": 12.5, "max_capacity_kg": 100.0},
        "items": [
            {"name": "Estuche para mapas o pergaminos", "qty": 2, "weight_kg": 0.5},
            {"name": "Aceite (frasco)", "qty": 4, "weight_kg": 0.5},
            {"name": "Papel (hoja)", "qty": 5, "weight_kg": 0.0},
            {"name": "Pergamino (hoja)", "qty": 5, "weight_kg": 0.0},
            {"name": "Lámpara", "qty": 1, "weight_kg": 0.5},
            {"name": "Perfume", "qty": 1, "weight_kg": 0.0},
            {"name": "Pluma", "qty": 5, "weight_kg": 0.0},
            {"name": "Ropas de calidad", "qty": 1, "weight_kg": 3.0},
            {"name": "Tinta", "qty": 1, "weight_kg": 0.0},
            {"name": "Yesquero", "qty": 1, "weight_kg": 0.5},
        ]
    },
    "Paquete de erudito": {
        "container": {"name": "Mochila (Paquete de erudito)", "weight_kg": 2.5, "max_capacity_kg": 15.0},
        "items": [
            {"name": "Aceite (frasco)", "qty": 10, "weight_kg": 0.5},
            {"name": "Pergamino (hoja)", "qty": 10, "weight_kg": 0.0},
            {"name": "Lámpara", "qty": 1, "weight_kg": 0.5},
            {"name": "Libro", "qty": 1, "weight_kg": 2.5},
            {"name": "Pluma", "qty": 1, "weight_kg": 0.0},
            {"name": "Tinta", "qty": 1, "weight_kg": 0.0},
            {"name": "Yesquero", "qty": 1, "weight_kg": 0.5},
        ]
    },
    "Paquete de explorador": {
        "container": {"name": "Mochila (Paquete de explorador)", "weight_kg": 2.5, "max_capacity_kg": 15.0},
        "items": [
            {"name": "Antorcha", "qty": 10, "weight_kg": 0.5},
            {"name": "Cantimplora", "qty": 1, "weight_kg": 2.5},
            {"name": "Cuerda", "qty": 1, "weight_kg": 2.5},
            {"name": "Aceite (frasco)", "qty": 2, "weight_kg": 0.5},
            {"name": "Petate", "qty": 1, "weight_kg": 3.5},
            {"name": "Raciones (día)", "qty": 10, "weight_kg": 1.0},
            {"name": "Yesquero", "qty": 1, "weight_kg": 0.5},
        ]
    },
    "Paquete de explorador de mazmorras": {
        "container": {"name": "Mochila (Explorador de mazmorras)", "weight_kg": 2.5, "max_capacity_kg": 15.0},
        "items": [
            {"name": "Abrojos", "qty": 1, "weight_kg": 1.0},
            {"name": "Antorcha", "qty": 10, "weight_kg": 0.5},
            {"name": "Cantimplora", "qty": 1, "weight_kg": 2.5},
            {"name": "Cuerda", "qty": 1, "weight_kg": 2.5},
            {"name": "Aceite (frasco)", "qty": 2, "weight_kg": 0.5},
            {"name": "Palanqueta", "qty": 1, "weight_kg": 2.5},
            {"name": "Raciones (día)", "qty": 10, "weight_kg": 1.0},
            {"name": "Yesquero", "qty": 1, "weight_kg": 0.5},
        ]
    },
    "Paquete de ladrón": {
        "container": {"name": "Mochila (Paquete de ladrón)", "weight_kg": 2.5, "max_capacity_kg": 15.0},
        "items": [
            {"name": "Bolas de metal", "qty": 1, "weight_kg": 1.0},
            {"name": "Campana", "qty": 1, "weight_kg": 0.0},
            {"name": "Cantimplora", "qty": 1, "weight_kg": 2.5},
            {"name": "Cuerda", "qty": 1, "weight_kg": 2.5},
            {"name": "Aceite (frasco)", "qty": 7, "weight_kg": 0.5},
            {"name": "Linterna sorda", "qty": 1, "weight_kg": 1.0},
            {"name": "Palanqueta", "qty": 1, "weight_kg": 2.5},
            {"name": "Raciones (día)", "qty": 5, "weight_kg": 1.0},
            {"name": "Vela", "qty": 10, "weight_kg": 0.0},
            {"name": "Yesquero", "qty": 1, "weight_kg": 0.5},
        ]
    },
    "Paquete de sacerdote": {
        "container": {"name": "Mochila (Paquete de sacerdote)", "weight_kg": 2.5, "max_capacity_kg": 15.0},
        "items": [
            {"name": "Agua bendita", "qty": 1, "weight_kg": 0.5},
            {"name": "Lámpara", "qty": 1, "weight_kg": 0.5},
            {"name": "Manta", "qty": 1, "weight_kg": 1.5},
            {"name": "Raciones (día)", "qty": 7, "weight_kg": 1.0},
            {"name": "Túnica", "qty": 1, "weight_kg": 2.0},
            {"name": "Yesquero", "qty": 1, "weight_kg": 0.5},
        ]
    }
}

# Catálogo Completo del Capítulo 6 dividido por Categorías Oficiales
ITEMS_CATALOG_BY_CATEGORY = {
    "Contenedores y Recipientes": [
        {"name": "Mochila", "weight_kg": 2.5, "price": "2 po", "is_container": True, "max_capacity_kg": 15.0, "desc": "Soporta hasta 15 kg en un volumen de 30 l. También sirve de alforja."},
        {"name": "Saco", "weight_kg": 0.25, "price": "1 pc", "is_container": True, "max_capacity_kg": 15.0, "desc": "Soporta hasta 15 kg en un volumen de 30 l."},
        {"name": "Cesta", "weight_kg": 1.0, "price": "4 pp", "is_container": True, "max_capacity_kg": 20.0, "desc": "Soporta hasta 20 kg en un volumen de 60 l."},
        {"name": "Bolsa", "weight_kg": 0.5, "price": "5 pp", "is_container": True, "max_capacity_kg": 3.0, "desc": "Soporta hasta 3 kg en un volumen de 6 l."},
        {"name": "Cofre", "weight_kg": 12.5, "price": "5 po", "is_container": True, "max_capacity_kg": 150.0, "desc": "Cabe un volumen de hasta 360 l de contenido."},
        {"name": "Barril", "weight_kg": 35.0, "price": "2 po", "is_container": True, "max_capacity_kg": 160.0, "desc": "Caben 160 l de líquido o 120 l de mercancías secas."},
        {"name": "Aljaba", "weight_kg": 0.5, "price": "1 po", "is_container": True, "max_capacity_kg": 2.0, "desc": "En una aljaba caben hasta 20 flechas."},
        {"name": "Estuche para virotes de ballesta", "weight_kg": 0.5, "price": "1 po", "is_container": True, "max_capacity_kg": 2.0, "desc": "Caben hasta 20 virotes."},
        {"name": "Estuche para mapas o pergaminos", "weight_kg": 0.5, "price": "1 po", "is_container": True, "max_capacity_kg": 1.0, "desc": "Caben hasta 10 hojas de papel o 5 de pergamino."},
        {"name": "Cubo", "weight_kg": 1.0, "price": "5 pc", "is_container": True, "max_capacity_kg": 15.0, "desc": "Cabe un volumen de 15 l de contenido."},
        {"name": "Saquito de componentes", "weight_kg": 1.0, "price": "25 po", "is_container": True, "max_capacity_kg": 2.0, "desc": "Bolsa hermética con compartimentos para componentes materiales gratuitos."},
        {"name": "Bolsa de Contención (Bag of Holding)", "weight_kg": 2.5, "price": "Objeto Mágico", "is_container": True, "max_capacity_kg": 225.0, "ignore_contents_weight": True, "desc": "Pesa siempre 2,5 kg sin importar lo que guardes dentro (hasta 225 kg)."},
    ],
    "Paquetes de Equipo (Auto-Desplegables)": [
        {"name": "Paquete de artista", "weight_kg": 29.25, "price": "40 po", "is_pack": True, "desc": "Se añade como Mochila desplegable con: campana, cantimplora, 3 disfraces, espejo, 8 aceites, linterna ojo de buey, petate, 9 raciones y yesquero."},
        {"name": "Paquete de diplomático", "weight_kg": 19.5, "price": "39 po", "is_pack": True, "desc": "Se añade como Cofre desplegable con: 2 estuches, 4 aceites, 5 papeles, 5 pergaminos, lámpara, perfume, 5 plumas, ropas de calidad, tinta y yesquero."},
        {"name": "Paquete de erudito", "weight_kg": 11.0, "price": "40 po", "is_pack": True, "desc": "Se añade como Mochila desplegable con: 10 aceites, 10 pergaminos, lámpara, libro, pluma, tinta y yesquero."},
        {"name": "Paquete de explorador", "weight_kg": 27.5, "price": "10 po", "is_pack": True, "desc": "Se añade como Mochila desplegable con: 10 antorchas, cantimplora, cuerda, 2 aceites, petate, 10 raciones y yesquero."},
        {"name": "Paquete de explorador de mazmorras", "weight_kg": 27.5, "price": "12 po", "is_pack": True, "desc": "Se añade como Mochila desplegable con: abrojos, 10 antorchas, cantimplora, cuerda, 2 aceites, palanqueta, 10 raciones y yesquero."},
        {"name": "Paquete de ladrón", "weight_kg": 21.0, "price": "16 po", "is_pack": True, "desc": "Se añade como Mochila desplegable con: bolas de metal, campana, cantimplora, cuerda, 7 aceites, linterna sorda, palanqueta, 5 raciones, 10 velas y yesquero."},
        {"name": "Paquete de sacerdote", "weight_kg": 14.5, "price": "33 po", "is_pack": True, "desc": "Se añade como Mochila desplegable con: agua bendita, lámpara, manta, 7 raciones, túnica y yesquero."},
    ],
    "Equipo de Aventureros": [
        {"name": "Abrojos", "weight_kg": 1.0, "price": "1 po", "desc": "Cubre zona de 1,5 m; salvación Des CD 15 o 1 daño perforante y velocidad 0."},
        {"name": "Aceite (frasco)", "weight_kg": 0.5, "price": "1 pp", "desc": "Combustible 6h o arrojar a 6 m (+5 daño de fuego al arder)."},
        {"name": "Ácido", "weight_kg": 0.5, "price": "25 po", "desc": "Arrojar a 6 m: salvación Des (CD 8+Des+Comp) o 2d6 daño de ácido."},
        {"name": "Agua bendita", "weight_kg": 0.5, "price": "25 po", "desc": "Arrojar a 6 m: 2d8 daño radiante a infernales y muertos vivientes."},
        {"name": "Antitoxina", "weight_kg": 0.0, "price": "50 po", "desc": "Acción adicional: ventaja en salvaciones contra envenenado por 1 hora."},
        {"name": "Antorcha", "weight_kg": 0.5, "price": "1 pc", "desc": "Luz brillante 6 m y tenue 6 m más durante 1h. Causa 1 daño de fuego."},
        {"name": "Ariete portátil", "weight_kg": 17.5, "price": "4 po", "desc": "+4 a pruebas de Fuerza para derribar puertas (ventaja con ayuda)."},
        {"name": "Bolas de metal", "weight_kg": 1.0, "price": "1 po", "desc": "Cubre zona de 3 m; salvación Des CD 10 o estado derribado."},
        {"name": "Botella de cristal", "weight_kg": 1.0, "price": "2 po", "desc": "Caben hasta 0,75 l de líquido."},
        {"name": "Cadena (3 m)", "weight_kg": 5.0, "price": "5 po", "desc": "Atar criatura (Fue Atletismo CD 13); escapar Des CD 18; romper Fue CD 20."},
        {"name": "Campana", "weight_kg": 0.0, "price": "1 po", "desc": "Sonido audible a 18 m de distancia."},
        {"name": "Cantimplora (llena)", "weight_kg": 2.5, "price": "2 pp", "desc": "Caben hasta 2 l de líquido."},
        {"name": "Catalejo", "weight_kg": 0.5, "price": "1000 po", "desc": "Los objetos se ven al doble de su tamaño real."},
        {"name": "Cerradura", "weight_kg": 0.5, "price": "10 po", "desc": "Forzar con herramientas de ladrón requiere Des (Juego de manos) CD 15."},
        {"name": "Cordel (3 m)", "weight_kg": 0.0, "price": "1 pp", "desc": "3 m de longitud."},
        {"name": "Cuerda", "weight_kg": 2.5, "price": "1 po", "desc": "Nudo Des CD 10; romper Fue CD 20; liberarse Acrobacias CD 15."},
        {"name": "Disfraz", "weight_kg": 2.0, "price": "5 po", "desc": "Ventaja en pruebas para hacerse pasar por la persona que representa."},
        {"name": "Escalera (3 m)", "weight_kg": 12.5, "price": "1 pp", "desc": "Escalera de 3 m de altura."},
        {"name": "Espejo", "weight_kg": 0.25, "price": "5 po", "desc": "Espejo de acero portátil (250 g) para mirar por esquinas."},
        {"name": "Esposas", "weight_kg": 3.0, "price": "2 po", "desc": "Esposar CD 13; escapar Juego de manos CD 20; romper Fue CD 25; forzar CD 15."},
        {"name": "Frasco", "weight_kg": 0.5, "price": "2 pc", "desc": "Caben hasta 0,5 l de líquido."},
        {"name": "Fuego de alquimista", "weight_kg": 0.5, "price": "50 po", "desc": "Arrojar a 6 m: salvación Des o 1d4 fuego y comienza a arder."},
        {"name": "Garfio de escalada", "weight_kg": 2.0, "price": "2 po", "desc": "Lanzar hasta 15 m (Des Acrobacias CD 13 para enganchar)."},
        {"name": "Jarro", "weight_kg": 2.0, "price": "2 pc", "desc": "Caben hasta 4 l de líquido."},
        {"name": "Lámpara", "weight_kg": 0.5, "price": "5 pp", "desc": "Luz brillante 4,5 m y tenue 9 m más con aceite."},
        {"name": "Libro", "weight_kg": 2.5, "price": "25 po", "desc": "+5 a pruebas de Inteligencia al consultar sobre su materia."},
        {"name": "Linterna de ojo de buey", "weight_kg": 1.0, "price": "10 po", "desc": "Cono de luz brillante de 18 m y tenue 18 m más."},
        {"name": "Linterna sorda", "weight_kg": 1.0, "price": "5 po", "desc": "Radio de luz brillante 9 m y tenue 9 m (tapar como acción adicional a 1,5 m)."},
        {"name": "Lupa", "weight_kg": 0.0, "price": "100 po", "desc": "Ventaja en pruebas para tasar o inspeccionar objetos muy detallados."},
        {"name": "Manta", "weight_kg": 1.5, "price": "5 pp", "desc": "Ventaja en salvaciones contra el frío extremo."},
        {"name": "Mapa", "weight_kg": 0.0, "price": "1 po", "desc": "+5 a Sabiduría (Supervivencia) para orientarse en el lugar representado."},
        {"name": "Olla de hierro", "weight_kg": 5.0, "price": "2 po", "desc": "Caben hasta 4 l."},
        {"name": "Pala", "weight_kg": 2.5, "price": "2 po", "desc": "1h de trabajo para cavar un agujero cúbico de 1,5 m de lado."},
        {"name": "Palanqueta", "weight_kg": 2.5, "price": "2 po", "desc": "Ventaja en pruebas de Fuerza donde se pueda hacer palanca."},
        {"name": "Papel (hoja)", "weight_kg": 0.0, "price": "2 pp", "desc": "Caben unas 250 palabras."},
        {"name": "Perfume", "weight_kg": 0.0, "price": "5 po", "desc": "Durante 1h da ventaja en Carisma (Persuasión) a 1,5 m."},
        {"name": "Pergamino (hoja)", "weight_kg": 0.0, "price": "1 pp", "desc": "Caben unas 250 palabras."},
        {"name": "Pergamino de conjuro (truco)", "weight_kg": 0.0, "price": "30 po", "desc": "CD salvación 13, ataque +5."},
        {"name": "Pergamino de conjuro (nivel 1)", "weight_kg": 0.0, "price": "50 po", "desc": "CD salvación 13, ataque +5."},
        {"name": "Petate", "weight_kg": 3.5, "price": "1 po", "desc": "Superas automáticamente salvaciones contra frío extremo mientras duermes."},
        {"name": "Pluma", "weight_kg": 0.0, "price": "2 pc", "desc": "Sirve para escribir o dibujar con tinta."},
        {"name": "Poción de curación", "weight_kg": 0.25, "price": "50 po", "desc": "Acción adicional: recupera 2d4 + 2 puntos de golpe (250 g)."},
        {"name": "Polipasto", "weight_kg": 2.5, "price": "1 po", "desc": "Permite levantar hasta 4 veces el peso normal."},
        {"name": "Puntas de hierro (10)", "weight_kg": 2.5, "price": "1 po", "desc": "Lote de 10 puntas para atrancar puertas o atar cuerdas."},
        {"name": "Raciones (1 día)", "weight_kg": 1.0, "price": "5 pp", "desc": "Alimentos secos de viaje para 1 día."},
        {"name": "Red", "weight_kg": 1.5, "price": "1 po", "desc": "Arrojar a 4,5 m: salvación Des o apresado (escapar Fue CD 10)."},
        {"name": "Ropas de calidad", "weight_kg": 3.0, "price": "15 po", "desc": "Indumentaria cara y ornamentada."},
        {"name": "Ropas de viaje", "weight_kg": 2.0, "price": "2 po", "desc": "Prendas resistentes diseñadas para viajar."},
        {"name": "Silbato de supervivencia", "weight_kg": 0.0, "price": "5 pc", "desc": "Produce un sonido audible a 180 m de distancia."},
        {"name": "Tienda (2 personas)", "weight_kg": 10.0, "price": "2 po", "desc": "Pueden dormir hasta dos criaturas Pequeñas o Medianas."},
        {"name": "Tinta (frasco 30 ml)", "weight_kg": 0.0, "price": "10 po", "desc": "Basta para escribir unas 500 páginas."},
        {"name": "Trampa para cazar", "weight_kg": 12.5, "price": "5 po", "desc": "Salvación Des CD 13 o 1d4 perforante y velocidad 0 (escapar Fue CD 13)."},
        {"name": "Túnica", "weight_kg": 2.0, "price": "1 po", "desc": "Prenda ceremonial o vocacional."},
        {"name": "Útiles de escalada", "weight_kg": 6.0, "price": "25 po", "desc": "Permite anclarse para no caer más de 7,5 m."},
        {"name": "Útiles de sanador (10 usos)", "weight_kg": 1.5, "price": "5 po", "desc": "Estabiliza a una criatura con 0 PG sin prueba de Medicina."},
        {"name": "Vara (3 m)", "weight_kg": 3.5, "price": "5 pc", "desc": "Vara de 3 m; da ventaja en Atletismo al saltar."},
        {"name": "Vela", "weight_kg": 0.0, "price": "1 pc", "desc": "Luz brillante 1,5 m y tenue 1,5 m más durante 1h."},
        {"name": "Veneno básico (vial)", "weight_kg": 0.0, "price": "100 po", "desc": "Acción adicional: +1d4 daño de veneno por 1 minuto."},
        {"name": "Vial", "weight_kg": 0.0, "price": "1 po", "desc": "Caben 120 ml de líquido."},
        {"name": "Yesquero", "weight_kg": 0.5, "price": "5 pp", "desc": "Acción adicional para prender antorchas, lámparas o velas."},
    ],
    "Munición, Canalizadores y Símbolos": [
        # Munición (Pág. 226)
        {"name": "Flechas (20 unidades)", "weight_kg": 0.5, "price": "1 po", "desc": "Munición para arcos (se guarda en aljaba)."},
        {"name": "Virotes de ballesta (20 unidades)", "weight_kg": 0.75, "price": "1 po", "desc": "Munición para ballestas (se guarda en estuche)."},
        {"name": "Balas de arma de fuego (10 unidades)", "weight_kg": 1.0, "price": "3 po", "desc": "Munición para pistola y mosquete."},
        {"name": "Agujas / Dardos de cerbatana (50 unidades)", "weight_kg": 0.5, "price": "1 po", "desc": "Munición para cerbatana."},
        {"name": "Proyectiles de honda (20 unidades)", "weight_kg": 0.75, "price": "4 pc", "desc": "Munición para honda."},
        # Canalizadores arcanos (Pág. 224)
        {"name": "Canalizador arcano: Bastón", "weight_kg": 2.0, "price": "5 po", "desc": "Foco para brujos, hechiceros o magos."},
        {"name": "Canalizador arcano: Cristal", "weight_kg": 0.5, "price": "10 po", "desc": "Foco para brujos, hechiceros o magos."},
        {"name": "Canalizador arcano: Orbe", "weight_kg": 1.5, "price": "20 po", "desc": "Foco para brujos, hechiceros o magos."},
        {"name": "Canalizador arcano: Vara", "weight_kg": 1.0, "price": "10 po", "desc": "Foco para brujos, hechiceros o magos."},
        {"name": "Canalizador arcano: Varita", "weight_kg": 0.5, "price": "10 po", "desc": "Foco para brujos, hechiceros o magos."},
        # Canalizadores druídicos (Pág. 224)
        {"name": "Canalizador druídico: Bastón de madera", "weight_kg": 2.0, "price": "5 po", "desc": "Foco para druidas o exploradores."},
        {"name": "Canalizador druídico: Rama de muérdago", "weight_kg": 0.0, "price": "1 po", "desc": "Foco para druidas o exploradores."},
        {"name": "Canalizador druídico: Varita de tejo", "weight_kg": 0.5, "price": "10 po", "desc": "Foco para druidas o exploradores."},
        # Símbolos sagrados (Pág. 228)
        {"name": "Símbolo sagrado: Amuleto", "weight_kg": 0.5, "price": "5 po", "desc": "Foco para clérigos o paladines."},
        {"name": "Símbolo sagrado: Emblema", "weight_kg": 0.0, "price": "5 po", "desc": "Mostrado en tela o en escudo."},
        {"name": "Símbolo sagrado: Relicario", "weight_kg": 1.0, "price": "5 po", "desc": "Foco sostenido para clérigos o paladines."},
    ],
    "Herramientas, Instrumentos y Juegos": [
        # Herramientas de artesano (Págs. 220-221)
        {"name": "Herramientas de albañil", "weight_kg": 4.0, "price": "10 po", "desc": "Fuerza | Esculpir piedra (CD 10) | Fabricar: polipasto."},
        {"name": "Herramientas de alfarero", "weight_kg": 1.5, "price": "10 po", "desc": "Inteligencia | Fabricar: jarro, lámpara."},
        {"name": "Herramientas de carpintero", "weight_kg": 3.0, "price": "8 po", "desc": "Fuerza | Sellar/forzar puerta (CD 20) | Fabricar: bastón, antorcha, cofre, escalera..."},
        {"name": "Herramientas de cartógrafo", "weight_kg": 3.0, "price": "15 po", "desc": "Sabiduría | Dibujar mapa (CD 15)."},
        {"name": "Herramientas de curtidor", "weight_kg": 2.5, "price": "5 po", "desc": "Destreza | Fabricar: armaduras de cuero, aljaba, mochila, bolsa..."},
        {"name": "Herramientas de ebanista", "weight_kg": 2.5, "price": "1 po", "desc": "Destreza | Tallar madera (CD 10) | Fabricar: arcos, flechas, virotes..."},
        {"name": "Herramientas de herrero", "weight_kg": 4.0, "price": "20 po", "desc": "Fuerza | Fabricar: armas cuerpo a cuerpo, armaduras medias y pesadas..."},
        {"name": "Herramientas de joyero", "weight_kg": 1.0, "price": "25 po", "desc": "Inteligencia | Discernir valor de gema (CD 15)."},
        {"name": "Herramientas de manitas", "weight_kg": 5.0, "price": "50 po", "desc": "Destreza | Fabricar: mosquete, pistola, cerradura, esposas, linternas..."},
        {"name": "Herramientas de soplador de vidrio", "weight_kg": 2.5, "price": "30 po", "desc": "Inteligencia | Fabricar: botella, catalejo, lupa, vial."},
        {"name": "Herramientas de tejedor", "weight_kg": 2.5, "price": "1 po", "desc": "Destreza | Fabricar: cuerda, manta, petate, red, ropas, saco, tienda..."},
        {"name": "Herramientas de zapatero", "weight_kg": 2.5, "price": "5 po", "desc": "Destreza | Modificar calzado para dar ventaja en Acrobacias (CD 10)."},
        {"name": "Suministros de alquimista", "weight_kg": 4.0, "price": "50 po", "desc": "Inteligencia | Identificar sustancia (CD 15) | Fabricar: aceite, ácido, fuego de alquimista..."},
        {"name": "Suministros de calígrafo", "weight_kg": 2.5, "price": "10 po", "desc": "Destreza | Fabricar: pergamino de conjuro, tinta."},
        {"name": "Suministros de cervecero", "weight_kg": 4.5, "price": "20 po", "desc": "Inteligencia | Detectar bebida envenenada (CD 15) | Fabricar: antitoxina."},
        {"name": "Suministros de pintor", "weight_kg": 2.5, "price": "10 po", "desc": "Sabiduría | Pintar imagen reconocible (CD 10)."},
        {"name": "Útiles de cocinero", "weight_kg": 4.0, "price": "1 po", "desc": "Sabiduría | Detectar comida envenenada (CD 15) | Fabricar: raciones."},
        # Otras herramientas (Pág. 221)
        {"name": "Herramientas de ladrón", "weight_kg": 0.5, "price": "25 po", "desc": "Destreza | Forzar cerradura (CD 15) o desarmar trampa (CD 15)."},
        {"name": "Herramientas de navegante", "weight_kg": 1.0, "price": "25 po", "desc": "Sabiduría | Trazar rumbo (CD 10) o mirar estrellas (CD 15)."},
        {"name": "Útiles de envenenador", "weight_kg": 1.0, "price": "50 po", "desc": "Inteligencia | Detectar objeto envenenado (CD 10) | Fabricar: veneno básico."},
        {"name": "Útiles de herborista", "weight_kg": 1.5, "price": "5 po", "desc": "Inteligencia | Fabricar: poción de curación, antitoxina, útiles de sanador."},
        {"name": "Útiles para disfrazarse", "weight_kg": 1.5, "price": "25 po", "desc": "Carisma | Maquillar (CD 10) | Fabricar: disfraz."},
        {"name": "Útiles para falsificar", "weight_kg": 2.5, "price": "15 po", "desc": "Destreza | Imitar letra (CD 15) o duplicar sello de cera (CD 20)."},
        # Instrumentos musicales (Pág. 221)
        {"name": "Instrumento: Chirimía", "weight_kg": 0.5, "price": "2 po", "desc": "Carisma | Tocar melodía (CD 10) o improvisar (CD 15)."},
        {"name": "Instrumento: Cuerno", "weight_kg": 1.0, "price": "3 po", "desc": "Carisma | Instrumento musical."},
        {"name": "Instrumento: Dulcémele", "weight_kg": 5.0, "price": "25 po", "desc": "Carisma | Instrumento musical."},
        {"name": "Instrumento: Flauta", "weight_kg": 0.5, "price": "2 po", "desc": "Carisma | Instrumento musical."},
        {"name": "Instrumento: Flauta de pan", "weight_kg": 1.0, "price": "12 po", "desc": "Carisma | Instrumento musical."},
        {"name": "Instrumento: Gaita", "weight_kg": 3.0, "price": "30 po", "desc": "Carisma | Instrumento musical."},
        {"name": "Instrumento: Laúd", "weight_kg": 1.0, "price": "35 po", "desc": "Carisma | Instrumento musical."},
        {"name": "Instrumento: Lira", "weight_kg": 1.0, "price": "30 po", "desc": "Carisma | Instrumento musical."},
        {"name": "Instrumento: Tambor", "weight_kg": 1.5, "price": "6 po", "desc": "Carisma | Instrumento musical."},
        {"name": "Instrumento: Viola", "weight_kg": 0.5, "price": "30 po", "desc": "Carisma | Instrumento musical."},
        # Juegos (Pág. 221)
        {"name": "Juego: Ajedrez dragón", "weight_kg": 0.0, "price": "1 po", "desc": "Sabiduría | Detectar trampas (CD 10) o ganar partida (CD 20)."},
        {"name": "Juego: Apuesta de los tres dragones", "weight_kg": 0.0, "price": "1 po", "desc": "Sabiduría | Juego de mesa."},
        {"name": "Juego: Dados", "weight_kg": 0.0, "price": "1 pp", "desc": "Sabiduría | Juego de mesa."},
        {"name": "Juego: Naipes", "weight_kg": 0.0, "price": "5 pp", "desc": "Sabiduría | Juego de mesa."},
    ],
    "Armas (Capítulo 6)": [
        {"name": k, "weight_kg": v["weight_kg"], "price": v["price"], "is_container": False, "desc": f"{v['damage']} | Maestría: {v['mastery']} | {v['props']}"}
        for k, v in WEAPONS_CATALOG_55E.items() if k != "-- Seleccionar Arma --"
    ],
    "Armaduras y Escudos (Capítulo 6)": [
        {"name": "Escudo (+2 CA)", "weight_kg": 3.0, "price": "10 po", "is_container": False, "desc": "+2 a la Clase de Armadura."},
        *[
            {"name": k.split(" (")[0], "weight_kg": v["weight_kg"], "price": v["price"], "is_container": False, "desc": f"{k} {('| Sigilo: ' + v['stealth']) if v['stealth'] else ''}"}
            for k, v in ARMORS_CATALOG_55E.items() if v["weight_kg"] > 0
        ]
    ],
    "Arreos, Sillas y Vehículos (Pág. 230)": [
        {"name": "Alimento para montura (por día)", "weight_kg": 5.0, "price": "5 pc", "desc": "Comida diaria para un animal de monta o tiro."},
        {"name": "Silla de monta", "weight_kg": 12.5, "price": "10 po", "desc": "Incluye bocado, bridas y riendas."},
        {"name": "Silla militar", "weight_kg": 15.0, "price": "20 po", "desc": "Da ventaja en pruebas para permanecer montado."},
        {"name": "Silla exótica", "weight_kg": 20.0, "price": "60 po", "desc": "Necesaria para monturas acuáticas o voladoras."},
        {"name": "Bote de remos", "weight_kg": 50.0, "price": "50 po", "desc": "Velocidad 2,25 km/h; 1 tripulante + 3 pasajeros."},
        {"name": "Carreta", "weight_kg": 100.0, "price": "15 po", "desc": "Vehículo tirado por animales."},
        {"name": "Carro", "weight_kg": 200.0, "price": "35 po", "desc": "Vehículo tirado por animales."},
        {"name": "Carro de guerra", "weight_kg": 50.0, "price": "250 po", "desc": "Vehículo ligero de combate."},
        {"name": "Carruaje", "weight_kg": 300.0, "price": "100 po", "desc": "Vehículo cerrado tirado por animales."},
        {"name": "Trineo", "weight_kg": 150.0, "price": "20 po", "desc": "Vehículo para nieve o hielo."},
    ]
}

SKILLS_55E = [
    ("Acrobacias", "Destreza"),
    ("Atletismo", "Fuerza"),
    ("Conocimiento Arcano", "Inteligencia"),
    ("Engaño", "Carisma"),
    ("Historia", "Inteligencia"),
    ("Interpretación", "Carisma"),
    ("Intimidación", "Carisma"),
    ("Investigación", "Inteligencia"),
    ("Juego de Manos", "Destreza"),
    ("Medicina", "Sabiduría"),
    ("Naturaleza", "Inteligencia"),
    ("Percepción", "Sabiduría"),
    ("Perspicacia", "Sabiduría"),
    ("Persuasión", "Carisma"),
    ("Religión", "Inteligencia"),
    ("Sigilo", "Destreza"),
    ("Supervivencia", "Sabiduría"),
    ("Trato con Animales", "Sabiduría"),
]

LANGUAGES_55E = [
    "Común", "Lengua de Signos Común", "Dracónico", "Enano", "Élfico",
    "Gigante", "Gnomo", "Goblin", "Mediano", "Orco",
    "Abisal", "Celestial", "Infernal", "Primordial", "Silvano", "Infracomún"
]

MUSICAL_INSTRUMENTS = [
    "Chirimía", "Cuerno", "Dulcémele", "Flauta", "Flauta de pan",
    "Gaita", "Laúd", "Lira", "Tambor", "Viola"
]

GAMING_SETS = ["Ajedrez dragón", "Apuesta de los tres dragones", "Dados", "Naipes"]

SPECIES_55E = {
    "Humano": {
        "speed": "9 m", "size": "Mediano",
        "traits": [
            ("Ingenioso (Resourceful)", "Ganas Inspiración Heroica siempre que terminas un Descanso Largo."),
            ("Habilidoso (Skillful)", "Ganas competencia en una habilidad de tu elección."),
            ("Versátil (Versatile)", "Ganas una Dote de Origen adicional de tu elección en nivel 1.")
        ]
    },
    "Aasimar": {
        "speed": "9 m", "size": "Mediano",
        "traits": [
            ("Visión en la Oscuridad", "Puedes ver en luz tenue hasta 18 m como si fuera luz brillante."),
            ("Resistencia Celestial", "Tienes resistencia al daño Necrótico y Radiante."),
            ("Manos Sanadoras", "Acción Mágica: tocas a una criatura y tiras tantos d4 como tu Bono de Competencia para curarla (1/Descanso Largo)."),
            ("Portador de Luz", "Conoces el truco Luz (Carisma)."),
            ("Revelación Celestial (Niv. 3)", "En nivel 3 puedes transformarte durante 1 minuto.")
        ]
    },
    "Dracónido": {
        "speed": "9 m", "size": "Mediano",
        "traits": [
            ("Linaje Dracónico", "Define el tipo de daño de tu aliento y tu resistencia elemental."),
            ("Arma de Aliento", "Reemplaza un ataque por un cono de 4,5 m o línea de 9 m (1d10 en niv 1, 2d10 en niv 5, 3d10 en niv 11, 4d10 en niv 17)."),
            ("Resistencia al Daño", "Resistencia al tipo de daño de tu Linaje Dracónico."),
            ("Visión en la Oscuridad", "Alcance de 18 m."),
            ("Vuelo Dracónico (Niv. 5)", "A partir de nivel 5, como Acción Adicional despliegas alas espectrales durante 10 minutos.")
        ]
    },
    "Enano": {
        "speed": "9 m", "size": "Mediano",
        "traits": [
            ("Visión en la Oscuridad Superior", "Alcance de 36 m en oscuridad."),
            ("Resistencia Enana", "Resistencia al daño de Veneno y Ventaja en salvaciones contra el estado Envenenado."),
            ("Dureza Enana (Dwarven Toughness)", "Tus Puntos de Golpe máximos aumentan en 1 por cada nivel que tengas."),
            ("Afinidad con la Piedra (Stonecunning)", "Como Acción Adicional ganas Sentido de la Vibración a 18 m sobre piedra durante 10 min.")
        ]
    },
    "Elfo": {
        "speed": "9 m", "size": "Mediano",
        "traits": [
            ("Visión en la Oscuridad", "Alcance de 18 m."),
            ("Linaje Élfico", "Drow, Alto Elfo o Elfo del Bosque con conjuros por nivel (Niv 1, 3 y 5)."),
            ("Ascendencia Feérica", "Ventaja en salvaciones para evitar o terminar el estado Hechizado."),
            ("Sentidos Agudos", "Ganas competencia en Perspicacia, Percepción o Supervivencia."),
            ("Trance", "Completas un Descanso Largo en 4 horas de meditación consciente.")
        ]
    },
    "Gnomo": {
        "speed": "9 m", "size": "Pequeño",
        "traits": [
            ("Visión en la Oscuridad", "Alcance de 18 m."),
            ("Astucia Gnoma", "Tienes Ventaja en las tiradas de salvación de Inteligencia, Sabiduría y Carisma."),
            ("Linaje Gnomo", "Gnomo del Bosque o Gnomo de las Rocas.")
        ]
    },
    "Goliat": {
        "speed": "10,5 m", "size": "Mediano",
        "traits": [
            ("Ancestría Gigante", "Don sobrenatural usable tantas veces como tu Bono de Competencia."),
            ("Forma Grande (Niv. 5)", "En nivel 5 puedes cambiar tu tamaño a Grande durante 10 min (+3 m velocidad y ventaja en FUE)."),
            ("Complexión Poderosa", "Cuentas como un tamaño mayor para tu capacidad de carga.")
        ]
    },
    "Mediano": {
        "speed": "9 m", "size": "Pequeño",
        "traits": [
            ("Valiente (Brave)", "Tienes Ventaja en las tiradas de salvación para evitar o terminar el estado Asustado."),
            ("Agilidad Mediana", "Puedes moverte a través del espacio de cualquier criatura que sea de un tamaño mayor que el tuyo."),
            ("Suerte (Luck)", "Cuando sacas un 1 en el d20 de una Prueba de d20, puedes volver a tirar el dado y usar el nuevo resultado."),
            ("Sigiloso Naturalmente", "Puedes Esconderte incluso cuando solo estás oscurecido por una criatura al menos un tamaño mayor que tú.")
        ]
    },
    "Orco": {
        "speed": "9 m", "size": "Mediano",
        "traits": [
            ("Subidón de Adrenalina", "Puedes Correr (Dash) como Acción Adicional y ganas PG Temporales = Bono de Competencia."),
            ("Visión en la Oscuridad Superior", "Alcance de 36 m."),
            ("Resistencia Implacable", "Cuando caes a 0 PG puedes quedar en 1 PG en su lugar (1/Descanso Largo).")
        ]
    },
    "Tiefling": {
        "speed": "9 m", "size": "Mediano",
        "traits": [
            ("Visión en la Oscuridad", "Alcance de 18 m."),
            ("Legado Infernal", "Linaje Abisal, Chtónico o Infernal con trucos y conjuros en niveles 1, 3 y 5."),
            ("Presencia de Otro Mundo", "Conoces el truco Taumaturgia.")
        ]
    }
}

BACKGROUNDS_55E = {
    "Acólito": {"abilities": ["Inteligencia", "Sabiduría", "Carisma"], "feat": "Iniciado en la Magia (Clérigo)", "skills": ["Perspicacia", "Religión"], "tool": "Suministros de calígrafo"},
    "Artesano": {"abilities": ["Fuerza", "Destreza", "Inteligencia"], "feat": "Reparador (Crafter)", "skills": ["Investigación", "Persuasión"], "tool": "Herramientas de artesano"},
    "Charlatán": {"abilities": ["Destreza", "Constitución", "Carisma"], "feat": "Habilidoso (Skilled)", "skills": ["Engaño", "Juego de Manos"], "tool": "Útiles para falsificar"},
    "Criminal": {"abilities": ["Destreza", "Constitución", "Inteligencia"], "feat": "Alerta (Alert)", "skills": ["Juego de Manos", "Sigilo"], "tool": "Herramientas de ladrón"},
    "Animador (Entertainer)": {"abilities": ["Fuerza", "Destreza", "Carisma"], "feat": "Músico (Musician)", "skills": ["Acrobacias", "Interpretación"], "tool": "Instrumento musical"},
    "Granjero": {"abilities": ["Fuerza", "Constitución", "Sabiduría"], "feat": "Duro (Tough)", "skills": ["Naturaleza", "Trato con Animales"], "tool": "Herramientas de carpintero"},
    "Guardia": {"abilities": ["Fuerza", "Inteligencia", "Sabiduría"], "feat": "Alerta (Alert)", "skills": ["Atletismo", "Percepción"], "tool": "Juego"},
    "Guía": {"abilities": ["Destreza", "Constitución", "Sabiduría"], "feat": "Iniciado en la Magia (Druida)", "skills": ["Sigilo", "Supervivencia"], "tool": "Herramientas de cartógrafo"},
    "Ermitaño": {"abilities": ["Constitución", "Sabiduría", "Carisma"], "feat": "Sanador (Healer)", "skills": ["Medicina", "Religión"], "tool": "Útiles de herborista"},
    "Mercader": {"abilities": ["Constitución", "Inteligencia", "Carisma"], "feat": "Afortunado (Lucky)", "skills": ["Persuasión", "Trato con Animales"], "tool": "Herramientas de navegante"},
    "Noble": {"abilities": ["Fuerza", "Inteligencia", "Carisma"], "feat": "Habilidoso (Skilled)", "skills": ["Historia", "Persuasión"], "tool": "Juego"},
    "Sabio": {"abilities": ["Constitución", "Inteligencia", "Sabiduría"], "feat": "Iniciado en la Magia (Mago)", "skills": ["Conocimiento Arcano", "Historia"], "tool": "Suministros de calígrafo"},
    "Marinero": {"abilities": ["Fuerza", "Destreza", "Sabiduría"], "feat": "Matón de Taberna (Tavern Brawler)", "skills": ["Acrobacias", "Percepción"], "tool": "Herramientas de navegante"},
    "Escriba": {"abilities": ["Destreza", "Inteligencia", "Sabiduría"], "feat": "Habilidoso (Skilled)", "skills": ["Investigación", "Percepción"], "tool": "Suministros de calígrafo"},
    "Soldado": {"abilities": ["Fuerza", "Destreza", "Constitución"], "feat": "Atacante Salvaje (Savage Attacker)", "skills": ["Atletismo", "Intimidación"], "tool": "Juego"},
    "Huérfano (Wayfarer)": {"abilities": ["Destreza", "Sabiduría", "Carisma"], "feat": "Afortunado (Lucky)", "skills": ["Perspicacia", "Sigilo"], "tool": "Herramientas de ladrón"}
}

CLASSES_55E = {
    "Bardo": {
        "hit_die": 8, "saves": ["Destreza", "Carisma"], "skill_choices_count": 3,
        "skill_pool": [sk[0] for sk in SKILLS_55E], "instruments_count": 3,
        "spellcasting": "full", "spell_ability": "Carisma",
        "cantrips_by_level": {1: 2, 4: 3, 10: 4},
        "prepared_by_level": {1: 4, 2: 5, 3: 6, 4: 7, 5: 9, 6: 10, 7: 11, 8: 12, 9: 14, 10: 15, 11: 16, 12: 16, 13: 17, 14: 17, 15: 18, 16: 18, 17: 19, 18: 20, 19: 21, 20: 22},
        "subclasses": ["Colegio de la Danza", "Colegio del Glamour", "Colegio del Conocimiento (Lore)", "Colegio del Valor"],
        "features_by_level": {
            1: [("Inspiración Bárdica (d6)", "Acción Adicional: otorgas un dado a una criatura a 18 m (usos = Mod. CAR por Descanso Largo)."),
                ("Lanzamiento de Conjuros", "Usas Carisma como aptitud mágica e instrumentos como foco.")],
            2: [("Pericia (Expertise)", "Doblas tu Bono de Competencia en 2 habilidades en las que seas competente."),
                ("Aprendiz de Todo (Jack of All Trades)", "Sumas la mitad de tu Bono de Competencia a pruebas de habilidad sin competencia.")],
            3: [("Subclase de Bardo", "Obtienes los rasgos de nivel 3 de tu Colegio Bárdico elegido.")],
            4: [("Mejora de Característica / Dote", "Aumentas atributos en +2 o eliges una Dote General.")],
            5: [("Fuente de Inspiración (Font of Inspiration)", "Tu dado de Inspiración Bárdica sube a d8 y recuperas todos los usos en un Descanso Corto o Largo.")],
            6: [("Rasgo de Colegio Bárdico (Niv. 6)", "Obtienes el rasgo de nivel 6 de tu subclase.")],
            7: [("Contraencantamiento (Countercharm)", "Reacción cuando tú o un aliado a 9 m fallen una salvación contra Hechizado o Asustado: repiten con Ventaja.")],
            8: [("Mejora de Característica / Dote (Niv. 8)", "Aumentas atributos en +2 o eliges una Dote General.")],
            9: [("Pericia Adicional", "Eliges otras 2 habilidades para doblar su Bono de Competencia.")],
            10: [("Inspiración Bárdica (d10) y Secretos Mágicos", "Tu dado sube a d10 y puedes elegir conjuros de Clérigo, Druida y Mago.")],
            14: [("Rasgo Superior de Colegio Bárdico (Niv. 14)", "Obtienes el rasgo culminante de tu subclase.")],
            15: [("Inspiración Bárdica (d12)", "Tu dado de Inspiración Bárdica sube a d12.")],
            18: [("Inspiración Superior", "Al tirar Iniciativa, si tienes menos de 2 usos de Inspiración Bárdica, recuperas hasta tener 2.")],
            19: [("Don Épico (Epic Boon)", "Obtienes una Dote de Don Épico.")],
            20: [("Palabras de la Creación", "Siempre tienes preparados Palabra de Poder: Sanar y Palabra de Poder: Matar.")]
        },
        "subclass_features": {
            "Colegio del Glamour": {
                3: [("Magia Seductora (Beguiling Magic)", "Siempre tienes preparados Hechizar Persona e Imagen Múltiple. Al lanzar Encantamiento o Ilusión puedes Hechizar/Asustar a 18 m."),
                    ("Manto de Inspiración (Mantle of Inspiration)", "Acción Adicional + 1 Inspiración Bárdica: aliados a 18 m ganan PG Temporales (2d6 + Mod. CAR) y se mueven como Reacción sin provocar ataques de oportunidad.")],
                6: [("Manto de Majestad (Mantle of Majesty)", "Siempre tienes preparado Orden Imperiosa (Command) y puedes lanzarlo como Acción Adicional cada turno durante 1 minuto.")],
                14: [("Majestad Inquebrantable (Unbreakable Majesty)", "Acción Adicional (1 min): quien te ataque debe superar salvación de CAR o fallar el ataque.")]
            },
            "Colegio del Conocimiento (Lore)": {
                3: [("Competencias Adicionales y Palabras Cortantes", "Ganas 3 habilidades y usas tu Reacción para restar tu dado de Inspiración Bárdica a un enemigo a 18 m.")],
                6: [("Descubrimientos Mágicos", "Aprendes 2 conjuros adicionales de Clérigo, Druida o Mago.")],
                14: [("Habilidad sin Igual", "Sumas tu dado de Inspiración Bárdica cuando fallas una prueba.")]
            },
            "Colegio del Valor": {
                3: [("Entrenamiento Marcial e Inspiración de Combate", "Competencia con armaduras medias, escudos y armas marciales; suma Inspiración a CA o daño.")],
                6: [("Ataque Extra", "Atacas dos veces y puedes sustituir un ataque por un Truco.")],
                14: [("Magia de Batalla", "Tras lanzar un conjuro con una acción, haces un ataque como Acción Adicional.")]
            },
            "Colegio de la Danza": {
                3: [("Gracia Deslumbrante", "CA sin armadura = 10 + DES + CAR y golpes desarmados ágiles.")],
                6: [("Movimiento en Tándem", "Sumas Inspiración Bárdica a la Iniciativa del grupo.")],
                14: [("Evasión Lírica", "Evasión compartida con aliados adyacentes a 1,5 m.")]
            }
        }
    },
    "Bárbaro": {
        "hit_die": 12, "saves": ["Fuerza", "Constitución"], "skill_choices_count": 2,
        "skill_pool": ["Atletismo", "Intimidación", "Naturaleza", "Percepción", "Supervivencia", "Trato con Animales"],
        "instruments_count": 0, "spellcasting": "none", "spell_ability": None,
        "cantrips_by_level": {}, "prepared_by_level": {},
        "subclasses": ["Senda del Berserker", "Senda del Corazón Salvaje", "Senda del Árbol del Mundo", "Senda del Fanático (Zealot)"],
        "features_by_level": {
            1: [("Furia, Defensa sin Armadura y Maestría de Armas", "Resistencia física en Furia, CA = 10 + DES + CON y 2 maestrías.")],
            2: [("Ataque Temerario y Sentido del Peligro", "Ventaja en ataques FUE y salvaciones DES.")],
            3: [("Subclase de Bárbaro y Conocimiento Primigenio", "Rasgos de senda y +1 habilidad.")],
            4: [("Mejora de Característica / Dote", "+2 a atributos o Dote General.")],
            5: [("Ataque Extra y Movimiento Rápido", "2 ataques y +3 m de velocidad.")],
            7: [("Instinto Salvaje", "Ventaja en Iniciativa.")],
            8: [("Mejora de Característica / Dote (Niv. 8)", "+2 a atributos o Dote General.")]
        },
        "subclass_features": {}
    },
    "Brujo": {
        "hit_die": 8, "saves": ["Sabiduría", "Carisma"], "skill_choices_count": 2,
        "skill_pool": ["Conocimiento Arcano", "Engaño", "Historia", "Intimidación", "Investigación", "Naturaleza", "Religión"],
        "instruments_count": 0, "spellcasting": "pact", "spell_ability": "Carisma",
        "cantrips_by_level": {1: 2, 4: 3, 10: 4},
        "prepared_by_level": {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 10, 11: 11, 12: 11, 13: 12, 14: 12, 15: 13, 16: 13, 17: 14, 18: 14, 19: 15, 20: 15},
        "subclasses": ["Patrón Archihada", "Patrón Celestial", "Patrón Infernal (Fiend)", "Patrón Primigenio (Great Old One)"],
        "features_by_level": {
            1: [("Invocaciones Sobrenaturales y Magia del Pacto", "Espacios recuperables en Descanso Corto.")],
            2: [("Astucia Mágica", "Rito de 1 min para recuperar mitad de espacios (1/Descanso Largo).")],
            3: [("Subclase de Brujo", "Dones de tu Patrón.")],
            4: [("Mejora de Característica / Dote", "+2 a atributos o Dote General.")],
            8: [("Mejora de Característica / Dote (Niv. 8)", "+2 a atributos o Dote General.")]
        },
        "subclass_features": {}
    },
    "Clérigo": {
        "hit_die": 8, "saves": ["Sabiduría", "Carisma"], "skill_choices_count": 2,
        "skill_pool": ["Historia", "Medicina", "Perspicacia", "Persuasión", "Religión"],
        "instruments_count": 0, "spellcasting": "full", "spell_ability": "Sabiduría",
        "cantrips_by_level": {1: 3, 4: 4, 10: 5},
        "prepared_by_level": {1: 4, 2: 5, 3: 6, 4: 7, 5: 9, 6: 10, 7: 11, 8: 12, 9: 14, 10: 15, 11: 16, 12: 16, 13: 17, 14: 17, 15: 18, 16: 18, 17: 19, 18: 20, 19: 21, 20: 22},
        "subclasses": ["Dominio de la Vida", "Dominio de la Luz", "Dominio del Engaño", "Dominio de la Guerra"],
        "features_by_level": {
            1: [("Orden Divina y Lanzamiento de Conjuros", "Protector o Taumaturgo.")],
            2: [("Canalizar Divinidad", "Chispa Divina y Expulsar Muertos Vivientes.")],
            3: [("Subclase de Clérigo", "Dominio Divino.")],
            4: [("Mejora de Característica / Dote", "+2 a atributos o Dote General.")],
            5: [("Destruir Muertos Vivientes", "Daño radiante al expulsar.")],
            7: [("Golpes Benditos", "+1d8 a armas o suma SAB a trucos.")],
            8: [("Mejora de Característica / Dote (Niv. 8)", "+2 a atributos o Dote General.")]
        },
        "subclass_features": {}
    },
    "Druida": {
        "hit_die": 8, "saves": ["Inteligencia", "Sabiduría"], "skill_choices_count": 2,
        "skill_pool": ["Conocimiento Arcano", "Medicina", "Naturaleza", "Percepción", "Perspicacia", "Religión", "Supervivencia", "Trato con Animales"],
        "instruments_count": 0, "spellcasting": "full", "spell_ability": "Sabiduría",
        "cantrips_by_level": {1: 2, 4: 3, 10: 4},
        "prepared_by_level": {1: 4, 2: 5, 3: 6, 4: 7, 5: 9, 6: 10, 7: 11, 8: 12, 9: 14, 10: 15, 11: 16, 12: 16, 13: 17, 14: 17, 15: 18, 16: 18, 17: 19, 18: 20, 19: 21, 20: 22},
        "subclasses": ["Círculo de la Tierra", "Círculo de la Luna", "Círculo del Mar", "Círculo de las Estrellas"],
        "features_by_level": {
            1: [("Druídico y Orden Primigenia", "Guardián o Mago.")],
            2: [("Forma Salvaje y Compañero Salvaje", "Transformación en bestia como Acción Adicional.")],
            3: [("Subclase de Druida", "Círculo Druídico.")],
            4: [("Mejora de Característica / Dote", "+2 a atributos o Dote General.")],
            8: [("Mejora de Característica / Dote (Niv. 8)", "+2 a atributos o Dote General.")]
        },
        "subclass_features": {}
    },
    "Explorador": {
        "hit_die": 10, "saves": ["Fuerza", "Destreza"], "skill_choices_count": 3,
        "skill_pool": ["Atletismo", "Investigación", "Naturaleza", "Percepción", "Perspicacia", "Sigilo", "Supervivencia", "Trato con Animales"],
        "instruments_count": 0, "spellcasting": "half", "spell_ability": "Sabiduría",
        "cantrips_by_level": {},
        "prepared_by_level": {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 6, 7: 7, 8: 7, 9: 9, 10: 9, 11: 10, 12: 10, 13: 11, 14: 11, 15: 12, 16: 12, 17: 14, 18: 14, 19: 15, 20: 15},
        "subclasses": ["Señor de las Bestias", "Errante Feérico", "Acechador en la Penumbra (Gloom Stalker)", "Cazador"],
        "features_by_level": {
            1: [("Enemigo Predilecto y Maestría de Armas", "Marca del Cazador y 2 maestrías.")],
            2: [("Explorador Hábil y Estilo de Combate", "Pericia en 1 habilidad.")],
            3: [("Subclase de Explorador", "Arquetipo de Explorador.")],
            5: [("Ataque Extra", "2 ataques por acción.")],
            6: [("Errante", "+3 m velocidad y trepar/nadar.")],
            8: [("Mejora de Característica / Dote (Niv. 8)", "+2 a atributos o Dote General.")]
        },
        "subclass_features": {}
    },
    "Guerrero": {
        "hit_die": 10, "saves": ["Fuerza", "Constitución"], "skill_choices_count": 2,
        "skill_pool": ["Acrobacias", "Atletismo", "Historia", "Intimidación", "Percepción", "Perspicacia", "Supervivencia", "Trato con Animales"],
        "instruments_count": 0, "spellcasting": "none", "spell_ability": "Inteligencia",
        "cantrips_by_level": {}, "prepared_by_level": {},
        "subclasses": ["Maestro de Batalla", "Campeón", "Caballero Arcano (Eldritch Knight)", "Guerrero Psiónico"],
        "features_by_level": {
            1: [("Estilo de Combate, Tomar Aliento y Maestría de Armas", "Recupera 1d10+Niv PG y 3 maestrías.")],
            2: [("Oleada de Acción y Mente Táctica", "Acción extra 1/Descanso Corto.")],
            3: [("Subclase de Guerrero", "Arquetipo Marcial.")],
            5: [("Ataque Extra y Cambio Táctico", "2 ataques por acción.")],
            6: [("Mejora de Característica Adicional (Niv. 6)", "Dote o +2 extra.")],
            8: [("Mejora de Característica / Dote (Niv. 8)", "+2 a atributos o Dote General.")]
        },
        "subclass_features": {}
    },
    "Hechicero": {
        "hit_die": 6, "saves": ["Constitución", "Carisma"], "skill_choices_count": 2,
        "skill_pool": ["Conocimiento Arcano", "Engaño", "Intimidación", "Perspicacia", "Persuasión", "Religión"],
        "instruments_count": 0, "spellcasting": "full", "spell_ability": "Carisma",
        "cantrips_by_level": {1: 4, 4: 5, 10: 6},
        "prepared_by_level": {1: 2, 2: 4, 3: 6, 4: 7, 5: 9, 6: 10, 7: 11, 8: 12, 9: 14, 10: 15, 11: 16, 12: 16, 13: 17, 14: 17, 15: 18, 16: 18, 17: 19, 18: 20, 19: 21, 20: 22},
        "subclasses": ["Hechicería Aberrante", "Hechicería Mecánica (Clockwork)", "Hechicería Dracónica", "Magia Salvaje"],
        "features_by_level": {
            1: [("Hechicería Innata y Lanzamiento de Conjuros", "+1 CD y ventaja en ataques mágicos.")],
            2: [("Fuente de Magia y Metamagia", "Puntos de Hechicería = Nivel.")],
            3: [("Subclase de Hechicero", "Origen Hechicero.")],
            8: [("Mejora de Característica / Dote (Niv. 8)", "+2 a atributos o Dote General.")]
        },
        "subclass_features": {}
    },
    "Mago": {
        "hit_die": 6, "saves": ["Inteligencia", "Sabiduría"], "skill_choices_count": 2,
        "skill_pool": ["Conocimiento Arcano", "Historia", "Investigación", "Medicina", "Naturaleza", "Religión"],
        "instruments_count": 0, "spellcasting": "full", "spell_ability": "Inteligencia",
        "cantrips_by_level": {1: 3, 4: 4, 10: 5},
        "prepared_by_level": {1: 4, 2: 5, 3: 6, 4: 7, 5: 9, 6: 10, 7: 11, 8: 12, 9: 14, 10: 15, 11: 16, 12: 16, 13: 17, 14: 18, 15: 19, 16: 21, 17: 22, 18: 23, 19: 24, 20: 25},
        "subclasses": ["Abjurador", "Adivino", "Evocador", "Ilusionista"],
        "features_by_level": {
            1: [("Libro de Conjuros y Recuperación Arcana", "Recupera espacios en Descanso Corto.")],
            2: [("Erudito", "Pericia en una habilidad académica.")],
            3: [("Subclase de Mago", "Tradición Arcana.")],
            8: [("Mejora de Característica / Dote (Niv. 8)", "+2 a atributos o Dote General.")]
        },
        "subclass_features": {}
    },
    "Monje": {
        "hit_die": 8, "saves": ["Fuerza", "Destreza"], "skill_choices_count": 2,
        "skill_pool": ["Acrobacias", "Atletismo", "Historia", "Perspicacia", "Religión", "Sigilo"],
        "instruments_count": 0, "spellcasting": "none", "spell_ability": "Sabiduría",
        "cantrips_by_level": {}, "prepared_by_level": {},
        "subclasses": ["Guerrero de la Mano Abierta", "Guerrero de la Sombra", "Guerrero de los Elementos", "Guerrero de la Misericordia"],
        "features_by_level": {
            1: [("Artes Marciales y Defensa sin Armadura", "CA = 10 + DES + SAB.")],
            2: [("Concentración del Monje y Movimiento sin Armadura", "Puntos de Concentración = Nivel.")],
            3: [("Desviar Ataques y Subclase", "Reacción defensiva.")],
            5: [("Ataque Extra y Golpe Aturdidor", "2 ataques por acción.")],
            8: [("Mejora de Característica / Dote (Niv. 8)", "+2 a atributos o Dote General.")]
        },
        "subclass_features": {}
    },
    "Paladín": {
        "hit_die": 10, "saves": ["Sabiduría", "Carisma"], "skill_choices_count": 2,
        "skill_pool": ["Atletismo", "Intimidación", "Medicina", "Perspicacia", "Persuasión", "Religión"],
        "instruments_count": 0, "spellcasting": "half", "spell_ability": "Carisma",
        "cantrips_by_level": {},
        "prepared_by_level": {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 6, 7: 7, 8: 7, 9: 9, 10: 9, 11: 10, 12: 10, 13: 11, 14: 11, 15: 12, 16: 12, 17: 14, 18: 14, 19: 15, 20: 15},
        "subclasses": ["Juramento de Devoción", "Juramento de Gloria", "Juramento de los Antiguos", "Juramento de Venganza"],
        "features_by_level": {
            1: [("Imposición de Manos y Maestría de Armas", "Reserva = 5 × Nivel.")],
            2: [("Castigo del Paladín y Estilo de Combate", "Castigo Divino preparado.")],
            3: [("Canalizar Divinidad y Juramento Sagrado", "Subclase de Paladín.")],
            5: [("Ataque Extra y Corcel Fiel", "2 ataques por acción.")],
            6: [("Aura de Protección", "+Mod CAR a salvaciones a 3 m.")],
            8: [("Mejora de Característica / Dote (Niv. 8)", "+2 a atributos o Dote General.")]
        },
        "subclass_features": {}
    },
    "Pícaro": {
        "hit_die": 8, "saves": ["Destreza", "Inteligencia"], "skill_choices_count": 4,
        "skill_pool": ["Acrobacias", "Atletismo", "Engaño", "Intimidación", "Investigación", "Juego de Manos", "Percepción", "Perspicacia", "Persuasión", "Sigilo"],
        "instruments_count": 0, "spellcasting": "none", "spell_ability": "Inteligencia",
        "cantrips_by_level": {}, "prepared_by_level": {},
        "subclasses": ["Bribón Arcano", "Asesino", "Hoja del Alma (Soulknife)", "Ladrón"],
        "features_by_level": {
            1: [("Pericia, Ataque Furtivo y Maestría de Armas", "Daño furtivo y 2 maestrías.")],
            2: [("Acción Astuta", "Correr, Destrabarse o Esconderse como Acción Adicional.")],
            3: [("Subclase de Pícaro y Apuntar Fijo", "Ventaja en ataque si no te mueves.")],
            5: [("Golpes Astutos y Esquiva Asombrosa", "Efectos tácticos en furtivo.")],
            7: [("Evasión y Talento Fiable", "Mínimo 10 en el d20 en habilidades con competencia.")],
            8: [("Mejora de Característica / Dote (Niv. 8)", "+2 a atributos o Dote General.")]
        },
        "subclass_features": {}
    }
}

SPELLS_CATALOG_55E = [
    {"name": "Burla Dañina (Vicious Mockery)", "level": 0, "school": "Encantamiento", "classes": ["Bardo"]},
    {"name": "Cuchilla Protectora (Blade Ward)", "level": 0, "school": "Abjuración", "classes": ["Bardo", "Brujo", "Hechicero", "Mago"]},
    {"name": "Luces Danzantes (Dancing Lights)", "level": 0, "school": "Evocación", "classes": ["Bardo", "Hechicero", "Mago"]},
    {"name": "Amigos (Friends)", "level": 0, "school": "Encantamiento", "classes": ["Bardo", "Brujo", "Hechicero", "Mago"]},
    {"name": "Luz (Light)", "level": 0, "school": "Evocación", "classes": ["Bardo", "Clérigo", "Hechicero", "Mago"]},
    {"name": "Mano de Mago (Mage Hand)", "level": 0, "school": "Conjuración", "classes": ["Bardo", "Brujo", "Hechicero", "Mago"]},
    {"name": "Remendar (Mending)", "level": 0, "school": "Transmutación", "classes": ["Bardo", "Clérigo", "Druida", "Hechicero", "Mago"]},
    {"name": "Mensaje (Message)", "level": 0, "school": "Transmutación", "classes": ["Bardo", "Druida", "Hechicero", "Mago"]},
    {"name": "Ilusión Menor (Minor Illusion)", "level": 0, "school": "Ilusión", "classes": ["Bardo", "Brujo", "Hechicero", "Mago"]},
    {"name": "Prestidigitación", "level": 0, "school": "Transmutación", "classes": ["Bardo", "Brujo", "Hechicero", "Mago"]},
    {"name": "Fuego fatuo Estelar (Starry Wisp)", "level": 0, "school": "Evocación", "classes": ["Bardo", "Druida"]},
    {"name": "Trueno (Thunderclap)", "level": 0, "school": "Evocación", "classes": ["Bardo", "Brujo", "Druida", "Hechicero", "Mago"]},
    {"name": "Descarga de Fuego (Fire Bolt)", "level": 0, "school": "Evocación", "classes": ["Hechicero", "Mago"]},
    {"name": "Descarga Sobrenatural (Eldritch Blast)", "level": 0, "school": "Evocación", "classes": ["Brujo"]},
    {"name": "Llama Sagrada (Sacred Flame)", "level": 0, "school": "Evocación", "classes": ["Clérigo"]},
    {"name": "Guía (Guidance)", "level": 0, "school": "Adivinación", "classes": ["Clérigo", "Druida"]},
    {"name": "Palabra Curativa (Healing Word)", "level": 1, "school": "Abjuración", "classes": ["Bardo", "Clérigo", "Druida"]},
    {"name": "Curar Heridas (Cure Wounds)", "level": 1, "school": "Abjuración", "classes": ["Bardo", "Clérigo", "Druida", "Explorador", "Paladín"]},
    {"name": "Fuego Feérico (Faerie Fire)", "level": 1, "school": "Evocación", "classes": ["Bardo", "Druida"]},
    {"name": "Onda Atronadora (Thunderwave)", "level": 1, "school": "Evocación", "classes": ["Bardo", "Druida", "Hechicero", "Mago"]},
    {"name": "Susurros Disonantes (Dissonant Whispers)", "level": 1, "school": "Encantamiento", "classes": ["Bardo"]},
    {"name": "Risa Horrible de Tasha", "level": 1, "school": "Encantamiento", "classes": ["Bardo", "Brujo", "Mago"]},
    {"name": "Dormir (Sleep)", "level": 1, "school": "Encantamiento", "classes": ["Bardo", "Hechicero", "Mago"]},
    {"name": "Hechizar Persona (Charm Person)", "level": 1, "school": "Encantamiento", "classes": ["Bardo", "Brujo", "Druida", "Hechicero", "Mago"]},
    {"name": "Disfrazarse (Disguise Self)", "level": 1, "school": "Ilusión", "classes": ["Bardo", "Hechicero", "Mago"]},
    {"name": "Detectar Magia (Detect Magic)", "level": 1, "school": "Adivinación", "classes": ["Bardo", "Clérigo", "Druida", "Explorador", "Hechicero", "Mago", "Paladín"]},
    {"name": "Proyectil Mágico (Magic Missile)", "level": 1, "school": "Evocación", "classes": ["Hechicero", "Mago"]},
    {"name": "Escudo (Shield)", "level": 1, "school": "Abjuración", "classes": ["Hechicero", "Mago"]},
    {"name": "Bendición (Bless)", "level": 1, "school": "Encantamiento", "classes": ["Clérigo", "Paladín"]},
    {"name": "Invisibilidad", "level": 2, "school": "Ilusión", "classes": ["Bardo", "Brujo", "Hechicero", "Mago"]},
    {"name": "Hacer Añicos (Shatter)", "level": 2, "school": "Evocación", "classes": ["Bardo", "Hechicero", "Mago"]},
    {"name": "Inmovilizar Persona (Hold Person)", "level": 2, "school": "Encantamiento", "classes": ["Bardo", "Brujo", "Clérigo", "Druida", "Hechicero", "Mago"]},
    {"name": "Calentar Metal (Heat Metal)", "level": 2, "school": "Transmutación", "classes": ["Bardo", "Druida"]},
    {"name": "Paso Brumoso (Misty Step)", "level": 2, "school": "Conjuración", "classes": ["Brujo", "Hechicero", "Mago"]},
    {"name": "Patrón Hipnótico (Hypnotic Pattern)", "level": 3, "school": "Ilusión", "classes": ["Bardo", "Brujo", "Hechicero", "Mago"]},
    {"name": "Disipar Magia (Dispel Magic)", "level": 3, "school": "Abjuración", "classes": ["Bardo", "Brujo", "Clérigo", "Druida", "Hechicero", "Mago", "Paladín"]},
    {"name": "Bola de Fuego (Fireball)", "level": 3, "school": "Evocación", "classes": ["Hechicero", "Mago"]},
    {"name": "Contrahechizo (Counterspell)", "level": 3, "school": "Abjuración", "classes": ["Brujo", "Hechicero", "Mago"]},
    {"name": "Polimorfar (Polymorph)", "level": 4, "school": "Transmutación", "classes": ["Bardo", "Druida", "Hechicero", "Mago"]},
    {"name": "Invisibilidad Mayor (Greater Invisibility)", "level": 4, "school": "Ilusión", "classes": ["Bardo", "Hechicero", "Mago"]},
    {"name": "Puerta Dimensional (Dimension Door)", "level": 4, "school": "Conjuración", "classes": ["Bardo", "Brujo", "Hechicero", "Mago"]},
]


# Tablas oficiales de Espacios de Conjuro por Nivel (Manual del Jugador 2024, Págs. 45, 60, 70, 82, 92, 104)
FULL_CASTER_SLOTS_55E = {
    1:  {1: 2},
    2:  {1: 3},
    3:  {1: 4, 2: 2},
    4:  {1: 4, 2: 3},
    5:  {1: 4, 2: 3, 3: 2},
    6:  {1: 4, 2: 3, 3: 3},
    7:  {1: 4, 2: 3, 3: 3, 4: 1},
    8:  {1: 4, 2: 3, 3: 3, 4: 2},
    9:  {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
    18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1},
}

HALF_CASTER_SLOTS_55E = {
    1:  {1: 2},
    2:  {1: 2},
    3:  {1: 3},
    4:  {1: 3},
    5:  {1: 4, 2: 2},
    6:  {1: 4, 2: 2},
    7:  {1: 4, 2: 3},
    8:  {1: 4, 2: 3},
    9:  {1: 4, 2: 3, 3: 2},
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
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
}

# Brujo: Magia del Pacto (cantidad de espacios, nivel de los espacios) - Pág. 70
WARLOCK_PACT_SLOTS_55E = {
    1: (1, 1), 2: (2, 1), 3: (2, 2), 4: (2, 2), 5: (2, 3),
    6: (2, 3), 7: (2, 4), 8: (2, 4), 9: (2, 5), 10: (2, 5),
    11: (3, 5), 12: (3, 5), 13: (3, 5), 14: (3, 5), 15: (3, 5),
    16: (3, 5), 17: (4, 5), 18: (4, 5), 19: (4, 5), 20: (4, 5)
}

# Linajes y Opciones de Especie (Cap. 4)
SPECIES_LINEAGES_55E = {
    "Elfo": ["Drow (Visión 36 m, Luces danzantes, Fuego feérico N3, Oscuridad N5)",
             "Alto Elfo (Prestidigitación, Detectar magia N3, Paso brumoso N5)",
             "Elfo del Bosque (Vel. 10,5 m, Saber druídico, Zancada prodigiosa N3, Pasar sin rastro N5)"],
    "Dracónido": ["Azul (Relámpago)", "Blanco (Frío)", "Bronce (Relámpago)", "Cobre (Ácido)",
                  "Latón (Fuego)", "Negro (Ácido)", "Oro (Fuego)", "Plata (Frío)", "Rojo (Fuego)", "Verde (Veneno)"],
    "Gnomo": ["Gnomo del Bosque (Ilusión menor, Hablar con los animales)",
              "Gnomo de las Rocas (Reparar, Prestidigitación)"],
    "Goliat": [" Aguante de la Piedra", "Acometida del Fuego", "Abrazo de la Escarcha",
               "Derribo de la Colina", "Salto de la Nube", "Trueno de la Tormenta"],
    "Tiefling": ["Legado Abisal (Veneno, Rociada venenosa, Rayo nauseabundo N3, Inmovilizar persona N5)",
                 "Legado Chtónico (Necrótico, Toque helado, Falsa vida N3, Rayo debilitador N5)",
                 "Legado Infernal (Fuego, Descarga de fuego, Reprensión infernal N3, Oscuridad N5)"]
}

# Opciones de Invocaciones Sobrenaturales de Brujo (Págs. 71-73)
ELD_INVOCATIONS_55E = [
    "Armadura de sombras", "Pacto de la cadena", "Pacto del filo", "Pacto del grimorio",
    "Mente sobrenatural", "Descarga agónica (Niv 2+)", "Descarga ahuyentadora (Niv 2+)",
    "Lanza sobrenatural (Niv 2+)", "Lecciones de los primeros (Niv 2+)", "Máscara de los mil rostros (Niv 2+)",
    "Salto sobrenatural (Niv 2+)", "Vigor infernal (Niv 2+)", "Visiones brumosas (Niv 2+)", "Vista del diablo (Niv 2+)",
    "Castigo arcano (Niv 5+)", "Don de las profundidades (Niv 5+)", "Filo sediento (Niv 5+)",
    "Inversión del amo de las cadenas (Niv 5+)", "Maestro de las formas innumerables (Niv 5+)",
    "Mirada de las dos mentes (Niv 5+)", "Paso ascendente (Niv 5+)", "Uno con las sombras (Niv 5+)",
    "Susurros del sepulcro (Niv 7+)", "Devorador de vida (Niv 9+)", "Don de los protectores (Niv 9+)",
    "Visiones de reinos remotos (Niv 9+)", "Hoja devoradora (Niv 12+)", "Visión bruja (Niv 15+)"
]

FIGHTING_STYLES_55E = [
    "Arquería (+2 ataque a distancia)", "Combate con armas grandes", "Combate con dos armas",
    "Defensa (+1 CA con armadura)", "Duelo (+2 daño a una mano)", "Intercepción",
    "Lucha a ciegas (Visión ciega 3 m)", " lanzamiento de armas", "Protección", "Combate sin armas",
    "Guerrero druídico / Bendición marcial (2 trucos)"
]

GENERAL_FEATS_55E = [
    "Mejora de característica (+2 a una o +1 a dos)",
    "Actor (+1 Car)", "Atleta (+1 Fue/Des)", "Cargador (+1 Fue/Des)", "Centinela (+1 Fue/Des)",
    "Chef (+1 Con/Sab)", "Combatiente con dos armas (+1 Fue/Des)", " Conjurador de guerra (+1 Int/Sab/Car)",
    "experto en ballestas (+1 Des)", "Experto en habilidades (+1 cualquiera, +1 comp, +1 pericia)",
    "francotirador (+1 Des)", "Inspirador (+1 Sab/Car)", "Lanzador ritual (+1 Int/Sab/Car)",
    "Mago elemental (+1 Int/Sab/Car)", "Maestro en armas grandes (+1 Fue)", "Maestro en armaduras medias (+1 Fue/Des)",
    "Maestro en armaduras pesadas (+1 Fue/Con)", "Maestro en armas de asta (+1 Fue/Des)",
    "Maestro en escudos (+1 Fue)", "Mente aguda (+1 Int)", "Observador (+1 Int/Sab)",
    "Resiliente (+1 atributo y competencia en su salvación)", "Resistente (+1 Con)", "Tocado por las hadas (+1 Int/Sab/Car)",
    "Tocado por las sombras (+1 Int/Sab/Car)", "Telequinético (+1 Int/Sab/Car)", "Telepático (+1 Int/Sab/Car)",
    "Veloz (+1 Des/Con, +3 m velocidad)"
]

EPIC_BOONS_55E = [
    "Don del ataque imparable (+1 atributo)", "Don del destino (+1 atributo)",
    "Don del recuerdo de conjuros (+1 Int/Sab/Car)", "Don del viaje dimensional (+1 atributo)",
    "Don de la velocidad (+1 atributo, +9 m velocidad)", "Don de la visión verdadera (+1 atributo)",
    "Don de la fortaleza (+1 atributo, +40 PG máx.)"
]

# Conjuros Siempre Preparados automáticamente por Subclase y Nivel (Cap. 3)
SUBCLASS_ALWAYS_PREPARED_55E = {
    "Colegio del Glamour": {
        3: ["Hechizar persona", "Imagen múltiple"],
        6: ["Orden imperiosa"]
    },
    "Patrón Celestial": {
        3: ["Auxilio", "Curar heridas", "Llama sagrada", "Luz", "Restablecimiento menor", "Saeta guía"],
        5: ["Luz del día", "Revivir"],
        7: ["Guardián de la fe", "Muro de fuego"],
        9: ["Invocar celestial", "Restablecimiento mayor"]
    },
    "Patrón Archihada": {
        3: ["Calmar emociones", "Dormir", "Fuego feérico", "Fuerza fantasmal", "Paso brumoso"],
        5: ["Crecimiento vegetal", "Desplazamiento"],
        7: ["Dominar bestia", "Invisibilidad mejorada"],
        9: ["Apariencia", "Dominar persona"]
    },
    "Patrón Infernal (Fiend)": {
        3: ["Manos ardientes", "Orden imperiosa", "Rayo abrasador", "Sugestión"],
        5: ["Bola de fuego", "Nube apestosa"],
        7: ["Escudo de fuego", "Muro de fuego"],
        9: ["Geas", "Plaga de insectos"]
    },
    "Patrón Primigenio (Great Old One)": {
        3: ["Detectar pensamientos", "Fuerza fantasmal", "Risa horrible de Tasha", "Susurros discordantes"],
        5: ["Clarividencia", "Hambre de Hadar"],
        7: ["Confusión", "Invocar aberración"],
        9: ["Alterar los recuerdos", "Telequinesis"]
    },
    "Dominio de la Guerra": {
        3: ["Arma espiritual", "Arma mágica", "Escudo de fe", "Saeta guía"],
        5: ["Espíritus guardianes", "Manto del cruzado"],
        7: ["Escudo de fuego", "Libertad de movimiento"],
        9: ["Golpe de viento acerado", "Inmovilizar monstruo"]
    },
    "Dominio de la Luz": {
        3: ["Fuego feérico", "Manos ardientes", "Rayo abrasador", "Ver invisibilidad"],
        5: ["Bola de fuego", "Luz del día"],
        7: ["Muro de fuego", "Ojo arcano"],
        9: ["Escudriñar", "Golpe flamígero"]
    },
    "Dominio de la Vida": {
        3: ["Auxilio", "Bendición", "Curar heridas", "Restablecimiento menor"],
        5: ["Palabra de curación en masa", "Revivir"],
        7: ["Aura de vida", "Guarda contra la muerte"],
        9: ["Curar heridas en masa", "Restablecimiento mayor"]
    },
    "Dominio del Engaño": {
        3: ["Disfrazarse", "Hechizar persona", "Invisibilidad", "Pasar sin rastro"],
        5: ["Indetectable", "Patrón hipnótico"],
        7: ["Confusión", "Puerta dimensional"],
        9: ["Alterar los recuerdos", "Dominar persona"]
    },
    "Círculo de la Luna": {
        3: ["Curar heridas", "Rayo de luna", "Voluta estelar"],
        5: ["Conjurar animales"],
        7: ["Fuente de luz lunar"],
        9: ["Curar heridas en masa"]
    },
    "Círculo del Mar": {
        3: ["Hacer añicos", "Nube de oscurecimiento", "Ola atronadora", "Ráfaga de viento", "Rayo de escarcha"],
        5: ["Relámpago", "Respirar bajo el agua"],
        7: ["Controlar agua", "Tormenta de hielo"],
        9: ["Conjurar elemental", "Inmovilizar monstruo"]
    }
}
# Tabla oficial "Comida, bebida y alojamiento" (Pág. 231 del Manual del Jugador 2024)
TAVERN_AND_SERVICES_55E = [
    {"name": "Cerveza (jarra)", "weight_kg": 0.5, "price": "4 pc", "desc": "Bebida de taberna."},
    {"name": "Vino común (jarra)", "weight_kg": 1.0, "price": "2 pp", "desc": "Bebida de taberna."},
    {"name": "Vino de calidad (botella)", "weight_kg": 1.0, "price": "10 po", "desc": "Vino selecto."},
    {"name": "Pan (hogaza)", "weight_kg": 0.25, "price": "2 pc", "desc": "Alimento sencillo."},
    {"name": "Queso (cuña)", "weight_kg": 0.25, "price": "1 pp", "desc": "Alimento sencillo."},
    {"name": "Comida pobre (por día)", "weight_kg": 0.0, "price": "1 pp", "desc": "Gasto diario de comida."},
    {"name": "Comida modesta (por día)", "weight_kg": 0.0, "price": "5 pp", "desc": "Gasto diario de comida."},
    {"name": "Comida cómoda (por día)", "weight_kg": 0.0, "price": "8 pp", "desc": "Gasto diario de comida."},
    {"name": "Comida lujosa (por día)", "weight_kg": 0.0, "price": "2 po", "desc": "Gasto diario de comida."},
    {"name": "Estancia en posada: Pobre (noche)", "weight_kg": 0.0, "price": "2 pp", "desc": "Alojamiento por 1 noche."},
    {"name": "Estancia en posada: Modesta (noche)", "weight_kg": 0.0, "price": "5 pp", "desc": "Alojamiento por 1 noche."},
    {"name": "Estancia en posada: Cómoda (noche)", "weight_kg": 0.0, "price": "8 pp", "desc": "Alojamiento por 1 noche."},
    {"name": "Estancia en posada: Lujosa (noche)", "weight_kg": 0.0, "price": "2 po", "desc": "Alojamiento por 1 noche."},
    {"name": "Estabulado para montura (por día)", "weight_kg": 0.0, "price": "5 pp", "desc": "Cuidado de montura en establo (Pág. 230)."},
    {"name": "Alimento para montura (1 día)", "weight_kg": 5.0, "price": "5 pc", "desc": "Forraje diario para animal (5 kg)."}
]

# Catálogo de ejemplos de Objetos Mágicos que requieren Sintonización (Pág. 232)
MAGIC_ITEMS_ATTUNEMENT_55E = [
    "Anillo de protección (+1 CA y salvaciones)",
    "Anillo de caída de pluma",
    "Anillo de natación",
    "Capa de protección (+1 CA y salvaciones)",
    "Capa élfica (Ventaja en Sigilo)",
    "Botas élficas (Ventaja en pasos silenciosos)",
    "Botas de zancada y brincos",
    "Brazales de defensa (+2 CA sin armadura ni escudo)",
    "Guanteletes de fuerza de ogro (Fuerza = 19)",
    "Diadema de intelecto (Inteligencia = 19)",
    "Amuleto de salud (Constitución = 19)",
    "Piedra Ioun de reserva",
    "Varita de proyectiles mágicos",
    "Varita de telaraña",
    "Bastón de curación",
    "Arma +1 (Sintonizada)",
    "Armadura +1 (Sintonizada)",
    "Perla de poder (Recupera 1 espacio hasta niv. 3)"
]

class Character55eRules:
    @staticmethod
    def get_combined_spells_catalog(db=None) -> list:
        """Devuelve la unión del catálogo base con todos los conjuros extraídos de los PDFs."""
        combined = {sp["name"].split("(")[0].strip().lower(): dict(sp) for sp in SPELLS_CATALOG_55E}
        if db is not None and hasattr(db, "get_all_extracted_spells"):
            for ext in db.get_all_extracted_spells():
                key = ext["name"].split("(")[0].strip().lower()
                if key not in combined:
                    combined[key] = {
                        "name": ext["name"],
                        "level": int(ext["level"]),
                        "school": ext["school"],
                        "classes": ext["classes"]
                    }
                else:
                    # Unir clases si ya existía
                    existing_cls = set(combined[key]["classes"])
                    existing_cls.update(ext["classes"])
                    combined[key]["classes"] = sorted(list(existing_cls))
        return sorted(combined.values(), key=lambda x: (x["level"], x["name"]))
    
    @staticmethod
    def parse_price_to_cp(price_str: str, multiplier: float = 1.0) -> int:
        """Convierte cadenas como '25 po', '5 pp' o '4 pc' a su valor total en piezas de cobre (pc)."""
        if not price_str:
            return 0
        clean = price_str.lower().strip().replace(".", "").replace(",", ".")
        parts = clean.split()
        if not parts:
            return 0
        try:
            num = float(parts[0])
        except ValueError:
            return 0
        unit = parts[1] if len(parts) > 1 else "po"
        if "ppt" in unit:
            cp = int(num * 1000)
        elif "po" in unit:
            cp = int(num * 100)
        elif "pe" in unit:
            cp = int(num * 50)
        elif "pp" in unit:
            cp = int(num * 10)
        elif "pc" in unit:
            cp = int(num)
        else:
            cp = int(num * 100)
        return max(0, int(round(cp * multiplier)))

    @staticmethod
    def format_cp_to_coins_str(total_cp: int) -> str:
        """Formatea una cantidad en piezas de cobre a texto legible en po / pp / pc."""
        if total_cp <= 0:
            return "Gratis"
        if total_cp >= 100 and total_cp % 100 == 0:
            return f"{total_cp // 100} po"
        if total_cp >= 10 and total_cp % 10 == 0:
            return f"{total_cp // 10} pp"
        return f"{total_cp} pc"
    
    @staticmethod
    def get_modifier(score: int) -> int:
        return math.floor((score - 10) / 2)

    @staticmethod
    def format_mod(mod: int) -> str:
        return f"+{mod}" if mod >= 0 else str(mod)

    @staticmethod
    def get_proficiency_bonus(level: int) -> int:
        level = max(1, min(20, level))
        return math.ceil(level / 4) + 1

    @staticmethod
    def get_next_level_xp(level: int) -> int:
        if level >= 20:
            return 355000
        return XP_THRESHOLDS_55E.get(level + 1, 300)

    @staticmethod
    def get_carrying_capacity_kg(str_score: int, species: str = "") -> float:
        multiplier = 15.0 if species == "Goliat" else 7.5
        return round(str_score * multiplier, 1)

    @staticmethod
    def get_spell_slots_by_level(char_class: str, subclass: str, level: int) -> dict:
        """Devuelve un diccionario {nivel_conjuro: cantidad_espacios} exacto según clase y nivel 5.5e."""
        stype = CLASSES_55E.get(char_class, {}).get("spellcasting", "none")
        if stype == "full":
            return dict(FULL_CASTER_SLOTS_55E.get(level, {}))
        if stype == "half":
            return dict(HALF_CASTER_SLOTS_55E.get(level, {}))
        if stype == "pact":
            cnt, slvl = WARLOCK_PACT_SLOTS_55E.get(level, (1, 1))
            return {slvl: cnt}
        if ("Caballero Arcano" in subclass or "Bribón Arcano" in subclass or "Embaucador" in subclass) and level >= 3:
            eff_lvl = max(1, math.ceil(level / 3))
            return dict(FULL_CASTER_SLOTS_55E.get(eff_lvl, {1: 2}))
        return {}

    @staticmethod
    def get_always_prepared_spells(char_class: str, subclass: str, level: int) -> list:
        """Devuelve todos los conjuros que la clase o subclase otorga siempre preparados hasta el nivel actual."""
        auto_spells = []
        if char_class == "Druida" and level >= 1:
            auto_spells.append("Hablar con los animales (Druídico)")
        if char_class == "Explorador" and level >= 1:
            auto_spells.append("Marca del cazador (Enemigo predilecto)")
        if char_class == "Paladín" and level >= 2:
            auto_spells.append("Castigo divino (Paladín Niv. 2)")
        if char_class == "Paladín" and level >= 5:
            auto_spells.append("Encontrar corcel (Paladín Niv. 5)")
        if char_class == "Brujo" and level >= 9:
            auto_spells.append("Contactar con otro plano (Brujo Niv. 9)")
        if char_class == "Bardo" and level >= 20:
            auto_spells.extend(["Palabra de poder: sanar", "Palabra de poder: matar"])

        sub_table = SUBCLASS_ALWAYS_PREPARED_55E.get(subclass, {})
        for req_lvl, sp_list in sorted(sub_table.items()):
            if level >= req_lvl:
                for s in sp_list:
                    if s not in auto_spells:
                        auto_spells.append(s)
        return auto_spells

    @staticmethod
    def get_asi_levels(char_class: str) -> list:
        if char_class == "Guerrero":
            return [4, 6, 8, 12, 14, 16]
        if char_class == "Pícaro":
            return [4, 8, 10, 12, 16]
        return [4, 8, 12, 16]

    @staticmethod
    def calculate_armor_class(armor_name: str, has_shield: bool, magic_bonus: int, mods: dict) -> int:
        info = ARMORS_CATALOG_55E.get(armor_name, ARMORS_CATALOG_55E["Sin Armadura (10 + Des)"])
        base = info["base_ac"]
        atype = info["type"]
        dex_mod = mods.get("Destreza", 0)

        if atype == "barbarian":
            ac = base + dex_mod + mods.get("Constitución", 0)
        elif atype == "monk":
            ac = base + dex_mod + mods.get("Sabiduría", 0)
        elif atype == "bard_dance":
            ac = base + dex_mod + mods.get("Carisma", 0)
        elif atype == "heavy":
            ac = base
        elif atype == "medium":
            ac = base + min(info["dex_cap"], dex_mod)
        else:
            ac = base + dex_mod

        if has_shield:
            ac += 2
        return ac + magic_bonus

    @staticmethod
    def calculate_item_tree_weight(item: dict) -> float:
        own_weight = round(float(item.get("qty", 1)) * float(item.get("weight_kg", 0.0)), 2)
        if not item.get("is_container", False):
            return own_weight
        if item.get("ignore_contents_weight", False):
            return own_weight
        inside_weight = sum(
            round(float(sub.get("qty", 1)) * float(sub.get("weight_kg", 0.0)), 2)
            for sub in item.get("contents", [])
        )
        return round(own_weight + inside_weight, 2)

    @staticmethod
    def get_cantrips_max(char_class: str, level: int, divine_or_primal_order: str = "") -> int:
        c_data = CLASSES_55E.get(char_class, {})
        prog = c_data.get("cantrips_by_level", {})
        count = 0
        for req_lvl, val in sorted(prog.items()):
            if level >= req_lvl:
                count = val
        if "Taumaturgo" in divine_or_primal_order or "Naturalista" in divine_or_primal_order:
            count += 1
        return count

    @staticmethod
    def get_prepared_spells_max(char_class: str, level: int) -> int:
        c_data = CLASSES_55E.get(char_class, {})
        prog = c_data.get("prepared_by_level", {})
        return prog.get(level, 0)

    @staticmethod
    def get_max_spell_level(char_class: str, level: int) -> int:
        stype = CLASSES_55E.get(char_class, {}).get("spellcasting", "none")
        if stype == "none":
            return 0
        if stype == "full":
            return min(9, math.ceil(level / 2))
        if stype == "half":
            return min(5, math.ceil(level / 4))
        if stype == "pact":
            return WARLOCK_PACT_SLOTS_55E.get(level, (1, 1))[1]
        return 0

    @staticmethod
    def calculate_max_hp(char_class: str, level: int, con_mod: int, origin_feat: str, species: str) -> int:
        hd = CLASSES_55E.get(char_class, {}).get("hit_die", 8)
        avg_per_lvl = (hd // 2) + 1
        base_hp = hd + con_mod + ((level - 1) * (avg_per_lvl + con_mod))
        if "Duro" in origin_feat or "Tough" in origin_feat:
            base_hp += 2 * level
        if species == "Enano":
            base_hp += level
        return max(1, base_hp)

    @staticmethod
    def get_features_up_to_level(species: str, char_class: str, subclass: str, level: int) -> list:
        compiled = []
        sp_traits = SPECIES_55E.get(species, {}).get("traits", [])
        if isinstance(sp_traits, list):
            for t_name, t_desc in sp_traits:
                if "Niv. 3" in t_name and level < 3:
                    continue
                if "Niv. 5" in t_name and level < 5:
                    continue
                compiled.append((f"[Especie: {species}] {t_name}", t_desc))

        c_info = CLASSES_55E.get(char_class, {})
        feat_by_lvl = c_info.get("features_by_level", {})
        sub_feats = c_info.get("subclass_features", {}).get(subclass, {})

        for lvl in range(1, level + 1):
            for f_name, f_desc in feat_by_lvl.get(lvl, []):
                compiled.append((f"[Niv. {lvl} - {char_class}] {f_name}", f_desc))
            for sf_name, sf_desc in sub_feats.get(lvl, []):
                compiled.append((f"[Niv. {lvl} - {subclass}] {sf_name}", sf_desc))

        return compiled

    @staticmethod
    def default_stats_payload() -> dict:
        return {
            "base_scores": {ab: 10 for ab in ABILITIES},
            "bg_bonuses": {"+1_a": "Ninguno", "+1_b": "Ninguno", "+1_c": "Ninguno"},
            "species_lineage": "Ninguno",
            "human_extra_skill": "Ninguna",
            "class_skill_choices": [],
            "skilled_feat_choices": [],
            "instrument_choices": [],
            "language_choices": ["Común", "Ninguno", "Ninguno"],
            "gaming_set_choice": "Ninguno",
            "level_progression_choices": {},
            "expertise_skills": [],
            "selected_cantrips": [],
            "selected_spells": [],
            "spent_spell_slots": {},
            "origin_feat": "",
            "xp_current": 0,
            "hit_dice_current": 1,
            "equipped_armor": "Sin Armadura (10 + Des)",
            "equipped_shield": False,
            "armor_magic_bonus": 0,
            "armor_class": 10,
            "speed": "9 m",
            "hp_max": 8,
            "hp_current": 8,
            "hp_temp": 0,
            "heroic_inspiration": False,
            "coins": {"cp": 0, "sp": 0, "gp": 0},
            "weapons": [
                {"name": "-- Seleccionar Arma --", "ability": "Fuerza", "damage": "", "mastery": "Ninguna"},
                {"name": "-- Seleccionar Arma --", "ability": "Fuerza", "damage": "", "mastery": "Ninguna"},
                {"name": "-- Seleccionar Arma --", "ability": "Fuerza", "damage": "", "mastery": "Ninguna"}
            ],
            "inventory_char": [],
            "mount_type": "Sin Montura",
            "inventory_mount": [],
            "adventure_notes": ""
        }