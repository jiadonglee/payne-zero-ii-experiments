# Cool-star pilot status

The solar-abundance pilot used `logg=5.0`, `[M/H]=0`, `[alpha/M]=0`, and
`vmic=1 km/s`.

## 3500 K continuation

Both 250 K paths reached 3500 K at the solver level:

| path | 4000 -> 3750 K | 3750 -> 3500 K |
| --- | ---: | ---: |
| full six-field carry | 28 iterations | 18 iterations |
| `(m,T)` rematerialized | 30 iterations | 18 iterations |

The two final 3500 K atmospheres agree closely: maximum relative differences
are 0.36% in column mass, 0.11% in temperature, and 0.58% in electron density.
Their 400--900 nm, `R=20,000` spectra also agree below the `5e-3` gate:

| metric | maximum difference |
| --- | ---: |
| normalized flux | 0.001126 |
| full flux | 0.001114 |
| continuum flux | 0.000128 |

This establishes a reproducible internal 3500 K continuation solution, not an
independent physical validation. At 3750 K, comparison with the MARCS-started
solution is just above the gate (`0.00598--0.00676` in normalized flux), so the
external reference is not yet resolved.

A fresh v2 remote rerun independently wrote the full-carry 3500 K product after
18 iterations, with final deep-layer change `3.185e-4`. Its NPZ file has a
different inode but is byte-for-byte identical to the earlier 250 K product;
the three-metric gate is therefore exactly zero. This is a useful
reproducibility check for the deterministic solver path, not an independent
MARCS validation. The matching v2 `(m,T)` rematerialized path has now completed.

The v2 rerun gives a direct paired check at the first continuation step: the
full-carry 4000 K -> 3750 K solve took 28 iterations, while the `(m,T)`-only
rematerialized solve took 30. Their 3750 K spectra pass all three metrics with
maxima `8.322e-4` (normalized flux), `7.549e-4` (full flux), and `2.228e-4`
(continuum). Thus the two-field route can reproduce the six-field solution at
3750 K, but it is slower in this pilot. The v2 two-field 3750 K -> 3500 K
step also converged in 18 iterations. Its 3500 K spectrum passes the same
three-metric gate against the full-carry continuation product:
`1.126e-3` (normalized flux), `1.114e-3` (full flux), and `2.228e-4`
(continuum). The corresponding six-field path took 28 + 18 iterations, while
the two-field path took 30 + 18. This is a successful internal two-field
recovery to 3500 K, but not an independent MARCS validation.

The v2 100 K full-carry follow-up completed 4000 K -> 3900 K and
3900 K -> 3800 K in 17 iterations each. Its 3800 K -> 3700 K step reached
the 30-iteration cap with final deep-layer residual `4.526e-2` and is a formal
solver failure; the trajectory became oscillatory after iteration 20.

In parallel, the adaptive reduced-state runner's direct 500 K step reached
the 30-iteration cap with final deep-layer residual `7.597e-2` and formally
failed. It then backtracked to 250 K: `4000 -> 3750 K` converged in 30
iterations with final deep-layer residual `1.983e-4`, and `3750 -> 3500 K`
converged in 18 iterations with final deep-layer residual `3.400e-4`. Both
accepted steps were 250 K. The final 3500 K product is finite, positive, and
strictly monotone in column mass.

The independent three-metric spectral gate for this adaptive 3500 K product
also passes against the formal six-field 3500 K reference:

| metric | maximum difference |
| --- | ---: |
| normalized flux | 0.001118 |
| full flux | 0.001110 |
| continuum flux | 0.000107 |

The independent 3750 K adaptive gate also passes:

| metric | maximum difference |
| --- | ---: |
| normalized flux | 0.000834 |
| full flux | 0.000756 |
| continuum flux | 0.000223 |

The formal v2 pilot summary is now complete. Its reduced-rematerialized 100 K
schedule converged at `4000 -> 3900 K` in 16 iterations and `3900 -> 3800 K`
in 19 iterations, then failed at `3800 -> 3700 K` after 30 iterations with
final residual `1.003e-1`. The full-carry 100 K path likewise failed at the
same boundary. The summary reports the 4000 K external reference as unresolved
because the MARCS anchor comparison misses the strict gate; therefore its
continuation `survival_rate=0` is a reference-status result, not evidence that
the internally compared full/reduced 250 K spectra failed.

