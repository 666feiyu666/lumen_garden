import unittest

from Lumen_Garden.puzzles import (
    KNOWN_SOLUTIONS,
    KNOWN_SOLUTION_FINAL_COUNTS,
    PUZZLES,
    Puzzle,
)
from Lumen_Garden.model import Command, GameState, Phase


class ModelParityTests(unittest.TestCase):
    def test_formal_garden_booklet_uses_one_board_scale(self) -> None:
        self.assertTrue(all((puzzle.width, puzzle.height) == (10, 10) for puzzle in PUZZLES))
        self.assertEqual("3", PUZZLES[0].target_label)
        self.assertIn("WAIT", KNOWN_SOLUTIONS[2])
        self.assertIn("WAIT", KNOWN_SOLUTIONS[3])

    def test_all_documented_paths_win_with_expected_bloom_count(self) -> None:
        for puzzle, opening, expected_count in zip(
            PUZZLES, KNOWN_SOLUTIONS, KNOWN_SOLUTION_FINAL_COUNTS
        ):
            with self.subTest(puzzle=puzzle.name):
                state = GameState(puzzle)
                for command_name in opening:
                    report = state.issue(Command[command_name])
                    self.assertTrue(report.accepted)
                while state.phase is Phase.ACTIVE:
                    self.assertTrue(state.issue(Command.WAIT).accepted)
                self.assertEqual(Phase.WON, state.phase)
                self.assertEqual(expected_count, state.bloom_count)

    def test_wait_only_does_not_solve_the_five_puzzles(self) -> None:
        for puzzle in PUZZLES:
            with self.subTest(puzzle=puzzle.name):
                state = GameState(puzzle)
                for _ in range(puzzle.turns):
                    state.issue(Command.WAIT)
                self.assertEqual(Phase.LOST, state.phase)

    def test_rejected_move_does_not_consume_a_step_or_grow(self) -> None:
        state = GameState(PUZZLES[0])
        report = state.issue(Command.RIGHT)
        self.assertFalse(report.accepted)
        self.assertEqual(PUZZLES[0].turns, state.turns_left)
        self.assertEqual(0, state.generation)
        self.assertTrue(state.last_rejected)

    def test_lantern_counts_as_neighbor_but_not_bloom_count(self) -> None:
        puzzle = Puzzle(
            99,
            "TEST",
            "测试",
            3,
            3,
            1,
            1,
            10,
            frozenset({(0, 1), (1, 0)}),
            "",
        )
        state = GameState(puzzle)
        state.issue(Command.WAIT)
        self.assertIn((1, 1), state.blooms)
        self.assertNotIn((2, 2), state.blooms)
        self.assertEqual(Phase.WON, state.phase)


if __name__ == "__main__":
    unittest.main()
