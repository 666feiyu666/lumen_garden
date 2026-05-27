# 《萤光花园》美术概念图 Prompts

## 当前方向

本项目已停止使用“培养皿 / 变异细胞 / 生物实验”作为视觉方向。当前主方案为 **萤光花园 / Lumen Garden**：月夜花圃中，一枚金色灯灵引导青绿花芽盛放。**星图守望 / Starwatch** 保留为未来可能的替代主题，见 [戏剧方向决策](narrative-directions.md)。

概念图用于确定情绪、布局和素材语言；中文、数字、按钮与状态提示应继续由程序清晰绘制。

## 正式目标确认

2026-05-27 确认：当前所选核心谜题概念图即为正式游戏画面的视觉目标，而不是只用于寻找另一种风格的草图。最终游戏应逼近其中的月夜花园背景、左侧深色 `10 x 10` 花圃、右侧木框羊皮纸手记面板、薄荷荧光花与暖金灯灵关系。

实现上仍需要将目标画面拆为可加载资产：背景、花圃表面/边框、空白 HUD 面板、按钮皮肤、灯灵和植物精灵分别生成，由程序叠加动态文字、数字、单位状态、点击反馈和动画。这样既忠于概念图，也不会失去交互能力。

当前美术生产路线为绘本精灵风；像素风仅作为未来在小尺寸可读性验证失败时的对照备选，不作为本轮主路线。

## 统一要求

- 画幅：`16:9`，按 `1280 x 720` PC 横屏界面构图。
- 情绪：安静、温暖、有一点童话感，但不幼稚。
- 配色：靛蓝月夜、鼠尾草绿花圃、薄荷绿花芽、暖金灯灵、奶白文字空间。
- 可玩性：棋盘格与单位必须清楚，背景纹理不能干扰 HUD。
- 排除：细胞、病毒、培养皿、医疗设备、实验室、生物恐怖、可读文字、数字、水印。

## 风格锚点

```text
Visual language: a gentle moonlit puzzle garden, deep indigo night, soft stone
planting tiles, sage and moss foliage, small mint-green glowing flower buds, one warm
golden lantern spirit that feels friendly and magical, drifting fireflies and dew,
quiet handcrafted indie game UI, poetic but highly readable, no biology, no laboratory,
no horror, no readable text, no numbers, no watermark.
```

## Prompt 1：简洁主菜单 / 模式入口

```text
Create a high-fidelity main menu concept for a cozy turn-based puzzle game called
Lumen Garden. 16:9 PC layout, 1280x720. A peaceful moonlit garden fills the scene:
indigo sky tones, softly layered grasses, rounded stepping stones, tiny mint-green
glowing flower buds, and a few golden fireflies. Keep a large calm title-safe space in
the upper-left. Below it arrange three spacious, immediately clickable menu actions:
one for guided garden play, one for planting classic patterns, and one smaller settings
action. Do not show a level list on this first screen. On the right place a quiet
decorative garden vignette or compact notebook panel describing the two ways to tend
the garden. A tiny floating golden lantern spirit rests near a flower path.
Readable game composition, gentle handcrafted detail, no text, no numbers, no logo,
no petri dish, no cells, no laboratory, no horror, no watermark.

Visual language: a gentle moonlit puzzle garden, deep indigo night, soft stone
planting tiles, sage and moss foliage, small mint-green glowing flower buds, one warm
golden lantern spirit that feels friendly and magical, drifting fireflies and dew,
quiet handcrafted indie game UI, poetic but highly readable, no biology, no laboratory,
no horror, no readable text, no numbers, no watermark.
```

## Prompt 2：核心谜题界面 / 花圃与手记

```text
Create a gameplay screen concept for Lumen Garden, a cozy grid-based puzzle game,
16:9, 1280x720. On the left show a large square garden bed divided into clean rounded
stone-and-soil planting tiles, 10 by 10, readable as a tactical grid. Several
tiles contain small mint-green luminous flower buds with simple petal silhouettes.
One tile contains a distinct warm golden floating lantern spirit, inviting and clearly
not a flower. A few buds are newly blooming with soft pale-green sparkle; one fading
bud leaves a gentle scattering of petals. On the right build a spacious garden-journal
HUD panel with blank regions for blooming count, bloom goal, steps until dawn, growth
cycle, status and controls. Moonlight, dew and subtle fireflies may enrich the edges,
but the puzzle board remains clear. No text, no numbers, no biology, no laboratory,
no horror, no watermark.

Visual language: a gentle moonlit puzzle garden, deep indigo night, soft stone
planting tiles, sage and moss foliage, small mint-green glowing flower buds, one warm
golden lantern spirit that feels friendly and magical, drifting fireflies and dew,
quiet handcrafted indie game UI, poetic but highly readable, no biology, no laboratory,
no horror, no readable text, no numbers, no watermark.
```

