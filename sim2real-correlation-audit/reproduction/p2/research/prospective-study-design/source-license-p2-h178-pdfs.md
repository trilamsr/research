# P2 H178 arXiv source-license disposition

Date checked: 2026-07-28

Status: canonical packaging decision record.

## Decision

The standalone P2 reproduction package must not vendor any of the six H178
source PDFs. It instead includes an exact-version download-and-hash acquisition
script.

Four official arXiv records use arXiv's non-exclusive distribution license.
That license grants distribution rights to arXiv; this project does not treat
it as permission for third-party rebundling:

- AutoEval, `2503.24278v2`;
- GE-Sim 2.0, `2605.27491v1`;
- A Practical Recipe, `2606.10366v1`; and
- RoboDojo, `2607.04434v3`.

Two official records use Creative Commons Attribution 4.0:

- UMI-Bench 1.0, `2606.10382v1`; and
- GigaWorld-1, `2607.02642v1`.

For a uniform minimal package boundary, the two CC BY PDFs are also acquired
on demand rather than vendored.

## Exact source trace

| identity | arXiv version | PDF SHA-256 | official license URI |
|---|---|---|---|
| AutoEval | `2503.24278v2` | `734840964f233f46ce2c1b8e64427a9cb65ca140b4152a0c4fd339677fd7e45f` | `https://arxiv.org/licenses/nonexclusive-distrib/1.0/` |
| GE-Sim 2.0 | `2605.27491v1` | `af875445ebe487962e308bbff5e76e19fdcfc57620a50ec6ec9070989cbfe641` | `https://arxiv.org/licenses/nonexclusive-distrib/1.0/` |
| A Practical Recipe | `2606.10366v1` | `0196e433f9523815aeb0e3151e069a466c614e838bc681883bac52a2d9160ab2` | `https://arxiv.org/licenses/nonexclusive-distrib/1.0/` |
| UMI-Bench 1.0 | `2606.10382v1` | `cd279ae9758460c2b1142b721ce2e0184b8adba755b21dc5319d03918ec90e2b` | `https://creativecommons.org/licenses/by/4.0/` |
| GigaWorld-1 | `2607.02642v1` | `15c685a1cfcd9b88635328b29d62f5cb7c8c55b7e1d12799a5a7a6c33a092a0f` | `https://creativecommons.org/licenses/by/4.0/` |
| RoboDojo | `2607.04434v3` | `e07c215f30169dde6a792c34b046b1f54818d09331763988732dcf9ead89a9d4` | `https://arxiv.org/licenses/nonexclusive-distrib/1.0/` |

The official record for each version is
`https://arxiv.org/abs/<version>`. The acquisition implementation is
`acquire_p2_h178_bound_pdfs.py`. Public availability is not treated as
redistribution permission.

