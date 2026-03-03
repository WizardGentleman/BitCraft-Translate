import customtkinter as ctk
import pyperclip
from threading import Thread
import time
import json
import os
from api_client import BitcraftAPI
from translator import ChatTranslator

CONFIG_FILE = "config.json"

# Design Constants
COLOR_BG = "#1a1a1a"
COLOR_SIDEBAR = "#252525"
COLOR_ACCENT = "#3a86ff"
COLOR_ACCENT_NAMES = "#ff7b00"  # Orange for names
COLOR_TEXT = "#ffffff"
COLOR_TEXT_SECONDARY = "#b0b0b0"
COLOR_SENDER = "#00d4ff"
COLOR_ORIGINAL = "#777777"

class BitcraftChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Bitcraft Chat Translator")
        self.geometry("900x600")
        self.configure(fg_color=COLOR_BG)

        # Initialize backend
        self.api = BitcraftAPI()
        
        # Load config and language
        config_data = self._load_config()
        self.selected_region = ctk.StringVar(value=config_data.get("region", "Todas"))
        self.target_lang = config_data.get("target_lang")
        self.target_lang_name = config_data.get("target_lang_name")
        
        # Initialize translator with saved language or default to 'pt'
        self.translator = ChatTranslator(target_lang=self.target_lang if self.target_lang else 'pt')
        
        self.auto_translate = ctk.BooleanVar(value=True)
        self.seen_message_ids = set()
        self.is_running = True

        self._setup_ui()
        
        # Check for first launch / missing language
        if not self.target_lang:
            self.after(100, self._open_language_selection)
        else:
            self._update_localized_ui()

        # Start background polling
        self.poll_thread = Thread(target=self._poll_messages, daemon=True)
        self.poll_thread.start()

    def _setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=COLOR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="BITCRAFT\nTRANSLATOR", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20, padx=20)

        # Region Selector
        self.region_label = ctk.CTkLabel(self.sidebar, text="Filtrar por Região:", font=ctk.CTkFont(size=12, weight="bold"))
        self.region_label.pack(pady=(10, 5), padx=20)
        
        regions = ["Todas"] + [str(i) for i in range(1, 21)]
        self.region_menu = ctk.CTkOptionMenu(self.sidebar, values=regions, variable=self.selected_region, 
                                            fg_color="#333333", button_color=COLOR_ACCENT, dropdown_fg_color="#333333",
                                            command=lambda _: self._save_config())
        self.region_menu.pack(pady=(0, 20), padx=20)

        self.translate_switch = ctk.CTkSwitch(self.sidebar, text="Auto Tradução", variable=self.auto_translate, progress_color=COLOR_ACCENT)
        self.translate_switch.pack(pady=20, padx=20)

        # Language Info and Gear
        self.lang_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.lang_frame.pack(side="bottom", pady=(0, 10), fill="x", padx=10)

        self.info_label = ctk.CTkLabel(self.lang_frame, text="Tradução:\nEN -> ...", text_color=COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=12))
        self.info_label.pack(side="left", padx=(10, 0), expand=True)

        self.settings_button = ctk.CTkButton(self.lang_frame, text="⚙️", width=30, height=30, 
                                            fg_color="transparent", hover_color="#333333", 
                                            font=ctk.CTkFont(size=18), command=self._open_language_selection)
        self.settings_button.pack(side="right", padx=10)

        # Signature
        self.signature_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.signature_frame.pack(side="bottom", pady=(0, 10))
        
        self.sig_prefix = ctk.CTkLabel(self.signature_frame, text="Criado por ", text_color=COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=11))
        self.sig_prefix.pack(side="left")
        
        self.sig_names = ctk.CTkLabel(self.signature_frame, text="PoetaBarroco", 
                                    text_color=COLOR_ACCENT_NAMES, font=ctk.CTkFont(size=11, weight="bold"))
        self.sig_names.pack(side="left")

        # Main Chat Area
        self.chat_container = ctk.CTkFrame(self, fg_color="transparent")
        self.chat_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.chat_container.grid_columnconfigure(0, weight=1)
        self.chat_container.grid_rowconfigure(0, weight=1)

        self.chat_display = ctk.CTkTextbox(self.chat_container, font=ctk.CTkFont(size=14), fg_color="#2b2b2b", text_color=COLOR_TEXT)
        self.chat_display.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        self.chat_display.configure(state="disabled")
        
        # Configure Tags for styling
        self.chat_display.tag_config("sender", foreground=COLOR_SENDER)
        self.chat_display.tag_config("content", foreground=COLOR_TEXT)
        self.chat_display.tag_config("original", foreground=COLOR_ORIGINAL)
        self.chat_display.tag_config("system", foreground=COLOR_TEXT_SECONDARY)

        # Outgoing Translation Area
        self.input_frame = ctk.CTkFrame(self.chat_container, fg_color=COLOR_SIDEBAR, height=120)
        self.input_frame.grid(row=1, column=0, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Escreva em Português para traduzir e copiar...", 
                                       height=40, fg_color="#333333", border_color="#444444")
        self.input_entry.grid(row=0, column=0, padx=20, pady=15, sticky="ew")
        self.input_entry.bind("<Return>", lambda e: self._translate_and_copy())

        self.copy_button = ctk.CTkButton(self.input_frame, text="Traduzir & Copiar", command=self._translate_and_copy,
                                        fg_color=COLOR_ACCENT, hover_color="#2a6fdf", font=ctk.CTkFont(weight="bold"))
        self.copy_button.grid(row=0, column=1, padx=(0, 20), pady=15)

        self.status_label = ctk.CTkLabel(self.input_frame, text="", text_color=COLOR_ACCENT, font=ctk.CTkFont(size=11))
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))

    def _add_message(self, sender, content, original=None):
        self.chat_display.configure(state="normal")
        
        # Sender header
        self.chat_display.insert("end", f"{sender}: ", "sender")
        
        # Main translated content
        self.chat_display.insert("end", f"{content}\n", "content")
        
        # Original text if translated
        if original and original != content:
            self.chat_display.insert("end", f"   ↳ {original}\n", "original")
        
        self.chat_display.insert("end", "\n") # Empty line instead of separator
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_config(self):
        try:
            config = {
                "region": self.selected_region.get(),
                "target_lang": self.target_lang,
                "target_lang_name": self.target_lang_name
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _open_language_selection(self):
        dialog = LanguageSelectionDialog(self, self._on_language_selected)
        
    def _on_language_selected(self, lang_name, lang_code):
        self.target_lang = lang_code
        self.target_lang_name = lang_name
        self.translator.set_target_lang(lang_code)
        self._save_config()
        self._update_localized_ui()

    def _update_localized_ui(self):
        # Update labels
        target_display = self.target_lang_name.upper() if self.target_lang_name else self.target_lang.upper()
        self.info_label.configure(text=f"Tradução:\nEN -> {target_display}")
        
        # update placeholder
        placeholder = f"Escreva em {self.target_lang_name} para traduzir e copiar..."
        self.input_entry.configure(placeholder_text=placeholder)

        # Translate "Created by"
        def translate_sig():
            translated_prefix = self.translator.translate_to_target("Created by")
            self.sig_prefix.configure(text=f"{translated_prefix} ")
        
        Thread(target=translate_sig, daemon=True).start()

    def _translate_and_copy(self):
        text = self.input_entry.get()
        if not text: return

        def task():
            self.copy_button.configure(state="disabled", text="Traduzindo...")
            en_text = self.translator.translate_to_en(text)
            pyperclip.copy(en_text)
            self.status_label.configure(text=f"Copiado: {en_text}")
            self.input_entry.delete(0, "end")
            self.copy_button.configure(state="normal", text="Traduzir & Copiar")
            
            # Clear status after 3 seconds
            time.sleep(3)
            self.status_label.configure(text="")

        Thread(target=task, daemon=True).start()

    def _poll_messages(self):
        while self.is_running:
            try:
                messages = self.api.get_messages(limit=10)
                # API returns messages newest first, we want old -> new for display if polling
                for msg in reversed(messages):
                    msg_id = msg.get("entityId")
                    if not msg_id or msg_id in self.seen_message_ids:
                        continue
                    
                    self.seen_message_ids.add(msg_id)
                    # Keep set size manageable
                    if len(self.seen_message_ids) > 1000:
                        # Convert to list to remove oldest items or just take a slice
                        self.seen_message_ids = set(list(self.seen_message_ids)[-500:])

                    region_id = msg.get("regionId")
                    current_filter = self.selected_region.get()
                    
                    if current_filter != "Todas" and str(region_id) != current_filter:
                        continue

                    sender = msg.get("username", "Unknown")
                    content = msg.get("text", "")
                    
                    # Clean sender name from API prefixes if any (bitcraft specific cleanup)
                    if sender.startswith("en/"): sender = sender[3:]
                    
                    # Only show region if not filtered
                    display_sender = sender if current_filter != "Todas" else f"{sender} (R{region_id})"
                    
                    if self.auto_translate.get():
                        translated = self.translator.translate_to_target(content)
                        self._add_message(display_sender, translated, original=content)
                    else:
                        self._add_message(display_sender, content)
                
            except Exception as e:
                print(f"Polling error: {e}")
            
            time.sleep(5) # Poll every 5 seconds

class LanguageSelectionDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Escolha sua Língua / Choose Your Language")
        self.geometry("400x500")
        self.transient(parent)
        self.grab_set()
        
        self.configure(fg_color=COLOR_BG)
        
        self.label = ctk.CTkLabel(self, text="Escolha a língua para tradução:\n(O inglês é o padrão de entrada)", 
                                 font=ctk.CTkFont(size=14, weight="bold"))
        self.label.pack(pady=20)

        # Get languages
        self.languages_dict = ChatTranslator.get_supported_languages()
        # Add specific variants for Portuguese, but both use 'pt' code
        self.languages_dict["português (brasil)"] = "pt"
        self.languages_dict["português (portugal)"] = "pt"
        
        # Sort by name
        sorted_names = sorted(self.languages_dict.keys())

        # Search box
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Procurar língua...")
        self.search_entry.pack(pady=(0, 10), padx=20, fill="x")
        self.search_entry.bind("<KeyRelease>", self._filter_languages)

        # Scrollable frame for languages
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#252525")
        self.scroll_frame.pack(expand=True, fill="both", padx=20, pady=(0, 20))

        self.buttons = []
        for name in sorted_names:
            btn = ctk.CTkButton(self.scroll_frame, text=name.capitalize(), 
                               fg_color="transparent", text_color=COLOR_TEXT,
                               anchor="w", hover_color="#444444",
                               command=lambda n=name, c=self.languages_dict[name]: self._select(n, c))
            btn.pack(fill="x", pady=2)
            self.buttons.append((name, btn))

    def _filter_languages(self, event=None):
        search_term = self.search_entry.get().lower()
        for name, btn in self.buttons:
            if search_term in name.lower():
                btn.pack(fill="x", pady=2)
            else:
                btn.pack_forget()

    def _select(self, name, code):
        self.callback(name.capitalize(), code)
        self.destroy()

if __name__ == "__main__":
    app = BitcraftChatApp()
    app.mainloop()
