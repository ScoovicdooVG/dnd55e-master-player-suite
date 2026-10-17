import sys
import sqlite3
import json
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_APP_DIR = Path(sys.executable).resolve().parent
else:
    BASE_APP_DIR = Path(__file__).resolve().parent.parent

DEFAULT_DB_PATH = BASE_APP_DIR / "dnd_data.db"


class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.init_database()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=15.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Inicializa las tablas principales y el motor de búsqueda FTS5 para los PDFs."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS manuals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    file_path TEXT UNIQUE NOT NULL,
                    total_pages INTEGER,
                    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS manual_toc (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    manual_id INTEGER NOT NULL,
                    level INTEGER,
                    heading TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    FOREIGN KEY (manual_id) REFERENCES manuals(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS pdf_search_index USING fts5(
                    manual_id UNINDEXED,
                    manual_title,
                    page_number UNINDEXED,
                    content,
                    tokenize='unicode61 remove_diacritics 1'
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    player_name TEXT,
                    species TEXT,
                    background TEXT,
                    char_class TEXT,
                    subclass TEXT,
                    level INTEGER DEFAULT 1,
                    stats_json TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monsters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    size_type_alignment TEXT,
                    armor_class TEXT,
                    hit_points TEXT,
                    speed TEXT,
                    initiative_bonus INTEGER DEFAULT 0,
                    challenge_rating TEXT,
                    statblock_json TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS campaign_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT DEFAULT 'Sesión',
                    content TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    # --- MÉTODOS DE MANUALES PDF ---
    def search_manuals(self, query_text: str, limit: int = 25):
        if not query_text.strip():
            return []
        safe_query = " ".join([f'"{word}"*' for word in query_text.strip().split()])
        with self.get_connection() as conn:
            cursor = conn.cursor()
            sql = """
                SELECT 
                    manual_id,
                    manual_title,
                    page_number,
                    snippet(pdf_search_index, 3, '[', ']', ' ... ', 20) as match_snippet
                FROM pdf_search_index
                WHERE pdf_search_index MATCH ?
                ORDER BY rank
                LIMIT ?
            """
            cursor.execute(sql, (safe_query, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_registered_manuals(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM manuals ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    # --- MÉTODOS DE HOJAS DE PERSONAJE 5.5e ---
    def save_character(self, char_data: dict) -> int:
        stats_str = json.dumps(char_data.get("stats", {}), ensure_ascii=False)
        char_id = char_data.get("id")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            if char_id:
                cursor.execute("""
                    UPDATE characters
                    SET name=?, player_name=?, species=?, background=?,
                        char_class=?, subclass=?, level=?, stats_json=?,
                        updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                """, (
                    char_data["name"], char_data.get("player_name", ""),
                    char_data["species"], char_data["background"],
                    char_data["char_class"], char_data.get("subclass", ""),
                    int(char_data.get("level", 1)), stats_str, char_id
                ))
                conn.commit()
                return char_id
            else:
                cursor.execute("""
                    INSERT INTO characters (name, player_name, species, background, char_class, subclass, level, stats_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    char_data["name"], char_data.get("player_name", ""),
                    char_data["species"], char_data["background"],
                    char_data["char_class"], char_data.get("subclass", ""),
                    int(char_data.get("level", 1)), stats_str
                ))
                conn.commit()
                return cursor.lastrowid

    def get_all_characters(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, player_name, species, char_class, level, stats_json FROM characters ORDER BY updated_at DESC")
            rows = []
            for r in cursor.fetchall():
                d = dict(r)
                d["stats"] = json.loads(d["stats_json"]) if d.get("stats_json") else {}
                rows.append(d)
            return rows

    def get_character_by_id(self, char_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM characters WHERE id = ?", (char_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            data["stats"] = json.loads(data["stats_json"]) if data.get("stats_json") else {}
            return data

    def add_xp_to_character(self, char_id: int, xp_amount: int):
        char = self.get_character_by_id(char_id)
        if not char:
            return
        stats = char.get("stats", {})
        curr_xp = int(stats.get("xp_current", 0))
        stats["xp_current"] = max(0, curr_xp + xp_amount)
        char["stats"] = stats
        self.save_character(char)

    def delete_character(self, char_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM characters WHERE id = ?", (char_id,))
            conn.commit()

    # --- MÉTODOS DE MONSTRUOS 5.5e (DM) ---
    def save_monster(self, monster_data: dict) -> int:
        sb_str = json.dumps(monster_data.get("statblock", {}), ensure_ascii=False)
        m_id = monster_data.get("id")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if m_id:
                cursor.execute("""
                    UPDATE monsters
                    SET name=?, size_type_alignment=?, armor_class=?, hit_points=?,
                        speed=?, initiative_bonus=?, challenge_rating=?, statblock_json=?
                    WHERE id=?
                """, (
                    monster_data["name"], monster_data["size_type_alignment"],
                    monster_data["armor_class"], monster_data["hit_points"],
                    monster_data["speed"], int(monster_data.get("initiative_bonus", 0)),
                    monster_data["challenge_rating"], sb_str, m_id
                ))
                conn.commit()
                return m_id
            else:
                cursor.execute("""
                    INSERT INTO monsters (name, size_type_alignment, armor_class, hit_points, speed, initiative_bonus, challenge_rating, statblock_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    monster_data["name"], monster_data["size_type_alignment"],
                    monster_data["armor_class"], monster_data["hit_points"],
                    monster_data["speed"], int(monster_data.get("initiative_bonus", 0)),
                    monster_data["challenge_rating"], sb_str
                ))
                conn.commit()
                return cursor.lastrowid

    def get_all_monsters(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM monsters ORDER BY name ASC")
            rows = []
            for r in cursor.fetchall():
                d = dict(r)
                d["statblock"] = json.loads(d["statblock_json"]) if d.get("statblock_json") else {}
                rows.append(d)
            return rows

    def delete_monster(self, monster_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM monsters WHERE id = ?", (monster_id,))
            conn.commit()

    # --- MÉTODOS DE CARPETAS DE AVENTURA, NOTAS Y ENCUENTROS DEL DM ---
    def ensure_dm_adventure_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS adventures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    expanded INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saved_encounters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    adventure_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    monsters_json TEXT NOT NULL,
                    notes TEXT DEFAULT '',
                    FOREIGN KEY (adventure_id) REFERENCES adventures(id) ON DELETE CASCADE
                )
            """)
            # Agregar columna adventure_id a campaign_notes si no existía
            cursor.execute("PRAGMA table_info(campaign_notes)")
            cols = [row["name"] for row in cursor.fetchall()]
            if "adventure_id" not in cols:
                cursor.execute("ALTER TABLE campaign_notes ADD COLUMN adventure_id INTEGER DEFAULT 1")
            if "npc_attitude" not in cols:
                cursor.execute("ALTER TABLE campaign_notes ADD COLUMN npc_attitude TEXT DEFAULT 'Indiferente'")

            # Crear una carpeta de aventura inicial por defecto si no hay ninguna
            cursor.execute("SELECT COUNT(*) as cnt FROM adventures")
            if cursor.fetchone()["cnt"] == 0:
                cursor.execute(
                    "INSERT INTO adventures (name, description, expanded) VALUES (?, ?, 1)",
                    ("Campaña Principal", "Carpeta principal de la aventura")
                )
            conn.commit()

    def get_all_adventures(self):
        self.ensure_dm_adventure_tables()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM adventures ORDER BY id ASC")
            return [dict(r) for r in cursor.fetchall()]

    def create_adventure(self, name: str, description: str = "") -> int:
        self.ensure_dm_adventure_tables()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO adventures (name, description, expanded) VALUES (?, ?, 1)",
                (name, description)
            )
            conn.commit()
            return cursor.lastrowid

    def toggle_adventure_expanded(self, adv_id: int, expanded: bool):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE adventures SET expanded=? WHERE id=?", (1 if expanded else 0, adv_id))
            conn.commit()

    def delete_adventure(self, adv_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM campaign_notes WHERE adventure_id=?", (adv_id,))
            cursor.execute("DELETE FROM saved_encounters WHERE adventure_id=?", (adv_id,))
            cursor.execute("DELETE FROM adventures WHERE id=?", (adv_id,))
            conn.commit()

    def save_campaign_note(self, note_data: dict) -> int:
        self.ensure_dm_adventure_tables()
        n_id = note_data.get("id")
        adv_id = int(note_data.get("adventure_id") or 1)
        attitude = note_data.get("npc_attitude", "Indiferente")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if n_id:
                cursor.execute("""
                    UPDATE campaign_notes
                    SET adventure_id=?, title=?, category=?, npc_attitude=?, content=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                """, (adv_id, note_data["title"], note_data["category"], attitude, note_data["content"], n_id))
                conn.commit()
                return n_id
            else:
                cursor.execute("""
                    INSERT INTO campaign_notes (adventure_id, title, category, npc_attitude, content)
                    VALUES (?, ?, ?, ?, ?)
                """, (adv_id, note_data["title"], note_data["category"], attitude, note_data["content"]))
                conn.commit()
                return cursor.lastrowid

    def get_all_campaign_notes(self, adventure_id: int = None):
        self.ensure_dm_adventure_tables()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if adventure_id is not None:
                cursor.execute("SELECT * FROM campaign_notes WHERE adventure_id=? ORDER BY updated_at DESC", (adventure_id,))
            else:
                cursor.execute("SELECT * FROM campaign_notes ORDER BY updated_at DESC")
            return [dict(r) for r in cursor.fetchall()]

    def delete_campaign_note(self, note_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM campaign_notes WHERE id = ?", (note_id,))
            conn.commit()

    def save_encounter_preset(self, adv_id: int, name: str, monsters_list: list, notes: str = "") -> int:
        self.ensure_dm_adventure_tables()
        m_json = json.dumps(monsters_list, ensure_ascii=False)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO saved_encounters (adventure_id, name, monsters_json, notes)
                VALUES (?, ?, ?, ?)
            """, (adv_id, name, m_json, notes))
            conn.commit()
            return cursor.lastrowid

    def get_encounters_by_adventure(self, adv_id: int = None):
        self.ensure_dm_adventure_tables()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if adv_id:
                cursor.execute("SELECT * FROM saved_encounters WHERE adventure_id=? ORDER BY id DESC", (adv_id,))
            else:
                cursor.execute("SELECT * FROM saved_encounters ORDER BY id DESC")
            rows = []
            for r in cursor.fetchall():
                d = dict(r)
                d["monsters"] = json.loads(d["monsters_json"]) if d.get("monsters_json") else []
                rows.append(d)
            return rows

    def delete_saved_encounter(self, enc_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM saved_encounters WHERE id=?", (enc_id,))
            conn.commit()

    def give_loot_to_character(self, char_id: int, item_name: str, qty: int, weight_kg: float, gp_bonus: int = 0):
        char = self.get_character_by_id(char_id)
        if not char:
            return
        stats = char.get("stats", {})
        if item_name.strip():
            inv = stats.setdefault("inventory_char", [])
            inv.append({
                "name": item_name.strip(),
                "qty": max(1, qty),
                "weight_kg": max(0.0, weight_kg),
                "is_container": False,
                "expanded": False,
                "contents": []
            })
        if gp_bonus != 0:
            coins = stats.setdefault("coins", {"cp": 0, "sp": 0, "gp": 0})
            coins["gp"] = max(0, int(coins.get("gp", 0)) + gp_bonus)
        char["stats"] = stats
        self.save_character(char)
        # --- MÉTODOS DE TIENDA ACTIVA DEL DM Y SINTONIZACIÓN ---
    def ensure_shop_table(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dm_shop_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    shop_name TEXT DEFAULT 'Mercado de los Aventureros',
                    shop_preset TEXT DEFAULT 'Mercado Completo (Todo el Cap. 6)',
                    price_multiplier REAL DEFAULT 1.0,
                    is_open INTEGER DEFAULT 1,
                    custom_items_json TEXT DEFAULT '[]'
                )
            """)
            cursor.execute("SELECT COUNT(*) as cnt FROM dm_shop_state")
            if cursor.fetchone()["cnt"] == 0:
                cursor.execute("""
                    INSERT INTO dm_shop_state (id, shop_name, shop_preset, price_multiplier, is_open, custom_items_json)
                    VALUES (1, 'Mercado del Pueblo', 'Mercado Completo (Todo el Cap. 6)', 1.0, 1, '[]')
                """)
            conn.commit()

    def get_shop_state(self) -> dict:
        self.ensure_shop_table()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dm_shop_state WHERE id = 1")
            row = cursor.fetchone()
            data = dict(row)
            data["custom_items"] = json.loads(data.get("custom_items_json") or "[]")
            data["is_open"] = bool(data.get("is_open", 1))
            return data

    def update_shop_state(self, shop_name: str, shop_preset: str, price_multiplier: float, is_open: bool, custom_items: list = None):
        self.ensure_shop_table()
        current = self.get_shop_state()
        c_json = json.dumps(custom_items if custom_items is not None else current["custom_items"], ensure_ascii=False)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE dm_shop_state
                SET shop_name=?, shop_preset=?, price_multiplier=?, is_open=?, custom_items_json=?
                WHERE id = 1
            """, (shop_name, shop_preset, float(price_multiplier), 1 if is_open else 0, c_json))
            conn.commit()


            # --- MÉTODOS DE CATÁLOGO DE CONJUROS EXTRAÍDOS DEL PDF ---
    def ensure_spells_table(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS spells_catalog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    level INTEGER NOT NULL,
                    school TEXT NOT NULL,
                    classes_json TEXT NOT NULL,
                    casting_time TEXT DEFAULT '',
                    range_str TEXT DEFAULT '',
                    components TEXT DEFAULT '',
                    duration TEXT DEFAULT '',
                    description TEXT DEFAULT '',
                    page_number INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def save_extracted_spells_batch(self, spells_list: list) -> int:
        self.ensure_spells_table()
        inserted = 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for sp in spells_list:
                cursor.execute("""
                    INSERT INTO spells_catalog
                    (name, level, school, classes_json, casting_time, range_str, components, duration, description, page_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                        level=excluded.level,
                        school=excluded.school,
                        classes_json=excluded.classes_json,
                        casting_time=excluded.casting_time,
                        range_str=excluded.range_str,
                        components=excluded.components,
                        duration=excluded.duration,
                        description=excluded.description,
                        page_number=excluded.page_number
                """, (
                    sp["name"], int(sp["level"]), sp["school"],
                    json.dumps(sp["classes"], ensure_ascii=False),
                    sp.get("casting_time", ""), sp.get("range_str", ""),
                    sp.get("components", ""), sp.get("duration", ""),
                    sp.get("description", ""), int(sp.get("page_number", 0))
                ))
                inserted += 1
            conn.commit()
        return inserted

    def get_all_extracted_spells(self) -> list:
        self.ensure_spells_table()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM spells_catalog ORDER BY level ASC, name ASC")
            rows = []
            for r in cursor.fetchall():
                d = dict(r)
                d["classes"] = json.loads(d.get("classes_json") or "[]")
                rows.append(d)
            return rows
            # --- MÉTODOS DE MESA EN VIVO: PROYECTOR DE HANDOUTS/MAPAS E INICIATIVA PÚBLICA ---
    def ensure_live_table_state(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dm_live_table (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    handout_title TEXT DEFAULT 'Sin imagen proyectada',
                    handout_caption TEXT DEFAULT '',
                    handout_b64 TEXT DEFAULT '',
                    lighting TEXT DEFAULT 'Luz brillante (Visión normal)',
                    travel_pace TEXT DEFAULT 'Normal (4,5 km/h | 36 km/día — Desventaja en Sigilo)',
                    combat_json TEXT DEFAULT '{"active": false, "round": 1, "turn_idx": 0, "combatants": []}'
                )
            """)
            cursor.execute("SELECT COUNT(*) as cnt FROM dm_live_table")
            if cursor.fetchone()["cnt"] == 0:
                cursor.execute("""
                    INSERT INTO dm_live_table (id, handout_title, handout_caption, handout_b64)
                    VALUES (1, 'Sin imagen proyectada', 'El DM aún no ha compartido ningún mapa o pista.', '')
                """)
            conn.commit()

    def get_live_table_state(self) -> dict:
        self.ensure_live_table_state()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dm_live_table WHERE id = 1")
            row = cursor.fetchone()
            data = dict(row)
            data["combat"] = json.loads(data.get("combat_json") or '{"active": false, "round": 1, "turn_idx": 0, "combatants": []}')
            return data

    def update_live_handout(self, title: str, caption: str, b64_img: str):
        self.ensure_live_table_state()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE dm_live_table
                SET handout_title=?, handout_caption=?, handout_b64=?
                WHERE id = 1
            """, (title, caption, b64_img))
            conn.commit()

    def update_live_environment(self, lighting: str, travel_pace: str):
        self.ensure_live_table_state()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE dm_live_table
                SET lighting=?, travel_pace=?
                WHERE id = 1
            """, (lighting, travel_pace))
            conn.commit()

    def update_live_combat_state(self, round_num: int, turn_idx: int, combatants_list: list):
        """
        Guarda el estado del combate aplicando la Niebla de Guerra para los jugadores:
        los monstruos nunca exponen sus PG exactos ni su CA numérica, solo si están
        Intactos, Maltrechos (<= 50% PG) o Derrotados (0 PG).
        """
        self.ensure_live_table_state()
        public_list = []
        for idx, c in enumerate(combatants_list):
            is_pj = bool(c.get("is_player", False))
            hp_c = int(c.get("hp_curr", 0))
            hp_m = max(1, int(c.get("hp_max", 1)))

            if is_pj:
                status_text = f"PG: {hp_c}/{hp_m} | CA: {c.get('ac', 10)}"
                status_tag = "ok" if hp_c > (hp_m // 2) else ("bloodied" if hp_c > 0 else "dead")
            else:
                if hp_c <= 0:
                    status_text = "💀 Derrotado"
                    status_tag = "dead"
                elif hp_c <= (hp_m // 2):
                    status_text = "🩸 Maltrecho (≤50% PG)"
                    status_tag = "bloodied"
                else:
                    status_text = "🛡️ Intacto"
                    status_tag = "ok"

            public_list.append({
                "name": c.get("name", "Combatiente"),
                "is_player": is_pj,
                "initiative": c.get("initiative", 10),
                "is_turn": (idx == turn_idx),
                "condition": c.get("condition", "Sin Estado"),
                "status_text": status_text,
                "status_tag": status_tag
            })

        payload = json.dumps({
            "active": len(public_list) > 0,
            "round": round_num,
            "turn_idx": turn_idx,
            "combatants": public_list
        }, ensure_ascii=False)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE dm_live_table SET combat_json=? WHERE id = 1", (payload,))
            conn.commit()
