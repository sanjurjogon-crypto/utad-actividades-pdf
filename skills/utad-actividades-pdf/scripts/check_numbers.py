#!/usr/bin/env python3
"""Print every line of the PDF that carries a number, page by page.

Usage: python check_numbers.py documento.pdf [pagina]

Use it next to the captures: each line printed here should be checkable in a figure or a table.
A line whose numbers appear nowhere in the images is either a mistake or something you measured
but never captured, and both get caught by the teacher.
"""
import re
import sys

try:
    import pymupdf
except ImportError:
    sys.exit("PyMuPDF not available: open the PDF by hand and read the numbers out loud")

DIGIT = re.compile(r"\d")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    pdf = sys.argv[1]
    only = int(sys.argv[2]) if len(sys.argv) > 2 else None

    doc = pymupdf.open(pdf)
    total = 0
    for i, page in enumerate(doc, 1):
        if only and i != only:
            continue
        lines = [l.strip() for l in page.get_text().splitlines() if l.strip()]
        hits = [l for l in lines if DIGIT.search(l)]
        print("== pagina %d: %d linea(s) con cifras" % (i, len(hits)))
        for l in hits:
            print("   " + l)
        total += len(hits)
    print("\n%d lineas. Cada cifra de aqui tiene que verse en una captura o en una tabla." % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
