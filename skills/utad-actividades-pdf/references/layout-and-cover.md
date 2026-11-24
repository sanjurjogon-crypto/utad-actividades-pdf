# Layout and cover — exact geometry

Everything here is measured from `Plantilla Trabajos.docx` (for the cover) and the accepted UTAD
body layout (for content pages). Do not "improve" it.

## Page

A4, portrait (`210 × 297 mm`).
- **Cover margins**: `25.4 mm` (1 inch) left/right, matching `Plantilla Trabajos.docx`.
- **Body margins**: **22 mm on all four sides** → text frame `166 × 253 mm`.
No header, no footer, no page number, no rule, nothing outside the frame on body pages.

Single body font family: Helvetica (reportlab built-in, equivalent to Arial in `Plantilla Trabajos.docx`).
No serif, no second family, no colour in the body. Dark grey (`#333333`) only for figure captions.

## Styles (reportlab)

```python
ss    = ParagraphStyle("ss", fontName="Helvetica", fontSize=10, leading=14,
                       alignment=TA_JUSTIFY, spaceAfter=6)
h2    = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11.5, leading=15,
                       spaceBefore=10, spaceAfter=5, keepWithNext=1)
cap   = ParagraphStyle("cap", fontName="Helvetica-Oblique", fontSize=8, leading=10.5,
                       textColor=HexColor("#333333"), spaceBefore=3)
cell  = ParagraphStyle("cell", fontName="Helvetica", fontSize=8.5, leading=11)
cellb = ParagraphStyle("cellb", fontName="Helvetica-Bold", fontSize=8.5, leading=11)
```

Notes:

- `keepWithNext=1` on `h2` avoids a heading alone at the bottom. It does **not** protect
  against a heading + one-line paragraph + figure jumping; if that happens, wrap
  `[h2, paragraph, figure]` in a single `KeepTogether`.
- Body is justified. Never justify the cover.
- No bold inside body paragraphs. `cellb` is for table headers only.

## Cover (`Plantilla Trabajos.docx`)

The user's reference: `assets/cover-reference.png`, derived directly from `Plantilla Trabajos.docx`.

Five clean elements, black regular text on white, nothing else:

1. **Date** (`Fecha`) — top-left: `Helvetica` **11 pt** regular, left-aligned at `x = 25.4 mm`,
   baseline at `H − 16.3 mm` (matching the 12.7 mm header distance in the Word template).
2. **Subject** (`Asignatura`) — centered: `Helvetica` **26 pt** regular, baseline at
   `H − 34.0 mm` (e.g. `Sistemas Operativos` or `Fundamentos de Hardware`).
3. **Group** (`ASIR 1º GRUPO A`) — centered directly below the subject: `Helvetica` **26 pt**
   regular, baseline at `H − 47.2 mm`.
4. **Activity** (`Actividad`) — centered after one blank line gap: `Helvetica` **26 pt**
   regular, baseline at `H − 65.5 mm` (e.g. `Actividad Complementaria 8` or `UD2 - AC8`).
5. **Author** (`Gonzalo Sanjurjo`) — bottom-right: `Helvetica` **11 pt** regular,
   right-aligned at `x = W − 25.4 mm`, baseline at `14.1 mm` above the bottom edge (matching the
   12.7 mm footer distance in `Plantilla Trabajos.docx`). If multiple authors are given, stack
   upward at `5.5 mm` per line so the last author stays at `14.1 mm`.

```python
from reportlab.lib.utils import simpleSplit

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
    mc = 25.4 * mm
    max_w = W - 2 * mc

    # Top-left date (header position)
    c.setFont("Helvetica", 11)
    c.drawString(mc, H - 16.3 * mm, date)

    # Centered title block (26 pt regular, Title style from Plantilla Trabajos.docx)
    c.setFont("Helvetica", 26)
    y = H - 34.0 * mm
    y = _draw_centered_wrapped(c, subject, "Helvetica", 26, y, max_w, 12.0 * mm)
    y -= 1.2 * mm
    y = _draw_centered_wrapped(c, group, "Helvetica", 26, y, max_w, 12.0 * mm)
    y -= 6.3 * mm
    _draw_centered_wrapped(c, activity, "Helvetica", 26, y, max_w, 12.0 * mm)

    # Bottom-right author(s) (footer position)
    c.setFont("Helvetica", 11)
    y_auth = (14.1 + 5.5 * (len(authors) - 1)) * mm
    for author in authors:
        c.drawRightString(W - mc, y_auth, author)
        y_auth -= 5.5 * mm
    c.restoreState()
```

Details to preserve:

- Do **not** add yellow boxes, brackets (`-[ACnn]`), or grey subtitles.
- Use `Helvetica` regular (not Bold) on the cover, matching the `Arial` 26 pt `Title` and 11 pt
  `Normal` styles measured in `Plantilla Trabajos.docx`.
- Date format: `dd/mm/yyyy` or `d.m.yyyy` (`24/11/2026` or `24.11.2026`).
- If the activity title or code is unknown, ask once.

## Figures

