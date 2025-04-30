#!/usr/bin/env python3
# 3-D Ultimate Tic Tac Toe — WiseOcelot
# https://github.com/a-meriac/3D-Ultimate-Tic-Tac-Toe
# ------------------------------------------------------------------
import json, os, re, sys, datetime
from typing import Any

# ──────────────────────────────────────────────────────────────────
#  Colour helpers
# ──────────────────────────────────────────────────────────────────
def _supports_colour() -> bool:
    return sys.stdout.isatty() and os.getenv("TERM") not in (None, "dumb")

USE_COLOUR = _supports_colour()

def colour(sym: str) -> str:
    if not USE_COLOUR or sym == ".":        # fallback to plain text
        return sym
    return {"X": "\033[91mX\033[0m",        # bright red
            "O": "\033[94mO\033[0m"}.get(sym, sym)

def banner(msg: str) -> str:
    return f"\033[93;1m{msg}\033[0m" if USE_COLOUR else msg   # yellow bold

# ──────────────────────────────────────────────────────────────────
ASCII_TITLE = r"""
 _____  _  ____     _____  ____  ____     _____  ____  _____
/__ __\/ \/   _\   /__ __\/  _ \/   _\   /__ __\/  _ \/  __/
  / \  | ||  / _____ / \  | / \||  / _____ / \  | / \||  \  
  | |  | ||  \_\____\| |  | |-|||  \_\____\| |  | \_/||  /_ 
  \_/  \_/\____/     \_/  \_/ \|\____/     \_/  \____/\____\
"""

# ──────────────────────────────────────────────────────────────────
#  Game data structures
# ──────────────────────────────────────────────────────────────────
# board[bx][by][bz][sx][sy][sz]  where each index ∈ {0,1,2}
board: list[list[list[list[list[list[str]]]]]] = [
    [
        [
            [
                [
                    ["." for _ in range(3)]           # sz
                    for _ in range(3)                 # sy
                ] for _ in range(3)                   # sx
            ] for _ in range(3)                       # bz
        ] for _ in range(3)                           # by
    ] for _ in range(3)                               # bx
]

wins: list[list[list[str | None]]] = [[[None for _ in range(3)] for _ in range(3)] for _ in range(3)]
move_history: list[dict[str, Any]] = []
players = ["Player X", "Player O"]
save_name: str | None = None

SAVE_DIR = "saves"
os.makedirs(SAVE_DIR, exist_ok=True)

# ──────────────────────────────────────────────────────────────────
#  Sanitisation helpers
# ──────────────────────────────────────────────────────────────────
SAVE_RE = re.compile(r"^[A-Za-z0-9_-]{1,30}$")

def valid_save_name(nm: str) -> bool:
    return bool(SAVE_RE.fullmatch(nm))

def prompt_save_name() -> str:
    while True:
        nm = input("Save name (A-Z a-z 0-9 _-, ≤30): ").strip()
        if valid_save_name(nm):
            return nm
        print("Invalid.")

def prompt_player(prompt: str) -> str:
    while True:
        nm = input(prompt).strip()[:20]
        if nm and all(c.isprintable() and c not in "/\\" for c in nm):
            return nm
        print("1-20 printable chars, no / or \\ please.")

# ──────────────────────────────────────────────────────────────────
#  File I/O helpers
# ──────────────────────────────────────────────────────────────────
def path(name: str) -> str:
    return os.path.join(SAVE_DIR, f"{name}.json")

def save_game() -> None:
    global save_name
    if not save_name:
        save_name = prompt_save_name()
    with open(path(save_name), "w") as f:
        json.dump({
            "board": board,
            "wins": wins,
            "move_history": move_history,
            "players": players,
            "timestamp": datetime.datetime.now().isoformat()
        }, f, indent=2)

def load_game(name: str) -> None:
    global board, wins, move_history, players, save_name
    with open(path(name)) as f:
        d = json.load(f)
    board[:]        = d["board"]
    wins[:]         = d["wins"]
    move_history[:] = d["move_history"]
    players[:]      = d["players"]
    save_name       = name

def list_saves() -> list[str]:
    files = sorted(fn[:-5] for fn in os.listdir(SAVE_DIR) if fn.endswith(".json"))
    for idx, nm in enumerate(files, 1):
        try:
            with open(path(nm)) as f:
                d = json.load(f)
            turns = len(d["move_history"])
            print(f"{idx}. {nm} — {d['players'][0]} vs {d['players'][1]} — turn {turns}")
        except Exception:
            print(f"{idx}. {nm} (corrupt)")
    return files

def delete_save(nm: str) -> None:
    if not valid_save_name(nm):
        print("Bad name.")
        return
    try:
        os.remove(path(nm)); print("Deleted.")
    except FileNotFoundError:
        print("No such save.")

