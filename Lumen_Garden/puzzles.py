from __future__ import annotations

from dataclasses import dataclass

Point = tuple[int, int]


@dataclass(frozen=True)
class Puzzle:
    number: int
    name: str
    name_cn: str
    width: int
    height: int
    turns: int
    target_min: int
    target_max: int
    buds: frozenset[Point]
    description: str

    @property
    def player_start(self) -> Point:
        return (self.width - 1, self.height - 1)

    @property
    def target_label(self) -> str:
        if self.target_min == self.target_max:
            return str(self.target_min)
        return f"{self.target_min}-{self.target_max}"


def _buds(*coordinates: Point) -> frozenset[Point]:
    return frozenset(coordinates)


# The first formal garden booklet uses one readable board scale throughout.
# Difficulty comes from timing, lantern position, and the bloom target.
PUZZLES: tuple[Puzzle, ...] = (
    Puzzle(
        1,
        "AWAKEN",
        "初光",
        10,
        10,
        3,
        3,
        3,
        _buds((7, 8), (8, 7)),
        "靠近两枚相伴的花芽，送出催生第三枚新芽的微光。",
    ),
    Puzzle(
        2,
        "SPROUT",
        "新芽",
        10,
        10,
        5,
        10,
        10,
        _buds((6, 7), (7, 6), (8, 7), (7, 8)),
        "沿花丛边缘行走，让短暂盛开的新芽在黎明前延续。",
    ),
    Puzzle(
        3,
        "CHORUS",
        "合鸣",
        10,
        10,
        6,
        19,
        19,
        _buds((4, 6), (5, 6), (6, 6), (7, 7), (8, 7)),
        "两段花声将要相遇；选择靠近与停留的时机，使它们同鸣。",
    ),
    Puzzle(
        4,
        "MOONBED",
        "月圃",
        10,
        10,
        7,
        19,
        19,
        _buds((5, 5), (6, 5), (5, 6), (7, 7), (8, 7)),
        "月圃需要耐心：主动停驻，让灯灵的光在恰当一轮留下来。",
    ),
    Puzzle(
        5,
        "DAWN",
        "黎明",
        10,
        10,
        9,
        25,
        25,
        _buds(
            (3, 4), (4, 4), (5, 4), (4, 5),
            (6, 6), (7, 6), (8, 6), (7, 7),
        ),
        "黎明将至，在相接的花群之间规划路线，收束最后的盛放。",
    ),
)

# Verified reference paths for the formal 10 x 10 booklet.
KNOWN_SOLUTIONS: tuple[tuple[str, ...], ...] = (
    ("UP", "WAIT", "WAIT"),
    ("UP", "UP", "WAIT", "WAIT", "UP"),
    ("WAIT", "UP", "UP", "WAIT", "UP", "WAIT"),
    ("UP", "UP", "WAIT", "LEFT", "WAIT", "WAIT", "RIGHT"),
    ("UP", "DOWN", "WAIT", "LEFT", "UP", "DOWN", "LEFT", "LEFT", "LEFT"),
)

KNOWN_SOLUTION_FINAL_COUNTS: tuple[int, ...] = (3, 10, 19, 19, 25)
