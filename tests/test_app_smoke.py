import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from Lumen_Garden.app import LumenGardenApp
from Lumen_Garden.model import PlantingPhase
from Lumen_Garden.patterns import PLANTING_PUZZLES


class PlantingAppSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = LumenGardenApp()

    def tearDown(self) -> None:
        pygame.quit()

    def test_mouse_can_open_garden_mode_and_start_tutorial(self) -> None:
        self.app._mouse_click((220, 360))
        self.assertEqual("garden_menu", self.app.scene)
        self.app._mouse_click((180, 210))
        self.assertEqual("tutorial", self.app.scene)

    def test_mouse_can_start_and_act_in_garden_puzzle(self) -> None:
        self.app._mouse_click((220, 360))
        self.app._mouse_click((180, 270))
        self.assertEqual("game", self.app.scene)
        self.app._mouse_click((356, 449))
        self.assertIsNotNone(self.app.state)
        self.assertEqual(1, self.app.state.generation)

    def test_mouse_can_change_settings(self) -> None:
        self.app._mouse_click((220, 540))
        self.assertTrue(self.app.settings_open)
        self.app._mouse_click((440, 300))
        self.assertEqual((1024, 576), self.app.window_size)
        volume = self.app.audio.volume
        self.app._mouse_click((680, 430))
        self.assertGreater(self.app.audio.volume, volume)
        self.app._mouse_click((750, 430))
        self.assertFalse(self.app.audio.enabled)
        self.app._mouse_click((500, 530))
        self.assertFalse(self.app.settings_open)

    def test_game_disables_text_input_so_letter_hotkeys_are_not_ime_composition(self) -> None:
        with patch("pygame.key.stop_text_input") as stop_text_input:
            LumenGardenApp()
        stop_text_input.assert_called_once_with()

    def test_complete_planting_puzzle_with_mouse_and_autoplay(self) -> None:
        self.app._mouse_click((220, 450))
        self.assertEqual("planting_menu", self.app.scene)
        self.app._mouse_click((200, 220))
        self.assertEqual("planting", self.app.scene)
        for point in ((377, 408), (377, 361), (330, 361), (283, 361)):
            self.app._mouse_click(point)
        self.app._mouse_click((283, 361))
        self.assertEqual(1, self.app.planting_state.seeds_left)
        self.assertIn("可按 P 播种", self.app.message)
        self.app._mouse_click((710, 585))
        self.app._mouse_click((283, 361))
        self.assertEqual(PlantingPhase.PLANTING, self.app.planting_state.phase)
        self.assertIn("SPACE 或 ENTER", self.app.message)
        self.app._mouse_click((900, 585))
        self.assertTrue(self.app.planting_autoplay)
        self.app._mouse_click((710, 585))
        self.assertFalse(self.app.planting_autoplay)
        self.app._update_planting_playback(0.71)
        self.assertEqual(0, self.app.planting_state.generation)
        self.app._mouse_click((810, 585))
        self.assertEqual(1, self.app.planting_state.generation)
        self.app._mouse_click((710, 585))
        self.assertTrue(self.app.planting_autoplay)
        for _ in range(2):
            self.app._update_planting_playback(0.71)
        self.assertIsNotNone(self.app.planting_state)
        self.assertEqual(PlantingPhase.WON, self.app.planting_state.phase)
        self.assertTrue(self.app.planting_autoplay)
        self.assertGreaterEqual(len(self.app.planting_showcase_frames), 2)
        self.app._mouse_click((710, 585))
        self.assertFalse(self.app.planting_autoplay)
        self.app._draw()
        pygame.display.flip()

    def test_planting_keys_require_explicit_seed_and_complete_layout(self) -> None:
        self.app._start_planting(0)
        state = self.app.planting_state
        self.assertIsNotNone(state)
        for key in (pygame.K_UP, pygame.K_UP, pygame.K_LEFT, pygame.K_LEFT):
            self.app._planting_key(key)

        before = set(state.blooms)
        self.app._planting_key(pygame.K_SPACE)
        self.assertEqual(before, state.blooms)
        self.assertEqual(1, state.seeds_left)
        self.assertIn("花种未种下", self.app.message)
        self.assertEqual(PlantingPhase.PLANTING, state.phase)

        self.app._planting_key(pygame.K_RETURN)
        self.assertEqual(PlantingPhase.PLANTING, state.phase)
        self.assertIn("花种未种下", self.app.message)

        self.app._planting_key(pygame.K_p)
        self.assertEqual(0, state.seeds_left)
        self.app._planting_key(pygame.K_SPACE)
        self.assertEqual(PlantingPhase.GROWING, state.phase)
        self.assertTrue(self.app.planting_autoplay)

        self.app._start_planting(0)
        state = self.app.planting_state
        for key in (pygame.K_UP, pygame.K_UP, pygame.K_LEFT, pygame.K_LEFT):
            self.app._planting_key(key)
        self.app._planting_key(pygame.K_p)
        self.app._planting_key(pygame.K_RETURN)
        self.assertEqual(PlantingPhase.GROWING, state.phase)
        self.assertTrue(self.app.planting_autoplay)

    def test_blinker_center_accepts_seed_and_can_exit_vertically(self) -> None:
        self.app._start_planting(1)
        state = self.app.planting_state
        for key in (pygame.K_LEFT, pygame.K_LEFT, pygame.K_UP):
            self.app._planting_key(key)
        self.assertEqual((4, 5), state.player)

        self.app._planting_key(pygame.K_p)
        self.assertEqual(0, state.seeds_left)
        self.assertIn((4, 5), state.blooms)
        self.assertIn((4, 5), state.planted)

        self.app._planting_key(pygame.K_LEFT)
        self.assertEqual((4, 5), state.player)
        self.assertIn("相邻空土格", self.app.message)
        self.app._planting_key(pygame.K_DOWN)
        self.assertEqual((4, 6), state.player)

    def test_winning_lwss_replays_verified_frames_without_advancing_state(self) -> None:
        self.app._start_planting(4)
        state = self.app.planting_state
        self.assertIsNotNone(state)
        required = set(PLANTING_PUZZLES[4].required_start_blooms or ())
        for point in required - set(PLANTING_PUZZLES[4].buds):
            state.player = point
            self.app._planting_key(pygame.K_p)
        self.app._planting_key(pygame.K_RETURN)
        for _ in range(PLANTING_PUZZLES[4].validation_generation):
            self.app._update_planting_playback(0.71)

        self.assertEqual(PlantingPhase.WON, state.phase)
        validated = set(state.blooms)
        validation_generation = state.generation
        frames = tuple(self.app.planting_showcase_frames)
        self.assertEqual(5, len(frames))

        for _ in range(len(frames) + 3):
            self.app._update_planting_playback(0.71)

        self.assertEqual(PlantingPhase.WON, state.phase)
        self.assertEqual(validation_generation, state.generation)
        self.assertEqual(validated, state.blooms)
        self.assertEqual(frames, tuple(self.app.planting_showcase_frames))

    def test_mouse_can_open_fifth_planting_pattern(self) -> None:
        self.app._mouse_click((220, 450))
        self.app._mouse_click((200, 480))
        self.assertEqual("planting", self.app.scene)
        self.assertIsNotNone(self.app.planting_state)
        self.assertEqual(5, self.app.planting_state.puzzle.number)


if __name__ == "__main__":
    unittest.main()
