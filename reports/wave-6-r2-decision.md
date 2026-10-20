# Wave 6 — regression/R² decision

Status: not applicable to the current Credit Risk Assignment.

The current assignment target is binary `bad/default-risk`. Precision, recall, F1, accuracy, PR-AUC and threshold economics are the valid evaluation branch. R² is a regression metric and cannot be substituted into this classification model.

The available South German Credit fields do not provide a separate continuous business outcome such as loss amount, recovery amount, repayment duration outcome or profit. The continuous-looking `hoehe` field is an input feature, not a valid target for this assignment. Turning it into the target would create a different project and would not satisfy the Credit Risk brief.

Decision: do not invent a regression target or report an artificial R². If Marc’s rubric later requires a genuine regression task, create a separate target contract first, then run baseline mean prediction, MAE, RMSE/MSE, R², residual analysis, cross-validation and one frozen-test confirmation.
