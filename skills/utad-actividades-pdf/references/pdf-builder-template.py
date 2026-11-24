#!/usr/bin/env python3
"""
Builder for UTAD activity PDFs (Gonzalo Sanjurjo / ASIR 1º GRUPO A).

Usage
-----
    python pdf-builder-template.py -o Sanjurjo_Gonzalo_UD2_AC89.pdf ^
        --subject "Fundamentos de Hardware" ^
        --group "ASIR 1º GRUPO A" ^
        --activity "Actividad Complementaria 89" ^
        --date 24/11/2026 ^
        --author "Gonzalo Sanjurjo"

Edit the STORY section (or import the module and build your own list).
Everything above STORY is the house style; do not change it casually.

Dependencies: reportlab, Pillow.
"""
import argparse
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import (BaseDocTemplate, Frame, Image, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Spacer, Table,
                                TableStyle, KeepTogether)

W, H = A4
M = 22 * mm
MC = 25.4 * mm  # Cover margin matching Plantilla Trabajos.docx (1 inch)
CW = W - 2 * M

# ---------------------------------------------------------------- styles
ss = ParagraphStyle("ss", fontName="Helvetica", fontSize=10, leading=14,
                    alignment=TA_JUSTIFY, spaceAfter=6)
h1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=13, leading=17,
                    spaceBefore=4, spaceAfter=6, keepWithNext=1)
h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11.5, leading=15,
                    spaceBefore=10, spaceAfter=5, keepWithNext=1)
cap = ParagraphStyle("cap", fontName="Helvetica-Oblique", fontSize=8, leading=10.5,
                     textColor=colors.HexColor("#333333"), spaceBefore=3)
cell = ParagraphStyle("cell", fontName="Helvetica", fontSize=8.5, leading=11)
cellb = ParagraphStyle("cellb", fontName="Helvetica-Bold", fontSize=8.5, leading=11)


# ---------------------------------------------------------------- helpers
def fig(path, w_mm, caption):
    """Image + caption, with 8 mm of air under the block."""
    im = PILImage.open(path)
    w, h = im.size
    ww = w_mm * mm
    t = Table([[Image(path, ww, ww * h / w)], [Paragraph(caption, cap)]], colWidths=[ww])
    t.setStyle(TableStyle([
        ("NOSPLIT", (0, 0), (-1, -1)),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 1), (0, 1), 8), ("BOTTOMPADDING", (0, 0), (0, 0), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    t.hAlign = "CENTER"
    return t


def tabla(rows, widths_mm):
    """Grey header, thin grid, wrapping cells. Add Spacer(1, 4*mm) after it."""
    data = [[Paragraph(str(c), cellb if i == 0 else cell) for c in row]
            for i, row in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths_mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t


def _draw_centered_wrapped(c, text, font, size, y, max_w, leading):
    lines = simpleSplit(text, font, size, max_w)
    for line in lines:
        c.drawCentredString(W / 2, y, line)
        y -= leading
    return y


def portada(c, d, subject, group, activity, date, authors):
    """Cover matching Plantilla Trabajos.docx (Gonzalo Sanjurjo / ASIR 1º GRUPO A)."""
    c.saveState()
    c.setFillColor(colors.black)
    max_w = W - 2 * MC

    # Top-left date (header position from Plantilla Trabajos.docx)
    c.setFont("Helvetica", 11)
    c.drawString(MC, H - 16.3 * mm, date)

    # Centered 26 pt regular title block
    c.setFont("Helvetica", 26)
    y = H - 34.0 * mm
    y = _draw_centered_wrapped(c, subject, "Helvetica", 26, y, max_w, 12.0 * mm)
    y -= 1.2 * mm
    y = _draw_centered_wrapped(c, group, "Helvetica", 26, y, max_w, 12.0 * mm)
    y -= 6.3 * mm
    _draw_centered_wrapped(c, activity, "Helvetica", 26, y, max_w, 12.0 * mm)

    # Bottom-right author(s) (footer position from Plantilla Trabajos.docx)
    c.setFont("Helvetica", 11)
    auth_list = authors if authors else ["Gonzalo Sanjurjo"]
    y_auth = (14.1 + 5.5 * (len(auth_list) - 1)) * mm
    for author in auth_list:
        c.drawRightString(W - MC, y_auth, author)
        y_auth -= 5.5 * mm
    c.restoreState()


# ---------------------------------------------------------------- STORY
def build_story():
    """Replace this with the real content. Skeleton below."""
    story = [NextPageTemplate("Body"), PageBreak()]

    story += [Paragraph("1. <bloque del enunciado>", h2),
              Paragraph("<una frase: qué haces y qué buscas>.", ss),
              # fig("fig/fig1.png", 145, "Figura 1. <qué se ve y qué demuestra>."),
              # tabla([["Comando", "Resultado", "Conclusión"],
              #        ["ip route", "default via 10.0.2.2", "hay puerta"]],
              #       [46, 60, 56]),
              # Spacer(1, 4 * mm),
              ]

    story += [Paragraph("<respuesta a la primera pregunta>.", ss)]
    return story


# ---------------------------------------------------------------- build
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--subject", default="Sistemas Operativos",
                    help="e.g. Sistemas Operativos | Fundamentos de Hardware")
    ap.add_argument("--group", default="ASIR 1º GRUPO A")
    ap.add_argument("--activity", required=True,
                    help="e.g. Actividad Complementaria 89 | UD2 - AC89")
    ap.add_argument("--date", required=True, help="dd/mm/yyyy or d.m.yyyy")
    ap.add_argument("--author", action="append", default=[])
    args = ap.parse_args()

    authors = args.author or ["Gonzalo Sanjurjo"]

    doc = BaseDocTemplate(args.out, pagesize=A4, leftMargin=M, rightMargin=M,
                          topMargin=M, bottomMargin=M,
                          title="%s - %s" % (args.subject, args.activity),
                          author="; ".join(authors))
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[Frame(MC, MC, W - 2 * MC, H - 2 * MC, id="c")],
                     onPage=lambda c, d: portada(c, d, args.subject, args.group,
                                                 args.activity, args.date, authors)),
        PageTemplate(id="Body", frames=[Frame(M, M, CW, H - 2 * M, id="b")])])
    doc.build(build_story())
    print("ok:", args.out)


if __name__ == "__main__":
    main()
