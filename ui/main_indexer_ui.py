import base64
import io
import threading
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from database.db_manager import DatabaseManager
from pdf_engine.pdf_engine import PDFEngine


class PDFIndexerView(ctk.CTkFrame):
    def __init__(self, master, db: DatabaseManager, pdf_engine: PDFEngine):
        super().__init__(master, fg_color="transparent")
        self.db = db
        self.pdf_engine = pdf_engine

        self.current_manual_id = None
        self.current_page = 1
        self.current_zoom = 1.0

        self._build_ui()
        self._refresh_manuals_list()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(self, width=360, corner_radius=6)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)
        left_frame.grid_propagate(False)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(left_frame, text="Biblioteca de Manuales", font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, padx=15, pady=(12, 5), sticky="w"
        )

        self.btn_add_pdf = ctk.CTkButton(
            left_frame, text="+ Agregar Manual en PDF (PHB / DMG / MM)",
            command=self._select_and_index_pdf, fg_color="#8B2635", hover_color="#6E1D29"
        )
        self.btn_add_pdf.grid(row=1, column=0, padx=15, pady=8, sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(left_frame)
        self.progress_bar.grid(row=2, column=0, padx=15, pady=(0, 4), sticky="ew")
        self.progress_bar.set(0)

        self.lbl_status = ctk.CTkLabel(left_frame, text="Listo para buscar.", font=("Segoe UI", 12))
        self.lbl_status.grid(row=3, column=0, padx=15, pady=(0, 8), sticky="w")

        search_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        search_frame.grid(row=4, column=0, padx=15, pady=4, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)

        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Buscar conjuro, dote, regla...")
        self.entry_search.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        self.entry_search.bind("<Return>", lambda event: self._perform_search())

        ctk.CTkButton(search_frame, text="Buscar", width=65, command=self._perform_search).grid(row=0, column=1, padx=(0, 4))
        ctk.CTkButton(search_frame, text="Manuales", width=70, fg_color="#3B3B3B", command=self._reset_search).grid(row=0, column=2)

        self.results_scroll = ctk.CTkScrollableFrame(left_frame, label_text="Resultados / Manuales Cargados")
        self.results_scroll.grid(row=5, column=0, padx=15, pady=10, sticky="nsew")

        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, sticky="nsew", pady=5)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        nav_frame = ctk.CTkFrame(right_frame, height=48)
        nav_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkButton(nav_frame, text="◀ Anterior", width=85, command=lambda: self._change_page(-1)).pack(side="left", padx=6, pady=6)
        self.lbl_page_info = ctk.CTkLabel(nav_frame, text="Selecciona un manual", font=("Segoe UI", 14, "bold"))
        self.lbl_page_info.pack(side="left", padx=12)

        self.entry_goto = ctk.CTkEntry(nav_frame, width=55, placeholder_text="Pág.")
        self.entry_goto.pack(side="left", padx=(10, 4))
        self.entry_goto.bind("<Return>", lambda e: self._goto_page())
        ctk.CTkButton(nav_frame, text="Ir", width=40, command=self._goto_page).pack(side="left", padx=(0, 10))

        ctk.CTkButton(nav_frame, text="Siguiente ▶", width=85, command=lambda: self._change_page(1)).pack(side="right", padx=6, pady=6)
        ctk.CTkButton(nav_frame, text="Zoom +", width=58, fg_color="#3B3B3B", command=lambda: self._change_zoom(0.15)).pack(side="right", padx=3)
        self.lbl_zoom = ctk.CTkLabel(nav_frame, text="100%", width=45)
        self.lbl_zoom.pack(side="right", padx=2)
        ctk.CTkButton(nav_frame, text="Zoom -", width=58, fg_color="#3B3B3B", command=lambda: self._change_zoom(-0.15)).pack(side="right", padx=3)

        self.page_viewer_scroll = ctk.CTkScrollableFrame(right_frame)
        self.page_viewer_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.lbl_pdf_image = ctk.CTkLabel(self.page_viewer_scroll, text="")
        self.lbl_pdf_image.pack(expand=True, pady=10)

        ctk.CTkButton(
            nav_frame, text= "Proyectar en Celulares", width=165, fg_color="#6D28D9", hover_color="#5B21B6",
            command=self._project_current_pdf_page_to_mobile
        ).pack(side="right", padx=6)

    def _reset_search(self):
        self.entry_search.delete(0, "end")
        self._refresh_manuals_list()

    def _select_and_index_pdf(self):
        file_path = filedialog.askopenfilename(title="Selecciona un manual de D&D en PDF", filetypes=[("Archivos PDF", "*.pdf")])
        if not file_path:
            return
        dialog = ctk.CTkInputDialog(text="Nombre del Manual (ej. PHB 5.5e, DMG 5.5e, MM 5.5e):", title="Registrar Manual")
        title = dialog.get_input() or "Manual D&D"

        self.btn_add_pdf.configure(state="disabled")
        self.lbl_status.configure(text=f"Indexando {title}...")

        def run_indexing():
            try:
                def update_prog(current, total):
                    self.after(0, lambda c=current, t=total: self.progress_bar.set(c / t))
                    self.after(0, lambda c=current, t=total: self.lbl_status.configure(text=f"Indexando página {c} de {t}..."))

                self.pdf_engine.index_pdf(file_path, title, "Core", progress_callback=update_prog)
                self.after(0, lambda: self.lbl_status.configure(text=f"¡{title} indexado con éxito!"))
                self.after(0, self._refresh_manuals_list)
            except Exception as err:
                err_msg = str(err)
                self.after(0, lambda msg=err_msg: messagebox.showerror("Error al indexar PDF", msg))
                self.after(0, lambda: self.lbl_status.configure(text="Error durante la indexación."))
            finally:
                self.after(0, lambda: self.btn_add_pdf.configure(state="normal"))

        threading.Thread(target=run_indexing, daemon=True).start()

    def _refresh_manuals_list(self):
        for widget in self.results_scroll.winfo_children():
            widget.destroy()
        manuals = self.db.get_registered_manuals()
        if not manuals:
            ctk.CTkLabel(self.results_scroll, text="Aún no hay manuales cargados.").pack(pady=10)
            return
        for m in manuals:
            card = ctk.CTkFrame(self.results_scroll)
            card.pack(fill="x", pady=4, padx=2)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=6, pady=(6, 2))
            ctk.CTkLabel(
                top_row, text=f"{m['title']} ({m['total_pages']} págs.)",
                font=("Segoe UI", 12, "bold")
            ).pack(side="left")
            ctk.CTkButton(
                top_row, text="Abrir", width=60, height=24,
                command=lambda mid=m['id'], mtitle=m['title']: self._load_page(mid, 1, mtitle)
            ).pack(side="right")

            bot_row = ctk.CTkFrame(card, fg_color="transparent")
            bot_row.pack(fill="x", padx=6, pady=(2, 6))

            ctk.CTkButton(
                bot_row, text="Extraer Conjuros", height=24, fg_color="#6D28D9", hover_color="#5B21B6",
                font=("Segoe UI", 11, "bold"),
                command=lambda mid=m['id'], mtitle=m['title']: self._run_spell_extraction(mid, mtitle)
            ).pack(side="left", fill="x", expand=True, padx=(0, 3))

            ctk.CTkButton(
                bot_row, text="Extraer Criaturas", height=24, fg_color="#059669", hover_color="#047857",
                font=("Segoe UI", 11, "bold"),
                command=lambda mid=m['id'], mtitle=m['title']: self._run_monster_extraction(mid, mtitle)
            ).pack(side="right", fill="x", expand=True, padx=(3, 0))

    def _run_spell_extraction(self, manual_id: int, title: str):
        self.lbl_status.configure(text=f"Extrayendo conjuros de {title}...")

        def task():
            try:
                count = self.pdf_engine.extract_spells_from_manual(manual_id)
                self.after(0, lambda c=count: self.lbl_status.configure(text=f"¡{c} conjuros extraídos!"))
                self.after(0, lambda c=count: messagebox.showinfo(
                    "Conjuros Extraídos",
                    f"Se extrajeron e integraron {c} conjuros desde '{title}'.\n"
                    f"Ya están disponibles en el selector de conjuros de PC y Móvil."
                ))
            except Exception as err:
                err_msg = str(err)
                self.after(0, lambda msg=err_msg: messagebox.showerror("Error", msg))

        threading.Thread(target=task, daemon=True).start()

    def _run_monster_extraction(self, manual_id: int, title: str):
        self.lbl_status.configure(text=f"Extrayendo criaturas de {title}...")

        def task():
            try:
                count = self.pdf_engine.extract_monsters_from_manual(manual_id)
                self.after(0, lambda c=count: self.lbl_status.configure(text=f"¡{c} criaturas añadidas al Bestiario!"))
                self.after(0, lambda c=count: messagebox.showinfo(
                    "Criaturas Extraídas",
                    f"Se detectaron y guardaron {c} nuevas criaturas desde '{title}' en tu Bestiario 5.5e."
                ))
            except Exception as err:
                err_msg = str(err)
                self.after(0, lambda msg=err_msg: messagebox.showerror("Error", msg))

        threading.Thread(target=task, daemon=True).start()

    def _perform_search(self):
        query = self.entry_search.get()
        if not query.strip():
            self._refresh_manuals_list()
            return
        results = self.db.search_manuals(query)
        for widget in self.results_scroll.winfo_children():
            widget.destroy()
        if not results:
            ctk.CTkLabel(self.results_scroll, text="Sin coincidencias encontradas.").pack(pady=10)
            return
        for r in results:
            card = ctk.CTkFrame(self.results_scroll)
            card.pack(fill="x", pady=5, padx=2)
            header = f"{r['manual_title']} — Pág. {r['page_number']}"
            ctk.CTkButton(
                card, text=header, anchor="w", fg_color="#2B4C7E",
                command=lambda mid=r['manual_id'], p=r['page_number'], t=r['manual_title']: self._load_page(mid, p, t)
            ).pack(fill="x", padx=6, pady=(6, 2))
            ctk.CTkLabel(
                card, text=r['match_snippet'].replace("\n", " "),
                wraplength=280, justify="left", font=("Segoe UI", 11)
            ).pack(fill="x", padx=8, pady=(0, 6))

    def _load_page(self, manual_id: int, page_num: int, title: str = ""):
        try:
            pil_img = self.pdf_engine.render_page_as_pil(manual_id, page_num, zoom=self.current_zoom)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
            self.lbl_pdf_image.configure(image=ctk_img, text="")
            self.lbl_pdf_image.image = ctk_img
            self.current_manual_id = manual_id
            self.current_page = page_num
            if title:
                self.current_title = title
            self.lbl_page_info.configure(text=f"{getattr(self, 'current_title', 'Manual')} — Pág. {page_num}")
            self.lbl_zoom.configure(text=f"{int(self.current_zoom * 100)}%")
        except Exception as err:
            messagebox.showwarning("Aviso", str(err))

    def _change_page(self, delta: int):
        if self.current_manual_id is not None:
            self._load_page(self.current_manual_id, self.current_page + delta)

    def _goto_page(self):
        if self.current_manual_id is None:
            return
        val = self.entry_goto.get().strip()
        if val.isdigit():
            self._load_page(self.current_manual_id, int(val))

    def _change_zoom(self, delta: float):
        if self.current_manual_id is None:
            return
        self.current_zoom = round(max(0.5, min(2.5, self.current_zoom + delta)), 2)
        self._load_page(self.current_manual_id, self.current_page)

    def _project_current_pdf_page_to_mobile(self):
        if self.current_manual_id is None:
            messagebox.showwarning("Sin página", "Primero abre una página de algún manual PDF.")
            return
        try:
            pil_img = self.pdf_engine.render_page_as_pil(self.current_manual_id, self.current_page, zoom=1.2)
            pil_img.thumbnail((1100, 1100))
            buf = io.BytesIO()
            pil_img.save(buf, format="JPEG", quality=82)
            b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")

            title = f"{getattr(self, 'current_title', 'Manual')} — Pág. {self.current_page}"
            self.db.update_live_handout(title, "Ilustración compartida por el DM desde el Manual.", b64_str)
            messagebox.showinfo(
                "Proyectado en Celulares",
                f"👁️ La página {self.current_page} ya está visible en la pestaña '🗺️ Mesa en Vivo' de todos los celulares."
            )
        except Exception as err:
            messagebox.showerror("Error al proyectar", str(err))