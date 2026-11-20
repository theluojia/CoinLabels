# 纪念币鉴定盒标签

本目录可以独立复制到另一台电脑继续制作。本文件是唯一的接续入口；agent 先读 `AGENTS.md` 和 `docs/PROGRESS.md` 最新记录。当前覆盖 139 枚普通纪念币，按编号自然排序，从 JB01-1 到 JB126；正面 8252 共 3 页，背面 8240 共 4 页。每页从左到右、从上到下排列，最后一页剩余格子留空。

标签文字以原始 `sources/Label01.pdf` 为主要批量来源；PDF 未收录的 JB123—JB126 经用户明确指定，从网站 `coin_data.json` 补齐，并在 `data/overrides.json` 记录来源。当前 139 枚均有正反面背景。`qr/` 已有 138 枚经官网目录核对的专属二维码；JB120 尚未找到指定目录中的唯一详情页，暂用指向官方普通纪念币目录的 `qr/fallback.png`。

## 在线预览

启用 GitHub Pages 后，访问 [CoinLabels 在线标签总览](https://theluojia.github.io/CoinLabels/)；仓库根目录会跳转至 output/index.html。预览图随仓库发布，两份印刷 Word 仍从 [v0.1.0 Release](https://github.com/theluojia/CoinLabels/releases/tag/v0.1.0) 下载。

## 接续顺序

1. 看 `docs/PROGRESS.md` 最后一项，确定当前已完成、尚待核对的内容；画图前看 `docs/DESIGN_RULES.md`，专题细节看 `docs/BATCHES.md`。
2. 查一枚币时核对 `data/catalog.json`、`data/pdf_text.json`／`data/overrides.json`、`coins/<ID>_f.webp` 及现有正反背景。不要凭编号猜图案。
3. 修改背景后运行 `python scripts/normalize_backgrounds.py` 和 `python scripts/validate_labels.py`；再运行 `python scripts/generate_html.py`，检查 `output/index.html` 中的实际叠字图。
4. 确认后运行 `python scripts/generate_labels.py` 更新 Word，并在 `docs/PROGRESS.md` 记录编号、参考、检查结果与待办。照片等参考图保存在 `backgrounds/references/`。

## 文件和提交范围

| 路径 | 用途 |
| --- | --- |
| `sources/` | 原始 `Label01.pdf`、`ZY8252.docx`、`ZY8240.doc` 及转换后的 `ZY8240.docx`；保留原件和模板尺寸 |
| `data/` | `catalog.json` 编号、`pdf_text.json` 原文、`overrides.json` 修订、`series_colors.json` 系列文字色 |
| `coins/` | 139 枚币的 278 张透明 WebP；独立生成所需素材 |
| `backgrounds/front/` | 8252 正面背景，例如 `JB115.png` |
| `backgrounds/back/` | 8240 背面背景，与正面一一配套，例如 `JB115.png` |
| `backgrounds/prompts.json` | 已有背景的实际生成提示词和相对参考路径 |
| `qr/` | 138 枚专属二维码、官方目录兜底码、逐枚链接清单及 `FALLBACK.md` 缺项说明 |
| `scripts/` | HTML／Word 生成、尺寸校验、背景归一化及可选导入、PDF 提取、二维码核对脚本 |
| `docs/` | 设计规则、批次说明、二维码说明和逐轮进度 |
| `AGENTS.md` | agent 入口，指向本文件与最新进度 |
| `requirements.txt` | Python 依赖 |
| `output/` | 正式 Word、HTML 及其配套图、位置索引、字号报告 |

提交时保留上述文件，但 `output/*.docx` 不纳入 Git。正式 Word 从 [GitHub Releases](https://github.com/theluojia/CoinLabels/releases) 下载，也可以用 `scripts/generate_labels.py` 在本地重新生成。不要提交虚拟环境、缓存、临时 PDF／截图、旧样张和 Office 的 `~$` 锁文件；本目录 `.gitignore` 已屏蔽这些临时目录。

网站使用 `JB01-1`，原 PDF 印作 `JB001-1`：**文件名使用网站的规范 ID，标签上的编号统一显示三位数**。真实顺序号另列，如 JB115 对应 (128)，不能把 JB 数字直接当作顺序号。

## 换电脑后生成

需要 Python 3.10 或以上。不需要 Node，也不需要启动网站或标记平台。

在 `label` 目录打开终端，首次运行：

```sh
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\validate_labels.py
.\.venv\Scripts\python.exe scripts\generate_html.py
.\.venv\Scripts\python.exe scripts\generate_labels.py
```

WSL／Linux／macOS（第一条可用 `python3 -m venv .venv`）：

```sh
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/validate_labels.py
.venv/bin/python scripts/generate_html.py
.venv/bin/python scripts/generate_labels.py
```

脚本默认使用 Windows 微软雅黑，WSL 自动查找 `/mnt/c/Windows/Fonts`；Linux 可以使用 Noto Sans CJK。其他路径通过 `LABEL_FONT_REGULAR`、`LABEL_FONT_BOLD` 指定完整字体路径，也可以用 `LABEL_FONT_DIR` 指定包含 `msyh.ttc`、`msyhbd.ttc` 的目录。字体需由使用者合法安装，不随工程分发。字体不同可能改变断行，须重新核对。

以后只换背景或修改文字，先运行 `scripts/validate_labels.py`，再重新执行 `scripts/generate_html.py` 和 `scripts/generate_labels.py`。Word 可选 `--front-only` 或 `--back-only`。生成前关闭正在打开的输出 Word，避免文件占用。

输出：

- `output/labels_8252_front.docx`：正面，52 格／页。
- `output/labels_8240_back.docx`：背面，40 格／页。
- `output/index.json`：每枚币的正反面页码、标签行号、列号，背景和文字缺项。
- `output/layout_report.json`：背面描述字号及过密提示。
- `output/index.html` 与 `output/html_assets/`：139 枚按编号排列的正反面同屏预览，使用与 Word 相同的文字、币图和二维码渲染函数；本地打开 HTML 即可查看。

两个纸张型号的每页格数不同，**不是同一张纸正反套印**，应分别使用对应型号的预切标签纸。

## 文字来源和待补项

PDF 提取去掉重复绘制的文字层，按实体单元格读取，不按照 PDF 内部对象顺序拼接。保留原文、数字、单位、标点；描述只去掉原排版换行，标题保留换行意图。每条记录都带原始位置，便于回看。

当前 PDF 收录 135 枚，截止 JB122。JB123—JB126 的标题、规格、正反面描述已按用户授权从网站数据补齐，发行日期采用用户提供的数据。JB126 国名面继续使用用户指定文字：

> 国徽、国名、年号，辅以中国戏曲乐器图案

PDF 中 JB006-1 没有发行日期，输出同样留空。PDF 某些文字和数值与网站不同（例如早期建国币的发行量），JB01-1—JB122 仍按 PDF 保留，不自行纠正。PDF 的 JB006-2 为排球、JB006-3 为体操，与网站素材编号相反，因此 `data/overrides.json` 仅在本标签工程交换这两枚的素材引用，让文字与币图一致；网站文件不变。

补充新文字时修改 `data/overrides.json`，例如以下结构（示意，不要把占位内容当事实）：

```json
{
  "JB126": {
    "description2": "用户确认的国名面描述",
    "description": "用户确认的主题面描述",
    "release_date": "用户确认的日期",
    "front": {
      "header": "中华人民共和国普通纪念币",
      "title": "用户确认的币名\n副标题",
      "footer": "年份 ⦁ 材质 ⦁ 发行量 ⦁ 尺寸 ⦁ 面额"
    }
  }
}
```

修改时保留文件中其他已有条目。覆盖 `front` 时填写完整的三个字段。文本必须经过人工确认，不使用 AI 编造币面信息。`data/pdf_text.json` 是原始提取记录，日常修订优先写入 `data/overrides.json`，便于区分来源。

`extract_pdf_text.py` 针对当前 PDF 的前 3 页正面、后 4 页背面及原有圆角格子设计。换成结构不同的新 PDF 时需要先调整提取方式并核对，不能直接假定格式相同。

## 补背景和增加新币

现有 139 套正反背景。按文件名对应，**不依靠文件夹排序匹配**。背景修改后运行生成脚本，即可将新版图片写入 Word。

1. 将新正面背景放入 `backgrounds/front/<ID>.png`，背面放入 `backgrounds/back/<ID>.png`。支持 PNG、WebP、JPG；同编号只保留一种格式，优先使用 PNG。不要把文字、币图或二维码画进背景。
2. 先运行尺寸校验和 HTML 预览；确认后重新生成 Word。脚本自动检测背景，无需改排版代码或再导入网站数据。
3. 在 `output/index.json` 查找该编号的位置，检查两面是否匹配。

新增尚未登记的钱币，需先在 `data/catalog.json` 增加 `id`、`theme`、`diameter_mm`、`serial`，在 `coins/` 放置 `<ID>_f.webp` 和 `<ID>_b.webp`，再添加用户确认的文字到 `data/overrides.json`。保持 ID 唯一，序号连续。脚本按数字自然排序，不能按字符串排序。

若完整 myCoins 仓库也在旁边，可以执行 `python scripts/import_catalog.py`；其他位置用 `python scripts/import_catalog.py --source /path/to/myCoins`。它只更新编号、系列、图片缩放直径、顺序并复制币图，不从网站导入标题、发行量或正反面描述，也不改 PDF 文字和用户修订。独立复制本目录时，不必执行导入脚本。

## 背景图的设计要求

正面约 50 × 20mm，交付背景统一 **1983 × 793 像素**；背面约 49 × 25.5mm，交付背景统一 **1738 × 905 像素**。**最终物理尺寸始终以 Word 模板中的数值为准**，不要手工改成近似毫米数。生成工具输出的比例不一定符合要求，放入背景目录后须运行 `python scripts/normalize_backgrounds.py` 等比裁切到标准尺寸，并逐张检查。`scripts/generate_labels.py` 会拒绝尺寸不符的背景，避免静默拉伸。完整规范见 `docs/DESIGN_RULES.md`。

- 正面建议至少 1200 × 480 像素，背面至少 1200 × 625；更高分辨率可用。按目标比例完整创作，不能裁切竖版人物后丢失主体。正面不叠加币图，背景完成后直接替换浅色底。
- 整套采用温暖浅象牙纸纹、中国水彩和淡墨风格。正面主景在右侧约 38%，左侧约 60% 及底部规格区自然淡化、虚化；文字直接叠在背景上，不做专门文字框。
- 各币人物动作、服饰、花卉、装饰、动物和地貌应符合自己的主题。不能只替换脸谱而机械复用其他所有元素。
- 主体重要细节距离上、下、右边至少约 10%；外围只放能容忍裁切的底纹和枝叶，不做硬边框，不把关键细节压在刀线边缘。
- 背面必须使用**该枚正面图片作为图像参考**重新设计，保留相同纸纹、色温、颜料和特有装饰；可以移除人物、动物，地貌淡化。边缘装饰保留约 25–35% 对比度，中央约 85% 区域极淡，适合密集文字。
- 背面不能以一张系列通用纹理替代逐枚匹配，也不能淡化到全是无特点的米黄色。
- 不生成币图、文字、数字、边框、二维码。正面标签不叠加币图；背面真实币图由脚本叠加，避免 AI 改变币面内容。
- 生成后人工检查主题、配套关系和文字区；把最终图片及提示词放入工程，失败版本不用保留。

正面提示词示例：

> 为 [币的主题] 创作一张 2.5:1 横向满版鉴定盒标签背景。温暖浅象牙纸纹、中国水彩与淡墨；主题完整放在右侧 38%，重要细节离边缘至少 10%。左侧 60% 和底部文字区自然淡化、虚化，没有独立文字框。外围装饰允许裁切。无文字、数字、币图、二维码、硬边框。按此宽幅构图重新创作，不裁切竖图。

背面提示词示例（必须附同枚正面图作为参考）：

> 将这张正面图改成 1.92:1 横向背面底纹，明显是同一套画作的另一面。保留原纸纹、色温、笔触和该图特有的花卉／植被／地貌装饰。移除主景人物、动物，中央 85% 极淡柔化，边缘装饰约保留 25–35% 对比度。背景满铺并允许裁切，没有独立空白框，无文字、币图、二维码或边框，不要变成无特点的米黄色。

`backgrounds/prompts.json` 保存已记录背景的实际提示词；新版式和验收规则以 `docs/DESIGN_RULES.md` 为准。AI 图像工具只负责生成背景，Word 脚本不会自动调用图像生成服务。

## 单元格填充和背面排版

原模板是定位权威：页面尺寸、页边距、表格位置、列宽、行高、间隔行都不得改变。不能为了容纳内容扩大格子或缩小整张标签。

- 单元格四边内边距、段前段后、左右缩进均为零，顶部对齐，关闭文字网格吸附。
- 每格使用 600dpi 合成图，按单元格完整宽高放置。使用相对单元格段落原点的浮动锚点；不改成带基线留白的嵌入图片。
- 背景铺到四边；隐藏原表格的打印辅助边框。文字和重要图案保留安全距离。表格的自然页边距和行间隔保留，不属于单元格内留白。
- 正面标签不叠加币图；没有背景图时只显示文字和浅色底，后续放入对应背景文件后自动应用。
- 正反面统一字体，同系列用同一文字色。京剧 `#805141`，国家公园 `#365b46`；其他系列见 `data/series_colors.json`。
- 8240 上排为国名面（`_b.webp`、`description2`），下排为主题面（`_f.webp`、`description`）。当前只包含 JB 普通纪念币，不套用到纪念钞。
- 左侧币图去透明空边后按实际直径同比缩放：32mm 占标签高度 46%，其他直径乘以 `diameter/32`。保持币图自身宽高比，加轻微右下柔和阴影。
- 两排之间加系列色细横线，只覆盖币图和描述栏，不穿过二维码栏。
- 每段描述最多五行，不足五行时按实际文字整体垂直居中。同币两段字号一致，不截断文字。报告会标出偏小字号；应由用户确认简写文本后填入修订文件，不能随意改原 PDF 文案。
- 右侧二维码约占标签宽度 31%，包含完整静区；编号和真实顺序号使用系列色底白字，日期在其下方。编号框及日期位置经过上移，日期使用较大字号和浅色柔化底衬。
- 正面顶部“中华人民共和国普通纪念币”及底部规格参数都保持原字体、字号、文字颜色；各行底衬按实际文字宽度生成很淡的无边框纸色柔化区，不再在规格下方铺满整格横条。规格参数统一使用中文间隔点“·”分隔。
- 缺少 `qr/<ID>.png` 时自动使用 `qr/fallback.png`，目标为中国印钞造币集团普通纪念币目录；当前使用兜底码的编号见 `qr/FALLBACK.md`。核实专属详情页后放入 `qr/<ID>.png` 即可自动替换；保留至少四模块静区、方形比例，禁止平滑模糊缩放。

Word 每格是一张合成图，因此不是在 Word 内逐字编辑；改 JSON 后重生成。这样换电脑打开 Word 时不依赖已安装字体，生成阶段仍需要字体。

## 验收和打印

脚本对比每个表格的网格、行高、列宽和页面属性，并在保存后再次校验。检查 `output/index.json` 中是否有漏号、缺文字、缺背景；139 枚的序号应为 001–139。

生成后还要用 Word 或 WPS 打开，逐页核对预览：当前应为 3 页正面、4 页背面；首尾编号正确，格内四边满铺，币图不拉伸，文字不重叠、不超过五行，系列颜色和配套背景一致。必要时导出临时 PDF 放在 `.qa/` 检查，完成后删除。

打印用 A4、100%／实际大小，关闭“适应页面”“缩放至纸张”等设置。先以普通纸试打一页，与标签纸对光核对位置，再使用预切标签纸。
