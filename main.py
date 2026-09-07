# main.py
import tkinter as tk
from tkinter import font as tkfont
import os
from games.slots import SlotsGame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

def load_image(path, size=None):
    if not os.path.exists(path):
        return None
    img = tk.PhotoImage(file=path)
    if size:
        img = img.subsample(max(1, img.width() // size[0]), max(1, img.height() // size[1]))
    return img

def load_sound(path):
    try:
        import pygame
        pygame.mixer.init()
        if os.path.exists(path):
            return pygame.mixer.Sound(path)
    except Exception:
        pass
    return None

class SoundManager:
    def __init__(self):
        self.sounds = {
            "click": load_sound(os.path.join(SOUNDS_DIR, "click.wav")),
            "win": load_sound(os.path.join(SOUNDS_DIR, "win.wav")),
            "lose": load_sound(os.path.join(SOUNDS_DIR, "lose.wav")),
            "spin": load_sound(os.path.join(SOUNDS_DIR, "spin.wav")),
        }

    def play(self, name):
        sound = self.sounds.get(name)
        if sound:
            sound.play()

class CasinoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Casino")
        self.root.geometry("900x700")
        self.root.configure(bg="#1a1a1a")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.balance = 1000
        self.sound_manager = SoundManager()

        self.main_menu_frame = tk.Frame(root, bg="#1a1a1a")
        self.main_menu_frame.grid(row=0, column=0, sticky="nsew")
        self.main_menu_frame.grid_rowconfigure(0, weight=1)
        self.main_menu_frame.grid_columnconfigure(0, weight=1)

        self.create_main_menu()
        self.current_game_frame = None

    def create_main_menu(self):
        title_font = tkfont.Font(family="Impact", size=28, weight="bold")
        btn_font = tkfont.Font(family="Arial", size=16, weight="bold")

        title = tk.Label(
            self.main_menu_frame,
            text="🎰 PYTHON CASINO 🎰",
            font=title_font,
            fg="#ffd700",
            bg="#1a1a1a"
        )
        title.grid(row=0, column=0, pady=40)

        menu_frame = tk.Frame(self.main_menu_frame, bg="#1a1a1a")
        menu_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        menu_frame.grid_rowconfigure(0, weight=1)
        menu_frame.grid_columnconfigure(0, weight=1)

        buttons = [
            ("Слоты", self.start_slots),
            ("Рулетка", self.placeholder_game),
            ("Карты", self.placeholder_game),
            ("Выход", self.quit_app),
        ]

        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(
                menu_frame,
                text=text,
                font=btn_font,
                bg="#b30000",
                fg="#ffffff",
                activebackground="#ff4d4d",
                activeforeground="#ffffff",
                command=command,
                bd=0,
                padx=20,
                pady=10
            )
            btn.grid(row=i, column=0, sticky="ew", pady=10)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#ff4d4d"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#b30000"))

        balance_label = tk.Label(
            self.main_menu_frame,
            text=f"Баланс: {self.balance} монет",
            font=tkfont.Font(family="Arial", size=18, weight="bold"),
            fg="#ffd700",
            bg="#1a1a1a"
        )
        balance_label.grid(row=2, column=0, pady=20)
        self.balance_label = balance_label

    def update_balance_label(self):
        self.balance_label.configure(text=f"Баланс: {self.balance} монет")

    def start_slots(self):
        self.sound_manager.play("click")
        self.main_menu_frame.grid_remove()
        if self.current_game_frame:
            self.current_game_frame.destroy()
        self.current_game_frame = SlotsGame(self.root, self)
        self.current_game_frame.grid(row=0, column=0, sticky="nsew")

    def placeholder_game(self):
        self.sound_manager.play("click")
        pass

    def quit_app(self):
        self.sound_manager.play("click")
        try:
            with open("balance.txt", "w", encoding="utf-8") as f:
                f.write(str(self.balance))
        except Exception:
            pass
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = CasinoApp(root)
    root.mainloop()
