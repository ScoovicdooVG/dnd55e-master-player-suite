import customtkinter as ctk
from database.db_manager import DatabaseManager
from pdf_engine.pdf_engine import PDFEngine
from ui.main_indexer_ui import PDFIndexerView
from ui.char_sheet_view import CharacterSheetView
from ui.dm_tools_view import DMToolsView
from mobile_server import MobileCompanionServer

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DnD55SuiteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("D&D 5.5e Master & Player Suite")
        self.geometry("1380x820")
        import sys
        from pathlib import Path
        base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        icon_file = base_dir / "dnd55_logo.ico"
        if icon_file.exists():
            self.iconbitmap(str(icon_file))

        self.db = DatabaseManager()
        self.pdf_engine = PDFEngine(self.db)

        # Iniciar servidor Wi-Fi para iOS y Android automáticamente
        self.mobile_srv = MobileCompanionServer(self.db, port=8080)
        self.mobile_url = self.mobile_srv.start()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- BARRA DE NAVEGACIÓN LATERAL ---
        self.nav_bar = ctk.CTkFrame(self, width=205, corner_radius=0, fg_color="#111827")
        self.nav_bar.grid(row=0, column=0, sticky="nsew")
        self.nav_bar.grid_propagate(False)

        ctk.CTkLabel(
            self.nav_bar, text="D&D 5.5e\nSUITE", 
            font=("Segoe UI", 22, "bold"), text_color="#F87171"
        ).pack(pady=(20, 20), padx=15)

        import sys
        from pathlib import Path
        from PIL import Image

        base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        icon_file = base_dir / "dnd55_logo.ico"
        png_file = base_dir / "dnd55_logo.png"

        if icon_file.exists():
            self.iconbitmap(str(icon_file))

        # Mostrar tu logo en la parte superior de la barra lateral
        logo_source = png_file if png_file.exists() else (icon_file if icon_file.exists() else None)
        if logo_source:
            pil_logo = Image.open(logo_source)
            self.sidebar_logo = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(95, 95))
            ctk.CTkLabel(self.nav_bar, image=self.sidebar_logo, text="").pack(pady=(15, 2))

        self.btn_nav_chars = ctk.CTkButton(
            self.nav_bar, text="Personajes 5.5e", height=40, anchor="w",
            font=("Segoe UI", 14, "bold"), command=lambda: self.show_view("chars")
        )
        self.btn_nav_chars.pack(fill="x", padx=12, pady=5)

        self.btn_nav_dm = ctk.CTkButton(
            self.nav_bar, text="Pantalla del DM", height=40, anchor="w",
            font=("Segoe UI", 14, "bold"), command=lambda: self.show_view("dm")
        )
        self.btn_nav_dm.pack(fill="x", padx=12, pady=5)

        self.btn_nav_pdf = ctk.CTkButton(
            self.nav_bar, text="Manuales PDF", height=40, anchor="w",
            font=("Segoe UI", 14, "bold"), command=lambda: self.show_view("pdf")
        )
        self.btn_nav_pdf.pack(fill="x", padx=12, pady=5)

        # --- TARJETA INFERIOR CON CÓDIGO QR PARA CELULARES (iOS / ANDROID) ---
        mobile_card = ctk.CTkFrame(self.nav_bar, fg_color="#1E293B")
        mobile_card.pack(side="bottom", fill="x", padx=10, pady=12)

        ctk.CTkLabel(
            mobile_card, text="Escanea con iOS / Android",
            font=("Segoe UI", 12, "bold"), text_color="#34D399"
        ).pack(padx=6, pady=(8, 4))

        qr_pil = self.mobile_srv.generate_qr_pil(self.mobile_url, box_size=5)
        self.qr_ctk_small = ctk.CTkImage(light_image=qr_pil, dark_image=qr_pil, size=(145, 145))
        lbl_qr = ctk.CTkLabel(mobile_card, image=self.qr_ctk_small, text="")
        lbl_qr.pack(padx=8, pady=4)

        entry_url = ctk.CTkEntry(mobile_card, justify="center", font=("Consolas", 11, "bold"), height=26)
        entry_url.insert(0, self.mobile_url)
        entry_url.configure(state="readonly")
        entry_url.pack(fill="x", padx=8, pady=4)

        ctk.CTkButton(
            mobile_card, text="Ampliar QR en Pantalla", height=26, fg_color="#2563EB",
            font=("Segoe UI", 11, "bold"), command=self._open_large_qr_modal
        ).pack(fill="x", padx=8, pady=(2, 4))

        ctk.CTkButton(
            mobile_card, text="↻ Sincronizar Lista Móvil", height=26, fg_color="#374151",
            font=("Segoe UI", 11), command=self._sync_from_mobile
        ).pack(fill="x", padx=8, pady=(0, 8))

        # --- CONTENEDOR DE VISTAS ---
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self.views = {
            "chars": CharacterSheetView(self.container, self.db),
            "dm": DMToolsView(self.container, self.db),
            "pdf": PDFIndexerView(self.container, self.db, self.pdf_engine)
        }

        self.show_view("chars")

    def _open_large_qr_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Código QR de la Mesa — D&D 5.5e")
        modal.geometry("420x480")
        modal.grab_set()

        ctk.CTkLabel(
            modal, text="Escanea con la cámara de tu celular",
            font=("Segoe UI", 18, "bold"), text_color="#34D399"
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            modal, text="(Debes estar conectado a la misma red Wi-Fi)",
            font=("Segoe UI", 12), text_color="#9CA3AF"
        ).pack(pady=(0, 10))

        qr_big_pil = self.mobile_srv.generate_qr_pil(self.mobile_url, box_size=10)
        qr_big_ctk = ctk.CTkImage(light_image=qr_big_pil, dark_image=qr_big_pil, size=(300, 300))
        lbl = ctk.CTkLabel(modal, image=qr_big_ctk, text="")
        lbl.image = qr_big_ctk
        lbl.pack(pady=10)

        ctk.CTkLabel(modal, text=self.mobile_url, font=("Consolas", 16, "bold"), text_color="#FBBF24").pack(pady=8)

    def _sync_from_mobile(self):
        self.views["chars"]._refresh_character_list()
        if self.views["chars"].current_char_id:
            self.views["chars"]._load_char_from_db(self.views["chars"].current_char_id)

    def show_view(self, name: str):
        for key, view in self.views.items():
            view.grid_forget()

        if name == "chars":
            self.views["chars"]._refresh_character_list()
            if self.views["chars"].current_char_id:
                self.views["chars"]._load_char_from_db(self.views["chars"].current_char_id)

        if name == "dm":
            self.views["dm"]._refresh_monster_list()
        self.views[name].grid(row=0, column=0, sticky="nsew")

        self.btn_nav_chars.configure(fg_color="#8B2635" if name == "chars" else "#1F2937")
        self.btn_nav_dm.configure(fg_color="#8B2635" if name == "dm" else "#1F2937")
        self.btn_nav_pdf.configure(fg_color="#8B2635" if name == "pdf" else "#1F2937")

if __name__ == "__main__":
    app = DnD55SuiteApp()
    app.mainloop()