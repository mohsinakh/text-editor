# editor/render.py
import curses

class Renderer:
    """
    Renders only the visible viewport of the TextBuffer using cursor.scroll_x/scroll_y
    and keeps a screen cache of lines to perform incremental updates.
    """

    def __init__(self, stdscr, buffer):
        self.stdscr = stdscr
        self.buffer = buffer
        self.screen_cache = []

        # initialize viewport sizes from terminal
        h, w = stdscr.getmaxyx()
        self.buffer.cursor.viewport_rows = max(1, h - 1)  # reserve maybe 1 row for status
        self.buffer.cursor.viewport_cols = max(10, w - 1)

    def render(self):
        # ensure cursor visible inside buffer
        self.buffer.cursor.ensure_visible()

        top = self.buffer.cursor.scroll_y
        left = self.buffer.cursor.scroll_x
        rows = self.buffer.cursor.viewport_rows
        cols = self.buffer.cursor.viewport_cols

        text = self.buffer.text

        # ensure cache length
        if len(self.screen_cache) < len(text):
            self.screen_cache.extend([""] * (len(text) - len(self.screen_cache)))

        for i in range(top, min(len(text), top + rows)):
            line_index = i
            rope = text[line_index]
            full_line = rope.get_text()
            # take viewport slice horizontally
            visible = full_line[left:left + cols]

            cache_index = line_index - top
            if cache_index >= len(self.screen_cache):
                # ensure we don't index incorrectly
                self.screen_cache.append("")

            if visible != self.screen_cache[line_index]:
                try:
                    self.stdscr.move(line_index - top, 0)
                    self.stdscr.clrtoeol()
                    self.stdscr.addstr(line_index - top, 0, visible)
                    self.screen_cache[line_index] = visible
                except curses.error:
                    pass

        # clear remaining cached rows visible previously if now gone
        # (simple approach: clear the rest of the terminal window area)
        h, w = self.stdscr.getmaxyx()
        for rr in range(min(rows, h)):
            try:
                # If we are past buffer length, clear
                real_line = top + rr
                if real_line >= len(text):
                    self.stdscr.move(rr, 0)
                    self.stdscr.clrtoeol()
            except curses.error:
                pass

        # Move cursor to (cursor.row - top, cursor.col - left)
        try:
            self.stdscr.move(self.buffer.cursor.row - top, self.buffer.cursor.col - left)
        except curses.error:
            # out of viewport or tiny terminal; ignore
            pass

        self.stdscr.refresh()
