import json
import customtkinter as ctk
from tkinter import filedialog, messagebox
from database.db_manager import DatabaseManager
from models.character_55e import (
    Character55eRules, SPECIES_55E, BACKGROUNDS_55E, CLASSES_55E,
    WEAPON_MASTERIES_55E, ABILITIES, SKILLS_55E, LANGUAGES_55E,
    MUSICAL_INSTRUMENTS, GAMING_SETS, SPELLS_CATALOG_55E,
    XP_THRESHOLDS_55E, MOUNTS_CAPACITY_KG, ARMORS_CATALOG_55E,
    WEAPONS_CATALOG_55E, ITEMS_CATALOG_BY_CATEGORY, PACK_CONTENTS_55E,
    SPECIES_LINEAGES_55E, ELD_INVOCATIONS_55E, FIGHTING_STYLES_55E,
    GENERAL_FEATS_55E, EPIC_BOONS_55E, MAGIC_ITEMS_ATTUNEMENT_55E
)

class ItemCatalogModal(ctk.CTkToplevel):
    """Buscador y Catálogo Completo del Capítulo 6 (Equipo.pdf) con auto-desempaquetado de Paquetes."""
    def __init__(self, parent_view, default_target="char", container_idx=None):
        super().__init__(parent_view)
        self.parent_view = parent_view
        self.default_target = default_target
        self.container_idx = container_idx

        self.title("Catálogo Oficial Capítulo 6: Equipo (D&D 5.5e)")
        self.geometry("760x680")
        self.grab_set()

        self._build_ui()
        self._render_catalog()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(header, text="Catálogo Oficial de Equipo (Capítulo 6)", font=("Segoe UI", 16, "bold")).pack(
            side="left", padx=15, pady=10
        )

        dest_frame = ctk.CTkFrame(header, fg_color="transparent")
        dest_frame.pack(side="right", padx=12)
        ctk.CTkLabel(dest_frame, text="Enviar a:", font=("Segoe UI", 12, "bold")).pack(side="left", padx=4)

        self.dest_options = self._build_destination_options()
        self.combo_dest = ctk.CTkComboBox(dest_frame, values=list(self.dest_options.keys()), width=250)
        self.combo_dest.pack(side="left", padx=4)

        if self.container_idx is not None:
            prefix = f"[Contenedor {'PJ' if self.default_target == 'char' else 'Montura'} #{self.container_idx + 1}]"
            for k in self.dest_options:
                if k.startswith(prefix):
                    self.combo_dest.set(k)
                    break
        elif self.default_target == "mount":
            self.combo_dest.set("Inventario de la Montura")
        else:
            self.combo_dest.set("Inventario del Personaje")

        filter_bar = ctk.CTkFrame(self)
        filter_bar.grid(row=1, column=0, sticky="ew", padx=12, pady=8)
        filter_bar.grid_columnconfigure(0, weight=1)

        self.entry_search = ctk.CTkEntry(filter_bar, placeholder_text="Buscar cualquier objeto del manual (ej. Paquete, Aljaba, Ácido, Mosquete, Herramientas)...")
        self.entry_search.grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        self.entry_search.bind("<KeyRelease>", lambda e: self._render_catalog())

        categories = ["Todas las Categorías"] + list(ITEMS_CATALOG_BY_CATEGORY.keys())
        self.combo_cat = ctk.CTkComboBox(filter_bar, values=categories, width=230, command=lambda _: self._render_catalog())
        self.combo_cat.set("Todas las Categorías")
        self.combo_cat.grid(row=0, column=1, padx=6, pady=6)

        ctk.CTkLabel(filter_bar, text="Cant.:", font=("Segoe UI", 12)).grid(row=0, column=2, padx=(6, 2))
        self.entry_qty = ctk.CTkEntry(filter_bar, width=48, justify="center")
        self.entry_qty.insert(0, "1")
        self.entry_qty.grid(row=0, column=3, padx=(0, 8), pady=6)

        self.catalog_scroll = ctk.CTkScrollableFrame(self)
        self.catalog_scroll.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 8))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=12, pady=8)
        ctk.CTkButton(footer, text="Cerrar Catálogo", width=130, fg_color="#374151", command=self.destroy).pack(side="right")

    def _build_destination_options(self) -> dict:
        opts = {
            "Inventario del Personaje": ("char", None),
            "Inventario de la Montura": ("mount", None),
        }
        for idx, it in enumerate(self.parent_view.builder_state.get("inventory_char", [])):
            if it.get("is_container"):
                opts[f"[Contenedor PJ #{idx+1}] {it['name']}"] = ("char", idx)
        for idx, it in enumerate(self.parent_view.builder_state.get("inventory_mount", [])):
            if it.get("is_container"):
                opts[f"[Contenedor Montura #{idx+1}] {it['name']}"] = ("mount", idx)
        return opts

    def _render_catalog(self):
        for w in self.catalog_scroll.winfo_children():
            w.destroy()

        query = self.entry_search.get().strip().lower()
        selected_cat = self.combo_cat.get()

        for cat_name, items in ITEMS_CATALOG_BY_CATEGORY.items():
            if selected_cat != "Todas las Categorías" and selected_cat != cat_name:
                continue

            filtered = [
                it for it in items
                if not query or query in it["name"].lower() or query in it.get("desc", "").lower()
            ]
            if not filtered:
                continue

            banner = ctk.CTkFrame(self.catalog_scroll, fg_color="#374151", height=28)
            banner.pack(fill="x", padx=4, pady=(8, 2))
            ctk.CTkLabel(banner, text=f"{cat_name} ({len(filtered)})", font=("Segoe UI", 12, "bold")).pack(
                side="left", padx=10, pady=3
            )

            for item_tpl in filtered:
                card = ctk.CTkFrame(self.catalog_scroll, fg_color="#1F2937")
                card.pack(fill="x", padx=4, pady=2)

                top = ctk.CTkFrame(card, fg_color="transparent")
                top.pack(fill="x", padx=8, pady=(4, 1))

                price_str = f" | {item_tpl.get('price', '')}" if item_tpl.get("price") else ""
                tag = " [Contenedor]" if item_tpl.get("is_container") else (" [Paquete Auto-Desplegable]" if item_tpl.get("is_pack") else "")
                ctk.CTkLabel(
                    top, text=f"{item_tpl['name']}{tag} — {item_tpl['weight_kg']} kg{price_str}",
                    font=("Segoe UI", 12, "bold"), text_color="#F3F4F6"
                ).pack(side="left")

                ctk.CTkButton(
                    top, text="+ Agregar", width=85, height=24, fg_color="#2563EB",
                    command=lambda tpl=item_tpl: self._add_selected_item(tpl)
                ).pack(side="right")

                if item_tpl.get("desc"):
                    ctk.CTkLabel(
                        card, text=item_tpl["desc"], font=("Segoe UI", 11),
                        text_color="#9CA3AF", wraplength=600, justify="left"
                    ).pack(anchor="w", padx=10, pady=(0, 4))

    def _add_selected_item(self, tpl: dict):
        try:
            qty = max(1, int(self.entry_qty.get().strip() or 1))
        except ValueError:
            qty = 1

        dest_key = self.combo_dest.get()
        target_list_type, cont_idx = self.dest_options.get(dest_key, ("char", None))
        inv_key = "inventory_char" if target_list_type == "char" else "inventory_mount"
        inv_list = self.parent_view.builder_state.setdefault(inv_key, [])

        # Si es uno de los 7 Paquetes Oficiales del manual, crear su Mochila/Cofre con todos los objetos adentro
        if tpl.get("is_pack") and tpl["name"] in PACK_CONTENTS_55E:
            pack_info = PACK_CONTENTS_55E[tpl["name"]]
            cont_info = pack_info["container"]
            inv_list.append({
                "name": cont_info["name"],
                "qty": 1,
                "weight_kg": cont_info["weight_kg"],
                "is_container": True,
                "max_capacity_kg": cont_info.get("max_capacity_kg", 15.0),
                "ignore_contents_weight": False,
                "expanded": True,
                "contents": [dict(sub) for sub in pack_info["items"]]
            })
        else:
            new_obj = {
                "name": tpl["name"].strip(),
                "qty": qty,
                "weight_kg": float(tpl["weight_kg"]),
                "is_container": bool(tpl.get("is_container", False)),
                "max_capacity_kg": tpl.get("max_capacity_kg"),
                "ignore_contents_weight": bool(tpl.get("ignore_contents_weight", False)),
                "expanded": True,
                "contents": []
            }

            if cont_idx is not None and 0 <= cont_idx < len(inv_list):
                inv_list[cont_idx].setdefault("contents", []).append({
                    "name": new_obj["name"],
                    "qty": new_obj["qty"],
                    "weight_kg": new_obj["weight_kg"]
                })
                inv_list[cont_idx]["expanded"] = True
            else:
                inv_list.append(new_obj)

        self.dest_options = self._build_destination_options()
        self.combo_dest.configure(values=list(self.dest_options.keys()))
        self.parent_view._refresh_inventory_views()


