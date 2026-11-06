# Credit Risk Classification

## Slide 1 - Conclusion

Use Random Forest to rank applications by historical bad/default-risk score. Send exactly the highest-risk 20% to enhanced human review.

- Monthly scenario: 8,000 applications and 1,600 reviews.
- Development estimate: **EUR 2,718,400 conditional net screening value per month**.
- Frozen-test confirmation: **EUR 2,497,600 conditional net screening value per month**.
- Development recall: **43.3%**; the queue captures approximately 13 of every 30 historical bad-risk cases.
- Frozen-test recall: **40.0%**; the queue captures 24 of 60 bad-risk cases.

This is a review-prioritisation aid, not an automatic approval or rejection system. Applicants outside the queue continue through the ordinary human credit process.

## Slide 2 KPIs

The following figures use the development estimate scaled from 800 development cases to 8,000 monthly applications. The model selected 160 of 800 development cases, which becomes 1,600 of 8,000.

**Reviews: 1,600**  
(8,000 x 20% = 1,600; applications x review capacity = maximum monthly reviews)

**True positives: 1,040**  
(104 x 10 = 1,040; development TP scaled from 800 to 8,000 applications)

**False positives: 560**  
(56 x 10 = 560; development FP scaled from 800 to 8,000 applications)

**False negatives: 1,360**  
(136 x 10 = 1,360; development FN scaled from 800 to 8,000 applications)

**True negatives: 5,040**  
(504 x 10 = 5,040; development TN scaled from 800 to 8,000 applications)

**Accuracy: 76.0%**  
((1,040 + 5,040) / 8,000 = 76.0%; correct predictions divided by all applications)

**Precision: 65.0%**  
(1,040 / (1,040 + 560) = 65.0%; true positives divided by all flagged applications)

**Recall: 43.3%**  
(1,040 / (1,040 + 1,360) = 43.3%; captured bad-risk cases divided by all bad-risk cases)

**F1: 52.0%**  
(2 x 65.0% x 43.3% / (65.0% + 43.3%) = 52.0%; combines precision and recall)

**Expected defaults prevented: 468**  
(1,040 x 45% = 468; TP x review effectiveness = expected events prevented)

**Gross loss avoided: EUR 2,808,000**  
(468 x EUR 6,000 = EUR 2,808,000; expected events prevented x LGD)

**Review cost: EUR 56,000**  
(1,600 x EUR 35 = EUR 56,000; number of reviews x cost per review)

**Expected friction loss: EUR 33,600**  
(560 x 5% x EUR 1,200 = EUR 33,600; FP x abandonment rate x contribution)

**Conditional net screening value: EUR 2,718,400**  
(EUR 2,808,000 - EUR 56,000 - EUR 33,600 = EUR 2,718,400; gross loss avoided minus both costs)

**Cost per expected default prevented: EUR 119.66**  
(EUR 56,000 / 468 = EUR 119.66; total review cost divided by expected events prevented)

**Missed avoidable loss: EUR 3,672,000**  
(1,360 x 45% x EUR 6,000 = EUR 3,672,000; FN x review effectiveness x LGD)

Model-running cost is not quantified and is therefore treated as zero in this scenario. The net screening value is not proven profit; it is conditional arithmetic based on the review-effectiveness, LGD, cost and abandonment assumptions.

Expected net screening value and missed avoidable loss answer different management questions:

- **Net screening value:** Is the proposed review programme expected to create positive incremental value after review and friction costs?
- **Missed avoidable loss:** How much potential loss remains among bad-risk cases that the review queue did not capture?

They should not be added together. The first is a net value estimate for the policy; the second is residual risk.

## Slide 3 Interpretation

### What changes if recall rises while precision falls?

Recall is how many of the positive classes we capture. In my opinion the most important metric.
Precision is out of all the positive class predictions (sent for human review) how many were actually in the positive class (were actually needed to be sent).

Higher recall while lower precision means we likely send more people for human review - and as such we are capturing more of the positive class but at higher cost.

### Which error is more expensive?

- One false negative = expected loss of 45% x EUR 6,000 = EUR 2,700.
- One false positive = expected loss of 5% x EUR 1,200 = EUR 60.

Therefore a false negative is potentially **45 times more expensive** than a false positive in the scenario. This alone is not definitive, but enough to priortise minimising false negatives.

### Why does prevalence matter?

Because that is what all our metrics depend on.
Prevalence = how many positive classes we have in the dataset > how many bad-risk cases.
In our case, 30%, if that was higher, our models should capture more of them since they are more "prevailent". And vice versa.

### Which policy should be used?

Rank bad-risk value (0-1) in descending order, send the top 20% for human review.
As they will be the highest risk for default, we should focus on them given our limited capacity.

### What information is missing?

