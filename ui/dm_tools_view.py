import base64
import io
import random
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import random
import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import DatabaseManager
from models.character_55e import ABILITIES
from models.monster_55e import (
    Monster55eRules, CR_TABLE_55E, CONDITIONS_55E, PRESET_MONSTERS_55E
)

# Presupuesto de XP por personaje según Nivel para calcular Dificultad de Encuentros 5.5e (Baja, Moderada, Alta)
XP_BUDGET_PER_CHAR_55E = {
    1: (50, 75, 100),     2: (100, 150, 200),   3: (150, 225, 400),   4: (250, 375, 500),
    5: (500, 750, 1100),  6: (600, 1000, 1400), 7: (750, 1300, 1700), 8: (1000, 1700, 2100),
    9: (1300, 2000, 2600),10: (1600, 2300, 3100),11: (1900, 2900, 4100),12: (2200, 3700, 4700),
    13: (2600, 4200, 5400),14: (2900, 4900, 6200),15: (3300, 5400, 7800),16: (3800, 6100, 9800),
    17: (4500, 7200, 11700),18: (5000, 8700, 14200),19: (5500, 10700, 17200),20: (6400, 13200, 22000)
}

# Selección de Bagatelas del Capítulo 2 (Págs. 46-47 del Manual del Jugador 2024)
TRINKETS_55E = [
    "01. La mano momificada de un goblin",
    "02. Un trozo de cristal que brilla débilmente a la luz de la luna",
    "03. Una moneda de oro acuñada en una tierra desconocida",
    "04. Un diario escrito en un idioma que desconoces",
    "05. Un anillo de latón que nunca pierde su lustre",
    "07. Un par de dados de hueso, ambos con una calavera en lugar del seis",
    "14. Una escama enorme, quizá de un dragón",
    "17. Un orbe de cristal lleno de humo serpenteante",
    "21. Una cajita de música fabricada por gnomos que toca una canción de tu infancia",
    "28. Una garra de dragón atada a un colgante de cuero",
    "40. Una gema que parece un pedazo de carbón cuando la mira alguien que no seas tú",
    "47. Un orbe de cristal lleno de agua en el que nada un pez mecánico",
    "56. Una llave vieja",
    "63. Una máscara de alabastro",
    "79. Una invitación a una fiesta en la que tuvo lugar un asesinato",
    "89. Un vial de sangre de dragón",
    "93. Una botella de vino vacía: 'Bodega El Mago de los Vinos, Cosecha del Dragón Rojo'",
    "100. Una urna de metal que contiene las cenizas de un héroe"
]


