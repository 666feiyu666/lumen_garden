from __future__ import annotations

from dataclasses import dataclass

from .puzzles import Point, Puzzle
from .model import Command


@dataclass(frozen=True)
class TutorialStep:
    title: str
    puzzle: Puzzle
    lines: tuple[str, ...]
    instruction: str
    allowed_commands: frozenset[Command] = frozenset()
    focus: Point | None = None
    move_target: Point | None = None
    result_text: str = ""
    quiz: bool = False


def _puzzle(
    name: str,
    width: int,
    height: int,
    turns: int,
    buds: frozenset[Point],
    target_min: int = 0,
    target_max: int = 99,
) -> Puzzle:
    return Puzzle(
        0,
        name,
        "月夜入门",
        width,
        height,
        turns,
        target_min,
        target_max,
        buds,
        "在月夜里学习花芽盛放的规律。",
    )


TUTORIAL_CARD = _puzzle("GUIDE", 5, 5, 0, frozenset())

TUTORIAL_STEPS: tuple[TutorialStep, ...] = (
    TutorialStep(
        "遇见灯灵",
        _puzzle("GUIDE", 5, 5, 99, frozenset({(1, 2), (2, 2), (2, 1)})),
        (
            "金色灯灵由你控制，它会一直守护这座花园。",
            "绿色花芽会随着每次移动或停留生长一轮。",
        ),
        "按 ENTER 开始倾听花园的规律",
    ),
    TutorialStep(
        "孤芽熄灭",
        _puzzle("LONELY", 5, 5, 1, frozenset({(2, 2)})),
        (
            "观察中央花芽：它身边没有伙伴的微光。",
            "花芽周围少于 2 位伙伴时会渐渐熄灭。",
        ),
        "按 SPACE 等待一轮生长",
        frozenset({Command.WAIT}),
        focus=(2, 2),
        result_text="伙伴 0：孤单的花芽熄灭了。",
    ),
    TutorialStep(
        "相伴常明",
        _puzzle("BALANCE", 5, 5, 1, frozenset({(1, 1), (2, 1), (1, 2), (2, 2)})),
        (
            "四枚花芽相互照亮，组成安稳的小花丛。",
            "拥有 2 或 3 位伙伴的花芽会继续发光。",
        ),
        "按 SPACE 检查稳定状态",
        frozenset({Command.WAIT}),
        focus=(1, 1),
        result_text="伙伴 3：花芽保持盛开，花丛安然不变。",
    ),
    TutorialStep(
        "新芽盛放",
        _puzzle("BLOOM", 5, 5, 1, frozenset({(1, 2), (2, 1), (3, 2)})),
        (
            "高亮的土格周围正好聚集三枚花芽。",
            "一片空地拥有恰好 3 束微光时会萌出新芽。",
        ),
        "按 SPACE 观察新芽盛放",
        frozenset({Command.WAIT}),
        focus=(2, 2),
        result_text="伙伴 3：高亮土格绽放了一枚新芽。",
    ),
    TutorialStep(
        "灯灵引路",
        _puzzle("GUIDANCE", 6, 6, 1, frozenset({(3, 4), (4, 3)})),
        (
            "高亮土格现在只有两枚花芽的微光。",
            "将金色灯灵移到标记格，为它送来第三束光。",
        ),
        "按 LEFT / A 移动灯灵",
        frozenset({Command.LEFT}),
        focus=(4, 4),
        move_target=(4, 5),
        result_text="灯灵送来第三束光：一枚新芽盛开。",
    ),
    TutorialStep(
        "第一则小谜题",
        _puzzle("RIDDLE", 6, 6, 2, frozenset({(3, 4), (4, 3)}), 3, 3),
        (
            "现在请自由行动：在两轮生长后让 3 枚花芽盛开。",
            "提示：先带灯灵靠近花芽，再停留观察。",
        ),
        "方向键移动或 SPACE 停留；未解开可按 R 重试",
        frozenset(Command),
        focus=(4, 4),
        result_text="花芽盛放：你已经懂得如何引导微光。",
        quiz=True,
    ),
)
