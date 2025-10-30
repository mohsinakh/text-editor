import curses
import logging
from editor.buffer import TextBuffer
from editor.render import Renderer
from editor.input_handler import InputHandler
from editor.file_manager import FileManager

logging.basicConfig(filename="editor.log", level=logging.INFO, format="%(asctime)s - %(message)s")

def main(stdscr):
    curses.curs_set(1)
    stdscr.clear()
    stdscr.refresh()

    buffer = TextBuffer()
    renderer = Renderer(stdscr, buffer)
    handler = InputHandler(buffer)
    handler.file_manager = FileManager(buffer)

    while True:
        try:
            renderer.render()
            key = stdscr.getch()
            if key == 27:  # ESC
                break
            handler.handle_key(key, stdscr)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    curses.wrapper(main)
