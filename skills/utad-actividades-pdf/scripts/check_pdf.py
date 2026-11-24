#!/usr/bin/env python3
"""Grade a finished PDF against the house rules, with measurements instead of opinions.

Usage:
    python check_pdf.py Sanjurjo_Gonzalo_UD2_AC12.pdf
    python check_pdf.py IMSO_UD2_AE2_Sanjurjo_Gonzalo.pdf --max-pages 8

Checks the file name, the cover layout matching Plantilla Trabajos.docx (author, group,
date, no legacy yellow boxes), the absence of em/en dashes, banned vocabulary, label-colon
paragraph starts, bold in body text, headers and footers on body pages, absence of the
legacy AI note, the figures and captions, and the page count. Every line must read PASS
before the file is delivered. Exit 1 on any FAIL.
"""
import argparse
import os
import re
import sys

import pymupdf

ap = argparse.ArgumentParser()
ap.add_argument("pdf")
ap.add_argument("--max-pages", type=int, default=5,
                help="maximum allowed total pages including cover (default: 5)")
ap.add_argument("--author", default="Gonzalo Sanjurjo",
                help="expected author name on the cover (default: Gonzalo Sanjurjo)")
ap.add_argument("--group", default="ASIR 1º GRUPO A",
                help="expected group line on the cover (default: ASIR 1º GRUPO A)")
ap.add_argument("--allow-no-question", action="store_true",
                help="do not fail when body text contains no '?'")
ap.add_argument("--min-figures", type=int, default=2,
                help="minimum number of figures required (default: 2; 0 for pure text/calc)")
args = ap.parse_args()

PDF = args.pdf
doc = pymupdf.open(PDF)
pages = doc.page_count
W, H = doc[0].rect.width, doc[0].rect.height
MM = 72 / 25.4

text = "\n".join(p.get_text() for p in doc)
cover_text = doc[0].get_text()
body_text = "\n".join(p.get_text() for p in doc[1:])
P = []          # (ok, label, detail)


def check(ok, label, detail=""):
    P.append((ok, label, detail))


# --- filename (supports Surname_Name_UDx_ACy.pdf, Surname_Name_SUBJECT_UDx_EVy.pdf, and SUBJECT_UDx_AEy_Surname_Name.pdf)
name = os.path.basename(PDF)
word = r"[A-Za-zÁÉÍÓÚÑáéíóúñ-]+"
subj = r"[A-Z]{2,6}"
ud_tag = r"UD\d+_(?:AC|AE|EV)\d+(?:-\d+)?"
name_ok = re.fullmatch(
    rf"(?:(?:{subj}_)?{word}_{word}(?:_{subj})?_{ud_tag}|{subj}_{ud_tag}_{word}_{word})\.pdf",
    name,
) is not None
check(name_ok, "nombre del archivo", name)

# --- cover layout (Plantilla Trabajos.docx: no yellow boxes, no -[ACn], author + group + date)
d = doc[0].get_drawings()
yellow_boxes = [
    it["rect"] for it in d
    if (f := it.get("fill")) and f[0] > 0.9 and f[1] > 0.85 and f[2] < 0.25
]
check(not yellow_boxes, "portada: sin recuadros amarillos",
      "limpia" if not yellow_boxes else "%d recuadro(s)" % len(yellow_boxes))
check(re.search(r"-\[(?:AC|AE|EV)\d+\]", cover_text) is None,
      "portada: sin etiqueta antigua -[ACn]", "")
check(args.author in cover_text, "portada: autor (%s)" % args.author, "")
check(args.group in cover_text, "portada: grupo (%s)" % args.group, "")
has_date = re.search(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b", cover_text) is not None
check(has_date, "portada: fecha presente", "")

# --- forbidden things in the whole document
banned = ["fundamental", "clave", "crucial", "robusto", "óptimo", "garantizar", "cabe destacar",
          "en definitiva", "en conclusión", "en resumen", "asimismo", "adicionalmente",
          "no obstante", "se procede a", "en una frase", "en el mundo actual", "sinergia"]
hits = [w for w in banned
        if re.search(r"(?<![\wáéíóúüñ])" + re.escape(w) + r"(?![\wáéíóúüñ])", text.lower())]
check(not hits, "sin vocabulario de IA", ", ".join(hits) if hits else "limpio")

check("—" not in text and "–" not in text, "sin rayas largas", "")

labels = re.findall(r"^\s*(Políticas|Formación|Conclusión|Resumen|Análisis|Plan|Objetivo|Nota):",
                    body_text, re.M)
check(not labels, "sin párrafos que empiezan por etiqueta", ", ".join(labels) if labels else "")

edge = []
for i, p in enumerate(doc, 1):
    if i == 1:
        continue
    for b in p.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            y0, y1 = ln["bbox"][1], ln["bbox"][3]
            if y0 < 22 * MM - 2 or y1 > H - 20 * MM:
                edge.append("p%d %.0f-%.0f pt" % (i, y0, y1))
check(not edge and "Página " not in body_text, "sin cabeceras ni pies en cuerpo",
      "; ".join(edge[:3]) if edge else "márgenes limpios")

# --- bold in body: bold spans at body size (pages >= 2)
bold_body = []
for p in doc[1:]:
    for b in p.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            for sp in ln["spans"]:
                if "Bold" in sp["font"] and 9.8 < sp["size"] < 10.6 and sp["text"].strip():
                    bold_body.append(sp["text"][:40])
check(not bold_body, "sin negritas en el cuerpo",
      "; ".join(bold_body[:3]) if bold_body else "limpio")

# --- no legacy AI note
has_ai_note = "inteligencia artificial agéntica" in text.lower()
check(not has_ai_note, "sin nota final de IA", "")

# --- evidence: images and captions
imgs = sum(len(p.get_images()) for p in doc)
caps = re.findall(r"Figura \d+(?:\s*\([^)]+\))?\.", text)
check(imgs >= args.min_figures, "capturas reales", "%d imágenes" % imgs)
check(len(caps) >= args.min_figures, "pie de figura", "%d pies" % len(caps))
check(len(caps) == imgs, "una figura por captura", "%d pies / %d imágenes" % (len(caps), imgs))

# --- answers: the statement's question marks
if not args.allow_no_question:
    check(body_text.count("?") >= 1, "hay respuesta a la pregunta", "")
check(pages <= args.max_pages, "extensión contenida (<= %d pág.)" % args.max_pages, "%d páginas" % pages)

print("PDF: %s  (%d páginas, %.0f×%.0f mm)" % (name, pages, W / MM, H / MM))
bad = 0
for ok, label, detail in P:
    print("  %s  %-46s %s" % ("PASS" if ok else "FAIL", label, detail))
    bad += 0 if ok else 1
print("\n%d/%d PASS" % (len(P) - bad, len(P)))
sys.exit(1 if bad else 0)
