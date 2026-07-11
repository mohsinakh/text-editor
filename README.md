# A Text Editor, Built From Scratch

Every developer lives inside a text editor. Almost none have built one.

I wanted to know what actually happens between pressing a key and seeing a character appear — cursor math, undo history, how you edit a 10,000-line file without redrawing the whole screen. So I built a terminal editor in Python, `curses` and nothing else, and refused to take shortcuts on the data structures underneath.

It started life as a `list[str]` and a hand-tracked cursor. It now runs on a **persistent rope tree** with O(log n) edits and undo/redo that costs almost nothing. This README is the short version of how it got there — and how to run it yourself.

> _"The best way to master a data structure is to build something that genuinely needs it."_

<!-- Add a terminal GIF here — it's worth it for a TUI project. Record with asciinema or a screen capture and drop it in screenshots/. -->
<!-- ![demo](screenshots/demo.gif) -->

## What it does

- **Real editing** — type, delete, navigate with arrow keys, split and merge lines
- **Cheap undo/redo** — no full-buffer copies, even on large files
- **Open & save files** — `Ctrl+O` / `Ctrl+S`, straight from the terminal
- **Smooth scrolling** — edit files taller than your terminal; the viewport follows the cursor
- **Modular core** — the text engine is fully decoupled from rendering and input, so the interesting part is reusable

## The interesting part: how the text is stored

This is the whole reason the project exists, so it's worth walking through how the storage evolved — because each version failed in a way that taught me why the next one existed.

**v1 — a list of strings.** Dead simple, works instantly. But inserting into the middle of a line is O(n), and every keystroke had to deep-copy the entire buffer to support undo. Great for a weekend demo, useless for understanding anything.

**v2 — a gap buffer per line.** Keeps a movable "gap" where the cursor is, so local edits are cheap. This is roughly what older editors used. Better, but undo was still copying whole lines around.

**v3 — a persistent rope tree.** This is where it got fun. Each line is a rope: a balanced binary tree whose leaves hold small chunks of text. Edits don't *mutate* the tree — they produce a **new version that shares every untouched node with the old one.** That single property buys two things almost for free:

- **Edits are O(log n)** instead of O(n) — insert, delete, split, and concat all just restructure a few nodes
- **Undo/redo is free** — "undo" is just keeping a reference to the previous root. No copying, no snapshots

On top of that:
- A **periodic rebalancer** keeps ropes from skewing during long editing sessions, holding access at average-case O(log n) even after thousands of edits
- A **small-leaf optimization** mutates leaves under ~64 characters in place instead of splitting them, so typing stays snappy and the tree stays shallow

This is, in miniature, how editors like Sublime Text and VS Code manage document history under the hood.

## Controls

| Key | Action |
|-----|--------|
| Type / Enter / Backspace | Edit text |
| Arrow keys | Move cursor |
| `Ctrl + S` | Save file |
| `Ctrl + O` | Open file |
| `Ctrl + U` | Undo |
| `Ctrl + R` | Redo |
| `Ctrl + Q` | Quit |

## Run it

```bash
git clone https://github.com/mohsinakh/text-editor.git
cd text-editor
python3 main.py       # Windows: python main.py
```

On Windows, install the curses backend first:
```bash
pip install windows-curses
```

## How it's organized

```
editor/
├── buffer.py         # the rope + cursor logic — the heart of the thing
├── renderer.py       # screen drawing + viewport scrolling
├── input_handler.py  # key bindings and command dispatch
├── file_manager.py   # open / save
└── editor.py         # the main event loop
main.py               # entry point
test_gap.py           # gap-buffer tests
```

The point of the split: `buffer.py` doesn't know the screen exists, and `renderer.py` doesn't know how text is stored. You could swap the curses front-end for a Qt one without touching the text engine.

## What building this actually taught me

| Feature | The real problem underneath | What solves it |
|---------|-----------------------------|----------------|
| Undo / redo | Cheap state history | Structural sharing (persistent trees) |
| Editing large lines | O(1)-ish mutation | Rope tree / gap buffer |
| Scrolling big files | Don't redraw everything | Windowed rendering |
| Cursor navigation | Track position across edits | Explicit cursor state synced to the buffer |

Turns out "just a text editor" quietly forces you to think like a compiler (parsing and managing buffers), a systems person (I/O and memory), and a UX engineer (making it feel instant) all at once. That combination is exactly what I was after.

## Where I'd take it next

- **Search & replace** with KMP
- **Copy / paste** and word-jump navigation
- **Syntax highlighting**
- A **GUI port** to PySide6/Qt, reusing the existing rope engine untouched

## License

MIT — learn from it, fork it, tear it apart.

---

Built by **Mohsin Abbas** · [Portfolio](https://mohsinkhan.online) · [LinkedIn](https://www.linkedin.com/in/mohsin-abbas-7252b126b)
