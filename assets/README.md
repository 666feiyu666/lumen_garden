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
    menu.ogg
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
