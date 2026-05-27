# Lumen Garden Asset Slots

The prototype uses prepared flower and lantern sprites when available, while the
board currently remains procedurally drawn. It falls back to procedural shapes
when an optional visual or audio file is absent. Add production garden assets at
these paths:

```text
assets/
  sprites/        flowers, lantern spirit, board candidates, petals, fireflies
  ui/             journal panels, puzzle cards, logo treatments
  fonts/          licensed TTF/OTF fonts, optional
  music/
    music_menu.mp3
    music_puzzle.mp3
  sfx/
    move.wav
    grow.wav
    reject.wav
    win.wav
    lose.wav
    select.wav
```

`AudioManager` detects files at startup; missing audio is intentionally silent.

## Prepared Production Sources

Runtime-ready transparent images currently loaded on the puzzle board:

```text
assets/sprites/puzzle_board.png
assets/sprites/flower_board.png
assets/sprites/lantern_board_idle.png
```

The matching `*_master.png` files and portrait images remain source or future
presentation assets; they are not loaded in gameplay currently.

Main menu environment currently loaded behind the title and notice-board options:

```text
assets/sprites/menu.png
assets/sprites/guide_menu.png
assets/sprites/guide_puzzle.png
assets/sprites/plant_menu.png
assets/sprites/plant_puzzle.png
```

Music tracks used by the game:

```text
assets/music/music_menu.mp3
assets/music/music_puzzle.mp3
```

The home screen and its mode-selection pages loop `music_menu.mp3`. Tutorials,
gameplay, and their result overlays loop `music_puzzle.mp3`. `music_style.mp3`
remains a production reference and is not played. If the corresponding optional
track is absent, that scene remains silent.
