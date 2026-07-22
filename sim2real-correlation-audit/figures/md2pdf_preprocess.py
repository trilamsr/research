#!/usr/bin/env python3
"""Preprocess PAPER.md for the PDF build: map unicode math characters that the body
font cannot represent (they would be silently DROPPED from the PDF, corrupting values
like 10^-5 into 10) onto pandoc super/subscript syntax and inline math.

PAPER.md itself keeps the unicode -- it renders correctly on GitHub; this rewrite
exists only inside the pandoc pipeline. Usage: md2pdf_preprocess.py < PAPER.md | pandoc ...
"""
import sys

REPLACEMENTS = [
    ("10⁻⁵", "10^−5^"),
    ("10⁻²¹", "10^−21^"),
    ("10⁹", "10^9^"),
    ("z₀", "z~0~"),
    ("Rᵢ−Rⱼ", "R~i~−R~j~"),
    ("ρ ∈", "ρ $\\in$"),
    ("≲", "$\\lesssim$"),
]

text = sys.stdin.read()
for src, dst in REPLACEMENTS:
    text = text.replace(src, dst)

# Fail loudly if an unmapped droppable character remains: silent glyph loss is the
# exact failure mode this file exists to prevent.
# NB: ¹ ² ³ are Latin-1 (0xB9/0xB2/0xB3), present in Times New Roman, and render fine;
# only the Unicode super/subscript block (U+2070+) and math symbols get dropped.
DROPPABLE = "⁻⁰⁴⁵⁶⁷⁸⁹₀₁₂ᵢⱼ∈≲★⚠"
leftover = sorted({c for c in text if c in DROPPABLE})
if leftover:
    sys.stderr.write(f"md2pdf_preprocess: unmapped characters {leftover} -- add a replacement\n")
    sys.exit(1)
sys.stdout.write(text)