class ShardOptionsDialog(ctk.CTkToplevel):
    """
    Constructor Progresivo Estilo Shard Tabletop (Niveles 1 a N):
    - Si el personaje es Nivel 1, muestra únicamente las opciones de Nivel 1 (Origen, Especie y Clase Niv 1).
    - Si sube de nivel o se crea en un nivel superior (ej. Nivel 8), genera acumulativamente
      todas las decisiones rellenables de cada nivel desde 1 hasta su nivel actual.
    """
    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.parent_view = parent_view
        self.char_class = self.parent_view.combo_class.get()
        self.species = self.parent_view.combo_species.get()
        self.bg_name = self.parent_view.combo_bg.get()
        self.level = int(self.parent_view.combo_level.get() or 1)

        self.title(f"Opciones de Personaje (Estilo Shard 5.5e) — Niveles 1 a {self.level}")
        self.geometry("680x780")
        self.grab_set()

        self.class_info = CLASSES_55E.get(self.char_class, CLASSES_55E["Bardo"])
        self.bg_info = BACKGROUNDS_55E.get(self.bg_name, BACKGROUNDS_55E["Noble"])

        self.skill_combos = []
        self.inst_combos = []
        self.lang_combos = []
        self.bg_abil_combos = []
        self.skilled_combos = []
        self.base_score_entries = {}
        self.prog_widgets = {}  # Guarda todas las elecciones de Nivel 1 a N

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top_bar = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=0)
        top_bar.grid(row=0, column=0, sticky="ew")

        con_score = int(self.parent_view.score_vars["Constitución"].get() or 10)
        con_mod = Character55eRules.get_modifier(con_score)
        calc_hp = Character55eRules.calculate_max_hp(
            self.char_class, self.level, con_mod, self.bg_info["feat"], self.species
        )

        ctk.CTkLabel(
            top_bar, text=f"Progresión Acumulada — {self.char_class} (Nivel 1 al {self.level})",
            font=("Segoe UI", 16, "bold")
        ).pack(side="left", padx=15, pady=12)

        ctk.CTkLabel(
            top_bar, text=f"{calc_hp} PG Sugeridos", font=("Segoe UI", 15, "bold"), text_color="#34D399"
        ).pack(side="right", padx=15, pady=12)

        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)
        self.scroll.grid_columnconfigure(0, weight=1)

        saved_prog = self.parent_view.builder_state.get("level_progression_choices", {})
        all_skills_pool = ["Ninguna"] + [sk[0] for sk in SKILLS_55E]

        # =====================================================================
        # BLOQUE A: PUNTUACIONES BASE Y ORIGEN (NIVEL 1: ESPECIE + TRASFONDO)
        # =====================================================================
        origin_box = ctk.CTkFrame(self.scroll, fg_color="#1E293B")
        origin_box.pack(fill="x", padx=6, pady=6)

        ctk.CTkLabel(
            origin_box, text="NIVEL 1 — Puntuaciones Base (Antes de Trasfondo y Mejoras)",
            font=("Segoe UI", 14, "bold"), text_color="#FBBF24"
        ).pack(anchor="w", padx=12, pady=(10, 4))

        scores_row = ctk.CTkFrame(origin_box, fg_color="transparent")
        scores_row.pack(fill="x", padx=12, pady=4)
        saved_base = self.parent_view.builder_state.get("base_scores", {})
        for idx, ab in enumerate(ABILITIES):
            col = ctk.CTkFrame(scores_row, fg_color="transparent")
            col.pack(side="left", expand=True, padx=2)
            ctk.CTkLabel(col, text=ab[:3].upper(), font=("Segoe UI", 11, "bold")).pack()
            e_sc = ctk.CTkEntry(col, width=48, justify="center")
            default_val = saved_base.get(ab, int(self.parent_view.score_vars[ab].get() or 10))
            e_sc.insert(0, str(default_val))
            e_sc.pack(pady=2)
            self.base_score_entries[ab] = e_sc

        ctk.CTkButton(
            origin_box, text="Aplicar Conjunto Estándar de la Clase (15, 14, 13, 12, 10, 8)",
            height=24, fg_color="#374151", command=self._apply_standard_array
        ).pack(padx=12, pady=(2, 8), fill="x")

        # Opciones de Especie (Idiomas + Linaje de Especie)
        sp_box = ctk.CTkFrame(self.scroll)
        sp_box.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(
            sp_box, text=f"NIVEL 1 — Opciones de Especie: {self.species}",
            font=("Segoe UI", 14, "bold"), text_color="#60A5FA"
        ).pack(anchor="w", padx=12, pady=(10, 4))

        if self.species in SPECIES_LINEAGES_55E:
            lin_opts = ["Ninguno"] + SPECIES_LINEAGES_55E[self.species]
            saved_lin = self.parent_view.builder_state.get("species_lineage", "Ninguno")
            self.prog_widgets["species_lineage"] = self._create_alert_dropdown(
                sp_box, f"Linaje / Ancestría de {self.species}", lin_opts, saved_lin
            )

        if self.species == "Humano":
            saved_h_sk = self.parent_view.builder_state.get("human_extra_skill", "Ninguna")
            self.prog_widgets["human_extra_skill"] = self._create_alert_dropdown(
                sp_box, "Rasgo Humano Habilidoso (1 Habilidad extra)", all_skills_pool, saved_h_sk
            )

        saved_langs = self.parent_view.builder_state.get("language_choices", ["Común", "Ninguno", "Ninguno"])
        for i in range(2):
            val = saved_langs[i+1] if (i+1) < len(saved_langs) else "Ninguno"
            cb = self._create_alert_dropdown(sp_box, f"Idioma Estándar Adicional #{i+1} (Cap. 2)", ["Ninguno"] + LANGUAGES_55E, val)
            self.lang_combos.append(cb)

        # Opciones de Trasfondo
        bg_box = ctk.CTkFrame(self.scroll)
        bg_box.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(
            bg_box, text=f"NIVEL 1 — Opciones de Trasfondo: {self.bg_name}",
            font=("Segoe UI", 14, "bold"), text_color="#60A5FA"
        ).pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(
            bg_box, text=f"Habilidades fijas: {', '.join(self.bg_info['skills'])} | Dote de Origen: {self.bg_info['feat']}",
            font=("Segoe UI", 11), text_color="#9CA3AF"
        ).pack(anchor="w", padx=12, pady=(0, 6))

        self.allow_all_abil_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            bg_box, text="Permitir selección de cualquier característica",
            variable=self.allow_all_abil_var, command=self._refresh_bg_ability_pools
        ).pack(anchor="w", padx=12, pady=4)

        saved_bg_bonuses = self.parent_view.builder_state.get("bg_bonuses", {})
        allowed_abils = ["Ninguno"] + self.bg_info["abilities"]
        for idx, key in enumerate(["+1_a", "+1_b", "+1_c"]):
            val = saved_bg_bonuses.get(key, "Ninguno")
            cb = self._create_alert_dropdown(bg_box, f"Aumento de Característica de Trasfondo +1 (#{idx+1})", allowed_abils, val)
            self.bg_abil_combos.append(cb)

        if "Habilidoso" in self.bg_info["feat"] or self.species == "Humano":
            ctk.CTkLabel(
                bg_box, text="Dote de Origen: Habilidoso (Skilled) — Elige 3 habilidades",
                font=("Segoe UI", 12, "bold"), text_color="#34D399"
            ).pack(anchor="w", padx=12, pady=(8, 2))
            saved_skilled = self.parent_view.builder_state.get("skilled_feat_choices", [])
            for i in range(3):
                val = saved_skilled[i] if i < len(saved_skilled) else "Ninguna"
                cb = self._create_alert_dropdown(bg_box, f"Elección de Habilidoso #{i+1}", all_skills_pool, val)
                self.skilled_combos.append(cb)

        if "Juego" in self.bg_info.get("tool", ""):
            self.gaming_combo = self._create_alert_dropdown(
                bg_box, "Competencia en Juego (Trasfondo)", ["Ninguno"] + GAMING_SETS,
                self.parent_view.builder_state.get("gaming_set_choice", "Dados")
            )
        else:
            self.gaming_combo = None

        # =====================================================================
        # BLOQUE B: OPCIONES DE CLASE NIVEL 1
        # =====================================================================
        cls_box = ctk.CTkFrame(self.scroll)
        cls_box.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(
            cls_box, text=f"NIVEL 1 — Opciones Iniciales de {self.char_class}",
            font=("Segoe UI", 14, "bold"), text_color="#34D399"
        ).pack(anchor="w", padx=12, pady=(10, 4))

        saved_cls_skills = self.parent_view.builder_state.get("class_skill_choices", [])
        skill_pool = ["Ninguna"] + self.class_info["skill_pool"]
        for i in range(self.class_info["skill_choices_count"]):
            val = saved_cls_skills[i] if i < len(saved_cls_skills) else "Ninguna"
            cb = self._create_alert_dropdown(cls_box, f"Competencia en Habilidad de {self.char_class} #{i+1}", skill_pool, val)
            self.skill_combos.append(cb)

        saved_inst = self.parent_view.builder_state.get("instrument_choices", [])
        for i in range(self.class_info.get("instruments_count", 0)):
            val = saved_inst[i] if i < len(saved_inst) else "Ninguno"
            cb = self._create_alert_dropdown(cls_box, f"Instrumento Musical #{i+1}", ["Ninguno"] + MUSICAL_INSTRUMENTS, val)
            self.inst_combos.append(cb)

        # Rasgos elegibles específicos de Nivel 1 por Clase
        if self.char_class == "Clérigo":
            self.prog_widgets["lvl1_order"] = self._create_alert_dropdown(
                cls_box, "Orden Divina (Clérigo Nivel 1)",
                ["Ninguna", "Protector (Armaduras pesadas y armas marciales)", "Taumaturgo (+1 Truco y +Sab a Religión/Arcano)"],
                saved_prog.get("lvl1_order", "Ninguna")
            )
        elif self.char_class == "Druida":
            self.prog_widgets["lvl1_order"] = self._create_alert_dropdown(
                cls_box, "Orden Primigenia (Druida Nivel 1)",
                ["Ninguna", "Guardián (Armaduras medias y armas marciales)", "Naturalista (+1 Truco y +Sab a Naturaleza/Arcano)"],
                saved_prog.get("lvl1_order", "Ninguna")
            )
        elif self.char_class == "Guerrero":
            self.prog_widgets["lvl1_style"] = self._create_alert_dropdown(
                cls_box, "Estilo de Combate (Guerrero Nivel 1)",
                ["Ninguno"] + FIGHTING_STYLES_55E,
                saved_prog.get("lvl1_style", "Ninguno")
            )
        elif self.char_class == "Pícaro":
            for i in range(2):
                k = f"lvl1_exp_{i+1}"
                self.prog_widgets[k] = self._create_alert_dropdown(
                    cls_box, f"Pericia de Pícaro Nivel 1 (Dobla competencia) #{i+1}",
                    all_skills_pool, saved_prog.get(k, "Ninguna")
                )
        elif self.char_class == "Brujo":
            self.prog_widgets["lvl1_invoc_1"] = self._create_alert_dropdown(
                cls_box, "Invocación Sobrenatural Inicial (Brujo Nivel 1)",
                ["Ninguna"] + ELD_INVOCATIONS_55E, saved_prog.get("lvl1_invoc_1", "Ninguna")
            )

        # =====================================================================
        # BLOQUE C: PROGRESIÓN ACUMULATIVA DESDE NIVEL 2 HASTA EL NIVEL ACTUAL
        # =====================================================================
        asi_levels = Character55eRules.get_asi_levels(self.char_class)

        for lvl in range(2, self.level + 1):
            lvl_card = ctk.CTkFrame(self.scroll, fg_color="#182232")
            lvl_card.pack(fill="x", padx=6, pady=6)

            # Obtener resumen de rasgos automáticos y de conjuros de este nivel
            c_feats = self.class_info.get("features_by_level", {}).get(lvl, [])
            feat_names = ", ".join([f[0] for f in c_feats]) if c_feats else "Progresión de Conjuros y PG"

            ctk.CTkLabel(
                lvl_card, text=f"NIVEL {lvl} — {feat_names}",
                font=("Segoe UI", 14, "bold"), text_color="#FBBF24"
            ).pack(anchor="w", padx=12, pady=(10, 4))

            # Mostrar cuántos trucos, conjuros preparados y espacios tiene en este nivel
            slots_at_lvl = Character55eRules.get_spell_slots_by_level(
                self.char_class, self.parent_view.combo_subclass.get(), lvl
            )
            if slots_at_lvl:
                c_max = Character55eRules.get_cantrips_max(self.char_class, lvl, saved_prog.get("lvl1_order", ""))
                p_max = Character55eRules.get_prepared_spells_max(self.char_class, lvl)
                slots_txt = " | ".join([f"Niv.{k}: {v} esp." for k, v in sorted(slots_at_lvl.items())])
                ctk.CTkLabel(
                    lvl_card,
                    text=f"Magia en Nivel {lvl}: {c_max} Trucos | {p_max} Conjuros Preparados | Espacios: {slots_txt}",
                    font=("Segoe UI", 11), text_color="#A78BFA"
                ).pack(anchor="w", padx=12, pady=(0, 6))

            # --- OPCIONES RELLENABLES DE NIVEL 2 ---
            if lvl == 2:
                if self.char_class == "Bardo":
                    ctk.CTkLabel(
                        lvl_card, text="✔ Aprendiz de mucho activado (+mitad de competencia a habilidades no competentes).",
                        font=("Segoe UI", 11), text_color="#34D399"
                    ).pack(anchor="w", padx=12, pady=2)
                    for i in range(2):
                        k = f"lvl2_exp_{i+1}"
                        self.prog_widgets[k] = self._create_alert_dropdown(
                            lvl_card, f"Pericia de Bardo Nivel 2 (Dobla competencia) #{i+1}",
                            all_skills_pool, saved_prog.get(k, "Ninguna")
                        )
                elif self.char_class in ("Explorador", "Paladín"):
                    self.prog_widgets["lvl2_style"] = self._create_alert_dropdown(
                        lvl_card, f"Estilo de Combate ({self.char_class} Nivel 2)",
                        ["Ninguno"] + FIGHTING_STYLES_55E, saved_prog.get("lvl2_style", "Ninguno")
                    )
                    if self.char_class == "Explorador":
                        self.prog_widgets["lvl2_exp_1"] = self._create_alert_dropdown(
                            lvl_card, "Explorador Hábil: Pericia en 1 Habilidad",
                            all_skills_pool, saved_prog.get("lvl2_exp_1", "Ninguna")
                        )
                elif self.char_class == "Mago":
                    self.prog_widgets["lvl2_exp_1"] = self._create_alert_dropdown(
                        lvl_card, "Erudito (Mago Nivel 2): Pericia en 1 habilidad académica",
                        ["Ninguna", "Conocimiento Arcano", "Historia", "Investigación", "Medicina", "Naturaleza", "Religión"],
                        saved_prog.get("lvl2_exp_1", "Ninguna")
                    )
                elif self.char_class == "Brujo":
                    for i in range(2, 4):
                        k = f"lvl2_invoc_{i}"
                        self.prog_widgets[k] = self._create_alert_dropdown(
                            lvl_card, f"Invocación Sobrenatural Adicional #{i} (Nivel 2)",
                            ["Ninguna"] + ELD_INVOCATIONS_55E, saved_prog.get(k, "Ninguna")
                        )

            # --- OPCIONES RELLENABLES DE NIVEL 3 (SUBCLASE Y RASGOS DE SUBCLASE) ---
            if lvl == 3:
                subs = ["Ninguna"] + self.class_info.get("subclasses", [])
                curr_sub = self.parent_view.combo_subclass.get()
                if curr_sub == "Se elige en Nivel 3":
                    curr_sub = saved_prog.get("lvl3_subclass", "Ninguna")
                self.prog_widgets["lvl3_subclass"] = self._create_alert_dropdown(
                    lvl_card, f"Elección de Subclase de {self.char_class} (Nivel 3)", subs, curr_sub
                )

                if self.char_class == "Bardo" and "Conocimiento" in curr_sub:
                    for i in range(3):
                        k = f"lvl3_lore_sk_{i+1}"
                        self.prog_widgets[k] = self._create_alert_dropdown(
                            lvl_card, f"Colegio del Conocimiento: Habilidad Adicional #{i+1}",
                            all_skills_pool, saved_prog.get(k, "Ninguna")
                        )
                elif self.char_class == "Bárbaro":
                    self.prog_widgets["lvl3_primal_sk"] = self._create_alert_dropdown(
                        lvl_card, "Conocimiento Primigenio: +1 Habilidad de Bárbaro",
                        skill_pool, saved_prog.get("lvl3_primal_sk", "Ninguna")
                    )

            # --- MEJORAS DE CARACTERÍSTICA / DOTES GENERALES (Niveles 4, 8, 12, 16, etc.) ---
            if lvl in asi_levels:
                k_feat = f"lvl{lvl}_feat"
                k_ab1 = f"lvl{lvl}_ab1"
                k_ab2 = f"lvl{lvl}_ab2"
                self.prog_widgets[k_feat] = self._create_alert_dropdown(
                    lvl_card, f"Dote General o Mejora de Característica (Nivel {lvl})",
                    ["Ninguna"] + GENERAL_FEATS_55E,
                    saved_prog.get(k_feat, "Mejora de característica (+2 a una o +1 a dos)")
                )
                self.prog_widgets[k_ab1] = self._create_alert_dropdown(
                    lvl_card, f"Aumento +1 Característica A (Nivel {lvl})",
                    ["Ninguno"] + ABILITIES, saved_prog.get(k_ab1, "Ninguno")
                )
                self.prog_widgets[k_ab2] = self._create_alert_dropdown(
                    lvl_card, f"Aumento +1 Característica B (Nivel {lvl} — Elige la misma para +2, o ninguna si tu Dote solo da +1)",
                    ["Ninguno"] + ABILITIES, saved_prog.get(k_ab2, "Ninguno")
                )

            # --- OPCIONES DE NIVELES INTERMEDIOS Y ALTOS (Pericia Niv 6/9, Invocaciones, Don Épico) ---
            if lvl == 5 and self.char_class == "Brujo":
                for i in range(4, 6):
                    k = f"lvl5_invoc_{i}"
                    self.prog_widgets[k] = self._create_alert_dropdown(
                        lvl_card, f"Invocación Sobrenatural #{i} (Nivel 5)",
                        ["Ninguna"] + ELD_INVOCATIONS_55E, saved_prog.get(k, "Ninguna")
                    )

            if lvl == 6 and self.char_class == "Pícaro":
                for i in range(2):
                    k = f"lvl6_exp_{i+1}"
                    self.prog_widgets[k] = self._create_alert_dropdown(
                        lvl_card, f"Pericia Adicional de Pícaro Nivel 6 #{i+1}",
                        all_skills_pool, saved_prog.get(k, "Ninguna")
                    )

            if lvl == 7 and self.char_class == "Clérigo":
                self.prog_widgets["lvl7_blessed"] = self._create_alert_dropdown(
                    lvl_card, "Golpes Benditos (Clérigo Nivel 7)",
                    ["Ninguno", "Golpe divino (+1d8 radiante/necrótico con armas)", "Lanzamiento potente (+Sab al daño de trucos)"],
                    saved_prog.get("lvl7_blessed", "Ninguno")
                )

            if lvl == 7 and self.char_class == "Druida":
                self.prog_widgets["lvl7_elem_fury"] = self._create_alert_dropdown(
                    lvl_card, "Furia Elemental (Druida Nivel 7)",
                    ["Ninguna", "Golpe primordial (+1d8 elemental en ataques)", "Lanzamiento potente (+Sab al daño de trucos)"],
                    saved_prog.get("lvl7_elem_fury", "Ninguna")
                )

            if lvl == 9 and self.char_class in ("Bardo", "Explorador"):
                for i in range(2):
                    k = f"lvl9_exp_{i+1}"
                    self.prog_widgets[k] = self._create_alert_dropdown(
                        lvl_card, f"Pericia Adicional de {self.char_class} Nivel 9 #{i+1}",
                        all_skills_pool, saved_prog.get(k, "Ninguna")
                    )

            if lvl == 19:
                self.prog_widgets["lvl19_boon"] = self._create_alert_dropdown(
                    lvl_card, "Don Épico (Nivel 19)",
                    ["Ninguno"] + EPIC_BOONS_55E, saved_prog.get("lvl19_boon", "Ninguno")
                )

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", padx=15, pady=10)

        ctk.CTkButton(footer, text="Cerrar", width=100, fg_color="#374151", command=self.destroy).pack(side="right", padx=6)
        ctk.CTkButton(
            footer, text="✔ Aplicar Toda la Progresión a la Hoja", width=240, fg_color="#2563EB",
            command=self._apply_changes
        ).pack(side="right", padx=6)

    def _apply_standard_array(self):
        # Tabla "Conjunto estándar por clase" de la página 38 del Manual del Jugador 2024
        std_by_class = {
            "Bárbaro":   {"Fuerza": 15, "Destreza": 13, "Constitución": 14, "Inteligencia": 10, "Sabiduría": 12, "Carisma": 8},
            "Bardo":     {"Fuerza": 8,  "Destreza": 14, "Constitución": 12, "Inteligencia": 13, "Sabiduría": 10, "Carisma": 15},
            "Brujo":     {"Fuerza": 8,  "Destreza": 14, "Constitución": 13, "Inteligencia": 12, "Sabiduría": 10, "Carisma": 15},
            "Clérigo":   {"Fuerza": 14, "Destreza": 8,  "Constitución": 13, "Inteligencia": 10, "Sabiduría": 15, "Carisma": 12},
            "Druida":    {"Fuerza": 8,  "Destreza": 12, "Constitución": 14, "Inteligencia": 13, "Sabiduría": 15, "Carisma": 10},
            "Explorador":{"Fuerza": 12, "Destreza": 15, "Constitución": 13, "Inteligencia": 8,  "Sabiduría": 14, "Carisma": 10},
            "Guerrero":  {"Fuerza": 15, "Destreza": 14, "Constitución": 13, "Inteligencia": 8,  "Sabiduría": 10, "Carisma": 12},
            "Hechicero": {"Fuerza": 10, "Destreza": 13, "Constitución": 14, "Inteligencia": 8,  "Sabiduría": 12, "Carisma": 15},
            "Mago":      {"Fuerza": 8,  "Destreza": 12, "Constitución": 13, "Inteligencia": 15, "Sabiduría": 14, "Carisma": 10},
            "Monje":     {"Fuerza": 12, "Destreza": 15, "Constitución": 13, "Inteligencia": 10, "Sabiduría": 14, "Carisma": 8},
            "Paladín":   {"Fuerza": 15, "Destreza": 10, "Constitución": 13, "Inteligencia": 8,  "Sabiduría": 12, "Carisma": 14},
            "Pícaro":    {"Fuerza": 12, "Destreza": 15, "Constitución": 13, "Inteligencia": 14, "Sabiduría": 10, "Carisma": 8},
        }
        arr = std_by_class.get(self.char_class, std_by_class["Bardo"])
        for ab, val in arr.items():
            self.base_score_entries[ab].delete(0, "end")
            self.base_score_entries[ab].insert(0, str(val))

    def _create_alert_dropdown(self, parent, subtitle: str, values: list, current_val: str):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=3)

        is_empty = current_val in ("Ninguno", "Ninguna", "")
        lbl_icon = ctk.CTkLabel(
            row, text="!" if is_empty else "OK",
            text_color="#EF4444" if is_empty else "#10B981",
            font=("Segoe UI", 13, "bold"), width=32
        )
        lbl_icon.pack(side="left", padx=(0, 8))

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(side="left", fill="x", expand=True)

        def on_change(choice):
            empty = choice in ("Ninguno", "Ninguna", "")
            lbl_icon.configure(text="!" if empty else "OK", text_color="#EF4444" if empty else "#10B981")

        combo = ctk.CTkComboBox(inner, values=values, command=on_change)
        combo.set(current_val if current_val in values else values[0])
        combo.pack(fill="x")

        ctk.CTkLabel(inner, text=subtitle, font=("Segoe UI", 11), text_color="#9CA3AF").pack(anchor="w")
        return combo

    def _refresh_bg_ability_pools(self):
        pool = ["Ninguno"] + (ABILITIES if self.allow_all_abil_var.get() else self.bg_info["abilities"])
        for cb in self.bg_abil_combos:
            cb.configure(values=pool)

    def _apply_changes(self):
        # 1. Leer puntuaciones base
        base_scores = {}
        for ab, entry_w in self.base_score_entries.items():
            raw = entry_w.get().strip()
            base_scores[ab] = int(raw) if raw.isdigit() else 10
        self.parent_view.builder_state["base_scores"] = base_scores

        # 2. Guardar progresión nivel por nivel
        prog_data = {k: cb.get() for k, cb in self.prog_widgets.items()}
        self.parent_view.builder_state["level_progression_choices"] = prog_data

        if "species_lineage" in prog_data:
            self.parent_view.builder_state["species_lineage"] = prog_data["species_lineage"]
        if "human_extra_skill" in prog_data:
            self.parent_view.builder_state["human_extra_skill"] = prog_data["human_extra_skill"]

        # Si eligió subclase en Nivel 3, actualizar el combo principal
        if self.level >= 3 and prog_data.get("lvl3_subclass") and prog_data["lvl3_subclass"] != "Ninguna":
            self.parent_view.combo_subclass.set(prog_data["lvl3_subclass"])

        # 3. Calcular Puntuaciones Finales = Base + Trasfondo (+1/+1/+1) + Mejoras de Nivel (4, 8, 12, 16...)
        final_scores = dict(base_scores)
        bg_bonuses = {
            "+1_a": self.bg_abil_combos[0].get(),
            "+1_b": self.bg_abil_combos[1].get(),
            "+1_c": self.bg_abil_combos[2].get(),
        }
        self.parent_view.builder_state["bg_bonuses"] = bg_bonuses
        for _, ab_chosen in bg_bonuses.items():
            if ab_chosen in final_scores:
                final_scores[ab_chosen] = min(20, final_scores[ab_chosen] + 1)

        for lvl in Character55eRules.get_asi_levels(self.char_class):
            if lvl <= self.level:
                for key_ab in (f"lvl{lvl}_ab1", f"lvl{lvl}_ab2"):
                    ab_up = prog_data.get(key_ab, "Ninguno")
                    if ab_up in final_scores:
                        final_scores[ab_up] = min(20, final_scores[ab_up] + 1)

        for ab, val in final_scores.items():
            self.parent_view.score_vars[ab].set(str(val))

        # 4. Recopilar Habilidades Competentes (Clase + Trasfondo + Habilidoso + Especie + Subclase)
        cls_skills = [cb.get() for cb in self.skill_combos if cb.get() not in ("Ninguna", "")]
        skilled_skills = [cb.get() for cb in self.skilled_combos if cb.get() not in ("Ninguna", "")]
        bg_fixed_skills = self.bg_info["skills"]
        extra_lvl_skills = []
        for k, v in prog_data.items():
            if ("_sk" in k or "human_extra_skill" in k) and v not in ("Ninguna", "Ninguno", ""):
                extra_lvl_skills.append(v)

        # Recopilar Habilidades con Pericia (Expertise) desbloqueadas hasta este nivel
        expertise_skills = []
        for k, v in prog_data.items():
            if "_exp_" in k and v not in ("Ninguna", "Ninguno", ""):
                expertise_skills.append(v)
        self.parent_view.builder_state["expertise_skills"] = expertise_skills

        self.parent_view.builder_state["class_skill_choices"] = cls_skills
        self.parent_view.builder_state["skilled_feat_choices"] = skilled_skills
        self.parent_view.builder_state["instrument_choices"] = [cb.get() for cb in self.inst_combos if cb.get() != "Ninguno"]
        self.parent_view.builder_state["language_choices"] = ["Común"] + [cb.get() for cb in self.lang_combos if cb.get() != "Ninguno"]

        if self.gaming_combo:
            self.parent_view.builder_state["gaming_set_choice"] = self.gaming_combo.get()

        for ab in ABILITIES:
            self.parent_view.save_prof_vars[ab].set(ab in self.class_info["saves"])

        combined_skills = set(cls_skills + skilled_skills + bg_fixed_skills + extra_lvl_skills + expertise_skills)
        for sk_name, _ in SKILLS_55E:
            self.parent_view.skill_prof_vars[sk_name].set(sk_name in combined_skills)

        # 5. Actualizar Velocidad, Dote de Origen y Puntos de Golpe Máximos según el Nivel y Constitución final
        sp_data = SPECIES_55E.get(self.species, {"speed": "9 m"})
        speed_str = "10,5 m" if "Elfo del Bosque" in prog_data.get("species_lineage", "") else sp_data["speed"]
        self.parent_view._set_entry(self.parent_view.entry_speed, speed_str)
        self.parent_view._set_entry(self.parent_view.entry_origin_feat, self.bg_info["feat"])

        con_mod = Character55eRules.get_modifier(final_scores["Constitución"])
        max_hp = Character55eRules.calculate_max_hp(self.char_class, self.level, con_mod, self.bg_info["feat"], self.species)
        self.parent_view._set_entry(self.parent_view.entry_hp_max, str(max_hp))
        self.parent_view._set_entry(self.parent_view.entry_hp_curr, str(max_hp))

        self.parent_view._update_features_display()
        self.parent_view._recalculate_all()
        self.destroy()