```python
def fig(path, w_mm, txt):
    im = Image.open(path); w, h = im.size
    ww = w_mm * mm
    t = Table([[Image(path, ww, ww*h/w)], [Paragraph(txt, cap)]], colWidths=[ww])
    t.setStyle(TableStyle([
        ("NOSPLIT", (0, 0), (-1, -1)),
        ("LEFTPADDING",(0,0),(-1,-1),0), ("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),
        ("BOTTOMPADDING",(0,1),(0,1),8), ("BOTTOMPADDING",(0,0),(0,0),0),
        ("VALIGN",(0,0),(-1,-1),"TOP")]))
    t.hAlign = "CENTER"
    return t
```

- Width: **130–170 mm**. Terminal captures: 130–150 mm when they are dense, 160–170 when
  they are sparse. Never exceed 166 mm (the frame width).
- The 8 mm bottom padding is the breathing room under the caption; without it the next heading
  sticks to the caption.
- Caption text: `Figura N. <what the reader sees and why it matters>.` One or two lines,
  italic grey. Count figures sequentially across the whole document.
- One figure per `fig()` call. Two screenshots side by side only when both are wide and short;
  by default stack them.
- For ReportLab `Drawing()` topology diagrams, offset text labels away from bus/connector lines
  and verify in rendered page PNGs that no stroke crosses text.

## Page budget (the arithmetic that decides pagination)

Usable text box on body pages: **253 mm tall** (`297 − 22 − 22`) by `166 mm` wide. What each
block costs:

| Element | Height |
| --- | --- |
| `h2` heading | 10 mm (8 if it is a single line) |
| body paragraph | 6 mm per line + 6 mm spaceAfter |
| figure | `width_mm / aspect_ratio` (see table) |
| caption | 9 mm for two lines, 5 mm for one, plus 8 mm gap after the block |
| table | ~9 mm header + 6 mm per row + 4 mm spacer after |

Height of a figure at a given width, `h = w / ratio`, where the ratio is `pixels_wide / pixels_tall`:

| Ratio | 150 mm | 160 mm | 166 mm |
| --- | --- | --- | --- |
| 2,0 (tall, wide terminal) | 75 | 80 | 83 |
| 2,3 (typical VirtualBox terminal crop) | 65 | 70 | 72 |
| 2,6 | 58 | 62 | 64 |
| 3,0 (one command, few lines) | 50 | 53 | 55 |

So two captures of ratio 2,3 at 160 mm plus their captions are 158 mm: with two headings and
three short paragraphs a page holds exactly two blocks. Three figures of that size never fit on
one page, and that is the usual cause of the half-empty page.

## The short activity (three blocks and a question)

The most common shape, and it fits in cover + 2 pages:

```
page 1   block 1: heading, one line of intro, figure (160 mm), one paragraph with the numbers
         block 2: heading, one line of intro, figure (150 mm), one paragraph
page 2   block 3: heading, one line of intro, figure (150 mm), one paragraph, optional small table
         question: heading with the question, two short paragraphs
```

If block 3 lands at the foot of page 1 with its figure pushed to page 2, put `CondPageBreak(75 * mm)`
before its heading. If page 2 ends past the halfway mark, the document is fine as it is: a short
last page is normal, a half-empty page in the middle is not.

## Tables

```python
def tabla(rows, widths):
    data = [[Paragraph(str(c), cellb if i == 0 else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[x*mm for x in widths], repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.4, HexColor("#999999")),
        ("BACKGROUND",(0,0),(-1,0), HexColor("#eeeeee")),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),4), ("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),3), ("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    return t
```

- Header row light grey `#EEEEEE`, grid 0.4 pt `#999999`, cells as `Paragraph` so they wrap.
- Widths in mm and must sum to ≤ 166.
- **Always** leave 4 mm between a table and whatever comes next:
  `Spacer(1, 4*mm)` before the following paragraph. A table glued to a paragraph was an actual
  correction the user asked for.
- `repeatRows=1` so a table that breaks across pages repeats its header.
- Never let a table break with only its header on one page: if the first row cannot fit, push
  the whole table to the next page.

## Pagination rules

The failure modes seen in real reviews, and the fix for each:

| Symptom | Fix |
| --- | --- |
| Big blank at the bottom of a page | the next block is a `KeepTogether` that does not fit. Shrink the figure 10–15 mm or let the block split |
| Heading alone at the page bottom | `keepWithNext` on the heading, and wrap heading + first paragraph + figure in `KeepTogether` |
| Two-line paragraph split across pages | let reportlab keep it whole by wrapping the paragraph + figure in `KeepTogether`, or shorten the paragraph |
| Table separated from its heading | `keepWithNext` on the heading |
| Caption of figure N printed above figure N+1 | the figure block lost its image (missing file) — check the path |
| Last page with only three lines | acceptable, but try shrinking one figure so it joins the previous page |
| Text overlapping a figure's edge | the figure is wider than 166 mm or the table cell padding is negative |

## Fonts and glyphs

- Use `Helvetica`; the Spanish characters (`á é í ó ú ñ ü ¿ ¡ º ª`) work as-is.
- Superscripts (`2<super>24</super>`) for powers in calculations.
- `&mdash;` and `&ndash;` are **forbidden**; also forbidden in the visible text.
- `&middot;` is fine for separating short items, though the body should not need it.
