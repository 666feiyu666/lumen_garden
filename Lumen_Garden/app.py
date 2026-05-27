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
MENU_BACKGROUND_PATH = "sprites/menu.png"
GUIDE_MENU_BACKGROUND_PATH = "sprites/guide_menu.png"
GUIDE_PUZZLE_BACKGROUND_PATH = "sprites/guide_puzzle.png"
PLANT_MENU_BACKGROUND_PATH = "sprites/plant_menu.png"
PLANT_PUZZLE_BACKGROUND_PATH = "sprites/plant_puzzle.png"
PUZZLE_BOARD_PATH = "sprites/puzzle_board.png"
PUZZLE_BOARD_SOURCE_SIZE = 500
PUZZLE_BOARD_X_CELLS = (
    (33, 70), (76, 114), (120, 157), (164, 201), (207, 245),
    (251, 289), (295, 333), (339, 376), (383, 420), (426, 464),
)
PUZZLE_BOARD_Y_CELLS = (
    (32, 68), (73, 109), (115, 150), (156, 192), (197, 234),
    (240, 275), (281, 317), (323, 359), (365, 400), (406, 441),
)
MENU_BUTTON_RECTS = tuple(pygame.Rect(819, 228 + index * 84, 342, 66) for index in range(3))
GARDEN_CARD_RECTS = (
    pygame.Rect(122, 133, 398, 62),
    pygame.Rect(122, 209, 398, 69),
    pygame.Rect(122, 289, 398, 65),
    pygame.Rect(122, 368, 398, 65),
    pygame.Rect(122, 448, 398, 65),
    pygame.Rect(122, 528, 398, 65),
)
GARDEN_BACK_RECT = pygame.Rect(194, 638, 222, 38)
PLANT_CARD_RECTS = (
    pygame.Rect(132, 138, 554, 81),
    pygame.Rect(132, 228, 554, 79),
    pygame.Rect(132, 317, 554, 78),
    pygame.Rect(132, 405, 554, 77),
    pygame.Rect(132, 493, 554, 77),
)
PLANT_MENU_BACK_RECT = pygame.Rect(1010, 648, 176, 38)
PUZZLE_TEXT_RECT = pygame.Rect(912, 151, 244, 462)
PUZZLE_PRIMARY_RECT = pygame.Rect(914, 521, 240, 42)
PUZZLE_RETRY_RECT = pygame.Rect(914, 575, 104, 32)
PUZZLE_BACK_RECT = pygame.Rect(1030, 575, 124, 32)
PLANT_CONTROL_RECTS = (
    pygame.Rect(912, 522, 75, 38),
    pygame.Rect(991, 522, 75, 38),
    pygame.Rect(1070, 522, 86, 38),
    pygame.Rect(912, 575, 116, 32),
    pygame.Rect(1040, 575, 116, 32),
)
LANGUAGE_BUTTON_RECTS = (
    pygame.Rect(551, 348, 128, 38),
    pygame.Rect(691, 348, 161, 38),
)
BOARD_SPRITES = {
    "flower": "sprites/flower_board.png",
    "lantern": "sprites/lantern_board_idle.png",
}
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
GUIDE_INK = (64, 52, 39)
GUIDE_INK_MUTED = (111, 93, 71)
GUIDE_ACCENT = (50, 103, 91)

PATTERN_BEHAVIOR_EN = {
    "BLOCK": "A four-bloom bed that remains still through every generation",
    "BLINKER": "A branch that returns to its pose every two generations",
    "BEACON": "Two flower stands that alternate every two generations",
    "GLIDER": "A seed-shape that travels diagonally after four generations",
    "LWSS": "A light vessel that travels right after four generations",
}
PATTERN_KIND_ZH = {
    "Still life": "静物",
    "Oscillator": "振荡器",
    "Spaceship": "移行体",
}
TUTORIAL_EN = (
    (
        "Meet the Lantern",
        ("You guide the golden lantern spirit through this garden.", "Green blooms evolve after each move or wait."),
        "Press ENTER to begin listening to the garden",
        "",
    ),
    (
        "A Lonely Bloom",
        ("Watch the central bloom without a companion light.", "A bloom with fewer than 2 neighbors fades away."),
        "Press SPACE to grow one generation",
        "Neighbors 0: the lonely bloom has faded.",
    ),
    (
        "Companion Light",
        ("Four blooms illuminate one another in a steady cluster.", "A bloom with 2 or 3 neighbors continues glowing."),
        "Press SPACE to check the stable shape",
        "Neighbors 3: the blooms remain steady.",
    ),
    (
        "A New Bloom",
        ("Exactly three blooms surround the highlighted soil.", "Empty soil with exactly 3 lights grows a new bloom."),
        "Press SPACE to watch a new bloom open",
        "Neighbors 3: a new bloom opens on the highlighted soil.",
    ),
    (
        "Lantern Guidance",
        ("The highlighted soil has only two nearby bloom lights.", "Move the lantern to the marked cell to add a third light."),
        "Press LEFT / A to move the lantern",
        "The lantern provides the third light: a new bloom opens.",
    ),
    (
        "Your First Puzzle",
        ("Act freely: end two generations with exactly 3 blooms.", "Hint: approach the blooms first, then wait."),
        "Arrow keys move; SPACE waits; press R to retry",
        "Blooming light: you now know how to guide the garden.",
    ),
)
REASON_EN = {
    "这则谜题已经结束": "This puzzle has already ended.",
    "灯灵不能走出花圃边界": "The lantern cannot leave the garden.",
    "落点已经有一枚花芽": "A bloom already occupies that cell.",
    "生长开始后，灯灵只能静静观看": "Once growth begins, the lantern can only watch.",
    "请移动灯灵，或在当前位置播种": "Move the lantern or plant at its current position.",
    "这里已经有一枚花芽，请改走相邻空土格": "A bloom is here; move to an adjacent empty cell.",
    "花谱已经开始生长": "This pattern has already begun growing.",
    "这格土地无法播种": "Seeds cannot be planted in this cell.",
    "这里已经有一枚花芽": "A bloom already occupies this cell.",
    "花种已经用完": "No seeds remain.",
    "还没有可以撤回的花种": "There is no placed seed to remove.",
    "请先确认开始生长": "Start growth before advancing.",
}


