from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .patterns import PlantingPuzzle
from .puzzles import Point, Puzzle


class Command(Enum):
    WAIT = (0, 0)
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class Phase(Enum):
    ACTIVE = "active"
    WON = "won"
    LOST = "lost"


class PlantingPhase(Enum):
    PLANTING = "planting"
    GROWING = "growing"
    WON = "won"
    LOST = "lost"


@dataclass(frozen=True)
class TurnReport:
    accepted: bool
    command: Command
    bloomed: frozenset[Point] = frozenset()
    faded: frozenset[Point] = frozenset()
    reason: str = ""


@dataclass(frozen=True)
class PlantingReport:
    accepted: bool
    bloomed: frozenset[Point] = frozenset()
    faded: frozenset[Point] = frozenset()
    reason: str = ""


def neighbor_count(point: Point, lights: set[Point]) -> int:
    x, y = point
    return sum(
        (x + dx, y + dy) in lights
        for dy in (-1, 0, 1)
        for dx in (-1, 0, 1)
        if dx != 0 or dy != 0
    )


def grow_once(
    blooms: set[Point] | frozenset[Point],
    width: int,
    height: int,
    extra_lights: set[Point] | frozenset[Point] = frozenset(),
) -> set[Point]:
    """Evolve one bounded generation, optionally adding non-bloom light sources."""
    ordinary = set(blooms)
    lights = ordinary | set(extra_lights)
    blocked = set(extra_lights)
    next_blooms: set[Point] = set()
    for y in range(height):
        for x in range(width):
            point = (x, y)
            if point in blocked:
                continue
            neighbors = neighbor_count(point, lights)
            if point in ordinary:
                alive_next = neighbors in (2, 3)
            else:
                alive_next = neighbors == 3
            if alive_next:
                next_blooms.add(point)
    return next_blooms


class GameState:
    """Pure game rules matching the FPGA implementation.

    Blooming buds are stored in ``blooms``. The immortal lantern spirit is
    separate, contributes as a live neighbor, and is removed from ordinary
    bloom results after every growth step.
    """

    def __init__(self, puzzle: Puzzle) -> None:
        self.puzzle = puzzle
        self.player = puzzle.player_start
        self.blooms = set(puzzle.buds)
        self.blooms.discard(self.player)
        self.turns_left = puzzle.turns
        self.generation = 0
        self.phase = Phase.ACTIVE
        self.last_rejected = False

    @property
    def bloom_count(self) -> int:
        return len(self.blooms)

    def issue(self, command: Command) -> TurnReport:
        if self.phase is not Phase.ACTIVE:
            return TurnReport(False, command, reason="这则谜题已经结束")

        dx, dy = command.value
        target = (self.player[0] + dx, self.player[1] + dy)
        if not self._inside(target):
            self.last_rejected = True
            return TurnReport(False, command, reason="灯灵不能走出花圃边界")
        if target in self.blooms:
            self.last_rejected = True
            return TurnReport(False, command, reason="落点已经有一枚花芽")

        before = set(self.blooms)
        self.player = target
        self.blooms = self._grow()
        self.turns_left -= 1
        self.generation += 1
        self.last_rejected = False

        if self.turns_left == 0:
            in_target = self.puzzle.target_min <= self.bloom_count <= self.puzzle.target_max
            self.phase = Phase.WON if in_target else Phase.LOST

        return TurnReport(
            True,
            command,
            frozenset(self.blooms - before),
            frozenset(before - self.blooms),
        )

    def _grow(self) -> set[Point]:
        return grow_once(self.blooms, self.puzzle.width, self.puzzle.height, {self.player})

    def _inside(self, point: Point) -> bool:
        return 0 <= point[0] < self.puzzle.width and 0 <= point[1] < self.puzzle.height

    @staticmethod
    def _neighbor_count(point: Point, lights: set[Point]) -> int:
        return neighbor_count(point, lights)


