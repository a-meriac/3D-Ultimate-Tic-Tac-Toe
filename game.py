#!/usr/bin/env python3
# 3-D Ultimate Tic Tac Toe — WiseOcelot
# https://github.com/a-meriac/3D-Ultimate-Tic-Tac-Toe
# ------------------------------------------------------------------
import json, os, re, sys, datetime
from typing import Any

# ────────────────────────────────────────────────────────────────
#  ANSI-colour helpers
# ────────────────────────────────────────────────────────────────
def _supports_colour() -> bool:
    return sys.stdout.isatty() and os.getenv("TERM") not in (None, "dumb")

USE_COLOUR = _supports_colour()

def colour(sym: str) -> str:
    """Colour X (red), O (blue), empty (dim)."""
    if not USE_COLOUR:
        return sym
    table = {"X": "\033[91mX\033[0m",        # bright red
             "O": "\033[94mO\033[0m",        # bright blue
             ".": "\033[90m·\033[0m"}        # dim middot
    return table.get(sym, sym)

def coord(txt: str) -> str:                  # cyan axis/coords
    return f"\033[96m{txt}\033[0m" if USE_COLOUR else txt

def br(txt: str) -> str:                     # green brackets
    return f"\033[92m{txt}\033[0m" if USE_COLOUR else txt

def banner(msg: str) -> str:                 # yellow bold
    return f"\033[93;1m{msg}\033[0m" if USE_COLOUR else msg

# ────────────────────────────────────────────────────────────────
ASCII_TITLE = r"""
 _____  _  ____     _____  ____  ____     _____  ____  _____
/__ __\/ \/   _\   /__ __\/  _ \/   _\   /__ __\/  _ \/  __/
  / \  | ||  / _____ / \  | / \||  / _____ / \  | / \||  \  
  | |  | ||  \_\____\| |  | |-|||  \_\____\| |  | \_/||  /_ 
  \_/  \_/\____/     \_/  \_/ \|\____/     \_/  \____/\____\
"""

# ────────────────────────────────────────────────────────────────
#  6-D game board  board[bigX][bigY][bigZ][localX][localY][localZ]
# ────────────────────────────────────────────────────────────────
board: list[list[list[list[list[list[str]]]]]] = [
    [
        [
            [
                [
                    ["." for _ in range(3)]           # localZ
                    for _ in range(3)                 # localY
                ] for _ in range(3)                   # localX
            ] for _ in range(3)                       # bigZ
        ] for _ in range(3)                           # bigY
    ] for _ in range(3)                               # bigX
]

wins: list[list[list[str | None]]] = [[[None for _ in range(3)]
                                       for _ in range(3)]
                                      for _ in range(3)]

move_history: list[dict[str, Any]] = []
players = ["Player X", "Player O"]
save_name: str | None = None

SAVE_DIR = "saves"
os.makedirs(SAVE_DIR, exist_ok=True)

# ────────────────────────────────────────────────────────────────
#  Sanitisation helpers
# ────────────────────────────────────────────────────────────────
SAVE_RE = re.compile(r"^[A-Za-z0-9_-]{1,30}$")

def valid_save_name(nm: str) -> bool:
    return bool(SAVE_RE.fullmatch(nm))

def prompt_save_name() -> str:
    while True:
        nm = input("Save name (A-Z a-z 0-9 _-, ≤30): ").strip()
        if valid_save_name(nm):
            return nm
        print("Invalid name.")

def prompt_player(prompt: str) -> str:
    while True:
        nm = input(prompt).strip()[:20]
        if nm and all(c.isprintable() and c not in "/\\" for c in nm):
            return nm
        print("1-20 printable characters please (no / or \\).")

# ────────────────────────────────────────────────────────────────
#  File I/O helpers
# ────────────────────────────────────────────────────────────────
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
            print(f"{idx}. {nm} — {d['players'][0]} vs {d['players'][1]} — turn {len(d['move_history'])}")
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

# ────────────────────────────────────────────────────────────────
#  Board utilities
# ────────────────────────────────────────────────────────────────
def print_cube(bx: int, by: int, bz: int) -> None:
    print(f"Cube {bx}{by}{bz}  (local x y z):")
    for lz in range(3):
        print(f" layer z={lz}")
        for ly in range(3):
            print(" ".join(
                colour(board[bx][by][bz][lx][ly][lz])
                if board[bx][by][bz][lx][ly][lz] != "."
                else coord(f"{lx}{ly}{lz}")
                for lx in range(3)
            ))
        print("-" * 18)

