class GapBuffer:
    def __init__(self, initial_text="", gap_size=10):
        self.buffer = list(initial_text) + [""] * gap_size
        self.gap_start = len(initial_text)
        self.gap_end = len(initial_text) + gap_size

    def _resize_gap(self, new_size):
        """Expand gap when full"""
        extra_space = [""] * new_size
        self.buffer = self.buffer[:self.gap_start] + extra_space + self.buffer[self.gap_end:]
        self.gap_end += new_size

    def insert(self, ch):
        """Insert a character at the cursor"""
        if self.gap_start == self.gap_end:
            self._resize_gap(10)
        self.buffer[self.gap_start] = ch
        self.gap_start += 1


    def move_left(self):
        """Move cursor left (shift gap left by one character)"""
        if self.gap_start > 0:
            self.gap_start -= 1
            self.gap_end -= 1
            self.buffer[self.gap_end] = self.buffer[self.gap_start]
            self.buffer[self.gap_start] = ""


    def move_right(self):
        """Move cursor right"""
        if self.gap_end < len(self.buffer):
            self.buffer[self.gap_start] = self.buffer[self.gap_end]
            self.buffer[self.gap_end] = ""
            self.gap_start += 1
            self.gap_end += 1

    def backspace(self):
        """Delete character before cursor"""
        if self.gap_start > 0:
            self.gap_start -= 1
            self.buffer[self.gap_start] = ""

    def get_text(self):
        """Return actual text (without gap)"""
        return "".join(self.buffer[:self.gap_start] + self.buffer[self.gap_end:])

    def __len__(self):
        """Return visible text length"""
        return len(self.buffer) - (self.gap_end - self.gap_start)


            
    def split_at_cursor(self):
        """Split buffer into two new GapBuffers at the current cursor position"""
        before = "".join(self.buffer[:self.gap_start])
        after = "".join(self.buffer[self.gap_end:])
        return GapBuffer(before), GapBuffer(after)