class PlantingState:
    """Two-phase classic puzzle state: place seeds, then verify pure growth."""

    def __init__(self, puzzle: PlantingPuzzle) -> None:
        self.puzzle = puzzle
        self.player = puzzle.player_start
        self.planted: set[Point] = set()
        self.planting_order: list[Point] = []
        self.blooms = set(puzzle.buds)
        self.seeds_left = puzzle.seeds
        self.generation = 0
        self.phase = PlantingPhase.PLANTING
        self.last_rejected = False
        self.start_layout_valid = False

    def move(self, command: Command) -> PlantingReport:
        if self.phase is not PlantingPhase.PLANTING:
            return PlantingReport(False, reason="生长开始后，灯灵只能静静观看")
        if command is Command.WAIT:
            return PlantingReport(False, reason="请移动灯灵，或在当前位置播种")
        dx, dy = command.value
        target = (self.player[0] + dx, self.player[1] + dy)
        if not self._inside(target):
            self.last_rejected = True
            return PlantingReport(False, reason="灯灵不能走出花圃边界")
        if target in self.blooms:
            self.last_rejected = True
            return PlantingReport(False, reason="这里已经有一枚花芽，请改走相邻空土格")
        self.player = target
        self.last_rejected = False
        return PlantingReport(True)

    def plant(self) -> PlantingReport:
        if self.phase is not PlantingPhase.PLANTING:
            return PlantingReport(False, reason="花谱已经开始生长")
        if self.player not in self.puzzle.seedable:
            self.last_rejected = True
            return PlantingReport(False, reason="这格土地无法播种")
        if self.player in self.blooms:
            self.last_rejected = True
            return PlantingReport(False, reason="这里已经有一枚花芽")
        if self.seeds_left <= 0:
            self.last_rejected = True
            return PlantingReport(False, reason="花种已经用完")
        self.planted.add(self.player)
        self.planting_order.append(self.player)
        self.blooms.add(self.player)
        self.seeds_left -= 1
        self.last_rejected = False
        return PlantingReport(True, bloomed=frozenset({self.player}))

    def remove_seed(self) -> PlantingReport:
        if self.phase is not PlantingPhase.PLANTING:
            return PlantingReport(False, reason="花谱已经开始生长")
        if not self.planting_order:
            self.last_rejected = True
            return PlantingReport(False, reason="还没有可以撤回的花种")
        point = self.planting_order.pop()
        self.planted.remove(point)
        self.blooms.remove(point)
        self.seeds_left += 1
        self.last_rejected = False
        return PlantingReport(True, faded=frozenset({point}))

    def start_growth(self) -> PlantingReport:
        if self.phase is not PlantingPhase.PLANTING:
            return PlantingReport(False, reason="花谱已经开始生长")
        if self.seeds_left > 0:
            self.last_rejected = True
            return PlantingReport(
                False,
                reason=f"还有 {self.seeds_left} 枚花种未种下，完成播种后再开始生长",
            )
        self.start_layout_valid = (
            self.puzzle.required_start_blooms is None
            or self.blooms == set(self.puzzle.required_start_blooms)
        )
        self.phase = PlantingPhase.GROWING
        self.last_rejected = False
        return PlantingReport(True)

    def advance(self) -> PlantingReport:
        if self.phase is not PlantingPhase.GROWING:
            return PlantingReport(False, reason="请先确认开始生长")
        before = set(self.blooms)
        self.blooms = grow_once(self.blooms, self.puzzle.width, self.puzzle.height)
        self.generation += 1
        if self.generation >= self.puzzle.validation_generation:
            self.phase = (
                PlantingPhase.WON
                if self.start_layout_valid
                and self.blooms == set(self.puzzle.expected_blooms)
                else PlantingPhase.LOST
            )
        return PlantingReport(
            True,
            bloomed=frozenset(self.blooms - before),
            faded=frozenset(before - self.blooms),
        )

    @property
    def bloom_count(self) -> int:
        return len(self.blooms)

    def _inside(self, point: Point) -> bool:
        return 0 <= point[0] < self.puzzle.width and 0 <= point[1] < self.puzzle.height