class ShardSpellPickerDialog(ctk.CTkToplevel):
    """Modal interactivo estilo 'Pick Spells' con Espacios por Nivel y Conjuros Siempre Preparados de Subclase."""
    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.parent_view = parent_view
        self.title("Selector de Conjuros 5.5e (Pick Spells)")
        self.geometry("720x760")
        self.grab_set()

        self.char_class = self.parent_view.combo_class.get()
        self.subclass = self.parent_view.combo_subclass.get()
        self.level = int(self.parent_view.combo_level.get() or 1)

        order_choice = self.parent_view.builder_state.get("level_progression_choices", {}).get("lvl1_order", "")
        self.max_cantrips = Character55eRules.get_cantrips_max(self.char_class, self.level, order_choice)
        self.max_spells = Character55eRules.get_prepared_spells_max(self.char_class, self.level)
        self.max_spell_lvl = Character55eRules.get_max_spell_level(self.char_class, self.level)

        self.slots_dict = Character55eRules.get_spell_slots_by_level(self.char_class, self.subclass, self.level)
        self.always_prepared = Character55eRules.get_always_prepared_spells(self.char_class, self.subclass, self.level)

        self.selected_cantrips = set(self.parent_view.builder_state.get("selected_cantrips", []))
        self.selected_spells = set(self.parent_view.builder_state.get("selected_spells", []))

        self._build_ui()
        self._render_spell_list()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            header, text=f"Elegir Conjuros — {self.char_class} Nivel {self.level} ({self.subclass})",
            font=("Segoe UI", 16, "bold")
        ).pack(side="left", padx=15, pady=12)

        self.only_class_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            header, text="Solo opciones de mi clase", variable=self.only_class_var, command=self._render_spell_list
        ).pack(side="right", padx=15)

        filter_bar = ctk.CTkFrame(self)
        filter_bar.grid(row=1, column=0, sticky="ew", padx=12, pady=8)
        filter_bar.grid_columnconfigure(0, weight=1)

        self.entry_filter = ctk.CTkEntry(filter_bar, placeholder_text="Buscar conjuro por nombre o escuela...")
        self.entry_filter.grid(row=0, column=0, padx=8, pady=6, sticky="ew")
        self.entry_filter.bind("<KeyRelease>", lambda e: self._render_spell_list())

        self.lbl_counters = ctk.CTkLabel(
            filter_bar, text="", font=("Segoe UI", 13, "bold"), text_color="#FBBF24"
        )
        self.lbl_counters.grid(row=1, column=0, padx=8, pady=(0, 2), sticky="w")

        slots_str = "  |  ".join([f"Nivel {k}: {v} espacios" for k, v in sorted(self.slots_dict.items())]) or "Sin espacios"
        ctk.CTkLabel(
            filter_bar, text=f"Espacios de Conjuro por Nivel:  {slots_str}",
            font=("Segoe UI", 12, "bold"), text_color="#60A5FA"
        ).grid(row=2, column=0, padx=8, pady=(0, 4), sticky="w")

        if self.always_prepared:
            ctk.CTkLabel(
                filter_bar,
                text=f"Siempre Preparados (Gratis por Clase/Subclase): {', '.join(self.always_prepared)}",
                font=("Segoe UI", 11), text_color="#34D399", wraplength=660, justify="left"
            ).grid(row=3, column=0, padx=8, pady=(0, 6), sticky="w")

        self.spells_scroll = ctk.CTkScrollableFrame(self)
        self.spells_scroll.grid(row=2, column=0, sticky="nsew", padx=12, pady=4)

        self.pdf_preview_box = ctk.CTkTextbox(self, height=110)
        self.pdf_preview_box.grid(row=3, column=0, sticky="ew", padx=12, pady=6)
        self.pdf_preview_box.insert("1.0", "Haz clic en 'Ver PDF' junto a cualquier conjuro para buscar su descripción directamente en tus manuales PDF indexados.")

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=4, column=0, sticky="ew", padx=12, pady=10)
        ctk.CTkButton(footer, text="Cancelar", width=100, fg_color="#374151", command=self.destroy).pack(side="right", padx=6)
        ctk.CTkButton(footer, text="Guardar Conjuros", width=160, fg_color="#2563EB", command=self._save_spells).pack(side="right", padx=6)

        self._update_counters_label()

    def _update_counters_label(self):
        c_cnt = len(self.selected_cantrips)
        s_cnt = len(self.selected_spells)
        self.lbl_counters.configure(
            text=f"Trucos (Cantrips): {c_cnt} / {self.max_cantrips}   |   Conjuros Preparados (Niv. 1 a {self.max_spell_lvl}): {s_cnt} / {self.max_spells}"
        )

    def _render_spell_list(self):
        for w in self.spells_scroll.winfo_children():
            w.destroy()

        query = self.entry_filter.get().strip().lower()
        only_cls = self.only_class_var.get()
        secretos_magicos = (self.char_class == "Bardo" and self.level >= 10)

        max_lvl = max(1, self.max_spell_lvl)
        for lvl in range(0, max_lvl + 1):
            matching = []
            for sp in Character55eRules.get_combined_spells_catalog(self.parent_view.db):
                if sp["level"] != lvl:
                    continue
                if only_cls:
                    allowed_classes = {self.char_class}
                    if secretos_magicos:
                        allowed_classes.update(["Clérigo", "Druida", "Mago"])
                    if not (allowed_classes & set(sp["classes"])):
                        continue
                if query and query not in sp["name"].lower() and query not in sp["school"].lower():
                    continue
                matching.append(sp)

            if not matching:
                continue

            slot_info = ""
            if lvl > 0 and lvl in self.slots_dict:
                slot_info = f" — [{self.slots_dict[lvl]} Espacios de Conjuro]"

            banner = ctk.CTkFrame(self.spells_scroll, fg_color="#374151", height=32)
            banner.pack(fill="x", padx=4, pady=(8, 2))
            title_txt = f"Trucos / Cantrips ({len(matching)})" if lvl == 0 else f"Conjuros de Nivel {lvl} ({len(matching)}){slot_info}"
            ctk.CTkLabel(banner, text=title_txt, font=("Segoe UI", 13, "bold")).pack(side="left", padx=10, pady=4)

            for sp in matching:
                row = ctk.CTkFrame(self.spells_scroll, fg_color="#1F2937")
                row.pack(fill="x", padx=4, pady=2)

                is_checked = (sp["name"] in self.selected_cantrips) if lvl == 0 else (sp["name"] in self.selected_spells)
                var_chk = ctk.BooleanVar(value=is_checked)

                def make_toggle(spell_obj=sp, v=var_chk):
                    return lambda: self._toggle_spell(spell_obj, v)

                chk = ctk.CTkCheckBox(
                    row, text=f"{sp['name']}  ({sp['school']})",
                    variable=var_chk, command=make_toggle(), font=("Segoe UI", 12)
                )
                chk.pack(side="left", padx=10, pady=6)

                btn_pdf = ctk.CTkButton(
                    row, text="Ver PDF", width=70, height=26, fg_color="#2B4C7E",
                    command=lambda sname=sp["name"]: self._lookup_spell_in_pdf(sname)
                )
                btn_pdf.pack(side="right", padx=8, pady=4)

    def _toggle_spell(self, spell_obj: dict, var_chk: ctk.BooleanVar):
        name = spell_obj["name"]
        lvl = spell_obj["level"]
        if lvl == 0:
            if var_chk.get():
                if len(self.selected_cantrips) >= self.max_cantrips:
                    var_chk.set(False)
                    messagebox.showwarning("Límite de Trucos", f"En nivel {self.level} puedes tener máximo {self.max_cantrips} trucos.")
                    return
                self.selected_cantrips.add(name)
            else:
                self.selected_cantrips.discard(name)
        else:
            if var_chk.get():
                if len(self.selected_spells) >= self.max_spells:
                    var_chk.set(False)
                    messagebox.showwarning("Límite de Conjuros", f"Un {self.char_class} de nivel {self.level} puede preparar {self.max_spells} conjuros (sin contar los siempre preparados de subclase).")
                    return
                self.selected_spells.add(name)
            else:
                self.selected_spells.discard(name)

        self._update_counters_label()

    def _lookup_spell_in_pdf(self, full_name: str):
        clean_term = full_name.split("(")[0].strip()
        hits = self.parent_view.db.search_manuals(clean_term, limit=3)

        self.pdf_preview_box.delete("1.0", "end")
        if not hits:
            self.pdf_preview_box.insert("1.0", f"No se encontró '{clean_term}' en los PDFs indexados.")
            return

        lines = [f"Resultados en tu PDF para '{clean_term}':"]
        for h in hits:
            snippet = h["match_snippet"].replace("\n", " ")
            lines.append(f"• [{h['manual_title']} - Pág. {h['page_number']}]: {snippet}")
        self.pdf_preview_box.insert("1.0", "\n".join(lines))

    def _save_spells(self):
        self.parent_view.builder_state["selected_cantrips"] = sorted(list(self.selected_cantrips))
        self.parent_view.builder_state["selected_spells"] = sorted(list(self.selected_spells))
        self.parent_view._update_features_display()
        self.parent_view._recalculate_all()
        self.destroy()


