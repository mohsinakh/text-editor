# editor/file_manager.py
import curses

class FileManager:
    def __init__(self, buffer):
        self.buffer = buffer
        self.current_file = None

    def prompt(self, stdscr, message):
        curses.echo()
        stdscr.addstr(curses.LINES - 1, 0, " " * (curses.COLS - 1))   # clear last line
        stdscr.addstr(curses.LINES - 1, 0, message)
        stdscr.refresh()
        path = stdscr.getstr(curses.LINES - 1, len(message)).decode()
        curses.noecho()
        return path.strip()

    def save(self, stdscr):
        if not self.current_file:
            self.current_file = self.prompt(stdscr, "Save as: ")

        if self.current_file:
            self.buffer.save_file(self.current_file)

    def open(self, stdscr):
        path = self.prompt(stdscr, "Open file: ")
        if path:
            self.current_file = path
            self.buffer.load_file(path)