- Did the default occur at any of them?
- Was the loan actually given? For how long?
- Do all defaults create the same loss? Unlikely.
- Economic conditions may also be useful > recession = higher defaults = higher risk
- A lot more data than 1000 rows.

## Slide 4 - Technical Explanation

### Frozen-test confirmation

The locked Random Forest/top-20% policy selected 40 of 200 test applications:

- TN=124, FP=16, FN=36, TP=24.
- Accuracy = (24 + 124) / 200 = 74.0%.
- Precision = 24 / (24 + 16) = 60.0%.
- Recall = 24 / (24 + 36) = 40.0%.
- F1 = 48.0%.

Scaling the frozen-test rates to 8,000 monthly applications means multiplying the 200-case counts by 40:

- TP=960, FP=640, FN=1,440, TN=4,960.
- The 1,600 reviewed applications are TP + FP: 960 + 640.

The test-based scenario calculation is:

(960 x 45% x EUR 6,000) - (1,600 x EUR 35) - (640 x 5% x EUR 1,200)

= EUR 2,592,000 - EUR 56,000 - EUR 38,400 = EUR 2,497,600.

This is a confirmation estimate, not a new tuning result. The model was selected using development data, and the frozen test was used once for confirmation.

### Interpretation

Precision of 60.0% means that, among the 40 test applications selected for review, 24 were historically labelled bad/default-risk and 16 were labelled good/performing. Recall of 40.0% means that the queue captured 24 of the 60 historical bad-risk test cases and missed 36.

The model is therefore useful for prioritising scarce human attention, but it does not identify every risky applicant. It should supplement human reviewers and existing credit controls. It must not replace human judgement or automatically approve or reject applications.

The 8,000-application scaling is an extrapolation from the 200-row frozen test and the 800-row development sample. It assumes that historical rates represent future monthly applications. That assumption requires prospective validation.

## Slide 5 - Threshold Table - Model Results

All development rows use the same exact top-20% capacity policy and are scaled to 8,000 monthly applications. The frozen-test row is the locked Random Forest confirmation.

| Split | Model and policy | Reviews / month | TP | FP | FN | TN | Accuracy | Precision | Recall | F1 | Gross loss avoided / month | Net value / month |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Development OOF | Majority baseline; top 20% | 1,600 | 550 | 1,050 | 1,850 | 4,550 | 63.8% | 34.4% | 22.9% | 27.5% | EUR 1,485,000 | EUR 1,366,000 |
| Development OOF | Logistic Regression; top 20% | 1,600 | 1,020 | 580 | 1,380 | 5,020 | 75.5% | 63.8% | 42.5% | 51.0% | EUR 2,754,000 | EUR 2,663,200 |
| Development OOF | Decision Tree; top 20% | 1,600 | 770 | 830 | 1,630 | 4,770 | 69.3% | 48.1% | 32.1% | 38.5% | EUR 2,079,000 | EUR 1,973,200 |
| Development OOF | Random Forest; top 20% | 1,600 | 1,040 | 560 | 1,360 | 5,040 | 76.0% | 65.0% | 43.3% | 52.0% | EUR 2,808,000 | EUR 2,718,400 |
| Frozen test | Random Forest; top 20% | 1,600 | 960 | 640 | 1,440 | 4,960 | 74.0% | 60.0% | 40.0% | 48.0% | EUR 2,592,000 | EUR 2,497,600 |

The development rows are used for model selection. The frozen-test row is confirmation only. No row represents measured real-world default prevention or guaranteed profit.

## Slide 6 - Dataset Information

South German Credit, 1,000 historical applications. 20 predictors. 700 good. 300 bad.

Prediction moment: before the credit offer. We predict for good/bad default risk.

Suggestions;
- Pool more company data and standardise format with LLM models & human review.
- Iterate & improve the model over time > especially as LLM updates come out. Unecessary technical details are ommited from this presentation, they are not needed for decisions regarding the model, they are required for validity and implementation.

## Slide 7 - Recommendation Once Again

Use Random Forest as a review-prioritisation aid only.

The accepted development estimate is **EUR 2,718,400 conditional net screening value per month**, with 65.0% precision and 43.3% recall at the 1,600-review capacity. The frozen-test confirmation is **EUR 2,497,600**, with 60.0% precision and 40.0% recall.

The queue still misses approximately 57% of historical bad-risk cases in development and 60% in the frozen test. Therefore the model supplements human review and other controls; it does not replace them.

The operating rule is exact top-k ranking: rank all applications by bad-risk score and send the highest-risk 20% to review. Do not automatically approve or reject applications.

Before any real-world pilot, verify feature availability, outcome horizon, temporal validation, calibration, applicant-level exposure/LGD and governance for sensitive or proxy variables.

## Slide 8 - Thank you
