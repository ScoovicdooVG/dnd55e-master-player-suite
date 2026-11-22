import re
import io
import pymupdf as fitz
from PIL import Image
from pathlib import Path
from database.db_manager import DatabaseManager


class PDFEngine:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def index_pdf(self, pdf_path: str, title: str, category: str, progress_callback=None):
        path_obj = Path(pdf_path).resolve()
        if not path_obj.exists():
            raise FileNotFoundError(f"No se encontró el archivo: {pdf_path}")

        doc = fitz.open(str(path_obj))
        total_pages = len(doc)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM manuals WHERE file_path = ?", (str(path_obj),))
            existing = cursor.fetchone()
            if existing:
                old_id = existing["id"]
                cursor.execute("DELETE FROM manuals WHERE id = ?", (old_id,))
                cursor.execute("DELETE FROM manual_toc WHERE manual_id = ?", (old_id,))
                cursor.execute("DELETE FROM pdf_search_index WHERE manual_id = ?", (old_id,))

            cursor.execute("""
                INSERT INTO manuals (title, category, file_path, total_pages)
                VALUES (?, ?, ?, ?)
            """, (title, category, str(path_obj), total_pages))
            manual_id = cursor.lastrowid

            toc = doc.get_toc()
            if toc:
                toc_rows = [(manual_id, item[0], item[1], item[2]) for item in toc]
                cursor.executemany("""
                    INSERT INTO manual_toc (manual_id, level, heading, page_number)
                    VALUES (?, ?, ?, ?)
                """, toc_rows)

            batch_pages = []
            for page_idx in range(total_pages):
                page = doc.load_page(page_idx)
                text = page.get_text("text").strip()
                if text:
                    batch_pages.append((manual_id, title, page_idx + 1, text))

                if progress_callback and (page_idx % 10 == 0 or page_idx == total_pages - 1):
                    progress_callback(page_idx + 1, total_pages)

            cursor.executemany("""
                INSERT INTO pdf_search_index (manual_id, manual_title, page_number, content)
                VALUES (?, ?, ?, ?)
            """, batch_pages)
            conn.commit()

        doc.close()
        return manual_id

    def render_page_as_pil(self, manual_id: int, page_number: int, zoom: float = 1.5) -> Image.Image:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM manuals WHERE id = ?", (manual_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Manual no encontrado en la base de datos.")
            file_path = row["file_path"]

        doc = fitz.open(file_path)
        if page_number < 1 or page_number > len(doc):
            doc.close()
            raise ValueError("Número de página fuera de rango.")

        page = doc.load_page(page_number - 1)
        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        img_bytes = pix.tobytes("png")
        doc.close()
        return Image.open(io.BytesIO(img_bytes))

    # =========================================================================
    # EXTRACTOR AUTOMÁTICO DE CONJUROS DESDE EL PDF (PHB 2024 ESPAÑOL)
    # =========================================================================
    def extract_spells_from_manual(self, manual_id: int) -> int:
        """
        Analiza las páginas indexadas del Manual del Jugador en español
        detectando tanto las listas por clase como las descripciones del Capítulo 7.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT page_number, content FROM pdf_search_index
                WHERE manual_id = ? ORDER BY CAST(page_number AS INTEGER) ASC
            """, (manual_id,))
            pages = cursor.fetchall()

        schools_map = {
            "abjuracion": "Abjuración", "abjuración": "Abjuración",
            "adivinacion": "Adivinación", "adivinación": "Adivinación",
            "conjuracion": "Conjuración", "conjuración": "Conjuración",
            "encantamiento": "Encantamiento",
            "evocacion": "Evocación", "evocación": "Evocación",
            "ilusionismo": "Ilusionismo", "ilusion": "Ilusión", "ilusión": "Ilusión",
            "nigromancia": "Nigromancia",
            "transmutacion": "Transmutación", "transmutación": "Transmutación"
        }
        class_map = {
            "bardo": "Bardo", "brujo": "Brujo", "clerigo": "Clérigo", "clérigo": "Clérigo",
            "druida": "Druida", "explorador": "Explorador", "hechicero": "Hechicero",
            "mago": "Mago", "paladin": "Paladín", "paladín": "Paladín"
        }

        extracted = {}

        # Patrón 1: Bloques completos del Capítulo 7 (Descripciones de conjuros)
        # Ejemplo:
        # BOLA DE FUEGO
        # Conjuro de nivel 3 de evocación (hechicero, mago)  o  Evocación de nivel 3 (hechicero, mago)
        header_regex = re.compile(
            r"(?P<name>[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s/':,-]{2,45})\n+"
            r"(?:(?P<truco>Truco)\s+de\s+(?P<school1>[a-záéíóúñ]+)|"
            r"(?:Conjuro\s+de\s+)?[Nn]ivel\s+(?P<lvl>[1-9])\s+de\s+(?P<school2>[a-záéíóúñ]+)|"
            r"(?P<school3>[A-ZÁÉÍÓÚÑa-záéíóúñ]+)\s+de\s+nivel\s+(?P<lvl2>[1-9]))"
            r"\s*\((?P<classes>[^)]+)\)",
            re.MULTILINE
        )

        for row in pages:
            pno = int(row["page_number"])
            text = row["content"]

            for match in header_regex.finditer(text):
                raw_name = match.group("name").strip().title()
                if len(raw_name) < 3 or "Capítulo" in raw_name or "Conjuros De" in raw_name:
                    continue

                if match.group("truco"):
                    lvl = 0
                    raw_sch = match.group("school1").lower()
                elif match.group("lvl"):
                    lvl = int(match.group("lvl"))
                    raw_sch = match.group("school2").lower()
                else:
                    lvl = int(match.group("lvl2"))
                    raw_sch = match.group("school3").lower()

                school = schools_map.get(raw_sch, raw_sch.capitalize())
                raw_classes = match.group("classes").lower()
                cls_list = []
                for k, v in class_map.items():
                    if k in raw_classes and v not in cls_list:
                        cls_list.append(v)
                if not cls_list:
                    cls_list = ["Mago", "Hechicero", "Bardo", "Clérigo", "Druida", "Brujo"]

                # Extraer metadatos posteriores al encabezado (hasta 700 caracteres)
                tail = text[match.end():match.end() + 900]
                c_time = self._extract_line_field(tail, "Tiempo de lanzamiento:")
                rng = self._extract_line_field(tail, "Alcance:")
                comp = self._extract_line_field(tail, "Componentes:")
                dur = self._extract_line_field(tail, "Duración:")

                desc_lines = []
                for line in tail.splitlines():
                    l_str = line.strip()
                    if not l_str:
                        continue
                    if any(l_str.startswith(prefix) for prefix in ("Tiempo de lanzamiento:", "Alcance:", "Componentes:", "Duración:")):
                        continue
                    if l_str.isupper() and len(l_str) > 4:
                        break
                    desc_lines.append(l_str)
                desc = " ".join(desc_lines)[:500]

                extracted[raw_name] = {
                    "name": raw_name,
                    "level": lvl,
                    "school": school,
                    "classes": cls_list,
                    "casting_time": c_time,
                    "range_str": rng,
                    "components": comp,
                    "duration": dur,
                    "description": desc,
                    "page_number": pno
                }

        # Patrón 2: Listas de Conjuros de Clase del Capítulo 3 (Págs. 62-160) para asegurar que no falte ninguno
        current_cls = None
        current_lvl = 0
        list_cls_regex = re.compile(r"LISTA DE CONJUROS DE (BARDO|BRUJO|CLÉRIGO|DRUIDA|EXPLORADOR|HECHICERO|MAGO|PALADÍN)", re.IGNORECASE)
        lvl_banner_regex = re.compile(r"TRUCOS\s*\(CONJUROS|CONJUROS DE [A-ZÁÉÍÓÚÑ]+ DE NIVEL\s+([1-9])", re.IGNORECASE)

        for row in pages:
            pno = int(row["page_number"])
            text = row["content"]
            cls_m = list_cls_regex.search(text)
            if cls_m:
                c_raw = cls_m.group(1).lower()
                current_cls = class_map.get(c_raw, "Mago")

            if not current_cls or pno > 175:
                continue

            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            for i, ln in enumerate(lines):
                if "TRUCOS (" in ln.upper():
                    current_lvl = 0
                    continue
                m_lvl = re.search(r"CONJUROS DE .+ DE NIVEL\s+([1-9])", ln.upper())
                if m_lvl:
                    current_lvl = int(m_lvl.group(1))
                    continue

                # Si una línea coincide exactamente con una Escuela Mágica, la línea anterior es el nombre del conjuro
                ln_low = ln.lower()
                if ln_low in schools_map and i > 0:
                    cand_name = lines[i - 1].strip()
                    if (2 < len(cand_name) < 42
                            and not cand_name.isupper()
                            and cand_name.lower() not in schools_map
                            and not any(w in cand_name.lower() for w in ("conjuro", "escuela", "especial", "nivel", "capítulo"))):
                        clean_name = cand_name[0].upper() + cand_name[1:]
                        sch_proper = schools_map[ln_low]
                        if clean_name in extracted:
                            if current_cls not in extracted[clean_name]["classes"]:
                                extracted[clean_name]["classes"].append(current_cls)
                        else:
                            extracted[clean_name] = {
                                "name": clean_name,
                                "level": current_lvl,
                                "school": sch_proper,
                                "classes": [current_cls],
                                "casting_time": "1 acción",
                                "range_str": "Ver PDF",
                                "components": "V, S",
                                "duration": "Instantánea",
                                "description": f"Registrado desde la Lista de Conjuros de {current_cls} (Pág. {pno}). Usa '📖 PDF' para ver el detalle.",
                                "page_number": pno
                            }

        if not extracted:
            return 0
        return self.db.save_extracted_spells_batch(list(extracted.values()))

   # =========================================================================
    # EXTRACTOR AUTOMÁTICO CALIBRADO PARA EL MANUAL DE MONSTRUOS 2024 (ESPAÑOL)
    # =========================================================================
    def extract_monsters_from_manual(self, manual_id: int) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT page_number, content FROM pdf_search_index
                WHERE manual_id = ? ORDER BY CAST(page_number AS INTEGER) ASC
            """, (manual_id,))
            pages = cursor.fetchall()

        if not pages:
            return 0

        active_edition = self.db.get_active_edition()
        existing_names = {m["name"].lower() for m in self.db.get_all_monsters(active_edition)}
        count_saved = 0

        types_group = (
            r"(?:Aberración|Autómata|Constructo|Bestia|Celestial|Cieno|Dragón|"
            r"Elemental|Feérico|Gigante|Humanoide|Infernal|Monstruosidad|"
            r"Muerto viviente|No muerto|Planta|Enjambre)"
        )
        sizes_group = r"(?:Diminut[oa]|Pequeñ[oa]|Median[oa]|Grande|Enorme|Gargantuesc[oa])"

        type_pattern = re.compile(
            rf"(?:{types_group}(?:\s*\([^)]+\))?[\s,]+{sizes_group}|"
            rf"{sizes_group}(?:\s+o\s+{sizes_group})?[\s,]+{types_group})",
            re.IGNORECASE
        )

        for row in pages:
            pno = int(row["page_number"])
            text = row["content"]

            has_ac = re.search(r"(Clase de armadura|\bCA\b)\s*[:.]?", text, re.IGNORECASE)
            has_hp = re.search(r"(Puntos de golpe|\bPG\b)\s*[:.]?", text, re.IGNORECASE)
            if not has_ac or not has_hp:
                continue

            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            num_lines = len(lines)

            match_indices = []
            for idx, ln in enumerate(lines):
                if type_pattern.search(ln) and len(ln) < 95:
                    match_indices.append(idx)

            for pos, idx in enumerate(match_indices):
                ln = lines[idx]

                start_slice = max(0, idx - 4)
                if pos + 1 < len(match_indices):
                    end_idx = max(idx + 5, match_indices[pos + 1] - 3)
                else:
                    end_idx = min(num_lines, idx + 80)

                block_slice = "\n".join(lines[start_slice:end_idx])

                if not re.search(r"(Clase de armadura|\bCA\b)", block_slice, re.IGNORECASE):
                    continue

                name_parts = []
                back = idx - 1
                steps = 0
                while back >= 0 and len(name_parts) < 2 and steps < 6:
                    cand = lines[back].strip()
                    cand_upper = cand.upper()
                    steps += 1
                    back -= 1

                    if len(cand) <= 2 or cand.isdigit():
                        continue

                    if any(cand_upper.startswith(p) for p in ("CA:", "CA ", "PG:", "PG ", "INICIATIVA:", "VELOCIDAD:", "MOD.", "SALV.")):
                        continue

                    is_stop = any(k in cand_upper for k in (
                        "VD:", "DESAFÍO", "CLASE DE ARMADURA", "PUNTOS DE GOLPE",
                        "FUE", "DES", "CON", "ÍNDICE", "MANUAL", "MONSTRUOS",
                        "CRÉDITOS", "VARIANTE:", "ACCIONES", "HÁBITAT:", "TESORO:"
                    ))
                    if is_stop:
                        break

                    if len(cand) < 48:
                        name_parts.insert(0, cand)
                        if cand.isupper():
                            break
                    else:
                        break

                if not name_parts:
                    continue

                raw_name = " ".join(name_parts).strip().title()
                if len(raw_name) < 3 or raw_name.lower() in existing_names:
                    continue
                if any(bad in raw_name.lower() for bad in ("capítulo", "apéndice", "tabla", "contenido", "introducción")):
                    continue

                ac_m = re.search(r"(?:Clase de armadura|\bCA\b)\s*[:.]?\s*([^\n]+)", block_slice, re.IGNORECASE)
                if ac_m:
                    ac_str = ac_m.group(1).strip()[:45]
                else:
                    ac_str = "12"

                hp_m = re.search(r"(?:Puntos de golpe|\bPG\b)\s*[:.]?\s*([^\n]+)", block_slice, re.IGNORECASE)
                if hp_m:
                    hp_str = hp_m.group(1).replace("$", "").strip()[:40]
                else:
                    hp_str = "20 (4d8)"

                spd_m = re.search(r"Velocidad\s*[:.]?\s*([^\n]+)", block_slice, re.IGNORECASE)
                if spd_m:
                    spd_str = spd_m.group(1).strip()[:45]
                else:
                    if active_edition == "5e":
                        spd_str = "30 pies"
                    else:
                        spd_str = "9 m"

                cr_m = re.search(r"(?:Valor de desafío|Desafío|\bVD\b)\s*[:.]?\s*\$?([0-9]+/[0-9]+|[0-9]+)\$?", block_slice, re.IGNORECASE)
                if cr_m:
                    cr_str = cr_m.group(1).strip()
                else:
                    cr_str = "1"

                scores = self._parse_all_ability_scores(block_slice)
                dex_mod = (scores["Destreza"] - 10) // 2

                init_m = re.search(r"Iniciativa\s*[:.]?\s*([+-]?\d+)", block_slice, re.IGNORECASE)
                if init_m:
                    init_bonus = int(init_m.group(1))
                else:
                    init_bonus = dex_mod

                senses_m = re.search(r"Sentidos\s*[:.]?\s*([^\n]+)", block_slice, re.IGNORECASE)
                if senses_m:
                    senses_str = senses_m.group(1).strip()
                else:
                    senses_str = "Percepción pasiva 10"

                langs_m = re.search(r"Idiomas\s*[:.]?\s*([^\n]+)", block_slice, re.IGNORECASE)
                if langs_m:
                    langs_str = langs_m.group(1).strip()
                else:
                    langs_str = "—"

                traits_text, actions_text, bonus_text = self._split_monster_sections(block_slice, pno)

                monster_payload = {
                    "id": None,
                    "name": raw_name,
                    "size_type_alignment": ln[:70],
                    "armor_class": ac_str,
                    "hit_points": hp_str,
                    "speed": spd_str,
                    "initiative_bonus": init_bonus,
                    "challenge_rating": cr_str,
                    "statblock": {
                        "edition": active_edition,
                        "scores": scores,
                        "senses": senses_str,
                        "languages": langs_str,
                        "traits": traits_text,
                        "actions": actions_text,
                        "bonus_reactions": bonus_text
                    }
                }
                self.db.save_monster(monster_payload)
                existing_names.add(raw_name.lower())
                count_saved += 1

        return count_saved

    def _parse_all_ability_scores(self, block_text: str) -> dict:
        keys = ["Fuerza", "Destreza", "Constitución", "Inteligencia", "Sabiduría", "Carisma"]
        abbrs = ["FUE", "DES", "CON", "INT", "SAB", "CAR"]

        scores = {}
        found_inline = 0
        for ab_full, abbr in zip(keys, abbrs):
            m = re.search(rf"\b{abbr}\b[\s|:\n]*([0-9]{{1,2}})(?![0-9])", block_text)
            if m:
                val = int(m.group(1))
                if 1 <= val <= 30:
                    scores[ab_full] = val
                    found_inline += 1
                    continue
            scores[ab_full] = 10

        if found_inline >= 4:
            return scores

        fue_pos = block_text.upper().find("FUE")
        if fue_pos != -1:
            sub = block_text[fue_pos:fue_pos + 240]
            matches = re.findall(r"\b([0-9]{1,2})\s*\(\s*[+-−]?\d+\s*\)", sub)
            if len(matches) >= 6:
                for i, ab_full in enumerate(keys):
                    val = int(matches[i])
                    if 1 <= val <= 30:
                        scores[ab_full] = val
                return scores

        return scores

    def _extract_multiline_field(self, text: str, prefix: str) -> str:
        stop_prefixes = (
            "Habilidades:", "Resistencias:", "Vulnerabilidades:", "Inmunidades:",
            "Equipo:", "Sentidos:", "Idiomas:", "VD:", "ATRIBUTOS", "ACCIONES"
        )
        lines = text.splitlines()
        collecting = False
        collected = []
        for ln in lines:
            s = ln.strip()
            if s.startswith(prefix):
                collecting = True
                collected.append(s[len(prefix):].strip())
            elif collecting:
                if any(s.startswith(sp) for sp in stop_prefixes) or s.isupper():
                    break
                collected.append(s)
        return " ".join(collected).strip()

    def _extract_section_between(self, text: str, start_headers: list, stop_headers: list) -> str:
        lines = text.splitlines()
        collecting = False
        out = []
        for ln in lines:
            s = ln.strip()
            if not collecting:
                if s in start_headers:
                    collecting = True
                continue
            else:
                if s in stop_headers:
                    break
                out.append(s)
        return "\n".join(out).strip()

    def _extract_line_field(self, text: str, prefix: str) -> str:
        for ln in text.splitlines():
            if ln.strip().startswith(prefix):
                return ln.strip().replace(prefix, "").strip()
        return ""

    def _split_monster_sections(self, block_text: str, pno: int) -> tuple:
        clean_text = block_text.replace("$", "")
        attr_match = re.search(r"\n\s*ATRIBUTOS\s*\n", clean_text)
        act_match = re.search(r"\n\s*ACCIONES\s*\n", clean_text)
        bonus_match = re.search(r"\n\s*(ACCIONES ADICIONALES|REACCIONES|ACCIONES LEGENDARIAS)\s*\n", clean_text)
        cr_match = re.search(r"(?:Valor de desafío|Desafío|\bVD\b)\s*[:.]?[^\n]*\n", clean_text, re.IGNORECASE)

        if attr_match and act_match and act_match.start() > attr_match.end():
            traits_text = clean_text[attr_match.end():act_match.start()].strip()
        elif cr_match and act_match and act_match.start() > cr_match.end():
            traits_text = clean_text[cr_match.end():act_match.start()].strip()
        else:
            traits_text = f"Extraído del Manual (Pág. {pno})."

        if act_match:
            if bonus_match and bonus_match.start() > act_match.end():
                actions_text = clean_text[act_match.end():bonus_match.start()].strip()
                bonus_text = clean_text[bonus_match.start():].strip()
            else:
                actions_text = clean_text[act_match.end():].strip()
                bonus_text = ""
        else:
            actions_text = clean_text[:1500]
            bonus_text = ""

        return traits_text[:1500], actions_text[:1800], bonus_text[:1500]