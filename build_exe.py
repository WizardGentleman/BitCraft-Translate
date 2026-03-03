import os
import subprocess
import sys

def build():
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    print("Building Executable...")
    # --noconsole: hide terminal
    # --onefile: single .exe
    # --name: name of the file
    # --add-data: inclusion of other modules (Note: PyInstaller handles imports automatically usually, 
    # but for ctk and custom logic sometimes explicit is better)
    
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        "--name", "BitcraftTranslator",
        "main_gui.pyw"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\nSUCCESS! Your .exe is in the 'dist' folder.")
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    build()
