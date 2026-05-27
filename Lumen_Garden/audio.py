from __future__ import annotations

from pathlib import Path

import pygame


class AudioManager:
    """Optional audio layer: the game remains runnable before assets exist."""

    MUSIC = {
        "menu": "music/music_menu.mp3",
        "puzzle": "music/music_puzzle.mp3",
    }
    SFX = {
        "move": "sfx/move.wav",
        "wait": "sfx/grow.wav",
        "reject": "sfx/reject.wav",
        "win": "sfx/win.wav",
        "lose": "sfx/lose.wav",
        "select": "sfx/select.wav",
    }

    def __init__(self, asset_root: Path) -> None:
        self.asset_root = asset_root
        self.ready = False
        self.current_music = ""
        self.volume = 0.48
        self.enabled = True
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.ready = True
            for name, relative_path in self.SFX.items():
                path = asset_root / relative_path
                if path.exists():
                    self.sounds[name] = pygame.mixer.Sound(str(path))
            self._apply_volume()
        except pygame.error:
            self.ready = False

    def play_music(self, name: str) -> None:
        if not self.ready or name == self.current_music:
            return
        path = self.asset_root / self.MUSIC[name]
        if path.exists():
            try:
                pygame.mixer.music.load(str(path))
                pygame.mixer.music.set_volume(self.volume if self.enabled else 0.0)
                pygame.mixer.music.play(-1, fade_ms=450)
                self.current_music = name
            except pygame.error:
                pygame.mixer.music.stop()
                self.current_music = name
                return
        else:
            pygame.mixer.music.stop()
            self.current_music = name

    def play(self, name: str) -> None:
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()

    def set_volume(self, volume: float) -> None:
        self.volume = max(0.0, min(1.0, volume))
        self._apply_volume()

    def toggle_enabled(self) -> None:
        self.enabled = not self.enabled
        self._apply_volume()

    def _apply_volume(self) -> None:
        level = self.volume if self.enabled else 0.0
        if self.ready:
            pygame.mixer.music.set_volume(level)
        for sound in self.sounds.values():
            sound.set_volume(level)
