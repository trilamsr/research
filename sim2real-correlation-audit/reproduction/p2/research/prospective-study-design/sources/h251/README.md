# H251 retained public inputs

Retrieved: 2026-08-11

These files are the small, calculation-relevant portion of the three public
sources fixed in `../../protocol-h251-three-source-real-record-application.md`.
Large videos, action arrays, and other media were not downloaded.

## AnkIle real01b R5

The `ankile/` directories retain each source card, `results.json`, dataset
lineage, dataset information, and initial-state manifest. They were downloaded
from the exact Hugging Face dataset revisions below. The source cards declare
the Apache-2.0 license.

| local name | Hugging Face dataset | revision |
|---|---|---|
| routing | `ankile/real01b-routing-d1-r5-threearm-checkpoint100000-iql-g0997-n16-heldout-sobol50` | `15d419013006f1e3e8363abbf95650f212eb77f6` |
| marker | `ankile/real01b-marker-d2-r5-trio-baseline-dp-iql-cfinal-n16-heval-sobolseed2026070704` | `cd5d0df42a622bcaad2b2a338396d4b6851cab9e` |
| square | `ankile/real01b-square-d2-r5-trio-baseline-dp-iql-s3fixfinal-n16-heval-sobolseed2026070901` | `d2d109029967c27fad4e09637206cfe7614ff3de` |

## Toyota Research Institute / Dryad

`tri/dryad-v4.zip` is the complete 1.38 MB Dryad version 4 download for DOI
`10.5061/dryad.xd2547dxc`; `tri/files/` is its extracted content. Dryad records
publication and last modification on 2026-04-07 and declares CC0-1.0. The zip
was retrieved from `https://datadryad.org/api/v2/versions/435338/download`.

## RoboArena

RoboArena's 3,883 metadata files contain potentially identifying evaluator
and free-text fields, so they are not vendored here. The analysis reads an
already downloaded or remotely reconstructed tree for
`RoboArena/DataDump_07-17-2026` revision
`7931db81f3f6a48a3245427f7213a4c461f92ccc` and writes only aggregates. The
source dataset declares the MIT license.

The canonical analysis output records SHA-256 for every retained file it uses.
