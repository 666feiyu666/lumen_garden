import unittest

from Lumen_Garden.model import Command, GameState, Phase
from Lumen_Garden.tutorial import TUTORIAL_STEPS


class TutorialStepTests(unittest.TestCase):
    def test_demo_steps_explain_real_rule_outcomes(self) -> None:
        lonely = GameState(TUTORIAL_STEPS[1].puzzle)
        lonely_report = lonely.issue(Command.WAIT)
        self.assertIn((2, 2), lonely_report.faded)

        balance = GameState(TUTORIAL_STEPS[2].puzzle)
        balance_report = balance.issue(Command.WAIT)
        self.assertFalse(balance_report.bloomed)
        self.assertFalse(balance_report.faded)

        birth = GameState(TUTORIAL_STEPS[3].puzzle)
        birth_report = birth.issue(Command.WAIT)
        self.assertIn((2, 2), birth_report.bloomed)

        intervene = GameState(TUTORIAL_STEPS[4].puzzle)
        intervene_report = intervene.issue(Command.LEFT)
        self.assertIn((4, 4), intervene_report.bloomed)

    def test_quiz_has_a_short_winning_solution(self) -> None:
        quiz = GameState(TUTORIAL_STEPS[5].puzzle)
        self.assertTrue(quiz.issue(Command.LEFT).accepted)
        self.assertTrue(quiz.issue(Command.WAIT).accepted)
        self.assertEqual(Phase.WON, quiz.phase)
        self.assertEqual(3, quiz.bloom_count)


if __name__ == "__main__":
    unittest.main()
