const gridElement = document.getElementById("grid");
const balanceElement = document.getElementById("balance");
const betElement = document.getElementById("bet");
const spinButton = document.getElementById("spinButton");
const resultElement = document.getElementById("result");

const ROWS = 5;
const COLS = 6;

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function randomSymbol() {
    const symbols = ["🍒", "🍋", "🍇", "🍉", "🍓", "💎", "7️⃣", "⭐"];
    return symbols[Math.floor(Math.random() * symbols.length)];
}

function createGrid() {
    return Array.from({ length: ROWS }, () =>
        Array.from({ length: COLS }, randomSymbol)
    );
}

function renderGrid(grid, winningPositions = []) {
    gridElement.innerHTML = "";
    
    const winningSet = new Set(
        winningPositions.map(([r, c]) => `${r}-${c}`)
    );

    for (let row = 0; row < ROWS; row++) {
        for (let col = 0; col < COLS; col++) {
            const cell = document.createElement("div");
            cell.className = "cell";
            
            if (winningSet.has(`${row}-${col}`)) {
                cell.classList.add("winner");
            }
            
            cell.textContent = grid[row][col] || "";
            gridElement.appendChild(cell);
        }
    }
}

async function spinAnimation() {
    for (let i = 0; i < 6; i++) {
        renderGrid(createGrid());
        await sleep(100);
    }
}

async function startSpin() {
    const bet = parseInt(betElement.value, 10);

    if (!bet || bet < 1) {
        resultElement.textContent = "❌ Введите ставку от 1";
        return;
    }

    spinButton.disabled = true;
    resultElement.textContent = "🎲 Вращение...";

    await spinAnimation();

    try {
        const response = await fetch("/api/spin", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ bet: bet })
        });

        const data = await response.json();

        if (!response.ok) {
            resultElement.textContent = `❌ ${data.error || "Ошибка"}`;
            spinButton.disabled = false;
            return;
        }

        balanceElement.textContent = data.balance;

        if (data.cascades && data.cascades.length > 0) {
            for (const cascade of data.cascades) {
                renderGrid(cascade.grid, cascade.positions);
                resultElement.textContent = `💥 x${cascade.multiplier} +${cascade.win}`;
                await sleep(700);
            }
        }

        renderGrid(data.grid);

        if (data.free_spins > 0) {
            resultElement.textContent = `🎉 БОНУС! +${data.free_spins} вращений`;
        } else if (data.total_win > 0) {
            resultElement.textContent = `💰 Победа: +${data.total_win}`;
        } else {
            resultElement.textContent = "😢 Попробуй ещё раз";
        }

    } catch (err) {
        console.error("Spin error:", err);
        resultElement.textContent = "❌ Ошибка соединения";
    } finally {
        spinButton.disabled = false;
    }
}

spinButton.addEventListener("click", startSpin);

// Стартовая сетка
renderGrid(createGrid());