class LumenGardenApp:
    def __init__(self) -> None:
        pygame.init()
        # Gameplay has no text fields; do not let an IME capture letter hotkeys.
        pygame.key.stop_text_input()
        self.language = "zh"
        pygame.display.set_caption("萤光花园")
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
        self.tutorial_completed = False
        self.completed_puzzles: set[int] = set()
        self.completed_planting: set[int] = set()
        self.message = "选择一则月夜谜题"
        self.message_timer = 0.0
        self.flash_timer = 0.0
        self.bloomed: frozenset[tuple[int, int]] = frozenset()
        self.faded: frozenset[tuple[int, int]] = frozenset()
        self.elapsed = 0.0
        self.fonts = self._load_fonts()
        self.background = self._build_background()
        self.menu_background = self._load_menu_background(MENU_BACKGROUND_PATH) or self.background
        self.guide_menu_background = (
            self._load_menu_background(GUIDE_MENU_BACKGROUND_PATH) or self.background
        )
        self.guide_puzzle_background = (
            self._load_menu_background(GUIDE_PUZZLE_BACKGROUND_PATH) or self.background
        )
        self.plant_menu_background = (
            self._load_menu_background(PLANT_MENU_BACKGROUND_PATH) or self.background
        )
        self.plant_puzzle_background = (
            self._load_menu_background(PLANT_PUZZLE_BACKGROUND_PATH) or self.background
        )
        self.board_sprites = self._load_board_sprites()
        self.scaled_board_sprites: dict[tuple[str, tuple[int, int]], pygame.Surface] = {}
        self.puzzle_board = self._load_puzzle_board()
        self.scaled_puzzle_boards: dict[tuple[int, int], pygame.Surface] = {}
        self.audio = AudioManager(ASSET_ROOT)
        self.audio.play_music("menu")

    def _tr(self, zh: str, en: str) -> str:
        return zh if self.language == "zh" else en

    def _name(self, item: object) -> str:
        return item.name_cn if self.language == "zh" else item.name

    def _pattern_kind(self, kind: str) -> str:
        return PATTERN_KIND_ZH.get(kind, kind) if self.language == "zh" else kind

    def _behavior(self, pattern: object) -> str:
        if self.language == "zh":
            return pattern.behavior
        return PATTERN_BEHAVIOR_EN.get(pattern.key, pattern.behavior)

    def _tutorial_copy(self, step: TutorialStep) -> tuple[str, tuple[str, ...], str, str]:
        if self.language == "zh":
            return step.title, step.lines, step.instruction, step.result_text
        return TUTORIAL_EN[self.tutorial_step]

    def _reason(self, reason: str) -> str:
        if self.language == "zh":
            return reason
        if reason.startswith("还有 ") and " 枚花种未种下" in reason:
            count = reason.split()[1]
            return f"{count} seeds remain; plant them all before starting growth."
        return REASON_EN.get(reason, reason)

    def _set_language(self, language: str) -> None:
        self.language = language
        pygame.display.set_caption(self._tr("萤光花园", "Lumen Garden"))

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
    def _load_board_sprites() -> dict[str, pygame.Surface]:
        sprites: dict[str, pygame.Surface] = {}
        for name, relative_path in BOARD_SPRITES.items():
            path = ASSET_ROOT / relative_path
            if not path.exists():
                continue
            try:
                sprites[name] = pygame.image.load(str(path)).convert_alpha()
            except (OSError, pygame.error):
                continue
        return sprites

    @staticmethod
    def _load_puzzle_board() -> pygame.Surface | None:
        path = ASSET_ROOT / PUZZLE_BOARD_PATH
        if not path.exists():
            return None
        try:
            return pygame.image.load(str(path)).convert_alpha()
        except (OSError, pygame.error):
            return None

    @staticmethod
    def _load_menu_background(relative_path: str) -> pygame.Surface | None:
        path = ASSET_ROOT / relative_path
        if not path.exists():
            return None
        try:
            source = pygame.image.load(str(path)).convert()
        except (OSError, pygame.error):
            return None
        return pygame.transform.smoothscale(source, SCREEN_SIZE)

    def _scaled_board_sprite(
        self, name: str, size: tuple[int, int]
    ) -> pygame.Surface | None:
        sprite = self.board_sprites.get(name)
        if sprite is None:
            return None
        key = (name, size)
        if key not in self.scaled_board_sprites:
            self.scaled_board_sprites[key] = pygame.transform.smoothscale(sprite, size)
        return self.scaled_board_sprites[key]

    def _scaled_puzzle_board(self, size: tuple[int, int]) -> pygame.Surface | None:
        if self.puzzle_board is None:
            return None
        if size not in self.scaled_puzzle_boards:
            self.scaled_puzzle_boards[size] = pygame.transform.smoothscale(
                self.puzzle_board, size
            )
        return self.scaled_puzzle_boards[size]

    @staticmethod
    def _sprite_destination(sprite: pygame.Surface, cell: pygame.Rect) -> pygame.Rect:
        visible = sprite.get_bounding_rect(min_alpha=4)
        destination = sprite.get_rect()
        destination.x = cell.centerx - visible.centerx
        destination.y = cell.centery - visible.centery
        return destination

    def _garden_entry_completed(self, index: int) -> bool:
        return self.tutorial_completed if index == 0 else index - 1 in self.completed_puzzles

    def _garden_entry_unlocked(self, index: int) -> bool:
        return index == 0 or self._garden_entry_completed(index - 1)

    def _planting_entry_unlocked(self, index: int) -> bool:
        return index == 0 or index - 1 in self.completed_planting

    def _locked_message(self) -> str:
        return self._tr(
            "请先完成上一关，才可解锁这一关。",
            "Complete the previous level to unlock this one.",
        )

    def _reject_locked_level(self) -> None:
        self.message = self._locked_message()
        self.message_timer = 2.0
        self.audio.play("reject")

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
            for index, rect in enumerate(MENU_BUTTON_RECTS):
                if rect.collidepoint(point):
                    self.main_selection = index
                    (self._open_garden_menu, self._open_planting_menu, self._open_settings)[
                        index
                    ]()
                    return
        elif self.scene == "garden_menu":
            for index, rect in enumerate(GARDEN_CARD_RECTS):
                if rect.collidepoint(point):
                    self.menu_selection = index
                    self._start_tutorial() if index == 0 else self._start_puzzle(index - 1)
                    return
            if GARDEN_BACK_RECT.collidepoint(point):
                self.scene = "menu"
        elif self.scene == "planting_menu":
            for index, rect in enumerate(PLANT_CARD_RECTS):
                if rect.collidepoint(point):
                    self.planting_selection = index
                    self._start_planting(index)
                    return
            if PLANT_MENU_BACK_RECT.collidepoint(point):
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
        for language, rect in zip(("zh", "en"), LANGUAGE_BUTTON_RECTS):
            if rect.collidepoint(point):
                self._set_language(language)
                self.audio.play("select")
                return
        if pygame.Rect(420, 438, 52, 45).collidepoint(point):
            self.audio.set_volume(self.audio.volume - 0.1)
        elif pygame.Rect(658, 438, 52, 45).collidepoint(point):
            self.audio.set_volume(self.audio.volume + 0.1)
        elif pygame.Rect(732, 438, 120, 45).collidepoint(point):
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

    @staticmethod
    def _formal_tile_rect(board: pygame.Rect, point: tuple[int, int]) -> pygame.Rect:
        x_start, x_end = PUZZLE_BOARD_X_CELLS[point[0]]
        y_start, y_end = PUZZLE_BOARD_Y_CELLS[point[1]]
        left = board.x + round(x_start * board.width / PUZZLE_BOARD_SOURCE_SIZE)
        top = board.y + round(y_start * board.height / PUZZLE_BOARD_SOURCE_SIZE)
        right = board.x + round(x_end * board.width / PUZZLE_BOARD_SOURCE_SIZE)
        bottom = board.y + round(y_end * board.height / PUZZLE_BOARD_SOURCE_SIZE)
        return pygame.Rect(left, top, max(1, right - left), max(1, bottom - top))

    def _formal_grid_command(
        self, point: tuple[int, int], board: pygame.Rect, player: tuple[int, int]
    ) -> Command | None:
        if not board.collidepoint(point):
            return None
        clicked = next(
            (
                (x, y)
                for y in range(len(PUZZLE_BOARD_Y_CELLS))
                for x in range(len(PUZZLE_BOARD_X_CELLS))
                if self._formal_tile_rect(board, (x, y)).collidepoint(point)
            ),
            None,
        )
        if clicked is None:
            return None
        delta = (clicked[0] - player[0], clicked[1] - player[1])
        return {
            (0, 0): Command.WAIT,
            (0, -1): Command.UP,
            (0, 1): Command.DOWN,
            (-1, 0): Command.LEFT,
            (1, 0): Command.RIGHT,
        }.get(delta)

    def _game_click(self, point: tuple[int, int]) -> None:
        assert self.state is not None
        puzzle = self.state.puzzle
        board, tile = self._formal_board_layout(puzzle.width, puzzle.height)
        command = self._formal_grid_command(point, board, self.state.player)
        if command is not None and self.state.phase is Phase.ACTIVE:
            self._issue(command)
        elif PUZZLE_PRIMARY_RECT.collidepoint(point):
            self._issue(Command.WAIT)
        elif PUZZLE_RETRY_RECT.collidepoint(point):
            self._start_puzzle(self.selected_puzzle)
        elif PUZZLE_BACK_RECT.collidepoint(point):
            self.scene = "garden_menu"
            self.state = None
            self.audio.play_music("menu")

    def _planting_click(self, point: tuple[int, int]) -> None:
        assert self.planting_state is not None
        state = self.planting_state
        puzzle = state.puzzle
        board, tile = self._formal_board_layout(puzzle.width, puzzle.height)
        if state.phase is PlantingPhase.PLANTING:
            command = self._formal_grid_command(point, board, state.player)
            if command is Command.WAIT:
                self.message = (
                    self._tr(
                        f"当前位置可按 P 播种；还剩 {state.seeds_left} 枚花种",
                        f"Press P to plant here; {state.seeds_left} seeds remain.",
                    )
                    if state.seeds_left > 0
                    else self._tr(
                        "花种已全部播下，请按 SPACE 或 ENTER 开始生长",
                        "All seeds are planted; press SPACE or ENTER to begin growth.",
                    )
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
        if PLANT_CONTROL_RECTS[0].collidepoint(point):
            self._planting_key(
                pygame.K_p if state.phase is PlantingPhase.PLANTING else pygame.K_SPACE
            )
        elif PLANT_CONTROL_RECTS[1].collidepoint(point) and state.phase is PlantingPhase.PLANTING:
            self._planting_key(pygame.K_x)
        elif PLANT_CONTROL_RECTS[1].collidepoint(point) and state.phase in (
            PlantingPhase.GROWING,
            PlantingPhase.WON,
        ):
            self._planting_key(pygame.K_RETURN)
        elif PLANT_CONTROL_RECTS[2].collidepoint(point) and state.phase is PlantingPhase.PLANTING:
            self._planting_key(pygame.K_RETURN)
        elif PLANT_CONTROL_RECTS[3].collidepoint(point):
            self._planting_key(pygame.K_r)
        elif PLANT_CONTROL_RECTS[4].collidepoint(point):
            self.scene = "planting_menu"
            self.planting_state = None
            self.audio.play_music("menu")

    def _tutorial_click(self, point: tuple[int, int]) -> None:
        if self.tutorial_step >= len(TUTORIAL_STEPS):
            if PUZZLE_PRIMARY_RECT.collidepoint(point):
                self._start_puzzle(0)
            elif PUZZLE_RETRY_RECT.collidepoint(point):
                self._start_tutorial()
            elif PUZZLE_BACK_RECT.collidepoint(point):
                self.scene = "garden_menu"
                self.state = None
                self.audio.play_music("menu")
            return
        if PUZZLE_PRIMARY_RECT.collidepoint(point):
            self._tutorial_key(pygame.K_RETURN)
        elif PUZZLE_RETRY_RECT.collidepoint(point):
            self._tutorial_key(pygame.K_r)
        elif PUZZLE_BACK_RECT.collidepoint(point):
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
        if not self._garden_entry_unlocked(index + 1):
            self._reject_locked_level()
            return
        self.selected_puzzle = index
        self.menu_selection = index + 1
        self.planting_state = None
        self.state = GameState(PUZZLES[index])
        self.scene = "game"
        self.message = self._tr(
            "谜题开始：带领金色灯灵走入花圃",
            "Puzzle begins: guide the golden lantern into the garden.",
        )
        self.message_timer = 2.4
        self.flash_timer = 0.0
        self.bloomed = frozenset()
        self.faded = frozenset()
        self.audio.play("select")
        self.audio.play_music("puzzle")

    def _start_planting(self, index: int) -> None:
        if not self._planting_entry_unlocked(index):
            self._reject_locked_level()
            return
        self.selected_planting = index
        self.menu_selection = len(PUZZLES) + 1 + index
        self.state = None
        self.planting_state = PlantingState(PLANTING_PUZZLES[index])
        self.planting_autoplay = False
        self.planting_playback_timer = 0.0
        self.planting_showcase_frames = []
        self.planting_showcase_index = 0
        self.scene = "planting"
        self.message = self._tr(
            "移动灯灵到缺失位置，按 P 播种，花种用完后开始生长",
            "Move to each missing cell and press P; begin growth after planting all seeds.",
        )
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
            self.message = self._tutorial_copy(step)[2]
        else:
            self.tutorial_completed = True
            self.state = None
            self.message = self._tr("月夜入门完成", "Moonlit tutorial complete")
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
                self.message = self._tutorial_copy(step)[2]
            return

        command = self._command_for_key(key)
        if command is None:
            return
        if not step.allowed_commands:
            self.message = self._tr(
                "按 ENTER 进入第一段花园指引",
                "Press ENTER to begin the first garden lesson.",
            )
            return
        if command not in step.allowed_commands:
            self.message = self._tr(
                f"本步骤请执行：{step.instruction}",
                f"For this step: {self._tutorial_copy(step)[2]}",
            )
            self.audio.play("reject")
            return
        if self.tutorial_resolved:
            self.message = self._tr(
                "按 ENTER 进入下一段指引",
                "Press ENTER for the next lesson.",
            )
            return
        self._issue_tutorial(step, command)

    def _issue_tutorial(self, step: TutorialStep, command: Command) -> None:
        assert self.state is not None
        report = self.state.issue(command)
        if not report.accepted:
            self.message = self._reason(report.reason)
            self.audio.play("reject")
            return

        self.bloomed = report.bloomed
        self.faded = report.faded
        self.flash_timer = 0.7
        self.audio.play("wait" if command is Command.WAIT else "move")
        if step.quiz:
            if self.state.phase is Phase.WON:
                self.tutorial_resolved = True
                self.message = self._tutorial_copy(step)[3]
                self.audio.play("win")
            elif self.state.phase is Phase.LOST:
                self.message = self._tr(
                    "花芽数量还不合适，按 R 重试这则小谜题",
                    "The bloom count is not right yet; press R to retry.",
                )
                self.audio.play("lose")
            else:
                self.message = self._tr(
                    "还剩一轮生长：让最终盛开的花芽达到 3",
                    "One generation remains: finish with exactly 3 blooms.",
                )
        else:
            self.tutorial_resolved = True
            self.message = self._tutorial_copy(step)[3]

    def _issue(self, command: Command) -> None:
        assert self.state is not None
        previous_phase = self.state.phase
        report = self.state.issue(command)
        if not report.accepted:
            self.message = self._reason(report.reason)
            self.message_timer = 1.1
            self.audio.play("reject")
            return

        self.bloomed = report.bloomed
        self.faded = report.faded
        self.flash_timer = 0.34
        self.message = self._tr("花园生长了一轮", "The garden grows by one generation.")
        self.message_timer = 0.55
        self.audio.play("wait" if command is Command.WAIT else "move")
        if previous_phase is Phase.ACTIVE and self.state.phase is Phase.WON:
            self.completed_puzzles.add(self.selected_puzzle)
            self.message = self._tr("花光恰好：谜题解开", "Bloom count matched: puzzle solved.")
            self.message_timer = 99.0
            self.audio.play("win")
            self.audio.play_music("puzzle")
        elif previous_phase is Phase.ACTIVE and self.state.phase is Phase.LOST:
            self.message = self._tr("月夜已尽：花芽未能成景", "Dawn arrives before the garden is solved.")
            self.message_timer = 99.0
            self.audio.play("lose")
            self.audio.play_music("puzzle")

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
                    self._tr(
                        "成谱演示继续循环；按 SPACE 暂停",
                        "Pattern replay continues; press SPACE to pause.",
                    )
                    if self.planting_autoplay
                    else self._tr(
                        "成谱演示已暂停；按 ENTER 从开头重播",
                        "Pattern replay paused; press ENTER to restart.",
                    )
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
                    self._tr(
                        "花种已全部播下，按 SPACE 或 ENTER 开始生长",
                        "All seeds planted; press SPACE or ENTER to begin growth.",
                    )
                    if state.seeds_left == 0
                    else self._tr(
                        "一枚花种落入土壤，继续按 P 播种",
                        "A seed takes root; press P again to keep planting.",
                    )
                )
                sound = "move"
            elif key in (pygame.K_BACKSPACE, pygame.K_x):
                report = state.remove_seed()
                accepted_message = self._tr(
                    "收回一枚花种，可以重新选择位置",
                    "Seed removed; choose a new cell.",
                )
                sound = "wait"
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                report = state.start_growth()
                accepted_message = self._tr(
                    "花圃开始自行生长；按 SPACE 可暂停播放",
                    "The garden begins growing; press SPACE to pause playback.",
                )
                sound = "wait"
            else:
                command = self._command_for_key(key)
                if command is None or command is Command.WAIT:
                    return
                report = state.move(command)
                accepted_message = self._tr(
                    "选择土格后按 P 播种",
                    "Choose a soil cell, then press P to plant.",
                )
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
                    self._tr(
                        "花谱继续自行生长；按 SPACE 暂停",
                        "Pattern growth continues; press SPACE to pause.",
                    )
                    if self.planting_autoplay
                    else self._tr(
                        "花谱已暂停；按 ENTER 单步查看",
                        "Pattern paused; press ENTER to advance one step.",
                    )
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
            self.message = self._reason(report.reason)
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
        self.message = self._tr(
            f"花谱自行生长至第 {state.generation} 代",
            f"Pattern grows to generation {state.generation}.",
        )
        self.message_timer = 99.0
        self.audio.play("wait")
        if state.phase is PlantingPhase.WON:
            self.completed_planting.add(self.selected_planting)
            self.planting_autoplay = True
            self.planting_playback_timer = 0.0
            self.message = self._tr(
                f"{state.puzzle.name_cn}成谱：{state.puzzle.pattern.behavior}；正在循环回看",
                f"{state.puzzle.name} complete: {self._behavior(state.puzzle.pattern)}. Replaying.",
            )
            self.audio.play("win")
            self.audio.play_music("puzzle")
        elif state.phase is PlantingPhase.LOST:
            self.planting_autoplay = False
            self.message = self._tr(
                f"{state.puzzle.name_cn}未达到目标行为，按 R 重新播种",
                f"{state.puzzle.name} did not match the target; press R to replant.",
            )
            self.audio.play("lose")
            self.audio.play_music("puzzle")

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
        self.message = self._tr(
            "从起始花形重播成谱演示；按 SPACE 暂停",
            "Replaying the completed pattern from its start; press SPACE to pause.",
        )
        self.message_timer = 99.0
        self.audio.play("select")

    def _draw(self) -> None:
        if self.scene == "menu":
            background = self.menu_background
        elif self.scene == "garden_menu":
            background = self.guide_menu_background
        elif self.scene == "planting_menu":
            background = self.plant_menu_background
        elif self.scene in ("tutorial", "game"):
            background = self.guide_puzzle_background
        elif self.scene == "planting":
            background = self.plant_puzzle_background
        else:
            background = self.background
        self.screen.blit(background, (0, 0))
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
        self._text(self._tr("萤光花园", "LUMEN GARDEN"), self.fonts["title"], TEXT, (74, 92))
        self._text(
            self._tr("微光盛放之谜", "A PUZZLE OF BLOOMING LIGHT"),
            self.fonts["subtitle"],
            CYAN,
            (80, 174),
        )
        labels = (
            (self._tr("花园谜题", "GARDEN PUZZLES"), self._tr("引导灯灵，照料生长", "Guide the lantern")),
            (self._tr("种植花谱", "PLANTING PATTERNS"), self._tr("播下花种，观察演化", "Plant and observe")),
            (self._tr("设置", "SETTINGS"), self._tr("画面、声音与语言", "Display, audio, language")),
        )
        for index, (label, detail) in enumerate(labels):
            rect = MENU_BUTTON_RECTS[index]
            selected = index == self.main_selection
            if selected:
                highlight = pygame.Surface(rect.size, pygame.SRCALPHA)
                highlight.fill((176, 128, 54, 42))
                self.screen.blit(highlight, rect.topleft)
            pygame.draw.rect(
                self.screen,
                GOLD if selected else (125, 94, 57),
                rect,
                width=2 if selected else 1,
                border_radius=8,
            )
            accent = TEXT if selected else (222, 199, 154)
            self._text(label, self.fonts["h2"], accent, (rect.x + 22, rect.y + 11))
            self._text(detail, self.fonts["small"], TEXT_MUTED, (rect.x + 153, rect.y + 25))
        self._text(
            self._tr("↑ ↓ / ENTER 选择    ESC 退出", "UP / DOWN / ENTER Select    ESC Quit"),
            self.fonts["small"],
            (211, 192, 153),
            (840, 510),
        )

    def _draw_garden_menu(self) -> None:
        self._text(self._tr("花园谜题", "GARDEN PUZZLES"), self.fonts["title"], TEXT, (76, 48))
        menu_puzzles = (TUTORIAL_CARD, *PUZZLES)
        for index, puzzle in enumerate(menu_puzzles):
            rect = GARDEN_CARD_RECTS[index]
            selected = index == self.menu_selection
            unlocked = self._garden_entry_unlocked(index)
            color = GUIDE_ACCENT if selected and unlocked else GUIDE_INK if unlocked else GUIDE_INK_MUTED
            number_color = GUIDE_ACCENT if selected and unlocked else GUIDE_INK_MUTED
            text_y = rect.centery - 12
            self._text(f"{puzzle.number:02d}", self.fonts["h2"], number_color, (rect.x + 21, text_y))
            self._text(self._name(puzzle), self.fonts["h2"], color, (rect.x + 87, text_y))
            if not unlocked:
                status = self._tr("未解锁", "LOCKED")
            elif self._garden_entry_completed(index):
                status = self._tr("已完成", "DONE")
            else:
                status = self._tr("进入", "OPEN")
            self._text(status, self.fonts["small"], color, (rect.right - 77, rect.centery - 8))

        self._text(
            self._tr("ENTER 开始    ESC 返回", "ENTER START    ESC BACK"),
            self.fonts["small"],
            TEXT_MUTED,
            (226, 619),
        )
        pygame.draw.rect(self.screen, (98, 129, 119), GARDEN_BACK_RECT, width=1, border_radius=8)
        self._text(
            self._tr("返回主菜单", "BACK TO MENU"),
            self.fonts["small"],
            TEXT,
            (GARDEN_BACK_RECT.x + 66, GARDEN_BACK_RECT.y + 11),
        )

    def _draw_planting_menu(self) -> None:
        for index, puzzle in enumerate(PLANTING_PUZZLES):
            rect = PLANT_CARD_RECTS[index]
            selected = index == self.planting_selection
            unlocked = self._planting_entry_unlocked(index)
            color = GOLD if selected and unlocked else GUIDE_INK if unlocked else GUIDE_INK_MUTED
            number_color = GOLD if selected and unlocked else GUIDE_INK_MUTED
            text_y = rect.centery - 12
            self._text(f"P{puzzle.number:02d}", self.fonts["h2"], number_color, (rect.x + 36, text_y))
            self._text(self._name(puzzle), self.fonts["h2"], color, (rect.x + 150, text_y))
            if not unlocked:
                status = self._tr("未解锁", "LOCKED")
            elif index in self.completed_planting:
                status = self._tr("已完成", "DONE")
            else:
                status = self._tr("进入", "OPEN")
            self._text(status, self.fonts["small"], color, (rect.right - 85, rect.centery - 8))

        pygame.draw.rect(self.screen, (98, 129, 119), PLANT_MENU_BACK_RECT, width=1, border_radius=8)
        self._text(
            self._tr("返回主菜单", "BACK TO MENU"),
            self.fonts["small"],
            TEXT,
            (PLANT_MENU_BACK_RECT.x + 43, PLANT_MENU_BACK_RECT.y + 11),
        )

    def _draw_settings(self) -> None:
        veil = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        veil.fill((5, 8, 14, 170))
        self.screen.blit(veil, (0, 0))
        panel = pygame.Rect(378, 142, 524, 446)
        self._rounded_panel(panel, active=False)
        self._text(self._tr("设置", "SETTINGS"), self.fonts["h1"], TEXT, (420, 183))
        self._text(self._tr("窗口大小", "WINDOW SIZE"), self.fonts["body"], TEXT_MUTED, (420, 246))
        for index, size in enumerate(WINDOW_SIZES):
            rect = pygame.Rect(420 + index * 144, 282, 128, 45)
            self._rounded_panel(rect, active=size == self.window_size)
            self._text(f"{size[0]} x {size[1]}", self.fonts["small"], TEXT, (rect.x + 13, rect.y + 14))
        self._text(self._tr("语言", "LANGUAGE"), self.fonts["body"], TEXT_MUTED, (420, 357))
        for language, rect, label in zip(("zh", "en"), LANGUAGE_BUTTON_RECTS, ("简体中文", "English")):
            self._rounded_panel(rect, active=self.language == language)
            self._text(label, self.fonts["small"], TEXT, (rect.x + 20, rect.y + 11))
        self._text(self._tr("音量", "VOLUME"), self.fonts["body"], TEXT_MUTED, (420, 410))
        for rect, label in (
            (pygame.Rect(420, 438, 52, 45), "-"),
            (pygame.Rect(658, 438, 52, 45), "+"),
        ):
            self._rounded_panel(rect, active=False)
            self._text(label, self.fonts["h2"], TEXT, (rect.x + 19, rect.y + 10))
        self._text(f"{int(self.audio.volume * 100):03d}%", self.fonts["stat"], TEXT, (526, 445))
        mute = pygame.Rect(732, 438, 120, 45)
        self._rounded_panel(mute, active=not self.audio.enabled)
        self._text(
            self._tr("静音" if self.audio.enabled else "已静音", "MUTE" if self.audio.enabled else "MUTED"),
            self.fonts["body"], TEXT, (mute.x + 29, mute.y + 13)
        )
        close = pygame.Rect(420, 514, 432, 44)
        self._rounded_panel(close, active=True)
        self._text(self._tr("关闭设置", "CLOSE SETTINGS"), self.fonts["h2"], CYAN, (562, 525))

    def _draw_tutorial(self) -> None:
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

        text_x = PUZZLE_TEXT_RECT.x
        text_width = PUZZLE_TEXT_RECT.width
        title, lines, _, _ = self._tutorial_copy(step)
        self._text(
            self._tr(
                f"月夜指引  {self.tutorial_step + 1:02d} / {len(TUTORIAL_STEPS):02d}",
                f"GUIDE  {self.tutorial_step + 1:02d} / {len(TUTORIAL_STEPS):02d}",
            ),
            self.fonts["small"],
            CYAN,
            (text_x, 160),
        )
        self._text(title, self.fonts["h1"], TEXT, (text_x, 193))
        body_y = 242
        for line in lines:
            body_y = self._draw_wrapped_text(
                line, self.fonts["small"], TEXT_MUTED, pygame.Rect(text_x, body_y, text_width, 80), 25
            ) + 5

        if step.quiz:
            self._text(self._tr("花芽 / 目标 / 夜步", "BLOOMS / GOAL / MOVES"), self.fonts["small"], TEXT_MUTED, (text_x, 365))
            self._text(
                f"{self.state.bloom_count:02d}  /  {step.puzzle.target_label}  /  {self.state.turns_left:02d}",
                self.fonts["h2"],
                BUD,
                (text_x, 392),
            )
        elif step.focus is not None:
            count = self._tutorial_neighbor_count(step.focus)
            self._text(self._tr("观察格伙伴数", "NEIGHBORS"), self.fonts["small"], TEXT_MUTED, (text_x, 365))
            self._text(f"{count:02d}", self.fonts["h2"], CYAN, (text_x, 392))

        message_color = BUD if self.tutorial_resolved else CYAN
        if step.quiz and self.state.phase is Phase.LOST:
            message_color = DANGER
        self._draw_wrapped_text(
            self.message,
            self.fonts["small"],
            message_color,
            pygame.Rect(text_x, 448, text_width, 58),
            23,
        )
        action = (
            self._tr("ENTER  下一步", "ENTER  NEXT")
            if self.tutorial_resolved
            else self._tr("按提示操作", "FOLLOW THE PROMPT")
        )
        self._draw_tutorial_button(PUZZLE_PRIMARY_RECT, action, CYAN)
        self._draw_tutorial_button(PUZZLE_RETRY_RECT, self._tr("R 重试", "R RETRY"), TEXT_MUTED)
        self._draw_tutorial_button(PUZZLE_BACK_RECT, self._tr("ESC 返回", "ESC BACK"), TEXT_MUTED)

    def _draw_tutorial_complete(self) -> None:
        text_x = PUZZLE_TEXT_RECT.x
        text_width = PUZZLE_TEXT_RECT.width
        self._text(self._tr("月夜指引  完成", "GUIDE  COMPLETE"), self.fonts["small"], CYAN, (text_x, 160))
        self._text(self._tr("入门完成", "COMPLETE"), self.fonts["h1"], BUD, (text_x, 193))
        self._draw_wrapped_text(
            self._tr(
                "你已经看过花芽熄灭、相伴盛开与灯灵引路。",
                "You have learned fading, blooming, and lantern guidance.",
            ),
            self.fonts["small"],
            TEXT,
            pygame.Rect(text_x, 252, text_width, 84),
            25,
        )
        self._draw_wrapped_text(
            self._tr(
                "现在去解开第一则花园谜题。",
                "Now begin the first garden puzzle.",
            ),
            self.fonts["small"],
            TEXT_MUTED,
            pygame.Rect(text_x, 354, text_width, 58),
            25,
        )
        self._draw_tutorial_button(
            PUZZLE_PRIMARY_RECT, self._tr("ENTER  开始初光", "ENTER  START AWAKEN"), CYAN
        )
        self._draw_tutorial_button(PUZZLE_RETRY_RECT, self._tr("R 重温", "R REPLAY"), TEXT_MUTED)
        self._draw_tutorial_button(PUZZLE_BACK_RECT, self._tr("ESC 返回", "ESC BACK"), TEXT_MUTED)

    def _draw_game(self) -> None:
        assert self.state is not None
        state = self.state
        puzzle = state.puzzle

        board_rect, tile = self._formal_board_layout(puzzle.width, puzzle.height)
        frame = board_rect.inflate(30, 30)
        self._draw_board(board_rect, tile)

        text_x = PUZZLE_TEXT_RECT.x
        text_width = PUZZLE_TEXT_RECT.width
        self._text(
            self._tr(
                f"花园谜题  {puzzle.number:02d} / {len(PUZZLES):02d}",
                f"PUZZLE  {puzzle.number:02d} / {len(PUZZLES):02d}",
            ),
            self.fonts["small"],
            CYAN,
            (text_x, 160),
        )
        self._text(self._name(puzzle), self.fonts["h1"], TEXT, (text_x, 193))
        self._text(self._tr("盛放目标", "BLOOM GOAL"), self.fonts["small"], TEXT_MUTED, (text_x, 251))
        self._text(
            self._tr(f"{puzzle.target_label} 枚花芽", f"{puzzle.target_label} BLOOMS"),
            self.fonts["h2"],
            GOLD,
            (text_x, 277),
        )
        self._text(self._tr("通关条件", "CONDITION"), self.fonts["small"], TEXT_MUTED, (text_x, 320))
        self._draw_wrapped_text(
            self._tr(
                f"在 {puzzle.turns} 轮生长结束时达成目标",
                f"Reach the goal after {puzzle.turns} growth turns.",
            ),
            self.fonts["small"],
            TEXT,
            pygame.Rect(text_x, 345, text_width, 52),
            22,
        )
        self._text(self._tr("当前花芽 / 剩余夜步", "BLOOMS / MOVES LEFT"), self.fonts["small"], TEXT_MUTED, (text_x, 406))
        self._text(
            f"{state.bloom_count:02d}  /  {state.turns_left:02d}",
            self.fonts["h2"],
            BUD,
            (text_x, 431),
        )

        status_color = DANGER if state.last_rejected else CYAN
        if state.phase is Phase.WON:
            status_color = BUD
        elif state.phase is Phase.LOST:
            status_color = DANGER
        self._draw_wrapped_text(
            self.message if self.message_timer > 0 else self._tr("等待灯灵前行", "Awaiting the lantern."),
            self.fonts["small"],
            status_color,
            pygame.Rect(text_x, 475, text_width, 42),
            21,
        )
        self._draw_tutorial_button(
            PUZZLE_PRIMARY_RECT, self._tr("停留并生长", "WAIT AND GROW"), CYAN
        )
        self._draw_tutorial_button(PUZZLE_RETRY_RECT, self._tr("R 重试", "R RETRY"), TEXT_MUTED)
        self._draw_tutorial_button(PUZZLE_BACK_RECT, self._tr("ESC 返回", "ESC BACK"), TEXT_MUTED)

        if state.phase is not Phase.ACTIVE:
            self._draw_result_overlay(frame, state.phase)

    def _draw_planting(self) -> None:
        assert self.planting_state is not None
        state = self.planting_state
        puzzle = state.puzzle

        board_rect, tile = self._formal_board_layout(puzzle.width, puzzle.height)
        frame = board_rect.inflate(30, 30)
        self._draw_planting_board(board_rect, tile)

        text_x = PUZZLE_TEXT_RECT.x
        text_width = PUZZLE_TEXT_RECT.width
        self._text(
            self._tr(
                f"种植花谱  P{puzzle.number:02d} / P{len(PLANTING_PUZZLES):02d}",
                f"PATTERN  P{puzzle.number:02d} / P{len(PLANTING_PUZZLES):02d}",
            ),
            self.fonts["small"],
            GOLD,
            (text_x, 160),
        )
        self._text(self._name(puzzle), self.fonts["h1"], TEXT, (text_x, 193))
        self._text(self._tr("目标行为", "TARGET BEHAVIOR"), self.fonts["small"], TEXT_MUTED, (text_x, 246))
        self._draw_wrapped_text(
            self._behavior(puzzle.pattern),
            self.fonts["small"],
            GOLD,
            pygame.Rect(text_x, 270, text_width, 48),
            22,
        )
        self._text(self._tr("验证条件", "CONDITION"), self.fonts["small"], TEXT_MUTED, (text_x, 324))
        self._draw_wrapped_text(
            self._tr(
                f"播下 {puzzle.seeds} 枚花种，观察 {puzzle.validation_generation} 代",
                f"Plant {puzzle.seeds} seeds; observe {puzzle.validation_generation} generations.",
            ),
            self.fonts["small"],
            TEXT,
            pygame.Rect(text_x, 347, text_width, 46),
            21,
        )

        phase_label = self._tr("播种", "PLANTING") if state.phase is PlantingPhase.PLANTING else self._tr("验证", "GROWING")
        if state.phase is PlantingPhase.WON:
            phase_label = self._tr("成谱", "COMPLETE")
        elif state.phase is PlantingPhase.LOST:
            phase_label = self._tr("失败", "FAILED")
        self._text(self._tr("阶段 / 花种 / 代数", "PHASE / SEEDS / GEN"), self.fonts["small"], TEXT_MUTED, (text_x, 401))
        self._text(
            f"{phase_label}  {state.seeds_left:02d}  /  {state.generation:02d}",
            self.fonts["small"],
            CYAN if state.phase is not PlantingPhase.LOST else DANGER,
            (text_x, 425),
        )

        status_color = DANGER if state.last_rejected else CYAN
        if state.phase is PlantingPhase.WON:
            status_color = BUD
        elif state.phase is PlantingPhase.LOST:
            status_color = DANGER
        self._draw_wrapped_text(
            self.message,
            self.fonts["small"],
            status_color,
            pygame.Rect(text_x, 460, text_width, 48),
            21,
        )

        if state.phase is PlantingPhase.PLANTING:
            labels = ("播种", "撤回", "开始", "重置", "返回")
        elif state.phase is PlantingPhase.GROWING:
            labels = ("暂停" if self.planting_autoplay else "播放", "单步", "", "重置", "返回")
        elif state.phase is PlantingPhase.WON:
            labels = ("暂停" if self.planting_autoplay else "播放", "重播", "", "重置", "返回")
        else:
            labels = ("", "", "", "重置", "返回")
        for index, label in enumerate(labels):
            if label:
                self._draw_tutorial_button(
                    PLANT_CONTROL_RECTS[index],
                    label,
                    CYAN if index in (0, 2) else TEXT_MUTED,
                )

        if state.phase is PlantingPhase.LOST:
            self._draw_planting_result_overlay(frame, state.phase)

    def _draw_planting_board(self, board: pygame.Rect, tile: int) -> None:
        assert self.planting_state is not None
        state = self.planting_state
        puzzle = state.puzzle
        board_art = self._scaled_puzzle_board(board.size)
        uses_formal_art = board_art is not None
        if board_art is not None:
            self.screen.blit(board_art, board.topleft)
        visible_blooms = (
            self.planting_showcase_frames[self.planting_showcase_index]
            if state.phase is PlantingPhase.WON and self.planting_showcase_frames
            else state.blooms
        )
        for y in range(puzzle.height):
            for x in range(puzzle.width):
                point = (x, y)
                rect = (
                    self._formal_tile_rect(board, point)
                    if uses_formal_art
                    else self._tile_rect(board, tile, point)
                )
                if not uses_formal_art:
                    pygame.draw.rect(self.screen, SOIL, rect, border_radius=7)
                    pygame.draw.rect(self.screen, SOIL_EDGE, rect, width=1, border_radius=7)
                if point in puzzle.expected_blooms:
                    pygame.draw.rect(self.screen, (126, 105, 58), rect.inflate(-8, -8), width=1, border_radius=5)
                if point in visible_blooms:
                    self._draw_bud(rect, False, point in self.bloomed)
                elif point in self.faded and self.flash_timer > 0:
                    pygame.draw.circle(self.screen, (74, 111, 87), rect.center, max(3, tile // 6))

        if state.phase is PlantingPhase.PLANTING:
            player_rect = (
                self._formal_tile_rect(board, state.player)
                if uses_formal_art
                else self._tile_rect(board, tile, state.player)
            )
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
        uses_formal_art = (
            self.puzzle_board is not None
            and state.puzzle.width == len(PUZZLE_BOARD_X_CELLS)
            and state.puzzle.height == len(PUZZLE_BOARD_Y_CELLS)
        )
        if uses_formal_art:
            board_art = self._scaled_puzzle_board(board.size)
            assert board_art is not None
            self.screen.blit(board_art, board.topleft)
        for y in range(state.puzzle.height):
            for x in range(state.puzzle.width):
                rect = (
                    self._formal_tile_rect(board, (x, y))
                    if uses_formal_art
                    else self._tile_rect(board, tile, (x, y))
                )
                if not uses_formal_art:
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

        player_rect = (
            self._formal_tile_rect(board, state.player)
            if uses_formal_art
            else self._tile_rect(board, tile, state.player)
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
        sprite = self._scaled_board_sprite("lantern" if player else "flower", rect.size)
        if sprite is not None:
            if newly_bloomed and self.flash_timer > 0:
                glow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow, (*BUD_CORE, 62), glow.get_rect().center, max(6, rect.width // 3)
                )
                self.screen.blit(glow, rect.topleft)
            self.screen.blit(sprite, self._sprite_destination(sprite, rect))
            return
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

    def _draw_wrapped_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        rect: pygame.Rect,
        line_height: int,
    ) -> int:
        x, y = rect.topleft
        line = ""
        for character in text:
            candidate = f"{line}{character}"
            if line and font.size(candidate)[0] > rect.width:
                self._text(line, font, color, (x, y))
                y += line_height
                line = character
            else:
                line = candidate
        if line and y + line_height <= rect.bottom + line_height:
            self._text(line, font, color, (x, y))
            y += line_height
        return y

    def _draw_tutorial_button(
        self, rect: pygame.Rect, label: str, color: tuple[int, int, int]
    ) -> None:
        pygame.draw.rect(self.screen, (75, 96, 88), rect, width=1, border_radius=7)
        surface = self.fonts["small"].render(label, True, color)
        self.screen.blit(surface, surface.get_rect(center=rect.center))

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
