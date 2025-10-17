
from gap_buffer import GapBuffer
import curses

def main(stdscr):
    curses.curs_set(1)
    stdscr.clear()
    stdscr.refresh()

    text = [GapBuffer("")]
    row, col = 0, 0
    undo_stack, redo_stack = [], []

    def save_state():
        undo_stack.append(([GapBuffer(line.get_text()) for line in text], row, col))
        redo_stack.clear()

    def undo():
        nonlocal text, row, col
        if undo_stack:
            redo_stack.append(([GapBuffer(line.get_text()) for line in text], row, col))
            snapshot, saved_row, saved_col = undo_stack.pop()
            text = [GapBuffer(line.get_text()) for line in snapshot]
            row, col = saved_row, saved_col
            return text, row, col

    def redo():
        nonlocal text, row, col
        if redo_stack:
            undo_stack.append(([GapBuffer(line.get_text()) for line in text], row, col))
            snapshot, saved_row, saved_col = redo_stack.pop()
            text = [GapBuffer(line.get_text()) for line in snapshot]
            row, col = saved_row, saved_col
            return text, row, col


    while True:
        stdscr.clear()
        for i, line in enumerate(text):
            stdscr.addstr(i, 0, line.get_text())
        stdscr.move(row, col)
        stdscr.refresh()

        key = stdscr.getch()

        if key == 27:  # ESC
            break


        elif key == 21:  # Ctrl+U Undo
            undo()


        elif key == 18:  # Ctrl+R Redo
            redo()


        elif key in (10, 13):  # Enter
            save_state()
            # Split the current line at the actual gap (cursor) position
            before_buf, after_buf = text[row].split_at_cursor()
            text[row] = before_buf
            text.insert(row + 1, after_buf)
            row += 1
            col = 0

        elif key in (curses.KEY_BACKSPACE, 127):
            save_state()
            if col > 0:
                # Normal character deletion
                text[row].backspace()
                col -= 1
            elif row > 0:
                # Merge with previous line if at start of line
                prev_len = len(text[row - 1])
                text[row - 1] = GapBuffer(text[row - 1].get_text() + text[row].get_text())
                del text[row]
                row -= 1
                col = prev_len


        elif key == curses.KEY_LEFT:
            text[row].move_left()
            col = max(0, col - 1)


        elif key == curses.KEY_RIGHT:
            text[row].move_right()
            col = min(len(text[row]), col + 1)


        elif key == curses.KEY_UP:
            row = max(0, row - 1)
            col = min(col, len(text[row]))


        elif key == curses.KEY_DOWN:
            row = min(len(text) - 1, row + 1)
            col = min(col, len(text[row]))


        elif 32 <= key <= 126:
            save_state()
            ch = chr(key)
            text[row].insert(ch)
            col += 1

if __name__ == "__main__":
    curses.wrapper(main)