# ────────────────────────────────────────────────────────────────
#  Pretty slice view  (axis labels, slab spacing, colours)
# ────────────────────────────────────────────────────────────────
def pretty_print_layers(active: tuple[int, int, int]) -> None:
    ax, ay, az = active
    header = "    " + " ".join(coord(f"{i:2}") for i in range(9))  # x-axis
    for z in range(9):
        print(f"\nLayer z={z}")
        print(header)
        bigZ, lz = divmod(z, 3)
        for y in range(9):
            bigY, ly = divmod(y, 3)
            row = [coord(f"{y:2} ")]                                # y-axis label
            for x in range(9):
                bigX, lx = divmod(x, 3)
                cell = board[bigX][bigY][bigZ][lx][ly][lz]
                cell = colour(cell if cell != "." else ".")
                if (bigX, bigY, bigZ) == (ax, ay, az):
                    cell = br(f"[{cell}]")
                else:
                    cell = f" {cell} "
                row.append(cell)
                if x % 3 == 2 and x != 8:
                    row.append("│")
            print("".join(row))
            if y % 3 == 2 and y != 8:
                print("   │───┼───┼───│")
        if z in (2, 5):                 # slab spacing between z=2,5
            print()
    print("Legend: [] active cube • X red • O blue • · empty")

# ----------------------------------------------------------------
def mark_cell(gx: int, gy: int, gz: int, turn: int) -> bool:
    bigX,lx = divmod(gx,3); bigY,ly = divmod(gy,3); bigZ,lz = divmod(gz,3)
    if board[bigX][bigY][bigZ][lx][ly][lz] != ".": return False
    board[bigX][bigY][bigZ][lx][ly][lz] = "X" if turn % 2 == 0 else "O"
    return True

def erase_cell(gx: int, gy: int, gz: int) -> None:
    bigX,lx = divmod(gx,3); bigY,ly = divmod(gy,3); bigZ,lz = divmod(gz,3)
    board[bigX][bigY][bigZ][lx][ly][lz] = "."

# ───────────────────── cube win / meta win / draw checks ─────────────────────
def _cube_lines(c):
    g = lambda x,y,z: c[x][y][z]; L=[]
    for i in range(3):
        for j in range(3):
            L += [[g(i,j,0),g(i,j,1),g(i,j,2)],
                  [g(i,0,j),g(i,1,j),g(i,2,j)],
                  [g(0,i,j),g(1,i,j),g(2,i,j)]]
    for i in range(3):
        L += [[g(0,0,i),g(1,1,i),g(2,2,i)],
              [g(0,2,i),g(1,1,i),g(2,0,i)],
              [g(0,i,0),g(1,i,1),g(2,i,2)],
              [g(0,i,2),g(1,i,1),g(2,i,0)],
              [g(i,0,0),g(i,1,1),g(i,2,2)],
              [g(i,0,2),g(i,1,1),g(i,2,0)]]
    L += [[g(0,0,0),g(1,1,1),g(2,2,2)],
          [g(0,0,2),g(1,1,1),g(2,2,0)],
          [g(0,2,0),g(1,1,1),g(2,0,2)],
          [g(0,2,2),g(1,1,1),g(2,0,0)]]
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
            lines+=[[g(i,j,0),g(i,j,1),g(i,j,2)],
                    [g(i,0,j),g(i,1,j),g(i,2,j)],
                    [g(0,i,j),g(1,i,j),g(2,i,j)]]
    for i in range(3):
        lines+=[[g(0,0,i),g(1,1,i),g(2,2,i)],
                [g(0,2,i),g(1,1,i),g(2,0,i)],
                [g(0,i,0),g(1,i,1),g(2,i,2)],
                [g(0,i,2),g(1,i,1),g(2,i,0)],
                [g(i,0,0),g(i,1,1),g(i,2,2)],
                [g(i,0,2),g(i,1,1),g(i,2,0)]]
    lines+=[[g(0,0,0),g(1,1,1),g(2,2,2)],
            [g(0,0,2),g(1,1,1),g(2,2,0)],
            [g(0,2,0),g(1,1,1),g(2,0,2)],
            [g(0,2,2),g(1,1,1),g(2,0,0)]]
    return any(all(c==player for c in ln) for ln in lines)

