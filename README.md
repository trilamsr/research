# Auspex research

This repository holds the durable scientific record for Auspex research. Work
is organized by research program; each program documents its own canonical
inputs, outputs, reproduction paths, limitations, and operational status.

Git exposes only each program's current `PAPER.md`, `PAPER.pdf`, and
`reproduction/` package. Working research records remain local and are folded
into the manifest-bound reproduction package when a result is released.

| Program | Status | Canonical entry point |
|---|---|---|
| Sim-to-real decision audit and prospective studies | Active | [`sim2real-correlation-audit/`](sim2real-correlation-audit/) |
| PPI gold-channel and target-alignment research | Retired historical record | [`ppi-gold-bias/`](ppi-gold-bias/) |
| Contact-compliance / dynamics-sensitivity work | Retirement candidate; retained methods note and post-mortem | [`dynamics-fidelity/`](dynamics-fidelity/) |

Repository-wide consequential external findings are indexed in
[`FINDINGS.md`](FINDINGS.md). `RESEARCH-STANDARD.md` defines the scientific and
reproducibility requirements, and `AGENTS.md` defines repository operating
rules. Proposal files are organizational inputs, not scientific conclusions.

Temporary work belongs in a program's designated ignored scratch area. It
must not remain as a parallel top-level project, and nothing needed to
reproduce or interpret a result may exist only there.

Code is MIT-licensed under [`LICENSE`](LICENSE). Individual research artifacts
may identify additional source, data, or content licenses in their owning
records.
