"""Audit label coins against the CBPM ordinary-commemorative-coin pages.

Run from the repository root with a Python installation that has lxml. This
script only writes the link audit; it never creates trusted QR images.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
import json
import re
import time

from lxml import html


ROOT = Path(__file__).resolve().parents[1]
LABEL = ROOT
BASE = "https://m.cbpm.cn/cn/rmbpic/rmbpic6/"
ARTICLE = re.compile(r"^https://www\.cbpm\.cn/cn/rmbpic/rmbpic6/\d{6}/t\d+_\d+\.html$")
IMAGE = re.compile(r"P\d+\.(?:png|jpe?g|webp)", re.IGNORECASE)


def fetch(url: str) -> str:
    error = None
    for attempt in range(3):
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=30) as response:
                return response.read().decode("utf-8", errors="replace")
        except Exception as exc:
            error = exc
            time.sleep(attempt + 1)
    raise RuntimeError(f"{url}: {error}")


def index_url(page: int) -> str:
    return BASE + ("index.html" if page == 0 else f"index_{page}.html")


def scan_index(page: int) -> dict:
    url = index_url(page)
    document = html.fromstring(fetch(url))
    items = []
    for anchor in document.xpath("//a[@href]"):
        target = urljoin(url, anchor.get("href")).replace("https://m.cbpm.cn/", "https://www.cbpm.cn/")
        if ARTICLE.fullmatch(target):
            items.append({"title": " ".join(anchor.text_content().split()), "url": target})
    return {"page": page, "url": url, "items": items}


def scan_article(url: str) -> dict:
    raw = fetch(url.replace("https://www.cbpm.cn/", "https://m.cbpm.cn/"))
    document = html.fromstring(raw)
    title = document.xpath("string(//title)").strip()
    image_files = sorted(set(IMAGE.findall(raw)))
    challenged = "访问验证" in title
    return {"url": url, "title": title, "images": image_files, "access_challenge": challenged}


def main() -> None:
    catalog = json.loads((LABEL / "data" / "catalog.json").read_text(encoding="utf-8"))
    coins = {coin["id"]: coin for coin in json.loads((ROOT / "coin_data.json").read_text(encoding="utf-8"))}
    pages = {}
    errors = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        tasks = {pool.submit(scan_index, page): page for page in range(21)}
        for future in as_completed(tasks):
            page = tasks[future]
            try:
                pages[page] = future.result()
                print(f"index {page}: {len(pages[page]['items'])} article links", flush=True)
            except Exception as exc:
                errors.append(str(exc))
    if len(pages) != 21 or any(not page["items"] for page in pages.values()):
        raise RuntimeError("Index scan incomplete; preserving previous audit")
    urls = sorted({item["url"] for page in pages.values() for item in page["items"]})
    articles = {}
    with ThreadPoolExecutor(max_workers=3) as pool:
        tasks = {pool.submit(scan_article, url): url for url in urls}
        for future in as_completed(tasks):
            url = tasks[future]
            try:
                articles[url] = future.result()
            except Exception as exc:
                errors.append(str(exc))
            if len(articles) % 25 == 0:
                print(f"articles {len(articles)}/{len(urls)}", flush=True)
    image_to_articles = {}
    for article in articles.values():
        for image_file in article["images"]:
            image_to_articles.setdefault(image_file, set()).add(article["url"])
    matches = []
    for item in catalog:
        coin = coins[item["id"]]
        image_files = [Path(urlparse(coin.get(key, "")).path).name for key in ("imageUrl", "imageUrl2")]
        candidates = sorted({url for filename in image_files if filename for url in image_to_articles.get(filename, ())})
        matches.append({"id": item["id"], "name": coin["name"], "image_files": image_files, "candidates": candidates})
    result = {"source_indexes": [pages[page] for page in sorted(pages)], "articles": articles, "matches": matches, "errors": errors}
    output = LABEL / "qr" / "cbpm_audit.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    counts = {}
    for match in matches:
        counts[len(match["candidates"])] = counts.get(len(match["candidates"]), 0) + 1
    print(f"saved {output}; pages={len(pages)}, articles={len(articles)}, match counts={counts}, errors={len(errors)}", flush=True)


if __name__ == "__main__":
    main()
