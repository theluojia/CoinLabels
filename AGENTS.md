# 标签项目 agent 入口

开始任何新建、修改或检查任务，先读根目录 `README.md`、`docs/DESIGN_RULES.md` 和 `docs/PROGRESS.md` 最后一项。以用户当前要求为优先。查主题时同时核对 `data/catalog.json`、`data/pdf_text.json`／`data/overrides.json` 与 `coins/<ID>_f.webp`；不要凭文件名猜图案。保持同系列色系与绘画语言，正面主景右置，背面中间留白。新增或替换图片后运行 `python scripts/validate_labels.py`。完成一轮工作即更新 `docs/PROGRESS.md`，明确已完成与待做事项。
