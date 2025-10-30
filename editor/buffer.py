# editor/buffer.py
import logging
from typing import List, Tuple

from editor.rope_tree import Rope
from editor.constants import REBALANCE_THRESHOLD
from editor.cursor import Cursor

logger = logging.getLogger(__name__)


class TextBuffer:
    """
    Text model + undo/redo + persistent rope snapshots + rebalance control.
    Cursor is separate inside Cursor class.
    """

    def __init__(self):
        self.text: List[Rope] = [Rope("")]
        self.cursor = Cursor()
        self.undo_stack: List[Tuple[List, int, int]] = []
        self.redo_stack: List[Tuple[List, int, int]] = []
        self.edit_counter = 0  # incremental diff-based performance trigger

    # ---------------- state (undo/redo) -----------------
    def save_state(self) -> None:
        """Snapshot rope roots (structural, O(1) persistence), not full text."""
        self.undo_stack.append(([t.root for t in self.text], self.cursor.row, self.cursor.col))
        self.redo_stack.clear()
        logger.debug("State saved. Undo depth=%d", len(self.undo_stack))

    def restore_state(self, snapshot) -> None:
        nodes, r, c = snapshot
        self.text = [Rope(node) for node in nodes]
        self.cursor.set_position(r, c)
        logger.debug("State restored: row=%d col=%d lines=%d", r, c, len(self.text))

    def undo(self) -> None:
        if not self.undo_stack:
            return
        self.redo_stack.append(([t.root for t in self.text], self.cursor.row, self.cursor.col))
        snapshot = self.undo_stack.pop()
        self.restore_state(snapshot)
        logger.info("Undo applied")

    def redo(self) -> None:
        if not self.redo_stack:
            return
        self.undo_stack.append(([t.root for t in self.text], self.cursor.row, self.cursor.col))
        snapshot = self.redo_stack.pop()
        self.restore_state(snapshot)
        logger.info("Redo applied")

    # ---------------- rebalance -----------------
    def increment_edit_counter(self) -> None:
        self.edit_counter += 1
        if self.edit_counter >= REBALANCE_THRESHOLD:
            logger.info("Rebalancing all lines (edit_counter=%d)", self.edit_counter)
            for i in range(len(self.text)):
                try:
                    self.text[i] = self.text[i].rebalance()
                except Exception:
                    logger.exception("Rebalance failed on line %d", i)
            self.edit_counter = 0

    # ---------------- cursor bounds -----------------
    def clamp_cursor(self) -> None:
        if self.cursor.row < 0:
            self.cursor.row = 0
        elif self.cursor.row >= len(self.text):
            self.cursor.row = len(self.text) - 1

        line_len = len(self.text[self.cursor.row].get_text())
        if self.cursor.col < 0:
            self.cursor.col = 0
        elif self.cursor.col > line_len:
            self.cursor.col = line_len

    def finalize_edit(self) -> None:
        self.clamp_cursor()
        self.cursor.ensure_visible()

    # ---------------- editing ops -----------------
    def insert_char(self, ch: str) -> None:
        r, c = self.cursor.row, self.cursor.col
        self.text[r] = self.text[r].insert(c, ch)
        self.cursor.col += 1
        self.cursor.preferred_col = self.cursor.col
        logger.debug("Inserted '%s' at row=%d col=%d", ch, r, c)
        self.increment_edit_counter()
        self.finalize_edit()

    def backspace_at_cursor(self) -> None:
        r, c = self.cursor.row, self.cursor.col

        if c == 0 and r > 0:  # merge lines
            prev_len = len(self.text[r - 1].get_text())
            self.text[r - 1] = self.text[r - 1].concat(self.text[r])
            del self.text[r]
            self.cursor.row -= 1
            self.cursor.col = prev_len
            logger.debug("Merged line up at row=%d -> row=%d", r, self.cursor.row)
        elif c > 0:  # delete
            self.text[r] = self.text[r].delete(c - 1, c)
            self.cursor.col -= 1
            logger.debug("Deleted char at row=%d col=%d", r, c - 1)

        self.increment_edit_counter()
        self.finalize_edit()

    def split_line_at_cursor(self) -> None:
        r, c = self.cursor.row, self.cursor.col
        left, right = self.text[r].split(c)
        self.text[r] = left
        self.text.insert(r + 1, right)
        self.cursor.row += 1
        self.cursor.col = 0
        logger.debug("Split line at row=%d col=%d", r, c)
        self.increment_edit_counter()
        self.finalize_edit()

    # ---------------- movement -----------------
    def move_cursor_left(self) -> None:
        old_row = self.cursor.row
        self.cursor.move_left()
        self.clamp_cursor()
        if self.cursor.row < old_row:
            self.cursor.col = len(self.text[self.cursor.row].get_text())
        self.cursor.preferred_col = self.cursor.col

    def move_cursor_right(self) -> None:
        old_row = self.cursor.row
        self.cursor.move_right()
        self.clamp_cursor()
        if self.cursor.row > old_row:
            self.cursor.col = 0
        self.cursor.preferred_col = self.cursor.col

    def move_cursor_up(self) -> None:
        if self.cursor.row > 0:
            self.cursor.row -= 1
        self.clamp_cursor()
        line_len = len(self.text[self.cursor.row].get_text())
        self.cursor.col = (self.cursor.preferred_col)

    def move_cursor_down(self) -> None:
        if self.cursor.row < len(self.text) - 1:
            self.cursor.row += 1
        self.clamp_cursor()
        line_len = len(self.text[self.cursor.row].get_text())
        self.cursor.col = min(self.cursor.preferred_col, line_len)

    # ---------------- renderer helpers -----------------
    def get_text_lines(self) -> List[str]:
        return [line.get_text() for line in self.text]

    # ---------------- file I/O -----------------
    def load_file(self, path: str, encoding: str = "utf-8") -> None:
        with open(path, "r", encoding=encoding) as f:
            raw = f.read()

        lines = raw.splitlines()
        if raw.endswith("\n"):
            lines.append("")  # preserve trailing newline

        self.text = [Rope(line) for line in (lines or [""])]
        self.cursor.set_position(0, 0)
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.edit_counter = 0
        logger.info("Loaded %s (%d lines)", path, len(self.text))

    def save_file(self, path: str, encoding: str = "utf-8") -> None:
        with open(path, "w", encoding=encoding) as f:
            f.write("\n".join(line.get_text() for line in self.text))
        logger.info("Saved file %s", path)
