"""Check catalog coverage and exact background pixels without third-party packages."""

from __future__ import annotations

import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
SIZES = {"front": (1983, 793), "back": (1738, 905)}


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as file:
        header = file.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("不是有效 PNG")
    return struct.unpack(">II", header[16:24])


def main() -> None:
    errors = []
    ids = [coin["id"] for coin in CATALOG]
    if len(ids) != len(set(ids)):
        errors.append("catalog.json 中有重复编号")
    for coin in CATALOG:
        ident = coin["id"]
        for side, expected in SIZES.items():
            path = ROOT / "backgrounds" / side / f"{ident}.png"
            if not path.exists():
                errors.append(f"缺少 {path.relative_to(ROOT)}")
                continue
            try:
                actual = png_size(path)
            except ValueError as exc:
                errors.append(f"{path.relative_to(ROOT)}: {exc}")
                continue
            if actual != expected:
                errors.append(f"{path.relative_to(ROOT)} 为 {actual}，应为 {expected}")
        for side in ("f", "b"):
            source = ROOT / "coins" / f"{ident}_{side}.webp"
            if not source.exists() and ident not in {"JB06-2", "JB06-3"}:
                errors.append(f"缺少币图 {source.relative_to(ROOT)}")
    print(f"目录 {len(ids)} 枚；背景目标：正面 {SIZES['front']}、背面 {SIZES['back']}")
    print(f"错误 {len(errors)} 项")
    for error in errors:
        print("-", error)
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
