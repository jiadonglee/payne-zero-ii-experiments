# Payne Zero II: experiments

Experiment scripts, preregistrations, closeout notes, and result summaries for

> J. Li & Y.-S. Ting, *The Payne Zero Project II: A robust atmosphere solver for
> M giants*.

The solver and synthesis code is [Payne Zero](https://github.com/tingyuansen/payne-zero)
(Paper I). This repository holds only the files that Paper II adds to or changes
in a Payne Zero checkout. Copied over Payne Zero commit `9c44001`, it gives the
code state used for the paper.

## Layout

| Path | Contents |
|---|---|
| `experiments/` | Run drivers, analyses, and cluster launch scripts. `reduced_state_emulator/` holds the two- and six-profile networks, restarts, and the M-giant bootstrap; `analytic_initializer/` the analytic starts. |
| `reduced_state/` | Reconstruction of a full atmosphere deck from column mass and temperature, and the solver adapter used for restarts. |
| `payne_zero_diffatm/` | Differentiable research twin of the atmosphere iteration, with `check_*` comparisons against the solver. |
| `bench/`, `continuity/` | Reference runs, deck perturbation, and the continuity harness. |
| `payne_zero_figures/` | Figure and report scripts with shared style. |
| `payne_zero_atmosphere/` | Solver files changed relative to Payne Zero. The added solver options are opt-in (`config.py`). |
| `notes/` | Preregistrations (`*_preregistration_*.md`) and closeouts (`*_closeout_*.md`), dated. |
| `results/` | Result summaries quoted by the closeouts and the paper. |

## Setup

Install Payne Zero at the paper's base commit, then copy this repository over it:

```bash
git clone https://github.com/tingyuansen/payne-zero.git
cd payne-zero
git checkout 9c44001
./install.sh
git clone https://github.com/jiadonglee/payne-zero-ii-experiments.git ../payne-zero-ii-experiments
git -C ../payne-zero-ii-experiments archive HEAD -- . ':(exclude)README.md' | tar -x
python -m pip install -e .
```

The `pyproject.toml` here replaces Payne Zero's (it adds `scipy`); install from the
overlaid checkout, not from this repository on its own.

Run experiments from the checkout root as modules, for example

```bash
PYTHONPATH=. python -m experiments.reduced_state_emulator.predict --help
```

The full restart campaigns ran on multi-core CPU nodes and an H100 GPU; their
launch scripts (`experiments/**/*.sh`) record the node layout and thread counts
used.

## Evidence

Each experiment has a preregistration written before its runs and a closeout
written after. Development, diagnostic, and sealed-holdout results are kept in
separate notes, and thresholds are those of the preregistration. Where a note and
a file in `results/` disagree, the file in `results/` is the reported number.

`notes/m_star_evidence_corrigendum_20260918.md` withdraws the M-dwarf causal
claims of earlier closeouts and states what the M-star runs support; its
machine-readable tally is `notes/ledgers/m_star_dual_path_validation_v1.json`.

Some files cited by the closeouts are not included: per-run arrays, training
corpora, input line lists, and full atmosphere products.

## License

BSD 3-Clause, as Payne Zero; see `LICENSE` and `NOTICE`.
