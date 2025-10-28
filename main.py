# main.py (with periodic rebalancer)
from rope_tree import Rope
import curses
import logging

logging.basicConfig(filename="editor.log", level=logging.INFO, format="%(asctime)s - %(message)s")

REBALANCE_THRESHOLD = 200  #  higher = rebalance less often

def main(stdscr):
    curses.curs_set(1)
    stdscr.clear()
    stdscr.refresh()

    text = [Rope("")]
    row, col = 0, 0
    undo_stack, redo_stack = [], []

    edit_counter = 0  # counts mutating edits (insert/delete/split/merge)

    def maybe_rebalance_all():
        nonlocal edit_counter, text
        if edit_counter >= REBALANCE_THRESHOLD:
            logging.info("Rebalancing all lines (edit_counter=%d)", edit_counter)
            for i in range(len(text)):
                try:
                    text[i] = text[i].rebalance()
                except Exception as e:
                    logging.exception("Rebalance failed on line %d: %s", i, e)
            edit_counter = 0

    def save_state():
        # Store structural reference (no deep copy)
        undo_stack.append(([t.root for t in text], row, col))
        redo_stack.clear()
        logging.info("State saved. Undo depth: %d", len(undo_stack))

    def restore_state(snapshot):
        nonlocal text, row, col
        nodes, row, col = snapshot
        text = [Rope(node) for node in nodes]

    def undo():
        if undo_stack:
            redo_stack.append(([t.root for t in text], row, col))
            snapshot = undo_stack.pop()
            restore_state(snapshot)
            logging.info("Undo applied")

    def redo():
        if redo_stack:
            undo_stack.append(([t.root for t in text], row, col))
            snapshot = redo_stack.pop()
            restore_state(snapshot)
            logging.info("Redo applied")

    while True:
        stdscr.clear()
        for i, line in enumerate(text):
            # guard against narrow terminals
            try:
                stdscr.addstr(i, 0, line.get_text())
            except curses.error:
                pass
        stdscr.move(row, col)
        stdscr.refresh()

        key = stdscr.getch()
        if key == 27:  # ESC
            break

        elif key == 21:  # Ctrl+U
            undo()
        elif key == 18:  # Ctrl+R
            redo()

        elif key in (10, 13):  # Enter (split line)
            save_state()
            left, right = text[row].split(col)
            text[row] = left
            text.insert(row + 1, right)
            row += 1
            col = 0
            edit_counter += 1
            logging.info("Enter -> split line (row=%d)", row)
            maybe_rebalance_all()

        elif key in (curses.KEY_BACKSPACE, 127):
            if col == 0 and row > 0:
                save_state()
                prev_text = text[row - 1].get_text()
                merged = text[row - 1].concat(text[row])
                text[row - 1] = merged
                del text[row]
                row -= 1
                col = len(prev_text)
                edit_counter += 1
                logging.info("Merged line %d", row)
                maybe_rebalance_all()
            elif col > 0:
                save_state()
                text[row] = text[row].delete(col - 1, col)
                col -= 1
                edit_counter += 1
                logging.info("Deleted char at row %d col %d", row, col)
                maybe_rebalance_all()

        elif key == curses.KEY_LEFT:
            col = max(0, col - 1)
        elif key == curses.KEY_RIGHT:
            col = min(len(text[row].get_text()), col + 1)
        elif key == curses.KEY_UP:
            row = max(0, row - 1)
            col = min(col, len(text[row].get_text()))
        elif key == curses.KEY_DOWN:
            row = min(len(text) - 1, row + 1)
            col = min(col, len(text[row].get_text()))

        elif 32 <= key <= 126:
            save_state()
            ch = chr(key)
            text[row] = text[row].insert(col, ch)
            col += 1
            edit_counter += 1
            logging.info("Inserted '%s' at row %d col %d", ch, row, col)
            maybe_rebalance_all()

if __name__ == "__main__":
    curses.wrapper(main)
