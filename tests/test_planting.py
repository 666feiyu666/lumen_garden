import unittest

from Lumen_Garden.model import Command, PlantingPhase, PlantingState, grow_once
from Lumen_Garden.patterns import BEACON, BLOCK, BLINKER, GLIDER, LWSS, PLANTING_PUZZLES, translate


def evolve(blooms, width, height, generations):
    result = set(blooms)
    for _ in range(generations):
        result = grow_once(result, width, height)
    return result


class ClassicPatternTests(unittest.TestCase):
    def test_block_remains_still(self) -> None:
        start = translate(BLOCK.blooms, 3, 3)
        self.assertEqual(set(start), evolve(start, 10, 10, 4))

    def test_blinker_returns_after_two_generations(self) -> None:
        start = translate(BLINKER.blooms, 3, 3)
        self.assertEqual(set(start), evolve(start, 10, 10, 2))

    def test_glider_moves_diagonally_after_four_generations(self) -> None:
        start = translate(GLIDER.blooms, 2, 2)
        expected = translate(GLIDER.blooms, 3, 3)
        self.assertEqual(set(expected), evolve(start, 12, 12, 4))

    def test_beacon_returns_after_two_generations(self) -> None:
        start = translate(BEACON.blooms, 3, 3)
        self.assertEqual(set(start), evolve(start, 10, 10, 2))

    def test_lwss_moves_horizontally_after_four_generations(self) -> None:
        start = translate(LWSS.blooms, 1, 3)
        expected = translate(LWSS.blooms, 3, 3)
        self.assertEqual(set(expected), evolve(start, 10, 10, 4))


class PlantingPuzzleTests(unittest.TestCase):
    def test_teaching_puzzle_uses_the_formal_board_scale(self) -> None:
        self.assertEqual(5, len(PLANTING_PUZZLES))
        self.assertTrue(all((puzzle.width, puzzle.height) == (10, 10) for puzzle in PLANTING_PUZZLES))

    def test_all_classic_puzzles_can_be_planted_and_verified(self) -> None:
        for puzzle in PLANTING_PUZZLES:
            state = PlantingState(puzzle)
            required = set(puzzle.required_start_blooms or ())
            missing = required - set(puzzle.buds)
            self.assertEqual(puzzle.seeds, len(missing), puzzle.name)
            for point in missing:
                state.player = point
                self.assertTrue(state.plant().accepted, puzzle.name)
            self.assertTrue(state.start_growth().accepted, puzzle.name)
            for _ in range(puzzle.validation_generation):
                self.assertTrue(state.advance().accepted, puzzle.name)
            self.assertEqual(PlantingPhase.WON, state.phase, puzzle.name)

    def test_movement_and_undo_do_not_grow_the_garden(self) -> None:
        state = PlantingState(PLANTING_PUZZLES[0])
        original = set(state.blooms)
        self.assertTrue(state.move(Command.LEFT).accepted)
        self.assertEqual(original, state.blooms)
        self.assertEqual(0, state.generation)

        self.assertTrue(state.plant().accepted)
        self.assertEqual(0, state.seeds_left)
        self.assertTrue(state.remove_seed().accepted)
        self.assertEqual(original, state.blooms)
        self.assertEqual(1, state.seeds_left)

    def test_cannot_start_growth_until_all_seeds_are_planted(self) -> None:
        state = PlantingState(PLANTING_PUZZLES[4])
        original = set(state.blooms)

        report = state.start_growth()

        self.assertFalse(report.accepted)
        self.assertIn("2 枚花种未种下", report.reason)
        self.assertEqual(PlantingPhase.PLANTING, state.phase)
        self.assertEqual(2, state.seeds_left)
        self.assertEqual(0, state.generation)
        self.assertEqual(original, state.blooms)

    def test_block_can_be_planted_and_verified_without_lantern_light(self) -> None:
        state = PlantingState(PLANTING_PUZZLES[0])
        for command in (Command.UP, Command.UP, Command.LEFT, Command.LEFT):
            self.assertTrue(state.move(command).accepted)
        self.assertTrue(state.plant().accepted)
        self.assertTrue(state.start_growth().accepted)
        self.assertEqual(PlantingPhase.GROWING, state.phase)
        locked_blooms = set(state.blooms)
        self.assertFalse(state.plant().accepted)
        self.assertFalse(state.move(Command.RIGHT).accepted)
        self.assertEqual(locked_blooms, state.blooms)
        for _ in range(3):
            self.assertTrue(state.advance().accepted)
        self.assertEqual(PlantingPhase.WON, state.phase)
        self.assertEqual(set(state.puzzle.expected_blooms), state.blooms)

    def test_wrong_seed_placement_fails_validation(self) -> None:
        state = PlantingState(PLANTING_PUZZLES[0])
        self.assertTrue(state.move(Command.LEFT).accepted)
        self.assertTrue(state.plant().accepted)
        self.assertTrue(state.start_growth().accepted)
        for _ in range(3):
            state.advance()
        self.assertEqual(PlantingPhase.LOST, state.phase)


if __name__ == "__main__":
    unittest.main()