# ──────────────────────────────────────────────────────────────────
#  Board utilities
# ──────────────────────────────────────────────────────────────────
def print_cube(bx: int, by: int, bz: int) -> None:
    print(f"Cube ({bx},{by},{bz})  (sxsy sz):")
    for sz in range(3):
        print(f" layer sz={sz}")
        for sy in range(3):
            print(" ".join(
                colour(board[bx][by][bz][sx][sy][sz])
                if board[bx][by][bz][sx][sy][sz] != "."
                else f"{sx}{sy}{sz}"
                for sx in range(3)
            ))
        print("-" * 18)
# ─────────────────────────────────────────────────────────────
#  Pretty 9×9×9 slice view (Tier-1 readable ASCII)
# ─────────────────────────────────────────────────────────────
def pretty_print_layers(current_big: tuple[int, int, int]) -> None:
    """Readable 9×9 slices; highlights the active 3×3×3 cube."""
    bx_h, by_h, bz_h = current_big
    for z in range(9):
        print(f"Layer Z={z}")
        bz, sz = divmod(z, 3)
        for y in range(9):
            by, sy = divmod(y, 3)
            row = []
            for x in range(9):
                bx, sx = divmod(x, 3)
                cell = board[bx][by][bz][sx][sy][sz]
                # Highlight current cube:
                if (bx, by, bz) == (bx_h, by_h, bz_h):
                    cell = f"[{colour(cell)}]"
                else:
                    cell = f" {colour(cell)} "
                row.append(cell)
                if x % 3 == 2 and x != 8:
                    row.append("│")
            print("".join(row))
            if y % 3 == 2 and y != 8:
                print("─" * 35)
        print("═" * 35)

def print_board() -> None:
    for z in range(9):
        print(f"Layer Z={z}")
        for y in range(9):
            row = []
            for x in range(9):
                bx, sx = divmod(x, 3)
                by, sy = divmod(y, 3)
                bz, sz = divmod(z, 3)
                row.append(colour(board[bx][by][bz][sx][sy][sz]))
                if x % 3 == 2 and x != 8:
                    row.append("|")
            print(" ".join(row))
            if y % 3 == 2 and y != 8:
                print("-" * 21)
        print("=" * 21)

def mark_cell(x: int, y: int, z: int, turn: int) -> bool:
    bx, sx = divmod(x,3); by, sy = divmod(y,3); bz, sz = divmod(z,3)
    if board[bx][by][bz][sx][sy][sz] != ".": return False
    board[bx][by][bz][sx][sy][sz] = "X" if turn % 2 == 0 else "O"
    return True

def erase_cell(x: int, y: int, z: int) -> None:
    bx, sx = divmod(x,3); by, sy = divmod(y,3); bz, sz = divmod(z,3)
    board[bx][by][bz][sx][sy][sz] = "."

# ──────────────────────────────────────────────────────────────────
#  Win / draw checks (unchanged logic)
# ──────────────────────────────────────────────────────────────────
def _cube_lines(c):
    g = lambda x,y,z: c[x][y][z]
    L=[]
    for i in range(3):
        for j in range(3):
            L += [
                [g(i,j,0),g(i,j,1),g(i,j,2)],
                [g(i,0,j),g(i,1,j),g(i,2,j)],
                [g(0,i,j),g(1,i,j),g(2,i,j)],
            ]
    for i in range(3):
        L += [
            [g(0,0,i),g(1,1,i),g(2,2,i)],
            [g(0,2,i),g(1,1,i),g(2,0,i)],
            [g(0,i,0),g(1,i,1),g(2,i,2)],
            [g(0,i,2),g(1,i,1),g(2,i,0)],
            [g(i,0,0),g(i,1,1),g(i,2,2)],
            [g(i,0,2),g(i,1,1),g(i,2,0)],
        ]
    L += [
        [g(0,0,0),g(1,1,1),g(2,2,2)],
        [g(0,0,2),g(1,1,1),g(2,2,0)],
        [g(0,2,0),g(1,1,1),g(2,0,2)],
        [g(0,2,2),g(1,1,1),g(2,0,0)],
    ]
    return L

def check_cube_win(bx,by,bz)->str|None:
    for ln in _cube_lines(board[bx][by][bz]):
        if ln[0]!="." and ln.count(ln[0])==3: return ln[0]
    return None

