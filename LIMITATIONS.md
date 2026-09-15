# Limitations

What this system cannot do, and what another two weeks would fix.

---

## What It Cannot Do

### 1. It does not prove a gateway actually requires a visit

The current score counts hours where telemetry exceeded 3 standard deviations above the 28-day historical mean. This identifies *unusual* telemetry relative to a gateway's own history — it is not a calibrated failure probability. A high score may reflect a temporary network event rather than a hardware fault requiring a site visit.

### 2. It does not optimise the €380 / €600 operational cost

Part 1 reproduces the supplied baseline ranking. The score is "number of flagged hours," not expected cost. There is no threshold analysis, no cost-benefit evaluation, and no mechanism to weigh the €380 wasted-visit cost against the €600/week missed-broken-gateway cost.

### 3. Silent telemetry gaps are not part of the score

A gateway that stops emitting telemetry entirely produces no anomaly flags — it has no recent data to compare against the baseline. Such gateways may be the most urgent to visit, but they are invisible to the current 3-sigma approach.

### 4. Rank-cutoff ties remain ambiguous

Score ties at the rank-15 boundary occur in 7 out of 8 scoring weeks, with 3–4 gateways sharing the exact cutoff score. The current ordering preserves the baseline's implicit stable-sort behaviour, which depends on DataFrame insertion order rather than operational priority.

### 5. Reference and detection windows overlap

The 28-day reference window [T−28d, T) contains the 7-day detection window [T−7d, T). Recent abnormal observations inflate the baseline mean and standard deviation, reducing the system's sensitivity to sustained or worsening anomalies (self-normalisation). Our audit showed this changes top-15 membership by 4–7 gateways per week compared to a separated window.

### 6. Historical field visits are selection-biased observations

The 642 field visit records reflect gateways the operations team *chose* to visit — they are not a random sample of all gateway states. Training on or evaluating against these records without accounting for selection bias would overfit to the current dispatch policy rather than measure true gateway health.

### 7. Engineer review is temporally limited

The engineer review (`engineer_review_2026-02.xlsx`) was performed on 2026-02-15. Using it for scoring weeks before that date (2026-02-02 and 2026-02-09) would constitute future-data leakage. It covers only 120 of 332 gateways and represents a single point-in-time snapshot, not a continuous monitoring signal.

### 8. The system produces rankings and reasons, not calibrated uncertainty

Each gateway receives a discrete flagged-hours score and a text reason. There is no confidence interval, no probability estimate, and no indication of how sensitive the ranking is to small changes in telemetry. A gateway ranked 15th may be nearly indistinguishable from one ranked 20th.

---

## What Another Two Weeks Would Fix

### Days 1–3: Define "Needs a Visit"

Build a defensible outcome variable using field visit outcomes, telemetry trajectories, and meter-read evidence. Apply strict point-in-time rules so that every label used is available before the corresponding scoring Monday. Document which definition was chosen and which alternatives were rejected.

### Days 4–6: Rolling Backtest and Cost Simulator

Construct a week-by-week backtest across the 8 scoring weeks using the €380 wasted-visit and €600/week unresolved-broken-gateway costs. Establish the baseline's total operational cost as the benchmark. All evaluation uses data available before each prediction Monday.

### Days 7–9: Test Candidate Improvements

Evaluate concrete changes against the cost simulator:

- **Separated reference window** [T−28d, T−7d) to eliminate self-normalisation.
- **Silent telemetry features** — flag gateways with missing or zero-emission hours.
- **Tie-break strategies** — meter-read success rate, telemetry gap duration, or recent field visit history as secondary sort criteria.
- **Threshold / top-k policies** — test whether sending fewer than 15 visits in low-risk weeks or reserving slots for silent gateways reduces total cost.

### Days 10–11: Uncertainty and Sensitivity Analysis

Quantify how much the cost result moves when tested on different subsets of gateways and weeks. Report ranges rather than single numbers. Check performance on weeks and gateways not used during development (hold-out validation).

### Days 12–13: Operations Manager Deliverables

Produce charts showing the cost trade-off curve (wasted visits vs. missed broken gateways) as the dispatch threshold moves. Review the worst failure cases — which broken gateways were missed and why — and write the findings for a non-technical audience.

### Day 14: Reproducibility and Live-Change Readiness

Ensure the full pipeline regenerates from `make run`, all tests pass, documentation is consistent, and a single parameter change (e.g., adjusting the threshold) can be demonstrated live with people watching.