A follow-up run starting from the converged 3750 K MARCS product and continuing
to 3500 K was performed independently for both initialization modes. Both
formal solver records and products are now available; the external spectral
comparisons are reported below.

The first full-carry and reduced-rematerialized follow-up processes were run in
parallel and stopped without a summary, so they are treated as interrupted
jobs rather than solver failures. Sequential retries were then run to a formal
result; neither interruption is included in the solver statistics below.

In parallel, a predictor-corrector initializer has been added for the direct
500 K question. It log-extrapolates the positive profiles from the converged
4000 K and 3750 K states; the reduced variant extrapolates only `(m,T)` and
reconstructs the other fields through the existing exact path. The new
plumbing passes the Linux unit suite (`6 passed, 1 skipped`). Both direct
predictor runs were stopped after oscillatory residuals failed to enter the
convergence region; neither produced a formal product.

The independent full-carry MARCS-started 3750 K -> 3500 K solve converged in
18 iterations and wrote a valid product. Its A100 spectral comparison against
the existing 250 K full-carry continuation product is not a gate pass:

| metric | maximum difference |
| --- | ---: |
| normalized flux | 0.006937 |
| full flux | 0.006793 |
| continuum flux | 0.001386 |

This confirms that the independent MARCS basin has not yet landed on the same
spectral fixed point. A strict all-layer reconvergence diagnostic was also run
from the 3750 K MARCS product; it kept the exact physics but added an
all-layer `5e-4` stopping condition before taking the 3500 K step.

The strict diagnostic has already shown a divergent source trajectory: after
the deep-layer residual reached `1.87e-1` and `1.13`, it grew to
`4.33e3` and then `inf`. This is evidence against a simple early-stop
explanation for the MARCS basin mismatch.

The two direct predictor diagnostics were stopped after their trajectories
clearly moved away from the convergence region, with logs preserved but no
structured product counted: the full predictor reached iteration 17 with a
deep-layer change of `3.08e-2`, while the reduced predictor reached iteration
12 with `1.64e-1`. The strict run reached iteration 30 with `inf` and was also
stopped before any invalid product could be retained.

The independent MARCS-started reduced-rematerialized 3750 K -> 3500 K solve
also converged in 18 iterations and wrote a valid product. Its final solver
diagnostics were `deep=4.280e-4` and `all-layer=2.380e-3`; the state had 80
finite, positive, monotone layers. Against the existing 250 K reduced
continuation product, the A100 spectral gate gave:

| metric | maximum difference |
| --- | ---: |
| normalized flux | 0.005911 |
| full flux | 0.005759 |
| continuum flux | 0.001469 |

Thus reduced rematerialization is modestly closer to the continuation spectrum
than full six-field carry in this independent-MARCS comparison, but it still
misses the `5e-3` gate. The products are recorded at
`runs/cool_star_marcs_to_3500_retry1_full/` and
`runs/cool_star_marcs_to_3500_retry1_reduced/`.

## 3500 K spectrum and structure comparison

The requested 3500 K comparison was synthesized on one common A100 grid:
400--900 nm, `R=20,000`, float64, with molecular lines enabled. The internal
six-field continuation is the fixed-point reference for the two-field route;
the MARCS benchmark is shown both as the native 56-layer structure and as
complete Payne-Zero endpoints reached from MARCS-derived starts.

| candidate versus reference | normalized flux max | total/continuum max | continuum relative max |
| --- | ---: | ---: | ---: |
| two-field continuation vs six-field continuation | 0.001126 | 0.001114 | 0.000128 |
| two-field continuation vs MARCS-started reduced | 0.005911 | 0.005768 | 0.001471 |
| two-field continuation vs MARCS-started full | 0.005811 | 0.005687 | 0.001261 |

The two-field and six-field continuation spectra are therefore essentially the
same and pass the `5e-3` three-metric bar. The MARCS-started endpoints are
nearby but sit just outside the normalized/total-flux bar; this is a benchmark
basin difference, not evidence that the two-field continuation failed.

Relative structure differences at the same 80-layer grid, measured against
the six-field continuation, are small for the two-field route: maximum
differences are 0.111% in `T`, 0.357% in `Pgas`, 0.583% in `ne`, 0.355% in
`rho`, and 0.156% in column-mass dex. The MARCS-started reduced endpoint has
larger maxima of 0.634%, 1.88%, 3.23%, 2.11%, and 0.867%, respectively. The
native raw MARCS node is only a 56-layer structural diagnostic; over the
overlapping `log m` range its temperature p95 difference from the six-field
profile is 0.823% and its electron-density p95 difference is 11.9%.

