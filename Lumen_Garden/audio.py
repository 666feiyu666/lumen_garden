from __future__ import annotations

from pathlib import Path

import pygame


class AudioManager:
    """Optional audio layer: the game remains runnable before assets exist."""

    MUSIC_END_EVENT = pygame.USEREVENT + 1
    MUSIC = {
        "menu": "music/menu.ogg",
        "puzzle": "music/moon_garden.ogg",
        "result": "music/result.ogg",
    }
    MUSIC_PLAYLISTS = {
        "menu": ("music/music1.mp3", "music/music2.mp3"),
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
        self.current_playlist: tuple[Path, ...] = ()
        self.playlist_index = 0
        self.volume = 0.48
        self.enabled = True
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.ready = True
            pygame.mixer.music.set_endevent(self.MUSIC_END_EVENT)
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
        playlist = tuple(
            self.asset_root / relative_path
            for relative_path in self.MUSIC_PLAYLISTS.get(name, ())
            if (self.asset_root / relative_path).exists()
        )
        if playlist:
            try:
                self.current_playlist = playlist
                self.playlist_index = 0
                pygame.mixer.music.load(str(playlist[0]))
                if len(playlist) > 1:
                    pygame.mixer.music.queue(str(playlist[1]))
                pygame.mixer.music.set_volume(self.volume if self.enabled else 0.0)
                pygame.mixer.music.play(fade_ms=450)
                self.current_music = name
            except pygame.error:
                self.current_playlist = ()
                pygame.mixer.music.stop()
                self.current_music = name
            return

        path = self.asset_root / self.MUSIC[name]
        if path.exists():
            try:
                self.current_playlist = ()
                pygame.mixer.music.load(str(path))
                pygame.mixer.music.set_volume(self.volume if self.enabled else 0.0)
                pygame.mixer.music.play(-1, fade_ms=450)
                self.current_music = name
            except pygame.error:
                pygame.mixer.music.stop()
                self.current_music = name
                return
        else:
            self.current_playlist = ()
            pygame.mixer.music.stop()
            self.current_music = name

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type != self.MUSIC_END_EVENT:
            return False
        if self.current_music != "menu" or not self.current_playlist:
            return True
        if len(self.current_playlist) > 1:
            self.playlist_index = (self.playlist_index + 1) % len(self.current_playlist)
            upcoming = self.current_playlist[
                (self.playlist_index + 1) % len(self.current_playlist)
            ]
            try:
                pygame.mixer.music.queue(str(upcoming))
            except pygame.error:
                pass
        else:
            try:
                pygame.mixer.music.play()
            except pygame.error:
                pass
        return True

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
