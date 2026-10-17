import subprocess
import sys
from pathlib import Path
from PIL import Image


def ensure_custom_ico(root: Path) -> Path:
    ico_path = root / "dnd55_logo.ico"
    png_path = root / "dnd55_logo.png"

    if ico_path.exists():
        print(f"✔ Usando tu ícono personalizado: {ico_path.name}")
        return ico_path

    if png_path.exists():
        img = Image.open(png_path).convert("RGBA")
        img.save(
            ico_path,
            format="ICO",
            sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        )
        print(f"✔ Tu imagen {png_path.name} fue convertida a {ico_path.name} con éxito.")
        return ico_path

    raise FileNotFoundError("Coloca 'dnd55_logo.ico' o 'dnd55_logo.png' en la carpeta raíz D:\\dnd55_suite\\")


def build_exe():
    root = Path(__file__).resolve().parent
    ico_path = ensure_custom_ico(root)
    png_path = root / "dnd55_logo.png"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "DnD55e_Suite",
        f"--icon={ico_path}",
        f"--add-data={ico_path};.",
        "--collect-all", "customtkinter",
        "--collect-all", "pymupdf",
        "main.py"
    ]

    if png_path.exists():
        cmd.insert(-1, f"--add-data={png_path};.")

    print("Empaquetando aplicación de Windows con tu logo personalizado...")
    subprocess.run(cmd, check=True)
    print("\n¡Listo! Tu ejecutable está en: D:\\dnd55_suite\\dist\\DnD55e_Suite\\DnD55e_Suite.exe")


if __name__ == "__main__":
    build_exe()
