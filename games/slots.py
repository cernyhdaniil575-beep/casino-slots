# games/slots.py
import tkinter as tk
from tkinter import font as tkfont
import random
import time
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS_DIR = os.path.join(BASE_DIR, "assets", "sounds")

SYMBOLS = ["🍒", "🍋", "🍇", "🔔", "💎", "7️⃣"]
BONUS_SYMBOL = "⭐"
ALL_REEL_SYMBOLS = SYMBOLS + [BONUS_SYMBOL]
WEIGHTS = [12, 12, 12, 8, 6, 4, 2]

MIN_MATCH = 8

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
            "bonus": load_sound(os.path.join(SOUNDS_DIR, "bonus.wav")),
            "cascade": load_sound(os.path.join(SOUNDS_DIR, "cascade.wav")),
        }

    def play(self, name):
        sound = self.sounds.get(name)
        if sound:
            sound.play()

class SlotsGame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg="#0f0f1a")
        self.app = app
        self.reels_count = 6
        self.rows_count = 5

        for i in range(self.rows_count):
            self.grid_rowconfigure(i, weight=1)
        for i in range(self.reels_count):
            self.grid_columnconfigure(i, weight=1)

        self.reel_labels = []
        for row in range(self.rows_count):
            row_labels = []
            for col in range(self.reels_count):
                lbl = tk.Label(
                    self, text="❓",
                    font=("Arial", 24, "bold"),
                    bg="#1a1a2e",
                    fg="#ffd700",
                    padx=12,
                    pady=12,
                    relief="ridge",
                    bd=2
                )
                lbl.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
                row_labels.append(lbl)
            self.reel_labels.append(row_labels)

        control_frame = tk.Frame(self, bg="#0f0f1a")
        control_frame.grid(row=self.rows_count, column=0, columnspan=self.reels_count, pady=15)

        self.bet_var = tk.IntVar(value=10)
        tk.Label(control_frame, text="💰 Ставка:", font=("Arial", 14, "bold"), fg="#ffd700", bg="#0f0f1a").grid(row=0, column=0, padx=10)
        tk.Entry(control_frame, textvariable=self.bet_var, width=5, font=("Arial", 14), bg="#1a1a2e", fg="#ffd700", relief="flat").grid(row=0, column=1, padx=8)

        self.play_btn = tk.Button(
            control_frame, text="⚡ КРУТИТЬ", font=("Arial", 16, "bold"),
            bg="#8b0000", fg="#ffd700",
            activebackground="#ff4500",
            activeforeground="#ffd700",
            command=self.play,
            relief="raised",
            bd=3,
            padx=25,
            pady=8
        )
        self.play_btn.grid(row=0, column=2, padx=20)

        self.back_btn = tk.Button(
            control_frame, text="🔙", font=("Arial", 14, "bold"),
            bg="#2a2a4a", fg="#ffd700",
            activebackground="#3a3a6a",
            activeforeground="#ffd700",
            command=self.go_back,
            relief="raised",
            bd=2,
            padx=15,
            pady=6
        )
        self.back_btn.grid(row=0, column=3, padx=10)

        self.info_label = tk.Label(
            self, text="🎯 8+ = 💰 | ⭐⭐⭐⭐ = 🎁",
            font=("Arial", 14, "bold"),
            fg="#ffd700",
            bg="#0f0f1a"
        )
        self.info_label.grid(row=self.rows_count + 1, column=0, columnspan=self.reels_count, pady=10)

        self.sound_manager = SoundManager()
        self.in_bonus = False
        self.free_spins_left = 0

    def get_random_symbol(self):
        return random.choices(ALL_REEL_SYMBOLS, weights=WEIGHTS, k=1)[0]

    def generate_reels(self):
        return [[self.get_random_symbol() for _ in range(self.rows_count)] for _ in range(self.reels_count)]

    def update_display(self, reels):
        for row in range(self.rows_count):
            for col in range(self.reels_count):
                sym = reels[col][row] if reels[col][row] else " "
                self.reel_labels[row][col].configure(text=sym)

    def flash_reels(self, reels, winning_positions):
        """Мигание выигрышных позиций."""
        for _ in range(3):
            for (col, row) in winning_positions:
                self.reel_labels[row][col].configure(bg="#ff4500", fg="#ffffff")
            self.update()
            time.sleep(0.12)
            for (col, row) in winning_positions:
                self.reel_labels[row][col].configure(bg="#1a1a2e", fg="#ffd700")
            self.update()
            time.sleep(0.12)

    def find_winning_positions(self, reels):
        """Находит позиции выигрышных символов (8+ одинаковых)."""
        from collections import Counter, defaultdict
        symbol_positions = defaultdict(list)
        
        for col in range(self.reels_count):
            for row in range(self.rows_count):
                sym = reels[col][row]
                if sym:
                    symbol_positions[sym].append((col, row))
        
        winning_positions = []
        winning_symbols = set()
        for sym, positions in symbol_positions.items():
            if len(positions) >= MIN_MATCH:
                winning_positions.extend(positions)
                winning_symbols.add(sym)
        
        return winning_positions, winning_symbols

    def remove_winning_symbols(self, reels, winning_positions):
        """Удаляет только выигрышные символы."""
        for (col, row) in winning_positions:
            reels[col][row] = None

    def apply_gravity(self, reels):
        """Символы падают вниз, сверху новые."""
        for col in range(self.reels_count):
            # Собираем все символы в колонке кроме None
            existing = [reels[col][row] for row in range(self.rows_count) if reels[col][row] is not None]
            # Сколько нужно добавить сверху
            missing = self.rows_count - len(existing)
            # Генерируем новые символы для верха
            new_symbols = [self.get_random_symbol() for _ in range(missing)]
            # Новые сверху + существующие снизу
            new_col = new_symbols + existing
            # Записываем обратно
            for row in range(self.rows_count):
                reels[col][row] = new_col[row]

    def count_bonus_symbols(self, reels):
        return sum(1 for col in range(self.reels_count) for row in range(self.rows_count) if reels[col][row] == BONUS_SYMBOL)

    def animate_cascade(self, reels, bet, multiplier):
        total_win = 0
        cascade_num = 0

        while True:
            winning_positions, winning_symbols = self.find_winning_positions(reels)
            if not winning_positions:
                break

            cascade_num += 1
            multiplier = min(multiplier + 1, 10)
            self.sound_manager.play("cascade")

            # Мигание выигрышных позиций
            self.flash_reels(reels, winning_positions)

            # Подсчёт победы
            round_win = len(winning_positions) * multiplier
            total_win += round_win

            self.info_label.configure(text=f"💥 x{multiplier} | +{round_win} | Всего: {total_win}")
            self.update()
            time.sleep(0.3)

            # Удаляем выигрышные символы
            self.remove_winning_symbols(reels, winning_positions)
            self.update_display(reels)
            self.update()
            time.sleep(0.2)

            # Применяем гравитацию
            self.apply_gravity(reels)
            self.update_display(reels)
            self.update()
            time.sleep(0.35)

        return total_win

    def play(self, free_spin=False):
        bet = self.bet_var.get()
        if not free_spin:
            if bet > self.app.balance or bet <= 0:
                self.info_label.configure(text="❌ Неверная ставка!")
                return
            self.app.balance -= bet
            self.app.update_balance_label()

        self.sound_manager.play("spin")

        reels = self.generate_reels()

        for _ in range(6):
            self.update_display(reels)
            self.update()
            time.sleep(0.08)
            reels = self.generate_reels()

        self.update_display(reels)
        self.update()
        time.sleep(0.3)

        if self.count_bonus_symbols(reels) >= 4:
            self.free_spins_left = 10
            self.in_bonus = True
            self.info_label.configure(text=f"🎉 БОНУС! {self.free_spins_left} вращений!")
            self.sound_manager.play("bonus")
            
            # Анимация триггера бонуса
            for _ in range(5):
                for row in range(self.rows_count):
                    for col in range(self.reels_count):
                        self.reel_labels[row][col].configure(bg="#ff4500", fg="#ffffff")
                self.update()
                time.sleep(0.1)
                for row in range(self.rows_count):
                    for col in range(self.reels_count):
                        self.reel_labels[row][col].configure(bg="#1a1a2e", fg="#ffd700")
                self.update()
                time.sleep(0.1)
            
            self.run_free_spins()
            return

        multiplier = 2 if free_spin else 1
        total_win = self.animate_cascade(reels, bet, multiplier)

        if total_win > 0:
            self.app.balance += total_win
            self.info_label.configure(text=f"💰 +{total_win} монет!")
            self.sound_manager.play("win")
        else:
            self.info_label.configure(text="😢 Попробуй снова!")
            self.sound_manager.play("lose")

        self.app.update_balance_label()

    def run_free_spins(self):
        while self.free_spins_left > 0:
            self.free_spins_left -= 1
            self.info_label.configure(text=f"🎁 Вращение {10 - self.free_spins_left}/10")
            self.update()
            time.sleep(0.4)
            self.play(free_spin=True)

        self.in_bonus = False
        self.info_label.configure(text="✅ Бонус завершён!")

    def go_back(self):
        self.sound_manager.play("click")
        self.grid_remove()
        self.app.main_menu_frame.grid()
