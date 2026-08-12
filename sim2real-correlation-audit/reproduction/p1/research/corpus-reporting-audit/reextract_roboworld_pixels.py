#!/usr/bin/env python
"""Pixel-based re-extraction of RoboWorld Fig 9a (arXiv:2607.01060v4).

Fully independent of the vector extraction: renders the figure PDF to a raster
at 300 dpi, finds gridlines and markers by pixel operations only (numpy), and
calibrates pixel->data from the rendered gridlines + the printed tick values
(800..1600 on x; 2.2..3.0 on y, read off the rendered figure by eye).
Nothing from the vector extraction's calibration or coordinates is used until
the final comparison step. The v3 and v4 scientific source trees and this
figure are byte-identical; see review-roboworld-version-provenance.md.
"""
import argparse
import csv
import sys
from pathlib import Path

import numpy as np

DEFAULT_PDF = "ranking_plot_compare_gpt_gemini_pearson_score.pdf"
PDF_HELP = (
    "path to the RoboWorld e-print figure PDF. To obtain it: download "
    "https://arxiv.org/e-print/2607.01060v4, extract the archive, and use "
    "appendix_figure/ranking_plot_compare_gpt_gemini_pearson_score.pdf"
)
CSV_PATH = Path(__file__).resolve().parent / "sources" / "source-roboworld.csv"
DPI = 300

X_TICKS = [800, 1000, 1200, 1400, 1600]      # left-to-right, read from figure
Y_TICKS = [3.0, 2.8, 2.6, 2.4, 2.2]          # top-to-bottom, read from figure

LEGEND_ORDER = ["Pi0.5", "Pi0 Fast", "PaliGemma VQ", "PaliGemma Diffusion",
                "PaliGemma Fast Specialist", "PaliGemma Fast", "Pi0",
                "PaliGemma Binning"]   # top-to-bottom, read from the rendered legend


def cluster(idx, gap=5):
    """Group sorted pixel indices into runs no more than `gap` apart; return run means."""
    groups, cur = [], [idx[0]]
    for v in idx[1:]:
        if v - cur[-1] <= gap:
            cur.append(v)
        else:
            groups.append(cur); cur = [v]
    groups.append(cur)
    return [float(np.mean(g)) for g in groups]


def components(mask_bool):
    """8-connected components of a boolean mask, as lists of (y, x) pixels."""
    ys, xs = np.where(mask_bool)
    pix_set = set(zip(ys.tolist(), xs.tolist()))
    comps, seen = [], set()
    for seed in pix_set:
        if seed in seen:
            continue
        stack, members = [seed], []
        seen.add(seed)
        while stack:
            y, x = stack.pop()
            members.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    p = (y + dy, x + dx)
                    if p in pix_set and p not in seen:
                        seen.add(p)
                        stack.append(p)
        comps.append(members)
    return comps