## Prompt 3：月夜入门 / 教学画面

```text
Design a tutorial screen for Lumen Garden, a welcoming puzzle game about guiding
glowing flower buds. 16:9 PC interface. On the left is an enlarged 5 by 5 garden plot
made of soft stone planting tiles. Highlight one empty soil tile with a warm outline;
three nearby mint-green buds shine toward it with thin gentle rays, indicating a bud
can bloom there. A small golden lantern spirit waits nearby. On the right is an airy
garden journal panel with empty blocks for two lines of instruction, a highlighted
action prompt and simple step dots made only from shapes. The mood is reassuring,
curious and understandable for a first-time player. No text, no numbers, no laboratory,
no cells, no medical imagery, no watermark.
```

## Prompt 4：谜题解开画面

```text
Create a victory overlay concept for Lumen Garden. The garden puzzle board remains
softly visible beneath a translucent indigo veil. A balanced cluster of mint-green
flowers is gently in bloom and the golden lantern spirit hovers nearby. Center a clear
empty area for a later program-rendered message. Add restrained drifting petals,
fireflies and the first suggestion of warm dawn light at the horizon. Quiet joy, not
an explosive celebration. No text, no numbers, no biology, no horror, no watermark.
```

## Prompt 5：花芽与灯灵素材探索板

```text
Create a clean character-and-effect exploration sheet for a cozy puzzle game named
Lumen Garden on a flat dark indigo background. Show isolated sprite-like designs:
a small closed mint-green glowing bud, a fully blooming five-petal bud, a newly
sprouting bud with gentle sparkles, a fading flower releasing soft petals, and a warm
golden lantern spirit with a simple floating glow and friendly silhouette. Designs
must remain recognizable at small game-token size and avoid faces unless extremely
subtle. Add tiny examples of firefly particles and moonlit ripple glows. No UI, no
text, no biology, no horror, no watermark.
```

## Prompt 6：无 UI 月夜背景

```text
Create a text-free 16:9 background plate for a cozy puzzle game's menu. A moonlit
garden path with deep indigo shadows, soft moss and low grass, rounded stones, sparse
mint-green bud glows near the far edges and a handful of warm golden fireflies. Keep
the left-center and right-panel zones very low contrast and open for UI overlay.
Peaceful, poetic, clean, no characters in the foreground, no interface, no text,
no laboratory, no horror, no watermark.
```

## 正式素材生产提示词

以下提示词用于将已确认的核心谜题概念图拆成真正可进入游戏的资产。生成时将所选概念图作为 `Image 1` 上传，并在每次提示中保留它的角色说明：`Image 1 is the approved final visual target and style reference; match its mood, materials, palette and handcrafted painterly finish.`

所有图像只生成视觉资产，不生成可读文字、数字或水印。透明精灵优先输出纯色抠图底：金色物体使用 `#00ff00`；绿色花朵使用 `#ff00ff`。最终游戏资产转换为透明 `PNG/RGBA`。每一个目标文件单独发起一次生成请求；段落中列出多个文件时，使用同一风格约束分别生成，不将不同最终资产拼成一张素材板再切割。

### P0：灯灵变体补绘

目标文件：`assets/sprites/lantern_portrait_idle.png`、`assets/sprites/lantern_board_idle.png`

```text
Use case: stylized-concept
Asset type: isolated character sprite variants for a 2D puzzle game
Input images: Image 1 is the approved final gameplay visual target and style reference.
If an existing lantern sprite is supplied as Image 2, preserve its character identity.

Create exactly one sprite of the same friendly golden lantern spirit from Lumen
Garden. For `lantern_portrait_idle.png`, use a front-facing portrait idle pose for
menu and tutorial scenes. For `lantern_board_idle.png`, use a compact high-angle
board-view idle pose for occupying a single garden tile. Preserve the small curled
flame tip, warm teardrop-shaped inner light, simple gentle eyes and quiet magical
personality seen in the approved concept. When generating the board view, it must
remain readable when reduced to about 48 pixels tall and must leave a flower beneath
it visually detectable.

Composition: one isolated full character, centered on a square working canvas with
generous padding.
Backdrop: perfectly flat solid #00ff00 chroma-key background for background removal.
Constraints: no scenery, no soil tiles, no text, no shadow, no broad outer halo,
no additional characters, no watermark.
```

### P1：核心谜题背景板

目标文件：`assets/ui/gameplay_background.png`

