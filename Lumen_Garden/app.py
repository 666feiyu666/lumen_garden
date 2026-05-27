from __future__ import annotations

import math
import os
from pathlib import Path

import pygame

from .audio import AudioManager
from .patterns import PLANTING_PUZZLES
from .puzzles import PUZZLES
from .model import Command, GameState, Phase, PlantingPhase, PlantingState
from .tutorial import TUTORIAL_CARD, TUTORIAL_STEPS, TutorialStep

SCREEN_SIZE = (1280, 720)
WINDOW_SIZES = ((1024, 576), (1280, 720), (1600, 900))
FPS = 60
PLANTING_PLAYBACK_INTERVAL = 0.7
ASSET_ROOT = Path(__file__).resolve().parent.parent / "assets"
FORMAL_BOARD_ORIGIN = (72, 150)
FORMAL_BOARD_TILE_LIMIT = 60
FORMAL_BOARD_MAX_SIZE = (550, 474)

BG_TOP = (18, 22, 49)
BG_BOTTOM = (29, 45, 48)
PANEL = (29, 38, 49)
PANEL_LIGHT = (42, 57, 55)
TEXT = (245, 238, 215)
TEXT_MUTED = (165, 178, 161)
CYAN = (146, 211, 166)
BUD = (135, 218, 139)
BUD_CORE = (243, 240, 174)
LANTERN = (255, 191, 76)
LANTERN_CORE = (255, 238, 177)
DANGER = (202, 132, 111)
GOLD = (255, 207, 99)
SOIL = (35, 52, 46)
SOIL_EDGE = (58, 83, 67)


