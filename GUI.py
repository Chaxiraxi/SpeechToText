import customtkinter as ctk
from threading import Thread as Th
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import StringVar,END
from functions import transcribe as transcribe_file
from config import *
CONFIG: dict = load_config()
STRINGS: dict = load_language(CONFIG["language"])
ctk.set_appearance_mode(CONFIG["appearance_mode"])
ctk.set_default_color_theme(CONFIG["theme"])
TITLE_FONT = ("Arial", 20, "bold")  # TODO: Load fonts from file

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Define StringVars
        self.api_key = StringVar()
        self.file_path = StringVar()
        self.transcribed_text = ""
        self.api_key.set(CONFIG["api_key"])

        self.title(STRINGS["title"])
        # self.resizable(False, False)
        self.geometry("500x450")

        # create 2x6 grid system
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Define frames and widgets
        # Title label
        self.title_label = ctk.CTkLabel(self, text=STRINGS["title"], font=TITLE_FONT, width=750)
        self.title_label.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Input CtkEntry for OpenAI API key
        self.api_key_entry = ctk.CTkEntry(self, placeholder_text=STRINGS["api_key_entry_placeholder"])
        self.api_key_entry.configure(textvariable=self.api_key)
        self.api_key_entry.bind("<Return>", self.save_api_key)
        self.api_key_entry.grid(row=1, column=0, padx=10, pady=10, columnspan=2, sticky="ew")

        # Input CtkEntry for file path
        self.file_path_entry = ctk.CTkEntry(self, placeholder_text=STRINGS["file_path_entry_placeholder"])
        self.file_path_entry.configure(textvariable=self.file_path)
        self.choose_file_button = ctk.CTkButton(self, text=STRINGS["choose_file_button"], command=self.choose_file)
        self.file_path_entry.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.choose_file_button.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        # Output CtkTextbox for generated text
        self.generated_text = ctk.CTkTextbox(self, width=50, height=10)
        self.generated_text.grid(row=3, column=0, padx=10, pady=10, columnspan=2, sticky="nsew")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=4, column=0, padx=10, pady=10, columnspan=2, sticky="ew")

        # Transcribe and save buttons
        self.transcribe_button = ctk.CTkButton(self, text=STRINGS["transcribe_button"], command=self.transcribe)
        self.transcribe_button.grid(row=5, column=0, padx=10, pady=10)
        self.save_to_file_button = ctk.CTkButton(self, text=STRINGS["save_to_file_button"], state="disabled", command=self.save_to_file)
        self.save_to_file_button.grid(row=5, column=1, padx=10, pady=10, sticky="e")

    def choose_file(self):
        """Open a file dialog to choose a file."""
        self.file_path.set(askopenfilename())

    def transcribe(self):
        """Transcribe the file."""
        file_path = self.file_path_entry.get()
        
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        self.generated_text.delete('1.0', END)
        def thread_function():
            self.transcribed_text = transcribe_file(file_path)
            self.generated_text.insert("1.0", self.transcribed_text)
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate")
            self.save_to_file_button.configure(state="normal")
            self.progress_bar.set(100)
        Th(target=thread_function, daemon=True).start()

    def save_to_file(self):
        """Save the generated text to a file."""
        file_path = asksaveasfilename()
        with open(file_path, "w") as f:
            f.write(self.transcribed_text)

    def save_api_key(self):
        """Save the config to the config file."""
        CONFIG["api_key"] = self.api_key_entry.get()
        save_config(CONFIG)

if __name__ == "__main__":
    app = App()
    app.mainloop()