class DMToolsView(ctk.CTkFrame):
    """Suite del Dungeon Master: Carpetas de Aventura, Encuentros Pre-armados, Combate y Bestiario 5.5e."""
    def __init__(self, master, db: DatabaseManager):
        super().__init__(master, fg_color="transparent")
        self.db = db
        self.db.ensure_dm_adventure_tables()

        # Estado del Rastreador de Combate
        self.combatants = []
        self.current_turn_idx = 0
        self.round_number = 1
        self.accumulated_xp = 0

        # Estado de la Fragua de Monstruos
        self.current_monster_id = None
        self.m_score_vars = {}
        self.m_mod_labels = {}

        # Estado de Carpetas de Aventura y Notas
        self.current_adventure_id = 1
        self.current_note_id = None
        self.staged_encounter_monsters = []  # Para armar encuentros antes de la sesión

        self._seed_preset_monsters_if_empty()
        self._build_ui()

    def _seed_preset_monsters_if_empty(self):
        existing = self.db.get_all_monsters()
        if not existing:
            for _, tpl in PRESET_MONSTERS_55E.items():
                self.db.save_monster(tpl)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        self.tab_campaign = self.tabs.add("Carpetas de Aventura y Encuentros")
        self.tab_combat = self.tabs.add("Rastreador de Combate Activo")
        self.tab_forge = self.tabs.add("Fragua de Monstruos 5.5e (Metros)")
        self.tab_ref = self.tabs.add("Referencia Rápida y Exploración (Cap. 1)")

        self._build_campaign_folders_tab()
        self._build_combat_tab()
        self._build_monster_forge_tab()
        self._build_quick_reference_tab()

    # =========================================================================
    # PESTAÑA 1: CARPETAS DE AVENTURA DESPLEGABLES + ENCUENTROS PRE-ARMADOS + BOTÍN
    # =========================================================================
    def _build_campaign_folders_tab(self):
        self.tab_campaign.grid_columnconfigure(1, weight=3)
        self.tab_campaign.grid_columnconfigure(2, weight=2)
        self.tab_campaign.grid_rowconfigure(0, weight=1)

        # --- COLUMNA IZQUIERDA: ÁRBOL DE CARPETAS DE AVENTURA DESPLEGABLES (▼ / ▶) ---
        sidebar = ctk.CTkFrame(self.tab_campaign, width=285)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(4, 6), pady=4)
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(sidebar, text="Carpetas de Aventura", font=("Segoe UI", 17, "bold")).grid(
            row=0, column=0, padx=12, pady=(10, 4), sticky="w"
        )

        btn_row = ctk.CTkFrame(sidebar, fg_color="transparent")
        btn_row.grid(row=1, column=0, sticky="ew", padx=10, pady=4)
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_row, text="+ Nueva Carpeta", fg_color="#D97706", hover_color="#B45309",
            command=self._create_new_adventure_folder
        ).grid(row=0, column=0, padx=(0, 3), sticky="ew")

        ctk.CTkButton(
            btn_row, text="+ Nueva Nota", fg_color="#2E7D32", hover_color="#1B5E20",
            command=self._new_campaign_note
        ).grid(row=0, column=1, padx=(3, 0), sticky="ew")

        # Filtro por Categoría
        self.combo_filter_cat = ctk.CTkComboBox(
            sidebar, values=["Todas las Categorías", "Sesión", "PNJ (NPC)", "Lugar / Sala", "Misión", "Lore / Secreto", "Botín / Tienda"],
            command=lambda _: self._refresh_adventure_tree()
        )
        self.combo_filter_cat.set("Todas las Categorías")
        self.combo_filter_cat.grid(row=2, column=0, padx=10, pady=4, sticky="ew")

        self.folders_tree_scroll = ctk.CTkScrollableFrame(sidebar, label_text="Aventuras, Notas y Encuentros")
        self.folders_tree_scroll.grid(row=3, column=0, padx=8, pady=6, sticky="nsew")

        # --- COLUMNA CENTRAL: EDITOR DE NOTA / PNJ / LUGAR DE LA CARPETA ACTIVA ---
        editor = ctk.CTkFrame(self.tab_campaign)
        editor.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        editor.grid_columnconfigure(0, weight=1)
        editor.grid_rowconfigure(2, weight=1)

        top_row = ctk.CTkFrame(editor, fg_color="#1F2937")
        top_row.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        top_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(top_row, text="Carpeta:", font=("Segoe UI", 11, "bold"), text_color="#FBBF24").grid(row=0, column=0, padx=(8, 4), pady=6)
        self.combo_note_adv = ctk.CTkComboBox(top_row, values=["Campaña Principal"], width=165)
        self.combo_note_adv.grid(row=0, column=1, padx=4, pady=6, sticky="ew")

        self.combo_note_cat = ctk.CTkComboBox(
            top_row, values=["Sesión", "PNJ (NPC)", "Lugar / Sala", "Misión", "Lore / Secreto", "Botín / Tienda"], width=130
        )
        self.combo_note_cat.grid(row=0, column=2, padx=4, pady=6)

        ctk.CTkLabel(top_row, text="Actitud PNJ:", font=("Segoe UI", 11)).grid(row=0, column=3, padx=(6, 2), pady=6)
        self.combo_npc_attitude = ctk.CTkComboBox(
            top_row, values=["N/A", "Amistoso (Ventaja Influir)", "Indiferente", "Hostil (Desventaja Influir)"], width=155
        )
        self.combo_npc_attitude.grid(row=0, column=4, padx=(2, 8), pady=6)

        title_row = ctk.CTkFrame(editor, fg_color="transparent")
        title_row.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        title_row.grid_columnconfigure(0, weight=1)

        self.entry_note_title = ctk.CTkEntry(
            title_row, placeholder_text="Título (ej. Cap. 1: La Taberna Sangre de la Vid / PNJ: Ismark el Menor)...",
            font=("Segoe UI", 13, "bold")
        )
        self.entry_note_title.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        ctk.CTkButton(title_row, text="Guardar Nota", width=110, fg_color="#2563EB", command=self._save_campaign_note).grid(row=0, column=1, padx=3)
        ctk.CTkButton(title_row, text="Eliminar", width=75, fg_color="#8B2635", command=self._delete_campaign_note).grid(row=0, column=2, padx=(3, 0))

        self.txt_note_content = ctk.CTkTextbox(editor, font=("Segoe UI", 13))
        self.txt_note_content.grid(row=2, column=0, sticky="nsew", padx=8, pady=(4, 8))

        # --- COLUMNA DERECHA: CONSTRUCTOR DE ENCUENTROS DE LA AVENTURA + ENTREGADOR DE BOTÍN ---
        right_panel = ctk.CTkFrame(self.tab_campaign)
        right_panel.grid(row=0, column=2, sticky="nsew", padx=(4, 4), pady=4)
        right_panel.grid_columnconfigure(0, weight=1)

        # Bloque 1: Pre-armar Encuentro para esta Carpeta de Aventura
        enc_box = ctk.CTkFrame(right_panel, fg_color="#1E293B")
        enc_box.pack(fill="x", padx=8, pady=(8, 6))

        ctk.CTkLabel(
            enc_box, text="Pre-armar Encuentro para la Aventura",
            font=("Segoe UI", 13, "bold"), text_color="#FBBF24"
        ).pack(anchor="w", padx=10, pady=(8, 2))

        self.lbl_enc_difficulty = ctk.CTkLabel(
            enc_box, text="Dificultad p/ Grupo: Sin monstruos (0 XP)",
            font=("Segoe UI", 11, "bold"), text_color="#34D399"
        )
        self.lbl_enc_difficulty.pack(anchor="w", padx=10, pady=(0, 4))

        self.entry_enc_name = ctk.CTkEntry(enc_box, placeholder_text="Nombre (ej. Sala 4: Emboscada Goblin)")
        self.entry_enc_name.pack(fill="x", padx=10, pady=4)

        add_m_row = ctk.CTkFrame(enc_box, fg_color="transparent")
        add_m_row.pack(fill="x", padx=10, pady=4)

        self.combo_stage_monster = ctk.CTkComboBox(add_m_row, values=self._get_monster_names_list(), width=155)
        self.combo_stage_monster.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.entry_stage_qty = ctk.CTkEntry(add_m_row, width=42, justify="center")
        self.entry_stage_qty.insert(0, "2")
        self.entry_stage_qty.pack(side="left", padx=2)

        ctk.CTkButton(
            add_m_row, text="+ Agregar", width=75, fg_color="#6D28D9",
            command=self._stage_monster_for_preset
        ).pack(side="left", padx=(4, 0))

        self.txt_staged_list = ctk.CTkTextbox(enc_box, height=70, font=("Segoe UI", 11))
        self.txt_staged_list.pack(fill="x", padx=10, pady=4)

        enc_btns = ctk.CTkFrame(enc_box, fg_color="transparent")
        enc_btns.pack(fill="x", padx=10, pady=(2, 8))
        ctk.CTkButton(enc_btns, text="Limpiar", width=70, height=26, fg_color="#374151", command=self._clear_staged_encounter).pack(side="left")
        ctk.CTkButton(
            enc_btns, text="Guardar Encuentro en Carpeta", height=26, fg_color="#2563EB",
            command=self._save_staged_encounter_to_folder
        ).pack(side="right", fill="x", expand=True, padx=(6, 0))

        # Bloque 2: Entregador de Botín, Oro y Bagatelas directo al Inventario del Jugador
        loot_box = ctk.CTkFrame(right_panel, fg_color="#111827")
        loot_box.pack(fill="x", padx=8, pady=6)

        ctk.CTkLabel(
            loot_box, text="Enviar Botín / Oro / Bagatela a un Héroe",
            font=("Segoe UI", 13, "bold"), text_color="#60A5FA"
        ).pack(anchor="w", padx=10, pady=(8, 4))

        target_row = ctk.CTkFrame(loot_box, fg_color="transparent")
        target_row.pack(fill="x", padx=10, pady=3)
        ctk.CTkLabel(target_row, text="Héroe:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0, 6))
        self.combo_loot_char = ctk.CTkComboBox(target_row, values=self._get_party_char_options(), width=200)
        self.combo_loot_char.pack(side="left", fill="x", expand=True)

        item_row = ctk.CTkFrame(loot_box, fg_color="transparent")
        item_row.pack(fill="x", padx=10, pady=3)
        self.entry_loot_item = ctk.CTkEntry(item_row, placeholder_text="Objeto o Tesoro (ej. Espada +1 / Rubí)")
        self.entry_loot_item.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.entry_loot_kg = ctk.CTkEntry(item_row, width=55, placeholder_text="kg")
        self.entry_loot_kg.insert(0, "0.5")
        self.entry_loot_kg.pack(side="left")

        gold_row = ctk.CTkFrame(loot_box, fg_color="transparent")
        gold_row.pack(fill="x", padx=10, pady=3)
        ctk.CTkLabel(gold_row, text="+ Oro (PO):", font=("Segoe UI", 11, "bold"), text_color="#FBBF24").pack(side="left")
        self.entry_loot_gp = ctk.CTkEntry(gold_row, width=65, justify="center")
        self.entry_loot_gp.insert(0, "0")
        self.entry_loot_gp.pack(side="left", padx=6)

        ctk.CTkButton(
            gold_row, text="Bagatela Aleatoria (Cap. 2)", height=26, fg_color="#374151",
            command=self._roll_random_trinket
        ).pack(side="right", fill="x", expand=True)

        ctk.CTkButton(
            loot_box, text="Enviar al Inventario del Jugador", fg_color="#059669",
            command=self._send_loot_to_player
        ).pack(fill="x", padx=10, pady=(6, 10))

        self._refresh_adventure_tree()
        self._new_campaign_note()

        # Bloque 3: Controlador de Tienda / Taberna en Vivo para los Celulares
        shop_box = ctk.CTkFrame(right_panel, fg_color="#1E1B4B")
        shop_box.pack(fill="x", padx=8, pady=6)

        top_sh = ctk.CTkFrame(shop_box, fg_color="transparent")
        top_sh.pack(fill="x", padx=10, pady=(8, 2))
        ctk.CTkLabel(
            top_sh, text="🏪 Tienda Activa en Celulares",
            font=("Segoe UI", 13, "bold"), text_color="#A78BFA"
        ).pack(side="left")

        shop_state = self.db.get_shop_state()
        self.chk_shop_open_var = ctk.BooleanVar(value=shop_state.get("is_open", True))
        ctk.CTkSwitch(
            top_sh, text="Abierta", variable=self.chk_shop_open_var,
            command=self._save_dm_shop_settings, font=("Segoe UI", 11, "bold")
        ).pack(side="right")

        self.entry_shop_name = ctk.CTkEntry(shop_box, placeholder_text="Nombre (ej. Herrería de Phandalin / Taberna)")
        self.entry_shop_name.insert(0, shop_state.get("shop_name", "Mercado del Pueblo"))
        self.entry_shop_name.pack(fill="x", padx=10, pady=3)

        shop_presets = [
            "Mercado Completo (Todo el Cap. 6)",
            "Taberna y Posada (Comida, Bebida y Camas - Pág. 231)",
            "Herrería y Armería (Armas, Armaduras y Escudos)",
            "Bazar del Aventurero (Mochilas, Cuerdas, Antorchas, Paquetes)",
            "Alquimia, Herboristería y Focos Mágicos",
            "Establo y Monturas (Alforjas, Sillas, Carretas y Forraje)"
        ]
        self.combo_shop_preset = ctk.CTkComboBox(shop_box, values=shop_presets)
        self.combo_shop_preset.set(shop_state.get("shop_preset", shop_presets[0]))
        self.combo_shop_preset.pack(fill="x", padx=10, pady=3)

        mult_row = ctk.CTkFrame(shop_box, fg_color="transparent")
        mult_row.pack(fill="x", padx=10, pady=(3, 8))
        ctk.CTkLabel(mult_row, text="Precios:", font=("Segoe UI", 11, "bold")).pack(side="left")

        self.combo_shop_mult = ctk.CTkComboBox(
            mult_row,
            values=["50% ( Aliado / Rebaja )", "100% ( Precio Oficial Manual )", "150% ( Caro / Escasez )", "200% ( Doble Precio )"],
            width=165
        )
        self.combo_shop_mult.set("100% ( Precio Oficial Manual )")
        self.combo_shop_mult.pack(side="left", padx=6)

        ctk.CTkButton(
            mult_row, text="Actualizar Tienda", height=26, fg_color="#6D28D9",
            command=self._save_dm_shop_settings
        ).pack(side="right", fill="x", expand=True)

    def _get_party_char_options(self) -> list:
        chars = self.db.get_all_characters()
        if not chars:
            return ["Sin Héroes Guardados"]
        return [f"{c['id']}: {c['name']} ({c['char_class']} Niv.{c['level']})" for c in chars]

    def _roll_random_trinket(self):
        chosen = random.choice(TRINKETS_55E)
        self._set_entry(self.entry_loot_item, f"Bagatela: {chosen}")
        self._set_entry(self.entry_loot_kg, "0.0")

    def _send_loot_to_player(self):
        sel = self.combo_loot_char.get()
        if ":" not in sel:
            messagebox.showwarning("Sin Héroe", "Primero guarda al menos un personaje en 'Personajes 5.5e'.")
            return
        char_id = int(sel.split(":")[0])
        item_name = self.entry_loot_item.get().strip()
        try:
            kg = float(self.entry_loot_kg.get().replace(",", ".").strip() or 0.0)
            gp = int(self.entry_loot_gp.get().strip() or 0)
        except ValueError:
            messagebox.showwarning("Dato inválido", "Verifica el peso en kg y la cantidad de monedas de oro.")
            return

        if not item_name and gp == 0:
            return

        self.db.give_loot_to_character(char_id, item_name, 1, kg, gp)
        self.entry_loot_item.delete(0, "end")
        self._set_entry(self.entry_loot_gp, "0")
        messagebox.showinfo("Botín Entregado", f"¡Se envió el botín directamente a la hoja de {sel.split(':')[1].strip()}!")

    # --- LÓGICA DE CARPETAS DE AVENTURA DESPLEGABLES ---
    def _create_new_adventure_folder(self):
        dialog = ctk.CTkInputDialog(
            text="Nombre de la nueva Carpeta de Aventura / Campaña\n(ej. La Maldición de Strahd / Cripta del Liche):",
            title="Crear Carpeta de Aventura"
        )
        name = dialog.get_input()
        if not name or not name.strip():
            return
        new_id = self.db.create_adventure(name.strip())
        self.current_adventure_id = new_id
        self._refresh_adventure_tree()

    def _toggle_adv_folder(self, adv_id: int, current_exp: int):
        self.db.toggle_adventure_expanded(adv_id, not bool(current_exp))
        self.current_adventure_id = adv_id
        self._refresh_adventure_tree()

    def _delete_adv_folder(self, adv_id: int, name: str):
        advs = self.db.get_all_adventures()
        if len(advs) <= 1:
            messagebox.showwarning("Aviso", "Debe existir al menos una Carpeta de Aventura.")
            return
        if messagebox.askyesno("Eliminar Carpeta", f"¿Seguro que deseas eliminar la carpeta '{name}' y todas sus notas/encuentros internos?"):
            self.db.delete_adventure(adv_id)
            remaining = self.db.get_all_adventures()
            self.current_adventure_id = remaining[0]["id"]
            self._refresh_adventure_tree()

    def _refresh_adventure_tree(self):
        for w in self.folders_tree_scroll.winfo_children():
            w.destroy()

        adventures = self.db.get_all_adventures()
        adv_combo_vals = [f"{a['id']}: {a['name']}" for a in adventures]
        self.combo_note_adv.configure(values=adv_combo_vals)
        self.combo_loot_char.configure(values=self._get_party_char_options())

        # Seleccionar la carpeta activa en el combo
        for v in adv_combo_vals:
            if v.startswith(f"{self.current_adventure_id}:"):
                self.combo_note_adv.set(v)
                break

        cat_filter = self.combo_filter_cat.get()

        for adv in adventures:
            aid = adv["id"]
            is_exp = bool(adv.get("expanded", 1))
            notes = self.db.get_all_campaign_notes(aid)
            if cat_filter != "Todas las Categorías":
                notes = [n for n in notes if n.get("category") == cat_filter]
            encounters = self.db.get_encounters_by_adventure(aid)

            folder_card = ctk.CTkFrame(self.folders_tree_scroll, fg_color="#1E293B")
            folder_card.pack(fill="x", padx=2, pady=4)

            header_row = ctk.CTkFrame(folder_card, fg_color="transparent")
            header_row.pack(fill="x", padx=4, pady=3)

            arrow = "▼" if is_exp else "▶"
            btn_folder = ctk.CTkButton(
                header_row,
                text=f"{arrow} 📁 {adv['name']} ({len(notes)}N | {len(encounters)}E)",
                anchor="w", fg_color="#334155" if aid == self.current_adventure_id else "#1E293B",
                hover_color="#475569", height=28, font=("Segoe UI", 12, "bold"),
                command=lambda i=aid, ex=is_exp: self._toggle_adv_folder(i, ex)
            )
            btn_folder.pack(side="left", fill="x", expand=True, padx=(2, 4))

            ctk.CTkButton(
                header_row, text="✕", width=24, height=24, fg_color="#7F1D1D",
                command=lambda i=aid, nm=adv["name"]: self._delete_adv_folder(i, nm)
            ).pack(side="right", padx=2)

            if is_exp:
                sub_box = ctk.CTkFrame(folder_card, fg_color="#0F172A")
                sub_box.pack(fill="x", padx=(12, 4), pady=(0, 5))

                if not notes and not encounters:
                    ctk.CTkLabel(
                        sub_box, text="Carpeta vacía (agrega notas o encuentros)",
                        font=("Segoe UI", 10), text_color="#64748B"
                    ).pack(anchor="w", padx=8, pady=4)

                # Mostrar Notas de esta Aventura
                for n in notes:
                    att = n.get("npc_attitude", "N/A")
                    att_tag = f" • {att.split(' ')[0]}" if n.get("category") == "PNJ (NPC)" and att != "N/A" else ""
                    btn_n = ctk.CTkButton(
                        sub_box,
                        text=f"↳ [{n['category']}{att_tag}] {n['title']}",
                        anchor="w", fg_color="transparent", hover_color="#1E293B",
                        height=24, font=("Segoe UI", 11), text_color="#E2E8F0",
                        command=lambda item=n: self._load_note_into_editor(item)
                    )
                    btn_n.pack(fill="x", padx=4, pady=1)

                # Mostrar Encuentros Pre-armados de esta Aventura con botón directo al Rastreador
                for enc in encounters:
                    e_row = ctk.CTkFrame(sub_box, fg_color="#1E1B4B")
                    e_row.pack(fill="x", padx=4, pady=2)

                    total_m = sum(m.get("qty", 1) for m in enc.get("monsters", []))
                    ctk.CTkLabel(
                        e_row, text=f"⚔️ {enc['name']} ({total_m} criat.)",
                        font=("Segoe UI", 11, "bold"), text_color="#A78BFA"
                    ).pack(side="left", padx=6, pady=2)

                    ctk.CTkButton(
                        e_row, text="✕", width=22, height=20, fg_color="#7F1D1D",
                        command=lambda eid=enc["id"]: (self.db.delete_saved_encounter(eid), self._refresh_adventure_tree())
                    ).pack(side="right", padx=2, pady=2)

                    ctk.CTkButton(
                        e_row, text="Lanzar ▶", width=62, height=20, fg_color="#059669",
                        font=("Segoe UI", 10, "bold"),
                        command=lambda e_obj=enc: self._launch_preset_encounter_to_combat(e_obj)
                    ).pack(side="right", padx=2, pady=2)

    # --- LÓGICA DEL CONSTRUCTOR DE ENCUENTROS Y DIFICULTAD 5.5e ---
    def _stage_monster_for_preset(self):
        m_name = self.combo_stage_monster.get()
        try:
            qty = max(1, int(self.entry_stage_qty.get().strip() or 1))
        except ValueError:
            qty = 1

        all_m = self.db.get_all_monsters()
        target = next((m for m in all_m if m["name"] == m_name), None)
        cr_str = target.get("challenge_rating", "1/4") if target else "1/4"
        xp_each, _ = Monster55eRules.get_cr_xp_and_prof(cr_str)

        self.staged_encounter_monsters.append({"name": m_name, "qty": qty, "cr": cr_str, "xp_each": xp_each})
        self._update_staged_encounter_preview()

    def _clear_staged_encounter(self):
        self.staged_encounter_monsters.clear()
        self._update_staged_encounter_preview()

    def _update_staged_encounter_preview(self):
        self.txt_staged_list.delete("1.0", "end")
        total_xp = sum(item["qty"] * item["xp_each"] for item in self.staged_encounter_monsters)

        lines = [f"• {it['qty']}x {it['name']} (VD {it['cr']} — {it['qty']*it['xp_each']:,} XP)" for it in self.staged_encounter_monsters]
        self.txt_staged_list.insert("1.0", "\n".join(lines) if lines else "Añade criaturas arriba para pre-armar el encuentro.")

        # Calcular dificultad según el grupo guardado
        chars = self.db.get_all_characters()
        if not chars:
            self.lbl_enc_difficulty.configure(text=f"Total Encuentro: {total_xp:,} XP")
            return

        low_b = sum(XP_BUDGET_PER_CHAR_55E.get(int(c.get("level", 1)), (50, 75, 100))[0] for c in chars)
        mod_b = sum(XP_BUDGET_PER_CHAR_55E.get(int(c.get("level", 1)), (50, 75, 100))[1] for c in chars)
        high_b = sum(XP_BUDGET_PER_CHAR_55E.get(int(c.get("level", 1)), (50, 75, 100))[2] for c in chars)

        if total_xp == 0:
            diff = "Vacío"
            col = "#9CA3AF"
        elif total_xp < low_b:
            diff = "Trivial / Muy Baja"
            col = "#34D399"
        elif total_xp < mod_b:
            diff = "Dificultad BAJA"
            col = "#34D399"
        elif total_xp <= high_b:
            diff = "Dificultad MODERADA"
            col = "#FBBF24"
        else:
            diff = "Dificultad ALTA / LETAL"
            col = "#EF4444"

        self.lbl_enc_difficulty.configure(
            text=f"{diff} ({total_xp:,} XP vs Grupo de {len(chars)} PJs)",
            text_color=col
        )

    def _save_staged_encounter_to_folder(self):
        if not self.staged_encounter_monsters:
            messagebox.showwarning("Encuentro vacío", "Agrega al menos un monstruo antes de guardar el encuentro.")
            return
        adv_sel = self.combo_note_adv.get()
        adv_id = int(adv_sel.split(":")[0]) if ":" in adv_sel else self.current_adventure_id
        name = self.entry_enc_name.get().strip() or "Encuentro Guardado"

        self.db.save_encounter_preset(adv_id, name, self.staged_encounter_monsters)
        self.entry_enc_name.delete(0, "end")
        self._clear_staged_encounter()
        self.current_adventure_id = adv_id
        self._refresh_adventure_tree()
        messagebox.showinfo("Encuentro Guardado", f"Encuentro '{name}' guardado dentro de tu carpeta de aventura.")

    def _launch_preset_encounter_to_combat(self, enc_obj: dict):
        # Cargar también al grupo de héroes si no están ya en combate
        self._add_party_characters_to_combat(silent=True)

        all_monsters = self.db.get_all_monsters()
        for item in enc_obj.get("monsters", []):
            m_name = item["name"]
            qty = int(item.get("qty", 1))
            target = next((m for m in all_monsters if m["name"] == m_name), None)
            if not target:
                continue

            base_hp = Monster55eRules.parse_base_hp(target["hit_points"])
            base_ac = Monster55eRules.parse_base_ac(target["armor_class"])
            init_bonus = int(target.get("initiative_bonus", 0))
            xp_val, _ = Monster55eRules.get_cr_xp_and_prof(target.get("challenge_rating", "1/4"))

            for i in range(qty):
                display_name = f"{target['name']} #{i+1}" if qty > 1 else target["name"]
                self.combatants.append({
                    "name": display_name,
                    "is_player": False,
                    "char_id": None,
                    "initiative": 10 + init_bonus,
                    "init_mod": init_bonus,
                    "ac": base_ac,
                    "hp_curr": base_hp,
                    "hp_max": base_hp,
                    "condition": "Sin Estado",
                    "xp_value": xp_val,
                    "details": self._format_monster_statblock_text(target)
                })

        self._render_combat_list()
        self.tabs.set("Rastreador de Combate Activo")
        messagebox.showinfo("¡Encuentro Iniciado!", f"Se cargó '{enc_obj['name']}' junto con tu grupo de héroes en el Rastreador de Combate.")

    def _new_campaign_note(self):
        self.current_note_id = None
        self._set_entry(self.entry_note_title, "")
        self.combo_note_cat.set("Sesión")
        self.combo_npc_attitude.set("N/A")
        self.txt_note_content.delete("1.0", "end")
        self.txt_note_content.insert(
            "1.0",
            "Escribe aquí los detalles de la sesión, descripciones para leer en voz alta, secretos del lugar o personalidad del PNJ..."
        )

    def _save_campaign_note(self):
        adv_sel = self.combo_note_adv.get()
        adv_id = int(adv_sel.split(":")[0]) if ":" in adv_sel else self.current_adventure_id
        self.current_adventure_id = adv_id

        payload = {
            "id": self.current_note_id,
            "adventure_id": adv_id,
            "title": self.entry_note_title.get().strip() or "Nota Sin Título",
            "category": self.combo_note_cat.get(),
            "npc_attitude": self.combo_npc_attitude.get(),
            "content": self.txt_note_content.get("1.0", "end").strip()
        }
        self.current_note_id = self.db.save_campaign_note(payload)
        self._refresh_adventure_tree()
        messagebox.showinfo("Guardado", "Nota guardada en la Carpeta de Aventura.")

    def _delete_campaign_note(self):
        if not self.current_note_id:
            return
        if messagebox.askyesno("Eliminar", "¿Seguro que deseas eliminar esta nota?"):
            self.db.delete_campaign_note(self.current_note_id)
            self._new_campaign_note()
            self._refresh_adventure_tree()

    def _load_note_into_editor(self, note: dict):
        self.current_note_id = note["id"]
        self.current_adventure_id = int(note.get("adventure_id") or 1)
        self._set_entry(self.entry_note_title, note["title"])
        self.combo_note_cat.set(note.get("category", "Sesión"))
        self.combo_npc_attitude.set(note.get("npc_attitude", "N/A"))

        for v in self.combo_note_adv.cget("values"):
            if v.startswith(f"{self.current_adventure_id}:"):
                self.combo_note_adv.set(v)
                break

        self.txt_note_content.delete("1.0", "end")
        self.txt_note_content.insert("1.0", note.get("content", ""))

    # =========================================================================
    # PESTAÑA 2: RASTREADOR DE COMBATE E INICIATIVA (DADOS FÍSICOS)
    # =========================================================================
    def _build_combat_tab(self):
        self.tab_combat.grid_columnconfigure(0, weight=3)
        self.tab_combat.grid_columnconfigure(1, weight=2)
        self.tab_combat.grid_rowconfigure(3, weight=1)

        top_bar = ctk.CTkFrame(self.tab_combat, fg_color="#111827")
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=6, pady=6)

        self.lbl_round = ctk.CTkLabel(
            top_bar, text="Asalto: 1  |  Esperando Iniciativa",
            font=("Segoe UI", 16, "bold"), text_color="#FBBF24"
        )
        self.lbl_round.pack(side="left", padx=15, pady=10)

        ctk.CTkButton(
            top_bar, text="Siguiente Turno ▶", width=140, fg_color="#2563EB",
            command=self._next_turn
        ).pack(side="left", padx=6, pady=8)

        ctk.CTkButton(
            top_bar, text="Ordenar por Iniciativa Física", width=190, fg_color="#059669",
            command=self._sort_combatants_by_initiative
        ).pack(side="left", padx=6, pady=8)

        ctk.CTkButton(
            top_bar, text="Limpiar Encuentro", width=130, fg_color="#8B2635",
            command=self._clear_combat
        ).pack(side="right", padx=10, pady=8)

        self.btn_award_xp = ctk.CTkButton(
            top_bar, text="Repartir XP Acumulada (0 XP)", width=210, fg_color="#D97706",
            command=self._award_xp_to_party
        )
        self.btn_award_xp.pack(side="right", padx=6, pady=8)

        add_bar = ctk.CTkFrame(self.tab_combat, fg_color="#1F2937")
        add_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 6))

        ctk.CTkButton(
            add_bar, text="+ Cargar Héroes del Grupo", width=180, fg_color="#2E7D32",
            command=self._add_party_characters_to_combat
        ).pack(side="left", padx=10, pady=8)

        ctk.CTkLabel(add_bar, text="Añadir Monstruo:", font=("Segoe UI", 12, "bold")).pack(side="left", padx=(15, 4))
        self.combo_combat_monster = ctk.CTkComboBox(add_bar, values=self._get_monster_names_list(), width=210)
        self.combo_combat_monster.pack(side="left", padx=4)

        ctk.CTkLabel(add_bar, text="Cant.:", font=("Segoe UI", 12)).pack(side="left", padx=(6, 2))
        self.entry_monster_qty = ctk.CTkEntry(add_bar, width=45, justify="center")
        self.entry_monster_qty.insert(0, "1")
        self.entry_monster_qty.pack(side="left", padx=4)

        ctk.CTkButton(
            add_bar, text="+ Añadir al Encuentro", width=150, fg_color="#6D28D9",
            command=self._add_selected_monster_to_combat
        ).pack(side="left", padx=8, pady=8)

        # Barra de Proyector de Mapas/Handouts y Ambiente en Vivo (Fila 2)
        live_bar = ctk.CTkFrame(self.tab_combat, fg_color="#1E1B4B")
        live_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 6))

        ctk.CTkLabel(
            live_bar, text="Mesa en Vivo (Celulares):",
            font=("Segoe UI", 12, "bold"), text_color="#A78BFA"
        ).pack(side="left", padx=(10, 6), pady=6)

        ctk.CTkButton(
            live_bar, text="Proyectar Imagen / Mapa", width=175, height=28, fg_color="#6D28D9",
            command=self._upload_and_project_handout
        ).pack(side="left", padx=4, pady=6)

        ctk.CTkButton(
            live_bar, text="Quitar Imagen", width=100, height=28, fg_color="#374151",
            command=self._clear_projected_handout
        ).pack(side="left", padx=4, pady=6)

        ctk.CTkLabel(live_bar, text="Luz:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(14, 3))
        self.combo_lighting = ctk.CTkComboBox(
            live_bar, width=185, height=28,
            values=[
                "Luz brillante (Visión normal)",
                "Luz tenue (Desv. Percepción visual)",
                "Oscuridad (Cegado sin Visión Osc.)"
            ],
            command=lambda _: self._sync_live_environment()
        )
        self.combo_lighting.pack(side="left", padx=3)

        ctk.CTkLabel(live_bar, text="Ritmo Viaje:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(10, 3))
        self.combo_pace = ctk.CTkComboBox(
            live_bar, width=220, height=28,
            values=[
                "Normal (4,5 km/h | 36 km/día — Desv. Sigilo)",
                "Rápido (6 km/h | 45 km/día — Desv. Perc/Sup/Sig)",
                "Lento (3 km/h | 27 km/día — Ventaja Perc/Sup)"
            ],
            command=lambda _: self._sync_live_environment()
        )
        self.combo_pace.pack(side="left", padx=3)

        self.combat_scroll = ctk.CTkScrollableFrame(
            self.tab_combat, label_text="Orden de Iniciativa (Introduce el total de la tirada física en la casilla 'Inic.')"
        )
        self.combat_scroll.grid(row=3, column=0, sticky="nsew", padx=(6, 4), pady=4)

        inspector_frame = ctk.CTkFrame(self.tab_combat)
        inspector_frame.grid(row=3, column=1, sticky="nsew", padx=(4, 6), pady=4)
        inspector_frame.grid_columnconfigure(0, weight=1)
        inspector_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            inspector_frame, text="Perfil / Statblock del Combatiente Activo",
            font=("Segoe UI", 14, "bold")
        ).grid(row=0, column=0, padx=10, pady=8, sticky="w")

        self.txt_combat_inspector = ctk.CTkTextbox(inspector_frame, font=("Segoe UI", 12))
        self.txt_combat_inspector.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.txt_combat_inspector.insert(
            "1.0",
            "Puedes lanzar un encuentro pre-armado desde tu Carpeta de Aventura o agregar combatientes aquí.\n\n"
            "1. Pide a tus jugadores su tirada física de Iniciativa y escríbela en su casilla 'Inic.'.\n"
            "2. Presiona 'Ordenar por Iniciativa Física' para comenzar el combate."
        )

    def _get_monster_names_list(self) -> list:
        monsters = self.db.get_all_monsters()
        return [m["name"] for m in monsters] if monsters else ["Goblin Guerrero"]

    def _add_party_characters_to_combat(self, silent=False):
        chars = self.db.get_all_characters()
        if not chars:
            if not silent:
                messagebox.showinfo("Sin personajes", "Aún no hay personajes guardados en 'Personajes 5.5e'.")
            return

        existing_names = {c["name"] for c in self.combatants if c["is_player"]}
        added = 0
        for ch in chars:
            if ch["name"] in existing_names:
                continue
            stats = ch.get("stats", {})
            dex_score = int(stats.get("scores", {}).get("Destreza", 10))
            dex_mod = Monster55eRules.get_mod(dex_score)
            hp_curr = int(stats.get("hp_current", 10))
            hp_max = int(stats.get("hp_max", 10))
            ac = int(stats.get("armor_class", 12))

            self.combatants.append({
                "name": ch["name"],
                "is_player": True,
                "char_id": ch["id"],
                "initiative": 10 + dex_mod,
                "init_mod": dex_mod,
                "ac": ac,
                "hp_curr": hp_curr,
                "hp_max": hp_max,
                "condition": "Sin Estado",
                "xp_value": 0,
                "details": (
                    f"=== HÉROE: {ch['name'].upper()} (Niv. {ch['level']} {ch['species']} {ch['char_class']}) ===\n"
                    f"• Jugador: {ch.get('player_name', '')}\n"
                    f"• CA: {ac}  |  PG: {hp_curr}/{hp_max}  |  Velocidad: {stats.get('speed', '9 m')}\n"
                    f"• Bono de Iniciativa: {Monster55eRules.format_mod(dex_mod)}\n"
                )
            })
            added += 1

        self._render_combat_list()
        if added > 0 and not silent:
            messagebox.showinfo("Grupo Cargado", f"Se agregaron {added} héroes al encuentro.")

    def _add_selected_monster_to_combat(self):
        m_name = self.combo_combat_monster.get()
        all_monsters = self.db.get_all_monsters()
        target = next((m for m in all_monsters if m["name"] == m_name), None)
        if not target:
            return

        try:
            qty = max(1, int(self.entry_monster_qty.get().strip() or 1))
        except ValueError:
            qty = 1

        base_hp = Monster55eRules.parse_base_hp(target["hit_points"])
        base_ac = Monster55eRules.parse_base_ac(target["armor_class"])
        init_bonus = int(target.get("initiative_bonus", 0))
        xp_val, _ = Monster55eRules.get_cr_xp_and_prof(target.get("challenge_rating", "1/4"))

        for i in range(qty):
            display_name = f"{target['name']} #{i+1}" if qty > 1 else target["name"]
            self.combatants.append({
                "name": display_name,
                "is_player": False,
                "char_id": None,
                "initiative": 10 + init_bonus,
                "init_mod": init_bonus,
                "ac": base_ac,
                "hp_curr": base_hp,
                "hp_max": base_hp,
                "condition": "Sin Estado",
                "xp_value": xp_val,
                "details": self._format_monster_statblock_text(target)
            })

        self._render_combat_list()

    def _render_combat_list(self):
        for w in self.combat_scroll.winfo_children():
            w.destroy()

        # Sincronizar automáticamente el orden de iniciativa y estados con los celulares
        self.db.update_live_combat_state(self.round_number, self.current_turn_idx, self.combatants)

        if not self.combatants:
            ctk.CTkLabel(self.combat_scroll, text="No hay combatientes en el encuentro actual.").pack(pady=15)
            return

        for idx, c in enumerate(self.combatants):
            is_active = (idx == self.current_turn_idx)
            is_dead = (c["hp_curr"] <= 0)
            is_bloodied = (0 < c["hp_curr"] <= c["hp_max"] // 2)
            bg_col = "#1E3A8A" if is_active else ("#3F1D1D" if is_dead else "#1F2937")

            row = ctk.CTkFrame(self.combat_scroll, fg_color=bg_col)
            row.pack(fill="x", padx=4, pady=3)

            ctk.CTkLabel(row, text="Inic.:", font=("Segoe UI", 11)).pack(side="left", padx=(8, 2), pady=6)
            e_init = ctk.CTkEntry(row, width=45, justify="center")
            e_init.insert(0, str(c["initiative"]))
            e_init.pack(side="left", padx=2, pady=6)

            def make_init_bind(comb=c, entry_w=e_init):
                def on_key(_):
                    val = entry_w.get().strip().lstrip("-")
                    if val.isdigit():
                        comb["initiative"] = int(entry_w.get().strip())
                return on_key

            e_init.bind("<KeyRelease>", make_init_bind())

            tag = "[PJ]" if c["is_player"] else "[PNJ]"
            turn_marker = "▶ " if is_active else ""
            blood_tag = " [Maltrecho]" if is_bloodied else ""
            btn_name = ctk.CTkButton(
                row, text=f"{turn_marker}{tag} {c['name']} (CA {c['ac']}){blood_tag}",
                anchor="w", fg_color="transparent", hover_color="#374151",
                font=("Segoe UI", 12, "bold"), width=195,
                command=lambda comb=c: self._inspect_combatant(comb)
            )
            btn_name.pack(side="left", padx=6, pady=6)

            hp_color = "#EF4444" if is_dead else ("#FBBF24" if is_bloodied else "#34D399")
            ctk.CTkLabel(
                row, text=f"PG: {c['hp_curr']}/{c['hp_max']}",
                font=("Segoe UI", 12, "bold"), text_color=hp_color, width=85
            ).pack(side="left", padx=4)

            e_delta = ctk.CTkEntry(row, width=48, placeholder_text="Cant.")
            e_delta.pack(side="left", padx=2)

            ctk.CTkButton(
                row, text="-Daño", width=52, height=24, fg_color="#991B1B",
                command=lambda i=idx, ew=e_delta: self._modify_combatant_hp(i, ew, -1)
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                row, text="+Cura", width=52, height=24, fg_color="#065F46",
                command=lambda i=idx, ew=e_delta: self._modify_combatant_hp(i, ew, 1)
            ).pack(side="left", padx=2)

            cb_cond = ctk.CTkComboBox(
                row, values=CONDITIONS_55E, width=125, height=24, font=("Segoe UI", 11),
                command=lambda val, comb=c: comb.update({"condition": val})
            )
            cb_cond.set(c.get("condition", "Sin Estado"))
            cb_cond.pack(side="left", padx=6)

            ctk.CTkButton(
                row, text="✕", width=26, height=24, fg_color="#374151",
                command=lambda i=idx: self._remove_combatant(i)
            ).pack(side="right", padx=6)

    def _modify_combatant_hp(self, idx: int, entry_widget, sign: int):
        raw = entry_widget.get().strip()
        if not raw.isdigit():
            return
        amount = int(raw) * sign
        c = self.combatants[idx]
        old_hp = c["hp_curr"]
        c["hp_curr"] = max(0, min(c["hp_max"], old_hp + amount))

        # Si es un PJ, sincronizar también sus PG actuales en la base de datos
        if c["is_player"] and c.get("char_id"):
            ch_db = self.db.get_character_by_id(c["char_id"])
            if ch_db:
                ch_db["stats"]["hp_current"] = str(c["hp_curr"])
                self.db.save_character(ch_db)

        if not c["is_player"] and old_hp > 0 and c["hp_curr"] == 0:
            self.accumulated_xp += c.get("xp_value", 0)
            self.btn_award_xp.configure(text=f"Repartir XP Acumulada ({self.accumulated_xp:,} XP)")

        entry_widget.delete(0, "end")
        self._render_combat_list()

    def _sort_combatants_by_initiative(self):
        if not self.combatants:
            return
        self.combatants.sort(key=lambda x: (x["initiative"], x["init_mod"]), reverse=True)
        self.current_turn_idx = 0
        self._update_round_banner()
        self._render_combat_list()
        self._inspect_combatant(self.combatants[0])

    def _next_turn(self):
        if not self.combatants:
            return
        self.current_turn_idx += 1
        if self.current_turn_idx >= len(self.combatants):
            self.current_turn_idx = 0
            self.round_number += 1
        self._update_round_banner()
        self._render_combat_list()
        self._inspect_combatant(self.combatants[self.current_turn_idx])

    def _update_round_banner(self):
        if not self.combatants:
            self.lbl_round.configure(text="Asalto: 1  |  Sin Combatientes")
            return
        active = self.combatants[self.current_turn_idx]
        self.lbl_round.configure(text=f"Asalto: {self.round_number}  |  Turno de: {active['name']} (Inic. {active['initiative']})")

    def _inspect_combatant(self, comb: dict):
        self.txt_combat_inspector.delete("1.0", "end")
        self.txt_combat_inspector.insert("1.0", comb.get("details", ""))

    def _remove_combatant(self, idx: int):
        if 0 <= idx < len(self.combatants):
            self.combatants.pop(idx)
            if self.current_turn_idx >= len(self.combatants):
                self.current_turn_idx = 0
            self._render_combat_list()

    def _clear_combat(self):
        self.combatants.clear()
        self.current_turn_idx = 0
        self.round_number = 1
        self.accumulated_xp = 0
        self.btn_award_xp.configure(text="Repartir XP Acumulada (0 XP)")
        self._update_round_banner()
        self._render_combat_list()

    def _award_xp_to_party(self):
        players = [c for c in self.combatants if c["is_player"] and c.get("char_id")]
        if not players:
            messagebox.showwarning("Sin Héroes", "No hay héroes del grupo en el rastreador para recibir la XP.")
            return
        if self.accumulated_xp <= 0:
            messagebox.showinfo("Sin XP", "Aún no hay XP acumulada por monstruos derrotados.")
            return

        xp_each = self.accumulated_xp // len(players)
        for p in players:
            self.db.add_xp_to_character(p["char_id"], xp_each)

        messagebox.showinfo(
            "XP Repartida al Grupo",
            f"¡Se han repartido {self.accumulated_xp:,} XP entre {len(players)} héroes!\n"
            f"• Cada héroe recibió +{xp_each:,} XP directamente en su Hoja de Personaje."
        )
        self.accumulated_xp = 0
        self.btn_award_xp.configure(text="Repartir XP Acumulada (0 XP)")

    # =========================================================================
    # PESTAÑA 3: FRAGUA DE MONSTRUOS 5.5e (EN METROS)
    # =========================================================================
    def _build_monster_forge_tab(self):
        self.tab_forge.grid_columnconfigure(1, weight=1)
        self.tab_forge.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self.tab_forge, width=250)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(4, 8), pady=4)
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(sidebar, text="Bestiario 5.5e", font=("Segoe UI", 17, "bold")).grid(
            row=0, column=0, padx=12, pady=(10, 4), sticky="w"
        )
        ctk.CTkButton(
            sidebar, text="+ Nuevo Monstruo", fg_color="#2E7D32",
            command=self._load_blank_monster
        ).grid(row=1, column=0, padx=12, pady=4, sticky="ew")

        self.entry_bestiary_filter = ctk.CTkEntry(
            sidebar, placeholder_text="🔍 Filtrar bestiario (ej. Dragón, Diablo)..."
        )
        self.entry_bestiary_filter.grid(row=2, column=0, padx=12, pady=4, sticky="ew")
        self.entry_bestiary_filter.bind("<KeyRelease>", lambda e: self._refresh_monster_list())

        self.monster_list_scroll = ctk.CTkScrollableFrame(sidebar, label_text="Criaturas Guardadas")
        self.monster_list_scroll.grid(row=3, column=0, padx=8, pady=6, sticky="nsew")

        forge_scroll = ctk.CTkScrollableFrame(self.tab_forge)
        forge_scroll.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        forge_scroll.grid_columnconfigure((0, 1, 2), weight=1)

        self.entry_m_name = self._labeled_entry(forge_scroll, "Nombre del Monstruo", 0, 0, "Ej. Hidra de las Ciénagas")
        self.entry_m_type = self._labeled_entry(forge_scroll, "Tamaño, Tipo y Alineamiento", 0, 1, "Enorme Monstruosidad, Sin Alineamiento")

        ctk.CTkLabel(forge_scroll, text="Valor de Desafío (VD / CR)", font=("Segoe UI", 11, "bold")).grid(
            row=0, column=2, padx=8, pady=(6, 0), sticky="w"
        )
        self.combo_m_cr = ctk.CTkComboBox(
            forge_scroll, values=list(CR_TABLE_55E.keys()),
            command=lambda _: self._recalc_monster_math()
        )
        self.combo_m_cr.grid(row=1, column=2, padx=8, pady=(0, 6), sticky="ew")

        self.entry_m_ac = self._labeled_entry(forge_scroll, "Clase de Armadura (CA)", 2, 0, "15 (Armadura natural)")
        self.entry_m_hp = self._labeled_entry(forge_scroll, "Puntos de Golpe (PG y Dados)", 2, 1, "172 (15d12 + 75)")
        self.entry_m_speed = self._labeled_entry(forge_scroll, "Velocidad (en metros)", 2, 2, "9 m, Nado 9 m")

        attr_frame = ctk.CTkFrame(forge_scroll, fg_color="#1F2937")
        attr_frame.grid(row=4, column=0, columnspan=3, sticky="ew", padx=8, pady=6)
        attr_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        for idx, ab in enumerate(ABILITIES):
            col_box = ctk.CTkFrame(attr_frame, fg_color="transparent")
            col_box.grid(row=0, column=idx, padx=4, pady=6)

            ctk.CTkLabel(col_box, text=ab[:3].upper(), font=("Segoe UI", 12, "bold")).pack()
            var_sc = ctk.StringVar(value="10")
            var_sc.trace_add("write", lambda *args: self._recalc_monster_math())
            self.m_score_vars[ab] = var_sc

            ctk.CTkEntry(col_box, width=48, textvariable=var_sc, justify="center").pack(pady=2)
            lbl_m = ctk.CTkLabel(col_box, text="+0", font=("Segoe UI", 12, "bold"), text_color="#60A5FA")
            lbl_m.pack()
            self.m_mod_labels[ab] = lbl_m

        self.entry_m_senses = self._labeled_entry(forge_scroll, "Sentidos (en metros) y Percepción Pasiva", 5, 0, "Visión en la oscuridad 18 m, Percepción pasiva 14")
        self.entry_m_langs = self._labeled_entry(forge_scroll, "Idiomas", 5, 1, "Común, Dracónico")
        self.lbl_m_cr_summary = ctk.CTkLabel(
            forge_scroll, text="XP: 450 | Competencia: +2 | Inic.: +0 (Pasiva 10)",
            font=("Segoe UI", 12, "bold"), text_color="#34D399"
        )
        self.lbl_m_cr_summary.grid(row=6, column=2, padx=8, pady=4)

        ctk.CTkLabel(forge_scroll, text="Rasgos Pasivos (Traits)", font=("Segoe UI", 12, "bold")).grid(row=7, column=0, columnspan=3, padx=8, pady=(6, 2), sticky="w")
        self.txt_m_traits = ctk.CTkTextbox(forge_scroll, height=75)
        self.txt_m_traits.grid(row=8, column=0, columnspan=3, sticky="ew", padx=8, pady=2)

        ctk.CTkLabel(forge_scroll, text="Acciones (Ataques con alcances en metros)", font=("Segoe UI", 12, "bold")).grid(row=9, column=0, columnspan=3, padx=8, pady=(6, 2), sticky="w")
        self.txt_m_actions = ctk.CTkTextbox(forge_scroll, height=95)
        self.txt_m_actions.grid(row=10, column=0, columnspan=3, sticky="ew", padx=8, pady=2)

        ctk.CTkLabel(forge_scroll, text="Acciones Adicionales, Reacciones y Acciones Legendarias", font=("Segoe UI", 12, "bold")).grid(row=11, column=0, columnspan=3, padx=8, pady=(6, 2), sticky="w")
        self.txt_m_bonus = ctk.CTkTextbox(forge_scroll, height=70)
        self.txt_m_bonus.grid(row=12, column=0, columnspan=3, sticky="ew", padx=8, pady=2)

        bot_bar = ctk.CTkFrame(forge_scroll, fg_color="#111827")
        bot_bar.grid(row=13, column=0, columnspan=3, sticky="ew", padx=8, pady=8)

        self.entry_m_pdf_search = ctk.CTkEntry(bot_bar, placeholder_text="Buscar criatura en tus PDFs indexados...", width=260)
        self.entry_m_pdf_search.pack(side="left", padx=8, pady=8)
        ctk.CTkButton(bot_bar, text="Consultar PDF", width=110, fg_color="#2B4C7E", command=self._search_monster_in_pdf).pack(side="left", padx=4)

        ctk.CTkButton(bot_bar, text="Eliminar", width=80, fg_color="#8B2635", command=self._delete_current_monster).pack(side="right", padx=8, pady=8)
        ctk.CTkButton(bot_bar, text="Guardar en Bestiario", width=165, fg_color="#2563EB", command=self._save_current_monster).pack(side="right", padx=6, pady=8)

        self._refresh_monster_list()
        self._populate_monster_form(PRESET_MONSTERS_55E["Goblin Guerrero"])

    def _recalc_monster_math(self):
        mods = {}
        for ab in ABILITIES:
            raw = self.m_score_vars[ab].get().strip()
            val = int(raw) if raw.isdigit() else 10
            m = Monster55eRules.get_mod(val)
            mods[ab] = m
            self.m_mod_labels[ab].configure(text=Monster55eRules.format_mod(m))

        cr = self.combo_m_cr.get() or "1/4"
        xp, prof = Monster55eRules.get_cr_xp_and_prof(cr)
        dex_m = mods.get("Destreza", 0)
        self.lbl_m_cr_summary.configure(
            text=f"XP: {xp:,} | Comp.: +{prof} | Inic.: {Monster55eRules.format_mod(dex_m)} (Pasiva {10 + dex_m})"
        )

    def _format_monster_statblock_text(self, m: dict) -> str:
        sb = m.get("statblock", {})
        scores = sb.get("scores", {})
        xp, prof = Monster55eRules.get_cr_xp_and_prof(m.get("challenge_rating", "1/4"))
        init_b = int(m.get("initiative_bonus", 0))

        score_line = " | ".join([
            f"{ab[:3].upper()} {scores.get(ab, 10)} ({Monster55eRules.format_mod(Monster55eRules.get_mod(int(scores.get(ab, 10))))})"
            for ab in ABILITIES
        ])

        lines = [
            f"=== {m['name'].upper()} ===",
            f"{m.get('size_type_alignment', '')}",
            f"• CA: {m.get('armor_class', '12')}   |   Iniciativa: {Monster55eRules.format_mod(init_b)} (Pasiva {10 + init_b})",
            f"• PG: {m.get('hit_points', '10')}   |   Velocidad: {m.get('speed', '9 m')}",
            f"--------------------------------------------------",
            score_line,
            f"--------------------------------------------------",
            f"• Sentidos: {sb.get('senses', 'Percepción pasiva 10')}",
            f"• Idiomas: {sb.get('languages', '—')}",
            f"• VD (CR): {m.get('challenge_rating', '1/4')} ({xp:,} XP  |  Bono de Competencia +{prof})",
            f"\n[RASGOS]",
            sb.get("traits", "Ninguno."),
            f"\n[ACCIONES]",
            sb.get("actions", "Ninguna.")
        ]
        if sb.get("bonus_reactions"):
            lines.append("\n[ACCIONES ADICIONALES / REACCIONES / LEGENDARIAS]")
            lines.append(sb["bonus_reactions"])
        return "\n".join(lines)

    def _populate_monster_form(self, m: dict):
        self.current_monster_id = m.get("id")
        self._set_entry(self.entry_m_name, m.get("name", ""))
        self._set_entry(self.entry_m_type, m.get("size_type_alignment", ""))
        self.combo_m_cr.set(str(m.get("challenge_rating", "1/4")))
        self._set_entry(self.entry_m_ac, m.get("armor_class", "12"))
        self._set_entry(self.entry_m_hp, m.get("hit_points", "10 (2d8)"))
        self._set_entry(self.entry_m_speed, m.get("speed", "9 m"))

        sb = m.get("statblock", {})
        scores = sb.get("scores", {})
        for ab in ABILITIES:
            self.m_score_vars[ab].set(str(scores.get(ab, 10)))

        self._set_entry(self.entry_m_senses, sb.get("senses", "Percepción pasiva 10"))
        self._set_entry(self.entry_m_langs, sb.get("languages", "Común"))

        self.txt_m_traits.delete("1.0", "end")
        self.txt_m_traits.insert("1.0", sb.get("traits", ""))

        self.txt_m_actions.delete("1.0", "end")
        self.txt_m_actions.insert("1.0", sb.get("actions", ""))

        self.txt_m_bonus.delete("1.0", "end")
        self.txt_m_bonus.insert("1.0", sb.get("bonus_reactions", ""))

        self._recalc_monster_math()

    def _load_blank_monster(self):
        self._populate_monster_form({
            "id": None,
            "name": "",
            "size_type_alignment": "Mediano Monstruosidad, Neutral",
            "armor_class": "14 (Armadura natural)",
            "hit_points": "45 (6d8 + 18)",
            "speed": "9 m",
            "challenge_rating": "2",
            "statblock": {
                "scores": {ab: 12 for ab in ABILITIES},
                "senses": "Visión en la oscuridad 18 m, Percepción pasiva 11",
                "languages": "Común",
                "traits": "",
                "actions": "",
                "bonus_reactions": ""
            }
        })

    def _save_current_monster(self):
        scores = {ab: int(self.m_score_vars[ab].get().strip() or 10) for ab in ABILITIES}
        dex_mod = Monster55eRules.get_mod(scores["Destreza"])
        payload = {
            "id": self.current_monster_id,
            "name": self.entry_m_name.get().strip() or "Criatura Sin Nombre",
            "size_type_alignment": self.entry_m_type.get().strip(),
            "armor_class": self.entry_m_ac.get().strip(),
            "hit_points": self.entry_m_hp.get().strip(),
            "speed": self.entry_m_speed.get().strip(),
            "initiative_bonus": dex_mod,
            "challenge_rating": self.combo_m_cr.get(),
            "statblock": {
                "scores": scores,
                "senses": self.entry_m_senses.get().strip(),
                "languages": self.entry_m_langs.get().strip(),
                "traits": self.txt_m_traits.get("1.0", "end").strip(),
                "actions": self.txt_m_actions.get("1.0", "end").strip(),
                "bonus_reactions": self.txt_m_bonus.get("1.0", "end").strip()
            }
        }
        self.current_monster_id = self.db.save_monster(payload)
        self._refresh_monster_list()
        m_list = self._get_monster_names_list()
        self.combo_combat_monster.configure(values=m_list)
        self.combo_stage_monster.configure(values=m_list)
        messagebox.showinfo("Bestiario", f"'{payload['name']}' guardado en el Bestiario.")

    def _delete_current_monster(self):
        if not self.current_monster_id:
            return
        if messagebox.askyesno("Eliminar", "¿Seguro que deseas eliminar este monstruo del Bestiario?"):
            self.db.delete_monster(self.current_monster_id)
            self._load_blank_monster()
            self._refresh_monster_list()
            m_list = self._get_monster_names_list()
            self.combo_combat_monster.configure(values=m_list)
            self.combo_stage_monster.configure(values=m_list)

    def _refresh_monster_list(self):
        for w in self.monster_list_scroll.winfo_children():
            w.destroy()

        monsters = self.db.get_all_monsters()
        q = ""
        if hasattr(self, "entry_bestiary_filter"):
            q = self.entry_bestiary_filter.get().strip().lower()

        filtered = [
            m for m in monsters
            if not q or q in m["name"].lower() or q in m.get("size_type_alignment", "").lower() or q == str(m.get("challenge_rating", "")).lower()
        ]

        # Mostrar hasta 60 tarjetas a la vez en el scroll para mantener la interfaz ultrarrápida
        for m in filtered[:60]:
            btn = ctk.CTkButton(
                self.monster_list_scroll,
                text=f"{m['name']} (VD {m['challenge_rating']})",
                anchor="w", fg_color="#2B4C7E", hover_color="#1E3A8A",
                command=lambda mon=m: self._populate_monster_form(mon)
            )
            btn.pack(fill="x", padx=4, pady=2)

        if len(filtered) > 60:
            ctk.CTkLabel(
                self.monster_list_scroll,
                text=f"+ {len(filtered) - 60} más (usa el buscador arriba para filtrar)...",
                font=("Segoe UI", 10), text_color="#9CA3AF"
            ).pack(pady=4)

        # Actualizar también los desplegables de combate y pre-armado de encuentros
        names = [m["name"] for m in monsters] if monsters else ["Goblin Guerrero"]
        if hasattr(self, "combo_combat_monster"):
            self.combo_combat_monster.configure(values=names)
        if hasattr(self, "combo_stage_monster"):
            self.combo_stage_monster.configure(values=names)

    def _search_monster_in_pdf(self):
        q = self.entry_m_pdf_search.get().strip()
        if not q:
            return
        hits = self.db.search_manuals(q, limit=4)
        if not hits:
            messagebox.showinfo("Búsqueda PDF", f"No se encontraron coincidencias para '{q}' en los PDFs indexados.")
            return
        lines = [f"Extractos encontrados en tus PDFs para '{q}':\n"]
        for h in hits:
            lines.append(f"[{h['manual_title']} - Pág. {h['page_number']}]:\n{h['match_snippet']}\n")
        messagebox.showinfo("Referencia del Manual PDF", "\n".join(lines))

    def _set_entry(self, entry_widget, text: str):
        entry_widget.delete(0, "end")
        entry_widget.insert(0, str(text))

    def _labeled_entry(self, parent, label_text, row, col, placeholder=""):
        ctk.CTkLabel(parent, text=label_text, font=("Segoe UI", 11, "bold")).grid(
            row=row, column=col, padx=8, pady=(6, 0), sticky="w"
        )
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder)
        entry.grid(row=row + 1, column=col, padx=8, pady=(0, 6), sticky="ew")
        return entry

    def _save_dm_shop_settings(self):
        name = self.entry_shop_name.get().strip() or "Tienda del Pueblo"
        preset = self.combo_shop_preset.get()
        mult_str = self.combo_shop_mult.get().split("%")[0].strip()
        mult = float(int(mult_str) / 100.0) if mult_str.isdigit() else 1.0
        is_open = self.chk_shop_open_var.get()

        self.db.update_shop_state(name, preset, mult, is_open)
        messagebox.showinfo(
            "Tienda Sincronizada",
            f"🏪 '{name}' ({preset}) actualizada para los celulares.\n"
            f"• Estado: {'Abierta' if is_open else 'Cerrada'}\n"
            f"• Multiplicador de Precios: {int(mult * 100)}%"
        )
    # =========================================================================
    # PESTAÑA 4: PANTALLA DE REFERENCIA RÁPIDA, VIAJE, LUZ Y ESTADOS (OPCIÓN 4)
    # =========================================================================
    def _build_quick_reference_tab(self):
        self.tab_ref.grid_columnconfigure((0, 1), weight=1)
        self.tab_ref.grid_rowconfigure(1, weight=1)

        # --- PANEL SUPERIOR IZQUIERDO: CALCULADORA DE RITMO DE VIAJE E ILUMINACIÓN (PÁGS. 19-20) ---
        travel_card = ctk.CTkFrame(self.tab_ref, fg_color="#1E293B")
        travel_card.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        travel_card.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(
            travel_card, text="Calculadora de Viaje y Exploración (Cap. 1, Pág. 20)",
            font=("Segoe UI", 14, "bold"), text_color="#FBBF24"
        ).grid(row=0, column=0, columnspan=3, padx=12, pady=(10, 4), sticky="w")

        ctk.CTkLabel(travel_card, text="Ritmo de Viaje:", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, padx=10, sticky="w")
        self.combo_travel_pace = ctk.CTkComboBox(
            travel_card,
            values=["Rápido (120 m/min | 6 km/h | 45 km/día)",
                    "Normal (90 m/min | 4,5 km/h | 36 km/día)",
                    "Lento (60 m/min | 3 km/h | 27 km/día)"],
            command=lambda _: self._recalc_travel_pace()
        )
        self.combo_travel_pace.set("Normal (90 m/min | 4,5 km/h | 36 km/día)")
        self.combo_travel_pace.grid(row=2, column=0, padx=10, pady=(2, 6), sticky="ew")

        ctk.CTkLabel(travel_card, text="Horas de Viaje:", font=("Segoe UI", 11, "bold")).grid(row=1, column=1, padx=6, sticky="w")
        self.entry_travel_hours = ctk.CTkEntry(travel_card, width=70, justify="center")
        self.entry_travel_hours.insert(0, "8")
        self.entry_travel_hours.bind("<KeyRelease>", lambda e: self._recalc_travel_pace())
        self.entry_travel_hours.grid(row=2, column=1, padx=6, pady=(2, 6))

        self.chk_mounted_gallop = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            travel_card, text="Monturas al galope (x2 por 1h)",
            variable=self.chk_mounted_gallop, command=self._recalc_travel_pace
        ).grid(row=2, column=2, padx=10, pady=(2, 6))

        self.lbl_travel_result = ctk.CTkLabel(
            travel_card, text="", font=("Segoe UI", 12, "bold"),
            text_color="#34D399", justify="left", wraplength=540
        )
        self.lbl_travel_result.grid(row=3, column=0, columnspan=3, padx=12, pady=(4, 10), sticky="w")

        # --- PANEL SUPERIOR DERECHO: ILUMINACIÓN, VISIÓN Y COBERTURA (PÁGS. 19 Y 26) ---
        env_card = ctk.CTkFrame(self.tab_ref, fg_color="#1E293B")
        env_card.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)

        ctk.CTkLabel(
            env_card, text="Visión, Iluminación y Cobertura (Págs. 19 y 26)",
            font=("Segoe UI", 14, "bold"), text_color="#60A5FA"
        ).pack(anchor="w", padx=12, pady=(10, 4))

        env_text = (
            "• Luz Brillante: Visión normal (día, antorchas en radio de 6 m, linternas en 9 m).\n"
            "• Luz Tenue (Zona Ligeramente Oscura): Sombras, amanecer o neblina. Impone DESVENTAJA en pruebas de Sabiduría (Percepción) que dependan de la vista.\n"
            "• Oscuridad (Zona Muy Oscura): Noche cerrada, mazmorra sin luz o niebla espesa. Impone el estado CEGADO al tratar de ver algo en ella.\n"
            "-------------------------------------------------------------------------\n"
            "• Cobertura Media (+2 CA y Salv. Destreza): Obstáculo o criatura que cubre al menos la mitad.\n"
            "• Cobertura Tres Cuartos (+5 CA y Salv. Destreza): Cubre al menos 3/4 del objetivo.\n"
            "• Cobertura Completa: No puede ser objetivo directo de ataques ni conjuros."
        )
        ctk.CTkLabel(
            env_card, text=env_text, font=("Segoe UI", 11),
            justify="left", wraplength=560, text_color="#E2E8F0"
        ).pack(anchor="w", padx=12, pady=(2, 10))

        # --- PANEL INFERIOR COMPLETO: BUSCADOR DE ESTADOS, ACCIONES Y PELIGROS (CAP. 1) ---
        ref_bottom = ctk.CTkFrame(self.tab_ref)
        ref_bottom.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)
        ref_bottom.grid_columnconfigure(1, weight=1)
        ref_bottom.grid_rowconfigure(1, weight=1)

        search_row = ctk.CTkFrame(ref_bottom, fg_color="transparent")
        search_row.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=6)

        ctk.CTkLabel(
            search_row, text="Glosario Rápido 5.5e (Estados, Acciones y Peligros):",
            font=("Segoe UI", 13, "bold")
        ).pack(side="left", padx=(4, 10))

        self.entry_ref_filter = ctk.CTkEntry(
            search_row, placeholder_text="Filtrar estado, acción o peligro (ej. Derribado, Cansancio, Esquivar, Caídas)...",
            width=360
        )
        self.entry_ref_filter.pack(side="left", fill="x", expand=True, padx=4)
        self.entry_ref_filter.bind("<KeyRelease>", lambda e: self._render_quick_ref_glossary())

        self.ref_list_scroll = ctk.CTkScrollableFrame(ref_bottom, width=290, label_text="Términos Oficiales")
        self.ref_list_scroll.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=(0, 8))

        self.txt_ref_detail = ctk.CTkTextbox(ref_bottom, font=("Segoe UI", 13))
        self.txt_ref_detail.grid(row=1, column=1, sticky="nsew", padx=(4, 8), pady=(0, 8))

        self._init_glossary_data()
        self._recalc_travel_pace()
        self._render_quick_ref_glossary()

    def _recalc_travel_pace(self):
        pace = self.combo_travel_pace.get()
        raw_h = self.entry_travel_hours.get().strip().replace(",", ".")
        try:
            hours = max(0.0, float(raw_h))
        except ValueError:
            hours = 8.0

        if pace.startswith("Rápido"):
            km_h, m_min = 6.0, 120
            effect = "Efecto en Juego: DESVENTAJA en Sabiduría (Percepción o Supervivencia) y Destreza (Sigilo)."
        elif pace.startswith("Lento"):
            km_h, m_min = 3.0, 60
            effect = "Efecto en Juego: VENTAJA en pruebas de Sabiduría (Percepción o Supervivencia)."
        else:
            km_h, m_min = 4.5, 90
            effect = "Efecto en Juego: DESVENTAJA en pruebas de Destreza (Sigilo)."

        total_km = hours * km_h
        if self.chk_mounted_gallop.get() and hours >= 1.0:
            total_km += km_h  # 1 hora al doble de velocidad

        self.lbl_travel_result.configure(
            text=f"Distancia Recorrida en {hours:g} h: {total_km:.1f} km ({m_min} m por minuto)\n{effect}"
        )

    def _init_glossary_data(self):
        self.glossary_55e = {
            "[Estado] Agarrado (Grappled)": (
                "• Velocidad 0: Tu velocidad es 0 y no puede aumentar.\n"
                "• Ataques afectados: Tienes Desventaja en las tiradas de ataque contra cualquier objetivo que no sea quien te agarra.\n"
                "• Movible: Quien te agarra puede arrastrarte o llevarte cuando se mueve, pero cada metro de movimiento le cuesta 1 m adicional a menos que seas Diminuto o dos tamaños más pequeño."
            ),
            "[Estado] Apresado (Restrained)": (
                "• Velocidad 0: Tu velocidad es 0 y no puede aumentar.\n"
                "• Ataques afectados: Las tiradas de ataque contra ti tienen Ventaja, y tus tiradas de ataque tienen Desventaja.\n"
                "• Salvaciones afectadas: Tienes Desventaja en las tiradas de salvación de Destreza."
            ),
            "[Estado] Asustado (Frightened)": (
                "• Pruebas y ataques afectados: Tienes Desventaja en las pruebas de característica y tiradas de ataque mientras la fuente de tu miedo esté en tu línea de visión.\n"
                "• Sin acercarse: No puedes moverte voluntariamente más cerca de la fuente de tu miedo."
            ),
            "[Estado] Aturdido (Stunned)": (
                "• Incapacitado: Tienes el estado de Incapacitado (no puedes realizar acciones, acciones adicionales ni reacciones y pierdes concentración).\n"
                "• Salvaciones afectadas: Fallas automáticamente las tiradas de salvación de Fuerza y Destreza.\n"
                "• Ataques afectados: Las tiradas de ataque contra ti tienen Ventaja."
            ),
            "[Estado] Cansancio / Exhaustion (Regla 2024)": (
                "• Niveles de Cansancio (1 a 6): Este estado es acumulativo. Si llegas al Nivel 6 de Cansancio, mueres.\n"
                "• Penalizador a Pruebas con d20: Cuando haces una Prueba con d20 (ataque, habilidad o salvación), restas 2 veces tu nivel de cansancio al total.\n"
                "• Velocidad reducida: Tu velocidad se reduce en 1,5 m multiplicado por tu nivel de cansancio.\n"
                "• Recuperación: Finalizar un Descanso Largo reduce tu nivel de cansancio en 1."
            ),
            "[Estado] Cegado (Blinded)": (
                "• No puedes ver: Fallas automáticamente cualquier prueba de característica que requiera la vista.\n"
                "• Ataques afectados: Las tiradas de ataque contra ti tienen Ventaja, y tus tiradas de ataque tienen Desventaja."
            ),
            "[Estado] Derribado (Prone)": (
                "• Movimiento restringido: Tus únicas opciones de movimiento son arrastrarte (cada 1 m cuesta 1 m adicional) o gastar una cantidad de movimiento igual a la mitad de tu velocidad (redondeado abajo) para ponerte de pie y terminar el estado.\n"
                "• Ataques afectados: Tienes Desventaja en tus tiradas de ataque. Una tirada de ataque contra ti tiene Ventaja si el atacante está a 1,5 m o menos de ti; de lo contrario, esa tirada de ataque tiene Desventaja."
            ),
            "[Estado] Ensordecido (Deafened)": (
                "• No puedes oír: Fallas automáticamente cualquier prueba de característica que requiera el oído."
            ),
            "[Estado] Envenenado (Poisoned)": (
                "• Pruebas y ataques afectados: Tienes Desventaja en las tiradas de ataque y en las pruebas de característica."
            ),
            "[Estado] Hechizado (Charmed)": (
                "• No dañar al encantador: No puedes atacar a quien te hechizó ni hacerlo objetivo de capacidades dañinas o efectos mágicos.\n"
                "• Ventaja social: Quien te hechizó tiene Ventaja en cualquier prueba de característica para interactuar socialmente contigo."
            ),
            "[Estado] Incapacitado (Incapacitated)": (
                "• Inactivo: No puedes llevar a cabo ninguna acción, acción adicional ni reacción.\n"
                "• Sin concentración: Tu concentración se rompe.\n"
                "• Sin hablar: No puedes hablar.\n"
                "• Sorprendido: Si estás Incapacitado cuando tiras Iniciativa, tienes Desventaja en la tirada."
            ),
            "[Estado] Inconsciente (Unconscious)": (
                "• Estados combinados: Tienes los estados de Incapacitado y Derribado, y sueltas todo lo que estés sosteniendo.\n"
                "• Velocidad 0 y sin consciencia de tu entorno.\n"
                "• Ataques afectados: Las tiradas de ataque contra ti tienen Ventaja, y cualquier ataque que te acierte es un Crítico si el atacante está a 1,5 m o menos de ti.\n"
                "• Fallas automáticamente las salvaciones de Fuerza y Destreza."
            ),
            "[Estado] Invisible": (
                "• Sorpresa: Si eres Invisible cuando tiras Iniciativa, tienes Ventaja en la tirada.\n"
                "• Oculto: No te afecta ningún efecto que requiera que su objetivo sea visto (a menos que el creador pueda verte de algún modo).\n"
                "• Ataques afectados: Las tiradas de ataque contra ti tienen Desventaja, y tus tiradas de ataque tienen Ventaja."
            ),
            "[Estado] Paralizado (Paralyzed)": (
                "• Incapacitado: Tienes el estado de Incapacitado, tu velocidad es 0 y no puedes hablar.\n"
                "• Salvaciones afectadas: Fallas automáticamente las salvaciones de Fuerza y Destreza.\n"
                "• Ataques y Críticos: Las tiradas de ataque contra ti tienen Ventaja, y cualquier ataque que te acierte es un Crítico si el atacante está a 1,5 m o menos de ti."
            ),
            "[Estado] Petrificado (Petrified)": (
                "• Transformado en piedra: Tu peso se multiplica por 10, dejas de envejecer y tienes el estado Incapacitado.\n"
                "• Resistencia total: Tienes Resistencia a todo el daño e Inmunidad al veneno y al estado Envenenado.\n"
                "• Fallas automáticamente las salvaciones de Fuerza y Destreza."
            ),
            "[Acción] Ayudar (Help - Pág. 15)": (
                "• Primeros Auxilios: Estabilizas a una criatura con 0 PG a 1,5 m de ti superando Sabiduría (Medicina) CD 10.\n"
                "• Asistir en Prueba de Característica: Eliges una habilidad o herramienta en la que tú seas competente y otra criatura a 1,5 m; esa criatura tiene Ventaja en la siguiente prueba que haga con ella.\n"
                "• Asistir en Ataque: Distraes a un enemigo a 1,5 m de ti; la siguiente tirada de ataque de un aliado contra ese enemigo tiene Ventaja."
            ),
            "[Acción] Buscar, Estudiar e Influir (Pág. 15)": (
                "• Buscar (Sabiduría): Medicina, Percepción, Perspicacia o Supervivencia.\n"
                "• Estudiar (Inteligencia): Conocimiento arcano, Historia, Investigación, Naturaleza o Religión.\n"
                "• Influir (Carisma o Sabiduría): Engaño, Interpretación, Intimidación, Persuasión o Trato con animales. Si el PNJ es Amistoso tienes Ventaja; si es Hostil tienes Desventaja."
            ),
            "[Acción] Esquivar, Destrabarse y Esconderse (Pág. 15)": (
                "• Esquivar: Hasta tu próximo turno, ataques contra ti tienen Desventaja y tienes Ventaja en salvaciones de Destreza.\n"
                "• Destrabarse: Tu movimiento no provoca ataques de oportunidad por el resto del turno.\n"
                "• Esconderse: Haces una prueba de Destreza (Sigilo) CD 15 estando Muy Oscurecido o tras cobertura Tres Cuartos/Completa fuera de línea de visión enemiga. Si tienes éxito ganas el estado Invisible."
            ),
            "[Peligro] Caídas, Asfixia y Fuego (Pág. 20)": (
                "• Caídas: Sufres 1d6 de daño contundente por cada 3 m de caída (máximo 20d6) y terminas Derribado si sufres daño.\n"
                "• Asfixia: Puedes aguantar la respiración 1 + Mod. CON minutos (mín. 30 seg). Al agotarse, ganas 1 nivel de Cansancio al final de cada uno de tus turnos.\n"
                "• Arder (Burning): Sufres 1d4 de daño de fuego al inicio de cada uno de tus turnos hasta que alguien use una acción o te tires al suelo (Derribado) y ruedes para apagar las llamas."
            )
        }

    def _render_quick_ref_glossary(self):
        for w in self.ref_list_scroll.winfo_children():
            w.destroy()

        q = self.entry_ref_filter.get().strip().lower()
        first_key = None

        for title, desc in self.glossary_55e.items():
            if q and q not in title.lower() and q not in desc.lower():
                continue
            if first_key is None:
                first_key = title

            btn = ctk.CTkButton(
                self.ref_list_scroll, text=title, anchor="w",
                fg_color="#2B4C7E" if "[Estado]" in title else "#374151",
                hover_color="#1E3A8A", height=28, font=("Segoe UI", 11, "bold"),
                command=lambda t=title, d=desc: self._show_glossary_entry(t, d)
            )
            btn.pack(fill="x", padx=3, pady=2)

        if first_key:
            self._show_glossary_entry(first_key, self.glossary_55e[first_key])

    def _show_glossary_entry(self, title: str, desc: str):
        self.txt_ref_detail.delete("1.0", "end")
        self.txt_ref_detail.insert("1.0", f"=== {title.upper()} ===\n\n{desc}")

    def _upload_and_project_handout(self):
        path = filedialog.askopenfilename(
            title="Selecciona un Mapa, Carta o Ilustración para proyectar en los celulares",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if not path:
            return
        dialog = ctk.CTkInputDialog(
            text="Título o descripción para los jugadores (ej. Mapa de Barovia / Carta del Burgomaestre):",
            title="Proyectar en Celulares"
        )
        title = dialog.get_input() or "Imagen compartida por el DM"

        try:
            img = Image.open(path).convert("RGB")
            img.thumbnail((1100, 1100))
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=82)
            b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")

            self.db.update_live_handout(title, "Proyectado por el DM en la Mesa en Vivo.", b64_str)
            messagebox.showinfo("Proyectado", f"'{title}' ya aparece en los celulares de todos tus jugadores.")
        except Exception as err:
            messagebox.showerror("Error con la imagen", str(err))

    def _clear_projected_handout(self):
        self.db.update_live_handout("Sin imagen proyectada", "El DM ha retirado la imagen de la mesa.", "")
        messagebox.showinfo("Imagen Retirada", "Se limpió el proyector de los celulares.")

    def _sync_live_environment(self):
        self.db.update_live_environment(self.combo_lighting.get(), self.combo_pace.get())