The figures and machine-readable arrays are in
`results/cool_star_3500_comparison_v3/`:

- `cool_star_3500_spectrum_comparison.pdf/png`
- `cool_star_3500_structure_comparison.pdf/png`
- `comparison_summary.json`, `structure_metrics.json`, and four spectrum NPZ files

To make the successful route usable without hand-selecting a schedule, a new
adaptive runner is available at
`experiments/reduced_state_emulator/cool_star_adaptive.py`. It first tries the
requested temperature step and halves it after a failed attempt, always
restarting from the latest converged state. The reduced mode only carries
`(m,T)` between attempts and reconstructs the other fields. Its policy tests
pass in the Linux suite (`8 passed, 1 skipped`); the existing 250 K solver
products remain the exact end-to-end validation of the fallback path.

## MARCS depth-coordinate probes

The raw MARCS grid does not use the Payne-Zero fixed Rosseland-depth grid. The
old log-mass remapping gives a 3750 K endpoint range of roughly
`m=0.0074--41.2`, whereas the converged Payne continuation spans roughly
`m=3.7e-4--83.4`. A direct `tau5000` remapping and a remapping after integrating
the exact Payne Rosseland opacity were tested as possible fixes. Neither solved
the problem: the direct `tau5000` trajectory reached residuals
`0.049, 0.038, 0.092, 0.064`, and the physical-Rosseland trajectory reached
`0.038, 0.041, 0.078, 0.060` before being stopped. Thus the MARCS mismatch is
not fixed by a simple change of depth coordinate alone.

## Direct analytic tests

The simple grey/hydrostatic initializer failed at 3500 K: after 30 iterations
its deep-layer change was 7.5%. The dedicated H2 direct-target runs now give
formal results for three temperatures. All three started from a finite,
positive, strictly monotone analytic `(m,T)` profile but failed the 30-iteration
solver criterion:

| target | iterations | final deep residual | final all-layer residual | max flux error |
| ---: | ---: | ---: | ---: | ---: |
| 3800 K | 30 | 0.0738 | 0.1167 | `3.80e6%` |
| 3700 K | 30 | 0.00864 | 0.0743 | `7.25e6%` |
| 3600 K | 30 | 0.1613 | 0.1613 | `3.46e6%` |

These are direct analytic target starts, not continuation from a converged
4000 K state. They therefore answer the no-emulator direct-start question:
the current H2 formula is not a reliable direct cool-star initializer even
though it is competitive on the broader 60-star warm-start funnel. The raw
auditable summaries are
`results/analytic_initializer/cool_star_h2_3800_summary.json`,
`cool_star_h2_3700_summary.json`, and `cool_star_h2_3600_summary.json`;
the 3750 K and 3500 K runs are still pending on Garching.

The separate emulator-free H2 population funnel gives a different, broader
result. On the same 60 held-out stars, the H2 formula converged on its first
solver trial for 55/60 stars, compared with 54/60 for the production emulator
start. Including the production retry, the totals are 55/60 and 56/60,
respectively; the H2 arm had no timeouts and 59/60 finite final states. This
supports the narrower claim that a Hopf-plus-opacity analytic formula can be a
competitive solver warm start without a neural network. It does not establish
cool-star accuracy or direct 4000 -> 3500 K convergence. The artifact is
`results/analytic_initializer/h2_paired_funnel60_result.json`; the dedicated
3900--3500 K H2 run is still pending on Garching.

## Nine-track confirmation

The Garching confirmation scan is now running on the frozen 9-track grid with
6 solver workers and 6 one-thread spectrum workers, with resume enabled. Its
manifest has been written to `results/cool_star_step_test_confirm/`; no
confirmation summary is available yet.

## Interpretation

The current evidence supports `4000 -> 3750 -> 3500` as a solver-level route
for the solar-abundance pilot. The full and reduced continuation products agree
internally, but both independent MARCS-started 3500 K products fail the strict
external spectral gate by a small margin. The direct 500 K predictor tests also
did not converge. Therefore this does not support the stronger claim that the
emulator is independently validated for all M dwarfs below 4000 K. The
9-track run is intended to measure how far this pilot result generalizes, not
to retroactively turn unresolved MARCS references into validated targets.
