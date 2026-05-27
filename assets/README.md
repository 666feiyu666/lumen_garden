# Lumen Garden Asset Slots

The prototype renders glowing buds, a lantern spirit, and interface shapes
procedurally, so it runs without external art or audio files. Add production
garden assets at these paths:

```text
assets/
  sprites/        buds, lantern spirit, petals, fireflies
  ui/             journal panels, puzzle cards, logo treatments
  fonts/          licensed TTF/OTF fonts, optional
  music/
    music1.mp3
    music2.mp3
    moon_garden.ogg
    result.ogg
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

The current art-production pass has prepared these lantern source and runtime-ready
transparent images:

```text
assets/sprites/lantern_portrait_green_master.png
assets/sprites/lantern_portrait_idle.png
assets/sprites/lantern_board_green_master.png
assets/sprites/lantern_board_idle.png
```

Menu music tracks used by the home screen playlist:

```text
assets/music/music1.mp3
assets/music/music2.mp3
```

The home screen and its mode-selection pages alternate `music1.mp3` and `music2.mp3`
continuously. `music_style.mp3` remains a production reference and is not played.
Entering gameplay or results switches away from the menu playlist; if the respective
optional track is absent, that scene remains silent.
