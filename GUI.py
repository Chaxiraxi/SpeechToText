import customtkinter as ctk
from tkinter.filedialog import askopenfilenames as ask_files
from tkinter.filedialog import askdirectory as ask_dir
from config import *
CONFIG: dict = load_config()
STRINGS: dict = load_language(CONFIG["language"])
ctk.set_appearance_mode(CONFIG["theme"])
TITLE_FONT = ("Arial", 20, "bold")  # TODO: Load fonts from file

class ModeSelectorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(STRINGS["title_mode_selector"])
        self.resizable(False, False)
        self.createWidgets()

    def createWidgets(self):
        """Create the widgets for the ModeSelector."""
        self.titleLable = ctk.CTkLabel(self, text=STRINGS["title_mode_selector"], font=TITLE_FONT)
        self.onlineButton = ctk.CTkButton(self, text=STRINGS["online_mode"], corner_radius=10, command=self.online)
        self.offlineButton = ctk.CTkButton(self, text=STRINGS["offline_mode"], corner_radius=10, command=self.offline)

        # self.onlineDescription = ctk.CTkLabel(self, text=STRINGS["online_description"])
        # self.offlineDescription = ctk.CTkLabel(self, text=STRINGS["offline_description"])

        self.titleLable.grid(row=0, column=0, columnspan=2)
        self.onlineButton.grid(row=1, column=0, padx=10, pady=10)
        self.offlineButton.grid(row=1, column=1, padx=10, pady=10)
        # self.onlineDescription.grid(row=2, column=0, padx=10, pady=10)
        # self.offlineDescription.grid(row=2, column=1, padx=10, pady=10)
    
    def online(self):
        self.destroy()
        OnlineGUI().mainloop()

    def offline(self):
        pass

class OnlineGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(STRINGS["online_mode"])
        self.createWidgets()

    def createWidgets(self):
        """Create the widgets for the OnlineGUI."""
        self.titleLable = ctk.CTkLabel(self, text=STRINGS["title_online"], font=TITLE_FONT)
        self.backButton = ctk.CTkButton(self, text=STRINGS["button_back"], corner_radius=10, command=self.back)
        self.titleLable.grid(row=0, column=0, columnspan=2)
        self.backButton.grid(row=1, column=0, padx=10, pady=10)

    def back(self):
        pass

if __name__ == "__main__":
    gui = ModeSelectorGUI()
    gui.mainloop()