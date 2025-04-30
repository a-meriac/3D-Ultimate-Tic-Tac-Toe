# 3D Ultimate Tic Tac Toe

Welcome to **3D Ultimate Tic Tac Toe** — a full-terminal Python game that combines classic Tic Tac Toe with the depth of Ultimate Tic Tac Toe... in **three dimensions**.


## What is this?

This is a Python implementation of a custom game based on:

- ✅ **Tic Tac Toe**  
- ✅ **Ultimate Tic Tac Toe**  
- ✅ **3D Tic Tac Toe**

## How to Play:

1. The game starts in the **center cube**.
2. You enter your move as a 3-digit coordinate, like `120`:
   - `sx` (small x): 1  
   - `sy` (small y): 2  
   - `sz` (small z): 0  
3. Your move determines which **big cube** the next player must play in.
   - Example: if you place in `(1,2,0)`, the opponent must play in big cube `(1,2,0)`.
4. Win a **3×3×3 cube** by lining up 3 marks (X or O).
5. Win the game by winning 3 cubes in a row — in **any direction** — across the 3D grid!

## 💾 Features

- 🧑‍🤝‍🧑 Named players with personalized turns
- ♻️ Undo your last move with `/undo`
- 💾 Save and load games by name
- 🗂️ Multiple named saves supported
- ❌ `/delete <savename>` to remove a saved game
- 🆕 `/new` to start fresh
- 🧠 `/help` for in-game command list

## Requirements:

- Python 3.6+
- Runs entirely in the terminal — no external libraries required

## How to run the Game

```bash
python3 main.py
