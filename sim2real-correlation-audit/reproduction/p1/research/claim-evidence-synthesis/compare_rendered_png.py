#!/usr/bin/env python3
"""Compare two generated PNGs while tolerating renderer-only drift.

Matplotlib and FreeType versions can change antialiasing and the one-pixel
extent of a tight bounding box. Scientific values are asserted in the figure
generator; this check guards against a materially different rendered figure.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.image as mpimg
import numpy as np
from scipy.ndimage import zoom


def opaque_rgb(path: Path) -> np.ndarray:
    image = mpimg.imread(path).astype(float)
    if image.ndim != 3 or image.shape[2] not in (3, 4):
        raise ValueError(f"{path}: expected an RGB or RGBA image, got {image.shape}")
    if image.shape[2] == 4:
        image = image[..., :3] * image[..., 3:4] + (1.0 - image[..., 3:4])
    return image


def compare(reference: Path, candidate: Path) -> tuple[float, float]:
    a = opaque_rgb(reference)
    b = opaque_rgb(candidate)
    aspect_a = a.shape[1] / a.shape[0]
    aspect_b = b.shape[1] / b.shape[0]
    aspect_delta = abs(aspect_a - aspect_b) / aspect_a
    if aspect_delta > 0.02:
        raise AssertionError(
            f"{candidate}: aspect ratio differs by {aspect_delta:.2%} from {reference}"
        )

    resized = zoom(
        b,
        (a.shape[0] / b.shape[0], a.shape[1] / b.shape[1], 1),
        order=1,
    )
    resized = resized[: a.shape[0], : a.shape[1], :]
    if resized.shape != a.shape:
        raise AssertionError(f"resizing failed: {resized.shape} != {a.shape}")

    difference = np.abs(a - resized)
    mean_absolute_difference = float(difference.mean())
    fraction_large = float(np.mean(difference > 0.1))
    if mean_absolute_difference > 0.04 or fraction_large > 0.08:
        raise AssertionError(
            f"{candidate}: rendered content differs materially "
            f"(mean |delta|={mean_absolute_difference:.4f}, "
            f"fraction >0.1={fraction_large:.4f})"
        )
    return mean_absolute_difference, fraction_large


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    mean_delta, fraction_large = compare(args.reference, args.candidate)
    print(
        f"OK: {args.reference.name} render equivalent "
        f"(mean |delta|={mean_delta:.4f}, fraction >0.1={fraction_large:.4f})"
    )


if __name__ == "__main__":
    main()
