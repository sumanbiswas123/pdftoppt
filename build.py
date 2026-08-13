import os
import subprocess

def build_exe():
    print("Building standalone executable with PyInstaller...")
    pyinstaller_bin = os.path.join("venv", "Scripts", "pyinstaller.exe")
    cmd = [
        pyinstaller_bin,
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name=ePDF_to_ePPT",
        "--collect-all=customtkinter",
        "app.py"
    ]
    subprocess.run(cmd, check=True)
    print("Build complete! Executable located in dist/ePDF_to_ePPT/ePDF_to_ePPT.exe")

if __name__ == "__main__":
    build_exe()
