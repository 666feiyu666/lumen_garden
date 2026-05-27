import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Lumen_Garden.audio import AudioManager


class AudioManagerTests(unittest.TestCase):
    def test_menu_music_loops_named_menu_track(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            music = root / "music"
            music.mkdir()
            menu = music / "music_menu.mp3"
            menu.touch()

            with (
                patch("Lumen_Garden.audio.pygame.mixer.get_init", return_value=True),
                patch("Lumen_Garden.audio.pygame.mixer.music") as mixer_music,
            ):
                audio = AudioManager(root)
                audio.play_music("menu")

                mixer_music.load.assert_called_once_with(str(menu))
                mixer_music.play.assert_called_once_with(-1, fade_ms=450)

    def test_puzzle_music_replaces_menu_music_with_single_loop(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            music = root / "music"
            music.mkdir()
            (music / "music_menu.mp3").touch()
            puzzle = music / "music_puzzle.mp3"
            puzzle.touch()

            with (
                patch("Lumen_Garden.audio.pygame.mixer.get_init", return_value=True),
                patch("Lumen_Garden.audio.pygame.mixer.music") as mixer_music,
            ):
                audio = AudioManager(root)
                audio.play_music("menu")
                audio.play_music("puzzle")

                mixer_music.load.assert_called_with(str(puzzle))
                mixer_music.play.assert_called_with(-1, fade_ms=450)

    def test_reselecting_puzzle_music_does_not_restart_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            music = root / "music"
            music.mkdir()
            puzzle = music / "music_puzzle.mp3"
            puzzle.touch()

            with (
                patch("Lumen_Garden.audio.pygame.mixer.get_init", return_value=True),
                patch("Lumen_Garden.audio.pygame.mixer.music") as mixer_music,
            ):
                audio = AudioManager(root)
                audio.play_music("puzzle")
                audio.play_music("puzzle")

                mixer_music.load.assert_called_once_with(str(puzzle))
                mixer_music.play.assert_called_once_with(-1, fade_ms=450)

    def test_missing_puzzle_track_stops_menu_music(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            music = root / "music"
            music.mkdir()
            (music / "music_menu.mp3").touch()

            with (
                patch("Lumen_Garden.audio.pygame.mixer.get_init", return_value=True),
                patch("Lumen_Garden.audio.pygame.mixer.music") as mixer_music,
            ):
                audio = AudioManager(root)
                audio.play_music("menu")
                audio.play_music("puzzle")

                self.assertEqual("puzzle", audio.current_music)
                mixer_music.stop.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
