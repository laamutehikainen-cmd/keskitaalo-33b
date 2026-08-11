#!/usr/bin/env python3
"""Generate the private A4 welcome sheet for Keskitaalo 33B."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


FOREST = HexColor("#24352B")
FOREST_DARK = HexColor("#17251E")
PAPER = HexColor("#FFFDF8")
SNOW = HexColor("#F6F3ED")
TAUPE = HexColor("#C9B8AA")
EMBER = HexColor("#B56F4C")
CHARCOAL = HexColor("#20231F")
MUTED = HexColor("#656960")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("private/welcome-data.json"),
        help="Private JSON data file (ignored by Git)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/keskitaalo-33b-tervetuloa.pdf"),
        help="Destination PDF",
    )
    return parser.parse_args()


def load_data(path: Path) -> dict[str, object]:
    if not path.exists():
        raise SystemExit(
            f"Missing {path}. Copy private/welcome-data.example.json to "
            "private/welcome-data.json and replace the placeholders."
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    required = ("site_url", "wifi_name", "wifi_password", "host_contact", "draft")
    missing = [key for key in required if key not in data]
    if missing:
        raise SystemExit(f"Missing required values: {', '.join(missing)}")
    if not str(data["site_url"]).startswith("https://"):
        raise SystemExit("site_url must use https://")
    return data


def draw_tracking_text(
    pdf: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    size: float,
    tracking: float,
    color: Color,
) -> None:
    pdf.setFont("Helvetica-Bold", size)
    pdf.setFillColor(color)
    cursor = x
    for character in text:
        pdf.drawString(cursor, y, character)
        cursor += stringWidth(character, "Helvetica-Bold", size) + tracking


def draw_wrapped(
    pdf: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    font: str,
    size: float,
    leading: float,
    color: Color,
) -> float:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if not current or stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)

    pdf.setFont(font, size)
    pdf.setFillColor(color)
    for line in lines:
        pdf.drawString(x, y, line)
        y -= leading
    return y


def draw_qr(pdf: canvas.Canvas, value: str, x: float, y: float, size: float) -> None:
    widget = qr.QrCodeWidget(value)
    widget.barFillColor = FOREST_DARK
    x0, y0, x1, y1 = widget.getBounds()
    width = x1 - x0
    height = y1 - y0
    drawing = Drawing(size, size, transform=[size / width, 0, 0, size / height, 0, 0])
    drawing.add(widget)
    renderPDF.draw(drawing, pdf, x, y)


def generate_pdf(data: dict[str, object], output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    width, height = A4
    pdf = canvas.Canvas(str(output), pagesize=A4, pageCompression=1)
    pdf.setTitle("Keskitaalo 33B - Tervetuloa / Welcome")
    pdf.setAuthor("Keskitaalo 33B")
    pdf.setSubject("Mökin vierasopas ja WiFi-tiedot")

    pdf.setFillColor(SNOW)
    pdf.rect(0, 0, width, height, stroke=0, fill=1)

    margin = 12 * mm
    hero_y = height - 92 * mm
    hero_h = 80 * mm
    pdf.setFillColor(FOREST_DARK)
    pdf.roundRect(margin, hero_y, width - 2 * margin, hero_h, 8 * mm, stroke=0, fill=1)

    pdf.setStrokeColor(Color(1, 1, 1, alpha=0.16))
    pdf.setLineWidth(0.7)
    pdf.circle(width - 46 * mm, hero_y + 39 * mm, 31 * mm, stroke=1, fill=0)
    pdf.circle(width - 46 * mm, hero_y + 39 * mm, 22 * mm, stroke=1, fill=0)
    pdf.setFillColor(TAUPE)
    pdf.circle(width - 46 * mm, hero_y + 39 * mm, 13 * mm, stroke=0, fill=1)

    draw_tracking_text(
        pdf,
        "TERVETULOA / WELCOME",
        margin + 13 * mm,
        hero_y + 61 * mm,
        7.5,
        1.25,
        Color(1, 1, 1, alpha=0.68),
    )
    pdf.setFillColor(PAPER)
    pdf.setFont("Times-Roman", 33)
    pdf.drawString(margin + 13 * mm, hero_y + 42 * mm, "Keskitaalo")
    pdf.setFont("Times-Roman", 58)
    pdf.drawString(margin + 13 * mm, hero_y + 19 * mm, "33B")

    if bool(data["draft"]):
        pdf.setFillColor(EMBER)
        pdf.roundRect(width - 61 * mm, height - 26 * mm, 38 * mm, 9 * mm, 4.5 * mm, stroke=0, fill=1)
        draw_tracking_text(pdf, "LUONNOS / DRAFT", width - 56 * mm, height - 22.5 * mm, 6.5, 0.55, PAPER)

    content_top = hero_y - 13 * mm
    pdf.setFillColor(CHARCOAL)
    pdf.setFont("Times-Roman", 18)
    pdf.drawCentredString(width / 2, content_top, "Mökin opas kulkee mukanasi")
    pdf.setFont("Helvetica", 8.5)
    pdf.setFillColor(MUTED)
    pdf.drawCentredString(width / 2, content_top - 6 * mm, "Scan for cabin guidance, departure notes and ideas for Levi")

    card_y = 83 * mm
    card_h = 92 * mm
    gap = 8 * mm
    left_x = margin
    left_w = 78 * mm
    right_x = left_x + left_w + gap
    right_w = width - margin - right_x

    pdf.setFillColor(PAPER)
    pdf.roundRect(left_x, card_y, left_w, card_h, 6 * mm, stroke=0, fill=1)
    qr_size = 53 * mm
    qr_x = left_x + (left_w - qr_size) / 2
    qr_y = card_y + 24 * mm
    draw_qr(pdf, str(data["site_url"]), qr_x, qr_y, qr_size)
    draw_tracking_text(pdf, "MÖKIN OPAS / CABIN GUIDE", left_x + 11 * mm, card_y + 11 * mm, 6.4, 0.45, FOREST)

    pdf.setFillColor(PAPER)
    pdf.roundRect(right_x, card_y, right_w, card_h, 6 * mm, stroke=0, fill=1)
    draw_tracking_text(pdf, "WIFI", right_x + 10 * mm, card_y + card_h - 14 * mm, 7, 1.2, EMBER)

    label_y = card_y + card_h - 28 * mm
    pdf.setFont("Helvetica-Bold", 6.6)
    pdf.setFillColor(MUTED)
    pdf.drawString(right_x + 10 * mm, label_y, "VERKKO / NETWORK")
    draw_wrapped(
        pdf,
        str(data["wifi_name"]),
        right_x + 10 * mm,
        label_y - 8 * mm,
        right_w - 20 * mm,
        "Courier-Bold",
        10.5,
        13,
        CHARCOAL,
    )

    password_y = card_y + 39 * mm
    pdf.setFont("Helvetica-Bold", 6.6)
    pdf.setFillColor(MUTED)
    pdf.drawString(right_x + 10 * mm, password_y, "SALASANA / PASSWORD")
    draw_wrapped(
        pdf,
        str(data["wifi_password"]),
        right_x + 10 * mm,
        password_y - 8 * mm,
        right_w - 20 * mm,
        "Courier-Bold",
        10.5,
        13,
        CHARCOAL,
    )

    pdf.setStrokeColor(TAUPE)
    pdf.setLineWidth(0.7)
    pdf.line(right_x + 10 * mm, card_y + 23 * mm, right_x + right_w - 10 * mm, card_y + 23 * mm)
    pdf.setFont("Helvetica", 7.3)
    pdf.setFillColor(MUTED)
    draw_wrapped(
        pdf,
        str(data["host_contact"]),
        right_x + 10 * mm,
        card_y + 15 * mm,
        right_w - 20 * mm,
        "Helvetica",
        7.3,
        9.5,
        MUTED,
    )

    footer_y = 37 * mm
    pdf.setStrokeColor(TAUPE)
    pdf.line(margin, footer_y + 13 * mm, width - margin, footer_y + 13 * mm)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.setFillColor(EMBER)
    pdf.drawString(margin, footer_y, "HÄTÄTILANNE / EMERGENCY  112")
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 7.5)
    pdf.drawRightString(width - margin, footer_y, "Keskitaalo 33B · 99130 Sirkka · Levi")

    pdf.save()
    return output


def write_manifest(output: Path, data: dict[str, object]) -> None:
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    manifest = {
        "artifact": output.name,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "sha256": digest,
        "page": "A4 portrait",
        "site_url": str(data["site_url"]),
        "draft": bool(data["draft"]),
        "wifi_name_length": len(str(data["wifi_name"])),
        "wifi_password_length": len(str(data["wifi_password"])),
        "contains_private_values": True,
        "source_images": "none",
    }
    manifest_path = output.with_name(f"{output.stem}-manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    data = load_data(args.config)
    output = generate_pdf(data, args.output)
    write_manifest(output, data)
    print(output.resolve())


if __name__ == "__main__":
    main()
