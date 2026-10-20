from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


BASE = {
    "monthly_applications": 8000,
    "max_monthly_reviews": 1600,
    "review_cost": 35.0,
    "lgd": 6000.0,
    "review_effectiveness": 0.45,
    "performing_contribution": 1200.0,
    "abandonment_rate": 0.05,
}

SCENARIOS = {
    "base": BASE,
    "conservative": {
        **BASE,
        "review_effectiveness": 0.30,
        "lgd": 4000.0,
        "review_cost": 45.0,
        "abandonment_rate": 0.08,
    },
    "adverse": {
        **BASE,
        "review_effectiveness": 0.20,
        "lgd": 3000.0,
        "review_cost": 60.0,
        "abandonment_rate": 0.10,
    },
    "upside": {
        **BASE,
        "review_effectiveness": 0.60,
        "lgd": 8000.0,
        "review_cost": 25.0,
        "abandonment_rate": 0.03,
    },
}


def scenario_metrics(policy: dict, scenario_name: str, assumptions: dict) -> dict:
    n = policy["tn"] + policy["fp"] + policy["fn"] + policy["tp"]
    scale = assumptions["monthly_applications"] / n
    reviews = (policy["fp"] + policy["tp"]) * scale
    prevented = policy["tp"] * scale * assumptions["review_effectiveness"]
    gross_avoided = prevented * assumptions["lgd"]
    review_cost = reviews * assumptions["review_cost"]
    friction = policy["fp"] * scale * assumptions["abandonment_rate"] * assumptions["performing_contribution"]
    net = gross_avoided - review_cost - friction
    missed = policy["fn"] * scale * assumptions["review_effectiveness"] * assumptions["lgd"]
    return {
        "scenario": scenario_name,
        "sample_size": n,
        "threshold": policy["threshold"],
        "tn": policy["tn"],
        "fp": policy["fp"],
        "fn": policy["fn"],
        "tp": policy["tp"],
        "accuracy": policy["accuracy"],
        "precision": policy["precision"],
        "recall": policy["recall"],
        "f1": policy["f1"],
        "monthly_reviews": reviews,
        "review_capacity": assumptions["max_monthly_reviews"],
        "expected_defaults_prevented": prevented,
        "gross_loss_avoided": gross_avoided,
        "monthly_review_cost": review_cost,
        "lost_contribution_from_friction": friction,
        "net_screening_value": net,
        "cost_per_expected_default_prevented": review_cost / prevented if prevented else None,
        "missed_avoidable_loss": missed,
        "review_effectiveness": assumptions["review_effectiveness"],
        "lgd": assumptions["lgd"],
        "review_cost": assumptions["review_cost"],
        "abandonment_rate": assumptions["abandonment_rate"],
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest_path = root / "artifacts" / "manifests" / "wave-4-policy.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    recommended = manifest["recommended_policy"]
    test_recommended = next(
        row for row in manifest["test_evaluation"] if row["policy"] == "recommended_capacity_constrained"
    ) if "policy" in manifest["test_evaluation"][0] else None
    # The stored test rows are keyed by policy only in the CSV; reconstruct from the CSV for exact counts.
    test_csv = root / "artifacts" / "tables" / "wave-4-selected-model-frozen-test-thresholds.csv"
    test_frame = pd.read_csv(test_csv)
    test_recommended = test_frame[test_frame["policy"] == "recommended_capacity_constrained"].iloc[0].to_dict()

    dev_rows = [scenario_metrics(recommended, name, assumptions) for name, assumptions in SCENARIOS.items()]
    test_rows = [scenario_metrics(test_recommended, name, assumptions) for name, assumptions in SCENARIOS.items()]
    out = root / "artifacts" / "tables"
    pd.DataFrame(dev_rows).to_csv(out / "wave-5-sensitivity-development.csv", index=False)
    pd.DataFrame(test_rows).to_csv(out / "wave-5-sensitivity-test.csv", index=False)
    policy = {
        "model": manifest["selected_model"],
        "operating_policy": "rank applications by predicted bad-risk score and send the top 20% to enhanced manual review; never auto-approve or auto-reject",
        "threshold_reference": recommended["threshold"],
        "capacity": BASE["max_monthly_reviews"],
        "monthly_volume": BASE["monthly_applications"],
        "development_sensitivity": dev_rows,
        "test_sensitivity": test_rows,
        "limitations": [
            "South German Credit is a historical proxy, not a directly observed 12-month default target.",
            "The business assumptions are scenario inputs, not measured outcomes in the dataset.",
            "The policy is a review-prioritization aid and not an automatic lending decision.",
        ],
    }
    (root / "artifacts" / "manifests" / "wave-5-business-policy.json").write_text(json.dumps(policy, indent=2), encoding="utf-8")
    print(json.dumps({"status": "complete", "model": policy["model"], "development": dev_rows, "test": test_rows}, indent=2))


if __name__ == "__main__":
    main()
