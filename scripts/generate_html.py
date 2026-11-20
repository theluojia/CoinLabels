"""Render the same label images used by Word into a browsable front/back catalog."""

from __future__ import annotations

from html import escape
from pathlib import Path

from PIL import Image

from generate_labels import CATALOG, LABEL, back, background_path, front


OUTPUT = LABEL / "output"
ASSETS = OUTPUT / "html_assets"


def preview(coin: dict, side: str) -> str | None:
    if not background_path(coin, back=side == "back"):
        return None
    size = (1983, 793) if side == "front" else (1738, 905)
    picture = front(coin, *size) if side == "front" else back(coin, *size)
    picture = picture.resize((round(size[0] * 0.65), round(size[1] * 0.65)), Image.Resampling.LANCZOS)
    name = f"{coin['id']}_{side}.webp"
    picture.save(ASSETS / name, "WEBP", quality=86, method=4)
    return f"html_assets/{name}"


def main() -> None:
    OUTPUT.mkdir(exist_ok=True)
    ASSETS.mkdir(exist_ok=True)
    items = []
    for coin in CATALOG:
        ident = escape(coin["id"])
        title = escape(coin["front"].get("title", "").replace("\n", " "))
        theme = escape(coin["theme"])
        faces = []
        for side, label in (("front", "正面 8252"), ("back", "背面 8240")):
            source = preview(coin, side)
            content = (
                f'<img loading="lazy" src="{escape(source)}" alt="{ident} {label}">'
                if source
                else '<div class="missing" aria-label="尚未制作">尚未制作</div>'
            )
            faces.append(f'<div class="face"><div class="face-name">{label}</div>{content}</div>')
        items.append(
            f'<article class="item" data-search="{ident} {title} {theme}">'
            f'<div class="item-heading"><span class="serial">{coin["serial"]:03d}</span>'
            f'<strong>{ident}</strong><span>{title}</span><em>{theme}</em></div>'
            f'<div class="pair">{"".join(faces)}</div></article>'
        )

    page = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>普通纪念币正反面标签总览</title>
<style>
:root{color-scheme:light;--ink:#193d41;--muted:#5b7173;--line:#d8e2de;--paper:#f6f7f3}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:"Microsoft YaHei","Noto Sans CJK SC",system-ui,sans-serif}
header{position:sticky;top:0;z-index:2;background:#f6f7f3ed;backdrop-filter:blur(12px);border-bottom:1px solid var(--line);padding:15px max(20px,calc((100vw - 1480px)/2))}
header h1{font-size:20px;margin:0 0 10px}header .tools{display:flex;gap:14px;align-items:center;flex-wrap:wrap}
input{border:1px solid #b9c9c5;border-radius:8px;padding:9px 12px;font:inherit;min-width:240px;background:white}#count{font-size:13px;color:var(--muted)}
main{max-width:1480px;margin:0 auto;padding:22px 20px 56px}.item{padding:18px 0 24px;border-bottom:1px solid var(--line)}
.item-heading{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap;margin:0 0 12px;font-size:14px}.item-heading strong{font-size:16px}.item-heading em{font-style:normal;color:var(--muted)}.serial{font-variant-numeric:tabular-nums;color:var(--muted)}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px;align-items:start}.face{min-width:0}.face-name{font-size:12px;color:var(--muted);margin-bottom:7px}
.face img,.missing{width:100%;height:auto;display:block;background:#fff;box-shadow:0 2px 12px #173e3b18;border:1px solid #dde4df}
.missing{aspect-ratio:2.5;display:grid;place-items:center;color:#8b9997}.face:nth-child(2) .missing{aspect-ratio:1.92}
@media(max-width:760px){.pair{grid-template-columns:1fr}header{position:static}}
@media print{header .tools{display:none}header{position:static;background:white}.item{break-inside:avoid}.pair{gap:6px}body{background:white}main{padding:0}.face img{box-shadow:none}}
</style></head><body><header><h1>普通纪念币正反面标签总览</h1><div class="tools"><input id="search" type="search" placeholder="搜索编号、名称或系列" aria-label="搜索编号、名称或系列"><span id="count"></span></div></header>
<main id="catalog">""" + "\n".join(items) + """</main>
<script>const q=document.getElementById('search'),cards=[...document.querySelectorAll('.item')],count=document.getElementById('count');function filter(){const s=q.value.trim().toLowerCase();let n=0;for(const c of cards){const show=c.dataset.search.toLowerCase().includes(s);c.hidden=!show;if(show)n++}count.textContent=`显示 ${n} / ${cards.length} 枚 · 正反面同屏 · __QR_STATUS__`;}q.addEventListener('input',filter);filter();</script></body></html>"""
    verified = sum((LABEL / "qr" / f"{coin['id']}.png").exists() for coin in CATALOG)
    page = page.replace("__QR_STATUS__", f"专属二维码 {verified} 枚，官方目录兜底 {len(CATALOG) - verified} 枚")
    (OUTPUT / "index.html").write_text(page, encoding="utf-8")
    print(f"index.html: {len(CATALOG)} paired entries")


if __name__ == "__main__":
    main()
