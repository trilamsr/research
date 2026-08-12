# Real2Sim upstream artifact audit

Snapshot checked 2026-07-23. This inventory asks whether the official release contains the inputs
needed to rerun the source paper's evaluations. It is not a requirement for reproducing this
correlation audit, whose extracted coordinates and computations are local and tested.

Official sources:

- paper: <https://arxiv.org/pdf/2511.04665v2>
- code: <https://github.com/kywind/real2sim-eval>
- artifact collection: <https://huggingface.co/collections/shashuo0104/real-to-sim-policy-eval>

| requested item | public-release finding | verdict |
|---|---|---|
| Policy weights for the iterations represented in Figures 3-4 | Twelve policy repositories expose many numbered checkpoints, with weights and (where applicable) optimizer/RNG state. The release contains plausible coverage of the plotted iterations, but no manifest maps each plotted point to an exact checkpoint. | **Partial:** weights are present; figure-to-checkpoint identity is not. |
| Per-task/policy/checkpoint real and simulated success rates behind Figure 3 | No CSV, JSON, results directory, or equivalent table was found in the official code tree or the 19-item artifact collection. The repository supplies evaluation and success-scoring programs, not the reported result matrix. | **Absent.** |
| Exact checkpoint iterations evaluated in Figures 3-4 | The supplied evaluation launchers identify one checkpoint per task-policy pair (typically the final/default evaluation), not every checkpoint plotted in Figures 3-4. The model repositories contain more checkpoints than the plotted point counts. | **Absent as an evaluation manifest.** |
| PhysTwin optimizer configuration | The three PhysTwin repositories contain `final_data.pkl`, a `best_*.pth`, and `optimal_params.pkl`. The code repository contains generic runtime physics defaults and points to the upstream PhysTwin project, but the released task artifacts have empty cards and no task-specific optimizer/training configuration. | **Partial:** fitted outputs and optimized parameters are present; the exact fitting configuration is not documented locally. |
| Multi-view RGB-D captures used to fit the twins | `gs-scans` contains one 152 MB `gs_scans.zip`; its card is empty. The three similarly named datasets in the collection are robot-policy training videos. No raw multi-view RGB-D capture set or capture manifest is identified in the collection. PhysTwin `final_data.pkl` files are processed fitting inputs, not documented raw captures. | **Not found.** |
| Realized grid initial states, or a seed sufficient to regenerate them | The code uses deterministic grid lists and calls `env.reset(seed=episode_id)`; the environment overloads that seed as the grid index. Each completed evaluation would write `random_variables.json`. However, the official release does not include those output directories or a manifest tying real trials to episode IDs. A top-level `seed: 0` exists but is not what the evaluation loop passes to reset. | **Partial:** simulation states can be regenerated from code/config and episode order; the realized real-trial pairing is absent. |

## What is actually present

The Hugging Face collection contains three policy-training datasets, twelve policy model
repositories (ACT, diffusion policy, Pi-0, and SmolVLA across three tasks), three PhysTwin model
repositories, and one Gaussian-splat scan repository. The PhysTwin repositories contain:

| repository | released task files |
|---|---|
| `phystwin-toy` | `final_data.pkl`, `best_199.pth`, `optimal_params.pkl` |
| `phystwin-rope` | `final_data.pkl`, `best_100.pth`, `optimal_params.pkl` |
| `phystwin-T-block` | `final_data.pkl`, `best_0.pth`, `optimal_params.pkl` |

The official evaluation code saves a resolved run configuration and per-episode randomized
variables when a run is performed. Those generated evaluation records are the missing bridge
between the released inputs and the paper's Figure 3 point matrix.

## Reproducibility boundary

The local audit package is sufficient to regenerate its claims about the published figures: it
ships the recovered integer success counts, provenance, exact MMRV implementation, and known-answer
tests. It is **not** sufficient—and does not claim to be sufficient—to rerun the source paper's real
robot experiment or reconstruct every Figure 3 point from original trials. That stronger
reproduction still requires the exact checkpoint-to-point manifest, underlying real/sim outcome
table, and real-trial initial-state pairing. Raw PhysTwin capture/config provenance would additionally
be required to refit rather than merely load the released twins.
