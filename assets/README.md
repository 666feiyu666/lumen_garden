# Lumen Garden Asset Slots

The game loads prepared image and audio assets when they exist, and falls back to
procedural drawing or silence when optional files are absent.

## Runtime Image Assets

Current Phase 2 screens load these files from `assets/sprites/`:

```text
menu.png              home screen background
tutorial_menu.png     static Life rules background
Introduction_1.png    Chapter 1 opening comic
end_1.png             Chapter 1 ending comic
setting.png           settings panel
garden.png            Lumen Garden placeholder / unlock page background
guide_puzzle.png      forest and legacy puzzle background fallback
```

Board and character images currently loaded during gameplay:

```text
puzzle_board.png
flower_board.png
lantern_board_idle.png
```

Legacy Phase 1 menu backgrounds remain available for retained prototype flows
and tests:

```text
guide_menu.png
plant_menu.png
plant_puzzle.png
```

Matching `*_master.png` files and portrait images are source or future
presentation assets unless explicitly loaded by code.

## Audio Slots

```text
assets/music/music_menu.mp3
assets/music/music_puzzle.mp3
assets/sfx/move.wav
assets/sfx/grow.wav
assets/sfx/reject.wav
assets/sfx/win.wav
assets/sfx/lose.wav
assets/sfx/select.wav
```

The home screen and selection-style scenes loop `music_menu.mp3`. Tutorials,
story, forest gameplay, legacy gameplay, and result overlays loop
`music_puzzle.mp3`. Missing audio is intentionally silent.

## Folder Map

```text
assets/
  sprites/        backgrounds, comics, panels, board sprites, character sprites
  ui/             reserved for future UI components
  fonts/          licensed TTF/OTF/TTC fonts, optional
  music/          optional background music
  sfx/            optional sound effects
```
