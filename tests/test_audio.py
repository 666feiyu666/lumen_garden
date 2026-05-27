import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pygame

from Lumen_Garden.audio import AudioManager


class AudioManagerTests(unittest.TestCase):
    def test_menu_music_alternates_prepared_tracks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            music = root / "music"
            music.mkdir()
            first = music / "music1.mp3"
            second = music / "music2.mp3"
            first.touch()
            second.touch()

            with (
                patch("Lumen_Garden.audio.pygame.mixer.get_init", return_value=True),
                patch("Lumen_Garden.audio.pygame.mixer.music") as mixer_music,
            ):
                audio = AudioManager(root)
                audio.play_music("menu")

                mixer_music.load.assert_called_once_with(str(first))
                mixer_music.queue.assert_called_once_with(str(second))
                mixer_music.play.assert_called_once_with(fade_ms=450)

                event = pygame.event.Event(AudioManager.MUSIC_END_EVENT)
                self.assertTrue(audio.handle_event(event))
                self.assertEqual(str(first), mixer_music.queue.call_args.args[0])

                self.assertTrue(audio.handle_event(event))
                self.assertEqual(str(second), mixer_music.queue.call_args.args[0])

    def test_other_music_replaces_menu_playlist_with_single_loop(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            music = root / "music"
            music.mkdir()
            (music / "music1.mp3").touch()
            (music / "music2.mp3").touch()
            puzzle = music / "moon_garden.ogg"
            puzzle.touch()

            with (
                patch("Lumen_Garden.audio.pygame.mixer.get_init", return_value=True),
                patch("Lumen_Garden.audio.pygame.mixer.music") as mixer_music,
            ):
                audio = AudioManager(root)
                audio.play_music("menu")
                audio.play_music("puzzle")

                self.assertEqual((), audio.current_playlist)
                mixer_music.load.assert_called_with(str(puzzle))
                mixer_music.play.assert_called_with(-1, fade_ms=450)

    def test_missing_puzzle_track_stops_menu_playlist(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            music = root / "music"
            music.mkdir()
            (music / "music1.mp3").touch()
            (music / "music2.mp3").touch()

            with (
                patch("Lumen_Garden.audio.pygame.mixer.get_init", return_value=True),
                patch("Lumen_Garden.audio.pygame.mixer.music") as mixer_music,
            ):
                audio = AudioManager(root)
                audio.play_music("menu")
                audio.play_music("puzzle")

                self.assertEqual((), audio.current_playlist)
                self.assertEqual("puzzle", audio.current_music)
                mixer_music.stop.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
