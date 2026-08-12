# P1 reproduction package

This standalone package reproduces the paper-facing results for **What Does a
Sim-to-Real Correlation Support?** from the retained audit records and derived
coordinates.

The package has three evidence boundaries:

1. It regenerates the manuscript's selected audit facts, decision results,
   tables, figures, sensitivities, and PDFs from retained inputs.
2. Figure-derived CSVs are retained derived inputs. Exact extraction can be
   rerun only where the corresponding extractor and public source asset are
   included.
3. It does not rerun the surveyed robot experiments, simulator training, or
   upstream policy evaluations.

## Reproduce

Python 3.12 is required. Node and Ruby are used by method-distinct challenge
implementations. Pandoc 3.10, Tectonic 0.16.9, and Poppler's `pdfunite` are
required to rebuild the PDFs.

```bash
make install
make verify
```

`SOURCE-MANIFEST.sha256` binds every distributed file. The complete-package
reader is `output/pdf/PAPER-with-supplement.pdf`.
