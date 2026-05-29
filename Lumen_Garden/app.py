from __future__ import annotations

import math
import os
from dataclasses import dataclass
from pathlib import Path

import pygame

from .audio import AudioManager
from .patterns import BLINKER, BLOCK, GLIDER, PLANTING_PUZZLES, translate
from .puzzles import PUZZLES
from .model import Command, GameState, Phase, PlantingPhase, PlantingState, grow_once
from .tutorial import TUTORIAL_CARD, TUTORIAL_STEPS, TutorialStep

SCREEN_SIZE = (1280, 720)
WINDOW_SIZES = ((1024, 576), (1280, 720), (1600, 900))
FPS = 60
PLANTING_PLAYBACK_INTERVAL = 0.7
ASSET_ROOT = Path(__file__).resolve().parent.parent / "assets"
MENU_BACKGROUND_PATH = "sprites/menu.png"
GUIDE_MENU_BACKGROUND_PATH = "sprites/guide_menu.png"
TUTORIAL_MENU_BACKGROUND_PATH = "sprites/tutorial_menu.png"
GARDEN_BACKGROUND_PATH = "sprites/garden.png"
GUIDE_PUZZLE_BACKGROUND_PATH = "sprites/guide_puzzle.png"
PLANT_MENU_BACKGROUND_PATH = "sprites/plant_menu.png"
PLANT_PUZZLE_BACKGROUND_PATH = "sprites/plant_puzzle.png"
INTRODUCTION_PATH = "sprites/Introduction_1.png"
ENDING_PATH = "sprites/end_1.png"
SETTING_PANEL_PATH = "sprites/setting.png"
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
MENU_BUTTON_RECTS = tuple(pygame.Rect(819, 192 + index * 74, 342, 58) for index in range(4))
GARDEN_CARD_RECTS = (
    pygame.Rect(122, 133, 398, 62),
    pygame.Rect(122, 209, 398, 69),
    pygame.Rect(122, 289, 398, 65),
    pygame.Rect(122, 368, 398, 65),
    pygame.Rect(122, 448, 398, 65),
    pygame.Rect(122, 528, 398, 65),
)
GARDEN_BACK_RECT = pygame.Rect(194, 638, 222, 38)
GARDEN_HUB_PLOT_RECTS = tuple(
    pygame.Rect(156 + column * 318, 112 + row * 278, 228, 228)
    for row in range(2)
    for column in range(3)
)
GARDEN_HUB_BACK_RECT = pygame.Rect(1048, 646, 160, 38)
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
FOREST_BAG_RECT = pygame.Rect(1000, 24, 116, 40)
FOREST_CODEX_RECT = pygame.Rect(1130, 24, 116, 40)
FOREST_RETRY_RECT = pygame.Rect(1000, 78, 116, 34)
FOREST_BACK_RECT = pygame.Rect(1130, 78, 116, 34)
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


@dataclass(frozen=True)
class ForestRoom:
    number: int
    name: str
    name_en: str
    goal: str
    goal_en: str
    width: int
    height: int
    player_start: tuple[int, int]
    exit_cell: tuple[int, int]
    ordinary_plants: frozenset[tuple[int, int]]
    mechanism_plants: frozenset[tuple[int, int]] = frozenset()
    mechanism_missing: tuple[int, int] | None = None
    seed_cell: tuple[int, int] | None = None
    receiver_cell: tuple[int, int] | None = None
    ordinary_seed_cells: frozenset[tuple[int, int]] = frozenset()
    stone_cells: frozenset[tuple[int, int]] = frozenset()
    button_cells: frozenset[tuple[int, int]] = frozenset()
    discovery_pattern: str | None = None
    discovery_cells: frozenset[tuple[int, int]] = frozenset()
    initial_mechanism_active: bool = False
    initial_door_open: bool = False
    next_message: str = ""
    next_message_en: str = ""


@dataclass
class ForestState:
    room: ForestRoom
    player: tuple[int, int]
    ordinary_plants: set[tuple[int, int]]
    mechanism_plants: set[tuple[int, int]]
    mechanism_active: bool = False
    seed_cell: tuple[int, int] | None = None
    ordinary_seed_cells: set[tuple[int, int]] | None = None
    carrying_seed: bool = False
    door_open: bool = False
    generation: int = 0
    completed: bool = False


_ROOM2_BLOCK = translate(BLOCK.blooms, 4, 4)
_ROOM2_STONES = frozenset({
    (3, 3), (4, 3), (5, 3), (6, 3),
    (3, 4), (6, 4),
    (3, 5), (6, 5),
    (3, 6), (4, 6), (5, 6), (6, 6),
})
_ROOM3_GLIDER = translate(GLIDER.blooms, 2, 2)
_ROOM3_MISSING = (4, 4)
_ROOM3_START = frozenset(_ROOM3_GLIDER - {_ROOM3_MISSING})
_ROOM4_BLINKER = translate(BLINKER.blooms, 3, 3)
_ROOM4_BUTTONS = frozenset({(3, 4), (5, 4)})