class LumenGardenApp:
    def __init__(self) -> None:
        pygame.init()
        # Gameplay has no text fields; do not let an IME capture letter hotkeys.
        pygame.key.stop_text_input()
        pygame.display.set_caption("Lumen Garden / 萤光花园")
        self.window_size = SCREEN_SIZE
        self.window = pygame.display.set_mode(self.window_size)
        self.screen = pygame.Surface(SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.selected_puzzle = 0
        self.selected_planting = 0
        self.main_selection = 0
        self.menu_selection = 0
        self.planting_selection = 0
        self.scene = "menu"
        self.settings_open = False
        self.state: GameState | None = None
        self.planting_state: PlantingState | None = None
        self.planting_autoplay = False
        self.planting_playback_timer = 0.0
        self.planting_showcase_frames: list[frozenset[tuple[int, int]]] = []
        self.planting_showcase_index = 0
        self.tutorial_step = 0
        self.tutorial_resolved = False
        self.message = "选择一则月夜谜题"
        self.message_timer = 0.0
        self.flash_timer = 0.0
        self.bloomed: frozenset[tuple[int, int]] = frozenset()
        self.faded: frozenset[tuple[int, int]] = frozenset()
        self.elapsed = 0.0
        self.fonts = self._load_fonts()
        self.background = self._build_background()
        self.audio = AudioManager(ASSET_ROOT)
        self.audio.play_music("menu")

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.elapsed += dt
            self.message_timer = max(0.0, self.message_timer - dt)
            self.flash_timer = max(0.0, self.flash_timer - dt)
            self._handle_events()
            self._update_planting_playback(dt)
            self._draw()
            if self.window_size == SCREEN_SIZE:
                self.window.blit(self.screen, (0, 0))
            else:
                self.window.blit(pygame.transform.smoothscale(self.screen, self.window_size), (0, 0))
            pygame.display.flip()
        pygame.quit()

    def _load_fonts(self) -> dict[str, pygame.font.Font]:
        asset_fonts = ASSET_ROOT / "fonts"
        font_path = next(
            (
                path
                for pattern in ("*.ttf", "*.otf", "*.ttc")
                for path in sorted(asset_fonts.glob(pattern))
            ),
            None,
        )
        family = "Microsoft YaHei UI,Microsoft YaHei,SimHei,Arial"
        windows_fonts = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"

        def bundled_font(*names: str) -> Path | None:
            return next(
                (windows_fonts / name for name in names if (windows_fonts / name).exists()),
                None,
            )

        regular_path = bundled_font("msyh.ttc", "simhei.ttf", "arial.ttf")
        bold_path = bundled_font(
            "msyhbd.ttc", "msyh.ttc", "simhei.ttf", "arialbd.ttf", "arial.ttf"
        )

        def make(size: int, bold: bool = False) -> pygame.font.Font:
            selected_path = font_path or (bold_path if bold else regular_path)
            if selected_path:
                return pygame.font.Font(str(selected_path), size)
            try:
                return pygame.font.SysFont(family, size, bold=bold)
            except (OSError, TypeError, pygame.error):
                return pygame.font.Font(None, size)

        return {
            "title": make(60, True),
            "subtitle": make(20),
            "h1": make(30, True),
            "h2": make(22, True),
            "body": make(18),
            "small": make(15),
            "stat": make(28, True),
            "result": make(56, True),
        }

    @staticmethod
    def _build_background() -> pygame.Surface:
        background = pygame.Surface(SCREEN_SIZE)
        for y in range(SCREEN_SIZE[1]):
            amount = y / SCREEN_SIZE[1]
            color = tuple(
                int(BG_TOP[i] * (1 - amount) + BG_BOTTOM[i] * amount)
                for i in range(3)
            )
            pygame.draw.line(background, color, (0, y), (SCREEN_SIZE[0], y))
        haze = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        pygame.draw.circle(haze, (220, 210, 132, 20), (1015, 92), 104)
        pygame.draw.circle(haze, (112, 176, 133, 24), (834, 330), 350)
        pygame.draw.circle(haze, (63, 101, 70, 44), (224, 658), 280)
        for x, y, radius in (
            (84, 154, 2),
            (1138, 192, 3),
            (1065, 608, 2),
            (746, 82, 2),
            (1190, 421, 2),
            (45, 535, 2),
        ):
            pygame.draw.circle(haze, (255, 214, 110, 115), (x, y), radius)
        background.blit(haze, (0, 0))
        return background

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if self.audio.handle_event(event):
                continue
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.settings_open:
                    self._settings_key(event.key)
                    continue
                if self.scene == "menu":
                    self._menu_key(event.key)
                elif self.scene == "garden_menu":
                    self._garden_menu_key(event.key)
                elif self.scene == "planting_menu":
                    self._planting_menu_key(event.key)
                elif self.scene == "tutorial":
                    self._tutorial_key(event.key)
                elif self.scene == "game":
                    self._game_key(event.key)
                else:
                    self._planting_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._mouse_click(self._logical_point(event.pos))

    def _menu_key(self, key: int) -> None:
        if key in (pygame.K_ESCAPE, pygame.K_q):
            self.running = False
        elif key in (pygame.K_UP, pygame.K_w):
            self.main_selection = (self.main_selection - 1) % 3
            self.audio.play("select")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.main_selection = (self.main_selection + 1) % 3
            self.audio.play("select")
        elif key == pygame.K_p:
            self._open_planting_menu()
        elif key in (pygame.K_g, pygame.K_0, pygame.K_t):
            self._open_garden_menu()
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            (self._open_garden_menu, self._open_planting_menu, self._open_settings)[
                self.main_selection
            ]()

    def _garden_menu_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.scene = "menu"
        elif key in (pygame.K_UP, pygame.K_w):
            self.menu_selection = (self.menu_selection - 1) % (len(PUZZLES) + 1)
            self.audio.play("select")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.menu_selection = (self.menu_selection + 1) % (len(PUZZLES) + 1)
            self.audio.play("select")
        elif key in (pygame.K_0, pygame.K_t):
            self._start_tutorial()
        elif pygame.K_1 <= key <= pygame.K_5:
            self._start_puzzle(key - pygame.K_1)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.menu_selection == 0:
                self._start_tutorial()
            else:
                self._start_puzzle(self.menu_selection - 1)

    def _planting_menu_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.scene = "menu"
        elif key in (pygame.K_UP, pygame.K_w):
            self.planting_selection = (self.planting_selection - 1) % len(PLANTING_PUZZLES)
            self.audio.play("select")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.planting_selection = (self.planting_selection + 1) % len(PLANTING_PUZZLES)
            self.audio.play("select")
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self._start_planting(self.planting_selection)

    def _open_garden_menu(self) -> None:
        self.scene = "garden_menu"
        self.menu_selection = 0
        self.audio.play("select")

    def _open_planting_menu(self) -> None:
        self.scene = "planting_menu"
        self.planting_selection = 0
        self.audio.play("select")

    def _open_settings(self) -> None:
        self.settings_open = True
        self.audio.play("select")

    def _settings_key(self, key: int) -> None:
        if key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.settings_open = False

    def _set_window_size(self, size: tuple[int, int]) -> None:
        self.window_size = size
        self.window = pygame.display.set_mode(size)

    def _logical_point(self, point: tuple[int, int]) -> tuple[int, int]:
        return (
            point[0] * SCREEN_SIZE[0] // self.window_size[0],
            point[1] * SCREEN_SIZE[1] // self.window_size[1],
        )

    def _mouse_click(self, point: tuple[int, int]) -> None:
        if self.settings_open:
            self._settings_click(point)
            return
        if self.scene == "menu":
            for index in range(3):
                if pygame.Rect(132, 334 + index * 88, 570, 68).collidepoint(point):
                    self.main_selection = index
                    (self._open_garden_menu, self._open_planting_menu, self._open_settings)[
                        index
                    ]()
                    return
        elif self.scene == "garden_menu":
            for index in range(len(PUZZLES) + 1):
                if pygame.Rect(78, 186 + index * 63, 634, 52).collidepoint(point):
                    self.menu_selection = index
                    self._start_tutorial() if index == 0 else self._start_puzzle(index - 1)
                    return
            if pygame.Rect(802, 568, 180, 34).collidepoint(point):
                self.scene = "menu"
        elif self.scene == "planting_menu":
            for index in range(len(PLANTING_PUZZLES)):
                if pygame.Rect(92, 205 + index * 66, 650, 54).collidepoint(point):
                    self.planting_selection = index
                    self._start_planting(index)
                    return
            if pygame.Rect(824, 477, 190, 40).collidepoint(point):
                self.scene = "menu"
        elif self.scene == "game":
            self._game_click(point)
        elif self.scene == "planting":
            self._planting_click(point)
        elif self.scene == "tutorial":
            self._tutorial_click(point)

    def _settings_click(self, point: tuple[int, int]) -> None:
        for index, size in enumerate(WINDOW_SIZES):
            if pygame.Rect(420 + index * 144, 282, 128, 45).collidepoint(point):
                self._set_window_size(size)
                return
        if pygame.Rect(420, 414, 52, 45).collidepoint(point):
            self.audio.set_volume(self.audio.volume - 0.1)
        elif pygame.Rect(658, 414, 52, 45).collidepoint(point):
            self.audio.set_volume(self.audio.volume + 0.1)
        elif pygame.Rect(732, 414, 120, 45).collidepoint(point):
            self.audio.toggle_enabled()
        elif pygame.Rect(420, 514, 432, 44).collidepoint(point):
            self.settings_open = False

    @staticmethod
    def _grid_command(
        point: tuple[int, int], board: pygame.Rect, tile: int, player: tuple[int, int]
    ) -> Command | None:
        if not board.collidepoint(point):
            return None
        clicked = ((point[0] - board.x) // tile, (point[1] - board.y) // tile)
        delta = (clicked[0] - player[0], clicked[1] - player[1])
        return {
            (0, 0): Command.WAIT,
            (0, -1): Command.UP,
            (0, 1): Command.DOWN,
            (-1, 0): Command.LEFT,
            (1, 0): Command.RIGHT,
        }.get(delta)

    @staticmethod
    def _formal_board_layout(width: int, height: int) -> tuple[pygame.Rect, int]:
        tile = min(
            FORMAL_BOARD_TILE_LIMIT,
            FORMAL_BOARD_MAX_SIZE[0] // width,
            FORMAL_BOARD_MAX_SIZE[1] // height,
        )
        board = pygame.Rect(
            FORMAL_BOARD_ORIGIN[0],
            FORMAL_BOARD_ORIGIN[1],
            width * tile,
            height * tile,
        )
        return board, tile

    def _game_click(self, point: tuple[int, int]) -> None:
        assert self.state is not None
        puzzle = self.state.puzzle
        board, tile = self._formal_board_layout(puzzle.width, puzzle.height)
        command = self._grid_command(point, board, tile, self.state.player)
        if command is not None and self.state.phase is Phase.ACTIVE:
            self._issue(command)
        elif pygame.Rect(796, 495, 385, 42).collidepoint(point):
            self._issue(Command.WAIT)
        elif pygame.Rect(796, 550, 182, 42).collidepoint(point):
            self._start_puzzle(self.selected_puzzle)
        elif pygame.Rect(995, 550, 186, 42).collidepoint(point):
            self.scene = "garden_menu"
            self.state = None
            self.audio.play_music("menu")

    def _planting_click(self, point: tuple[int, int]) -> None:
        assert self.planting_state is not None
        state = self.planting_state
        puzzle = state.puzzle
        board, tile = self._formal_board_layout(puzzle.width, puzzle.height)
        if state.phase is PlantingPhase.PLANTING:
            command = self._grid_command(
                point,
                board,
                tile,
                state.player,
            )
            if command is Command.WAIT:
                self.message = (
                    f"当前位置可按 P 播种；还剩 {state.seeds_left} 枚花种"
                    if state.seeds_left > 0
                    else "花种已全部播下，请按 SPACE 或 ENTER 开始生长"
                )
                self.message_timer = 1.8
                self.audio.play("select")
                return
            if command is not None:
                key = {
                    Command.UP: pygame.K_UP,
                    Command.DOWN: pygame.K_DOWN,
                    Command.LEFT: pygame.K_LEFT,
                    Command.RIGHT: pygame.K_RIGHT,
                }[command]
                self._planting_key(key)
                return
        if pygame.Rect(686, 570, 90, 40).collidepoint(point):
            self._planting_key(
                pygame.K_p if state.phase is PlantingPhase.PLANTING else pygame.K_SPACE
            )
        elif pygame.Rect(785, 570, 90, 40).collidepoint(point) and state.phase is PlantingPhase.PLANTING:
            self._planting_key(pygame.K_x)
        elif pygame.Rect(785, 570, 90, 40).collidepoint(point) and state.phase in (
            PlantingPhase.GROWING,
            PlantingPhase.WON,
        ):
            self._planting_key(pygame.K_RETURN)
        elif pygame.Rect(884, 570, 90, 40).collidepoint(point) and state.phase is PlantingPhase.PLANTING:
            self._planting_key(pygame.K_RETURN)
        elif pygame.Rect(983, 570, 90, 40).collidepoint(point):
            self._planting_key(pygame.K_r)
        elif pygame.Rect(1082, 570, 90, 40).collidepoint(point):
            self.scene = "planting_menu"
            self.planting_state = None
            self.audio.play_music("menu")

    def _tutorial_click(self, point: tuple[int, int]) -> None:
        if self.tutorial_step >= len(TUTORIAL_STEPS):
            if pygame.Rect(254, 430, 300, 48).collidepoint(point):
                self._start_puzzle(0)
            elif pygame.Rect(254, 485, 300, 42).collidepoint(point):
                self.scene = "garden_menu"
                self.state = None
                self.audio.play_music("menu")
            return
        if pygame.Rect(656, 512, 218, 49).collidepoint(point):
            self._tutorial_key(pygame.K_RETURN)
        elif pygame.Rect(656, 574, 114, 33).collidepoint(point):
            self._tutorial_key(pygame.K_r)
        elif pygame.Rect(788, 574, 150, 33).collidepoint(point):
            self.scene = "garden_menu"
            self.state = None
            self.audio.play_music("menu")
        elif self.state is not None and self.tutorial_step < len(TUTORIAL_STEPS):
            step = TUTORIAL_STEPS[self.tutorial_step]
            tile = 68 if step.puzzle.width <= 5 else 62
            command = self._grid_command(
                point,
                pygame.Rect(88, 180, step.puzzle.width * tile, step.puzzle.height * tile),
                tile,
                self.state.player,
            )
            key = {
                Command.WAIT: pygame.K_SPACE,
                Command.UP: pygame.K_UP,
                Command.DOWN: pygame.K_DOWN,
                Command.LEFT: pygame.K_LEFT,
                Command.RIGHT: pygame.K_RIGHT,
            }.get(command)
            if key is not None:
                self._tutorial_key(key)

    @staticmethod
    def _command_for_key(key: int) -> Command | None:
        return {
            pygame.K_w: Command.UP,
            pygame.K_UP: Command.UP,
            pygame.K_s: Command.DOWN,
            pygame.K_DOWN: Command.DOWN,
            pygame.K_a: Command.LEFT,
            pygame.K_LEFT: Command.LEFT,
            pygame.K_d: Command.RIGHT,
            pygame.K_RIGHT: Command.RIGHT,
            pygame.K_SPACE: Command.WAIT,
        }.get(key)

    def _game_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.scene = "garden_menu"
            self.state = None
            self.audio.play_music("menu")
            return
        if pygame.K_1 <= key <= pygame.K_5:
            self._start_puzzle(key - pygame.K_1)
            return
        if key == pygame.K_r or (key == pygame.K_RETURN and self.state and self.state.phase is not Phase.ACTIVE):
            self._start_puzzle(self.selected_puzzle)
            return

        command = self._command_for_key(key)
        if command is not None and self.state is not None:
            self._issue(command)

    def _start_puzzle(self, index: int) -> None:
        self.selected_puzzle = index
        self.menu_selection = index + 1
        self.planting_state = None
        self.state = GameState(PUZZLES[index])
        self.scene = "game"
        self.message = "谜题开始：带领金色灯灵走入花圃"
        self.message_timer = 2.4
        self.flash_timer = 0.0
        self.bloomed = frozenset()
        self.faded = frozenset()
        self.audio.play("select")
        self.audio.play_music("puzzle")

    def _start_planting(self, index: int) -> None:
        self.selected_planting = index
        self.menu_selection = len(PUZZLES) + 1 + index
        self.state = None
        self.planting_state = PlantingState(PLANTING_PUZZLES[index])
        self.planting_autoplay = False
        self.planting_playback_timer = 0.0
        self.planting_showcase_frames = []
        self.planting_showcase_index = 0
        self.scene = "planting"
        self.message = "移动灯灵到缺失位置，按 P 播种，花种用完后开始生长"
        self.message_timer = 99.0
        self.flash_timer = 0.0
        self.bloomed = frozenset()
        self.faded = frozenset()
        self.audio.play("select")
        self.audio.play_music("puzzle")

    def _start_tutorial(self) -> None:
        self.menu_selection = 0
        self.scene = "tutorial"
        self.planting_state = None
        self.tutorial_step = 0
        self.audio.play("select")
        self.audio.play_music("puzzle")
        self._load_tutorial_step()

    def _load_tutorial_step(self) -> None:
        self.tutorial_resolved = False
        self.flash_timer = 0.0
        self.bloomed = frozenset()
        self.faded = frozenset()
        if self.tutorial_step < len(TUTORIAL_STEPS):
            step = TUTORIAL_STEPS[self.tutorial_step]
            self.state = GameState(step.puzzle)
            self.message = step.instruction
        else:
            self.state = None
            self.message = "月夜入门完成"
        self.message_timer = 99.0

    def _tutorial_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.scene = "garden_menu"
            self.state = None
            self.audio.play_music("menu")
            return
        if self.tutorial_step >= len(TUTORIAL_STEPS):
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self._start_puzzle(0)
            elif key == pygame.K_r:
                self._start_tutorial()
            return

        step = TUTORIAL_STEPS[self.tutorial_step]
        if key == pygame.K_r:
            self._load_tutorial_step()
            return
        if key == pygame.K_RETURN:
            if not step.allowed_commands or self.tutorial_resolved:
                self.tutorial_step += 1
                self._load_tutorial_step()
            else:
                self.message = step.instruction
            return

        command = self._command_for_key(key)
        if command is None:
            return
        if not step.allowed_commands:
            self.message = "按 ENTER 进入第一段花园指引"
            return
        if command not in step.allowed_commands:
            self.message = f"本步骤请执行：{step.instruction}"
            self.audio.play("reject")
            return
        if self.tutorial_resolved:
            self.message = "按 ENTER 进入下一段指引"
            return
        self._issue_tutorial(step, command)

    def _issue_tutorial(self, step: TutorialStep, command: Command) -> None:
        assert self.state is not None
        report = self.state.issue(command)
        if not report.accepted:
            self.message = report.reason
            self.audio.play("reject")
            return

        self.bloomed = report.bloomed
        self.faded = report.faded
        self.flash_timer = 0.7
        self.audio.play("wait" if command is Command.WAIT else "move")
        if step.quiz:
            if self.state.phase is Phase.WON:
                self.tutorial_resolved = True
                self.message = step.result_text
                self.audio.play("win")
            elif self.state.phase is Phase.LOST:
                self.message = "花芽数量还不合适，按 R 重试这则小谜题"
                self.audio.play("lose")
            else:
                self.message = "还剩一轮生长：让最终盛开的花芽达到 3"
        else:
            self.tutorial_resolved = True
            self.message = step.result_text

    def _issue(self, command: Command) -> None:
        assert self.state is not None
        previous_phase = self.state.phase
        report = self.state.issue(command)
        if not report.accepted:
            self.message = report.reason
            self.message_timer = 1.1
            self.audio.play("reject")
            return

        self.bloomed = report.bloomed
        self.faded = report.faded
        self.flash_timer = 0.34
        self.message = "花园生长了一轮"
        self.message_timer = 0.55
        self.audio.play("wait" if command is Command.WAIT else "move")
        if previous_phase is Phase.ACTIVE and self.state.phase is Phase.WON:
            self.message = "花光恰好：谜题解开"
            self.message_timer = 99.0
            self.audio.play("win")
            self.audio.play_music("result")
        elif previous_phase is Phase.ACTIVE and self.state.phase is Phase.LOST:
            self.message = "月夜已尽：花芽未能成景"
            self.message_timer = 99.0
            self.audio.play("lose")
            self.audio.play_music("result")

    def _planting_key(self, key: int) -> None:
        assert self.planting_state is not None
        state = self.planting_state
        if key == pygame.K_ESCAPE:
            self.scene = "planting_menu"
            self.planting_state = None
            self.audio.play_music("menu")
            return
        if key == pygame.K_r:
            self._start_planting(self.selected_planting)
            return
        if state.phase is PlantingPhase.LOST:
            if key == pygame.K_RETURN:
                self._start_planting(self.selected_planting)
            return
        if state.phase is PlantingPhase.WON:
            if key == pygame.K_SPACE:
                self.planting_autoplay = not self.planting_autoplay
                self.planting_playback_timer = 0.0
                self.message = (
                    "成谱演示继续循环；按 SPACE 暂停"
                    if self.planting_autoplay
                    else "成谱演示已暂停；按 ENTER 从开头重播"
                )
                self.message_timer = 99.0
                self.audio.play("select")
            elif key == pygame.K_RETURN:
                self._restart_planting_showcase()
            return

        if state.phase is PlantingPhase.PLANTING:
            if key == pygame.K_p:
                report = state.plant()
                accepted_message = (
                    "花种已全部播下，按 SPACE 或 ENTER 开始生长"
                    if state.seeds_left == 0
                    else "一枚花种落入土壤，继续按 P 播种"
                )
                sound = "move"
            elif key in (pygame.K_BACKSPACE, pygame.K_x):
                report = state.remove_seed()
                accepted_message = "收回一枚花种，可以重新选择位置"
                sound = "wait"
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                report = state.start_growth()
                accepted_message = "花圃开始自行生长；按 SPACE 可暂停播放"
                sound = "wait"
            else:
                command = self._command_for_key(key)
                if command is None or command is Command.WAIT:
                    return
                report = state.move(command)
                accepted_message = "选择土格后按 P 播种"
                sound = "move"
            if report.accepted and key in (pygame.K_RETURN, pygame.K_SPACE):
                self.planting_autoplay = True
                self.planting_playback_timer = 0.0
                self.planting_showcase_frames = [frozenset(state.blooms)]
                self.planting_showcase_index = 0
        else:
            if key == pygame.K_SPACE:
                self.planting_autoplay = not self.planting_autoplay
                self.planting_playback_timer = 0.0
                self.message = (
                    "花谱继续自行生长；按 SPACE 暂停"
                    if self.planting_autoplay
                    else "花谱已暂停；按 ENTER 单步查看"
                )
                self.message_timer = 99.0
                self.audio.play("select")
                return
            if key != pygame.K_RETURN:
                return
            self.planting_autoplay = False
            self._advance_planting_generation()
            return

        if not report.accepted:
            self.message = report.reason
            self.message_timer = 1.6
            self.audio.play("reject")
            return
        self.bloomed = report.bloomed
        self.faded = report.faded
        self.flash_timer = 0.5
        self.message = accepted_message
        self.message_timer = 99.0
        self.audio.play(sound)

    def _update_planting_playback(self, dt: float) -> None:
        if (
            self.scene != "planting"
            or self.planting_state is None
            or self.planting_state.phase not in (PlantingPhase.GROWING, PlantingPhase.WON)
            or not self.planting_autoplay
        ):
            return
        self.planting_playback_timer += dt
        if self.planting_playback_timer >= PLANTING_PLAYBACK_INTERVAL:
            self.planting_playback_timer -= PLANTING_PLAYBACK_INTERVAL
            if self.planting_state.phase is PlantingPhase.GROWING:
                self._advance_planting_generation()
            else:
                self._advance_planting_showcase()

    def _advance_planting_generation(self) -> None:
        assert self.planting_state is not None
        state = self.planting_state
        report = state.advance()
        if not report.accepted:
            return
        self.bloomed = report.bloomed
        self.faded = report.faded
        self.flash_timer = 0.5
        self.planting_showcase_frames.append(frozenset(state.blooms))
        self.planting_showcase_index = len(self.planting_showcase_frames) - 1
        self.message = f"花谱自行生长至第 {state.generation} 代"
        self.message_timer = 99.0
        self.audio.play("wait")
        if state.phase is PlantingPhase.WON:
            self.planting_autoplay = True
            self.planting_playback_timer = 0.0
            self.message = f"{state.puzzle.name_cn}成谱：{state.puzzle.pattern.behavior}；正在循环回看"
            self.audio.play("win")
            self.audio.play_music("result")
        elif state.phase is PlantingPhase.LOST:
            self.planting_autoplay = False
            self.message = f"{state.puzzle.name_cn}未达到目标行为，按 R 重新播种"
            self.audio.play("lose")
            self.audio.play_music("result")

    def _advance_planting_showcase(self) -> None:
        if len(self.planting_showcase_frames) < 2:
            return
        before = self.planting_showcase_frames[self.planting_showcase_index]
        self.planting_showcase_index = (
            self.planting_showcase_index + 1
        ) % len(self.planting_showcase_frames)
        after = self.planting_showcase_frames[self.planting_showcase_index]
        self.bloomed = frozenset(after - before)
        self.faded = frozenset(before - after)
        self.flash_timer = 0.5
        self.audio.play("wait")

    def _restart_planting_showcase(self) -> None:
        if not self.planting_showcase_frames:
            return
        before = self.planting_showcase_frames[self.planting_showcase_index]
        self.planting_showcase_index = 0
        after = self.planting_showcase_frames[0]
        self.bloomed = frozenset(after - before)
        self.faded = frozenset(before - after)
        self.flash_timer = 0.5
        self.planting_autoplay = True
        self.planting_playback_timer = 0.0
        self.message = "从起始花形重播成谱演示；按 SPACE 暂停"
        self.message_timer = 99.0
        self.audio.play("select")

    def _draw(self) -> None:
        self.screen.blit(self.background, (0, 0))
        if self.scene == "menu":
            self._draw_menu()
        elif self.scene == "garden_menu":
            self._draw_garden_menu()
        elif self.scene == "planting_menu":
            self._draw_planting_menu()
        elif self.scene == "tutorial":
            self._draw_tutorial()
        elif self.scene == "game":
            self._draw_game()
        else:
            self._draw_planting()
        if self.settings_open:
            self._draw_settings()

    def _draw_menu(self) -> None:
        self._text("萤光花园", self.fonts["title"], TEXT, (128, 126))
        self._text("LUMEN GARDEN  //  A PUZZLE OF BLOOMING LIGHT", self.fonts["subtitle"], CYAN, (132, 202))
        self._text(
            "让微光生长，或亲手种下一则会自行绽放的花谱。",
            self.fonts["body"],
            TEXT_MUTED,
            (132, 250),
        )
        labels = (
            ("花园引导", "移动灯灵，在每一轮生长中照料花圃"),
            ("种植花谱", "播下花种，再放手观看经典图案生长"),
            ("设置", "窗口大小与声音"),
        )
        for index, (label, detail) in enumerate(labels):
            rect = pygame.Rect(132, 334 + index * 88, 570, 68)
            self._rounded_panel(rect, active=index == self.main_selection)
            color = TEXT if index == self.main_selection else TEXT_MUTED
            accent = CYAN if index == 0 else GOLD if index == 1 else TEXT_MUTED
            self._text(label, self.fonts["h2"], accent, (160, rect.y + 13))
            self._text(detail, self.fonts["small"], color, (316, rect.y + 23))
        self._text("点击选择    ↑ ↓ / ENTER 操作    ESC 退出", self.fonts["small"], TEXT_MUTED, (136, 632))

        garden = pygame.Rect(820, 148, 318, 410)
        self._rounded_panel(garden, active=False)
        self._text("今夜的花园", self.fonts["h1"], TEXT, (858, 192))
        self._text("两种照料方式", self.fonts["body"], TEXT_MUTED, (858, 249))
        self._stat_line_at("引导", "边走边生长", 858, 322)
        self._stat_line_at("种植", "先种后放手", 858, 375)
        self._stat_line_at("花谱", "P01-P05 已开放", 858, 428)
        self._text("用鼠标即可游玩", self.fonts["h2"], CYAN, (858, 501))

    def _draw_garden_menu(self) -> None:
        self._text("花园引导", self.fonts["title"], TEXT, (74, 52))
        self._text("移动灯灵，每一次行动都会让花圃生长一轮", self.fonts["subtitle"], CYAN, (78, 126))
        menu_puzzles = (TUTORIAL_CARD, *PUZZLES)
        for index, puzzle in enumerate(menu_puzzles):
            rect = pygame.Rect(78, 186 + index * 63, 634, 52)
            selected = index == self.menu_selection
            self._rounded_panel(rect, active=selected)
            color = TEXT if selected else TEXT_MUTED
            number_color = CYAN if selected else (67, 104, 102)
            self._text(f"{puzzle.number:02d}", self.fonts["h2"], number_color, (96, rect.y + 10))
            self._text(f"{puzzle.name}  {puzzle.name_cn}", self.fonts["h2"], color, (148, rect.y + 8))
            if index == 0:
                info = "5 x 5    月夜指引    无压力"
            else:
                info = f"{puzzle.width} x {puzzle.height}    {puzzle.turns} 步    盛放 {puzzle.target_label}"
            self._text(info, self.fonts["small"], color, (405, rect.y + 16))

        intro = pygame.Rect(770, 172, 430, 440)
        self._rounded_panel(intro, active=False)
        self._text("花园手记", self.fonts["h1"], TEXT, (802, 253))
        if self.menu_selection == 0:
            self._text("随灯灵学习花芽的盛放规律。", self.fonts["body"], TEXT_MUTED, (802, 312))
            self._stat_line("篇章", "月夜入门", 371)
            self._stat_line("主题", "微光相伴", 417)
            self._stat_line("挑战", "无失败惩罚", 463)
        elif self.menu_selection <= len(PUZZLES):
            puzzle = menu_puzzles[self.menu_selection]
            self._text(puzzle.description, self.fonts["body"], TEXT_MUTED, (802, 312))
            self._stat_line("花圃", f"{puzzle.width} x {puzzle.height}", 371)
            self._stat_line("可用步数", f"{puzzle.turns} 步", 417)
            self._stat_line("盛开目标", puzzle.target_label, 463)
        self._text("点击卡片或 ENTER 开始", self.fonts["h2"], CYAN, (802, 545))
        back = pygame.Rect(802, 568, 180, 34)
        self._rounded_panel(back, active=False)
        self._text("返回主菜单", self.fonts["small"], TEXT_MUTED, (839, 578))

    def _draw_planting_menu(self) -> None:
        self._text("种植花谱", self.fonts["title"], TEXT, (112, 90))
        self._text("移动灯灵播下有限花种，确认后让花谱自行生长", self.fonts["subtitle"], GOLD, (116, 167))
        for index, puzzle in enumerate(PLANTING_PUZZLES):
            rect = pygame.Rect(92, 205 + index * 66, 650, 54)
            selected = index == self.planting_selection
            self._rounded_panel(rect, active=selected)
            self._text(f"P{puzzle.number:02d}", self.fonts["h2"], GOLD, (143, rect.y + 20))
            self._text(f"{puzzle.name}  {puzzle.name_cn}", self.fonts["h2"], TEXT, (230, rect.y + 17))
            self._text(f"{puzzle.seeds} 枚花种    {puzzle.pattern.kind}", self.fonts["small"], TEXT_MUTED, (520, rect.y + 26))
        panel = pygame.Rect(790, 205, 390, 330)
        self._rounded_panel(panel, active=False)
        puzzle = PLANTING_PUZZLES[self.planting_selection]
        self._text("花谱札记", self.fonts["h1"], TEXT, (874, 250))
        self._stat_line_at("目标", puzzle.name_cn, 874, 318)
        self._stat_line_at("花种", f"{puzzle.seeds} 枚", 874, 367)
        self._stat_line_at("验证", f"观察 {puzzle.validation_generation} 代", 874, 416)
        self._text("点击卡片开始种植", self.fonts["h2"], GOLD, (92, 572))
        back = pygame.Rect(824, 477, 190, 40)
        self._rounded_panel(back, active=False)
        self._text("返回主菜单", self.fonts["small"], TEXT_MUTED, (914, 473))

    def _draw_settings(self) -> None:
        veil = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        veil.fill((5, 8, 14, 170))
        self.screen.blit(veil, (0, 0))
        panel = pygame.Rect(378, 142, 524, 446)
        self._rounded_panel(panel, active=False)
        self._text("设置", self.fonts["h1"], TEXT, (420, 183))
        self._text("窗口大小", self.fonts["body"], TEXT_MUTED, (420, 246))
        for index, size in enumerate(WINDOW_SIZES):
            rect = pygame.Rect(420 + index * 144, 282, 128, 45)
            self._rounded_panel(rect, active=size == self.window_size)
            self._text(f"{size[0]} x {size[1]}", self.fonts["small"], TEXT, (rect.x + 13, rect.y + 14))
        self._text("音量", self.fonts["body"], TEXT_MUTED, (420, 377))
        for rect, label in (
            (pygame.Rect(420, 414, 52, 45), "-"),
            (pygame.Rect(658, 414, 52, 45), "+"),
        ):
            self._rounded_panel(rect, active=False)
            self._text(label, self.fonts["h2"], TEXT, (rect.x + 19, rect.y + 10))
        self._text(f"{int(self.audio.volume * 100):03d}%", self.fonts["stat"], TEXT, (526, 421))
        mute = pygame.Rect(732, 414, 120, 45)
        self._rounded_panel(mute, active=not self.audio.enabled)
        self._text("静音" if self.audio.enabled else "已静音", self.fonts["body"], TEXT, (mute.x + 32, mute.y + 13))
        close = pygame.Rect(420, 514, 432, 44)
        self._rounded_panel(close, active=True)
        self._text("关闭设置", self.fonts["h2"], CYAN, (594, 525))

    def _draw_tutorial(self) -> None:
        self._text("萤光花园", self.fonts["h1"], TEXT, (52, 30))
        self._text("引导 00  /  GUIDE  月夜入门", self.fonts["subtitle"], CYAN, (52, 75))
        if self.tutorial_step >= len(TUTORIAL_STEPS):
            self._draw_tutorial_complete()
            return

        assert self.state is not None
        step = TUTORIAL_STEPS[self.tutorial_step]
        tile = 68 if step.puzzle.width <= 5 else 62
        board_rect = pygame.Rect(88, 180, step.puzzle.width * tile, step.puzzle.height * tile)
        frame = board_rect.inflate(36, 36)
        self._rounded_panel(frame, active=False)
        self._draw_board(board_rect, tile)
        self._draw_tutorial_marks(board_rect, tile, step)

        panel = pygame.Rect(620, 116, 605, 538)
        self._rounded_panel(panel, active=False)
        self._text(f"月夜指引  {self.tutorial_step + 1:02d} / {len(TUTORIAL_STEPS):02d}", self.fonts["small"], CYAN, (656, 151))
        self._text(step.title, self.fonts["h1"], TEXT, (656, 185))
        for index, line in enumerate(step.lines):
            self._text(line, self.fonts["body"], TEXT_MUTED, (656, 252 + index * 35))

        if step.quiz:
            self._text("盛开花芽", self.fonts["small"], TEXT_MUTED, (656, 349))
            self._text(f"{self.state.bloom_count:03d}", self.fonts["stat"], BUD, (656, 376))
            self._text("盛开目标", self.fonts["small"], TEXT_MUTED, (864, 349))
            self._text(step.puzzle.target_label, self.fonts["stat"], GOLD, (864, 376))
            self._text("剩余夜步", self.fonts["small"], TEXT_MUTED, (1034, 349))
            self._text(f"{self.state.turns_left:02d}", self.fonts["stat"], TEXT, (1034, 376))
        elif step.focus is not None:
            count = self._tutorial_neighbor_count(step.focus)
            self._text("观察格伙伴数", self.fonts["small"], TEXT_MUTED, (656, 349))
            self._text(f"{count:02d}", self.fonts["stat"], CYAN, (656, 376))

        message_color = BUD if self.tutorial_resolved else CYAN
        if step.quiz and self.state.phase is Phase.LOST:
            message_color = DANGER
        self._text(self.message, self.fonts["body"], message_color, (656, 465))
        if self.tutorial_resolved:
            self._text("ENTER  下一步", self.fonts["h2"], CYAN, (656, 527))
        else:
            self._text(step.instruction, self.fonts["h2"], CYAN, (656, 527))
        self._text("R 重试当前指引    ESC 返回引导选择", self.fonts["small"], TEXT_MUTED, (656, 584))

    def _draw_tutorial_complete(self) -> None:
        panel = pygame.Rect(185, 150, 910, 440)
        self._rounded_panel(panel, active=False)
        self._text("月夜入门完成", self.fonts["result"], BUD, (252, 218))
        self._text("你已经看过花芽熄灭、相伴盛开与灯灵引路。", self.fonts["body"], TEXT, (254, 326))
        self._text("每则谜题都要在黎明之前留下恰好数量的花光。", self.fonts["body"], TEXT_MUTED, (254, 364))
        self._text("ENTER  开始 01 初光", self.fonts["h2"], CYAN, (254, 447))
        self._text("R 重温入门       ESC 返回引导选择", self.fonts["body"], TEXT_MUTED, (254, 497))

    def _draw_game(self) -> None:
        assert self.state is not None
        state = self.state
        puzzle = state.puzzle
        self._text("萤光花园", self.fonts["h1"], TEXT, (52, 30))
        self._text(
            f"谜题 0{puzzle.number}  /  {puzzle.name}  {puzzle.name_cn}",
            self.fonts["subtitle"],
            CYAN,
            (52, 75),
        )

        board_rect, tile = self._formal_board_layout(puzzle.width, puzzle.height)
        frame = board_rect.inflate(30, 30)
        self._rounded_panel(frame, active=False)
        self._draw_board(board_rect, tile)

        panel = pygame.Rect(760, 116, 465, 538)
        self._rounded_panel(panel, active=False)
        self._text("花园记录", self.fonts["h1"], TEXT, (796, 150))
        self._text("盛开花芽", self.fonts["small"], TEXT_MUTED, (796, 213))
        self._text(f"{state.bloom_count:03d}", self.fonts["stat"], BUD, (796, 239))
        self._text("盛开目标", self.fonts["small"], TEXT_MUTED, (1008, 213))
        self._text(puzzle.target_label, self.fonts["stat"], GOLD, (1008, 239))
        self._text("黎明倒计时", self.fonts["small"], TEXT_MUTED, (796, 306))
        self._text(f"{state.turns_left:02d}", self.fonts["stat"], TEXT, (796, 332))
        self._text("生长轮次", self.fonts["small"], TEXT_MUTED, (1008, 306))
        self._text(f"{state.generation:02d}", self.fonts["stat"], TEXT, (1008, 332))

        status_color = DANGER if state.last_rejected else CYAN
        if state.phase is Phase.WON:
            status_color = BUD
        elif state.phase is Phase.LOST:
            status_color = DANGER
        self._text(self.message if self.message_timer > 0 else "等待灯灵前行", self.fonts["body"], status_color, (796, 405))

        self._text("灯灵行动", self.fonts["h2"], TEXT, (796, 452))
        wait = pygame.Rect(796, 495, 385, 42)
        retry = pygame.Rect(796, 550, 182, 42)
        back = pygame.Rect(995, 550, 186, 42)
        for rect in (wait, retry, back):
            self._rounded_panel(rect, active=False)
        self._text("停留并生长一轮", self.fonts["body"], CYAN, (918, 507))
        self._text("重试", self.fonts["body"], TEXT_MUTED, (866, 562))
        self._text("返回选择", self.fonts["body"], TEXT_MUTED, (1053, 562))
        self._text("也可点击灯灵或相邻土格行动", self.fonts["small"], TEXT_MUTED, (796, 614))

        if state.phase is not Phase.ACTIVE:
            self._draw_result_overlay(frame, state.phase)

    def _draw_planting(self) -> None:
        assert self.planting_state is not None
        state = self.planting_state
        puzzle = state.puzzle
        self._text("萤光花园", self.fonts["h1"], TEXT, (52, 30))
        self._text(
            f"种植花谱 P{puzzle.number:02d}  /  {puzzle.name}  {puzzle.name_cn}",
            self.fonts["subtitle"],
            GOLD,
            (52, 75),
        )

        board_rect, tile = self._formal_board_layout(puzzle.width, puzzle.height)
        frame = board_rect.inflate(30, 30)
        self._rounded_panel(frame, active=False)
        self._draw_planting_board(board_rect, tile)

        panel = pygame.Rect(650, 116, 575, 538)
        self._rounded_panel(panel, active=False)
        self._text("花谱札记", self.fonts["h1"], TEXT, (686, 150))
        self._text(f"{puzzle.pattern.kind}  /  {puzzle.pattern.behavior}", self.fonts["body"], TEXT_MUTED, (686, 201))
        phase_label = "播种阶段" if state.phase is PlantingPhase.PLANTING else "生长验证"
        if state.phase is PlantingPhase.WON:
            phase_label = "成谱演示"
        elif state.phase is PlantingPhase.LOST:
            phase_label = "重新播种"
        self._text("阶段", self.fonts["small"], TEXT_MUTED, (686, 257))
        self._text(phase_label, self.fonts["stat"], CYAN, (686, 282))
        self._text("剩余花种", self.fonts["small"], TEXT_MUTED, (921, 257))
        self._text(f"{state.seeds_left:02d}", self.fonts["stat"], GOLD, (921, 282))
        self._text("生长轮次", self.fonts["small"], TEXT_MUTED, (1045, 257))
        self._text(f"{state.generation:02d}", self.fonts["stat"], TEXT, (1045, 282))

        status_color = DANGER if state.last_rejected else CYAN
        if state.phase is PlantingPhase.WON:
            status_color = BUD
        elif state.phase is PlantingPhase.LOST:
            status_color = DANGER
        self._text(self.message, self.fonts["body"], status_color, (686, 366))
        self._text("种植行动", self.fonts["h2"], TEXT, (686, 412))
        if state.phase is PlantingPhase.PLANTING:
            self._text("点击相邻土格移动，按 P 或点击“播种”种下花种。", self.fonts["body"], TEXT_MUTED, (686, 452))
            self._text("花种用完后按 SPACE / ENTER，或点击“开始”。", self.fonts["body"], TEXT_MUTED, (686, 480))
            labels = ("播种", "撤回", "开始", "重置", "返回")
        elif state.phase is PlantingPhase.GROWING:
            playback = "自动播放中" if self.planting_autoplay else "播放已暂停"
            self._text(f"{playback}；目标：{puzzle.pattern.behavior}", self.fonts["body"], TEXT_MUTED, (686, 452))
            self._text("可暂停观察，或单步推进验证过程。", self.fonts["body"], TEXT_MUTED, (686, 480))
            labels = ("暂停" if self.planting_autoplay else "播放", "单步", "", "重置", "返回")
        elif state.phase is PlantingPhase.WON:
            playback = "演示循环中" if self.planting_autoplay else "演示已暂停"
            self._text(f"{playback}；已验证：{puzzle.pattern.behavior}", self.fonts["body"], TEXT_MUTED, (686, 452))
            self._text("循环为安全片段回看，不改变成谱判定。", self.fonts["body"], TEXT_MUTED, (686, 480))
            labels = ("暂停" if self.planting_autoplay else "播放", "重播", "", "重置", "返回")
        else:
            self._text("验证结束，可以重新播种或返回花谱。", self.fonts["body"], TEXT_MUTED, (686, 452))
            labels = ("", "", "", "重置", "返回")
        for index, label in enumerate(labels):
            rect = pygame.Rect(686 + index * 99, 570, 90, 40)
            self._rounded_panel(rect, active=False)
            if label:
                self._text(label, self.fonts["body"], CYAN if index in (0, 2) else TEXT_MUTED, (rect.x + 26, rect.y + 12))

        if state.phase is PlantingPhase.LOST:
            self._draw_planting_result_overlay(frame, state.phase)

    def _draw_planting_board(self, board: pygame.Rect, tile: int) -> None:
        assert self.planting_state is not None
        state = self.planting_state
        puzzle = state.puzzle
        visible_blooms = (
            self.planting_showcase_frames[self.planting_showcase_index]
            if state.phase is PlantingPhase.WON and self.planting_showcase_frames
            else state.blooms
        )
        for y in range(puzzle.height):
            for x in range(puzzle.width):
                point = (x, y)
                rect = pygame.Rect(board.x + x * tile, board.y + y * tile, tile - 1, tile - 1)
                pygame.draw.rect(self.screen, SOIL, rect, border_radius=7)
                pygame.draw.rect(self.screen, SOIL_EDGE, rect, width=1, border_radius=7)
                if point in puzzle.expected_blooms:
                    pygame.draw.rect(self.screen, (126, 105, 58), rect.inflate(-8, -8), width=1, border_radius=5)
                if point in visible_blooms:
                    self._draw_bud(rect, False, point in self.bloomed)
                elif point in self.faded and self.flash_timer > 0:
                    pygame.draw.circle(self.screen, (74, 111, 87), rect.center, max(3, tile // 6))

        if state.phase is PlantingPhase.PLANTING:
            player_rect = self._tile_rect(board, tile, state.player)
            if state.player in state.planted:
                pygame.draw.rect(
                    self.screen,
                    GOLD,
                    player_rect.inflate(-5, -5),
                    width=3,
                    border_radius=9,
                )
                pygame.draw.circle(
                    self.screen,
                    LANTERN_CORE,
                    (player_rect.right - 12, player_rect.top + 12),
                    max(4, tile // 10),
                )
            else:
                self._draw_bud(player_rect, True, False)

    def _draw_board(self, board: pygame.Rect, tile: int) -> None:
        assert self.state is not None
        state = self.state
        for y in range(state.puzzle.height):
            for x in range(state.puzzle.width):
                rect = pygame.Rect(board.x + x * tile, board.y + y * tile, tile - 1, tile - 1)
                pygame.draw.rect(self.screen, SOIL, rect, border_radius=7)
                pygame.draw.rect(self.screen, SOIL_EDGE, rect, width=1, border_radius=7)
                if (x, y) in state.blooms:
                    self._draw_bud(rect, False, (x, y) in self.bloomed)
                elif (x, y) in self.faded and self.flash_timer > 0:
                    ghost = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    alpha = int(90 * self.flash_timer / 0.34)
                    center = ghost.get_rect().center
                    pygame.draw.circle(ghost, (*BUD, alpha), center, max(3, tile // 4))
                    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                        petal = (center[0] + dx * tile // 5, center[1] + dy * tile // 5)
                        pygame.draw.circle(ghost, (*BUD, alpha // 2), petal, max(2, tile // 7))
                    self.screen.blit(ghost, rect.topleft)

        player_rect = pygame.Rect(
            board.x + state.player[0] * tile,
            board.y + state.player[1] * tile,
            tile - 1,
            tile - 1,
        )
        self._draw_bud(player_rect, True, False)

    def _draw_tutorial_marks(self, board: pygame.Rect, tile: int, step: TutorialStep) -> None:
        if step.focus is not None:
            focus_rect = self._tile_rect(board, tile, step.focus)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    point = (step.focus[0] + dx, step.focus[1] + dy)
                    if 0 <= point[0] < step.puzzle.width and 0 <= point[1] < step.puzzle.height:
                        neighbor_rect = self._tile_rect(board, tile, point)
                        pygame.draw.rect(
                            self.screen, (31, 76, 78), neighbor_rect, width=1, border_radius=6
                        )
            focus_color = GOLD
            if self.tutorial_resolved and step.focus in self.bloomed:
                focus_color = BUD
            elif self.tutorial_resolved and step.focus in self.faded:
                focus_color = DANGER
            pygame.draw.rect(self.screen, focus_color, focus_rect, width=3, border_radius=7)

        if step.move_target is not None and not self.tutorial_resolved:
            target_rect = self._tile_rect(board, tile, step.move_target)
            pygame.draw.rect(self.screen, LANTERN_CORE, target_rect, width=3, border_radius=7)
            self._text(
                "MOVE", self.fonts["small"], LANTERN_CORE, (target_rect.x + 6, target_rect.y + 20)
            )

    @staticmethod
    def _tile_rect(board: pygame.Rect, tile: int, point: tuple[int, int]) -> pygame.Rect:
        return pygame.Rect(
            board.x + point[0] * tile, board.y + point[1] * tile, tile - 1, tile - 1
        )

    def _tutorial_neighbor_count(self, point: tuple[int, int]) -> int:
        assert self.state is not None
        effective = self.state.blooms | {self.state.player}
        x, y = point
        return sum(
            (x + dx, y + dy) in effective
            for dy in (-1, 0, 1)
            for dx in (-1, 0, 1)
            if dx != 0 or dy != 0
        )

    def _draw_bud(self, rect: pygame.Rect, player: bool, newly_bloomed: bool) -> None:
        pulse = 0.5 + 0.5 * math.sin(self.elapsed * (4.2 if player else 2.2))
        radius = max(4, rect.width // 4 + (1 if player and pulse > 0.55 else 0))
        glow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        color = LANTERN if player else BUD
        if newly_bloomed and self.flash_timer > 0:
            color = BUD_CORE
        center = (rect.width // 2, rect.height // 2)
        pygame.draw.circle(glow, (*color, 42 if player else 30), center, radius + 9)
        self.screen.blit(glow, rect.topleft)
        if player:
            pygame.draw.circle(self.screen, LANTERN, rect.center, radius + 2)
            pygame.draw.circle(self.screen, LANTERN_CORE, rect.center, max(3, radius // 2))
            pygame.draw.circle(self.screen, LANTERN_CORE, rect.center, radius + 5, width=1)
        else:
            petal_radius = max(3, radius * 2 // 3)
            petal_distance = max(3, radius)
            for angle in range(0, 360, 72):
                radians = math.radians(angle - 90)
                petal_center = (
                    rect.centerx + int(math.cos(radians) * petal_distance),
                    rect.centery + int(math.sin(radians) * petal_distance),
                )
                pygame.draw.circle(self.screen, color, petal_center, petal_radius)
            pygame.draw.circle(self.screen, BUD_CORE, rect.center, max(2, radius // 2))

    def _draw_result_overlay(self, frame: pygame.Rect, phase: Phase) -> None:
        veil = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
        veil.fill((3, 8, 11, 190))
        self.screen.blit(veil, frame.topleft)
        succeeded = phase is Phase.WON
        label = "花园盛放" if succeeded else "月夜散场"
        color = BUD if succeeded else DANGER
        text = self.fonts["result"].render(label, True, color)
        self.screen.blit(text, text.get_rect(center=(frame.centerx, frame.centery - 25)))
        hint = self.fonts["body"].render("ENTER / R 重试谜题    ESC 返回引导选择", True, TEXT)
        self.screen.blit(hint, hint.get_rect(center=(frame.centerx, frame.centery + 48)))

    def _draw_planting_result_overlay(self, frame: pygame.Rect, phase: PlantingPhase) -> None:
        veil = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
        veil.fill((3, 8, 11, 190))
        self.screen.blit(veil, frame.topleft)
        succeeded = phase is PlantingPhase.WON
        label = "花谱盛放" if succeeded else "花谱未成"
        color = BUD if succeeded else DANGER
        text = self.fonts["result"].render(label, True, color)
        self.screen.blit(text, text.get_rect(center=(frame.centerx, frame.centery - 25)))
        hint = self.fonts["body"].render("ENTER / R 重新播种    ESC 返回花谱选择", True, TEXT)
        self.screen.blit(hint, hint.get_rect(center=(frame.centerx, frame.centery + 48)))

    def _rounded_panel(self, rect: pygame.Rect, active: bool) -> None:
        pygame.draw.rect(self.screen, PANEL_LIGHT if active else PANEL, rect, border_radius=12)
        border = CYAN if active else (25, 53, 58)
        pygame.draw.rect(self.screen, border, rect, width=1, border_radius=12)

    def _stat_line(self, name: str, value: str, y: int) -> None:
        self._text(name, self.fonts["body"], TEXT_MUTED, (802, y))
        self._text(value, self.fonts["h2"], TEXT, (1032, y - 3))

    def _stat_line_at(self, name: str, value: str, x: int, y: int) -> None:
        self._text(name, self.fonts["body"], TEXT_MUTED, (x, y))
        self._text(value, self.fonts["h2"], TEXT, (x + 106, y - 3))

    def _text(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        position: tuple[int, int],
    ) -> None:
        self.screen.blit(font.render(text, True, color), position)


def run() -> None:
    LumenGardenApp().run()