class ShortRestManualDialog(ctk.CTkToplevel):
    """Modal de Descanso Corto (Sin tiradas digitales: el jugador introduce lo que salió en sus dados físicos)."""
    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.parent_view = parent_view
        self.title("Descanso Corto (Dados Físicos)")
        self.geometry("460x360")
        self.grab_set()

        self.char_class = self.parent_view.combo_class.get()
        self.hd_faces = CLASSES_55E.get(self.char_class, {}).get("hit_die", 8)
        self.hd_avail = int(self.parent_view.builder_state.get("hit_dice_current", 1))
        self.level = int(self.parent_view.combo_level.get() or 1)

        con_score = int(self.parent_view.score_vars["Constitución"].get() or 10)
        self.con_mod = Character55eRules.get_modifier(con_score)

        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(
            self, text=f"Descanso Corto — {self.char_class}", font=("Segoe UI", 17, "bold")
        ).pack(padx=15, pady=(15, 6), anchor="w")

        ctk.CTkLabel(
            self,
            text=f"Dados de Golpe disponibles: {self.hd_avail} / {self.level} (d{self.hd_faces})\n"
                 f"Modificador de Constitución: {Character55eRules.format_mod(self.con_mod)} por cada dado gastado.",
            justify="left", font=("Segoe UI", 12), text_color="#9CA3AF"
        ).pack(padx=15, pady=4, anchor="w")

        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=15, pady=10)
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form, text="1. ¿Cuántos Dados de Golpe gastaste?", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.entry_dice_spent = ctk.CTkEntry(form, width=80)
        self.entry_dice_spent.insert(0, "1" if self.hd_avail > 0 else "0")
        self.entry_dice_spent.grid(row=0, column=1, padx=10, pady=8, sticky="e")

        ctk.CTkLabel(form, text=f"2. Suma total de tus d{self.hd_faces} físicos (sin CON):", font=("Segoe UI", 12, "bold")).grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.entry_physical_roll = ctk.CTkEntry(form, width=80, placeholder_text="Ej. 6")
        self.entry_physical_roll.grid(row=1, column=1, padx=10, pady=8, sticky="e")

        ctk.CTkLabel(
            self, text="*El programa sumará automáticamente tu Mod. CON por cada dado gastado y restaurará tus PG actuales sin superar el máximo.",
            wraplength=420, justify="left", font=("Segoe UI", 11), text_color="#60A5FA"
        ).pack(padx=15, pady=4, anchor="w")

        btn_bar = ctk.CTkFrame(self, fg_color="transparent")
        btn_bar.pack(fill="x", padx=15, pady=12)

        ctk.CTkButton(btn_bar, text="Cancelar", width=90, fg_color="#374151", command=self.destroy).pack(side="right", padx=5)
        ctk.CTkButton(btn_bar, text="Aplicar Curación y Descanso", fg_color="#059669", command=self._apply_short_rest).pack(side="right", padx=5)

    def _apply_short_rest(self):
        try:
            spent = int(self.entry_dice_spent.get().strip() or 0)
            roll_sum = int(self.entry_physical_roll.get().strip() or 0)
        except ValueError:
            messagebox.showwarning("Dato inválido", "Introduce números enteros para los dados gastados y la suma de tu tirada física.")
            return

        if spent < 0 or spent > self.hd_avail:
            messagebox.showwarning("Dados insuficientes", f"Solo tienes {self.hd_avail} Dados de Golpe disponibles.")
            return

        total_healed = 0
        if spent > 0:
            total_healed = max(spent, roll_sum + (spent * self.con_mod))

        hp_max = int(self.parent_view.entry_hp_max.get().strip() or 10)
        hp_curr = int(self.parent_view.entry_hp_curr.get().strip() or 10)
        new_hp = min(hp_max, hp_curr + total_healed)

        self.parent_view.builder_state["hit_dice_current"] = self.hd_avail - spent
        self.parent_view._set_entry(self.parent_view.entry_hp_curr, str(new_hp))
        self.parent_view._recalculate_all()

        messagebox.showinfo(
            "Descanso Corto Completado",
            f"• Dados de Golpe gastados: {spent}d{self.hd_faces}\n"
            f"• Tirada física ({roll_sum}) + Bono CON ({spent * self.con_mod}) = +{total_healed} PG\n"
            f"• PG Actuales: {hp_curr} → {new_hp} / {hp_max}"
        )
        self.destroy()


class LevelUpManualDialog(ctk.CTkToplevel):
    """Modal para Subir de Nivel introduciendo el resultado del dado físico."""
    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.parent_view = parent_view
        self.title("Subir de Nivel (Reglas 5.5e)")
        self.geometry("460x350")
        self.grab_set()

        self.curr_level = int(self.parent_view.combo_level.get() or 1)
        self.next_level = min(20, self.curr_level + 1)
        self.char_class = self.parent_view.combo_class.get()
        self.species = self.parent_view.combo_species.get()
        self.origin_feat = self.parent_view.entry_origin_feat.get()

        self.hd_faces = CLASSES_55E.get(self.char_class, {}).get("hit_die", 8)
        self.fixed_avg = (self.hd_faces // 2) + 1

        con_score = int(self.parent_view.score_vars["Constitución"].get() or 10)
        self.con_mod = Character55eRules.get_modifier(con_score)

        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(
            self, text=f"Subir a Nivel {self.next_level} ({self.char_class})",
            font=("Segoe UI", 17, "bold"), text_color="#FBBF24"
        ).pack(padx=15, pady=(15, 6), anchor="w")

        extra_bonuses = []
        if self.species == "Enano":
            extra_bonuses.append("+1 PG (Dureza Enana)")
        if "Duro" in self.origin_feat or "Tough" in self.origin_feat:
            extra_bonuses.append("+2 PG (Dote Duro)")
        extra_str = f" + {', '.join(extra_bonuses)}" if extra_bonuses else ""

        ctk.CTkLabel(
            self,
            text=f"Tira 1d{self.hd_faces} físico en la mesa (o usa el valor fijo de {self.fixed_avg}).\n"
                 f"El programa sumará automáticamente tu Mod. CON ({Character55eRules.format_mod(self.con_mod)}){extra_str}.",
            justify="left", font=("Segoe UI", 12), text_color="#9CA3AF"
        ).pack(padx=15, pady=6, anchor="w")

        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=15, pady=10)
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form, text=f"Resultado en tu d{self.hd_faces} físico (1 a {self.hd_faces}):", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        self.entry_die = ctk.CTkEntry(form, width=80)
        self.entry_die.insert(0, str(self.fixed_avg))
        self.entry_die.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        btn_fixed = ctk.CTkButton(
            form, text=f"Usar Promedio Fijo ({self.fixed_avg})", height=26, fg_color="#374151",
            command=lambda: (self.entry_die.delete(0, "end"), self.entry_die.insert(0, str(self.fixed_avg)))
        )
        btn_fixed.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        btn_bar = ctk.CTkFrame(self, fg_color="transparent")
        btn_bar.pack(fill="x", padx=15, pady=10)
        ctk.CTkButton(btn_bar, text="Cancelar", width=90, fg_color="#374151", command=self.destroy).pack(side="right", padx=5)
        ctk.CTkButton(btn_bar, text=f"Confirmar Nivel {self.next_level}", fg_color="#D97706", command=self._confirm_level_up).pack(side="right", padx=5)

    def _confirm_level_up(self):
        try:
            die_val = int(self.entry_die.get().strip() or self.fixed_avg)
        except ValueError:
            messagebox.showwarning("Error", "Introduce el número que salió en tu dado físico.")
            return

        hp_gain = max(1, die_val + self.con_mod)
        if self.species == "Enano":
            hp_gain += 1
        if "Duro" in self.origin_feat or "Tough" in self.origin_feat:
            hp_gain += 2

        old_max = int(self.parent_view.entry_hp_max.get().strip() or 10)
        old_curr = int(self.parent_view.entry_hp_curr.get().strip() or 10)

        self.parent_view.combo_level.set(str(self.next_level))
        self.parent_view._set_entry(self.parent_view.entry_hp_max, str(old_max + hp_gain))
        self.parent_view._set_entry(self.parent_view.entry_hp_curr, str(old_curr + hp_gain))

        curr_hd = int(self.parent_view.builder_state.get("hit_dice_current", self.curr_level))
        self.parent_view.builder_state["hit_dice_current"] = min(self.next_level, curr_hd + 1)

        min_xp_needed = XP_THRESHOLDS_55E.get(self.next_level, 0)
        if int(self.parent_view.builder_state.get("xp_current", 0)) < min_xp_needed:
            self.parent_view.builder_state["xp_current"] = min_xp_needed

        self.parent_view._on_class_change(self.char_class)
        messagebox.showinfo(
            "¡Nivel Subido!",
            f"¡Has subido a Nivel {self.next_level}!\n"
            f"• PG Máximos aumentados en +{hp_gain} ({old_max} → {old_max + hp_gain})."
        )
        self.destroy()


