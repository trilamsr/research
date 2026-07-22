"""Coverage simulation for the hybrid 'Fisher-z reference bound' used with
clustered data (16 points in k=4 clusters, Digital-Cousins-style geometry).

Intervals (95% nominal):
  I1 hybrid : tanh(atanh(r_pooled) +/- 1.96 * 1/sqrt(k-3)), k=4  -> half-width 1.96 on z-scale
  I2 agg-z  : r over 4 cluster means, Fisher-z with n=4 (1/sqrt(n-3)=1)
  I3 naive  : r_pooled, Fisher-z with n=16 (1/sqrt(13))

Estimands:
  E1 = rho_unit (unit/cluster-level correlation)
  E2 = pooled population corr = (rho_unit + sigma^2 * rho_within) / (1 + sigma^2)

Generative model: cluster i: (a_i,b_i) ~ BVN(0, corr=rho_unit, var 1);
point j: x_ij = a_i + eps_ij, y_ij = b_i + del_ij, (eps,del) ~ BVN(0, corr=rho_within, sd sigma).
Outlier condition: cluster 4's x-values shifted +3 (3 cluster-sd leverage point).

Binomial condition (the surveyed data are success rates, not Gaussians): the latent
point values are pushed through a logistic link to probabilities and observed as
Bin(n_ep, p)/n_ep with n_ep = 20 episodes (the surveyed papers use 16-40); the
estimand is the latent unit-level rho_unit. This asks whether binomial observation
noise breaks the intervals' coverage of the unit-level correlation.

Runnable end-to-end; numpy only; seed fixed. Default is 10,000 replications per
condition; pass --quick for 1,000 replications (faster, noisier -- for impatient
reviewers; the paper numbers use the default).
"""
import argparse

import numpy as np

NSIM = 10_000
K, M = 4, 4          # clusters, points per cluster
Z = 1.96
rng = np.random.default_rng(20260720)


def corr_rows(x, y):
    """Row-wise Pearson correlation for 2D arrays (nsim, n)."""
    xc = x - x.mean(axis=1, keepdims=True)
    yc = y - y.mean(axis=1, keepdims=True)
    num = (xc * yc).sum(axis=1)
    den = np.sqrt((xc**2).sum(axis=1) * (yc**2).sum(axis=1))
    return np.clip(num / den, -0.999999, 0.999999)


def bvn(nsim, n, rho, sd):
    z1 = rng.standard_normal((nsim, n))
    z2 = rng.standard_normal((nsim, n))
    a = z1 * sd
    b = (rho * z1 + np.sqrt(1 - rho**2) * z2) * sd
    return a, b


def simulate(rho_u, rho_w, sigma, outlier=False):
    a, b = bvn(NSIM, K, rho_u, 1.0)                    # cluster effects
    eps, del_ = bvn(NSIM, K * M, rho_w, sigma)         # point noise
    x = np.repeat(a, M, axis=1) + eps
    y = np.repeat(b, M, axis=1) + del_
    if outlier:                                        # cluster 4 shifted +3 sd in x
        x[:, (K - 1) * M:] += 3.0
    r_pool = corr_rows(x, y)
    xm = x.reshape(NSIM, K, M).mean(axis=2)
    ym = y.reshape(NSIM, K, M).mean(axis=2)
    r_agg = corr_rows(xm, ym)

    zp, za = np.arctanh(r_pool), np.arctanh(r_agg)
    ivs = {
        "I1_hybrid": (np.tanh(zp - Z * 1.0), np.tanh(zp + Z * 1.0)),
        "I2_agg_z":  (np.tanh(za - Z * 1.0), np.tanh(za + Z * 1.0)),
        "I3_naive":  (np.tanh(zp - Z / np.sqrt(13)), np.tanh(zp + Z / np.sqrt(13))),
    }
    E1 = rho_u
    E2 = (rho_u + sigma**2 * rho_w) / (1 + sigma**2)
    out = {}
    for name, (lo, hi) in ivs.items():
        out[name] = {
            "cov_E1": np.mean((lo <= E1) & (E1 <= hi)),
            "cov_E2": np.mean((lo <= E2) & (E2 <= hi)),
            "width": np.median(hi - lo),
        }
    return E2, out


