# M-star evidence reproduction package

The canonical input is `../m_star_dual_path_validation_v1.json`. This package contains the six-label identities and their input hash, fixed configuration and config hash, scalar iteration diagnostics extracted from available result directories, final metrics, and a product manifest. Large NPZ/checkpoint products are intentionally not copied.

Regenerate the ledger CSV, summary, figure, and this package with:

```sh
PYTHONPATH=. python -m experiments.reduced_state_emulator.m_star_validation_ledger
```

`product_manifest.json` records which products are present locally and how to retrieve missing products from the paths in the closeouts.
