"""Build the full-bleed Lulu interior from canonical AI LegalFlow MX content."""
from __future__ import annotations

import json
import re
from pathlib import Path

import reportlab
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch as reportlab_inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
OUT = ROOT / "output" / "pdf" / "ai-legalflow-mx-guia-maestra-interior.pdf"
ART = BOOK / "assets" / "ai-legalflow-mx-title-full-bleed-300ppi.png"
CAPABILITIES = ROOT / "docs" / "content" / "capabilities.json"
PAGE = (6.25 * inch, 9.25 * inch)
FONT = Path(reportlab.__file__).resolve().parent / "fonts" / "Vera.ttf"


def blocks(path: Path) -> list[tuple[str, str | Path]]:
    result: list[tuple[str, str | Path]] = []
    source_parts = re.split(r"(```[\s\S]*?```)", path.read_text(encoding="utf-8"))
    for source_part in source_parts:
        if source_part.startswith("```"):
            result.append(("code", re.sub(r"^```[^\n]*\n?|\n?```$", "", source_part.strip())))
            continue
        for raw in source_part.split("\n\n"):
            raw = raw.strip()
            if not raw:
                continue
            if raw.startswith("# "):
                result.append(("h1", raw[2:]))
            elif image_match := re.fullmatch(r"!\[[^]]*\]\(([^)]+)\)", raw):
                result.append(("image", (path.parent / image_match.group(1)).resolve()))
            elif raw.startswith("Estado:"):
                result.append(("status", raw.removeprefix("Estado:").strip()))
            elif raw == "{{CAPABILITY_MATRIX}}":
                result.append(("matrix", raw))
            else:
                text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", raw.replace("\n", " "))
                text = re.sub(r"`([^`]+)`", r"<font name='AILegalFlow'>\1</font>", text)
                text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
                result.append(("body", text))
    return result


def footer(canvas, doc) -> None:  # type: ignore[no-untyped-def]
    canvas.saveState()
    canvas.setStrokeColor(HexColor("#D1D5DB"))
    canvas.line(doc.leftMargin, 0.47 * inch, PAGE[0] - doc.rightMargin, 0.47 * inch)
    canvas.setFillColor(HexColor("#475569"))
    canvas.setFont("AILegalFlow", 7.5)
    canvas.drawString(doc.leftMargin, 0.30 * inch, "AI LegalFlow MX · Guía Maestra")
    canvas.drawRightString(PAGE[0] - doc.rightMargin, 0.30 * inch, str(doc.page))
    canvas.restoreState()


def title_page(canvas, doc) -> None:  # type: ignore[no-untyped-def]
    """The generated artwork owns every visible element of the title page."""
    canvas.drawImage(str(ART), 0, 0, width=PAGE[0], height=PAGE[1], mask="auto")


def capability_matrix(style: ParagraphStyle) -> Table:
    entries = json.loads(CAPABILITIES.read_text(encoding="utf-8"))
    rows = [[Paragraph("Capacidad", style), Paragraph("Estado", style), Paragraph("Alcance", style)]]
    for item in entries:
        rows.append([
            Paragraph(item["capability"], style),
            Paragraph(item["status"], style),
            Paragraph(item["detail"], style),
        ])
    table = Table(rows, colWidths=[1.5 * inch, 0.9 * inch, 2.25 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#7F1D1D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, HexColor("#F8FAFC")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def qr_block(body: ParagraphStyle) -> Table:
    widget = qr.QrCodeWidget("https://hassanvfx.github.io/legalflow-mx/")
    drawing = Drawing(1.15 * inch, 1.15 * inch)
    drawing.add(widget)
    return Table([[drawing, Paragraph("Continúa en la guía viva:<br/>hassanvfx.github.io/legalflow-mx", body)]], colWidths=[1.3 * inch, 3.7 * inch], style=[("VALIGN", (0, 0), (-1, -1), "MIDDLE")])


def main() -> None:
    if not FONT.is_file():
        raise SystemExit(f"Missing required embedded font: {FONT}")
    if not ART.is_file():
        raise SystemExit(f"Missing required generated title artwork: {ART}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdfmetrics.registerFont(TTFont("AILegalFlow", str(FONT)))
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="AILegalFlow", fontSize=18, leading=22, textColor=HexColor("#7F1D1D"), spaceBefore=12, spaceAfter=10, keepWithNext=1)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontName="AILegalFlow", fontSize=10.15, leading=14.5, textColor=HexColor("#1F2937"), spaceAfter=9)
    code = ParagraphStyle("Code", parent=body, fontSize=8.4, leading=11.2, textColor=HexColor("#111827"), backColor=HexColor("#F1F5F9"), borderColor=HexColor("#CBD5E1"), borderWidth=.5, borderPadding=7, spaceAfter=10)
    table_text = ParagraphStyle("Table", parent=body, fontSize=7.2, leading=9.2, spaceAfter=0)
    doc = SimpleDocTemplate(str(OUT), pagesize=PAGE, leftMargin=.825 * inch, rightMargin=.625 * inch, topMargin=.625 * inch, bottomMargin=.70 * inch, title="AI LegalFlow MX", author="Hassan Uriostegui; Aurora Cotne")
    story = [PageBreak()]
    for chapter in sorted((BOOK / "chapters").glob("*.md")):
        for kind, text in blocks(chapter):
            if kind == "h1":
                story.append(Paragraph(str(text), h1))
            elif kind == "status":
                continue
            elif kind == "matrix":
                story.append(capability_matrix(table_text))
                story.append(Spacer(1, 10))
            elif kind == "image":
                image_path = Path(text)
                if not image_path.is_file():
                    raise SystemExit(f"Missing booklet image: {image_path}")
                max_width = 4.0 * inch if "official" in str(image_path) else 4.8 * inch
                image = Image(str(image_path))
                scale = min(max_width / image.imageWidth, 4.5 * inch / image.imageHeight)
                image.drawWidth = image.imageWidth * scale
                image.drawHeight = image.imageHeight * scale
                story.append(image)
                story.append(Spacer(1, 8))
                if "onboarding" in str(image_path) or "official" in str(image_path):
                    story.append(qr_block(body))
                    story.append(Spacer(1, 10))
            elif kind == "code":
                story.append(KeepTogether([Preformatted(str(text), code)]))
            else:
                story.append(Paragraph(str(text), body))
    story.append(PageBreak())
    story.append(Paragraph("Guía viva", h1))
    story.append(Paragraph("Consulta los pasos actualizados de instalación y recuperación. Este QR no concede acceso a ningún asunto ni transmite secretos.", body))
    story.append(Spacer(1, 10))
    story.append(qr_block(body))
    doc.build(story, onFirstPage=title_page, onLaterPages=footer)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
