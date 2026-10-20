# Feature availability and prediction-moment audit

## Operational assumption

The model is interpreted as a review-prioritization score computed at application submission, before any repayment outcome or review decision is known. The target `kredit` is not a future 12-month default field; it is a historical bad/good credit outcome.

## Availability table

| Feature class | Fields | Required availability | Evidence and boundary |
|---|---|---|---|
| Application terms | `laufzeit`, `hoehe`, `rate`, `verw` | At submission | Codebook describes requested terms; deployment must confirm these are pre-decision values. |
| Applicant profile | `pers`, `famges`, `alter`, `beruf`, `beszeit` | At submission | Codebook describes applicant attributes; `famges` must receive governance review because it is a personal-status/sex proxy. |
| Financial position | `sparkont`, `verm`, `wohn`, `bishkred`, `weitkred` | At submission | Historical codebook descriptions are compatible with application-time use, but source-system timestamps are unavailable. |
| Relationship and history | `laufkont`, `moral`, `buerge`, `wohnzeit`, `telef`, `gastarb` | At submission | Must be confirmed as known before the lending decision; `gastarb` is a foreign-worker proxy and is audited separately. |
| Outcome | `kredit` | After the prediction event | Excluded from `X`; maps `0` to positive `bad_default_risk`. It must never be available to the scoring service. |

## Gate

The code is leakage-safe with respect to the saved target column and cross-validation pipeline: the target is excluded, preprocessing is fitted inside each pipeline, and threshold/model selection uses development out-of-fold scores. The historical file does not prove feature timestamps or a future outcome horizon. Therefore this audit is a deployment precondition, not a claim that the old dataset is temporally valid.

Before any real pilot, obtain source-system timestamps, remove fields unavailable at submission, define the outcome horizon, and rerun the frozen protocol on a time-based validation sample.