def erode(m, r):
    """Binary erosion of mask `m` with a (2r+1)x(2r+1) square structuring element."""
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out &= np.roll(np.roll(m, dy, axis=0), dx, axis=1)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Re-extract RoboWorld Fig 9a marker coordinates from the rendered "
                    "figure PDF by pixel operations only, then compare against the "
                    "vector extraction in sources/source-roboworld.csv.")
    ap.add_argument("--pdf", default=DEFAULT_PDF, help=PDF_HELP)
    args = ap.parse_args()

    try:
        import fitz  # PyMuPDF
    except ImportError:
        sys.exit("error: PyMuPDF is not installed. Install it with:\n"
                 "  pip install pymupdf")
    if not Path(args.pdf).is_file():
        sys.exit(f"error: PDF not found: {args.pdf}\n"
                 f"Download https://arxiv.org/e-print/2607.01060v4, extract the archive,\n"
                 f"and pass --pdf appendix_figure/{DEFAULT_PDF}")

    # ------------------------------------------------------------ render
    doc = fitz.open(args.pdf)
    pix = doc[0].get_pixmap(dpi=DPI)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].astype(np.int16)
    H, W = img.shape[:2]
    print(f"rendered {W}x{H} @ {DPI}dpi")

    mx = img.max(axis=2)
    mn = img.min(axis=2)
    dark = mx < 100                       # spines, text, marker edges
    grid = (mn > 140) & (mx <= 235) & ((mx - mn) < 15)  # light-gray gridlines

    # ------------------------------------------------------------ panel frame (left panel only)
    half = int(W * 0.45)
    col_dark = dark[:, :half].sum(axis=0)
    frame_cols = np.where(col_dark > H * 0.4)[0]     # the two vertical spines
    row_dark = dark[:, frame_cols.min():frame_cols.max()].sum(axis=1)
    frame_rows = np.where(row_dark > (frame_cols.max() - frame_cols.min()) * 0.4)[0]

    clustered_cols = cluster(frame_cols)
    assert len(clustered_cols) >= 2, "could not recover both left-panel spines"
    cL, cR = clustered_cols[:2]
    rT, rB = cluster(frame_rows)[0], cluster(frame_rows)[-1]
    print(f"panel frame: x [{cL:.0f},{cR:.0f}]  y [{rT:.0f},{rB:.0f}]")
    x0, x1 = int(cL) + 6, int(cR) - 6
    y0, y1 = int(rT) + 6, int(rB) - 6

    # ------------------------------------------------------------ gridlines -> calibration
    sub_grid = grid[y0:y1, x0:x1]
    gcols = np.where(sub_grid.sum(axis=0) > (y1 - y0) * 0.5)[0]
    grows = np.where(sub_grid.sum(axis=1) > (x1 - x0) * 0.5)[0]
    vx = [c + x0 for c in cluster(gcols)]
    hy = [r + y0 for r in cluster(grows)]
    print(f"vertical gridlines ({len(vx)}): {[round(v,1) for v in vx]}")
    print(f"horizontal gridlines ({len(hy)}): {[round(v,1) for v in hy]}")
    assert len(vx) == len(X_TICKS) and len(hy) == len(Y_TICKS), "gridline count mismatch"

    ax, bx = np.polyfit(vx, X_TICKS, 1)
    ay, by = np.polyfit(hy, Y_TICKS, 1)
    rx = np.max(np.abs(np.polyval([ax, bx], vx) - np.array(X_TICKS)))
    ry = np.max(np.abs(np.polyval([ay, by], hy) - np.array(Y_TICKS)))
    print(f"calibration residuals: x {rx:.4f} data-units, y {ry:.5f} data-units")

    # ------------------------------------------------------------ legend palette (sampled from rendered legend swatches)
    leg_region = np.zeros((H, W), dtype=bool)
    leg_region[:, int(W * 0.82):] = True
    leg_mask = leg_region & ((mx - mn) > 20) & (mx < 245)
    leg_comps = sorted(components(erode(leg_mask, 3)), key=len, reverse=True)[:8]
    leg_comps.sort(key=lambda c: np.mean([p[0] for p in c]))   # top-to-bottom
    palette = []
    for name, c in zip(LEGEND_ORDER, leg_comps):
        arr = np.array(c)
        rgb = img[arr[:, 0], arr[:, 1]].mean(axis=0)
        palette.append((name, rgb))
        print(f"legend swatch {name:<26} rgb={tuple(round(v) for v in rgb)}  area={len(c)}")

    # ------------------------------------------------------------ markers: global near-palette mask, assign by colour
    panel = np.zeros((H, W), dtype=bool)
    panel[y0:y1, x0:x1] = True

    dmin = np.full((H, W), 1e9)
    for _, rgb in palette:
        d2 = ((img - rgb[None, None, :]) ** 2).sum(axis=2)
        np.minimum(dmin, d2, out=dmin)
    gmask = panel & (dmin < 45 ** 2)
    er = erode(gmask, 4)   # 9x9 erosion: kills the ~6px dashed trend line, keeps marker discs
    big = [c for c in components(er) if len(c) > 300]
    print(f"marker components found: {len(big)} (areas {sorted(len(c) for c in big)})")
    assert len(big) == 8, f"expected 8 markers, got {len(big)}"

    pts = []
    taken = set()
    for c in big:
        arr = np.array(c, dtype=float)
        cy, cx = arr[:, 0].mean(), arr[:, 1].mean()
        crgb = img[arr[:, 0].astype(int), arr[:, 1].astype(int)].mean(axis=0)
        dists = [((crgb - rgb) ** 2).sum() for _, rgb in palette]
        k = int(np.argmin(dists))
        assert k not in taken, f"colour {palette[k][0]} claimed twice"
        taken.add(k)
        pts.append((palette[k][0], ax * cx + bx, ay * cy + by, len(c)))

    # ------------------------------------------------------------ compare with vector CSV (matched by series name)
    vec = {}
    with open(CSV_PATH) as f:
        lines = [l for l in f if l.strip() and not l.startswith("#")]
        for row in csv.DictReader(lines):
            if row["panel"] == "9a_GPT-4o_score":
                vec[row["series"]] = (float(row["x_real"]), float(row["y_sim"]))
    xr = max(v[0] for v in vec.values()) - min(v[0] for v in vec.values())
    yr = max(v[1] for v in vec.values()) - min(v[1] for v in vec.values())

    rows = []
    for name, px_, py_, area in pts:
        vx_, vy_ = vec[name]
        rows.append((name, vx_, vy_, px_, py_, px_ - vx_, py_ - vy_, area))

    print("\nseries                      vec_x    vec_y    pix_x    pix_y      dx       dy    area")
    for r in rows:
        print(f"{r[0]:<26}{r[1]:9.2f}{r[2]:9.4f}{r[3]:9.2f}{r[4]:9.4f}{r[5]:+8.2f}{r[6]:+9.4f}{r[7]:6d}")

    def pearson(a, b):
        return float(np.corrcoef(a, b)[0, 1])

    vX = np.array([r[1] for r in rows]); vY = np.array([r[2] for r in rows])
    pX = np.array([r[3] for r in rows]); pY = np.array([r[4] for r in rows])
    r_vec, r_pix = pearson(vX, vY), pearson(pX, pY)
    print(f"\nPearson r  vector: {r_vec:.4f}   pixel: {r_pix:.4f}   published: 0.989")
    delta_r = abs(r_pix - r_vec)
    max_dx = np.max(np.abs(pX - vX))
    max_dy = np.max(np.abs(pY - vY))
    print(f"|dr| pixel-vs-vector: {delta_r:.5f}   pixel-vs-published: {abs(r_pix - 0.989):.5f}")
    print(f"max |dx|: {max_dx:.3f} RoboArena units ({max_dx/xr*100:.2f}% of x-range)")
    print(f"max |dy|: {max_dy:.4f} Score units ({max_dy/yr*100:.2f}% of y-range)")
    assert delta_r <= 0.0005, "pixel/vector Pearson mismatch"
    assert max_dx <= 1.0, "pixel/vector x-coordinate mismatch"
    assert max_dy <= 0.003, "pixel/vector y-coordinate mismatch"

    # drop-one r range from pixel data
    dr = [pearson(np.delete(pX, i), np.delete(pY, i)) for i in range(8)]
    print(f"pixel drop-one r range: {min(dr):.3f} .. {max(dr):.3f}  (vector: 0.798 .. 0.994)")
    print(f"pixel max |dr| drop-one: {max(abs(d - r_pix) for d in dr):.3f}  (vector: 0.191)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