def check_meta_win(player:str)->bool:
    g=lambda x,y,z:wins[x][y][z]
    lines=[]
    for i in range(3):
        for j in range(3):
            lines += [
                [g(i,j,0),g(i,j,1),g(i,j,2)],
                [g(i,0,j),g(i,1,j),g(i,2,j)],
                [g(0,i,j),g(1,i,j),g(2,i,j)],
            ]
    for i in range(3):
        lines += [
            [g(0,0,i),g(1,1,i),g(2,2,i)],
            [g(0,2,i),g(1,1,i),g(2,0,i)],
            [g(0,i,0),g(1,i,1),g(2,i,2)],
            [g(0,i,2),g(1,i,1),g(2,i,0)],
            [g(i,0,0),g(i,1,1),g(i,2,2)],
            [g(i,0,2),g(i,1,1),g(i,2,0)],
        ]
    lines += [
        [g(0,0,0),g(1,1,1),g(2,2,2)],
        [g(0,0,2),g(1,1,1),g(2,2,0)],
        [g(0,2,0),g(1,1,1),g(2,0,2)],
        [g(0,2,2),g(1,1,1),g(2,0,0)],
    ]
    return any(all(c==player for c in ln) for ln in lines)

def cube_full(bx,by,bz)->bool:
    return all(board[bx][by][bz][sx][sy][sz]!="."
               for sx in range(3) for sy in range(3) for sz in range(3))

def is_draw()->bool:
    for bx in range(3):
        for by in range(3):
            for bz in range(3):
                if wins[bx][by][bz] is None and not cube_full(bx,by,bz):
                    return False
    return True

# ──────────────────────────────────────────────────────────────────
#  Command parser
# ──────────────────────────────────────────────────────────────────
def do_command(cmd:str, turn:int, cur_big:tuple[int,int,int]):
    if cmd=="/help":
        print("""
Commands:
/help          show this
/print         9×9×9 board
/saves         list saves
/delete NAME   delete save
/undo          undo last move
""")
        return True, cur_big, turn

    if cmd == "/print":
        pretty_print_layers(cur_big)
        return True, cur_big, turn

    if cmd=="/saves":
        list_saves(); return True, cur_big, turn

    if cmd.startswith("/delete "):
        delete_save(cmd.split(maxsplit=1)[1]); return True, cur_big, turn

    if cmd=="/undo":
        if not move_history: print("Nothing to undo."); return True,cur_big,turn
        last=move_history.pop(); erase_cell(last["x"],last["y"],last["z"])
        lbx,lby,lbz = last["x"]//3//3, last["y"]//3//3, last["z"]//3//3
        wins[lbx][lby][lbz]=check_cube_win(lbx,lby,lbz)
        turn-=1; cur_big=(1,1,1) if not move_history else move_history[-1]["next_big"]
        save_game(); print("Undone."); return True,cur_big,turn

    return False, cur_big, turn

# ──────────────────────────────────────────────────────────────────
def main() -> None:
    global players
    print(ASCII_TITLE if USE_COLOUR else ASCII_TITLE.replace("\033",""))

    names=list_saves()
    if names:
        ch=input("Load # or 'n' new: ").strip()
        if ch.isdigit() and 1<=int(ch)<=len(names):
            load_game(names[int(ch)-1])
        elif ch.lower()!="n": print("Bad choice."); return

    if not move_history:
        players[0]=prompt_player("Player X name: ")
        players[1]=prompt_player("Player O name: ")

    turn=len(move_history)
    cur_big=(1,1,1) if not move_history else move_history[-1]["next_big"]

    while True:
        bx,by,bz=cur_big
        print(f"\nTurn {turn+1} — {players[turn%2]} ({'X' if turn%2==0 else 'O'})")
        print(f"Target cube → ({bx},{by},{bz})")
        print_cube(bx,by,bz)

        entry=input("3 digits or command: ").strip()
        if entry.startswith("/"):
            handled,cur_big,turn=do_command(entry,turn,cur_big)
            if handled: continue
            print("Unknown cmd. /help")
            continue

        if not(entry.isdigit() and len(entry)==3 and all(c in "012" for c in entry)):
            print("Enter three digits 0-2 (e.g. 102)"); continue
        sx,sy,sz=map(int,entry)
        x,y,z=bx*3+sx,by*3+sy,bz*3+sz
        if not mark_cell(x,y,z,turn): print("Taken."); continue

        w=check_cube_win(bx,by,bz)
        if w and wins[bx][by][bz] is None:
            wins[bx][by][bz]=w
            print(banner(f"🏆 {players[turn%2]} wins cube ({bx},{by},{bz})!"))
            if check_meta_win(w):
                print(banner(f"🎉 {players[turn%2]} wins the game!")); save_game(); return

        if is_draw(): print(banner("🤝 Draw!")); save_game(); return

        move_history.append({"x":x,"y":y,"z":z,"next_big":(sx,sy,sz)})
        save_game()

        cur_big=(sx,sy,sz)
        if wins[sx][sy][sz] or cube_full(sx,sy,sz):
            cur_big=(1,1,1)

        turn+=1

# ──────────────────────────────────────────────────────────────────
if __name__=="__main__":
    main()
