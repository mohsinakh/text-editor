from gap_buffer import GapBuffer

buf = GapBuffer("Hello")
print("Start:", buf.get_text())
# print(buf.buffer)

buf.insert('!')
print("Insert:", buf.get_text())
# print(buf.buffer)

buf.move_left()
buf.insert('X')
print("Move left + insert:", buf.get_text())
# print(buf.buffer)

buf.backspace()
print("Backspace:", buf.get_text())
# print(buf.buffer)
