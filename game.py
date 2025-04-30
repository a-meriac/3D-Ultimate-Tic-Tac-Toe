#Made by WiseOcelot
#https://github.com/a-meriac/3D-Ultimate-Tic-Tac-Toe

import os
import json
import datetime

SAVE_DIR = "saves"
os.makedirs(SAVE_DIR, exist_ok=True)

# ========== ASCII Title ========== #
ASCII_TITLE = r"""
 _____  _  ____     _____  ____  ____     _____  ____  _____
/__ __\/ \/   _\   /__ __\/  _ \/   _\   /__ __\/  _ \/  __/
  / \  | ||  / _____ / \  | / \||  / _____ / \  | / \||  \  
  | |  | ||  \_\____\| |  | |-|||  \_\____\| |  | \_/||  /_ 
  \_/  \_/\____/     \_/  \_/ \|\____/     \_/  \____/\____\                                                         
"""

# ========== Game State ========== #
board = [[[[["." for _ in range(3)] for _ in range(3)] for _ in range(3)]
          for _ in range(3)] for _ in range(3)]
wins = [[[None for _ in range(3)] for _ in range(3)] for _ in range(3)]
move_history = []
players = ["Player 1", "Player 2"]
save_name = None

# ========== File Save / Load ========== #
def get_save_path(name):
    return os.path.join(SAVE_DIR, f"{name}.json")

def save_game():
    global save_name
    if not save_name:
        save_name = input("Enter a name for your save file: ").strip()
    data = {
        "board": board,
        "wins": wins,
        "move_history": move_history,
        "players": players,
        "timestamp": datetime.datetime.now().isoformat()
    }
    with open(get_save_path(save_name), "w") as f:
        json.dump(data, f, indent=2)

def load_game(name):
    global board, wins, move_history, players, save_name
    with open(get_save_path(name), "r") as f:
        data = json.load(f)
        board = data["board"]
        wins = data["wins"]
        move_history = data["move_history"]
        players = data["players"]
        save_name = name

def list_saves():
    saves = [f for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
    for i, filename in enumerate(sorted(saves)):
        path = os.path.join(SAVE_DIR, filename)
        with open(path) as f:
            try:
                data = json.load(f)
                ts = data.get("timestamp", "unknown")
                p1 = data.get("players", ["?", "?"])[0]
                p2 = data.get("players", ["?", "?"])[1]
                turns = len(data.get("move_history", []))
                print(f"{i + 1}. {filename[:-5]} — {p1} vs {p2} — Turn {turns} — Saved: {ts}")
            except:
                print(f"{i + 1}. {filename[:-5]} (Corrupt or unreadable)")
    return [f[:-5] for f in saves]

def delete_save(name):
    path = get_save_path(name)
    if os.path.exists(path):
        os.remove(path)
        print(f"Save '{name}' deleted.")
    else:
        print(f"Save '{name}' not found.")

# ========== Helper Functions ========== #
def user_command(x):
    if x == "/help":
        print("""
Commands:
  /help        - Show this help message
  /print       - Print the full 3D board
  /restart     - Restart and re-enter player names
  /new         - Start a brand new game
  /undo        - Undo the last move
  /delete NAME - Delete a saved game by name
        """)
        return True
    elif x == "/print":
        printBoard()
        return True
    return False

def main():
    print(ASCII_TITLE)
    saves = list_saves()
    if saves:
        choice = input("Type number to load, or 'n' for new: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(saves):
            load_game(saves[int(choice) - 1])
        elif choice.lower() == 'n':
            pass
        else:
            print("Invalid choice.")
            return main()

    if not move_history:
        players[0] = input("Enter name for Player X: ").strip() or "Player X"
        players[1] = input("Enter name for Player O: ").strip() or "Player O"

    turn = len(move_history)
    current_big = (1, 1, 1) if not move_history else move_history[-1]["next_big"]

    while True:
        print(f"\nTurn {turn + 1} — {players[turn % 2]} ({'X' if turn % 2 == 0 else 'O'})")
        bx, by, bz = current_big
        print(f"📦 Play in big cube (big_x={bx}, big_y={by}, big_z={bz})")
        print_cube_coordinates(bx, by, bz)

        move = input("Enter move (sxsy sz as 3 digits or command): ").strip()
        if move.startswith("/"):
            if not user_command(move):
                print("Unknown command. Type /help for options.")
            continue

        if not move.isdigit() or len(move) != 3:
            print("Invalid format. Use 3 digits, e.g., 120")
            continue

        sx, sy, sz = map(int, move)
        if not all(0 <= n < 3 for n in (sx, sy, sz)):
            print("Digits must be in range 0–2")
            continue

        x = bx * 3 + sx
        y = by * 3 + sy
        z = bz * 3 + sz

        if not mark_cell(x, y, z, turn):
            print("That square is already taken.")
            continue

        winner = check_win_in_small_cube(bx, by, bz)
        if winner and not wins[bx][by][bz]:
            wins[bx][by][bz] = winner
            print(f"🏆 {players[turn % 2]} won cube ({bx},{by},{bz})!")
            if check_meta_win(winner):
                print(f"🎉 {players[turn % 2]} wins the entire game!")
                return

        move_history.append({"x": x, "y": y, "z": z, "next_big": (sx, sy, sz)})
        save_game()  # Save after every move
        current_big = (sx, sy, sz) if not wins[sx][sy][sz] else (1, 1, 1)
        turn += 1
        save_game()

main()
