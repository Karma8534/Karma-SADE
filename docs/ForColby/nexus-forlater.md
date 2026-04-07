# Nexus For Later

Living deferred / tabled / future-work tracker for Nexus.

Rules:
- This file is for real deferred work, experiments, benchmarks, and future candidates.
- Items move out when they are promoted into the active plan or completed.
- Do not treat anything here as implemented.
- Keep entries grounded in current runtime truth, not speculation.

## Deferred Tasks

| ID | Title | Type | Status | Why Deferred | Trigger To Promote | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| FL-001 | Benchmark Gemma 4 E4B against K2 `qwen3.5:4b` | Benchmark | Decided | Candidate model was pulled and tested against the current K2 floor | Re-open only if K2 runtime, quant, or Gemma build changes materially | Current runtime evidence says keep `qwen3.5:4b` as the K2 local floor. `gemma4:e4b` is installed but timed out on most bounded structured tasks. |
| FL-002 | Normalize historical binary/archive references to stale `claude-mem` ports | Cleanup | Deferred | Live code/docs were prioritized; binary/history rewrite is low-value and high-risk | Only if archive normalization is explicitly requested | Current known archive-style holdout was binary/historical, not runtime |

## Future Experiments

| ID | Experiment | Goal | Preconditions | Success Signal |
| --- | --- | --- | --- | --- |
| EXP-001 | Gemma 4 E4B role benchmark rerun | Determine whether Gemma 4 E4B beats K2 `qwen3.5:4b` for any real Nexus role after runtime changes | Re-run only if K2 runtime changes materially or a better Gemma quant/build is installed | Clear role win on latency/quality/reliability for at least one Nexus job |
| EXP-002 | Gemma 4 multimodal document pass | Test whether Gemma 4 meaningfully improves PDF/OCR/screenshot workflows | Multimodal invocation path available on K2/local stack | Better OCR/document understanding than current fragmented local path |

## Parking Lot

| ID | Idea | Reason Parked |
| --- | --- | --- |
| PK-001 | Use Gemma 4 as a future local multimodal layer | Worth evaluating, but not a current replacement for Claude Max CLI primary path |