```text
Use case: stylized-concept
Asset type: 16:9 gameplay environment background plate for a 2D puzzle game
Input images: Image 1 is the approved final visual target and style reference; match
its moonlit enchanted garden atmosphere, palette, materials and painterly finish.

Create the environment layer behind the interactive gameplay screen for Lumen Garden.
A deep indigo moonlit garden at night, a full moon above a quiet stone path in the
center distance, dense vines and tiny flowers around the edges, warm garden lantern
light near the lower corners, sparse fireflies, rich handcrafted storybook painting.

Composition: 1280 by 720 landscape. Reserve a large calm rectangular zone on the left
for a 10 by 10 garden board, and a large calm rectangular zone on the right for a
wood-framed journal HUD. Keep these two overlay zones dark and low-detail enough for
interactive assets and program-rendered text to remain readable. Preserve the lush
garden framing around them and the moonlit path visible between them.

Constraints: background environment only; do not draw the board grid, HUD panel,
buttons, character, flowers placed on tiles, text, numbers, logo or watermark.
```

### P2：空花圃外框与土格风格

目标文件：`assets/ui/board_frame_reference.png` 与后续单格纹理参考

```text
Use case: stylized-concept
Asset type: empty interactive garden board visual reference
Input images: Image 1 is the approved final visual target and style reference.

Create an empty front-facing square garden board for Lumen Garden, matching the left
board in Image 1: a handcrafted wooden and stone outer frame overgrown with restrained
ivy, holding a perfectly readable 10 by 10 array of empty dark soil planting tiles.
Each tile has a rounded stone rim and deep brown earth center, with subtle moonlit
highlights and no distracting texture.

Composition: isolated board, straight-on view, square, centered, all ten columns and
ten rows clearly separated and equally sized. The board must remain suitable for
placing dynamic character and flower sprites on top.

Constraints: empty tiles only; no lantern spirit, no flower, no petals, no interaction
markers, no scenery behind the board, no text, no numbers, no watermark.
```

说明：图片模型若无法稳定保持精确 `10 x 10`，该图只作为框体和土格质感参考；正式交互棋盘继续由程序用单格/边框资产构造。

### P3：右侧花园手记空白面板

目标文件：`assets/ui/journal_panel_blank.png`

```text
Use case: stylized-concept
Asset type: blank HUD panel skin for a 2D puzzle game
Input images: Image 1 is the approved final visual target and style reference.

Create the right-side blank garden journal HUD panel from the approved Lumen Garden
gameplay screen: a tall warm wooden frame with soft vine details and a hanging golden
lantern accent, containing layered cream parchment areas for title, statistics,
status text and bottom controls. Elegant engraved botanical corner ornaments, gentle
warm highlights, handcrafted storybook quality.

Composition: tall rectangular isolated UI panel, front-facing, matching the relative
shape of the panel in Image 1. Keep all parchment fields spacious, plain and low
contrast so Chinese text and numbers can be drawn on top by the game.

Backdrop: perfectly flat solid #00ff00 chroma-key background for background removal.
Constraints: completely blank panel; no readable text, no numbers, no icons that look
like labels, no button wording, no watermark, no broad shadow outside the panel.
```

### P4：按钮与卡片皮肤

目标文件：`assets/ui/button_idle.png`、`button_hover.png`、`card_blank.png`

```text
Use case: stylized-concept
Asset type: blank UI control skin exploration sheet
Input images: Image 1 is the approved final visual target and style reference.

Create exactly one blank interface component matching the wooden and parchment garden
journal style in Image 1. Generate one requested target per image: a wide idle button,
a gently golden-highlighted hover button, a selected button, or a blank puzzle card
frame. Warm cream parchment center, dark carved wood or bronze edging, restrained leaf
engravings, clear readable center.

Composition: one isolated component centered with generous space on a perfectly flat
solid #00ff00 chroma-key background. All separately generated button variants must
preserve identical dimensions and padding from the idle button reference.

Constraints: no text, no numbers, no logos, no complex decoration in the text area,
no watermark, no cast shadows beyond compact component edges.
```

### P5：花苞精灵

目标文件：`assets/sprites/bud_planted.png`

```text
Use case: stylized-concept
Asset type: isolated board sprite for a 2D puzzle game
Input images: Image 1 is the approved final visual target and style reference.

Create one closed mint-green luminous flower bud matching the flowers on the approved
Lumen Garden board. A delicate closed bud with two small dark green leaves, soft inner
moonlit glow, clean silhouette, painterly handcrafted finish. It must be clearly
readable when reduced to about 38 pixels tall on a dark soil tile.

Composition: single centered plant, front-facing with a slightly elevated board-token
view, square canvas, generous padding.
Backdrop: perfectly flat solid #ff00ff chroma-key background for background removal.
Constraints: no soil tile, no scenery, no text, no gold colors that confuse it with
the lantern spirit, compact glow only, no large haze, no watermark.
```

