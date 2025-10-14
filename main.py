import curses

def main(stdscr):
    curses.curs_set(1)
    stdscr.clear()
    stdscr.refresh()

    text = [""]
    row, col = 0, 0

    while True:
        key = stdscr.getch()

        if key == 27:  # ESC to quit
            break

        elif key in (10, 13):  # Enter key
            text.insert(row + 1, "")
            row += 1
            col = 0

        elif key in (curses.KEY_BACKSPACE, 127):
            if col > 0:
                text[row] = text[row][:col-1] + text[row][col:]
                col -= 1
            elif row > 0:
                prev_len = len(text[row-1])
                text[row-1] += text[row]
                text.pop(row)
                row -= 1
                col = prev_len

        elif key == curses.KEY_LEFT:
            col = max(0, col - 1)
        elif key == curses.KEY_RIGHT:
            col = min(len(text[row]), col + 1)
        elif key == curses.KEY_UP:
            row = max(0, row - 1)
            col = min(col, len(text[row]))
        elif key == curses.KEY_DOWN:
            row = min(len(text)-1, row + 1)
            col = min(col, len(text[row]))

        elif 32 <= key <= 126:  # Printable ASCII
            ch = chr(key)
            text[row] = text[row][:col] + ch + text[row][col:]
            col += 1

        # Redraw
        stdscr.clear()
        for i, line in enumerate(text):
            stdscr.addstr(i, 0, line)
        stdscr.move(row, col)
        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)
