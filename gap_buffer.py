class GapBuffer:
    def __init__(self, text=""):
        self.buffer = list(text)
        self.cursor = len(text)

    def insert(self, ch):
        self.buffer.insert(self.cursor, ch)
        self.cursor += 1

    def backspace(self):
        if self.cursor > 0:
            self.cursor -= 1
            self.buffer.pop(self.cursor)


    def move_left(self):
        if self.cursor > 0:
            self.cursor -= 1

    def move_right(self):
        if self.cursor < len(self.buffer):
            self.cursor += 1

    def get_text(self):
        return "".join(self.buffer)

    def __len__(self):
        return len(self.buffer)

    def split_at_cursor(self):
        before = self.get_text()[:self.cursor]
        after = self.get_text()[self.cursor:]
        return GapBuffer(before), GapBuffer(after.lstrip())