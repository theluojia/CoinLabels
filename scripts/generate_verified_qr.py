"""Create high-correction coin QR PNGs and an official-catalog fallback.

Requires cbpm_audit.json from scan_cbpm.py. Unmatched coins remain without a
coin-specific PNG; links.json and FALLBACK.md record them for manual review.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
import json
import re
import unicodedata

from docx import Document
from PIL import Image, ImageDraw
from reportlab.graphics.barcode.qrencoder import QRCode, QRErrorCorrectLevel


LABEL = Path(__file__).resolve().parents[1]
QR_DIR = LABEL / "qr"
FALLBACK_URL = "https://www.cbpm.cn/cn/rmbpic/rmbpic6/"
EXPECTED_INDEX_TITLES = {
    "JB20": "第四十三届世界乒乓球锦标赛",
    "JB78": "环境保护（第一组）",
    "JB79": "上海世界博览会",
    "JB82": "环境保护（第二组）",
    "JB98": "2018年贺岁",
    "JB100": "改革开放40周年",
    "JB108-1": "第24届冬季奥林匹克运动会",
    "JB108-2": "第24届冬季奥林匹克运动会",
    "JB121": "中国人民抗日战争暨世界反法西斯战争胜利80周年",
    "JB122": "中国京剧艺术（净）",
    "JB123": "2026年贺岁",
    "JB124": "武夷山国家公园",
    "JB125": "江泽民诞辰100周年纪念币",
    "JB126": "中国京剧艺术（丑）",
}


def normalize_title(title: str) -> str:
    title = unicodedata.normalize("NFKC", title)
    title = re.sub(r"[（(][甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥][）)]$", "", title)
    title = re.sub(r"(?<=[生旦净丑])角", "", title)
    return re.sub(r"[^\w]", "", title)


def qr_size() -> int:
    cell = Document(LABEL / "sources" / "ZY8240.docx").tables[0].rows[0].cells[0]
    rendered_width = round(int(cell.width) / 914400 * 600)
    return round(rendered_width * .31)


def render_and_check(url: str, target: Path, size: int) -> dict:
    qr = QRCode(None, QRErrorCorrectLevel.H)
    qr.addData(url)
    qr.make()
    n = qr.getModuleCount()
    full = n + 8
    image = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(image)
    for y in range(n):
        for x in range(n):
            if qr.isDark(y, x):
                left = round((x + 4) * size / full)
                top = round((y + 4) * size / full)
                right = round((x + 5) * size / full) - 1
                bottom = round((y + 5) * size / full) - 1
                draw.rectangle((left, top, right, bottom), fill="black")
    image.save(target, format="PNG", dpi=(600, 600))

    # Reopen every file and compare its full matrix with the URL's QR matrix.
    with Image.open(target) as saved:
        assert saved.format == "PNG" and saved.size == (size, size)
        pixels = saved.convert("RGB")
        for y in range(full):
            for x in range(full):
                px = round((x + .5) * size / full)
                py = round((y + .5) * size / full)
                expected = (x >= 4 and y >= 4 and x < n + 4 and y < n + 4
                            and qr.isDark(y - 4, x - 4))
                assert pixels.getpixel((px, py)) == ((0, 0, 0) if expected else (255, 255, 255)), target
    return {"image_px": size, "modules": n, "quiet_zone_modules": 4, "error_correction": "H"}


def main() -> None:
    audit = json.loads((QR_DIR / "cbpm_audit.json").read_text(encoding="utf-8"))
    assert len(audit["source_indexes"]) == 21 and not audit["errors"]
    articles = audit["articles"]
    index_items = [item for page in audit["source_indexes"] for item in page["items"]]
    results = []
    size = qr_size()
    for match in audit["matches"]:
        ident = match["id"]
        candidates = match["candidates"]
        method = None
        if len(candidates) == 1:
            article = articles[candidates[0]]
            expected_images = {name for name in match["image_files"] if name}
            assert len(expected_images) == 2 and expected_images <= set(article["images"]), ident
            method = "both_official_coin_images_match"
        elif not candidates:
            title = EXPECTED_INDEX_TITLES.get(ident, match["name"])
            title_matches = [item["url"] for item in index_items
                             if normalize_title(item["title"]) == normalize_title(title)]
            if len(title_matches) == 1:
                candidates = title_matches
                method = "unique_official_index_title"
        if len(candidates) == 1 and method:
            url = candidates[0]
            assert url in articles and urlparse(url).netloc == "www.cbpm.cn"
            details = render_and_check(url, QR_DIR / f"{ident}.png", size)
            results.append({"id": ident, "name": match["name"], "status": "generated", "url": url,
                            "evidence": method, **details})
            print(f"checked {ident}: {url}", flush=True)
        else:
            results.append({"id": ident, "name": match["name"], "status": "needs_manual_review",
                            "reason": "No unique detail page in the specified 21 official index pages",
                            "fallback_url": FALLBACK_URL})
            print(f"REVIEW {ident}: {match['name']}", flush=True)
    fallback_details = render_and_check(FALLBACK_URL, QR_DIR / "fallback.png", size)
    catalog = json.loads((LABEL / "data" / "catalog.json").read_text(encoding="utf-8"))
    names = {item["id"]: item["name"] for item in results}
    missing = [item["id"] for item in catalog if not (QR_DIR / f"{item['id']}.png").exists()]
    lines = [
        "# 暂用官方目录二维码的标签",
        "",
        f"`fallback.png` 指向 {FALLBACK_URL}，采用 H 级容错、四模块静区，尺寸 {size} × {size} 像素。",
        "标签缺少同编号的 `qr/<ID>.png` 时，生成器自动使用 `fallback.png`。补上专属 PNG 后会自动优先使用专属二维码。",
        "",
        f"当前暂用 fallback：{len(missing)} 枚。",
        "",
    ]
    lines += [f"- `{ident}` {names.get(ident, '')}" for ident in missing]
    if not missing:
        lines.append("- 无")
    lines += ["", "本清单由 `scripts/generate_verified_qr.py` 根据 `data/catalog.json` 与 `qr/` 中现有 PNG 自动生成。", ""]
    (QR_DIR / "FALLBACK.md").write_text("\n".join(lines), encoding="utf-8")
    output = QR_DIR / "links.json"
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    generated = [item for item in results if item["status"] == "generated"]
    print(f"{len(generated)}/{len(results)} dedicated QR images; {len(missing)} use fallback; {size} x {size} px; fallback modules={fallback_details['modules']}", flush=True)


if __name__ == "__main__":
    main()
