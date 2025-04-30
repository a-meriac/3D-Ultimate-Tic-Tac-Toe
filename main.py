# Initialise board: 6D array, filled with "."
board = [[[[[[ "." for _ in range(3)] for _ in range(3)] for _ in range(3)]
            for _ in range(3)] for _ in range(3)] for _ in range(3)]

def mark_cell(x, y, z, turn):
    symbol = "X" if turn % 2 == 0 else "O"
    bx, sx = divmod(x, 3)
    by, sy = divmod(y, 3)
    bz, sz = divmod(z, 3)
    if board[bx][by][bz][sx][sy][sz] == ".":
        board[bx][by][bz][sx][sy][sz] = symbol
        return True
    return False

def printBoard(board):
    for z in range(9):
        print(f"Layer Z={z}")
        for y in range(9):
            row = ""
            for x in range(9):
                bx, sx = divmod(x, 3)
                by, sy = divmod(y, 3)
                bz, sz = divmod(z, 3)
                val = board[bx][by][bz][sx][sy][sz]
                row += str(val) + " "
                if x % 3 == 2 and x != 8:
                    row += "| "
            print(row.strip())
            if y % 3 == 2 and y != 8:
                print("-" * 21)
        print("=" * 21)

def print_cube_coordinates():
    print("Here are the coordinates inside the 3×3×3 cube (format: sx sy sz):")
    for sz in range(3):
        print(f"Layer sz={sz}")
        for sy in range(3):
            row = ""
            for sx in range(3):
                row += f"{sx}{sy}{sz} "
            print(row.strip())
        print("-" * 15)

def user_input(string):
    x = input(string).strip()
    if x == "":
        print("Invalid input.")
        return user_input(string)
    elif x == "/help":
        print("📘 3D Ultimate Tic Tac Toe Help")
        print("Play in a 3×3×3 cube. Each move determines where your opponent plays next.")
        print("Commands:\n  /print - shows the current board\n  /restart - restart the game")
        return user_input(string)
    elif x == "/restart":
        print("Restarting game...\n")
        main()
    elif x == "/print":
        printBoard(board)
        return user_input(string)
    return x

def check_win_in_small_cube(bx, by, bz):
    cube = board[bx][by][bz]
    def get(x, y, z): return cube[x][y][z]
    lines = []
    for i in range(3):
        for j in range(3):
            lines.extend([
                [get(i, j, 0), get(i, j, 1), get(i, j, 2)],
                [get(i, 0, j), get(i, 1, j), get(i, 2, j)],
                [get(0, i, j), get(1, i, j), get(2, i, j)],
            ])
    for i in range(3):
        lines.extend([
            [get(0, 0, i), get(1, 1, i), get(2, 2, i)],
            [get(0, 2, i), get(1, 1, i), get(2, 0, i)],
            [get(0, i, 0), get(1, i, 1), get(2, i, 2)],
            [get(0, i, 2), get(1, i, 1), get(2, i, 0)],
            [get(i, 0, 0), get(i, 1, 1), get(i, 2, 2)],
            [get(i, 0, 2), get(i, 1, 1), get(i, 2, 0)],
        ])
    lines.extend([
        [get(0, 0, 0), get(1, 1, 1), get(2, 2, 2)],
        [get(0, 0, 2), get(1, 1, 1), get(2, 2, 0)],
        [get(0, 2, 0), get(1, 1, 1), get(2, 0, 2)],
        [get(0, 2, 2), get(1, 1, 1), get(2, 0, 0)],
    ])
    for line in lines:
        if line[0] != "." and line.count(line[0]) == 3:
            return line[0]
    return None

def main():
    turn = 0
    current_big = (1, 1, 1)  # Start in center cube

    while True:
        print(f"\n🎮 Turn {turn + 1} — Player {'X' if turn % 2 == 0 else 'O'}")
        bx, by, bz = current_big
        print(f"📦 Play in big cube (big_x={bx}, big_y={by}, big_z={bz})")
        print_cube_coordinates()

        coord_str = user_input("Enter coordinates (sx sy sz as 3 digits, e.g. 120): ")
        if not coord_str or len(coord_str) != 3 or not coord_str.isdigit():
            print("Please enter exactly 3 digits, like 012 or 221.")
            continue

        sx, sy, sz = map(int, coord_str)
        if not all(0 <= d <= 2 for d in [sx, sy, sz]):
            print("Each digit must be 0, 1, or 2.")
            continue

        if not (0 <= sx <= 2 and 0 <= sy <= 2 and 0 <= sz <= 2):
            print("Coordinates must be between 0 and 2.")
            continue

        x = bx * 3 + sx
        y = by * 3 + sy
        z = bz * 3 + sz

        if not mark_cell(x, y, z, turn):
            print("⛔ That square is already taken.")
            continue

        winner = check_win_in_small_cube(bx, by, bz)
        if winner:
            print(f"🏆 Player {winner} has won cube ({bx}, {by}, {bz})!")

        printBoard(board)
        current_big = (sx, sy, sz)
        turn += 1

main()