### P6：盛开花精灵

目标文件：`assets/sprites/bloom_open.png`

```text
Use case: stylized-concept
Asset type: isolated board sprite for a 2D puzzle game
Input images: Image 1 is the approved final visual target and style reference.

Create one fully opened mint-green luminous garden flower matching the blooming
flowers in Image 1. Five soft petals around a pale glowing center, small supporting
leaves, elegant and calm, visibly more open and brighter than the closed bud. Strong
simple silhouette readable when reduced to about 40 pixels tall on a dark soil tile.

Composition: single centered flower, front-facing with a slight elevated token view,
square canvas, generous padding.
Backdrop: perfectly flat solid #ff00ff chroma-key background for background removal.
Constraints: no soil tile, no additional loose petals, no scenery, no text, no broad
outer halo, no watermark.
```

### P7：衰退花与花瓣精灵

目标文件：`assets/sprites/bloom_fading.png`、`assets/sprites/petal.png`

```text
Use case: stylized-concept
Asset type: isolated fading-state board sprite and petal accent
Input images: Image 1 is the approved final visual target and style reference.

Create exactly one requested asset per image. For `bloom_fading.png`, create a fading
version of the same mint-green luminous flower: the bloom tilts slightly, its glow is
softer, and two or three petals are just releasing from the flower, communicating
disappearance without looking damaged or sad. For `petal.png`, create one separate
small loose mint-green petal for later particle animation. Retain the same flower
identity and scale relationship as the open bloom sprite.

Composition: one isolated requested asset centered on a square canvas with generous padding.
Backdrop: perfectly flat solid #ff00ff chroma-key background for background removal.
Constraints: no soil tile, no scenery, no text, no horror or decay, no watermark.
```

### P8：主菜单同世界背景

目标文件：`assets/ui/menu_background.png`

```text
Use case: stylized-concept
Asset type: main menu background plate for a 2D puzzle game
Input images: Image 1 is the approved final gameplay visual target and style reference.

Create a main menu environment in exactly the same Lumen Garden world as Image 1:
a peaceful moonlit garden path, full moon, indigo foliage, tiny mint flower lights,
warm lanterns, ivy-covered wooden structures and gentle fireflies. The scene should
feel like the quiet entrance to the same garden shown in gameplay.

Composition: 1280 by 720 landscape. Keep a broad calm area on the left for the game
title and menu buttons, and a quieter decorative space on the right for optional
summary content or a large front-facing golden lantern spirit.

Constraints: environment only; no menu buttons drawn in, no character in the
foreground, no text, no numbers, no logo, no watermark.
```

## 生成验收顺序

1. 以现有灯灵素材为角色锚点，先生成 `P5-P7` 花朵状态，验证棋盘小尺寸可读性。
2. 生成 `P2` 花圃外观与 `P3` 手记面板，使单屏组合开始接近最终概念图。
3. 生成 `P1` gameplay 背景板，并与动态棋盘/HUD 组合检查明暗层次。
4. 生成 `P4` 与 `P8`，补齐菜单和操作层美术。
5. 所有候选素材以程序实际绘制的 `10 x 10` 花圃叠放结果为验收对象，不以单独大图的观感替代可玩性检查。

## 保留探索：星图守望

仅在需要比较另一种情绪时生成，不作为当前版本制作基准：

```text
Create a gameplay concept for a tranquil puzzle game called Starwatch. 16:9 PC
interface. A clear grid of faint constellation lines appears in a velvety midnight
sky on the left, populated by small soft-blue stars and one warm golden guiding star.
On the right is a minimal stargazer's chart panel with blank spaces for puzzle stats.
Elegant, quiet, celestial, readable, no text, no numbers, no science laboratory,
no horror, no watermark.
```

## 筛选标准

| 维度 | 通过标准 |
| --- | --- |
| 情绪 | 看起来温暖、安静、愿意靠近，不产生医疗或恐怖联想 |
| 可读性 | 灯灵与花芽在最小棋盘显示尺寸下仍可立即区分 |
| 谜题感 | 格子、状态和操作区域清楚，视觉不遮蔽判断 |
| 可落地 | 可拆为背景、面板、土格、花芽、灯灵与粒子素材 |
| 一致性 | 菜单、谜题、入门和结算像同一个月夜花园世界 |
