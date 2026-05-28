# 萤光花园 / Lumen Garden

《萤光花园》是一款以康威生命游戏为底层规则的回合制箱庭解谜原型。玩家扮演一只迷路的小灯灵，在夜色遗迹与荧光森林中观察植物的生长、死亡与移动图案，逐步学会用普通植物和机关植物打开道路，最终回到灯漫村。

当前版本已进入 **Phase 2 第一章**：首页入口改为 `教程 / 荧光森林 / 荧光花园 / 设置`，主线先验证三房间线性迷宫、开场漫画、结尾漫画、静态规则页和设置弹窗流程。Phase 1 的花园谜题与种植花谱代码仍保留为规则资产和回归测试基础，但不再作为首页主入口。

## 当前版本

- `教程`：静态生命游戏规则页，使用 `assets/sprites/tutorial_menu.png` 作为底图，只展示基础生死规则和小棋盘示意。
- `荧光森林`：第一章剧情模式。进入后先显示 `Introduction_1.png` 开场漫画，再依次通过普通植物房、机关植物房和混合房。
- `荧光花园`：当前为占位入口，使用 `garden.png` 作为底图；通关第一章后会显示解锁回报，后续将扩展为大本营、花谱和自由种植空间。
- `设置`：使用 `setting.png` 弹窗。首页按 `Esc` 会打开设置，不会直接退出；关卡中按 `Esc` 也打开设置，并提供退出关卡选项。
- 第一章结尾：第三个房间出口触发 `end_1.png` 结尾漫画，随后进入荧光花园解锁提示。
- 规则分层：普通植物每次灯灵行动都会演化；机关植物未启动前休眠，补齐并启动后才随行动演化。
- 保留 Phase 1 的纯 Python 规则层、经典图案数据、种植验证、回归测试和旧菜单方法，便于继续作为谜题搜索、机制验证和后续花谱玩法基础。

## 运行

推荐使用当前机器上的 Anaconda Python：

```powershell
cd D:\ProgramScripts\Lumen_Garden
& 'D:\ProgramData\Anaconda3\python.exe' -m pip install -r requirements.txt
& 'D:\ProgramData\Anaconda3\python.exe' main.py
```

## 控制

| 场景 | 操作 |
| --- | --- |
| 首页 | 鼠标点击入口；方向键或 `W/S` 切换；`Enter` / `Space` 确认 |
| 首页快捷键 | `G` / `T` / `0` 打开教程，`F` 进入荧光森林，`P` 打开荧光花园占位页，`Esc` 打开设置 |
| 教程 | 点击 `返回主页` 或按 `Esc` 返回首页 |
| 开场 / 结尾漫画 | 点击、`Enter` 或 `Space` 继续；开场漫画按 `Esc` 返回首页 |
| 荧光森林 | `W/A/S/D` 或方向键移动灯灵，`Space` 等待一回合 |
| 荧光森林机关 | 拾取流光种后站到缺口，按 `P` 补齐并启动机关植物 |
| 荧光森林关卡 | `R` 重试当前房间，`Esc` 打开设置 |
| 设置 | 点击按钮调整窗口大小、语言、音量、静音、返回、退出关卡或退出游戏 |

## 验证

回归测试覆盖 Phase 1 规则与种植验证、Phase 2 首页入口、静态教程、剧情漫画、三房间森林流程、设置弹窗和无窗口 UI smoke tests：

```powershell
& 'D:\ProgramData\Anaconda3\python.exe' -m unittest discover -s tests -v
```

## 项目结构

```text
main.py                    启动入口
Lumen_Garden/
  app.py                   pygame 场景、输入、绘制、Phase 2 森林流程
  audio.py                 可选 BGM/SFX 加载与播放
  model.py                 Phase 1 花园谜题与种植验证规则核心
  patterns.py              经典生命图案与种植花谱数据
  puzzles.py               Phase 1 花园谜题数据
  tutorial.py              Phase 1 互动入门数据
assets/
  sprites/                 首页、教程、漫画、设置、棋盘与角色素材
  music/                   可选背景音乐
  sfx/                     可选音效
docs/
  phase-1/                 已归档的原型设计文档
  phase-2/                 第一章设计与房间机制文档
harness/
  phase-1/                 Phase 1 已执行提示词
  phase-2/                 Phase 2 执行提示词
tests/                     规则、种植和 UI smoke tests
```

## 素材接口

当前运行已接入的关键图片位于 `assets/sprites/`：

```text
menu.png
tutorial_menu.png
Introduction_1.png
end_1.png
setting.png
garden.png
guide_puzzle.png
flower_board.png
lantern_board_idle.png
```

音频接口见 [assets/README.md](assets/README.md)。缺失音频时游戏会静音运行。

## 设计文档

阶段文档从 [docs/README.md](docs/README.md) 进入：

- [Phase 2 总览](docs/phase-2/README.md)
- [Phase 2 第一章设计总纲](docs/phase-2/chapter-one-design.md)
- [房间与机制规范](docs/phase-2/room-and-mechanism-design.md)
- [Phase 1 原型归档](docs/phase-1/README.md)
- [Harness 执行记录](harness/README.md)
