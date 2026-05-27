from __future__ import annotations

from dataclasses import dataclass

from .puzzles import Point


@dataclass(frozen=True)
class ClassicPattern:
    key: str
    name_cn: str
    kind: str
    behavior: str
    blooms: frozenset[Point]


@dataclass(frozen=True)
class PlantingPuzzle:
    number: int
    name: str
    name_cn: str
    width: int
    height: int
    player_start: Point
    buds: frozenset[Point]
    seeds: int
    seedable: frozenset[Point]
    pattern: ClassicPattern
    required_start_blooms: frozenset[Point] | None
    expected_blooms: frozenset[Point]
    validation_generation: int
    description: str


def translate(points: frozenset[Point], dx: int, dy: int) -> frozenset[Point]:
    return frozenset((x + dx, y + dy) for x, y in points)


def seedable_except(buds: frozenset[Point]) -> frozenset[Point]:
    return frozenset(
        (x, y) for y in range(1, 9) for x in range(1, 9) if (x, y) not in buds
    )


BLOCK = ClassicPattern(
    "BLOCK",
    "四叶眠床",
    "Still life",
    "连续生长仍保持安稳的四叶花床",
    frozenset({(0, 0), (1, 0), (0, 1), (1, 1)}),
)

BLINKER = ClassicPattern(
    "BLINKER",
    "摇曳花枝",
    "Oscillator",
    "每两代回到原有姿态的摇曳花枝",
    frozenset({(0, 1), (1, 1), (2, 1)}),
)

BEACON = ClassicPattern(
    "BEACON",
    "双灯花台",
    "Oscillator",
    "两座花台每两代交替明灭的灯塔节律",
    frozenset({(0, 0), (1, 0), (0, 1), (3, 2), (2, 3), (3, 3)}),
)

GLIDER = ClassicPattern(
    "GLIDER",
    "流光种",
    "Spaceship",
    "每四代向右下迁移一格的流光种",
    frozenset({(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)}),
)

LWSS = ClassicPattern(
    "LWSS",
    "晨风舟",
    "Spaceship",
    "每四代向右迁移两格的轻型流光舟",
    frozenset({
        (0, 0), (3, 0), (4, 1), (0, 2), (4, 2),
        (1, 3), (2, 3), (3, 3), (4, 3),
    }),
)

CLASSIC_PATTERNS: tuple[ClassicPattern, ...] = (BLOCK, BLINKER, BEACON, GLIDER, LWSS)


_BLOCK_TARGET = translate(BLOCK.blooms, 3, 3)
_BLOCK_INITIAL = _BLOCK_TARGET - {(4, 4)}
_BLINKER_TARGET = translate(BLINKER.blooms, 3, 4)
_BLINKER_INITIAL = _BLINKER_TARGET - {(4, 5)}
_BEACON_TARGET = translate(BEACON.blooms, 3, 3)
_BEACON_INITIAL = _BEACON_TARGET - {(6, 6)}
_GLIDER_TARGET = translate(GLIDER.blooms, 2, 2)
_GLIDER_INITIAL = _GLIDER_TARGET - {(4, 4)}
_GLIDER_VALIDATED = translate(GLIDER.blooms, 3, 3)
_LWSS_TARGET = translate(LWSS.blooms, 1, 3)
_LWSS_INITIAL = _LWSS_TARGET - {(1, 3), (5, 4)}
_LWSS_VALIDATED = translate(LWSS.blooms, 3, 3)

PLANTING_PUZZLES: tuple[PlantingPuzzle, ...] = (
    PlantingPuzzle(
        1,
        "BLOCK",
        "四叶眠床",
        10,
        10,
        (6, 6),
        _BLOCK_INITIAL,
        1,
        seedable_except(_BLOCK_INITIAL),
        BLOCK,
        _BLOCK_TARGET,
        _BLOCK_TARGET,
        3,
        "教学花谱：种下一枚花芽，再放手见证四叶花床安稳不变。",
    ),
    PlantingPuzzle(
        2,
        "BLINKER",
        "摇曳花枝",
        10,
        10,
        (6, 6),
        _BLINKER_INITIAL,
        1,
        seedable_except(_BLINKER_INITIAL),
        BLINKER,
        _BLINKER_TARGET,
        _BLINKER_TARGET,
        2,
        "补上摇曳花枝的中心花芽，让它完成一次呼吸般的往复。",
    ),
    PlantingPuzzle(
        3,
        "BEACON",
        "双灯花台",
        10,
        10,
        (7, 7),
        _BEACON_INITIAL,
        1,
        seedable_except(_BEACON_INITIAL),
        BEACON,
        _BEACON_TARGET,
        _BEACON_TARGET,
        2,
        "修复两座相望的花台，观察它们交替亮起的节律。",
    ),
    PlantingPuzzle(
        4,
        "GLIDER",
        "流光种",
        10,
        10,
        (7, 7),
        _GLIDER_INITIAL,
        1,
        seedable_except(_GLIDER_INITIAL),
        GLIDER,
        _GLIDER_TARGET,
        _GLIDER_VALIDATED,
        4,
        "补全一枚流光种；四次生长后，它应自己越过对角月光。",
    ),
    PlantingPuzzle(
        5,
        "LWSS",
        "晨风舟",
        10,
        10,
        (8, 8),
        _LWSS_INITIAL,
        2,
        seedable_except(_LWSS_INITIAL),
        LWSS,
        _LWSS_TARGET,
        _LWSS_VALIDATED,
        4,
        "以两枚花种修好轻型流光舟，放手看它横渡花圃。",
    ),
)
