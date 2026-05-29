import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from Lumen_Garden.app import (
    FOREST_ROOMS,
    GARDEN_CARD_RECTS,
    GARDEN_HUB_PLOT_RECTS,
    LumenGardenApp,
    MENU_BUTTON_RECTS,
    PLANT_CARD_RECTS,
    PLANT_CONTROL_RECTS,
    PUZZLE_BACK_RECT,
    SCREEN_SIZE,
)
from Lumen_Garden.model import Command, Phase, PlantingPhase
from Lumen_Garden.patterns import PLANTING_PUZZLES
from Lumen_Garden.puzzles import KNOWN_SOLUTIONS, PUZZLES
from Lumen_Garden.tutorial import TUTORIAL_STEPS


class PlantingAppSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = LumenGardenApp()

    def tearDown(self) -> None:
        pygame.quit()

    def test_mouse_can_open_static_rules_tutorial(self) -> None:
        self.app._mouse_click(MENU_BUTTON_RECTS[0].center)
        self.assertEqual("rules", self.app.scene)
        self.app._mouse_click(self.app._rules_back_rect().center)
        self.assertEqual("menu", self.app.scene)

    def test_mouse_can_start_and_act_in_garden_puzzle(self) -> None:
        self.app._open_garden_menu()
        self.app.tutorial_completed = True
        self.app._mouse_click(GARDEN_CARD_RECTS[1].center)
        self.assertEqual("game", self.app.scene)
        board, tile = self.app._formal_board_layout(
            self.app.state.puzzle.width, self.app.state.puzzle.height
        )
        player = self.app.state.player
        self.app._mouse_click(self.app._formal_tile_rect(board, player).center)
        self.assertIsNotNone(self.app.state)
        self.assertEqual(1, self.app.state.generation)

    def test_formal_modes_share_the_same_board_layout(self) -> None:
        garden_board, garden_tile = self.app._formal_board_layout(
            PUZZLES[0].width, PUZZLES[0].height
        )
        planting_board, planting_tile = self.app._formal_board_layout(
            PLANTING_PUZZLES[0].width, PLANTING_PUZZLES[0].height
        )
        self.assertEqual(garden_tile, planting_tile)
        self.assertEqual(garden_board, planting_board)
        self.assertEqual(47, garden_tile)

    def test_sprite_assets_are_loaded_and_used_for_gameplay(self) -> None:
        self.assertEqual({"flower", "lantern"}, set(self.app.board_sprites))
        self.assertIsNotNone(self.app.puzzle_board)
        self.app.tutorial_completed = True
        self.app._start_puzzle(0)
        with patch.object(
            self.app, "_scaled_board_sprite", wraps=self.app._scaled_board_sprite
        ) as scaled_sprite, patch.object(
            self.app, "_scaled_puzzle_board", wraps=self.app._scaled_puzzle_board
        ) as scaled_board:
            self.app._draw()
        requested = {call.args[0] for call in scaled_sprite.call_args_list}
        self.assertEqual({"flower", "lantern"}, requested)
        scaled_board.assert_called()
        self.assertEqual(
            self.app.guide_puzzle_background.get_at((700, 40)),
            self.app.screen.get_at((700, 40)),
        )

    def test_menu_uses_background_art_and_notice_board_buttons(self) -> None:
        self.assertIsNot(self.app.menu_background, self.app.background)
        self.assertIsNot(self.app.guide_menu_background, self.app.background)
        self.assertIsNot(self.app.tutorial_menu_background, self.app.background)
        self.assertIsNot(self.app.guide_puzzle_background, self.app.background)
        self.assertIsNotNone(self.app.setting_panel)
        self.assertIsNot(self.app.plant_menu_background, self.app.background)
        self.assertIsNot(self.app.plant_puzzle_background, self.app.background)
        self.assertTrue(all(rect.centerx > SCREEN_SIZE[0] // 2 for rect in MENU_BUTTON_RECTS))
        self.assertTrue(all(rect.right < SCREEN_SIZE[0] // 2 for rect in GARDEN_CARD_RECTS))
        self.assertTrue(all(rect.right < SCREEN_SIZE[0] // 2 + 50 for rect in PLANT_CARD_RECTS))

    def test_garden_puzzles_unlock_in_order_after_completion(self) -> None:
        self.app._open_garden_menu()
        self.app._mouse_click(GARDEN_CARD_RECTS[1].center)
        self.assertEqual("garden_menu", self.app.scene)
        self.assertIn("完成上一关", self.app.message)

        self.app.tutorial_step = len(TUTORIAL_STEPS)
        self.app._load_tutorial_step()
        self.app._mouse_click(GARDEN_CARD_RECTS[1].center)
        self.assertEqual("game", self.app.scene)
        for action in KNOWN_SOLUTIONS[0]:
            self.app._issue(Command[action])
        self.assertEqual(Phase.WON, self.app.state.phase)

        self.app.scene = "garden_menu"
        self.app._mouse_click(GARDEN_CARD_RECTS[2].center)
        self.assertEqual("game", self.app.scene)
        self.assertEqual(2, self.app.state.puzzle.number)

    def test_board_sprites_anchor_visible_art_at_cell_center(self) -> None:
        board, _ = self.app._formal_board_layout(10, 10)
        cell = self.app._formal_tile_rect(board, (9, 9))
        for name in ("flower", "lantern"):
            sprite = self.app._scaled_board_sprite(name, cell.size)
            self.assertIsNotNone(sprite)
            visible = sprite.get_bounding_rect(min_alpha=4)
            destination = self.app._sprite_destination(sprite, cell)
            drawn = visible.move(destination.topleft)
            self.assertLessEqual(abs(drawn.centerx - cell.centerx), 1)
            self.assertLessEqual(abs(drawn.centery - cell.centery), 1)

    def test_mouse_can_change_settings(self) -> None:
        self.app._mouse_click(MENU_BUTTON_RECTS[3].center)
        self.assertTrue(self.app.settings_open)
        self.app._mouse_click((440, 300))
        self.assertEqual((1024, 576), self.app.window_size)
        volume = self.app.audio.volume
        self.app._mouse_click((680, 460))
        self.assertGreater(self.app.audio.volume, volume)
        self.app._mouse_click((800, 460))
        self.assertFalse(self.app.audio.enabled)
        self.app._mouse_click((500, 530))
        self.assertFalse(self.app.settings_open)

    def test_escape_on_menu_opens_settings_and_quit_button_exits(self) -> None:
        self.app._menu_key(pygame.K_ESCAPE)
        self.assertTrue(self.app.settings_open)
        self.assertTrue(self.app.running)
        self.app._mouse_click((700, 530))
        self.assertFalse(self.app.running)

    def test_escape_in_forest_opens_settings_and_exit_level_records_room(self) -> None:
        self.app._start_forest_room(1)
        self.app._forest_key(pygame.K_ESCAPE)
        self.assertTrue(self.app.settings_open)
        self.assertEqual("forest", self.app.scene)
        self.app._mouse_click((620, 530))
        self.assertEqual("menu", self.app.scene)
        self.assertFalse(self.app.settings_open)
        self.assertIsNone(self.app.forest_state)
        self.assertEqual(1, self.app.forest_resume_room)
        self.app._start_forest_intro()
        self.app._intro_key(pygame.K_RETURN)
        self.assertEqual(1, self.app.forest_state.room.number)

    def test_game_disables_text_input_so_letter_hotkeys_are_not_ime_composition(self) -> None:
        with patch("pygame.key.stop_text_input") as stop_text_input:
            LumenGardenApp()
        stop_text_input.assert_called_once_with()

    def test_complete_planting_puzzle_with_mouse_and_autoplay(self) -> None:
        self.app._open_planting_menu()
        self.assertEqual("planting_menu", self.app.scene)
        self.app._mouse_click(PLANT_CARD_RECTS[0].center)
        self.assertEqual("planting", self.app.scene)
        board, tile = self.app._formal_board_layout(
            self.app.planting_state.puzzle.width, self.app.planting_state.puzzle.height
        )

        def click_cell(point: tuple[int, int]) -> None:
            self.app._mouse_click(self.app._formal_tile_rect(board, point).center)

        for point in ((6, 5), (6, 4), (5, 4), (4, 4)):
            click_cell(point)
        click_cell((4, 4))
        self.assertEqual(1, self.app.planting_state.seeds_left)
        self.assertIn("可按 P 播种", self.app.message)
        self.app._mouse_click(PLANT_CONTROL_RECTS[0].center)
        click_cell((4, 4))
        self.assertEqual(PlantingPhase.PLANTING, self.app.planting_state.phase)
        self.assertIn("SPACE 或 ENTER", self.app.message)
        self.app._mouse_click(PLANT_CONTROL_RECTS[2].center)
        self.assertTrue(self.app.planting_autoplay)
        self.app._mouse_click(PLANT_CONTROL_RECTS[0].center)
        self.assertFalse(self.app.planting_autoplay)
        self.app._update_planting_playback(0.71)
        self.assertEqual(0, self.app.planting_state.generation)
        self.app._mouse_click(PLANT_CONTROL_RECTS[1].center)
        self.assertEqual(1, self.app.planting_state.generation)
        self.app._mouse_click(PLANT_CONTROL_RECTS[0].center)
        self.assertTrue(self.app.planting_autoplay)
        for _ in range(2):
            self.app._update_planting_playback(0.71)
        self.assertIsNotNone(self.app.planting_state)
        self.assertEqual(PlantingPhase.WON, self.app.planting_state.phase)
        self.assertTrue(self.app._planting_entry_unlocked(1))
        self.assertTrue(self.app.planting_autoplay)
        self.assertGreaterEqual(len(self.app.planting_showcase_frames), 2)
        self.app._mouse_click(PLANT_CONTROL_RECTS[0].center)
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
        self.app.completed_planting.add(0)
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
        self.app.completed_planting.update(range(4))
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
        self.app.completed_planting.update(range(4))
        self.app._open_planting_menu()
        self.app._mouse_click(PLANT_CARD_RECTS[4].center)
        self.assertEqual("planting", self.app.scene)
        self.assertIsNotNone(self.app.planting_state)
        self.assertEqual(5, self.app.planting_state.puzzle.number)

    def test_locked_planting_pattern_does_not_start(self) -> None:
        self.app._open_planting_menu()
        self.app._mouse_click(PLANT_CARD_RECTS[1].center)
        self.assertEqual("planting_menu", self.app.scene)
        self.assertIn("完成上一关", self.app.message)

    def test_menu_story_mode_shows_intro_then_forest_room(self) -> None:
        self.app._mouse_click(MENU_BUTTON_RECTS[1].center)
        self.assertEqual("intro", self.app.scene)
        self.assertIsNotNone(self.app.introduction_image)
        self.app._intro_key(pygame.K_RETURN)
        self.assertEqual("forest", self.app.scene)
        self.assertIsNotNone(self.app.forest_state)
        self.assertEqual(0, self.app.forest_state.room.number)

    def test_free_garden_entry_opens_six_plot_hub(self) -> None:
        self.app._mouse_click(MENU_BUTTON_RECTS[2].center)
        self.assertEqual("garden_hub", self.app.scene)
        self.assertEqual(6, len(self.app.garden_plots))
        self.assertIn("选择一块空花圃", self.app.message)
        self.assertIsNot(self.app.garden_background, self.app.guide_puzzle_background)

    def test_forest_mechanism_sleeps_until_restored_and_awakened(self) -> None:
        self.app._start_forest_room(3)
        state = self.app.forest_state
        self.assertIsNotNone(state)
        start = set(state.mechanism_plants)
        self.app._issue_forest(Command.WAIT)
        self.assertEqual(start, state.mechanism_plants)
        state.carrying_seed = True
        state.player = state.room.mechanism_missing
        self.app._forest_plant_or_start()
        self.assertTrue(state.mechanism_active)
        restored = set(state.mechanism_plants)
        self.app._issue_forest(Command.WAIT)
        self.assertNotEqual(restored, state.mechanism_plants)

    def test_forest_completion_shows_ending_comic_before_garden_unlock(self) -> None:
        self.app._start_forest_room(4)
        state = self.app.forest_state
        self.assertIsNotNone(state)
        self.assertIsNotNone(self.app.ending_image)
        state.door_open = True
        state.player = state.room.exit_cell
        self.app._complete_forest_room()
        self.assertEqual("ending", self.app.scene)
        self.assertTrue(self.app.forest_completed)
        self.app._ending_key(pygame.K_RETURN)
        self.assertEqual("garden_hub", self.app.scene)
        self.assertIn("荧光花园已解锁", self.app.message)

    def test_phase_two_story_has_five_numbered_rooms(self) -> None:
        self.assertEqual([0, 1, 2, 3, 4], [room.number for room in FOREST_ROOMS])
        self.assertFalse(FOREST_ROOMS[0].ordinary_plants)
        self.assertTrue(FOREST_ROOMS[2].stone_cells)
        self.assertTrue(FOREST_ROOMS[4].button_cells)

    def test_forest_uses_separate_maze_board_art(self) -> None:
        self.app._start_forest_room(0)
        self.assertLessEqual(self.app.message_timer, 5.0)
        board, _ = self.app._forest_board_layout(10, 10)
        self.assertGreater(board.width, 560)
        self.assertLess(abs(board.centerx - SCREEN_SIZE[0] // 2), 8)
        with patch.object(self.app, "_scaled_puzzle_board", wraps=self.app._scaled_puzzle_board) as scaled_board:
            self.app._draw()
        scaled_board.assert_not_called()
        self.assertNotEqual(
            self.app.guide_puzzle_background.get_at((700, 40)),
            self.app.screen.get_at((700, 40)),
        )

    def test_forest_dialog_can_be_dismissed_by_clicking_it(self) -> None:
        self.app._start_forest_room(0)
        self.assertGreater(self.app.message_timer, 0)
        self.app._mouse_click(self.app._forest_dialog_rect().center)
        self.assertEqual(0.0, self.app.message_timer)

    def test_second_story_room_collects_ordinary_seed(self) -> None:
        self.app._start_forest_room(1)
        state = self.app.forest_state
        self.assertIsNotNone(state)
        self.assertEqual({(8, 7)}, state.ordinary_seed_cells)
        state.player = (8, 8)
        self.app._issue_forest(Command.UP)
        self.assertEqual(1, self.app.ordinary_seed_inventory)
        self.assertEqual(set(), state.ordinary_seed_cells)
        self.assertIn("普通植物种子", self.app.message)

    def test_garden_plot_uses_backpack_seed_to_plant(self) -> None:
        self.app.ordinary_seed_inventory = 1
        self.app._open_free_garden()
        self.app._mouse_click(GARDEN_HUB_PLOT_RECTS[0].center)
        self.assertEqual("ORDINARY", self.app.garden_plots[0])
        self.assertEqual(0, self.app.ordinary_seed_inventory)
        self.assertIn("普通植物", self.app.message)

    def test_garden_dialog_can_be_dismissed_by_clicking_it(self) -> None:
        self.app._open_free_garden()
        self.assertGreater(self.app.message_timer, 0)
        self.app._mouse_click(self.app._garden_hub_dialog_rect().center)
        self.assertEqual(0.0, self.app.message_timer)

    def test_garden_plot_requires_codex_and_enough_seeds_for_pattern(self) -> None:
        self.app.codex_patterns.add("BLOCK")
        self.app.ordinary_seed_inventory = 4
        self.app._open_free_garden()
        self.app._mouse_click(GARDEN_HUB_PLOT_RECTS[1].center)
        self.assertEqual("BLOCK", self.app.garden_plots[1])
        self.assertEqual(0, self.app.ordinary_seed_inventory)

    def test_block_room_records_codex_pattern(self) -> None:
        self.app._start_forest_room(2)
        state = self.app.forest_state
        self.assertIsNotNone(state)
        state.player = (2, 4)
        self.app._check_forest_discovery()
        self.assertIn("BLOCK", self.app.codex_patterns)

    def test_blinker_buttons_toggle_exit(self) -> None:
        self.app._start_forest_room(4)
        state = self.app.forest_state
        self.assertIsNotNone(state)
        self.assertTrue(state.door_open)
        self.app._issue_forest(Command.WAIT)
        self.assertFalse(state.door_open)
        self.app._issue_forest(Command.WAIT)
        self.assertTrue(state.door_open)

    def test_mouse_back_from_puzzle_restores_menu_music(self) -> None:
        self.app.tutorial_completed = True
        self.app._start_puzzle(0)
        with patch.object(self.app.audio, "play_music") as play_music:
            self.app._mouse_click(PUZZLE_BACK_RECT.center)
        self.assertEqual("garden_menu", self.app.scene)
        play_music.assert_called_once_with("menu")

    def test_mouse_back_from_planting_restores_menu_music(self) -> None:
        self.app._start_planting(0)
        with patch.object(self.app.audio, "play_music") as play_music:
            self.app._mouse_click(PLANT_CONTROL_RECTS[4].center)
        self.assertEqual("planting_menu", self.app.scene)
        play_music.assert_called_once_with("menu")


if __name__ == "__main__":
    unittest.main()