def simulate_binomial(rho_u, rho_w, sigma, n_ep=20):
    """Same clustered latents; rates observed as Bin(n_ep, logistic(latent))/n_ep."""
    a, b = bvn(NSIM, K, rho_u, 1.0)
    eps, del_ = bvn(NSIM, K * M, rho_w, sigma)
    lat_x = np.repeat(a, M, axis=1) + eps
    lat_y = np.repeat(b, M, axis=1) + del_
    px = 1.0 / (1.0 + np.exp(-lat_x))
    py = 1.0 / (1.0 + np.exp(-lat_y))
    x = rng.binomial(n_ep, px) / n_ep
    y = rng.binomial(n_ep, py) / n_ep
    # degenerate rows (zero variance on an axis) are dropped and counted
    def safe(rr):
        return rr[np.isfinite(rr)]
    with np.errstate(invalid="ignore", divide="ignore"):
        r_pool = corr_rows(x, y)
        xm = x.reshape(NSIM, K, M).mean(axis=2)
        ym = y.reshape(NSIM, K, M).mean(axis=2)
        r_agg = corr_rows(xm, ym)
    keep = np.isfinite(r_pool) & np.isfinite(r_agg)
    r_pool, r_agg = r_pool[keep], r_agg[keep]
    zp, za = np.arctanh(r_pool), np.arctanh(r_agg)
    ivs = {
        "I1_hybrid": (np.tanh(zp - Z * 1.0), np.tanh(zp + Z * 1.0)),
        "I2_agg_z":  (np.tanh(za - Z * 1.0), np.tanh(za + Z * 1.0)),
        "I3_naive":  (np.tanh(zp - Z / np.sqrt(13)), np.tanh(zp + Z / np.sqrt(13))),
    }
    E1 = rho_u
    out = {}
    for name, (lo, hi) in ivs.items():
        out[name] = {
            "cov_E1": np.mean((lo <= E1) & (E1 <= hi)),
            "cov_E2": float("nan"),   # pooled estimand not defined on the rate scale
            "width": np.median(hi - lo),
        }
    return keep.mean(), out


def main():
    global NSIM
    ap = argparse.ArgumentParser(
        description="Coverage simulation for the hybrid Fisher-z reference bound "
                    "on clustered data (4 clusters x 4 points). See module docstring.")
    ap.add_argument("--quick", action="store_true",
                    help="run 1,000 replications per condition instead of 10,000 "
                         "(faster, noisier; paper numbers use the default)")
    args = ap.parse_args()
    if args.quick:
        NSIM = 1_000

    rows = []
    for rho_u in (0.0, 0.5, 0.9, 0.95):
        for sigma in (0.3, 0.7):
            for case, rho_w in (("match", rho_u), ("zero", 0.0)):
                E2, res = simulate(rho_u, rho_w, sigma)
                rows.append((rho_u, sigma, case, False, E2, res))
    # outlier condition: primary case (rho_w = rho_u), both sigmas
    for rho_u in (0.0, 0.5, 0.9, 0.95):
        for sigma in (0.3, 0.7):
            E2, res = simulate(rho_u, rho_u, sigma, outlier=True)
            rows.append((rho_u, sigma, "match", True, E2, res))

    hdr = (f"{'rho_u':>5} {'sig':>4} {'rho_w':>5} {'outl':>4} {'E2':>6} | "
           f"{'I1cE1':>6} {'I1cE2':>6} {'I1w':>5} | "
           f"{'I2cE1':>6} {'I2cE2':>6} {'I2w':>5} | "
           f"{'I3cE1':>6} {'I3cE2':>6} {'I3w':>5}")
    print(hdr)
    print("-" * len(hdr))
    for rho_u, sigma, case, outl, E2, res in rows:
        cells = []
        for k in ("I1_hybrid", "I2_agg_z", "I3_naive"):
            r = res[k]
            cells.append(f"{r['cov_E1']:6.3f} {r['cov_E2']:6.3f} {r['width']:5.3f}")
        print(f"{rho_u:5.2f} {sigma:4.1f} {case:>5} {str(outl):>4} {E2:6.3f} | "
              + " | ".join(cells))

    print("\nBinomial condition (rates = Bin(20, logistic(latent))/20; coverage of latent rho_u):")
    print(f"{'rho_u':>5} {'sig':>4} {'rho_w':>5} {'kept':>5} | {'I1cE1':>6} {'I1w':>5} | "
          f"{'I2cE1':>6} {'I2w':>5} | {'I3cE1':>6} {'I3w':>5}")
    for rho_u in (0.0, 0.5, 0.9, 0.95):
        for sigma in (0.3, 0.7):
            kept, res = simulate_binomial(rho_u, rho_u, sigma)
            cells = [f"{res[k]['cov_E1']:6.3f} {res[k]['width']:5.3f}"
                     for k in ("I1_hybrid", "I2_agg_z", "I3_naive")]
            print(f"{rho_u:5.2f} {sigma:4.1f} {rho_u:5.2f} {kept:5.3f} | " + " | ".join(cells))


if __name__ == "__main__":
    main()
