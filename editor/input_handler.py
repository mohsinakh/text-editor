# editor/input_handler.py
import curses
from editor.file_manager import FileManager


# top: constants
CTRL_S = 19   # CTRL+S
CTRL_O = 15   # CTRL+O
CTRL_Q = 17   # CTRL+Q



class InputHandler:
    """
    Handles key input and maps to TextBuffer actions.
    UI key logic stays separate from editing logic.
    """

    def __init__(self, buffer):
        self.buffer = buffer
        self.file_manager = None 
    def handle_key(self, key, stdscr=None):
        # ===== Exit =====
        if key == 27:  # ESC
            return False

        # ===== Undo / Redo =====
        if key == 21:  # Ctrl+U
            self.buffer.undo()
            return True

        if key == 18:  # Ctrl+R
            self.buffer.redo()
            return True

        # ===== File actions =====
        if key in (CTRL_S, 19):  # Ctrl+S
            if self.file_manager:
                self.file_manager.save(stdscr)
            return True
    
        if key in (CTRL_O, curses.KEY_F2):  # Ctrl+O OR F2
            if self.file_manager:
                self.file_manager.open(stdscr)
            return True

        if key in (CTRL_Q, 3):  # Ctrl+Q OR Ctrl+C
            raise KeyboardInterrupt

        # ===== Enter =====
        if key in (10, 13):
            self.buffer.save_state()
            self.buffer.split_line_at_cursor()
            self.buffer.increment_edit_counter()
            return True

        # ===== Backspace =====
        if key in (curses.KEY_BACKSPACE, 127):
            self.buffer.save_state()
            self.buffer.backspace_at_cursor()
            self.buffer.increment_edit_counter()
            return True

        # ===== Cursor Movement =====
        if key == curses.KEY_LEFT:
            self.buffer.move_cursor_left()
            return True
        if key == curses.KEY_RIGHT:
            self.buffer.move_cursor_right()
            return True
        if key == curses.KEY_UP:
            self.buffer.move_cursor_up()
            return True
        if key == curses.KEY_DOWN:
            self.buffer.move_cursor_down()
            return True

        # ===== Printable Characters =====
        if 32 <= key <= 126:
            ch = chr(key)
            self.buffer.save_state()
            self.buffer.insert_char(ch)
            self.buffer.increment_edit_counter()
            return True

        return True
