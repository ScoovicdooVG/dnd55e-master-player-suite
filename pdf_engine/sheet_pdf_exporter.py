import base64
import io
import sys
from pathlib import Path
from PIL import Image
import pymupdf as fitz
from models.character_55e import (
    Character55eRules, ABILITIES, SKILLS_55E, WEAPON_MASTERIES_55E
)


class CharacterSheetPDFExporter:
    @staticmethod
    def export_to_pdf(char_data: dict, output_path: str, edition: str = "5.5e"):
        doc = fitz.open()
        stats = char_data.get("stats", {})
        level = int(char_data.get("level", 1))
        char_class = char_data.get("char_class", "Guerrero")
        subclass = char_data.get("subclass", "")
        species = char_data.get("species", "Humano")
        background = char_data.get("background", "")
        name = char_data.get("name", "Héroe Sin Nombre")
        player_name = char_data.get("player_name", "")

        prof = Character55eRules.get_proficiency_bonus(level)
        scores = stats.get("scores", {ab: 10 for ab in ABILITIES})
        saves_prof = stats.get("saving_throws_prof", {})
        skills_prof = stats.get("skills_prof", {})
        exp_set = set(stats.get("expertise_skills", []))
        jack = (char_class == "Bardo" and level >= 2)
        prog_order = stats.get("level_progression_choices", {}).get("lvl1_order", "")

        mods = {}
        for ab in ABILITIES:
            mods[ab] = Character55eRules.get_modifier(int(scores.get(ab, 10)))

        border_col = (0.25, 0.28, 0.35)
        accent_col = (0.55, 0.15, 0.21)
        header_bg = (0.12, 0.16, 0.24)
        box_bg = (0.97, 0.97, 0.96)
        text_dark = (0.10, 0.10, 0.12)
        text_muted = (0.38, 0.40, 0.45)

        page1 = doc.new_page(width=612, height=792)

        logo_bytes = CharacterSheetPDFExporter._get_logo_bytes()

        page1.draw_rect(fitz.Rect(22, 18, 590, 90), color=border_col, fill=header_bg, width=1.2)

        if logo_bytes:
            page1.insert_image(fitz.Rect(28, 26, 82, 80), stream=logo_bytes, keep_proportion=True)
            title_x = 90
        else:
            title_x = 32

        clean_name = name[:32]
        if len(clean_name) <= 15:
            name_fs = 15.5
        elif len(clean_name) <= 22:
            name_fs = 12.5
        else:
            name_fs = 10.5

        page1.insert_text((title_x, 45), clean_name, fontsize=name_fs, fontname="hebo", color=(1, 1, 1))
        page1.insert_text((title_x, 63), f"HOJA DE PERSONAJE - D&D {edition}", fontsize=8, fontname="hebo", color=(0.98, 0.75, 0.15))
        if player_name:
            page1.insert_text((title_x, 78), f"Jugador: {player_name[:24]}", fontsize=8, fontname="helv", color=(0.82, 0.85, 0.90))

        if edition == "5e":
            sp_label = "RAZA"
            insp_label = "INSPIRACIÓN"
            feat_label = "RASGO TRASFONDO"
        else:
            sp_label = "ESPECIE"
            insp_label = "INSPIRACIÓN HEROICA"
            feat_label = "DOTE DE ORIGEN"

        meta_items = [
            ("CLASE Y NIVEL", f"{char_class} (Niv. {level})", 292, 34),
            ("TRASFONDO", background[:18], 412, 34),
            ("EXPERIENCIA", f"{int(stats.get('xp_current', 0)):,} XP", 516, 34),
            (sp_label, species[:18], 292, 64),
            ("SUBCLASE", subclass[:20], 412, 64),
            ("COMPETENCIA", f"+{prof}", 516, 64),
        ]
        for lbl, val, mx, my in meta_items:
            page1.insert_text((mx, my), lbl, fontsize=6.5, fontname="hebo", color=(0.70, 0.75, 0.82))
            page1.insert_text((mx, my + 12), str(val), fontsize=8.8, fontname="helv", color=(1, 1, 1))

        y_ab = 102
        for ab in ABILITIES:
            rect_ab = fitz.Rect(22, y_ab, 182, y_ab + 76)
            page1.draw_rect(rect_ab, color=border_col, fill=box_bg, width=1.0)
            page1.draw_rect(fitz.Rect(22, y_ab, 182, y_ab + 16), color=border_col, fill=accent_col, width=0.5)
            page1.insert_text((30, y_ab + 11.5), ab.upper(), fontsize=8.5, fontname="hebo", color=(1, 1, 1))

            sc_val = int(scores.get(ab, 10))
            mod_str = Character55eRules.format_mod(mods[ab])
            page1.insert_text((34, y_ab + 44), mod_str, fontsize=19, fontname="hebo", color=text_dark)
            page1.draw_rect(fitz.Rect(30, y_ab + 51, 74, y_ab + 71), color=border_col, fill=(1, 1, 1), width=0.8)
            page1.insert_text((44, y_ab + 65), str(sc_val), fontsize=10.5, fontname="hebo", color=text_dark)

            is_save_prof = bool(saves_prof.get(ab, False))
            if is_save_prof:
                save_val = mods[ab] + prof
                mark = "[X]"
            else:
                save_val = mods[ab]
                mark = "[ ]"
            save_str = Character55eRules.format_mod(save_val)
            page1.insert_text((88, y_ab + 34), "SALVACIÓN", fontsize=7, fontname="hebo", color=text_muted)
            page1.insert_text((88, y_ab + 52), f"{mark}  {save_str}", fontsize=11, fontname="hebo", color=text_dark)

            y_ab += 82

        page1.draw_rect(fitz.Rect(22, 598, 182, 660), color=border_col, fill=box_bg, width=1.0)
        if stats.get("heroic_inspiration"):
            insp_mark = "[X]"
        else:
            insp_mark = "[ ]"
        page1.insert_text((30, 613), f"{insp_mark} {insp_label}", fontsize=8.5, fontname="hebo", color=text_dark)
        page1.insert_text((30, 626), f"{feat_label}:", fontsize=7, fontname="hebo", color=text_muted)
        origin_txt = str(stats.get("origin_feat", "-"))
        page1.insert_textbox(fitz.Rect(28, 629, 178, 658), origin_txt, fontsize=6.5, fontname="helv", color=text_dark)

        skill_totals = {}
        skill_lines = []
        for sk_name, ab in SKILLS_55E:
            base = mods.get(ab, 0)
            if sk_name in exp_set:
                tot = base + (prof * 2)
                pref = "[**]"
            elif skills_prof.get(sk_name):
                tot = base + prof
                pref = "[X]"
            elif jack:
                tot = base + (prof // 2)
                pref = "[~]"
            else:
                tot = base
                pref = "[ ]"

            if "Taumaturgo" in prog_order and sk_name in ("Conocimiento Arcano", "Religión"):
                tot += max(1, mods.get("Sabiduría", 0))
            elif "Naturalista" in prog_order and sk_name in ("Conocimiento Arcano", "Naturaleza"):
                tot += max(1, mods.get("Sabiduría", 0))

            skill_totals[sk_name] = tot
            skill_lines.append((pref, sk_name, ab[:3].upper(), Character55eRules.format_mod(tot)))

        page1.draw_rect(fitz.Rect(22, 664, 182, 768), color=border_col, fill=box_bg, width=1.0)
        page1.draw_rect(fitz.Rect(22, 664, 182, 680), color=border_col, fill=header_bg, width=0.5)
        page1.insert_text((30, 675), "SENTIDOS PASIVOS", fontsize=8, fontname="hebo", color=(1, 1, 1))
        page1.insert_text((30, 698), f"Percepción Pasiva: {10 + skill_totals.get('Percepción', 0)}", fontsize=9.5, fontname="hebo", color=text_dark)
        page1.insert_text((30, 718), f"Perspicacia Pasiva: {10 + skill_totals.get('Perspicacia', 0)}", fontsize=9.5, fontname="helv", color=text_dark)
        page1.insert_text((30, 738), f"Investigación Pasiva: {10 + skill_totals.get('Investigación', 0)}", fontsize=9.5, fontname="helv", color=text_dark)
        langs_str = ", ".join(stats.get("language_choices", ["Común"]))
        page1.insert_textbox(fitz.Rect(30, 746, 176, 766), f"Idiomas: {langs_str}", fontsize=7.5, fontname="helv", color=text_muted)

        speed_txt = Character55eRules.format_distance_for_edition(str(stats.get("speed", "9 m")), edition)
        combat_boxes = [
            ("CA", str(stats.get("armor_class", 10)), 194, 260),
            ("INICIATIVA", Character55eRules.format_mod(mods.get("Destreza", 0)), 266, 332),
            ("VELOCIDAD", speed_txt, 338, 404),
        ]
        for lbl, val, x0, x1 in combat_boxes:
            page1.draw_rect(fitz.Rect(x0, 102, x1, 154), color=border_col, fill=box_bg, width=1.0)
            page1.insert_textbox(fitz.Rect(x0 + 2, 106, x1 - 2, 124), lbl, fontsize=7, fontname="hebo", align=1, color=text_muted)
            page1.insert_textbox(fitz.Rect(x0 + 2, 124, x1 - 2, 152), val, fontsize=13.5, fontname="hebo", align=1, color=accent_col)

        page1.draw_rect(fitz.Rect(194, 160, 404, 258), color=border_col, fill=box_bg, width=1.0)
        page1.draw_rect(fitz.Rect(194, 160, 404, 176), color=border_col, fill=accent_col, width=0.5)
        page1.insert_text((202, 171), "PUNTOS DE GOLPE Y SUPERVIVENCIA", fontsize=8, fontname="hebo", color=(1, 1, 1))
        page1.insert_text((202, 194), f"PG Máximos: {stats.get('hp_max', 10)}", fontsize=9.5, fontname="hebo", color=text_dark)
        page1.insert_text((312, 194), f"PG Actuales: {stats.get('hp_current', 10)}", fontsize=9.5, fontname="hebo", color=text_dark)
        page1.insert_text((202, 212), f"PG Temporales: {stats.get('hp_temp', 0)}", fontsize=9, fontname="helv", color=text_dark)

        classes_cat = Character55eRules.get_classes_catalog(edition)
        hd_faces = classes_cat.get(char_class, {}).get("hit_die", 8)
        hd_curr = stats.get("hit_dice_current", level)
        page1.insert_text((312, 212), f"Dados Golpe: {hd_curr}/{level} d{hd_faces}", fontsize=9, fontname="helv", color=text_dark)
        page1.insert_text((202, 234), "Salvaciones contra Muerte:", fontsize=7.5, fontname="hebo", color=text_muted)
        page1.insert_text((202, 248), "Éxitos: ( ) ( ) ( )     Fallos: ( ) ( ) ( )", fontsize=8.5, fontname="helv", color=text_dark)

        page1.draw_rect(fitz.Rect(194, 264, 404, 304), color=border_col, fill=box_bg, width=1.0)
        if stats.get("equipped_shield"):
            shield_str = "Sí (+2 CA)"
        else:
            shield_str = "No"
        page1.insert_text((202, 278), f"Armadura: {stats.get('equipped_armor', 'Sin Armadura')}", fontsize=8.5, fontname="hebo", color=text_dark)
        page1.insert_text((202, 294), f"Escudo: {shield_str}   |   Bono Mágico CA: +{stats.get('armor_magic_bonus', 0)}", fontsize=8, fontname="helv", color=text_muted)

        page1.draw_rect(fitz.Rect(194, 310, 404, 466), color=border_col, fill=box_bg, width=1.0)
        page1.draw_rect(fitz.Rect(194, 310, 404, 326), color=border_col, fill=header_bg, width=0.5)
        page1.insert_text((202, 321), "ATAQUES Y ARMAS EQUIPADAS", fontsize=8, fontname="hebo", color=(1, 1, 1))

        y_w = 334
        for w in stats.get("weapons", []):
            w_name = w.get("name", "")
            if not w_name or w_name.startswith("--"):
                continue
            ab_u = w.get("ability", "Fuerza")
            ab_m = mods.get(ab_u, 0)
            atk_str = Character55eRules.format_mod(ab_m + prof)
            dmg_mod_str = Character55eRules.format_mod(ab_m)
            dmg_txt = Character55eRules.format_distance_for_edition(w.get("damage", ""), edition)

            page1.insert_text((202, y_w + 10), f"{w_name}   (Atq: {atk_str})", fontsize=9, fontname="hebo", color=text_dark)
            page1.insert_text((202, y_w + 22), f"Daño: {dmg_txt} ({dmg_mod_str})", fontsize=8, fontname="helv", color=text_muted)
            if edition == "5.5e":
                m_name = w.get("mastery", "Ninguna")
                if m_name and m_name != "Ninguna":
                    page1.insert_text((202, y_w + 33), f"Maestría: {m_name}", fontsize=7.5, fontname="hebo", color=accent_col)
            y_w += 42

        page1.draw_rect(fitz.Rect(194, 472, 404, 768), color=border_col, fill=box_bg, width=1.0)
        page1.draw_rect(fitz.Rect(194, 472, 404, 488), color=border_col, fill=header_bg, width=0.5)
        page1.insert_text((202, 483), "RASGOS Y ATRIBUTOS", fontsize=8, fontname="hebo", color=(1, 1, 1))

        feats = Character55eRules.get_features_up_to_level(
            species, char_class, subclass, level, edition, stats.get("species_lineage", "")
        )
        feat_lines = []
        for t, d in feats:
            feat_lines.append(f"- {t}: {d}")
        page1.insert_textbox(
            fitz.Rect(200, 492, 398, 764),
            "\n".join(feat_lines),
            fontsize=7.2, fontname="helv", color=text_dark
        )

        portrait_rect = fitz.Rect(416, 102, 590, 252)
        page1.draw_rect(portrait_rect, color=border_col, fill=box_bg, width=1.0)
        portrait_b64 = stats.get("portrait_b64", "")
        if portrait_b64:
            try:
                img_bytes = base64.b64decode(portrait_b64)
                inner_rect = fitz.Rect(420, 106, 586, 248)
                page1.insert_image(inner_rect, stream=img_bytes, keep_proportion=True)
            except Exception:
                page1.insert_textbox(portrait_rect, "\n\n\nSin Retrato", fontsize=9, fontname="helv", align=1, color=text_muted)
        else:
            page1.insert_textbox(portrait_rect, "\n\n\nRetrato del Personaje", fontsize=9, fontname="helv", align=1, color=text_muted)

        page1.draw_rect(fitz.Rect(416, 258, 590, 658), color=border_col, fill=box_bg, width=1.0)
        page1.draw_rect(fitz.Rect(416, 258, 590, 274), color=border_col, fill=header_bg, width=0.5)
        page1.insert_text((424, 269), "HABILIDADES (SKILLS)", fontsize=8, fontname="hebo", color=(1, 1, 1))

        y_sk = 288
        for pref, sk_name, ab_short, bonus_str in skill_lines:
            page1.insert_text((422, y_sk), f"{pref} {sk_name} ({ab_short})", fontsize=7.8, fontname="helv", color=text_dark)
            page1.insert_text((562, y_sk), bonus_str, fontsize=8.2, fontname="hebo", color=accent_col)
            y_sk += 20.5

        page1.draw_rect(fitz.Rect(416, 664, 590, 768), color=border_col, fill=box_bg, width=1.0)
        page1.draw_rect(fitz.Rect(416, 664, 590, 680), color=border_col, fill=accent_col, width=0.5)
        page1.insert_text((424, 675), "MONEDERO Y TESORO", fontsize=8, fontname="hebo", color=(1, 1, 1))
        coins = stats.get("coins", {"cp": 0, "sp": 0, "gp": 0})
        page1.insert_text((426, 704), f"Oro (PO): {coins.get('gp', 0)}", fontsize=10, fontname="hebo", color=text_dark)
        page1.insert_text((426, 724), f"Plata (PP): {coins.get('sp', 0)}", fontsize=10, fontname="helv", color=text_dark)
        page1.insert_text((426, 744), f"Cobre (PC): {coins.get('cp', 0)}", fontsize=10, fontname="helv", color=text_dark)

        page2 = doc.new_page(width=612, height=792)
        page2.draw_rect(fitz.Rect(22, 18, 590, 60), color=border_col, fill=header_bg, width=1.2)
        if logo_bytes:
            page2.insert_image(fitz.Rect(28, 22, 62, 56), stream=logo_bytes, keep_proportion=True)
            p2_title_x = 70
        else:
            p2_title_x = 34
        page2.insert_text((p2_title_x, 44), f"{name.upper()} - CONJUROS, EQUIPO Y NOTAS ({edition})", fontsize=12.5, fontname="hebo", color=(1, 1, 1))

        page2.draw_rect(fitz.Rect(22, 72, 590, 310), color=border_col, fill=box_bg, width=1.0)
        page2.draw_rect(fitz.Rect(22, 72, 590, 88), color=border_col, fill=accent_col, width=0.5)
        page2.insert_text((30, 83), "LANZAMIENTO DE CONJUROS", fontsize=8.5, fontname="hebo", color=(1, 1, 1))

        slots_dict = Character55eRules.get_spell_slots_by_level(char_class, subclass, level, edition)
        always_prep = Character55eRules.get_always_prepared_spells(char_class, subclass, level, edition)
        sp_abil = classes_cat.get(char_class, {}).get("spell_ability") or "Carisma"
        sp_mod = mods.get(sp_abil, 0)

        spell_lines = []
        if slots_dict:
            slots_str = "  |  ".join([f"Niv.{k}: {v}" for k, v in sorted(slots_dict.items())])
            spell_lines.append(f"Aptitud Mágica: {sp_abil}   |   CD Salvación: {8 + prof + sp_mod}   |   Ataque Mágico: +{prof + sp_mod}")
            spell_lines.append(f"Espacios de Conjuro: {slots_str}")
        else:
            spell_lines.append("Esta clase / nivel no dispone de espacios de conjuro.")

        cantrips = stats.get("selected_cantrips", [])
        if cantrips:
            spell_lines.append(f"\nTrucos (Cantrips): {', '.join(cantrips)}")
        if always_prep:
            spell_lines.append(f"\nSiempre Preparados: {', '.join(always_prep)}")
        prep_spells = stats.get("selected_spells", [])
        if prep_spells:
            spell_lines.append(f"\nConjuros Preparados / Conocidos:\n{', '.join(prep_spells)}")

        page2.insert_textbox(fitz.Rect(30, 94, 582, 304), "\n".join(spell_lines), fontsize=8.5, fontname="helv", color=text_dark)

        if edition == "5e":
            w_mult = 2.0
            w_unit = "lb"
        else:
            w_mult = 1.0
            w_unit = "kg"

        page2.draw_rect(fitz.Rect(22, 320, 302, 565), color=border_col, fill=box_bg, width=1.0)
        page2.draw_rect(fitz.Rect(22, 320, 302, 336), color=border_col, fill=header_bg, width=0.5)
        max_char_cap = Character55eRules.get_carrying_capacity(int(scores.get("Fuerza", 10)), species, edition)
        inv_char_lines = []
        total_char_kg = 0.0
        for it in stats.get("inventory_char", []):
            item_kg = Character55eRules.calculate_item_tree_weight(it)
            total_char_kg += item_kg
            disp_w = round(item_kg * w_mult, 2)
            inv_char_lines.append(f"- {it['name']} (x{it.get('qty', 1)}) - {disp_w} {w_unit}")
            for sub in it.get("contents", []):
                sub_w = round(float(sub.get("qty", 1)) * float(sub.get("weight_kg", 0.0)) * w_mult, 2)
                inv_char_lines.append(f"    - {sub['name']} (x{sub.get('qty', 1)}) - {sub_w} {w_unit}")

        tot_char_disp = round(total_char_kg * w_mult, 1)
        page2.insert_text((30, 331), f"EQUIPO ({tot_char_disp} / {max_char_cap} {w_unit})", fontsize=8, fontname="hebo", color=(1, 1, 1))
        page2.insert_textbox(fitz.Rect(28, 342, 296, 560), "\n".join(inv_char_lines) or "Sin objetos registrados.", fontsize=7.8, fontname="helv", color=text_dark)

        page2.draw_rect(fitz.Rect(310, 320, 590, 565), color=border_col, fill=box_bg, width=1.0)
        page2.draw_rect(fitz.Rect(310, 320, 590, 336), color=border_col, fill=header_bg, width=0.5)
        mount_type = stats.get("mount_type", "Sin Montura")
        page2.insert_text((318, 331), f"MONTURA ({mount_type[:22]}) Y SINTONIZACIÓN", fontsize=7.5, fontname="hebo", color=(1, 1, 1))

        right_inv_lines = []
        attuned = [x for x in stats.get("attuned_items", []) if x]
        if attuned:
            right_inv_lines.append("Objetos Sintonizados:")
            for a_it in attuned:
                right_inv_lines.append(f"  * {a_it}")
            right_inv_lines.append("")

        right_inv_lines.append("Carga en Montura:")
        mount_items = stats.get("inventory_mount", [])
        if not mount_items:
            right_inv_lines.append("  Sin objetos en la montura.")
        else:
            for it in mount_items:
                item_kg = Character55eRules.calculate_item_tree_weight(it)
                disp_w = round(item_kg * w_mult, 2)
                right_inv_lines.append(f"- {it['name']} (x{it.get('qty', 1)}) - {disp_w} {w_unit}")

        page2.insert_textbox(fitz.Rect(316, 342, 584, 560), "\n".join(right_inv_lines), fontsize=7.8, fontname="helv", color=text_dark)

        page2.draw_rect(fitz.Rect(22, 575, 590, 768), color=border_col, fill=box_bg, width=1.0)
        page2.draw_rect(fitz.Rect(22, 575, 590, 591), color=border_col, fill=header_bg, width=0.5)
        page2.insert_text((30, 586), "NOTAS DE AVENTURA, HISTORIA Y ALIADOS", fontsize=8, fontname="hebo", color=(1, 1, 1))
        notes_text = stats.get("adventure_notes", "") or "Sin notas registradas."
        page2.insert_textbox(fitz.Rect(30, 597, 582, 762), notes_text, fontsize=8.2, fontname="helv", color=text_dark)

        doc.save(output_path)
        doc.close()

    @staticmethod
    def _get_logo_bytes():
        if hasattr(sys, "_MEIPASS"):
            base_dir = Path(sys._MEIPASS)
        else:
            base_dir = Path(__file__).resolve().parent.parent

        png_path = base_dir / "dnd55_logo.png"
        ico_path = base_dir / "dnd55_logo.ico"

        if png_path.exists():
            logo_path = png_path
        elif ico_path.exists():
            logo_path = ico_path
        else:
            return None

        try:
            img = Image.open(logo_path).convert("RGBA")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
        except Exception:
            return None