from dataclasses import dataclass
from editor.constants import SCROLL_MARGIN

@dataclass
class Cursor:
    row: int = 0
    col: int = 0
    preferred_col: int = 0
    scroll_x: int = 0
    scroll_y: int = 0
    viewport_rows: int = 24
    viewport_cols: int = 80

    def set_position(self, row: int, col: int):
        self.row = max(0, row)
        self.col = max(0, col)
        self.preferred_col = self.col

    # Raw cursor movements (TextBuffer clamps row/col to text)
    def move_left(self):
        if self.col > 0:
            self.col -= 1
        else:
            if self.row > 0:          # only wrap if not at top
                self.row -= 1
                self.col = 10**9      # let buffer clamp to actual line end
        self.preferred_col = self.col

    def move_right(self):
        self.col += 1
        self.preferred_col = self.col

    def move_up(self):
        self.row -= 1
        self.col = self.preferred_col

    def move_down(self):
        self.row += 1
        self.col = self.preferred_col


    def ensure_visible(self):
        """
        Smooth scrolling: only scroll screen when cursor approaches viewport edges
        instead of snapping immediately.
        """

        # ------- Vertical scrolling -------
        # near top
        if self.row < self.scroll_y + SCROLL_MARGIN:
            self.scroll_y = max(0, self.row - SCROLL_MARGIN)

        # near bottom
        elif self.row >= self.scroll_y + self.viewport_rows - SCROLL_MARGIN:
            self.scroll_y = max(0, self.row - self.viewport_rows + SCROLL_MARGIN + 1)

        # ------- Horizontal scrolling -------
        # near left
        if self.col < self.scroll_x + SCROLL_MARGIN:
            self.scroll_x = max(0, self.col - SCROLL_MARGIN)

        # near right
        elif self.col >= self.scroll_x + self.viewport_cols - SCROLL_MARGIN:
            self.scroll_x = max(0, self.col - self.viewport_cols + SCROLL_MARGIN + 1)