FOREST_ROOMS: tuple[ForestRoom, ...] = (
    ForestRoom(
        1,
        "引路空庭",
        "Guiding Clearing",
        "熟悉上下左右移动，把灯灵带到发光出口。",
        "Practice moving the lantern and reach the glowing exit.",
        10,
        10,
        (5, 9),
        (5, 1),
        frozenset(),
        initial_door_open=True,
        next_message="第 1 个房间没有植物。先学会移动，再走向目标。",
        next_message_en="Room 1 has no plants. Learn to move, then reach the goal.",
    ),
    ForestRoom(
        2,
        "普通植物房",
        "Ordinary Grove",
        "穿过会生长与熄灭的花和蘑菇，到达左侧出口。",
        "Cross the living plants and reach the left edge exit.",
        10,
        10,
        (6, 9),
        (0, 5),
        frozenset({(2, 4), (3, 4), (4, 4), (3, 5), (1, 6), (2, 6), (3, 6)}),
        ordinary_seed_cells=frozenset({(8, 7)}),
        initial_door_open=True,
        next_message="普通植物会随灯灵行动生长或熄灭。",
        next_message_en="Ordinary plants grow or fade whenever the lantern acts.",
    ),
    ForestRoom(
        3,
        "静物图案房",
        "Still-Life Grove",
        "靠近被石头保护的四叶眠床，观察它为什么一直稳定。",
        "Approach the stone-ringed block and observe why it remains stable.",
        10,
        10,
        (5, 9),
        (9, 1),
        _ROOM2_BLOCK | frozenset({(1, 7), (2, 7), (2, 8)}),
        stone_cells=_ROOM2_STONES,
        discovery_pattern=BLOCK.key,
        discovery_cells=_ROOM2_BLOCK,
        initial_door_open=True,
        next_message="石头围住了一个 2x2 图案。靠近后，图鉴会记录这个稳定结构。",
        next_message_en="Stones protect a 2x2 pattern. Move near it to record the stable structure.",
    ),
    ForestRoom(
        4,
        "机关植物房",
        "Mechanism Grove",
        "拾起流光种的缺失种子，补回形状并启动它。",
        "Recover the missing glider seed, restore the shape, and awaken it.",
        10,
        10,
        (5, 9),
        (9, 0),
        frozenset(),
        _ROOM3_START,
        _ROOM3_MISSING,
        (5, 8),
        (5, 5),
        discovery_pattern=GLIDER.key,
        discovery_cells=_ROOM3_GLIDER,
        next_message="机关植物在启动前休眠；启动后才按生命规则飞行。",
        next_message_en="Mechanism plants sleep until awakened; then they follow Life rules.",
    ),
    ForestRoom(
        5,
        "脉冲门廊",
        "Blinker Gate",
        "观察摇曳花枝在两个按钮之间交替，趁出口变绿时离开。",
        "Watch the blinker alternate across two buttons, then leave while the exit is green.",
        10,
        10,
        (1, 9),
        (8, 1),
        frozenset({(1, 6), (2, 6), (2, 7), (7, 5), (8, 5), (8, 6)}),
        _ROOM4_BLINKER,
        button_cells=_ROOM4_BUTTONS,
        discovery_pattern=BLINKER.key,
        discovery_cells=_ROOM4_BLINKER,
        initial_mechanism_active=True,
        initial_door_open=True,
        next_message="两个按钮会读取植物是否压在上面；摇曳花枝让出口红绿交替。",
        next_message_en="The two buttons read whether plants stand on them; the blinker toggles the exit.",
    ),
)


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
        self.forest_state: ForestState | None = None
        self.planting_autoplay = False
        self.planting_playback_timer = 0.0
        self.planting_showcase_frames: list[frozenset[tuple[int, int]]] = []
        self.planting_showcase_index = 0
        self.tutorial_step = 0
        self.tutorial_resolved = False
        self.tutorial_completed = False
        self.completed_puzzles: set[int] = set()
        self.completed_planting: set[int] = set()
        self.forest_completed = False
        self.forest_resume_room = 0
        self.ordinary_seed_inventory = 0
        self.seed_inventory = 0
        self.codex_patterns: set[str] = set()
        self.garden_plots: list[str | None] = [None] * len(GARDEN_HUB_PLOT_RECTS)
        self.message = "选择一则月夜谜题"
        self.message_timer = 0.0
        self.flash_timer = 0.0
        self.bloomed: frozenset[tuple[int, int]] = frozenset()
        self.faded: frozenset[tuple[int, int]] = frozenset()
        self.elapsed = 0.0
        self.fonts = self._load_fonts()
        self.background = self._build_background()
        self.forest_background = self._build_forest_background()
        self.menu_background = self._load_menu_background(MENU_BACKGROUND_PATH) or self.background
        self.guide_menu_background = (
            self._load_menu_background(GUIDE_MENU_BACKGROUND_PATH) or self.background
        )
        self.guide_puzzle_background = (
            self._load_menu_background(GUIDE_PUZZLE_BACKGROUND_PATH) or self.background
        )
        self.tutorial_menu_background = (
            self._load_menu_background(TUTORIAL_MENU_BACKGROUND_PATH) or self.guide_puzzle_background
        )
        self.garden_background = (
            self._load_menu_background(GARDEN_BACKGROUND_PATH) or self.guide_puzzle_background
        )
        self.plant_menu_background = (
            self._load_menu_background(PLANT_MENU_BACKGROUND_PATH) or self.background
        )
        self.plant_puzzle_background = (
            self._load_menu_background(PLANT_PUZZLE_BACKGROUND_PATH) or self.background
        )
        self.introduction_image = self._load_image(INTRODUCTION_PATH)
        self.ending_image = self._load_image(ENDING_PATH)
        self.setting_panel = self._load_image(SETTING_PANEL_PATH)
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

    @staticmethod
    def _load_image(relative_path: str) -> pygame.Surface | None:
        path = ASSET_ROOT / relative_path
        if not path.exists():
            return None
        try:
            return pygame.image.load(str(path)).convert_alpha()
        except (OSError, pygame.error):
            return None

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

    @staticmethod
    def _build_forest_background() -> pygame.Surface:
        background = pygame.Surface(SCREEN_SIZE)
        top = (8, 24, 28)
        bottom = (20, 48, 34)
        for y in range(SCREEN_SIZE[1]):
            amount = y / SCREEN_SIZE[1]
            color = tuple(
                int(top[i] * (1 - amount) + bottom[i] * amount)
                for i in range(3)
            )
            pygame.draw.line(background, color, (0, y), (SCREEN_SIZE[0], y))
        canopy = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        for x, radius, alpha in (
            (58, 150, 48),
            (228, 210, 36),
            (1020, 260, 34),
            (1220, 180, 44),
        ):
            pygame.draw.circle(canopy, (20, 72, 48, alpha), (x, 90), radius)
        for x in range(24, SCREEN_SIZE[0], 96):
            pygame.draw.rect(canopy, (7, 18, 18, 58), pygame.Rect(x, 0, 26, 720))
        pygame.draw.circle(canopy, (156, 216, 164, 32), (384, 520), 260)
        pygame.draw.circle(canopy, (255, 207, 99, 24), (1032, 144), 120)
        background.blit(canopy, (0, 0))
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
                elif self.scene == "rules":
                    self._rules_key(event.key)
                elif self.scene == "game":
                    self._game_key(event.key)
                elif self.scene == "intro":
                    self._intro_key(event.key)
                elif self.scene == "ending":
                    self._ending_key(event.key)
                elif self.scene == "forest":
                    self._forest_key(event.key)
                elif self.scene == "garden_hub":
                    self._garden_hub_key(event.key)
                else:
                    self._planting_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._mouse_click(self._logical_point(event.pos))

    def _menu_key(self, key: int) -> None:
        if key in (pygame.K_ESCAPE, pygame.K_q):
            self._open_settings()
        elif key in (pygame.K_UP, pygame.K_w):
            self.main_selection = (self.main_selection - 1) % 4
            self.audio.play("select")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.main_selection = (self.main_selection + 1) % 4
            self.audio.play("select")
        elif key == pygame.K_p:
            self._open_free_garden()
        elif key in (pygame.K_g, pygame.K_0, pygame.K_t):
            self._open_rules()
        elif key == pygame.K_f:
            self._start_forest_intro()
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            (self._open_rules, self._start_forest_intro, self._open_free_garden, self._open_settings)[
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

    def _open_rules(self) -> None:
        self.scene = "rules"
        self.state = None
        self.planting_state = None
        self.forest_state = None
        self.message = self._tr(
            "生命规则",
            "Life rules",
        )
        self.message_timer = 99.0
        self.audio.play("select")
        self.audio.play_music("puzzle")

    def _open_free_garden(self) -> None:
        self.scene = "garden_hub"
        self.state = None
        self.planting_state = None
        self.forest_state = None
        self.message = self._tr(
            "选择一块空花圃，用背包里的种子按图鉴复现植物。",
            "Choose an empty plot and plant from your backpack and codex.",
        )
        self.message_timer = 5.0
        self.audio.play("select")
        self.audio.play_music("menu")

    def _start_forest_intro(self) -> None:
        self.scene = "intro"
        self.state = None
        self.planting_state = None
        self.forest_state = None
        self.message = self._tr(
            "按 ENTER / SPACE 或点击继续",
            "Press ENTER / SPACE or click to continue.",
        )
        self.message_timer = 99.0
        self.audio.play("select")
        self.audio.play_music("puzzle")

    def _open_settings(self) -> None:
        self.settings_open = True
        self.audio.play("select")

    def _settings_key(self, key: int) -> None:
        if key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.settings_open = False

    def _intro_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.scene = "menu"
            self.audio.play_music("menu")
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self._start_forest_room(self.forest_resume_room)

    def _ending_key(self, key: int) -> None:
        if key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
            self._show_unlocked_garden()

    def _garden_hub_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.scene = "menu"
            self.audio.play_music("menu")

    def _rules_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.scene = "menu"
            self.audio.play_music("menu")

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
                    (self._open_rules, self._start_forest_intro, self._open_free_garden, self._open_settings)[
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
        elif self.scene == "rules":
            if self._rules_back_rect().collidepoint(point):
                self.scene = "menu"
                self.audio.play_music("menu")
        elif self.scene == "intro":
            self._start_forest_room(self.forest_resume_room)
        elif self.scene == "ending":
            self._show_unlocked_garden()
        elif self.scene == "forest":
            self._forest_click(point)
        elif self.scene == "garden_hub":
            self._garden_hub_click(point)

    def _settings_click(self, point: tuple[int, int]) -> None:
        for index, (size, rect) in enumerate(zip(WINDOW_SIZES, self._settings_size_rects())):
            if rect.collidepoint(point):
                self._set_window_size(size)
                return
        for language, rect in zip(("zh", "en"), self._settings_language_rects()):
            if rect.collidepoint(point):
                self._set_language(language)
                self.audio.play("select")
                return
        minus_rect, plus_rect, mute_rect = self._settings_volume_rects()
        if minus_rect.collidepoint(point):
            self.audio.set_volume(self.audio.volume - 0.1)
        elif plus_rect.collidepoint(point):
            self.audio.set_volume(self.audio.volume + 0.1)
        elif mute_rect.collidepoint(point):
            self.audio.toggle_enabled()
        back_rect, exit_level_rect, quit_rect = self._settings_action_rects()
        if back_rect.collidepoint(point):
            self.settings_open = False
        elif exit_level_rect is not None and exit_level_rect.collidepoint(point):
            self._exit_current_level()
        elif quit_rect.collidepoint(point):
            self.running = False

    def _settings_action_rects(self) -> tuple[pygame.Rect, pygame.Rect | None, pygame.Rect]:
        panel = self._settings_panel_rect()
        if self._settings_has_level_exit():
            return (
                pygame.Rect(panel.x + 36, panel.y + 388, 148, 44),
                pygame.Rect(panel.x + 202, panel.y + 388, 166, 44),
                pygame.Rect(panel.x + 386, panel.y + 388, 120, 44),
            )
        return (
            pygame.Rect(panel.x + 64, panel.y + 388, 200, 44),
            None,
            pygame.Rect(panel.x + 304, panel.y + 388, 200, 44),
        )

    def _settings_has_level_exit(self) -> bool:
        return self.scene in ("forest", "game", "planting", "tutorial")

    def _settings_panel_rect(self) -> pygame.Rect:
        if self.setting_panel is not None:
            return self.setting_panel.get_rect(center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2))
        return pygame.Rect(378, 142, 524, 446)

    def _settings_size_rects(self) -> tuple[pygame.Rect, pygame.Rect, pygame.Rect]:
        panel = self._settings_panel_rect()
        return (
            pygame.Rect(panel.x + 64, panel.y + 148, 128, 45),
            pygame.Rect(panel.x + 212, panel.y + 148, 128, 45),
            pygame.Rect(panel.x + 360, panel.y + 148, 128, 45),
        )

    def _settings_language_rects(self) -> tuple[pygame.Rect, pygame.Rect]:
        panel = self._settings_panel_rect()
        return (
            pygame.Rect(panel.x + 178, panel.y + 248, 160, 45),
            pygame.Rect(panel.x + 356, panel.y + 248, 160, 45),
        )

    def _settings_volume_rects(self) -> tuple[pygame.Rect, pygame.Rect, pygame.Rect]:
        panel = self._settings_panel_rect()
        return (
            pygame.Rect(panel.x + 64, panel.y + 330, 52, 45),
            pygame.Rect(panel.x + 298, panel.y + 330, 52, 45),
            pygame.Rect(panel.x + 410, panel.y + 330, 106, 45),
        )

    def _exit_current_level(self) -> None:
        if self.scene == "forest" and self.forest_state is not None:
            self.forest_resume_room = self._forest_room_index(self.forest_state.room)
            self.message = self._tr(
                f"下次将从第 {self.forest_state.room.number} 个房间开始。",
                f"Next time starts from room {self.forest_state.room.number}.",
            )
        else:
            self.message = self._tr("已退出关卡。", "Level exited.")
        self.settings_open = False
        self.state = None
        self.planting_state = None
        self.forest_state = None
        self.scene = "menu"
        self.audio.play_music("menu")

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

    @staticmethod
    def _forest_board_layout(width: int, height: int) -> tuple[pygame.Rect, int]:
        size = min(620, SCREEN_SIZE[1] - 110)
        tile = size // max(width, height)
        board = pygame.Rect(
            (SCREEN_SIZE[0] - width * tile) // 2,
            62,
            width * tile,
            height * tile,
        )
        return board, tile

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

    def _garden_hub_click(self, point: tuple[int, int]) -> None:
        if GARDEN_HUB_BACK_RECT.collidepoint(point):
            self.scene = "menu"
            self.audio.play_music("menu")
            return
        if self.message_timer > 0 and self._garden_hub_dialog_rect().collidepoint(point):
            self.message_timer = 0.0
            return
        for index, rect in enumerate(GARDEN_HUB_PLOT_RECTS):
            if rect.collidepoint(point):
                self._interact_garden_plot(index)
                return

    def _interact_garden_plot(self, index: int) -> None:
        planted = self.garden_plots[index]
        if planted is not None:
            self.message = self._tr(
                f"第 {index + 1} 块花圃已经种下：{self._garden_pattern_name(planted)}。",
                f"Plot {index + 1} already grows {self._garden_pattern_name(planted)}.",
            )
            self.message_timer = 4.0
            self.audio.play("select")
            return

        choice = self._next_garden_planting_choice()
        if choice is None:
            self.message = self._garden_missing_requirements_message()
            self.message_timer = 5.0
            self.audio.play("reject")
            return

        key, ordinary_cost, glider_cost = choice
        self.ordinary_seed_inventory -= ordinary_cost
        self.seed_inventory -= glider_cost
        self.garden_plots[index] = key
        self.message = self._tr(
            f"第 {index + 1} 块花圃种下了{self._garden_pattern_name(key)}。",
            f"Plot {index + 1} now grows {self._garden_pattern_name(key)}.",
        )
        self.message_timer = 4.0
        self.audio.play("grow")

    def _next_garden_planting_choice(self) -> tuple[str, int, int] | None:
        if BLOCK.key in self.codex_patterns and self.ordinary_seed_inventory >= 4:
            return (BLOCK.key, 4, 0)
        if BLINKER.key in self.codex_patterns and self.ordinary_seed_inventory >= 3:
            return (BLINKER.key, 3, 0)
        if GLIDER.key in self.codex_patterns and self.seed_inventory >= 1:
            return (GLIDER.key, 0, 1)
        if self.ordinary_seed_inventory >= 1:
            return ("ORDINARY", 1, 0)
        return None

    def _garden_missing_requirements_message(self) -> str:
        if not self.codex_patterns and self.ordinary_seed_inventory <= 0 and self.seed_inventory <= 0:
            return self._tr(
                "背包和图鉴都是空的。先去荧光森林收集种子、记录图案。",
                "Backpack and codex are empty. Visit the forest to collect seeds and record patterns.",
            )
        return self._tr(
            "还不能复现新的图案：普通植物需要 1 枚种子，四叶眠床需要图鉴记录和 4 枚普通种子，流光种需要图鉴记录和 1 枚流光种。",
            "No new planting is ready: ordinary plants need 1 seed, Block needs its codex entry and 4 ordinary seeds, Glider needs its codex entry and 1 glider seed.",
        )

    @staticmethod
    def _garden_pattern_name(key: str) -> str:
        return {
            "ORDINARY": "普通植物",
            BLOCK.key: "四叶眠床",
            BLINKER.key: "摇曳花枝",
            GLIDER.key: "流光种",
        }.get(key, key)

    def _tutorial_click(self, point: tuple[int, int]) -> None:
        if self.tutorial_step >= len(TUTORIAL_STEPS):
            if PUZZLE_PRIMARY_RECT.collidepoint(point):
                self.scene = "menu"
                self.state = None
                self.audio.play_music("menu")
            elif PUZZLE_RETRY_RECT.collidepoint(point):
                self._start_tutorial()
            elif PUZZLE_BACK_RECT.collidepoint(point):
                self.scene = "menu"
                self.state = None
                self.audio.play_music("menu")
            return
        if PUZZLE_PRIMARY_RECT.collidepoint(point):
            self._tutorial_key(pygame.K_RETURN)
        elif PUZZLE_RETRY_RECT.collidepoint(point):
            self._tutorial_key(pygame.K_r)
        elif PUZZLE_BACK_RECT.collidepoint(point):
            self.scene = "menu"
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

    def _start_forest_room(self, index: int) -> None:
        room = FOREST_ROOMS[index]
        self.forest_state = ForestState(
            room=room,
            player=room.player_start,
            ordinary_plants=set(room.ordinary_plants),
            mechanism_plants=set(room.mechanism_plants),
            mechanism_active=room.initial_mechanism_active,
            seed_cell=room.seed_cell,
            ordinary_seed_cells=set(room.ordinary_seed_cells),
            carrying_seed=self.seed_inventory > 0,
            door_open=room.initial_door_open,
        )
        if room.button_cells:
            self.forest_state.door_open = self._forest_buttons_have_plants(self.forest_state)
        self.state = None
        self.planting_state = None
        self.scene = "forest"
        self.bloomed = frozenset()
        self.faded = frozenset()
        self.flash_timer = 0.0
        self.message = self._tr(room.next_message, room.next_message_en)
        self.message_timer = 5.0
        self.audio.play_music("puzzle")

    def _forest_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self._open_settings()
            return
        if key == pygame.K_r and self.forest_state is not None:
            self._start_forest_room(self._forest_room_index(self.forest_state.room))
            return
        if key == pygame.K_p:
            self._forest_plant_or_start()
            return
        command = self._command_for_key(key)
        if command is not None:
            self._issue_forest(command)

    def _forest_click(self, point: tuple[int, int]) -> None:
        assert self.forest_state is not None
        board, _ = self._forest_board_layout(
            self.forest_state.room.width, self.forest_state.room.height
        )
        if FOREST_BAG_RECT.collidepoint(point):
            self._show_forest_bag()
            return
        if FOREST_CODEX_RECT.collidepoint(point):
            self._show_forest_codex()
            return
        if FOREST_RETRY_RECT.collidepoint(point):
            self._start_forest_room(self._forest_room_index(self.forest_state.room))
            return
        if FOREST_BACK_RECT.collidepoint(point):
            self.scene = "menu"
            self.forest_state = None
            self.audio.play_music("menu")
            return
        if self.message_timer > 0 and self._forest_dialog_rect().collidepoint(point):
            self.message_timer = 0.0
            return
        command = self._formal_grid_command(point, board, self.forest_state.player)
        if command is not None:
            self._issue_forest(command)

    def _forest_plant_or_start(self) -> None:
        assert self.forest_state is not None
        state = self.forest_state
        room = state.room
        if room.mechanism_missing is None:
            self._show_forest_bag()
            return
        if state.mechanism_active:
            self.message = self._tr("机关植物已经醒来。移动或等待让它继续飞行。", "The mechanism plant is awake. Move or wait to advance it.")
            self.message_timer = 3.0
            self.audio.play("reject")
            return
        if not state.carrying_seed and self.seed_inventory <= 0:
            self.message = self._tr("先拾起流光种的缺失种子。", "Pick up the missing glider seed first.")
            self.message_timer = 3.0
            self.audio.play("reject")
            return
        if state.player != room.mechanism_missing:
            self.message = self._tr("站到高亮缺口上，按 P 补回并启动。", "Stand on the highlighted gap and press P to restore it.")
            self.message_timer = 3.0
            self.audio.play("reject")
            return
        before = set(state.mechanism_plants)
        state.mechanism_plants.add(room.mechanism_missing)
        state.carrying_seed = False
        if self.seed_inventory > 0:
            self.seed_inventory -= 1
        state.mechanism_active = True
        self._record_forest_pattern(room.discovery_pattern)
        self.bloomed = frozenset(state.mechanism_plants - before)
        self.faded = frozenset()
        self.flash_timer = 0.5
        self.message = self._tr("流光种醒来了。移动或等待，让它飞向机关。", "The glider wakes. Move or wait to send it onward.")
        self.message_timer = 4.0
        self.audio.play("grow")

    def _issue_forest(self, command: Command) -> None:
        assert self.forest_state is not None
        state = self.forest_state
        room = state.room
        dx, dy = command.value
        target = (state.player[0] + dx, state.player[1] + dy)
        if command is not Command.WAIT:
            if not self._forest_inside(target):
                self.message = self._tr("森林边缘还没有路。", "There is no path beyond this edge.")
                self.message_timer = 2.5
                self.audio.play("reject")
                return
            if target in self._forest_blocking_plants():
                self.message = self._tr("植物挡住了路，试着移动或等待改变它。", "A plant blocks the path; move or wait to change it.")
                self.message_timer = 2.5
                self.audio.play("reject")
                return
            state.player = target
            if state.ordinary_seed_cells is not None and target in state.ordinary_seed_cells:
                state.ordinary_seed_cells.remove(target)
                self.ordinary_seed_inventory += 1
                self.message = self._tr(
                    "拾起了一枚普通植物种子，已经收进背包。",
                    "You picked up an ordinary plant seed and stored it in the backpack.",
                )
                self.message_timer = 4.0
                self.audio.play("select")
            if state.seed_cell == target:
                state.carrying_seed = True
                state.seed_cell = None
                self.seed_inventory += 1
                self.message = self._tr("拾起了一枚流光种。前往缺口按 P。", "You picked up a glider seed. Carry it to the gap and press P.")
                self.message_timer = 4.0
                self.audio.play("select")

        self._advance_forest_plants()
        self._check_forest_discovery()
        self._check_forest_goal()
        if command is Command.WAIT:
            self.audio.play("wait")
        else:
            self.audio.play("move")

    def _advance_forest_plants(self) -> None:
        assert self.forest_state is not None
        state = self.forest_state
        room = state.room
        ordinary_before = set(state.ordinary_plants)
        mechanism_before = set(state.mechanism_plants)
        state.ordinary_plants = grow_once(
            state.ordinary_plants,
            room.width,
            room.height,
            {state.player},
        )
        state.ordinary_plants.difference_update(room.stone_cells)
        if state.mechanism_active:
            state.mechanism_plants = grow_once(
                state.mechanism_plants,
                room.width,
                room.height,
            )
            state.mechanism_plants.difference_update(room.stone_cells)
        state.generation += 1
        all_before = ordinary_before | mechanism_before
        all_after = state.ordinary_plants | state.mechanism_plants
        self.bloomed = frozenset(all_after - all_before)
        self.faded = frozenset(all_before - all_after)
        self.flash_timer = 0.45

    def _check_forest_goal(self) -> None:
        assert self.forest_state is not None
        state = self.forest_state
        room = state.room
        if room.button_cells:
            was_open = state.door_open
            state.door_open = self._forest_buttons_have_plants(state)
            if state.door_open != was_open:
                self.message = self._tr(
                    "按钮上的植物改变了出口颜色。",
                    "Plants on the buttons changed the exit color.",
                )
                self.message_timer = 3.0
                self.audio.play("select")
        if room.receiver_cell is not None and room.receiver_cell in state.mechanism_plants:
            if not state.door_open:
                self.message = self._tr("流光种触碰机关，出口打开了。", "The glider touches the mechanism; the exit opens.")
                self.audio.play("win")
            state.door_open = True
        if state.player == room.exit_cell and state.door_open:
            self._complete_forest_room()

    def _complete_forest_room(self) -> None:
        assert self.forest_state is not None
        current = self._forest_room_index(self.forest_state.room)
        if current + 1 < len(FOREST_ROOMS):
            self._start_forest_room(current + 1)
            return
        self.forest_completed = True
        self.forest_state = None
        self.scene = "ending"
        self.message = self._tr(
            "灯灵穿过荧光森林，看见了灯漫村的光。",
            "The lantern leaves the forest and sees the lights of the village.",
        )
        self.message_timer = 99.0
        self.audio.play("win")
        self.audio.play_music("puzzle")

    def _show_unlocked_garden(self) -> None:
        self.scene = "garden_hub"
        self.message = self._tr(
            "灯漫村的微光回应了它。荧光花园已解锁，选择花圃开始种植。",
            "The village lights answer. Lumen Garden is unlocked; choose a plot to plant.",
        )
        self.message_timer = 5.0
        self.audio.play_music("menu")

    @staticmethod
    def _forest_room_index(room: ForestRoom) -> int:
        return FOREST_ROOMS.index(room)

    def _forest_seed_total(self) -> int:
        return self.ordinary_seed_inventory + self.seed_inventory

    def _show_forest_bag(self) -> None:
        self.message = self._tr(
            f"背包里有普通植物种子 {self.ordinary_seed_inventory} 枚，流光种 {self.seed_inventory} 枚。",
            f"Backpack: {self.ordinary_seed_inventory} ordinary seed(s), {self.seed_inventory} glider seed(s).",
        )
        self.message_timer = 4.0
        self.audio.play("select")

    def _show_forest_codex(self) -> None:
        self.message = self._tr(
            f"图鉴已记录：{self._forest_codex_label()}。",
            f"Codex records: {self._forest_codex_label()}.",
        )
        self.message_timer = 4.0
        self.audio.play("select")

    @staticmethod
    def _forest_buttons_have_plants(state: ForestState) -> bool:
        plants = state.ordinary_plants | state.mechanism_plants
        return any(button in plants for button in state.room.button_cells)

    def _record_forest_pattern(self, pattern_key: str | None) -> None:
        if pattern_key is not None:
            self.codex_patterns.add(pattern_key)

    def _check_forest_discovery(self) -> None:
        assert self.forest_state is not None
        room = self.forest_state.room
        if room.discovery_pattern is None or room.discovery_pattern in self.codex_patterns:
            return
        px, py = self.forest_state.player
        near_pattern = any(
            max(abs(px - x), abs(py - y)) <= 2 for x, y in room.discovery_cells
        )
        if near_pattern:
            self._record_forest_pattern(room.discovery_pattern)
            self.message = self._tr(
                f"图鉴记录了新图案：{self._forest_pattern_name(room.discovery_pattern)}。",
                f"Codex recorded a new pattern: {self._forest_pattern_name(room.discovery_pattern)}.",
            )
            self.message_timer = 4.0
            self.audio.play("select")

    @staticmethod
    def _forest_pattern_name(pattern_key: str) -> str:
        return {
            BLOCK.key: "四叶眠床",
            GLIDER.key: "流光种",
            BLINKER.key: "摇曳花枝",
        }.get(pattern_key, pattern_key)

    def _forest_codex_label(self) -> str:
        if not self.codex_patterns:
            return self._tr("空", "empty")
        return " / ".join(
            self._forest_pattern_name(key)
            for key in (BLOCK.key, GLIDER.key, BLINKER.key)
            if key in self.codex_patterns
        )

    def _forest_inside(self, point: tuple[int, int]) -> bool:
        assert self.forest_state is not None
        room = self.forest_state.room
        return 0 <= point[0] < room.width and 0 <= point[1] < room.height

    def _forest_blocking_plants(self) -> set[tuple[int, int]]:
        assert self.forest_state is not None
        state = self.forest_state
        return set(state.ordinary_plants) | set(state.mechanism_plants) | set(state.room.stone_cells)

    def _game_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self._open_settings()
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
            self._open_settings()
            return
        if self.tutorial_step >= len(TUTORIAL_STEPS):
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.scene = "menu"
                self.state = None
                self.audio.play_music("menu")
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
            self._open_settings()
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
        elif self.scene == "rules":
            background = self.tutorial_menu_background
        elif self.scene in ("tutorial", "game"):
            background = self.guide_puzzle_background
        elif self.scene == "planting":
            background = self.plant_puzzle_background
        elif self.scene == "garden_hub":
            background = self.garden_background
        elif self.scene in ("intro", "ending"):
            background = self.guide_puzzle_background
        elif self.scene == "forest":
            background = self.forest_background
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
        elif self.scene == "rules":
            self._draw_rules()
        elif self.scene == "game":
            self._draw_game()
        elif self.scene == "planting":
            self._draw_planting()
        elif self.scene == "intro":
            self._draw_intro()
        elif self.scene == "ending":
            self._draw_ending()
        elif self.scene == "forest":
            self._draw_forest()
        elif self.scene == "garden_hub":
            self._draw_garden_hub()
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
            (self._tr("教程", "TUTORIAL"), ""),
            (self._tr("荧光森林", "LUMEN FOREST"), ""),
            (self._tr("荧光花园", "LUMEN GARDEN"), ""),
            (self._tr("设置", "SETTINGS"), ""),
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
            label_surface = self.fonts["h2"].render(label, True, accent)
            self.screen.blit(label_surface, label_surface.get_rect(center=rect.center))
            if detail:
                self._text(detail, self.fonts["small"], TEXT_MUTED, (rect.x + 153, rect.y + 25))
        self._text(
            self._tr("↑ ↓ / ENTER 选择    ESC 退出", "UP / DOWN / ENTER Select    ESC Quit"),
            self.fonts["small"],
            (211, 192, 153),
            (840, 522),
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

    def _draw_intro(self) -> None:
        self._draw_story_image(
            self.introduction_image,
            self._tr("开场漫画素材缺失", "Introduction image missing"),
        )

    def _draw_ending(self) -> None:
        self._draw_story_image(
            self.ending_image,
            self._tr("结尾漫画素材缺失", "Ending image missing"),
        )

    def _draw_story_image(
        self,
        image: pygame.Surface | None,
        missing_text: str,
    ) -> None:
        self.screen.fill((0, 0, 0))
        if image is not None:
            scale = min(SCREEN_SIZE[0] / image.get_width(), SCREEN_SIZE[1] / image.get_height())
            size = (int(image.get_width() * scale), int(image.get_height() * scale))
            scaled = pygame.transform.smoothscale(image, size)
            rect = scaled.get_rect(center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2))
            self.screen.blit(scaled, rect)
        else:
            self._text(missing_text, self.fonts["h1"], TEXT, (420, 300))
        self._draw_click_hint()
        self._draw_skip_button()

    def _draw_click_hint(self) -> None:
        center = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] - 31)
        alpha = 90 + int(50 * (0.5 + 0.5 * math.sin(self.elapsed * 3.0)))
        hint = pygame.Surface((44, 18), pygame.SRCALPHA)
        pygame.draw.circle(hint, (245, 238, 215, alpha), (12, 9), 5)
        pygame.draw.circle(hint, (245, 238, 215, alpha // 2), (27, 9), 5, width=2)
        pygame.draw.polygon(
            hint,
            (245, 238, 215, alpha),
            ((36, 5), (42, 9), (36, 13)),
        )
        self.screen.blit(hint, hint.get_rect(center=center))

    def _draw_skip_button(self) -> None:
        rect = self._skip_button_rect()
        label = self._tr("跳过剧情", "SKIP")
        surface = self.fonts["small"].render(label, True, (232, 224, 200))
        shade = pygame.Surface(rect.size, pygame.SRCALPHA)
        shade.fill((0, 0, 0, 128))
        self.screen.blit(shade, rect.topleft)
        pygame.draw.rect(self.screen, (116, 106, 86), rect, width=1, border_radius=6)
        self.screen.blit(surface, surface.get_rect(center=rect.center))

    def _skip_button_rect(self) -> pygame.Rect:
        label = self._tr("跳过剧情", "SKIP")
        width, height = self.fonts["small"].size(label)
        padding_x = 14
        padding_y = 8
        return pygame.Rect(
            SCREEN_SIZE[0] - width - padding_x * 2 - 28,
            SCREEN_SIZE[1] - height - padding_y * 2 - 22,
            width + padding_x * 2,
            height + padding_y * 2,
        )

    def _draw_coming_soon(self) -> None:
        panel = pygame.Rect(338, 198, 604, 270)
        self._rounded_panel(panel, active=False)
        self._text(self._tr("荧光花园", "LUMEN GARDEN"), self.fonts["title"], TEXT, (panel.x + 72, panel.y + 54))
        self._draw_wrapped_text(
            self.message,
            self.fonts["body"],
            CYAN,
            pygame.Rect(panel.x + 80, panel.y + 135, panel.width - 160, 78),
            28,
        )
        self._text(
            self._tr("ENTER / SPACE / 点击  返回首页", "ENTER / SPACE / Click  Back to menu"),
            self.fonts["small"],
            TEXT_MUTED,
            (panel.x + 177, panel.y + 226),
        )

    def _draw_garden_hub(self) -> None:
        veil = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        veil.fill((8, 20, 18, 70))
        self.screen.blit(veil, (0, 0))
        self._text(self._tr("荧光花园", "LUMEN GARDEN"), self.fonts["title"], TEXT, (74, 42))
        self._text(
            self._tr(
                f"背包 普通种子 {self.ordinary_seed_inventory} / 流光种 {self.seed_inventory}    图鉴 {self._forest_codex_label()}",
                f"Backpack ordinary {self.ordinary_seed_inventory} / glider {self.seed_inventory}    Codex {self._forest_codex_label()}",
            ),
            self.fonts["small"],
            GOLD,
            (80, 108),
        )
        for index, rect in enumerate(GARDEN_HUB_PLOT_RECTS):
            self._draw_garden_plot(index, rect)
        if self.message_timer > 0:
            panel = self._garden_hub_dialog_rect()
            shade = pygame.Surface(panel.size, pygame.SRCALPHA)
            shade.fill((7, 18, 18, 210))
            self.screen.blit(shade, panel.topleft)
            pygame.draw.rect(self.screen, (92, 142, 102), panel, width=2, border_radius=10)
            self._draw_wrapped_text(
                self.message,
                self.fonts["small"],
                TEXT,
                pygame.Rect(panel.x + 24, panel.y + 14, panel.width - 48, 28),
                21,
            )
        self._draw_tutorial_button(GARDEN_HUB_BACK_RECT, self._tr("返回首页", "HOME"), TEXT_MUTED)

    @staticmethod
    def _garden_hub_dialog_rect() -> pygame.Rect:
        return pygame.Rect(236, 634, 780, 54)

    def _draw_garden_plot(self, index: int, rect: pygame.Rect) -> None:
        board_art = self._scaled_puzzle_board(rect.size)
        if board_art is not None:
            self.screen.blit(board_art, rect.topleft)
        else:
            pygame.draw.rect(self.screen, SOIL, rect, border_radius=10)
            pygame.draw.rect(self.screen, SOIL_EDGE, rect, width=2, border_radius=10)
        pygame.draw.rect(self.screen, GOLD if self.garden_plots[index] else (92, 142, 102), rect, width=2, border_radius=10)
        planted = self.garden_plots[index]
        if planted is None:
            self._text(
                self._tr(f"花圃 {index + 1}", f"PLOT {index + 1}"),
                self.fonts["small"],
                TEXT_MUTED,
                (rect.x + 17, rect.y + 15),
            )
            return
        for point in self._garden_plot_blooms(planted):
            cell = self._garden_plot_cell_rect(rect, point)
            self._draw_mechanism_bloom(cell, False, True) if planted == GLIDER.key else self._draw_bud(cell, False, False)
        self._text(
            self._garden_pattern_name(planted),
            self.fonts["small"],
            GOLD,
            (rect.x + 17, rect.bottom - 30),
        )

    @staticmethod
    def _garden_plot_cell_rect(board: pygame.Rect, point: tuple[int, int]) -> pygame.Rect:
        x_start, x_end = PUZZLE_BOARD_X_CELLS[point[0]]
        y_start, y_end = PUZZLE_BOARD_Y_CELLS[point[1]]
        left = board.x + round(x_start * board.width / PUZZLE_BOARD_SOURCE_SIZE)
        top = board.y + round(y_start * board.height / PUZZLE_BOARD_SOURCE_SIZE)
        right = board.x + round(x_end * board.width / PUZZLE_BOARD_SOURCE_SIZE)
        bottom = board.y + round(y_end * board.height / PUZZLE_BOARD_SOURCE_SIZE)
        return pygame.Rect(left, top, max(1, right - left), max(1, bottom - top))

    @staticmethod
    def _garden_plot_blooms(key: str) -> frozenset[tuple[int, int]]:
        if key == BLOCK.key:
            return translate(BLOCK.blooms, 4, 4)
        if key == BLINKER.key:
            return translate(BLINKER.blooms, 3, 4)
        if key == GLIDER.key:
            return translate(GLIDER.blooms, 3, 3)
        return frozenset({(5, 5)})

    def _draw_rules(self) -> None:
        rules = (
            (
                self._tr("有生命的格子，0 或 1 个邻居：死亡。", "Live cell with 0 or 1 neighbors: dies."),
                {(1, 1), (2, 2)},
                {(2, 2)},
                (2, 2),
            ),
            (
                self._tr("有生命的格子，4 个或更多邻居：死亡。", "Live cell with 4 or more neighbors: dies."),
                {(1, 1), (2, 1), (3, 1), (2, 2), (1, 3), (3, 3)},
                {(1, 1), (3, 1), (1, 3), (3, 3)},
                (2, 2),
            ),
            (
                self._tr("有生命的格子，2 或 3 个邻居：存活。", "Live cell with 2 or 3 neighbors: survives."),
                {(1, 1), (2, 2), (2, 3)},
                {(1, 2), (2, 2)},
                (2, 2),
            ),
            (
                self._tr("空格子，恰好 3 个邻居：诞生。", "Empty cell with exactly 3 neighbors: becomes alive."),
                {(1, 1), (1, 2), (3, 3)},
                {(2, 2)},
                (2, 2),
            ),
        )
        for index, (label, before, after, focus) in enumerate(rules):
            y = 252 + index * 82
            self._draw_wrapped_text(label, self.fonts["body"], TEXT, pygame.Rect(104, y + 9, 520, 38), 24)
            self._draw_rule_grid((744, y), before, focus)
            self._draw_rule_arrow((846, y + 30))
            self._draw_rule_grid((948, y), after, focus)

        back = self._rules_back_rect()
        self._rounded_panel(back, active=True)
        label = self._tr("返回主页", "HOME")
        surface = self.fonts["h2"].render(label, True, CYAN)
        self.screen.blit(surface, surface.get_rect(center=back.center))

    @staticmethod
    def _rules_back_rect() -> pygame.Rect:
        return pygame.Rect(104, 632, 210, 48)

    def _draw_rule_grid(
        self,
        position: tuple[int, int],
        cells: set[tuple[int, int]],
        focus: tuple[int, int],
    ) -> None:
        size = 15
        x0, y0 = position
        for y in range(5):
            for x in range(5):
                rect = pygame.Rect(x0 + x * size, y0 + y * size, size - 1, size - 1)
                color = (181, 184, 181)
                if (x, y) == focus:
                    color = (111, 114, 113)
                if (x, y) in cells:
                    color = (248, 246, 101)
                pygame.draw.rect(self.screen, color, rect)

    def _draw_rule_arrow(self, position: tuple[int, int]) -> None:
        x, y = position
        pygame.draw.arc(self.screen, (177, 181, 181), pygame.Rect(x, y - 18, 58, 44), math.radians(205), math.radians(20), 6)
        pygame.draw.polygon(
            self.screen,
            (177, 181, 181),
            ((x + 55, y + 1), (x + 42, y - 14), (x + 42, y + 13)),
        )

    def _draw_forest(self) -> None:
        assert self.forest_state is not None
        state = self.forest_state
        room = state.room
        board_rect, tile = self._forest_board_layout(room.width, room.height)
        self._draw_forest_board(board_rect, tile)
        self._draw_forest_hud(room, state)
        if self.message_timer > 0:
            self._draw_forest_dialog(room)

    def _draw_forest_hud(self, room: ForestRoom, state: ForestState) -> None:
        self._text(
            self._tr(f"荧光森林 {room.number:02d} / {len(FOREST_ROOMS):02d}", f"LUMEN FOREST {room.number:02d} / {len(FOREST_ROOMS):02d}"),
            self.fonts["small"],
            CYAN,
            (34, 22),
        )
        self._text(
            self._tr(f"第 {state.generation} 代", f"GEN {state.generation}"),
            self.fonts["h2"],
            TEXT,
            (34, 44),
        )
        self._draw_tutorial_button(
            FOREST_BAG_RECT,
            self._tr(f"背包 {self._forest_seed_total()}", f"BAG {self._forest_seed_total()}"),
            CYAN,
        )
        self._draw_tutorial_button(
            FOREST_CODEX_RECT,
            self._tr(f"图鉴 {len(self.codex_patterns)}", f"CODEX {len(self.codex_patterns)}"),
            CYAN,
        )
        self._draw_tutorial_button(FOREST_RETRY_RECT, self._tr("R 重试", "R RETRY"), TEXT_MUTED)
        self._draw_tutorial_button(FOREST_BACK_RECT, self._tr("ESC 返回", "ESC BACK"), TEXT_MUTED)

    def _draw_forest_dialog(self, room: ForestRoom) -> None:
        panel = self._forest_dialog_rect()
        shade = pygame.Surface(panel.size, pygame.SRCALPHA)
        shade.fill((7, 18, 18, 210))
        self.screen.blit(shade, panel.topleft)
        pygame.draw.rect(self.screen, (92, 142, 102), panel, width=2, border_radius=12)
        self._text(self._tr(room.name, room.name_en), self.fonts["h2"], GOLD, (panel.x + 28, panel.y + 20))
        self._draw_wrapped_text(
            self.message,
            self.fonts["body"],
            TEXT,
            pygame.Rect(panel.x + 28, panel.y + 58, panel.width - 56, 54),
            25,
        )

    @staticmethod
    def _forest_dialog_rect() -> pygame.Rect:
        return pygame.Rect(210, 560, 860, 128)

    def _forest_status_text(self) -> str:
        assert self.forest_state is not None
        state = self.forest_state
        if state.room.button_cells:
            door = self._tr("绿色", "green") if state.door_open else self._tr("红色", "red")
            return self._tr(
                f"背包 {self.seed_inventory} | 图鉴 {self._forest_codex_label()} | 出口{door} | 第 {state.generation} 代",
                f"Backpack {self.seed_inventory} | Codex {self._forest_codex_label()} | Exit {door} | Gen {state.generation}",
            )
        if state.room.mechanism_missing is None:
            return self._tr(
                f"背包 {self.seed_inventory} | 图鉴 {self._forest_codex_label()} | 普通植物第 {state.generation} 代",
                f"Backpack {self.seed_inventory} | Codex {self._forest_codex_label()} | Ordinary gen {state.generation}",
            )
        if state.mechanism_active:
            return self._tr(
                f"背包 {self.seed_inventory} | 图鉴 {self._forest_codex_label()} | 机关第 {state.generation} 代",
                f"Backpack {self.seed_inventory} | Codex {self._forest_codex_label()} | Mechanism gen {state.generation}",
            )
        if state.carrying_seed:
            return self._tr(
                f"背包 {self.seed_inventory} | 携带种子：站到缺口按 P",
                f"Backpack {self.seed_inventory} | Carrying seed: stand on the gap and press P.",
            )
        return self._tr(
            f"背包 {self.seed_inventory} | 机关植物休眠：先拾起缺失种子",
            f"Backpack {self.seed_inventory} | Mechanism sleeps: pick up the missing seed.",
        )

    def _draw_forest_board(self, board: pygame.Rect, tile: int) -> None:
        assert self.forest_state is not None
        state = self.forest_state
        room = state.room
        pygame.draw.rect(self.screen, (9, 23, 23), board.inflate(24, 24), border_radius=16)
        pygame.draw.rect(self.screen, (54, 91, 61), board.inflate(14, 14), width=3, border_radius=14)
        for y in range(room.height):
            for x in range(room.width):
                point = (x, y)
                rect = self._formal_tile_rect(board, point)
                floor = (22, 58, 43) if (x + y) % 2 == 0 else (18, 49, 39)
                pygame.draw.rect(self.screen, floor, rect, border_radius=4)
                pygame.draw.rect(self.screen, (37, 78, 54), rect, width=1, border_radius=4)
                if x in (0, room.width - 1) or y in (0, room.height - 1):
                    edge = pygame.Surface(rect.size, pygame.SRCALPHA)
                    edge.fill((8, 20, 18, 54))
                    self.screen.blit(edge, rect.topleft)
                if point in room.stone_cells:
                    pygame.draw.rect(self.screen, (74, 76, 75), rect.inflate(-5, -5), border_radius=5)
                    pygame.draw.rect(self.screen, (142, 145, 139), rect.inflate(-9, -9), width=2, border_radius=5)
                if point in room.button_cells:
                    pressed = point in state.ordinary_plants or point in state.mechanism_plants
                    color = BUD if pressed else DANGER
                    pygame.draw.circle(self.screen, color, rect.center, max(6, rect.width // 4), width=3)
                if point == room.exit_cell:
                    color = BUD if state.door_open else DANGER
                    pygame.draw.rect(self.screen, color, rect.inflate(-8, -8), width=3, border_radius=7)
                if point == room.receiver_cell:
                    pygame.draw.circle(self.screen, GOLD if state.door_open else TEXT_MUTED, rect.center, max(5, rect.width // 5), width=3)
                if state.ordinary_seed_cells is not None and point in state.ordinary_seed_cells:
                    pygame.draw.circle(self.screen, BUD, rect.center, max(5, rect.width // 5))
                    pygame.draw.circle(self.screen, BUD_CORE, rect.center, max(2, rect.width // 10))
                if point == state.seed_cell:
                    pygame.draw.circle(self.screen, GOLD, rect.center, max(5, rect.width // 5))
                    pygame.draw.circle(self.screen, LANTERN_CORE, rect.center, max(2, rect.width // 10))
                if point == room.mechanism_missing and not state.mechanism_active:
                    pygame.draw.rect(self.screen, GOLD, rect.inflate(-10, -10), width=2, border_radius=6)
                if point in state.ordinary_plants:
                    self._draw_bud(rect, False, point in self.bloomed)
                elif point in state.mechanism_plants:
                    self._draw_mechanism_bloom(rect, point in self.bloomed, state.mechanism_active)
                elif point in self.faded and self.flash_timer > 0:
                    pygame.draw.circle(self.screen, (74, 111, 87), rect.center, max(3, tile // 6))
        player_rect = self._formal_tile_rect(board, state.player)
        self._draw_bud(player_rect, True, False)
        if state.carrying_seed:
            pygame.draw.circle(self.screen, GOLD, (player_rect.right - 10, player_rect.top + 10), max(4, player_rect.width // 10))

    def _draw_mechanism_bloom(self, rect: pygame.Rect, newly_bloomed: bool, active: bool) -> None:
        color = GOLD if active else (113, 116, 122)
        core = LANTERN_CORE if active else (161, 164, 167)
        if newly_bloomed and self.flash_timer > 0:
            color = BUD_CORE
        glow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*color, 36 if active else 18), glow.get_rect().center, max(6, rect.width // 3))
        self.screen.blit(glow, rect.topleft)
        pygame.draw.polygon(
            self.screen,
            color,
            (
                (rect.centerx, rect.top + rect.height // 5),
                (rect.right - rect.width // 5, rect.centery),
                (rect.centerx, rect.bottom - rect.height // 5),
                (rect.left + rect.width // 5, rect.centery),
            ),
        )
        pygame.draw.circle(self.screen, core, rect.center, max(3, rect.width // 9))

    def _draw_settings(self) -> None:
        veil = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        veil.fill((5, 8, 14, 170))
        self.screen.blit(veil, (0, 0))
        panel = self._settings_panel_rect()
        if self.setting_panel is not None:
            self.screen.blit(self.setting_panel, panel)
        else:
            self._rounded_panel(panel, active=False)
        self._text(self._tr("设置", "SETTINGS"), self.fonts["h1"], TEXT, (panel.x + 78, panel.y + 64))
        self._text(self._tr("窗口大小", "WINDOW SIZE"), self.fonts["body"], TEXT_MUTED, (panel.x + 64, panel.y + 110))
        for size, rect in zip(WINDOW_SIZES, self._settings_size_rects()):
            self._rounded_panel(rect, active=size == self.window_size)
            self._text(f"{size[0]} x {size[1]}", self.fonts["small"], TEXT, (rect.x + 13, rect.y + 14))
        self._text(self._tr("语言", "LANGUAGE"), self.fonts["body"], TEXT_MUTED, (panel.x + 64, panel.y + 214))
        for language, rect, label in zip(("zh", "en"), self._settings_language_rects(), ("简体中文", "English")):
            self._rounded_panel(rect, active=self.language == language)
            self._text(label, self.fonts["small"], TEXT, (rect.x + 28, rect.y + 11))
        self._text(self._tr("音量", "VOLUME"), self.fonts["body"], TEXT_MUTED, (panel.x + 64, panel.y + 304))
        minus_rect, plus_rect, mute = self._settings_volume_rects()
        for rect, label in ((minus_rect, "-"), (plus_rect, "+")):
            self._rounded_panel(rect, active=False)
            self._text(label, self.fonts["h2"], TEXT, (rect.x + 19, rect.y + 10))
        self._text(f"{int(self.audio.volume * 100):03d}%", self.fonts["stat"], TEXT, (panel.x + 180, panel.y + 337))
        self._rounded_panel(mute, active=not self.audio.enabled)
        self._text(
            self._tr("静音" if self.audio.enabled else "已静音", "MUTE" if self.audio.enabled else "MUTED"),
            self.fonts["body"], TEXT, (mute.x + 27, mute.y + 13)
        )
        if self._settings_has_level_exit():
            self._draw_wrapped_text(
                self._tr(
                    "退出关卡后，下次将从当前房间开始。",
                    "Exit the level; next time starts from this room.",
                ),
                self.fonts["small"],
                TEXT_MUTED,
                pygame.Rect(panel.x + 66, panel.y + 362, 420, 22),
                20,
            )
        close, exit_level, quit_button = self._settings_action_rects()
        self._rounded_panel(close, active=True)
        self._text(self._tr("返回", "BACK"), self.fonts["h2"], CYAN, (close.x + 40, close.y + 11))
        if exit_level is not None:
            self._rounded_panel(exit_level, active=False)
            self._text(
                self._tr("退出关卡", "EXIT LEVEL"),
                self.fonts["small"],
                GOLD,
                (exit_level.x + 37, exit_level.y + 14),
            )
        self._rounded_panel(quit_button, active=False)
        self._text(
            self._tr("退出游戏", "QUIT"),
            self.fonts["small"] if exit_level is not None else self.fonts["h2"],
            DANGER,
            (quit_button.x + (43 if exit_level is not None else 56), quit_button.y + (14 if exit_level is not None else 11)),
        )

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
