# Reproduction packages

This directory is the canonical home for the standalone reproduction
packages distributed with the two active papers.

- `p1/` reproduces the finite-panel correlation audit and its paper-facing
  tables, figures, analyses, and PDFs.
- `p2/` reproduces the identification, minimax, route-graph, finite-sample,
  and fixed public-record analyses and its PDFs.

The package directories are generated snapshots. Do not edit them directly.
Edit the canonical files elsewhere in the project, then rebuild both packages:

```bash
.venv/bin/python reproduction/build_packages.py
```

Each package contains its own instructions, pinned Python dependencies, and
SHA-256 manifest. From within either package, the complete offline gate is:

```bash
make install
make verify
```

PDF reconstruction additionally requires the system versions documented in
the package README. P2's H251 RoboArena result is shipped with a verified
canonical aggregate and an independent reconstruction; rerunning the
RoboArena-dependent source traversal requires the separately pinned public
snapshot named in the package.
