const gridElement = document.getElementById("grid");
const balanceElement = document.getElementById("balance");
const betElement = document.getElementById("bet");
const spinButton = document.getElementById("spinButton");
const resultElement = document.getElementById("result");

const ROWS = 5;
const COLS = 6;
let currentGrid = [];

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function randomDemoSymbol() {
    const symbols = ["🍒", "🍋", "🍇", "🍉", "🍓", "💎", "7️⃣", "⭐"];
    return symbols[Math.floor(Math.random() * symbols.length)];
}

function demoGrid() {
    return Array.from({ length: ROWS }, () =>
        Array.from({ length: COLS }, randomDemoSymbol())
    );
}

function renderGrid(grid, winning = [], removed = [], falling = false) {
    const winningSet = new Set(winning.map(([row, col]) => `${row}-${col}`));
    const removedSet = new Set(removed.map(([row, col]) => `${row}-${col}`));

    gridElement.innerHTML = "";

    grid.forEach((row, rowIndex) => {
        row.forEach((symbol, colIndex) => {
            const cell = document.createElement("div");
            const key = `${rowIndex}-${colIndex}`;
            cell.className = "cell";

            if (winningSet.has(key)) cell.classList.add("winner");
            if (removedSet.has(key)) cell.classList.add("removed");
            if (falling) cell.classList.add("fall");

            cell.textContent = symbol || "";
            gridElement.appendChild(cell);
        });
    });
}

async function spinVisual() {
    for (let i = 0; i < 8; i++) {
        renderGrid(demoGrid(), [], [], true);
        await sleep(90);
    }
}

async function startSpin() {
    const bet = Number(betElement.value);

    if (!Number.isInteger(bet) || bet < 1) {
        resultElement.textContent = "Введите корректную ставку.";
        return;
    }

    spinButton.disabled = true;
    resultElement.textContent = "Барабаны вращаются...";
    await spinVisual();

    try {
        const response = await fetch("/api/spin", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ bet })
        });

        const data = await response.json();

        if (!response.ok) {
            resultElement.textContent = `❌ ${data.error}`;
            spinButton.disabled = false;
            return;
        }

        // Обновляем баланс
        balanceElement.textContent = data.balance;

        // Показываем каскады
        for (const cascade of data.cascades) {
            renderGrid(cascade.grid, cascade.positions);
            resultElement.textContent = `💥 Каскад! Множитель x${cascade.multiplier}, выигрыш +${cascade.win}`;
            await sleep(800);
        }

        // Финальная сетка
        renderGrid(data.grid, [], [], true);

        // Результат
        if (data.free_spins > 0) {
            resultElement.textContent = `🎉 БОНУС: ${data.bonus_count} звезды! Получено ${data.free_spins} бесплатных вращений.`;
        } else if (data.total_win > 0) {
            resultElement.textContent = `💰 Победа: +${data.total_win} монет!`;
        } else {
            resultElement.textContent = "😢 В этот раз без выигрыша.";
        }
    } catch (error) {
        console.error(error);
        resultElement.textContent = "Ошибка соединения с сервером.";
    } finally {
        spinButton.disabled = false;
    }
}

spinButton.addEventListener("click", startSpin);

// Инициализация
currentGrid = demoGrid();
renderGrid(currentGrid);
