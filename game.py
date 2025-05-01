#!/usr/bin/env python3
# 3-D Ultimate Tic-Tac-Toe (cube-tinted board) — WiseOcelot
# ---------------------------------------------------------
import json, os, re, sys, datetime
from typing import Any

# ──────────────────────────────────────────────────────────
#  ANSI colour helpers  (auto-disable on dumb terminals)
# ──────────────────────────────────────────────────────────
USE_COLOR = sys.stdout.isatty() and os.getenv("TERM") not in (None, "dumb")

def ansi(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text

# base colours
RED, BLUE, CYAN, GREY, YEL = "91", "94", "96", "90", "93;1"

def player_mark(sym: str) -> str:
    if sym == "X": return ansi("X", RED)
    if sym == "O": return ansi("O", BLUE)
    return ansi("·", GREY)

# ─── add just after player_mark() ──────────────────────────────
def axis(lbl: str) -> str:                 # cyan axis labels
    return ansi(lbl, CYAN)

def banner(msg: str) -> str:
    return ansi(msg, YEL)

# 27 gentle tints for cubes (6-bit ANSI “bright” palette)
TINTS = [str(code) for code in (
    36, 37, 38,  33, 34, 35,  92, 93, 94,
    95, 96, 97,  32, 33, 34,  35, 36, 37,
    91, 92, 93,  94, 95, 96,  31, 32, 33)]

def cube_code(bx: int, by: int, bz: int) -> str:
    idx = bz * 9 + by * 3 + bx
    return TINTS[idx % len(TINTS)]

def tint(text: str, bx: int, by: int, bz: int) -> str:
    return ansi(text, cube_code(bx, by, bz))

# ──────────────────────────────────────────────────────────
ASCII_TITLE = r"""
 ╔══════════════════════════════════════════════════════╗
 ║            3-D  ULTIMATE  TIC-TAC-TOE                ║
 ╚══════════════════════════════════════════════════════╝
"""

# ──────────────────────────────────────────────────────────
#  6-D board  board[bigX][bigY][bigZ][localX][localY][localZ]
# ──────────────────────────────────────────────────────────
board = [
    [ [ [ [ [ "." for _ in range(3)] for _ in range(3)] for _ in range(3)]
        for _ in range(3)] for _ in range(3)]
    for _ in range(3)
]
wins = [[[None for _ in range(3)] for _ in range(3)] for _ in range(3)]
move_history: list[dict[str, Any]] = []
players = ["Player X", "Player O"]
save_name: str | None = None

SAVE_DIR = "saves"
os.makedirs(SAVE_DIR, exist_ok=True)

# ──────────────────────────────────────────────────────────
#  Save / load / delete helpers
# ──────────────────────────────────────────────────────────
NAME_OK = re.compile(r"^[A-Za-z0-9_-]{1,30}$").fullmatch
path = lambda n: os.path.join(SAVE_DIR, f"{n}.json")

def save_game():
    global save_name
    if not save_name:
        while True:
            nm = input("Save name (A-Z a-z 0-9 _-): ").strip()
            if NAME_OK(nm): save_name = nm; break
            print("Bad name.")
    with open(path(save_name), "w") as f:
        json.dump(dict(board=board, wins=wins,
                       move_history=move_history, players=players,
                       timestamp=datetime.datetime.now().isoformat()),
                  f, indent=2)

def load_game(nm: str):
    global board, wins, move_history, players, save_name
    with open(path(nm)) as f:
        d = json.load(f)
    board[:] = d["board"]; wins[:] = d["wins"]
    move_history[:] = d["move_history"]; players[:] = d["players"]
    save_name = nm

def list_saves() -> list[str]:
    files = sorted(f[:-5] for f in os.listdir(SAVE_DIR) if f.endswith(".json"))
    for i, nm in enumerate(files, 1):
        try:
            with open(path(nm)) as f: d = json.load(f)
            print(f"{i}. {nm} — {d['players'][0]} vs {d['players'][1]} — turn {len(d['move_history'])}")
        except Exception:
            print(f"{i}. {nm} (corrupt)")
    return files

def delete_save(nm: str):
    if not NAME_OK(nm): print("Bad name."); return
    try: os.remove(path(nm)); print("Deleted.")
    except FileNotFoundError: print("No such save.")

# ──────────────────────────────────────────────────────────
#  Big-cube descriptors
# ──────────────────────────────────────────────────────────
_X_DESC = ["left", "middle", "right"]
_Y_DESC = ["top", "middle", "bottom"]
_Z_DESC = ["front", "middle", "back"]

def describe_cube(bx, by, bz) -> str:
    return f"{_Y_DESC[by]}-{_X_DESC[bx]}-{_Z_DESC[bz]}"

# ──────────────────────────────────────────────────────────
#  Cube availability helpers
# ──────────────────────────────────────────────────────────
def full_cube(bx,by,bz):                      # no empty cell
    return all(board[bx][by][bz][lx][ly][lz]!="."
               for lx in range(3) for ly in range(3) for lz in range(3))

def cube_open(bx,by,bz):
    return wins[bx][by][bz] is None and not full_cube(bx,by,bz)

# ──────────────────────────────────────────────────────────
#  Board display
# ──────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────
#  Coloured 9×9×9 board  (cube-tinted empties, bright marks)
# ──────────────────────────────────────────────────────────
def print_board() -> None:
    for z in range(9):
        print(f"\nLayer z={z}")
        for y in range(9):
            line = []
            for x in range(9):
                bx, lx = divmod(x, 3)
                by, ly = divmod(y, 3)
                bz, lz = divmod(z, 3)

                sym = board[bx][by][bz][lx][ly][lz]

                if sym == ".":                              # empty → tint
                    cell = tint("·", bx, by, bz)
                else:                                        # X or O keep colour
                    cell = player_mark(sym)

                line.append(cell)

                if x % 3 == 2 and x != 8:
                    line.append("|")
            print(" ".join(line))
            if y % 3 == 2 and y != 8:
                print("─" * 21)
        print("═" * 21)

def print_key():
    print("\nCube colour key:")
    for bz in range(3):
        for by in range(3):
            row=[]
            for bx in range(3):
                tag = f"{bx}{by}{bz}"
                colour_tag = tint(tag, bx, by, bz)
                row.append(f"{colour_tag}:{describe_cube(bx,by,bz)}")
            print("  ".join(row))
        print()

def print_cube(bx, by, bz):
    print(f"Cube {bx}{by}{bz} – {describe_cube(bx,by,bz)} (local xyz):")
    for lz in range(3):
        print(f" layer z={lz}")
        for ly in range(3):
            row = [
                # coloured mark OR coloured coordinate
                tint(player_mark(board[bx][by][bz][lx][ly][lz]), bx, by, bz)
                if board[bx][by][bz][lx][ly][lz] != "."
                else tint(axis(f"{lx}{ly}{lz}"), bx, by, bz)
                for lx in range(3)
            ]
            print(" ".join(row))
        print("-" * 18)

# ──────────────────────────────────────────────────────────
#  Move helpers
# ──────────────────────────────────────────────────────────
def mark_cell(gx,gy,gz,turn):
    bx,lx=divmod(gx,3); by,ly=divmod(gy,3); bz,lz=divmod(gz,3)
    if board[bx][by][bz][lx][ly][lz]!=".": return False
    board[bx][by][bz][lx][ly][lz]="X" if turn%2==0 else "O"
    return True

def erase_cell(gx,gy,gz):
    bx,lx=divmod(gx,3); by,ly=divmod(gy,3); bz,lz=divmod(gz,3)
    board[bx][by][bz][lx][ly][lz]="."

# ──────────────────────────────────────────────────────────
#  Win / draw checks (same as earlier)
# ──────────────────────────────────────────────────────────
def cube_lines(c):
    g=lambda x,y,z:c[x][y][z];L=[]
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

def cube_win(bx,by,bz):
    for ln in cube_lines(board[bx][by][bz]):
        if ln[0]!="." and ln.count(ln[0])==3: return ln[0]
    return None

def meta_win(player):
    g=lambda x,y,z:wins[x][y][z]; L=[]
    for i in range(3):
        for j in range(3):
            L+=[[g(i,j,0),g(i,j,1),g(i,j,2)],
                [g(i,0,j),g(i,1,j),g(i,2,j)],
                [g(0,i,j),g(1,i,j),g(2,i,j)]]
    for i in range(3):
        L+=[[g(0,0,i),g(1,1,i),g(2,2,i)],
            [g(0,2,i),g(1,1,i),g(2,0,i)],
            [g(0,i,0),g(1,i,1),g(2,i,2)],
            [g(0,i,2),g(1,i,1),g(2,i,0)],
            [g(i,0,0),g(i,1,1),g(i,2,2)],
            [g(i,0,2),g(i,1,1),g(i,2,0)]]
    L+=[[g(0,0,0),g(1,1,1),g(2,2,2)],
        [g(0,0,2),g(1,1,1),g(2,2,0)],
        [g(0,2,0),g(1,1,1),g(2,0,2)],
        [g(0,2,2),g(1,1,1),g(2,0,0)]]
    return any(all(c==player for c in ln) for ln in L)

def draw():
    return all(wins[bx][by][bz] or full_cube(bx,by,bz)
               for bx in range(3) for by in range(3) for bz in range(3))

# ──────────────────────────────────────────────────────────
#  Command parser
# ──────────────────────────────────────────────────────────
def do_cmd(cmd, turn, current):
    if cmd=="/help":
        print("""
/help            show this text
/print           coloured 9×9×9 board
/key             colour legend for cubes
/saves           list saves
/delete NAME     delete save
/undo            undo last move
"""); return True,current,turn

    if cmd=="/print": print_board(); return True,current,turn
    if cmd=="/key":   print_key();   return True,current,turn
    if cmd=="/saves": list_saves();  return True,current,turn

    if cmd.startswith("/delete "):
        delete_save(cmd.split(maxsplit=1)[1]); return True,current,turn

    if cmd=="/undo":
        if not move_history: print("Nothing to undo."); return True,current,turn
        last=move_history.pop(); erase_cell(last["x"],last["y"],last["z"])
        bx,by,bz = last["x"]//3//3, last["y"]//3//3, last["z"]//3//3
        wins[bx][by][bz]=cube_win(bx,by,bz)
        turn-=1
        current=(1,1,1) if not move_history else move_history[-1]["next_big"]
        save_game(); print("Undone."); return True,current,turn
    return False,current,turn

def choose_open_cube() -> tuple[int, int, int]:
    """Prompt until user enters an open cube XYZ."""
    while True:
        raw = input("Pick any open cube (XYZ 0-2 each): ").strip()
        if not (raw.isdigit() and len(raw) == 3 and all(ch in "012" for ch in raw)):
            print("Use exactly three digits, e.g. 120."); continue
        bx, by, bz = map(int, raw)
        if cube_open(bx, by, bz):
            print(f"You chose cube {bx}{by}{bz} ({describe_cube(bx,by,bz)})")
            return bx, by, bz
        print("That cube is closed. Choose another.")

# ──────────────────────────────────────────────────────────
#  MAIN LOOP
# ──────────────────────────────────────────────────────────
def main():
    global players
    print(ASCII_TITLE)

    # load or new
    names=list_saves()
    if names:
        ch=input("Load save # or 'n' new: ").strip()
        if ch.isdigit() and 1<=int(ch)<=len(names): load_game(names[int(ch)-1])
        elif ch.lower()!="n": print("Bad choice."); return

    if not move_history:
        players[0]=input("Player X name: ").strip() or "Player X"
        players[1]=input("Player O name: ").strip() or "Player O"

    turn=len(move_history)
    current=(1,1,1) if not move_history else move_history[-1]["next_big"]

    while True:
        bx,by,bz = current
        hdr=f" Turn {turn+1} — {players[turn%2]} ({'X' if turn%2==0 else 'O'}) "
        print(banner("\n"+"─"*10+hdr+"─"*10))
        print(f"Cube {bx}{by}{bz} ({describe_cube(bx,by,bz)})")
        print_cube(bx,by,bz)

        entry=input("move (xyz) or command: ").strip()
        if entry.startswith("/"):
            handled,current,turn=do_cmd(entry,turn,current)
            if handled: continue
            print("Unknown command."); continue

        if not(entry.isdigit() and len(entry)==3 and all(ch in "012" for ch in entry)):
            print("Use three digits 0-2."); continue

        lx,ly,lz=map(int,entry)
        gx,gy,gz = bx*3+lx, by*3+ly, bz*3+lz
        if not mark_cell(gx,gy,gz,turn): print("Square occupied."); continue

        win=cube_win(bx,by,bz)
        if win and wins[bx][by][bz] is None:
            wins[bx][by][bz]=win
            print(banner(f"🏆 {players[turn%2]} wins cube {bx}{by}{bz}!"))
            if meta_win(win):
                print(banner(f"🎉 {players[turn%2]} WINS THE GAME!")); save_game(); return

        if draw(): print(banner("🤝 Draw — board filled.")); save_game(); return

        move_history.append(dict(x=gx,y=gy,z=gz,next_big=(lx,ly,lz)))
        save_game()

        # meta snapshot
        meta="".join(wins[bx][by][bz] or "." for bz in range(3)
                                         for by in range(3)
                                         for bx in range(3))
        print("Meta:", " ".join(meta[i:i+9] for i in range(0,27,9)))

        # pick next cube
        next_c=(lx,ly,lz)
        if cube_open(*next_c):
            current=next_c
        else:
            print("Next cube closed — choose any open cube.")
            current=choose_open_cube()

        turn+=1

# ──────────────────────────────────────────────────────────
if __name__=="__main__":
    main()
