# BitCraft Translate

A modern, global chat translator for the Bitcraft universe. This tool allows users to monitor game chat in real-time, automatically translating messages into any of the 100+ languages supported by Google Translate.

![Preview](https://via.placeholder.com/800x450?text=Bitcraft+Chat+Translator+Preview)

## ✨ Features

- **Global reach:** Supports nearly every language on earth.
- **First-launch setup:** Choose your language once and forget it.
- **Smart outgoing translation:** Type in your native language, and it automatically translates to English and copies to your clipboard.
- **Region Filtering:** Focused on a specific game region? Filter messages easily.
- **Modern UI:** Built with `customtkinter` for a sleek, dark-mode experience.
- **Persistent History:** Remembers your region and language preferences.

## 🛠️ Installation

### For Users (Recommended)
You can download the latest standalone `.exe` from the [Releases](https://github.com/WizardGentleman/bitcraft-translator/releases) page. No Python installation required!

### For Developers
If you want to run the code directly or contribute:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/WizardGentleman/bitcraft-translator.git
   cd bitcraft-translator
   ```

2. **Install dependencies:**
   ```bash
   pip install customtkinter requests pyperclip deep-translator
   ```

3. **Run the application:**
   ```bash
   python main_gui.pyw
   ```

## 📦 Building the Executable

To create a standalone `.exe`, use `PyInstaller`:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name "BitcraftTranslator" --add-data "translator.py;." --add-data "api_client.py;." main_gui.pyw
```

## 🤝 Credits

Created by **PoetaBarroco**.

Special thanks to the Bitcraft community for the API access.
