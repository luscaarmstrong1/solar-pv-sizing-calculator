from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "diagrams" / "architecture.png"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    width, height = 980, 1280
    image = Image.new("RGB", (width, height), "#F8FAFC")
    draw = ImageDraw.Draw(image)
    title_font = font(34, True)
    box_font = font(22, True)
    small_font = font(16)
    draw.text((70, 45), "Solar PV System Sizing Calculator", fill="#17324D", font=title_font)
    draw.text((70, 92), "Preliminary engineering workflow", fill="#475569", font=small_font)
    steps = [
        "Consumption",
        "Coverage Target",
        "HSP + Performance Ratio",
        "Required PV Power",
        "PV Modules",
        "Inverter",
        "String Sizing",
        "Technical Validations",
        "Monthly Generation",
        "Report",
    ]
    x, y, box_w, box_h, gap = 210, 150, 560, 72, 38
    colors = ["#EAF2FF", "#E8F5F0", "#FFF7E6", "#EAF2FF", "#E8F5F0", "#FFF7E6", "#EAF2FF", "#FEE2E2", "#E8F5F0", "#EAF2FF"]
    for idx, step in enumerate(steps):
        top = y + idx * (box_h + gap)
        draw.rounded_rectangle((x, top, x + box_w, top + box_h), radius=10, fill=colors[idx], outline="#CBD5E1", width=2)
        text_box = draw.textbbox((0, 0), step, font=box_font)
        draw.text((x + (box_w - (text_box[2] - text_box[0])) / 2, top + 22), step, fill="#17324D", font=box_font)
        if idx < len(steps) - 1:
            cx = x + box_w / 2
            start = top + box_h + 8
            end = top + box_h + gap - 8
            draw.line((cx, start, cx, end), fill="#2563EB", width=4)
            draw.polygon([(cx - 8, end - 2), (cx + 8, end - 2), (cx, end + 12)], fill="#2563EB")
    image.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
