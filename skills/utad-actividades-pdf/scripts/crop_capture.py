#!/usr/bin/env python3
"""Crop a screenshot to its content: trims black/plain borders and empty rows.

Usage:
    python crop_capture.py in.png out.png            # auto (dark desktop border trim)
    python crop_capture.py in.png out.png --window   # auto-detect foreground terminal window + trim
    python crop_capture.py in.png out.png --box 0,28,1228,800   # fixed window box first
    python crop_capture.py in.png out.png --pad 12 --thresh 110

It keeps the full width of the content and trims top/bottom to the rows that have text,
which is what makes screenshots of terminals legible once placed at 130-150 mm.
"""
import argparse
from collections import Counter
import sys

try:
    from PIL import Image
except Exception:
    print("Pillow not available: install Pillow (`pip install pillow`) or crop with ImageMagick (`magick`)")
    sys.exit(1)


def has_black_bottom(im, min_frac=0.06):
    """Detect half-drawn captures whose bottom band is pure #000000."""
    w, h = im.size
    px = im.load()
    black_rows = 0
    for y in range(h - 1, -1, -1):
        if all(px[x, y] == (0, 0, 0) for x in range(0, w, 16)):
            black_rows += 1
        else:
            break
    return black_rows >= int(h * min_frac)


def box_uniformity(im, box, bg, tol=8):
    """Fraction of pixels inside box matching bg within tol (terminals > 0.7, photos low)."""
    x0, y0, x1, y1 = box
    px = im.load()
    tot = hits = 0
    for y in range(y0 + 10, max(y0 + 11, y1 - 10), 8):
        for x in range(x0 + 10, max(x0 + 11, x1 - 10), 8):
            c = px[x, y]
            tot += 1
            if abs(c[0] - bg[0]) <= tol and abs(c[1] - bg[1]) <= tol and abs(c[2] - bg[2]) <= tol:
                hits += 1
    return hits / max(1, tot)


def _box_for_bg(im, px, w, h, bg, tol):
    """Compute tight uniform rectangle matching bg."""
    def match(c):
        return abs(c[0] - bg[0]) <= tol and abs(c[1] - bg[1]) <= tol and abs(c[2] - bg[2]) <= tol

    row_frac = [sum(1 for x in range(0, w, 4) if match(px[x, y])) / ((w + 3) // 4) for y in range(h)]
    best_y, cur = (0, 0), None
    for y, f in enumerate(row_frac):
        if f >= 0.15:
            cur = y if cur is None else cur
        elif cur is not None:
            if y - cur > best_y[1] - best_y[0]:
                best_y = (cur, y)
            cur = None
    if cur is not None and h - cur > best_y[1] - best_y[0]:
        best_y = (cur, h)

    y0, y1 = best_y
    if y1 <= y0:
        return (0, 0, 0, 0)
    ys = range(y0, y1, max(1, (y1 - y0) // 60))
    col_frac = [sum(1 for y in ys if match(px[x, y])) / len(ys) for x in range(w)]
    best_x, cur = (0, 0), None
    for x, f in enumerate(col_frac):
        if f >= 0.35:
            cur = x if cur is None else cur
        elif cur is not None:
            if x - cur > best_x[1] - best_x[0]:
                best_x = (cur, x)
            cur = None
    if cur is not None and w - cur > best_x[1] - best_x[0]:
        best_x = (cur, w)

    return (best_x[0], y0, best_x[1], y1)


def find_window_box(im, tol=8):
    """Locate the largest uniform interior rectangle (foreground terminal window)."""
    w, h = im.size
    px = im.load()
    counts = Counter()
    for y in range(int(h * 0.12), int(h * 0.88), 4):
        for x in range(int(w * 0.12), int(w * 0.88), 4):
            r, g, b = px[x, y]
            counts[(r // 4 * 4, g // 4 * 4, b // 4 * 4)] += 1

    # Skip pure/near-black and dark-wallpaper shadows (max(c) < 10)
    # so wallpapers never mask a real dark terminal (#1e1e1e Ubuntu, #0c0c0c Windows).
    ranked = [c for c, _ in counts.most_common(12) if max(c) >= 10]
    for bg in ranked[:5]:
        box = _box_for_bg(im, px, w, h, bg, tol)
        if box[2] - box[0] >= 200 and box[3] - box[1] >= 60 and box_uniformity(im, box, bg, tol) >= 0.75:
            return box, bg

    bg = counts.most_common(1)[0][0]
    return _box_for_bg(im, px, w, h, bg, tol), bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--box", help="x0,y0,x1,y1 fixed crop before auto-trim")
    ap.add_argument("--window", action="store_true",
                    help="auto-detect foreground terminal window before trimming empty rows")
    ap.add_argument("--allow-empty", action="store_true",
                    help="do not fail (exit 2) when black-bottom or missing terminal is detected")
    ap.add_argument("--pad", type=int, default=10)
    ap.add_argument("--thresh", type=int, default=110)
    ap.add_argument("--min-bright", type=int, default=4,
                    help="pixels per row above threshold to count the row as content")
    args = ap.parse_args()

    im = Image.open(args.src).convert("RGB")
    bg = None
    if args.box:
        x0, y0, x1, y1 = (int(v) for v in args.box.split(","))
        im = im.crop((x0, y0, x1, y1))
    elif args.window:
        box, bg = find_window_box(im)
        unif = box_uniformity(im, box, bg)
        bw, bh = box[2] - box[0], box[3] - box[1]
        if bw < 200 or bh < 60 or unif < 0.75 or max(bg) < 10:
            print("error: no terminal window detected in %s (bg=%s box=%s unif=%.2f)"
                  % (args.src, bg, box, unif), file=sys.stderr)
            if not args.allow_empty:
                sys.exit(2)
        im = im.crop(box)
        if has_black_bottom(im, min_frac=0.10):
            print("error: terminal window in %s has solid black band (partial VM redraw)" % args.src,
                  file=sys.stderr)
            if not args.allow_empty:
                sys.exit(2)

    w, h = im.size
    if bg is not None:
        px = im.load()
        rows = []
        for y in range(6, max(6, h - 6)):
            fg = 0
            for x in range(8, max(8, w - 20), 2):
                c = px[x, y]
                if max(abs(c[0] - bg[0]), abs(c[1] - bg[1]), abs(c[2] - bg[2])) > 30:
                    fg += 1
                    if fg >= args.min_bright:
                        rows.append(y)
                        break
    else:
        g = im.convert("L")
        px = g.load()
        rows = []
        for y in range(h):
            bright = 0
            for x in range(0, w, 2):
                if px[x, y] > args.thresh:
                    bright += 1
                    if bright >= args.min_bright:
                        rows.append(y)
                        break

    if args.window and (len(rows) < 5 or (rows[-1] - rows[0]) < 12):
        print("error: cropped terminal in %s has no readable text rows" % args.src, file=sys.stderr)
        if not args.allow_empty:
            sys.exit(2)

    if rows:
        top = max(0, rows[0] - args.pad)
        bot = min(h, rows[-1] + args.pad)
        im = im.crop((0, top, w, bot))

    im.save(args.dst)
    print("%s -> %s  %dx%d" % (args.src, args.dst, im.size[0], im.size[1]))


if __name__ == "__main__":
    main()
