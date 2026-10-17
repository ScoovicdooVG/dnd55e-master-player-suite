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
        """
        Extrae perfiles de monstruos del Manual de Monstruos de forma tolerante y flexible,
        detectando cualquier bloque que contenga CA, PG y VD/CR.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT page_number, content FROM pdf_search_index
                WHERE manual_id = ? ORDER BY CAST(page_number AS INTEGER) ASC
            """, (manual_id,))
            pages = cursor.fetchall()

        existing_names = {m["name"].lower() for m in self.db.get_all_monsters()}
        count_saved = 0

        # Patrón flexible para detectar perfiles en cualquier versión del Manual de Monstruos
        for row in pages:
            pno = int(row["page_number"])
            text = row["content"]

            # Buscar bloques que tengan indicadores de monstruo
            if not re.search(r"\bCA\b[:\s]", text, re.IGNORECASE) or not re.search(r"\b(PG|Puntos de golpe)\b[:\s]", text, re.IGNORECASE):
                continue

            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            num_lines = len(lines)

            for idx, ln in enumerate(lines):
                # Un perfil suele tener una línea con el Tipo de criatura y Tamaño (ej. "Monstruosidad Grande", "Infernal Mediano")
                is_type_line = re.search(
                    r"(Aberración|Autómata|Constructo|Bestia|Celestial|Cieno|Dragón|Elemental|Feérico|Fedrico|Gigante|Humanoide|Infernal|Monstruosidad|Muerto viviente|Planta)\s+"
                    r"(Diminuto|Diminuta|Pequeño|Pequeña|Mediano|Mediana|Grande|Enorme|Gargantuesco|Gargantuesca)",
                    ln, re.IGNORECASE
                )
                if not is_type_line:
                    continue

                # El nombre del monstruo suele estar en las 1 o 2 líneas anteriores en MAYÚSCULAS o título
                name_parts = []
                back = idx - 1
                while back >= 0 and len(name_parts) < 2:
                    cand = lines[back].strip()
                    if len(cand) >= 3 and not any(
                        k in cand.upper() for k in ("CA:", "PG:", "VD:", "FUE", "DES", "CON", "ÍNDICE", "MANUAL", "MONSTRUOS", "CRÉDITOS")
                    ):
                        name_parts.insert(0, cand)
                        back -= 1
                    else:
                        break

                if not name_parts and idx > 0:
                    cand = lines[idx - 1].strip()
                    if 2 < len(cand) < 45:
                        name_parts = [cand]

                raw_name = " ".join(name_parts).strip().title()
                if not raw_name or len(raw_name) < 3 or raw_name.lower() in existing_names:
                    continue
                if any(bad in raw_name.lower() for bad in ("capítulo", "apéndice", "tabla", "contenido", "introducción")):
                    continue

                block_slice = "\n".join(lines[idx:min(num_lines, idx + 40)])

                ac_m = re.search(r"(?:Clase de armadura|CA)\s*[:.]?\s*([^\n]+)", block_slice, re.IGNORECASE)
                ac_str = ac_m.group(1).strip()[:35] if ac_m else "14"

                hp_m = re.search(r"(?:Puntos de golpe|PG)\s*[:.]?\s*([^\n]+)", block_slice, re.IGNORECASE)
                hp_str = hp_m.group(1).replace("\n", " ").strip()[:35] if hp_m else "45 (6d8 + 18)"

                spd_m = re.search(r"Velocidad\s*[:.]?\s*([^\n]+)", block_slice, re.IGNORECASE)
                spd_str = spd_m.group(1).strip()[:40] if spd_m else "9 m"

                cr_m = re.search(r"(?:Desafío|VD|Valor de desafío)\s*[:.]?\s*([0-9]+/[0-9]+|[0-9]+)", block_slice, re.IGNORECASE)
                cr_str = cr_m.group(1).strip() if cr_m else "2"

                scores = {
                    "Fuerza": self._parse_ability_score(block_slice, "FUE"),
                    "Destreza": self._parse_ability_score(block_str := block_slice, "DES"),
                    "Constitución": self._parse_ability_score(block_slice, "CON"),
                    "Inteligencia": self._parse_ability_score(block_slice, "INT"),
                    "Sabiduría": self._parse_ability_score(block_slice, "SAB"),
                    "Carisma": self._parse_ability_score(block_slice, "CAR"),
                }
                dex_mod = (scores["Destreza"] - 10) // 2

                senses_m = re.search(r"Sentidos\s*[:.]?\s*([^\n]+)", block_slice, re.IGNORECASE)
                langs_m = re.search(r"Idiomas\s*[:.]?\s*([^\n]+)", block_slice, re.IGNORECASE)

                monster_payload = {
                    "id": None,
                    "name": raw_name,
                    "size_type_alignment": ln[:65],
                    "armor_class": ac_str,
                    "hit_points": hp_str,
                    "speed": spd_str,
                    "initiative_bonus": dex_mod,
                    "challenge_rating": cr_str,
                    "statblock": {
                        "scores": scores,
                        "senses": senses_m.group(1).strip() if senses_m else "Percepción pasiva 10",
                        "languages": langs_m.group(1).strip() if langs_m else "—",
                        "traits": f"Extraído del Manual de Monstruos (Pág. {pno}).",
                        "actions": block_slice[:1500],
                        "bonus_reactions": ""
                    }
                }
                self.db.save_monster(monster_payload)
                existing_names.add(raw_name.lower())
                count_saved += 1

        return count_saved

    def _parse_ability_score(self, block_text: str, abbr: str) -> int:
        # En el PDF de 2024 puede aparecer como "FUE 17 +3 +3" o con salto de línea "FUE\n17" o pegado "INT 6-2-2"
        m = re.search(rf"\b{abbr}\b[\s|:\n]*([0-9]{{1,2}})(?![0-9])", block_text)
        if m:
            val = int(m.group(1))
            if 1 <= val <= 30:
                return val
        return 10

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