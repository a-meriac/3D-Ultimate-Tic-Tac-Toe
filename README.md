# 🎮 3D Ultimate Tic Tac Toe

Welcome to **3D Ultimate Tic Tac Toe** — a full-terminal Python game that combines classic Tic Tac Toe with the layered strategy of Ultimate Tic Tac Toe… in **three dimensions**.

---

## 📖 What is this?

A Python implementation that merges:

| ✔ | Concept                 |
|---|-------------------------|
| ✅ | Regular Tic Tac Toe     |
| ✅ | Ultimate Tic Tac Toe    |
| ✅ | 3-D Tic Tac Toe (3×3×3) |

You play on a **3×3×3 grid of 3×3×3 mini-boards** (729 cells total). Win mini-cubes, then align three won cubes to claim total victory.

---

## 🕹️ How to Play

1. **Game start:** first move is always in the **center cube** `(1,1,1)`.
2. **Input format:** type a **3-digit** coordinate such as `120`
   - `sx` (small x)   `1`
   - `sy` (small y)   `2`
   - `sz` (small z)   `0`
3. That move forces your opponent to play in big cube `(1,2,0)`.
4. **Win a mini-cube** by lining up 3 marks (rows, columns, pillars, diagonals).
5. **Win the game** by winning 3 mini-cubes in a row in the 3-D meta-grid.

---

## 💾 Features

| Command / Feature            | Description                                                     |
|------------------------------|-----------------------------------------------------------------|
| **Named players**            | Game greets each player by name                                 |
| `/undo`                      | Undo the last move                                              |
| `/print`                     | Show the full 9 × 9 × 9 board                                   |
| `/saves`                     | List all saved games with stats                                 |
| `/delete &lt;name&gt;`       | Delete a saved game                                             |
| `/new`                       | Start a fresh game                                              |
| **Multiple saves**           | Create any number of named save files                           |
| **Auto-save**                | The game saves **once per turn**                                |
| **Meta-win detection**       | Detects 3-in-a-row of won cubes for the overall win             |
| `/help`                      | In-game command reference                                       |

---

## 🔧 Requirements

- **Python 3.6+**  
- No external libraries — 100 % standard library

---

## 🚀 Running the Game

```bash
python game.py
