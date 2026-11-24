#!/usr/bin/env python3
"""Render every page of a PDF to PNG so the layout can be inspected.

Usage: python render_pages.py doc.pdf [outdir] [dpi]

Tries PyMuPDF, then pdftoppm, then Ghostscript. Prints the paths.
"""
import os
import shutil
import subprocess
import sys


def with_pymupdf(pdf, outdir, dpi):
    import pymupdf
    doc = pymupdf.open(pdf)
    paths = []
    for i, page in enumerate(doc, 1):
        p = os.path.join(outdir, "page%02d.png" % i)
        page.get_pixmap(dpi=dpi).save(p)
        paths.append(p)
    return paths


def with_poppler(pdf, outdir, dpi):
    base = os.path.join(outdir, "page")
    subprocess.run(["pdftoppm", "-png", "-r", str(dpi), pdf, base], check=True)
    return sorted(os.path.join(outdir, f) for f in os.listdir(outdir) if f.startswith("page"))


def with_gs(pdf, outdir, dpi):
    gs = shutil.which("gswin64c") or shutil.which("gs")
    if not gs:
        return None
    out_pat = os.path.join(outdir, "page%02d.png")
    subprocess.run([gs, "-sDEVICE=png16m", "-r%d" % dpi, "-o", out_pat, pdf],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return sorted(os.path.join(outdir, f) for f in os.listdir(outdir) if f.startswith("page"))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    pdf = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else "pages"
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    os.makedirs(outdir, exist_ok=True)

    paths = None
    try:
        paths = with_pymupdf(pdf, outdir, dpi)
    except Exception:
        paths = None
    if not paths and shutil.which("pdftoppm"):
        paths = with_poppler(pdf, outdir, dpi)
    if not paths:
        paths = with_gs(pdf, outdir, dpi)
    if not paths:
        print("no renderer available: install PyMuPDF or poppler, or open the PDF by hand")
        return 1

    for p in paths:
        print(p)
    print("%d page(s) rendered. Look at every one before delivering." % len(paths))
    return 0


if __name__ == "__main__":
    sys.exit(main())
