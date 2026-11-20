# 二维码

已依据中国印钞造币集团官网普通纪念币目录 `index.html` 至 `index_20.html` 核对并生成 138 枚专属二维码。`JB120`（海南热带雨林国家公园）未在指定的 21 页目录找到唯一详情页，暂用 `qr/fallback.png`，指向官方普通纪念币目录 `https://www.cbpm.cn/cn/rmbpic/rmbpic6/`。以后缺少专属 PNG 的编号也会自动使用此兜底码；当前清单见 `qr/FALLBACK.md`。

每枚的目标网址与匹配证据见 `qr/links.json`，官网目录和图片文件名的抓取记录见 `qr/cbpm_audit.json`。二维码为方形 PNG、H 级容错、四模块静区，按背面标签预留栏生成 359 × 359 像素。`scripts/scan_cbpm.py` 可重新抓取目录，`scripts/generate_verified_qr.py` 可从核对记录重建 PNG 并刷新 `qr/FALLBACK.md`。补齐 `qr/JB120.png` 后重新生成标签即可自动换成专属码。以上路径均以 `label/` 为起点。
