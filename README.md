# 萤光花园 / Lumen Garden

《萤光花园》是一款 `pygame` 回合制规则解谜原型。玩家引导一枚金色灯灵，在黎明前让月夜花圃中的绿色花芽达到目标盛开数量。当前第一册关卡以统一花圃规格，让难度来自微光介入的时机与路线。

## 当前版本

- 保留康威规则骨架：不会熄灭的金色灯灵、依邻近微光生长的花芽、合法移动与 `WAIT`、黎明时的盛开目标结算。
- 搭载五则 `10 x 10` 正式花园谜题及其参考解法；棋盘不再通过逐关扩大制造难度。
- 提供 `00 GUIDE` 月夜入门，演示熄灭、相伴、萌芽和灯灵引路。
- 提供 `10 x 10` 的种植花谱第一册：`BLOCK`、`BLINKER`、`BEACON`、`GLIDER` 与 `LWSS` 五关；灯灵以明确的播种动作补全花谱，确认后花圃自动播放纯康威规则验证，成功后可循环回看安全片段。
- 提供简洁主菜单、分模式选择页、设置弹窗、花园记录 HUD、花芽生长反馈和谜题结算界面。
- 支持鼠标导航与游玩；设置弹窗可切换窗口尺寸、调节音量并静音。
- 游戏场景不接收文本输入，已关闭输入法文本合成以避免 `P` / `X` / `WASD` 热键被占用。
- 音频接口已接入；没有素材文件时保持静音运行，添加约定文件后自动播放。
- 纯 Python 规则层与回归测试独立于 `pygame`，可继续支持谜题搜索、平衡测试或未来引擎迁移。

## 运行

推荐使用当前机器上已有的 Anaconda Python：

```powershell
cd D:\ProgramScripts\Lumen_Garden
& 'D:\ProgramData\Anaconda3\python.exe' -m pip install -r requirements.txt
& 'D:\ProgramData\Anaconda3\python.exe' main.py
```

## 控制

| 按键 | 功能 |
| --- | --- |
| 鼠标左键 | 选择模式/关卡、操作按钮；在花圃点击灯灵或相邻格行动 |
| `G` / `0` / `T` | 从主菜单进入花园引导选择页 |
| `P` | 从主菜单进入种植花谱选择页 |
| `1` 至 `5` | 在花园引导选择页直接开始谜题 |
| `Enter` / `Space` | 确认选中的模式或关卡 |
| `W/A/S/D` 或方向键 | 移动灯灵并生长一轮 |
| `Space` | 停留并生长一轮 |
| `R` | 重试当前谜题 |
| `Esc` | 对局中返回模式选择；模式选择返回主菜单；主菜单退出 |

月夜入门中按面板提示完成操作；演示结果出现后按 `Enter` 进入下一步，按 `R` 可重试当前指引。

在 `P01-P05` 种植花谱中，方向键或点击相邻土格只移动灯灵而不触发生长；按 `P` 或点击“播种”按钮种下花种，`X` / `Backspace` 或按钮撤回花种。花圃内点击灯灵不会播种或启动验证。花种未用完时，`Space` 与 `Enter` 只会提醒继续播种；花种用完后按 `Space` / `Enter` 或点击“开始”进入自动验证。验证时 `Space` 暂停/继续，`Enter` 单步查看；成功后会进入不改变判定的成谱演示，`Space` 暂停/继续，`Enter` 从片段开头重播。

## 验证

规则测试包含固定 `10 x 10` 关卡规范与五则参考解法、教程、经典图案纯规则行为、种植题成功/失败路径、显式播种防误触与成谱循环演示，以及 UI 无窗口烟雾测试：

```powershell
& 'D:\ProgramData\Anaconda3\python.exe' -m unittest discover -s tests -v
```

## 项目结构

```text
main.py                    启动入口
Lumen_Garden/
  app.py                   pygame 场景、绘制和输入
  audio.py                 可选 BGM/SFX 加载与播放
  patterns.py              经典图案与种植谜题数据
  puzzles.py               数据驱动谜题与已知解法
  tutorial.py              月夜入门步骤
  model.py                 自由演化与种植验证规则核心
assets/                    正式素材投放位置
tests/test_model.py        规则回归测试
tests/test_planting.py     经典行为与种植状态测试
tests/test_app_smoke.py    无窗口 UI 烟雾测试
```

## 美术与音乐接口

当前版本已转为程序绘制的月夜花园风格。后续素材可以增量替换：

- `assets/sprites/`：透明 PNG 花芽、灯灵、花瓣和萤火序列。
- `assets/ui/`：花园手记面板、谜题封面和标题视觉。
- `assets/fonts/`：具有授权的中文字体文件；任意 `.ttf`、`.otf` 或 `.ttc` 会被优先用于界面。
- `assets/music/menu.ogg`、`moon_garden.ogg`、`result.ogg`：循环背景音乐。
- `assets/sfx/*.wav`：灯灵移动、生长、拒绝、盛放与选择音效，具体文件名见 [assets/README.md](assets/README.md)。

正式扩展建议以 `model.py` 作为稳定玩法层，在其上增加新谜题、花园素材和进度存档，而不是把表现逻辑混入规则计算。

## 设计与制作文档

说明书、流程、美术概念图 prompts 与主题决策位于 [docs/README.md](docs/README.md)：

- [单页说明书](docs/one-page-manual.md)
- [十页说明书](docs/ten-page-manual.md)
- [游戏流程表](docs/game-flow.md)
- [游戏设计文档](docs/game-design-document.md)
- [月夜入门设计](docs/tutorial-level-design.md)
- [美术概念图 Prompts](docs/art-prompts.md)
- [戏剧方向决策](docs/narrative-directions.md)
- [Harness 执行记录](harness/README.md)
