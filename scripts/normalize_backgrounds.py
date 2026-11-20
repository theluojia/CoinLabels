"""Normalize generated label PNGs by proportional cover crop, never by stretching."""

from pathlib import Path
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1] / "backgrounds"
SIZES = {"front": (1983, 793), "back": (1738, 905)}


def main():
    for side, size in SIZES.items():
        for path in sorted((ROOT / side).glob("*.png")):
            with Image.open(path) as source:
                if source.size == size:
                    continue
                result = ImageOps.fit(
                    source.convert("RGB"), size, method=Image.Resampling.LANCZOS
                )
            result.save(path)
            print(f"{side}/{path.name} -> {size[0]}x{size[1]}")


if __name__ == "__main__":
    main()
