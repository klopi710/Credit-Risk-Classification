# Credit Risk Classification

## Slide 1 - Conclusion

Use Logistic Regression to rank applications by historical bad/default-risk score. Send exactly the highest-risk 20% to enhanced human review.

- Monthly scenario: 8,000 applications and 1,600 reviews.
- Development estimate: **EUR 2,635,600 conditional net screening value per month**.
- Frozen-test confirmation: **EUR 2,608,000 conditional net screening value per month**.
- Development recall: **42.1%**; the queue captures approximately 10 of every 24 historical bad-risk cases.
- Frozen-test recall: **41.7%**; the queue captures 25 of 60 bad-risk cases.

This is a review-prioritisation aid, not an automatic approval or rejection system. Applicants outside the queue continue through the ordinary human credit process.

## Slide 2 KPIs

The following figures use the development estimate scaled from 800 development cases to 8,000 monthly applications. The model selected 160 of 800 development cases, which becomes 1,600 of 8,000.

**Reviews: 1,600**  
(8,000 x 20% = 1,600; applications x review capacity = maximum monthly reviews)

**True positives: 1,010**  
(101 x 10 = 1,010; development TP scaled from 800 to 8,000 applications)

**False positives: 590**  
(59 x 10 = 590; development FP scaled from 800 to 8,000 applications)

**False negatives: 1,390**  
(139 x 10 = 1,390; development FN scaled from 800 to 8,000 applications)

**True negatives: 5,010**  
(501 x 10 = 5,010; development TN scaled from 800 to 8,000 applications)

**Accuracy: 75.3%**  
((1,010 + 5,010) / 8,000 = 75.3%; correct predictions divided by all applications)

**Precision: 63.1%**  
(1,010 / (1,010 + 590) = 63.1%; true positives divided by all flagged applications)

**Recall: 42.1%**  
(1,010 / (1,010 + 1,390) = 42.1%; captured bad-risk cases divided by all bad-risk cases)

**F1: 50.5%**  
(2 x 63.1% x 42.1% / (63.1% + 42.1%) = 50.5%; combines precision and recall)

**Expected defaults prevented: 454.5**  
(1,010 x 45% = 454.5; TP x review effectiveness = expected events prevented)

**Gross loss avoided: EUR 2,727,000**  
(454.5 x EUR 6,000 = EUR 2,727,000; expected events prevented x LGD)

**Review cost: EUR 56,000**  
(1,600 x EUR 35 = EUR 56,000; number of reviews x cost per review)

**Expected friction loss: EUR 35,400**  
(590 x 5% x EUR 1,200 = EUR 35,400; FP x abandonment rate x contribution)

**Conditional net screening value: EUR 2,635,600**  
(EUR 2,727,000 - EUR 56,000 - EUR 35,400 = EUR 2,635,600; gross loss avoided minus both costs)

**Cost per expected default prevented: EUR 123.21**  
(EUR 56,000 / 454.5 = EUR 123.21; total review cost divided by expected events prevented)

**Missed avoidable loss: EUR 3,753,000**  
(1,390 x 45% x EUR 6,000 = EUR 3,753,000; FN x review effectiveness x LGD)

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

The locked Logistic Regression/top-20% policy selected 40 of 200 test applications:

- TN=125, FP=15, FN=35, TP=25.
- Accuracy = (25 + 125) / 200 = 75.0%.
- Precision = 25 / (25 + 15) = 62.5%.
- Recall = 25 / (25 + 35) = 41.7%.
- F1 = 50.0%.

Scaling the frozen-test rates to 8,000 monthly applications means multiplying the 200-case counts by 40:

- TP=1,000, FP=600, FN=1,400, TN=5,000.
- The 1,600 reviewed applications are TP + FP: 1,000 + 600.

The test-based scenario calculation is:

(1,000 x 45% x EUR 6,000) - (1,600 x EUR 35) - (600 x 5% x EUR 1,200)

= EUR 2,700,000 - EUR 56,000 - EUR 36,000 = EUR 2,608,000.

This is a confirmation estimate, not a new tuning result. The model was selected using development data, and the frozen test was used once for confirmation.

### Interpretation

Precision of 62.5% means that, among the 40 test applications selected for review, 25 were historically labelled bad/default-risk and 15 were labelled good/performing. Recall of 41.7% means that the queue captured 25 of the 60 historical bad-risk test cases and missed 35.

The model is therefore useful for prioritising scarce human attention, but it does not identify every risky applicant. It should supplement human reviewers and existing credit controls. It must not replace human judgement or automatically approve or reject applications.

The 8,000-application scaling is an extrapolation from the 200-row frozen test and the 800-row development sample. It assumes that historical rates represent future monthly applications. That assumption requires prospective validation.

## Slide 5 - Threshold Table - Model Results

All development rows use the same exact top-20% capacity policy and are scaled to 8,000 monthly applications. The frozen-test row is the locked Logistic Regression confirmation.

| Split | Model and policy | Reviews / month | TP | FP | FN | TN | Accuracy | Precision | Recall | F1 | Gross loss avoided / month | Net value / month |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Development OOF | Majority baseline; top 20% | 1,600 | 530 | 1,070 | 1,870 | 4,530 | 63.3% | 33.1% | 22.1% | 26.5% | EUR 1,431,000 | EUR 1,310,800 |
| Development OOF | Logistic Regression; top 20% | 1,600 | 1,010 | 590 | 1,390 | 5,010 | 75.3% | 63.1% | 42.1% | 50.5% | EUR 2,727,000 | EUR 2,635,600 |
| Development OOF | Decision Tree; top 20% | 1,600 | 820 | 780 | 1,580 | 4,820 | 70.5% | 51.3% | 34.2% | 41.0% | EUR 2,214,000 | EUR 2,111,200 |
| Development OOF | Random Forest; top 20% | 1,600 | 970 | 630 | 1,430 | 4,970 | 74.3% | 60.6% | 40.4% | 48.5% | EUR 2,619,000 | EUR 2,525,200 |
| Frozen test | Logistic Regression; top 20% | 1,600 | 1,000 | 600 | 1,400 | 5,000 | 75.0% | 62.5% | 41.7% | 50.0% | EUR 2,700,000 | EUR 2,608,000 |

The development rows are used for model selection. The frozen-test row is confirmation only. No row represents measured real-world default prevention or guaranteed profit.

## Slide 6 - Dataset Information

South German Credit, 1,000 historical applications. 20 predictors. 700 good. 300 bad.

Prediction moment: before the credit offer. We predict for good/bad default risk.

Suggestions;
- Pool more company data and standardise format with LLM models & human review.
- Iterate & improve the model over time > especially as LLM updates come out. Unecessary technical details are ommited from this presentation, they are not needed for decisions regarding the model, they are required for validity and implementation.

## Slide 7 - Recommendation Once Again

Use Logistic Regression as a review-prioritisation aid only.

The accepted development estimate is **EUR 2,635,600 conditional net screening value per month**, with 63.1% precision and 42.1% recall at the 1,600-review capacity. The frozen-test confirmation is **EUR 2,608,000**, with 62.5% precision and 41.7% recall.

The queue still misses approximately 58% of historical bad-risk cases. Therefore the model supplements human review and other controls; it does not replace them.

The operating rule is exact top-k ranking: rank all applications by bad-risk score and send the highest-risk 20% to review. Do not automatically approve or reject applications.

Before any real-world pilot, verify feature availability, outcome horizon, temporal validation, calibration, applicant-level exposure/LGD and governance for sensitive or proxy variables.

## Slide 8 - Thank you