def cube_full(bx,by,bz)->bool:
    return all(board[bx][by][bz][lx][ly][lz]!="."
               for lx in range(3) for ly in range(3) for lz in range(3))

def is_draw()->bool:
    for bx in range(3):
        for by in range(3):
            for bz in range(3):
                if wins[bx][by][bz] is None and not cube_full(bx,by,bz):
                    return False
    return True

# ────────────────────────────────────────────────────────────────
#  Command parser
# ────────────────────────────────────────────────────────────────
def do_command(cmd:str, turn:int, cur_big:tuple[int,int,int]):
    if cmd=="/help":
        print("""
Commands:
/help          show this
/print         pretty 9×9×9 view
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
        if not move_history:
            print("Nothing to undo."); return True,cur_big,turn
        last=move_history.pop(); erase_cell(last["x"],last["y"],last["z"])
        lbx,lby,lbz = last["x"]//3//3, last["y"]//3//3, last["z"]//3//3
        wins[lbx][lby][lbz]=check_cube_win(lbx,lby,lbz)
        turn-=1; cur_big=(1,1,1) if not move_history else move_history[-1]["next_big"]
        save_game(); print("Undone."); return True,cur_big,turn
    return False, cur_big, turn

# ────────────────────────────────────────────────────────────────
def meta_snapshot()->None:
    meta="".join(wins[bx][by][bz] or "." for bz in range(3)
                                       for by in range(3)
                                       for bx in range(3))
    lines=[meta[i:i+9] for i in range(0,27,9)]
    print("Meta-board:", " | ".join(lines))

# ────────────────────────────────────────────────────────────────
def main() -> None:
    global players
    print(ASCII_TITLE if USE_COLOUR else ASCII_TITLE.replace("\033",""))

    existing=list_saves()
    if existing:
        ch=input("Load # or 'n' new: ").strip()
        if ch.isdigit() and 1<=int(ch)<=len(existing):
            load_game(existing[int(ch)-1])
        elif ch.lower()!="n":
            print("Bad choice."); return

    if not move_history:
        players[0]=prompt_player("Player X name: ")
        players[1]=prompt_player("Player O name: ")

    turn=len(move_history)
    cur_big=(1,1,1) if not move_history else move_history[-1]["next_big"]

    while True:
        bigX,bigY,bigZ=cur_big
        hdr=f" Turn {turn+1} — {players[turn%2]} ({'X' if turn%2==0 else 'O'}) "
        print(banner("\n──────────"+hdr+"──────────"))
        print(f"Target cube → ({bigX}{bigY}{bigZ})")
        print_cube(bigX,bigY,bigZ)

        entry=input("Move (lx ly lz) or command: ").strip()
        if entry.startswith("/"):
            handled,cur_big,turn=do_command(entry,turn,cur_big)
            if handled: continue
            print("Unknown cmd. /help"); continue

        if not(entry.isdigit() and len(entry)==3 and all(c in "012" for c in entry)):
            print("Enter three digits 0-2 (e.g. 102)"); continue
        lx,ly,lz=map(int,entry)
        gx,gy,gz=bigX*3+lx, bigY*3+ly, bigZ*3+lz
        if not mark_cell(gx,gy,gz,turn):
            print("Square taken."); continue

        winner=check_cube_win(bigX,bigY,bigZ)
        if winner and wins[bigX][bigY][bigZ] is None:
            wins[bigX][bigY][bigZ]=winner
            print(banner(f"🏆 {players[turn%2]} wins cube {bigX}{bigY}{bigZ}!"))
            if check_meta_win(winner):
                print(banner(f"🎉 {players[turn%2]} WINS the game!")); save_game(); return

        if is_draw(): print(banner("🤝 Draw — board full.")); save_game(); return

        move_history.append({"x":gx,"y":gy,"z":gz,"next_big":(lx,ly,lz)})
        save_game()
        meta_snapshot()

        cur_big=(lx,ly,lz)
        if wins[lx][ly][lz] or cube_full(lx,ly,lz):
            cur_big=(1,1,1)

        turn+=1

# ────────────────────────────────────────────────────────────────
if __name__=="__main__":
    main()
