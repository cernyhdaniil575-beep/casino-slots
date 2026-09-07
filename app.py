from flask import Flask, render_template, request, jsonify
from collections import Counter
import random

app = Flask(__name__)

SYMBOLS = ["🍒", "🍋", "🍇", "🍉", "🍓", "💎", "7️⃣"]
BONUS = "⭐"
ALL_SYMBOLS = SYMBOLS + [BONUS]
WEIGHTS = [16, 16, 14, 12, 12, 6, 4, 2]

ROWS = 5
COLS = 6
MIN_MATCH = 8

balance = 1000


def random_symbol():
    return random.choices(ALL_SYMBOLS, weights=WEIGHTS, k=1)[0]


def make_grid():
    return [[random_symbol() for _ in range(COLS)] for _ in range(ROWS)]


def winning_positions(grid):
    positions_by_symbol = {}

    for row in range(ROWS):
        for col in range(COLS):
            symbol = grid[row][col]
            if symbol == BONUS:
                continue
            positions_by_symbol.setdefault(symbol, []).append([row, col])

    winners = []
    for symbol, positions in positions_by_symbol.items():
        if len(positions) >= MIN_MATCH:
            winners.extend(positions)

    return winners


def cascade_grid(grid, positions):
    remove_set = {tuple(position) for position in positions}

    for col in range(COLS):
        remaining = [
            grid[row][col]
            for row in range(ROWS)
            if (row, col) not in remove_set
        ]

        new_symbols = [random_symbol() for _ in range(ROWS - len(remaining))]
        new_column = new_symbols + remaining

        for row in range(ROWS):
            grid[row][col] = new_column[row]

    return grid


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/state")
def state():
    return jsonify({"balance": balance})


@app.route("/api/spin", methods=["POST"])
def spin():
    global balance

    data = request.get_json() or {}
    try:
        bet = int(data.get("bet", 10))
    except (TypeError, ValueError):
        return jsonify({"error": "Ставка должна быть числом."}), 400

    if bet <= 0:
        return jsonify({"error": "Ставка должна быть больше нуля."}), 400

    if bet > balance:
        return jsonify({"error": "Недостаточно монет."}), 400

    balance -= bet
    grid = make_grid()
    cascades = []
    total_win = 0
    multiplier = 1

    bonus_count = sum(cell == BONUS for row in grid for cell in row)
    free_spins = 10 if bonus_count >= 4 else 0

    while True:
        positions = winning_positions(grid)
        if not positions:
            break

        multiplier = min(multiplier + 1, 10)
        win = max(1, round(bet * len(positions) / 10 * multiplier))
        total_win += win

        cascades.append({
            "grid": [row[:] for row in grid],
            "positions": positions,
            "win": win,
            "multiplier": multiplier,
        })

        grid = cascade_grid(grid, positions)

    balance += total_win

    return jsonify({
        "balance": balance,
        "grid": grid,
        "total_win": total_win,
        "cascades": cascades,
        "free_spins": free_spins,
        "bonus_count": bonus_count,
    })


if __name__ == "__main__":
    app.run(debug=True)
