#!/usr/bin/env python3
"""Preprocess the paper Markdown for the PDF build: map Unicode math characters that the body
font cannot represent (they would be silently DROPPED from the PDF, corrupting values
like 10^-5 into 10) onto pandoc super/subscript syntax and inline math.

The Markdown itself keeps the Unicode—it renders correctly on GitHub; this rewrite
exists only inside the Pandoc pipeline.
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

# Pandoc's automatic width allocation gives short numeric columns the same share
# as prose-heavy columns in these two Section 6 tables. Keep PAPER.md portable
# Markdown, but give the PDF explicit, content-proportional widths.
TABLE_REPLACEMENTS = [
    (
        r"""| *k* | papers | ceiling | mass of one draw |
|---|---|---|---|
| 1 | RoboSnap, SC3-Eval, DreamDojo, dWorldEval, Colosseum V2, VISER | 1 | 100% |
| 2 | WEAVER, EmbodiedSplat, Mem-World, OSCAR, Hi-WM | 3 | 25% |
| 3 | REALM, WorldGym, Cosmos-Surg-dVRK, WM-PolicyEval | 10 | 3.70% |
| 4 | real2sim-eval, PolaRiS, SIMPLER, Digital Cousins, WorldEval, MolmoSpaces | 35 | 0.39% |
| 5 | A Practical Recipe, SimFoundry† | 126 | 0.032% |
| 8 | RoboWorld, Gemini/Veo | 6,435 | 0.000006% |
| 18 | PlayWorld | 4.5 × 10⁹ | ~10⁻²¹ % |""",
        r"""\begin{longtable}{@{}p{0.05\linewidth}>{\raggedright\arraybackslash}p{0.55\linewidth}p{0.14\linewidth}p{0.18\linewidth}@{}}
\hline
\textit{k} & papers & ceiling & mass of one draw \\
\hline
1 & RoboSnap, SC3-Eval, DreamDojo, dWorldEval, Colosseum V2, VISER & 1 & 100\% \\
2 & WEAVER, EmbodiedSplat, Mem-World, OSCAR, Hi-WM & 3 & 25\% \\
3 & REALM, WorldGym, Cosmos-Surg-dVRK, WM-PolicyEval & 10 & 3.70\% \\
4 & real2sim-eval, PolaRiS, SIMPLER, Digital Cousins, WorldEval, MolmoSpaces & 35 & 0.39\% \\
5 & A Practical Recipe, SimFoundry\textsuperscript{\dag} & 126 & 0.032\% \\
8 & RoboWorld, Gemini/Veo & 6,435 & 0.000006\% \\
18 & PlayWorld & $4.5 \times 10^9$ & $\sim 10^{-21}$\% \\
\hline
\end{longtable}""",
    ),
    (
        r"""| method | status |
|---|---|
| Cluster bootstrap | ≤35 atoms; lower endpoint set by 2–3 resamples of 256 |
| BCa | **unstable** — acceleration from 4 jackknife values, z₀ from a 35-atom distribution |
| Fisher-z | **works** — toy [+0.431, +1.000], rope [−0.800, +0.993] |
| Exact permutation | **works** — 4! = 24 labelings, minimum *p* = 0.0417 |
| Bayesian posterior | **works** — uniform prior on ρ, exact small-sample *r* density (Fisher 1915): toy [−0.163, +0.989], rope [−0.538, +0.901] (`research/real2sim-noise-floor/analyze_bayesian_interval.py`, released) |""",
        r"""\begin{longtable}{@{}p{0.22\linewidth}>{\raggedright\arraybackslash}p{0.70\linewidth}@{}}
\hline
method & status \\
\hline
Cluster bootstrap & $\leq 35$ atoms; lower endpoint set by 2--3 resamples of 256 \\
BCa & \textbf{unstable} --- acceleration from 4 jackknife values, $z_0$ from a 35-atom distribution \\
Fisher-z & \textbf{works} --- toy $[+0.431,+1.000]$, rope $[-0.800,+0.993]$ \\
Exact permutation & \textbf{works} --- $4!=24$ labelings, minimum $p=0.0417$ \\
Bayesian posterior & \textbf{works} --- uniform prior on $\rho$, exact small-sample $r$ density
(Fisher 1915): toy $[-0.163,+0.989]$, rope $[-0.538,+0.901]$
(\texttt{bayes\_interval.py}, released) \\
\hline
\end{longtable}""",
    ),
]
for src, dst in TABLE_REPLACEMENTS:
    if src in text:
        text = text.replace(src, dst)

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