class CharacterSheetView(ctk.CTkFrame):
    def __init__(self, master, db: DatabaseManager):
        super().__init__(master, fg_color="transparent")
        self.db = db
        self.current_char_id = None
        self.builder_state = Character55eRules.default_stats_payload()

        self.score_vars = {}
        self.mod_labels = {}
        self.save_prof_vars = {}
        self.save_labels = {}
        self.skill_prof_vars = {}
        self.skill_labels = {}
        self.weapon_widgets = []

        self._build_layout()
        self._refresh_character_list()
        self._load_default_blank()

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=235)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=5)
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(sidebar, text="Héroes 5.5e", font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, padx=12, pady=(12, 6), sticky="w"
        )

        btn_new = ctk.CTkButton(
            sidebar, text="+ Nuevo Personaje", fg_color="#2E7D32", hover_color="#1B5E20",
            command=self._load_default_blank
        )
        btn_new.grid(row=1, column=0, padx=12, pady=4, sticky="ew")

        io_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        io_frame.grid(row=2, column=0, padx=12, pady=4, sticky="ew")
        io_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(io_frame, text="Importar JSON", width=95, fg_color="#3B3B3B", command=self._import_json).grid(row=0, column=0, padx=(0, 3), sticky="ew")
        ctk.CTkButton(io_frame, text="Exportar JSON", width=95, fg_color="#3B3B3B", command=self._export_json).grid(row=0, column=1, padx=(3, 0), sticky="ew")

        self.char_list_scroll = ctk.CTkScrollableFrame(sidebar, label_text="Personajes Guardados")
        self.char_list_scroll.grid(row=3, column=0, padx=10, pady=8, sticky="nsew")

        self.sheet_scroll = ctk.CTkScrollableFrame(self)
        self.sheet_scroll.grid(row=0, column=1, sticky="nsew", pady=5)
        self.sheet_scroll.grid_columnconfigure((0, 1, 2), weight=1)

        self._build_header_section()
        self._build_abilities_and_saves_section()
        self._build_combat_and_mastery_section()
        self._build_skills_section()
        self._build_bottom_tabs_section()

    def _build_header_section(self):
        header = ctk.CTkFrame(self.sheet_scroll)
        header.grid(row=0, column=0, columnspan=3, sticky="ew", padx=6, pady=6)
        header.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.entry_name = self._labeled_entry(header, "Nombre del Personaje", 0, 0, "Ej. Nistor")
        self.entry_player = self._labeled_entry(header, "Jugador", 0, 1, "Víctor")

        ctk.CTkLabel(header, text="Especie (5.5e)", font=("Segoe UI", 11, "bold")).grid(row=0, column=2, padx=8, pady=(6, 0), sticky="w")
        self.combo_species = ctk.CTkComboBox(header, values=list(SPECIES_55E.keys()), command=self._on_species_change)
        self.combo_species.grid(row=1, column=2, padx=8, pady=(0, 6), sticky="ew")

        ctk.CTkLabel(header, text="Trasfondo (2024)", font=("Segoe UI", 11, "bold")).grid(row=0, column=3, padx=8, pady=(6, 0), sticky="w")
        self.combo_bg = ctk.CTkComboBox(header, values=list(BACKGROUNDS_55E.keys()), command=self._on_background_change)
        self.combo_bg.grid(row=1, column=3, padx=8, pady=(0, 6), sticky="ew")

        ctk.CTkLabel(header, text="Clase", font=("Segoe UI", 11, "bold")).grid(row=2, column=0, padx=8, pady=(6, 0), sticky="w")
        self.combo_class = ctk.CTkComboBox(header, values=list(CLASSES_55E.keys()), command=self._on_class_change)
        self.combo_class.grid(row=3, column=0, padx=8, pady=(0, 8), sticky="ew")

        ctk.CTkLabel(header, text="Subclase (Niv. 3+)", font=("Segoe UI", 11, "bold")).grid(row=2, column=1, padx=8, pady=(6, 0), sticky="w")
        self.combo_subclass = ctk.CTkComboBox(
            header, values=["Sin Subclase (Niv. 1-2)"],
            command=lambda _: (self._update_features_display(), self._recalculate_all())
        )
        self.combo_subclass.grid(row=3, column=1, padx=8, pady=(0, 8), sticky="ew")

        ctk.CTkLabel(header, text="Nivel (1-20)", font=("Segoe UI", 11, "bold")).grid(row=2, column=2, padx=8, pady=(6, 0), sticky="w")
        self.combo_level = ctk.CTkComboBox(header, values=[str(i) for i in range(1, 21)], command=lambda _: self._on_class_change(self.combo_class.get()))
        self.combo_level.grid(row=3, column=2, padx=8, pady=(0, 8), sticky="ew")

        self.entry_origin_feat = self._labeled_entry(header, "Dote de Origen (Origin Feat)", 2, 3, "Habilidoso (Skilled)")

        # Barra de XP y Descansos
        xp_rest_bar = ctk.CTkFrame(header, fg_color="#111827")
        xp_rest_bar.grid(row=4, column=0, columnspan=4, sticky="ew", padx=8, pady=(4, 2))

        self.lbl_xp_info = ctk.CTkLabel(xp_rest_bar, text="XP: 0 / 300", font=("Segoe UI", 12, "bold"), text_color="#FBBF24")
        self.lbl_xp_info.pack(side="left", padx=(12, 6), pady=6)

        ctk.CTkButton(xp_rest_bar, text="+ XP", width=52, height=28, fg_color="#374151", command=self._add_xp_dialog).pack(side="left", padx=3, pady=6)
        ctk.CTkButton(
            xp_rest_bar, text="Subir Nivel", width=105, height=28, fg_color="#D97706", hover_color="#B45309",
            command=lambda: LevelUpManualDialog(self)
        ).pack(side="left", padx=6, pady=6)

        self.lbl_hit_dice = ctk.CTkLabel(xp_rest_bar, text="Dados de Golpe: 1/1 d8", font=("Segoe UI", 12, "bold"), text_color="#34D399")
        self.lbl_hit_dice.pack(side="left", padx=(18, 6), pady=6)

        ctk.CTkButton(
            xp_rest_bar, text="Descanso Largo", width=125, height=28, fg_color="#1E3A8A", hover_color="#1E40AF",
            command=self._take_long_rest
        ).pack(side="right", padx=8, pady=6)

        ctk.CTkButton(
            xp_rest_bar, text="Descanso Corto", width=125, height=28, fg_color="#065F46", hover_color="#047857",
            command=lambda: ShortRestManualDialog(self)
        ).pack(side="right", padx=4, pady=6)

        # Barra de Acciones y Pasivas
        action_bar = ctk.CTkFrame(header, fg_color="#1F2937")
        action_bar.grid(row=5, column=0, columnspan=4, sticky="ew", padx=8, pady=(2, 8))

        self.lbl_prof_bonus = ctk.CTkLabel(action_bar, text="Competencia: +2", font=("Segoe UI", 12, "bold"), text_color="#60A5FA")
        self.lbl_prof_bonus.pack(side="left", padx=10, pady=6)

        self.lbl_passive_stats = ctk.CTkLabel(
            action_bar, text="Percepción Pasiva: 10 | Perspicacia: 10 | Investigación: 10",
            font=("Segoe UI", 12, "bold")
        )
        self.lbl_passive_stats.pack(side="left", padx=10, pady=6)

        ctk.CTkButton(action_bar, text="Eliminar", width=65, fg_color="#8B2635", hover_color="#6E1D29", command=self._delete_current).pack(side="right", padx=6, pady=6)
        ctk.CTkButton(action_bar, text="Guardar", width=90, fg_color="#2563EB", command=self._save_current).pack(side="right", padx=4, pady=6)

        self.btn_pick_spells = ctk.CTkButton(
            action_bar, text="Conjuros (0/0)", width=150, fg_color="#6D28D9", hover_color="#5B21B6",
            command=lambda: ShardSpellPickerDialog(self)
        )
        self.btn_pick_spells.pack(side="right", padx=4, pady=6)

        ctk.CTkButton(
            action_bar, text="Opciones Shard", width=130, fg_color="#D97706", hover_color="#B45309",
            command=lambda: ShardOptionsDialog(self)
        ).pack(side="right", padx=4, pady=6)

    def _build_abilities_and_saves_section(self):
        left_col = ctk.CTkFrame(self.sheet_scroll)
        left_col.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)
        left_col.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(left_col, text="Características y Salvaciones", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, columnspan=4, padx=10, pady=6, sticky="w"
        )

        headers = ["Atributo", "Valor", "Mod.", "Salvación"]
        for c, h in enumerate(headers):
            ctk.CTkLabel(left_col, text=h, font=("Segoe UI", 11, "bold")).grid(row=1, column=c, padx=4, pady=2)

        for idx, ab in enumerate(ABILITIES):
            r = idx + 2
            ctk.CTkLabel(left_col, text=ab, font=("Segoe UI", 12, "bold")).grid(row=r, column=0, padx=8, pady=5, sticky="w")

            var_score = ctk.StringVar(value="10")
            var_score.trace_add("write", lambda *args: self._recalculate_all())
            self.score_vars[ab] = var_score

            entry = ctk.CTkEntry(left_col, width=48, textvariable=var_score, justify="center")
            entry.grid(row=r, column=1, padx=4, pady=5)

            lbl_mod = ctk.CTkLabel(left_col, text="+0", font=("Segoe UI", 12, "bold"), width=36)
            lbl_mod.grid(row=r, column=2, padx=4, pady=5)
            self.mod_labels[ab] = lbl_mod

            save_frame = ctk.CTkFrame(left_col, fg_color="transparent")
            save_frame.grid(row=r, column=3, padx=4, pady=5, sticky="w")

            var_save = ctk.BooleanVar(value=False)
            self.save_prof_vars[ab] = var_save
            chk = ctk.CTkCheckBox(save_frame, text="", width=20, variable=var_save, command=self._recalculate_all)
            chk.pack(side="left")

            lbl_save = ctk.CTkLabel(save_frame, text="+0", font=("Segoe UI", 12))
            lbl_save.pack(side="left", padx=4)
            self.save_labels[ab] = lbl_save

        self.chk_inspiration_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            left_col, text="Inspiración Heroica (5.5e)", variable=self.chk_inspiration_var
        ).grid(row=9, column=0, columnspan=4, padx=10, pady=10, sticky="w")

    def _build_combat_and_mastery_section(self):
        mid_col = ctk.CTkFrame(self.sheet_scroll)
        mid_col.grid(row=1, column=1, sticky="nsew", padx=6, pady=4)
        mid_col.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(mid_col, text="Combate, Armadura Equipada y Salud", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, columnspan=3, padx=10, pady=6, sticky="w"
        )

        # Panel de Armadura Equipada con cálculo automático de CA
        armor_box = ctk.CTkFrame(mid_col, fg_color="#1F2937")
        armor_box.grid(row=1, column=0, columnspan=3, sticky="ew", padx=8, pady=4)
        armor_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(armor_box, text="Armadura Equipada:", font=("Segoe UI", 11, "bold")).grid(
            row=0, column=0, padx=8, pady=(4, 0), sticky="w"
        )
        self.combo_armor = ctk.CTkComboBox(
            armor_box, values=list(ARMORS_CATALOG_55E.keys()),
            command=lambda _: self._recalculate_all()
        )
        self.combo_armor.grid(row=1, column=0, padx=8, pady=(2, 6), sticky="ew")

        self.chk_shield_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            armor_box, text="Escudo (+2)", width=95, variable=self.chk_shield_var,
            command=self._recalculate_all, font=("Segoe UI", 11)
        ).grid(row=1, column=1, padx=4, pady=(2, 6))

        ctk.CTkLabel(armor_box, text="Bono CA:", font=("Segoe UI", 11)).grid(row=0, column=2, padx=4, pady=(4, 0))
        self.entry_ac_bonus = ctk.CTkEntry(armor_box, width=42, justify="center")
        self.entry_ac_bonus.insert(0, "0")
        self.entry_ac_bonus.bind("<KeyRelease>", lambda e: self._recalculate_all())
        self.entry_ac_bonus.grid(row=1, column=2, padx=4, pady=(2, 6))

        self.lbl_ac_calculated = ctk.CTkLabel(
            armor_box, text="CA: 13", font=("Segoe UI", 15, "bold"), text_color="#60A5FA", width=70
        )
        self.lbl_ac_calculated.grid(row=0, column=3, rowspan=2, padx=10, pady=4)

        # Iniciativa, Velocidad y Puntos de Golpe
        self.lbl_initiative = ctk.CTkLabel(mid_col, text="Iniciativa: +0", font=("Segoe UI", 13, "bold"), text_color="#34D399")
        self.lbl_initiative.grid(row=2, column=0, columnspan=2, padx=10, pady=4, sticky="w")
        self.entry_speed = self._labeled_entry(mid_col, "Velocidad (m)", 2, 2, "9 m")

        self.entry_hp_max = self._labeled_entry(mid_col, "PG Máximos", 4, 0, "59")
        self.entry_hp_curr = self._labeled_entry(mid_col, "PG Actuales", 4, 1, "59")
        self.entry_hp_temp = self._labeled_entry(mid_col, "PG Temporales", 4, 2, "0")

        # Armas con Selector Desplegable Automático
        ctk.CTkLabel(mid_col, text="Armas Equipadas (Autocompletado 5.5e)", font=("Segoe UI", 13, "bold")).grid(
            row=6, column=0, columnspan=3, padx=10, pady=(8, 2), sticky="w"
        )

        self.weapon_widgets = []
        weapon_names_list = list(WEAPONS_CATALOG_55E.keys())

        for i in range(3):
            w_card = ctk.CTkFrame(mid_col)
            w_card.grid(row=7 + i, column=0, columnspan=3, sticky="ew", padx=8, pady=3)
            w_card.grid_columnconfigure(0, weight=1)

            top_row = ctk.CTkFrame(w_card, fg_color="transparent")
            top_row.pack(fill="x", padx=6, pady=(5, 2))

            c_wname = ctk.CTkComboBox(top_row, values=weapon_names_list, width=150)
            c_wname.pack(side="left", padx=(0, 4), fill="x", expand=True)

            c_wabil = ctk.CTkComboBox(top_row, values=["Fuerza", "Destreza"], width=95, command=lambda _: self._recalculate_all())
            c_wabil.pack(side="left", padx=3)

            e_wdmg = ctk.CTkEntry(top_row, placeholder_text="Daño", width=95)
            e_wdmg.pack(side="left", padx=3)

            lbl_atk = ctk.CTkLabel(top_row, text="Atq: +2 | Daño: +0", font=("Segoe UI", 11, "bold"), text_color="#FBBF24", width=115)
            lbl_atk.pack(side="right", padx=4)

            bot_row = ctk.CTkFrame(w_card, fg_color="transparent")
            bot_row.pack(fill="x", padx=6, pady=(2, 5))

            lbl_desc = ctk.CTkLabel(bot_row, text="", font=("Segoe UI", 11), wraplength=330, justify="left", text_color="#9CA3AF")
            
            def make_mastery_cb(label_widget):
                return lambda choice: label_widget.configure(text=WEAPON_MASTERIES_55E.get(choice, ""))

            c_wmast = ctk.CTkComboBox(
                bot_row, values=list(WEAPON_MASTERIES_55E.keys()), width=145,
                command=make_mastery_cb(lbl_desc)
            )
            c_wmast.pack(side="left", padx=(0, 6))
            lbl_desc.pack(side="left", fill="x", expand=True)

            def make_weapon_select_cb(idx_slot=i):
                return lambda chosen_weapon: self._on_weapon_preset_selected(idx_slot, chosen_weapon)

            c_wname.configure(command=make_weapon_select_cb(i))

            self.weapon_widgets.append({
                "name": c_wname, "ability": c_wabil, "damage": e_wdmg,
                "mastery": c_wmast, "atk_label": lbl_atk, "desc_label": lbl_desc
            })

    def _on_weapon_preset_selected(self, slot_idx: int, weapon_name: str):
        w_ui = self.weapon_widgets[slot_idx]
        preset = WEAPONS_CATALOG_55E.get(weapon_name)
        if not preset:
            return

        # Si el arma es Sutil (Finesse), elegir automáticamente entre Fuerza o Destreza según cuál tenga más alta el personaje
        if preset.get("finesse"):
            str_val = int(self.score_vars["Fuerza"].get() or 10)
            dex_val = int(self.score_vars["Destreza"].get() or 10)
            best_abil = "Destreza" if dex_val >= str_val else "Fuerza"
            w_ui["ability"].set(best_abil)
        else:
            w_ui["ability"].set(preset.get("ability", "Fuerza"))

        self._set_entry(w_ui["damage"], preset.get("damage", ""))
        mast = preset.get("mastery", "Ninguna")
        w_ui["mastery"].set(mast)
        w_ui["desc_label"].configure(text=WEAPON_MASTERIES_55E.get(mast, ""))
        self._recalculate_all()

    def _build_skills_section(self):
        right_col = ctk.CTkFrame(self.sheet_scroll)
        right_col.grid(row=1, column=2, sticky="nsew", padx=6, pady=4)

        ctk.CTkLabel(right_col, text="Habilidades (Skills)", font=("Segoe UI", 14, "bold")).pack(
            anchor="w", padx=12, pady=6
        )

        for skill_name, ability in SKILLS_55E:
            row = ctk.CTkFrame(right_col, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=1)

            var_sk = ctk.BooleanVar(value=False)
            self.skill_prof_vars[skill_name] = var_sk

            chk = ctk.CTkCheckBox(
                row, text=f"{skill_name} ({ability[:3].upper()})",
                variable=var_sk, command=self._recalculate_all, font=("Segoe UI", 11)
            )
            chk.pack(side="left")

            lbl_val = ctk.CTkLabel(row, text="+0", font=("Segoe UI", 11, "bold"))
            lbl_val.pack(side="right", padx=6)
            self.skill_labels[skill_name] = lbl_val

    def _build_bottom_tabs_section(self):
        """Pestañas inferiores sin emojis incompatibles y con Monedero + Contenedores Desplegables."""
        self.bottom_tabs = ctk.CTkTabview(self.sheet_scroll, height=380)
        self.bottom_tabs.grid(row=2, column=0, columnspan=3, sticky="ew", padx=6, pady=(8, 12))

        tab_features = self.bottom_tabs.add("Rasgos de Especie, Clase y Magia")
        tab_equip = self.bottom_tabs.add("Equipamiento y Montura (kg)")
        tab_notes = self.bottom_tabs.add("Notas de Aventura")

        # --- PESTAÑA 1: RASGOS Y MAGIA ---
        tab_features.grid_columnconfigure(0, weight=3)
        tab_features.grid_columnconfigure(1, weight=2)
        tab_features.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            tab_features, text="Rasgos Obtenidos por Especie, Clase, Subclase y Conjuros Preparados",
            font=("Segoe UI", 13, "bold")
        ).grid(row=0, column=0, padx=8, pady=4, sticky="w")

        self.txt_features = ctk.CTkTextbox(tab_features, height=260, font=("Segoe UI", 12))
        self.txt_features.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)

        pdf_lookup_frame = ctk.CTkFrame(tab_features)
        pdf_lookup_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=8, pady=4)
        pdf_lookup_frame.grid_columnconfigure(0, weight=1)
        pdf_lookup_frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(pdf_lookup_frame, text="Consultar Rasgo/Regla en tu PDF", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=2, padx=8, pady=(6, 2), sticky="w"
        )
        self.entry_feat_pdf_query = ctk.CTkEntry(pdf_lookup_frame, placeholder_text="Ej. Manto de Majestad / Suerte...")
        self.entry_feat_pdf_query.grid(row=1, column=0, padx=(8, 4), pady=4, sticky="ew")
        self.entry_feat_pdf_query.bind("<Return>", lambda e: self._lookup_feature_in_pdf())

        ctk.CTkButton(pdf_lookup_frame, text="Buscar PDF", width=85, fg_color="#2B4C7E", command=self._lookup_feature_in_pdf).grid(
            row=1, column=1, padx=(0, 8), pady=4
        )

        self.txt_feat_pdf_result = ctk.CTkTextbox(pdf_lookup_frame, font=("Segoe UI", 11))
        self.txt_feat_pdf_result.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=8, pady=(2, 8))
        self.txt_feat_pdf_result.insert("1.0", "Escribe el nombre de cualquier rasgo de tu clase o especie para leer el texto exacto de tu manual PDF.")

        # --- PESTAÑA 2: MONEDAS, EQUIPAMIENTO PERSONAL Y MONTURA (CON CONTENEDORES DESPLEGABLES) ---
        tab_equip.grid_columnconfigure((0, 1), weight=1)
        tab_equip.grid_rowconfigure(2, weight=1)

        # Barra Superior de Monedas (Cobre, Plata y Oro) + Botón de Catálogo por Categorías
        coins_bar = ctk.CTkFrame(tab_equip, fg_color="#111827")
        coins_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=6, pady=(2, 6))

        # Barra de Sintonización con Objetos Mágicos (Máximo 3 según Pág. 232)
        attune_bar = ctk.CTkFrame(tab_equip, fg_color="#1E293B")
        attune_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 6))
        attune_bar.grid_columnconfigure((1, 2, 3), weight=1)

        ctk.CTkLabel(
            attune_bar, text="✨ Sintonización Mágica (Máx. 3):",
            font=("Segoe UI", 12, "bold"), text_color="#A78BFA"
        ).grid(row=0, column=0, padx=10, pady=6, sticky="w")

        self.attune_combos = []
        attune_pool = ["-- Ranura Libre --"] + MAGIC_ITEMS_ATTUNEMENT_55E
        for i in range(3):
            cb_att = ctk.CTkComboBox(
                attune_bar, values=attune_pool,
                command=lambda choice, slot=i: self._on_attunement_change(slot, choice)
            )
            cb_att.set("-- Ranura Libre --")
            cb_att.grid(row=0, column=i + 1, padx=6, pady=6, sticky="ew")
            self.attune_combos.append(cb_att)

        ctk.CTkLabel(coins_bar, text="Monedas:", font=("Segoe UI", 12, "bold"), text_color="#FBBF24").pack(side="left", padx=(12, 6), pady=6)

        ctk.CTkLabel(coins_bar, text="Cobre (MC):", font=("Segoe UI", 11, "bold"), text_color="#D97706").pack(side="left", padx=(6, 2))
        self.entry_cp = ctk.CTkEntry(coins_bar, width=55, justify="center")
        self.entry_cp.pack(side="left", padx=(0, 8), pady=5)

        ctk.CTkLabel(coins_bar, text="Plata (MP):", font=("Segoe UI", 11, "bold"), text_color="#9CA3AF").pack(side="left", padx=(6, 2))
        self.entry_sp = ctk.CTkEntry(coins_bar, width=55, justify="center")
        self.entry_sp.pack(side="left", padx=(0, 8), pady=5)

        ctk.CTkLabel(coins_bar, text="Oro (MO):", font=("Segoe UI", 11, "bold"), text_color="#FBBF24").pack(side="left", padx=(6, 2))
        self.entry_gp = ctk.CTkEntry(coins_bar, width=65, justify="center")
        self.entry_gp.pack(side="left", padx=(0, 12), pady=5)

        ctk.CTkButton(
            coins_bar, text="Catálogo de Objetos por Categoría", width=230, fg_color="#2563EB",
            command=lambda: ItemCatalogModal(self, default_target="char")
        ).pack(side="right", padx=10, pady=5)

        # Columna Izquierda: Inventario del Personaje
        char_inv_frame = ctk.CTkFrame(tab_equip)
        char_inv_frame.grid(row=2, column=0, sticky="nsew", padx=6, pady=4)
        char_inv_frame.grid_columnconfigure(0, weight=1)
        char_inv_frame.grid_rowconfigure(2, weight=1)

        top_c_inv = ctk.CTkFrame(char_inv_frame, fg_color="transparent")
        top_c_inv.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 2))
        ctk.CTkLabel(top_c_inv, text="Inventario del Personaje", font=("Segoe UI", 13, "bold")).pack(side="left")
        self.lbl_char_weight = ctk.CTkLabel(top_c_inv, text="Peso: 0.0 / 75.0 kg", font=("Segoe UI", 12, "bold"), text_color="#34D399")
        self.lbl_char_weight.pack(side="right")

        add_c_row = ctk.CTkFrame(char_inv_frame, fg_color="transparent")
        add_c_row.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        self.entry_c_item_name = ctk.CTkEntry(add_c_row, placeholder_text="Objeto (ej. Cuerda 15 m)")
        self.entry_c_item_name.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.entry_c_item_qty = ctk.CTkEntry(add_c_row, width=42, placeholder_text="Cant.")
        self.entry_c_item_qty.insert(0, "1")
        self.entry_c_item_qty.pack(side="left", padx=2)
        self.entry_c_item_kg = ctk.CTkEntry(add_c_row, width=58, placeholder_text="Peso kg")
        self.entry_c_item_kg.pack(side="left", padx=2)
        self.chk_c_is_cont = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(add_c_row, text="Contenedor", width=85, variable=self.chk_c_is_cont, font=("Segoe UI", 11)).pack(side="left", padx=3)
        ctk.CTkButton(add_c_row, text="+ Añadir", width=65, fg_color="#2563EB", command=self._add_char_item).pack(side="left", padx=(2, 0))

        self.scroll_char_inv = ctk.CTkScrollableFrame(char_inv_frame, height=195)
        self.scroll_char_inv.grid(row=2, column=0, sticky="nsew", padx=8, pady=(2, 8))

        # Columna Derecha: Inventario de la Montura (Independiente)
        mount_inv_frame = ctk.CTkFrame(tab_equip)
        mount_inv_frame.grid(row=2, column=1, sticky="nsew", padx=6, pady=4)
        mount_inv_frame.grid_columnconfigure(0, weight=1)
        mount_inv_frame.grid_rowconfigure(2, weight=1)

        top_m_inv = ctk.CTkFrame(mount_inv_frame, fg_color="transparent")
        top_m_inv.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 2))
        ctk.CTkLabel(top_m_inv, text="Montura:", font=("Segoe UI", 13, "bold")).pack(side="left", padx=(0, 6))

        self.combo_mount = ctk.CTkComboBox(
            top_m_inv, values=list(MOUNTS_CAPACITY_KG.keys()), width=195,
            command=lambda _: self._refresh_inventory_views()
        )
        self.combo_mount.pack(side="left")

        self.lbl_mount_weight = ctk.CTkLabel(top_m_inv, text="Carga: 0.0 / 600.0 kg", font=("Segoe UI", 12, "bold"), text_color="#60A5FA")
        self.lbl_mount_weight.pack(side="right")

        add_m_row = ctk.CTkFrame(mount_inv_frame, fg_color="transparent")
        add_m_row.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        self.entry_m_item_name = ctk.CTkEntry(add_m_row, placeholder_text="Objeto en la Montura (ej. Barril, Tienda)")
        self.entry_m_item_name.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.entry_m_item_qty = ctk.CTkEntry(add_m_row, width=42, placeholder_text="Cant.")
        self.entry_m_item_qty.insert(0, "1")
        self.entry_m_item_qty.pack(side="left", padx=2)
        self.entry_m_item_kg = ctk.CTkEntry(add_m_row, width=58, placeholder_text="Peso kg")
        self.entry_m_item_kg.pack(side="left", padx=2)
        self.chk_m_is_cont = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(add_m_row, text="Contenedor", width=85, variable=self.chk_m_is_cont, font=("Segoe UI", 11)).pack(side="left", padx=3)
        ctk.CTkButton(add_m_row, text="+ A Montura", width=80, fg_color="#D97706", command=self._add_mount_item).pack(side="left", padx=(2, 0))

        self.scroll_mount_inv = ctk.CTkScrollableFrame(mount_inv_frame, height=195)
        self.scroll_mount_inv.grid(row=2, column=0, sticky="nsew", padx=8, pady=(2, 8))

        # --- PESTAÑA 3: NOTAS DE AVENTURA ---
        tab_notes.grid_columnconfigure(0, weight=1)
        tab_notes.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            tab_notes, text="Diario de Aventura, Misiones, NPCs, Organizaciones y Apuntes de Sesión",
            font=("Segoe UI", 13, "bold")
        ).grid(row=0, column=0, padx=10, pady=(6, 2), sticky="w")

        self.txt_adventure_notes = ctk.CTkTextbox(tab_notes, height=255, font=("Segoe UI", 12))
        self.txt_adventure_notes.grid(row=1, column=0, sticky="nsew", padx=10, pady=(2, 8))

    def _labeled_entry(self, parent, label_text, row, col, placeholder=""):
        ctk.CTkLabel(parent, text=label_text, font=("Segoe UI", 11, "bold")).grid(
            row=row, column=col, padx=8, pady=(6, 0), sticky="w"
        )
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder)
        entry.grid(row=row + 1, column=col, padx=8, pady=(0, 6), sticky="ew")
        return entry

    def _add_xp_dialog(self):
        dialog = ctk.CTkInputDialog(
            text="¿Cuánta Experiencia (XP) ganaste en la sesión?\n(Puedes usar números negativos para restar)",
            title="Añadir Experiencia (XP)"
        )
        val = dialog.get_input()
        if not val:
            return
        try:
            added = int(val.strip())
        except ValueError:
            messagebox.showwarning("Aviso", "Introduce un número entero de XP.")
            return

        curr_xp = int(self.builder_state.get("xp_current", 0))
        new_xp = max(0, curr_xp + added)
        self.builder_state["xp_current"] = new_xp
        self._recalculate_all()

        lvl = int(self.combo_level.get() or 1)
        next_xp = Character55eRules.get_next_level_xp(lvl)
        if lvl < 20 and new_xp >= next_xp:
            if messagebox.askyesno("¡Experiencia Suficiente!", f"Tienes {new_xp:,} XP (necesitas {next_xp:,} XP para Nivel {lvl+1}).\n¿Quieres abrir la ventana para Subir de Nivel ahora?"):
                LevelUpManualDialog(self)

    def _take_long_rest(self):
        hp_max = int(self.entry_hp_max.get().strip() or 10)
        lvl = int(self.combo_level.get() or 1)
        char_class = self.combo_class.get()
        hd_faces = CLASSES_55E.get(char_class, {}).get("hit_die", 8)

        self._set_entry(self.entry_hp_curr, str(hp_max))
        self._set_entry(self.entry_hp_temp, "0")
        self.builder_state["hit_dice_current"] = lvl

        if self.combo_species.get() == "Humano":
            self.chk_inspiration_var.set(True)

        self._recalculate_all()
        messagebox.showinfo(
            "Descanso Largo Completado (Reglas 5.5e)",
            f"• Puntos de Golpe restaurados al máximo ({hp_max} / {hp_max}).\n"
            f"• PG Temporales reiniciados a 0.\n"
            f"• Dados de Golpe restaurados al máximo ({lvl}/{lvl} d{hd_faces}).\n"
            f"• Todos tus espacios de conjuro y usos de rasgos por Descanso Largo han sido restaurados."
        )

    # --- LÓGICA DE INVENTARIO Y CONTENEDORES DESPLEGABLES ---
    def _add_char_item(self):
        name = self.entry_c_item_name.get().strip()
        if not name:
            return
        try:
            qty = max(1, int(self.entry_c_item_qty.get().strip() or 1))
            kg = max(0.0, float(self.entry_c_item_kg.get().replace(",", ".").strip() or 0.0))
        except ValueError:
            messagebox.showwarning("Peso inválido", "Introduce cantidad entera y peso unitario en kg (ej. 1.5).")
            return

        inv = self.builder_state.setdefault("inventory_char", [])
        inv.append({
            "name": name, "qty": qty, "weight_kg": kg,
            "is_container": self.chk_c_is_cont.get(),
            "ignore_contents_weight": "bolsa de contención" in name.lower(),
            "expanded": True, "contents": []
        })
        self.entry_c_item_name.delete(0, "end")
        self.entry_c_item_kg.delete(0, "end")
        self.chk_c_is_cont.set(False)
        self._refresh_inventory_views()

    def _add_mount_item(self):
        name = self.entry_m_item_name.get().strip()
        if not name:
            return
        try:
            qty = max(1, int(self.entry_m_item_qty.get().strip() or 1))
            kg = max(0.0, float(self.entry_m_item_kg.get().replace(",", ".").strip() or 0.0))
        except ValueError:
            messagebox.showwarning("Peso inválido", "Introduce cantidad entera y peso unitario en kg (ej. 5.0).")
            return

        inv = self.builder_state.setdefault("inventory_mount", [])
        inv.append({
            "name": name, "qty": qty, "weight_kg": kg,
            "is_container": self.chk_m_is_cont.get(),
            "ignore_contents_weight": "bolsa de contención" in name.lower(),
            "expanded": True, "contents": []
        })
        self.entry_m_item_name.delete(0, "end")
        self.entry_m_item_kg.delete(0, "end")
        self.chk_m_is_cont.set(False)
        self._refresh_inventory_views()

    def _toggle_container_expand(self, inv_key: str, idx: int):
        inv = self.builder_state.get(inv_key, [])
        if 0 <= idx < len(inv):
            inv[idx]["expanded"] = not inv[idx].get("expanded", True)
        self._refresh_inventory_views()

    def _remove_inv_item(self, key: str, index: int, sub_idx: int = None):
        inv = self.builder_state.get(key, [])
        if 0 <= index < len(inv):
            if sub_idx is not None:
                contents = inv[index].get("contents", [])
                if 0 <= sub_idx < len(contents):
                    contents.pop(sub_idx)
            else:
                inv.pop(index)
        self._refresh_inventory_views()

    def _transfer_inv_item(self, from_key: str, to_key: str, index: int):
        src = self.builder_state.get(from_key, [])
        dst = self.builder_state.setdefault(to_key, [])
        if 0 <= index < len(src):
            item = src.pop(index)
            dst.append(item)
        self._refresh_inventory_views()

    def _render_inventory_column(self, scroll_widget, inv_key: str, is_char: bool):
        for w in scroll_widget.winfo_children():
            w.destroy()

        items = self.builder_state.get(inv_key, [])
        total_kg = 0.0

        for idx, it in enumerate(items):
            item_total_kg = Character55eRules.calculate_item_tree_weight(it)
            total_kg += item_total_kg
            is_cont = bool(it.get("is_container", False))
            expanded = bool(it.get("expanded", True))
            contents = it.get("contents", [])

            card = ctk.CTkFrame(scroll_widget, fg_color="#1E293B" if is_cont else "#1F2937")
            card.pack(fill="x", padx=2, pady=2)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=4, pady=3)

            if is_cont:
                arrow = "▼" if expanded else "▶"
                btn_exp = ctk.CTkButton(
                    top_row, text=f"{arrow} {it['name']} ({len(contents)} ítems) — {item_total_kg} kg",
                    anchor="w", fg_color="#334155", hover_color="#475569", height=26,
                    font=("Segoe UI", 11, "bold"),
                    command=lambda k=inv_key, i=idx: self._toggle_container_expand(k, i)
                )
                btn_exp.pack(side="left", fill="x", expand=True, padx=(2, 4))

                ctk.CTkButton(
                    top_row, text="+ Meter", width=56, height=24, fg_color="#2563EB",
                    command=lambda t=("char" if is_char else "mount"), i=idx: ItemCatalogModal(self, default_target=t, container_idx=i)
                ).pack(side="left", padx=2)
            else:
                ctk.CTkLabel(
                    top_row, text=f"{it['name']} (x{it['qty']}) — {item_total_kg} kg", font=("Segoe UI", 11)
                ).pack(side="left", padx=6)

            ctk.CTkButton(
                top_row, text="✕", width=26, height=24, fg_color="#8B2635",
                command=lambda k=inv_key, i=idx: self._remove_inv_item(k, i)
            ).pack(side="right", padx=2)

            transfer_txt = "→ Montura" if is_char else "← PJ"
            other_key = "inventory_mount" if is_char else "inventory_char"
            ctk.CTkButton(
                top_row, text=transfer_txt, width=68, height=24, fg_color="#374151",
                command=lambda fk=inv_key, tk=other_key, i=idx: self._transfer_inv_item(fk, tk, i)
            ).pack(side="right", padx=2)

            # Si es un contenedor y está expandido, mostrar sus objetos internos
            if is_cont and expanded:
                sub_box = ctk.CTkFrame(card, fg_color="#0F172A")
                sub_box.pack(fill="x", padx=(18, 6), pady=(0, 5))

                if not contents:
                    ctk.CTkLabel(
                        sub_box, text="Contenedor vacío (usa '+ Meter' para guardar objetos aquí)",
                        font=("Segoe UI", 10), text_color="#64748B"
                    ).pack(anchor="w", padx=8, pady=3)
                else:
                    for s_idx, sub in enumerate(contents):
                        s_kg = round(float(sub.get("qty", 1)) * float(sub.get("weight_kg", 0.0)), 2)
                        s_row = ctk.CTkFrame(sub_box, fg_color="transparent")
                        s_row.pack(fill="x", padx=6, pady=1)

                        ctk.CTkLabel(
                            s_row, text=f"↳ {sub['name']} (x{sub['qty']}) — {s_kg} kg",
                            font=("Segoe UI", 11), text_color="#CBD5E1"
                        ).pack(side="left")

                        ctk.CTkButton(
                            s_row, text="✕", width=22, height=20, fg_color="#7F1D1D",
                            command=lambda k=inv_key, i=idx, si=s_idx: self._remove_inv_item(k, i, si)
                        ).pack(side="right", padx=2)

        return total_kg

    def _refresh_inventory_views(self):
        total_char_kg = self._render_inventory_column(self.scroll_char_inv, "inventory_char", is_char=True)

        raw_str = self.score_vars.get("Fuerza", ctk.StringVar(value="10")).get().strip()
        str_score = int(raw_str) if raw_str.isdigit() else 10
        max_char_kg = Character55eRules.get_carrying_capacity_kg(str_score, self.combo_species.get())
        over_char = total_char_kg > max_char_kg
        self.lbl_char_weight.configure(
            text=f"Peso: {total_char_kg:.1f} / {max_char_kg:.1f} kg" + (" [SOBRECARGA]" if over_char else ""),
            text_color="#EF4444" if over_char else "#34D399"
        )

        mount_name = self.combo_mount.get()
        self.builder_state["mount_type"] = mount_name
        max_mount_kg = MOUNTS_CAPACITY_KG.get(mount_name, 0.0)

        total_mount_kg = self._render_inventory_column(self.scroll_mount_inv, "inventory_mount", is_char=False)
        over_mount = total_mount_kg > max_mount_kg and max_mount_kg > 0
        self.lbl_mount_weight.configure(
            text=f"Carga: {total_mount_kg:.1f} / {max_mount_kg:.1f} kg" + (" [EXCESO]" if over_mount else ""),
            text_color="#EF4444" if over_mount else "#60A5FA"
        )

    def _lookup_feature_in_pdf(self):
        q = self.entry_feat_pdf_query.get().strip()
        if not q:
            return
        hits = self.db.search_manuals(q, limit=4)
        self.txt_feat_pdf_result.delete("1.0", "end")
        if not hits:
            self.txt_feat_pdf_result.insert("1.0", f"Sin resultados en tus PDFs para '{q}'.")
            return
        lines = [f"Extractos del Manual para '{q}':\n"]
        for h in hits:
            snip = h["match_snippet"].replace("\n", " ")
            lines.append(f"• [{h['manual_title']} Pág. {h['page_number']}]: {snip}\n")
        self.txt_feat_pdf_result.insert("1.0", "\n".join(lines))

    def _update_features_display(self):
            sp_name = self.combo_species.get()
            c_name = self.combo_class.get()
            sub_name = self.combo_subclass.get()
            lvl = int(self.combo_level.get() or 1)
            prof = Character55eRules.get_proficiency_bonus(lvl)

            langs = ", ".join(self.builder_state.get("language_choices", ["Común"]))
            insts = ", ".join(self.builder_state.get("instrument_choices", []))
            cantrips = ", ".join(self.builder_state.get("selected_cantrips", []))
            spells = ", ".join(self.builder_state.get("selected_spells", []))
            always_prep = Character55eRules.get_always_prepared_spells(c_name, sub_name, lvl)
            slots_dict = Character55eRules.get_spell_slots_by_level(c_name, sub_name, lvl)
            prog_choices = self.builder_state.get("level_progression_choices", {})

            lines = [
                f"=== RESUMEN DE ORIGEN Y PROGRESIÓN ({c_name.upper()} NIVEL {lvl}) ===",
                f"• Idiomas: {langs}",
                f"• Dote de Origen: {self.entry_origin_feat.get()}"
            ]
            if self.builder_state.get("species_lineage"):
                lines.append(f"• Linaje de {sp_name}: {self.builder_state['species_lineage']}")
            if insts:
                lines.append(f"• Instrumentos Musicales: {insts}")
            if self.builder_state.get("expertise_skills"):
                lines.append(f"• Pericia (Doble Competencia ★★): {', '.join(self.builder_state['expertise_skills'])}")

            # Mostrar Espacios de Conjuro, CD de Salvación y Ataque de Conjuro (Pág. 41)
            if slots_dict:
                sp_abil = CLASSES_55E.get(c_name, {}).get("spell_ability") or "Carisma"
                raw_sc = self.score_vars.get(sp_abil, ctk.StringVar(value="10")).get().strip()
                sp_mod = Character55eRules.get_modifier(int(raw_sc) if raw_sc.isdigit() else 10)
                spell_dc = 8 + prof + sp_mod
                spell_atk = prof + sp_mod
                slots_str = "  |  ".join([f"Nivel {k}: {v} espacios" for k, v in sorted(slots_dict.items())])

                lines.append(f"\n=== LANZAMIENTO DE CONJUROS (Aptitud: {sp_abil} | CD Salvación: {spell_dc} | Ataque Mágico: +{spell_atk}) ===")
                lines.append(f"• Espacios de Conjuro por Nivel: {slots_str}")
                if cantrips:
                    lines.append(f"• Trucos Conocidos: {cantrips}")
                if always_prep:
                    lines.append(f"• Conjuros Siempre Preparados (Clase/Subclase): {', '.join(always_prep)}")
                if spells:
                    lines.append(f"• Conjuros Preparados de tu Lista: {spells}")

            # Mostrar elecciones hechas nivel por nivel
            if prog_choices:
                lines.append("\n=== DECISIONES TOMADAS POR NIVEL (SHARD BUILDER) ===")
                for k, val in prog_choices.items():
                    if val and val not in ("Ninguno", "Ninguna"):
                        lines.append(f"• [{k.upper()}]: {val}")

            lines.append("\n=== RASGOS DE ESPECIE, CLASE Y SUBCLASE DESBLOQUEADOS HASTA TU NIVEL ===")
            features = Character55eRules.get_features_up_to_level(sp_name, c_name, sub_name, lvl)
            for title, desc in features:
                lines.append(f"▸ {title}:\n   {desc}")

            self.txt_features.delete("1.0", "end")
            self.txt_features.insert("1.0", "\n".join(lines))

    def _on_species_change(self, sp_name: str):
        sp_info = SPECIES_55E.get(sp_name, {"speed": "9 m"})
        self._set_entry(self.entry_speed, sp_info["speed"])
        self._update_features_display()
        self._recalculate_all()

    def _on_background_change(self, bg_name: str):
        bg_info = BACKGROUNDS_55E.get(bg_name, {})
        suggested_feat = bg_info.get("feat", "")
        if suggested_feat:
            self._set_entry(self.entry_origin_feat, suggested_feat)
        self._update_features_display()

    def _on_class_change(self, class_name: str):
        lvl = int(self.combo_level.get() or 1)
        c_info = CLASSES_55E.get(class_name, CLASSES_55E["Bardo"])

        if lvl >= 3:
            subs = c_info.get("subclasses", ["Subclase Estándar"])
            self.combo_subclass.configure(values=subs)
            if self.combo_subclass.get() not in subs:
                self.combo_subclass.set(subs[0])
        else:
            self.combo_subclass.configure(values=["Se elige en Nivel 3"])
            self.combo_subclass.set("Se elige en Nivel 3")

        self._update_features_display()
        self._recalculate_all()

    def _recalculate_all(self):
        try:
            level = int(self.combo_level.get() or 1)
        except ValueError:
            level = 1

        char_class = self.combo_class.get()
        prof = Character55eRules.get_proficiency_bonus(level)
        self.lbl_prof_bonus.configure(text=f"Competencia: +{prof}")

        curr_xp = int(self.builder_state.get("xp_current", 0))
        next_xp = Character55eRules.get_next_level_xp(level)
        self.lbl_xp_info.configure(text=f"XP: {curr_xp:,} / {next_xp:,}")

        hd_faces = CLASSES_55E.get(char_class, {}).get("hit_die", 8)
        hd_curr = min(level, int(self.builder_state.get("hit_dice_current", level)))
        self.builder_state["hit_dice_current"] = hd_curr
        self.lbl_hit_dice.configure(text=f"Dados de Golpe: {hd_curr}/{level} d{hd_faces}")

        mods = {}
        for ab in ABILITIES:
            raw = self.score_vars[ab].get().strip()
            score = int(raw) if raw.isdigit() else 10
            mod = Character55eRules.get_modifier(score)
            mods[ab] = mod
            self.mod_labels[ab].configure(text=Character55eRules.format_mod(mod))

            save_val = mod + (prof if self.save_prof_vars[ab].get() else 0)
            self.save_labels[ab].configure(text=Character55eRules.format_mod(save_val))

        if hasattr(self, "combo_armor"):
            armor_name = self.combo_armor.get()
            has_shield = self.chk_shield_var.get()
            raw_bonus = self.entry_ac_bonus.get().strip().replace("+", "")
            ac_bonus = int(raw_bonus) if raw_bonus.lstrip("-").isdigit() else 0
            calc_ac = Character55eRules.calculate_armor_class(armor_name, has_shield, ac_bonus, mods)
            self.lbl_ac_calculated.configure(text=f"CA: {calc_ac}")
            self.builder_state["armor_class"] = calc_ac

        dex_mod = mods.get("Destreza", 0)
        self.lbl_initiative.configure(text=f"Iniciativa: {Character55eRules.format_mod(dex_mod)}")

        # Cálculo de Habilidades incluyendo Pericia (★★ = x2 comp) y Aprendiz de Mucho (Bardo Niv 2+ = +mitad comp)
        expertise_set = set(self.builder_state.get("expertise_skills", []))
        jack_of_all_trades = (char_class == "Bardo" and level >= 2)
        prog_order = self.builder_state.get("level_progression_choices", {}).get("lvl1_order", "")

        skill_totals = {}
        for skill_name, ability in SKILLS_55E:
            base_mod = mods.get(ability, 0)
            is_prof = self.skill_prof_vars[skill_name].get()
            is_exp = (skill_name in expertise_set)

            if is_exp:
                total = base_mod + (prof * 2)
                prefix = "★★ "
            elif is_prof:
                total = base_mod + prof
                prefix = ""
            elif jack_of_all_trades:
                total = base_mod + (prof // 2)
                prefix = "~"
            else:
                total = base_mod
                prefix = ""

            # Bono extra de Orden Divina (Taumaturgo) o Primigenia (Naturalista)
            if "Taumaturgo" in prog_order and skill_name in ("Conocimiento Arcano", "Religión"):
                total += max(1, mods.get("Sabiduría", 0))
            elif "Naturalista" in prog_order and skill_name in ("Conocimiento Arcano", "Naturaleza"):
                total += max(1, mods.get("Sabiduría", 0))

            skill_totals[skill_name] = total
            self.skill_labels[skill_name].configure(text=f"{prefix}{Character55eRules.format_mod(total)}")

        p_perc = 10 + skill_totals.get("Percepción", 0)
        p_ins = 10 + skill_totals.get("Perspicacia", 0)
        p_inv = 10 + skill_totals.get("Investigación", 0)
        self.lbl_passive_stats.configure(
            text=f"Percepción Pasiva: {p_perc} | Perspicacia: {p_ins} | Investigación: {p_inv}"
        )

        c_max = Character55eRules.get_cantrips_max(char_class, level, prog_order)
        s_max = Character55eRules.get_prepared_spells_max(char_class, level)
        c_cur = len(self.builder_state.get("selected_cantrips", []))
        s_cur = len(self.builder_state.get("selected_spells", []))
        if c_max > 0 or s_max > 0:
            self.btn_pick_spells.configure(
                state="normal",
                text=f"Conjuros ({c_cur}/{c_max} T | {s_cur}/{s_max} C)"
            )
        else:
            self.btn_pick_spells.configure(state="disabled", text="Sin Conjuros")

        for w in self.weapon_widgets:
            ab_used = w["ability"].get()
            ab_mod = mods.get(ab_used, 0)
            atk_bonus = ab_mod + prof
            w["atk_label"].configure(
                text=f"Atq: {Character55eRules.format_mod(atk_bonus)} | Daño: {Character55eRules.format_mod(ab_mod)}"
            )
            mast_name = w["mastery"].get()
            w["desc_label"].configure(text=WEAPON_MASTERIES_55E.get(mast_name, ""))

        if hasattr(self, "scroll_char_inv"):
            self._refresh_inventory_views()

    def _collect_form_data(self) -> dict:
        weapons_data = []
        for w in self.weapon_widgets:
            weapons_data.append({
                "name": w["name"].get().strip(),
                "ability": w["ability"].get(),
                "damage": w["damage"].get().strip(),
                "mastery": w["mastery"].get()
            })

        raw_bonus = self.entry_ac_bonus.get().strip().replace("+", "")
        ac_bonus = int(raw_bonus) if raw_bonus.lstrip("-").isdigit() else 0

        coins = {
            "cp": int(self.entry_cp.get().strip() or 0) if self.entry_cp.get().strip().isdigit() else 0,
            "sp": int(self.entry_sp.get().strip() or 0) if self.entry_sp.get().strip().isdigit() else 0,
            "gp": int(self.entry_gp.get().strip() or 0) if self.entry_gp.get().strip().isdigit() else 0,
        }

        stats = dict(self.builder_state)
        stats.update({
            "scores": {ab: int(self.score_vars[ab].get() or 10) for ab in ABILITIES},
            "saving_throws_prof": {ab: self.save_prof_vars[ab].get() for ab in ABILITIES},
            "skills_prof": {sk[0]: self.skill_prof_vars[sk[0]].get() for sk in SKILLS_55E},
            "origin_feat": self.entry_origin_feat.get().strip(),
            "equipped_armor": self.combo_armor.get(),
            "equipped_shield": self.chk_shield_var.get(),
            "armor_magic_bonus": ac_bonus,
            "speed": self.entry_speed.get().strip() or "9 m",
            "hp_max": self.entry_hp_max.get().strip() or "8",
            "hp_current": self.entry_hp_curr.get().strip() or "8",
            "hp_temp": self.entry_hp_temp.get().strip() or "0",
            "heroic_inspiration": self.chk_inspiration_var.get(),
            "coins": coins,
            "weapons": weapons_data,
            "mount_type": self.combo_mount.get(),
            "adventure_notes": self.txt_adventure_notes.get("1.0", "end").strip()
        })

        return {
            "id": self.current_char_id,
            "name": self.entry_name.get().strip() or "Héroe Sin Nombre",
            "player_name": self.entry_player.get().strip(),
            "species": self.combo_species.get(),
            "background": self.combo_bg.get(),
            "char_class": self.combo_class.get(),
            "subclass": self.combo_subclass.get(),
            "level": int(self.combo_level.get() or 1),
            "stats": stats
        }

    def _populate_form(self, data: dict):
        self.current_char_id = data.get("id")
        stats = data.get("stats", Character55eRules.default_stats_payload())
        self.builder_state = dict(Character55eRules.default_stats_payload())
        self.builder_state.update(stats)

        lvl = int(data.get("level", 1))
        if "hit_dice_current" not in stats:
            self.builder_state["hit_dice_current"] = lvl
        if "xp_current" not in stats:
            self.builder_state["xp_current"] = XP_THRESHOLDS_55E.get(lvl, 0)

        self._set_entry(self.entry_name, data.get("name", ""))
        self._set_entry(self.entry_player, data.get("player_name", ""))
        self.combo_species.set(data.get("species", "Mediano"))
        self.combo_bg.set(data.get("background", "Noble"))
        self.combo_class.set(data.get("char_class", "Bardo"))
        self.combo_level.set(str(lvl))
        self._on_class_change(self.combo_class.get())
        if data.get("subclass"):
            self.combo_subclass.set(data.get("subclass"))

        for ab in ABILITIES:
            self.score_vars[ab].set(str(stats.get("scores", {}).get(ab, 10)))
            self.save_prof_vars[ab].set(bool(stats.get("saving_throws_prof", {}).get(ab, False)))

        for sk_name, _ in SKILLS_55E:
            self.skill_prof_vars[sk_name].set(bool(stats.get("skills_prof", {}).get(sk_name, False)))

        self._set_entry(self.entry_origin_feat, stats.get("origin_feat", "Habilidoso (Skilled)"))

        # Armadura equipada
        armor_saved = stats.get("equipped_armor", "Cuero (11 + DES)")
        if armor_saved not in ARMORS_CATALOG_55E:
            armor_saved = "Cuero (11 + DES)"
        self.combo_armor.set(armor_saved)
        self.chk_shield_var.set(bool(stats.get("equipped_shield", False)))
        self._set_entry(self.entry_ac_bonus, str(stats.get("armor_magic_bonus", 0)))

        self._set_entry(self.entry_speed, stats.get("speed", "9 m"))
        self._set_entry(self.entry_hp_max, str(stats.get("hp_max", "59")))
        self._set_entry(self.entry_hp_curr, str(stats.get("hp_current", "59")))
        self._set_entry(self.entry_hp_temp, str(stats.get("hp_temp", "0")))
        self.chk_inspiration_var.set(bool(stats.get("heroic_inspiration", False)))

        # Monedas
        coins = stats.get("coins", {"cp": 0, "sp": 25, "gp": 150})
        self._set_entry(self.entry_cp, str(coins.get("cp", 0)))
        self._set_entry(self.entry_sp, str(coins.get("sp", 0)))
        self._set_entry(self.entry_gp, str(coins.get("gp", 0)))

        weapons = stats.get("weapons", [])
        for i, w_ui in enumerate(self.weapon_widgets):
            w_data = weapons[i] if i < len(weapons) else {"name": "-- Seleccionar Arma --", "ability": "Fuerza", "damage": "", "mastery": "Ninguna"}
            w_ui["name"].set(w_data.get("name") or "-- Seleccionar Arma --")
            w_ui["ability"].set(w_data.get("ability", "Fuerza"))
            self._set_entry(w_ui["damage"], w_data.get("damage", ""))
            w_ui["mastery"].set(w_data.get("mastery", "Ninguna"))

        mount_saved = self.builder_state.get("mount_type", "Carreta / Carro Tirado")
        if mount_saved not in MOUNTS_CAPACITY_KG:
            mount_saved = "Carreta / Carro Tirado"
        self.combo_mount.set(mount_saved)

        self.txt_adventure_notes.delete("1.0", "end")
        adv_notes = stats.get("adventure_notes") or stats.get("features_notes", "")
        self.txt_adventure_notes.insert("1.0", adv_notes)

        self._update_features_display()
        self._refresh_inventory_views()
        self._recalculate_all()

        attuned = stats.get("attuned_items", ["", "", ""])
        if hasattr(self, "attune_combos"):
            for i in range(3):
                val = attuned[i] if i < len(attuned) and attuned[i] else "-- Ranura Libre --"
                self.attune_combos[i].set(val)

    def _set_entry(self, entry_widget, text: str):
        entry_widget.delete(0, "end")
        entry_widget.insert(0, text)

    def _load_default_blank(self):
        blank = {
            "id": None,
            "name": "",
            "player_name": "",
            "species": "Humano",
            "background": "Acólito",
            "char_class": "Guerrero",
            "subclass": "Se elige en Nivel 3",
            "level": 1,
            "stats": Character55eRules.default_stats_payload()
        }
        self._populate_form(blank)
        # Dejar Dote de Origen vacía hasta que el jugador elija su Trasfondo u Opciones Shard
        self._set_entry(self.entry_origin_feat, "")
        self._set_entry(self.entry_hp_max, "10")
        self._set_entry(self.entry_hp_curr, "10")
        self._recalculate_all()

    def _save_current(self):
        data = self._collect_form_data()
        saved_id = self.db.save_character(data)
        self.current_char_id = saved_id
        self._refresh_character_list()
        messagebox.showinfo("Guardado", f"Personaje '{data['name']}' guardado correctamente.")

    def _delete_current(self):
        if not self.current_char_id:
            return
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este personaje?"):
            self.db.delete_character(self.current_char_id)
            self._load_default_blank()
            self._refresh_character_list()

    def _refresh_character_list(self):
        for w in self.char_list_scroll.winfo_children():
            w.destroy()

        chars = self.db.get_all_characters()
        if not chars:
            ctk.CTkLabel(self.char_list_scroll, text="Sin personajes aún.").pack(pady=10)
            return

        for c in chars:
            card = ctk.CTkFrame(self.char_list_scroll)
            card.pack(fill="x", padx=2, pady=3)

            title = f"{c['name']}\nNiv. {c['level']} {c['species']} {c['char_class']}"
            btn = ctk.CTkButton(
                card, text=title, anchor="w", fg_color="#2B4C7E", hover_color="#1E3A8A",
                command=lambda cid=c["id"]: self._load_char_from_db(cid)
            )
            btn.pack(fill="x", padx=4, pady=4)

    def _load_char_from_db(self, char_id: int):
        data = self.db.get_character_by_id(char_id)
        if data:
            self._populate_form(data)

    def _export_json(self):
        data = self._collect_form_data()
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=f"{data['name'].replace(' ', '_')}_55e.json",
            filetypes=[("Archivo JSON", "*.json")]
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Exportado", "Hoja exportada en formato JSON.")

    def _import_json(self):
        path = filedialog.askopenfilename(filetypes=[("Archivo JSON", "*.json")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["id"] = None
            self._populate_form(data)
            self._save_current()

    def _on_attunement_change(self, slot_idx: int, chosen_item: str):
        current_list = [cb.get().strip() for cb in self.attune_combos]
        # Regla Pág. 232: No puedes sintonizarte con más de una copia del mismo objeto
        if chosen_item != "-- Ranura Libre --" and current_list.count(chosen_item) > 1:
            messagebox.showwarning(
                "Regla de Sintonización (Pág. 232)",
                f"No puedes sintonizarte con más de una copia de '{chosen_item}' a la vez."
            )
            self.attune_combos[slot_idx].set("-- Ranura Libre --")
            current_list[slot_idx] = "-- Ranura Libre --"

        self.builder_state["attuned_items"] = [
            x if x != "-- Ranura Libre --" else "" for x in current_list
        ]