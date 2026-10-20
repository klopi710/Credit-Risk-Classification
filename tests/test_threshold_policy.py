import unittest

from src.threshold_policy import metrics_at_capacity, metrics_at_threshold, top_k_predictions


class ThresholdPolicyTests(unittest.TestCase):
    def test_metrics_and_business_scaling(self):
        result = metrics_at_threshold(
            [0, 0, 1, 1],
            [0.1, 0.8, 0.7, 0.2],
            0.5,
            {
                "monthly_applications": 4,
                "max_monthly_reviews": 2,
                "review_cost": 10,
                "lgd": 100,
                "review_effectiveness": 0.5,
                "performing_contribution": 20,
                "abandonment_rate": 0.1,
            },
        )
        self.assertEqual(result["tn"], 1)
        self.assertEqual(result["fp"], 1)
        self.assertEqual(result["fn"], 1)
        self.assertEqual(result["tp"], 1)
        self.assertAlmostEqual(result["accuracy"], 0.5)
        self.assertAlmostEqual(result["precision"], 0.5)
        self.assertAlmostEqual(result["recall"], 0.5)
        self.assertAlmostEqual(result["f1"], 0.5)
        self.assertAlmostEqual(result["monthly_reviews"], 2.0)
        self.assertAlmostEqual(result["expected_defaults_prevented"], 0.5)

    def test_capacity_policy_selects_exact_ranked_queue(self):
        result = metrics_at_capacity(
            [0, 0, 1, 1, 1],
            [0.10, 0.20, 0.30, 0.40, 0.90],
            fraction=0.40,
            assumptions={
                "monthly_applications": 5,
                "max_monthly_reviews": 2,
                "review_cost": 0,
                "lgd": 100,
                "review_effectiveness": 1.0,
                "performing_contribution": 0,
                "abandonment_rate": 0,
            },
        )
        self.assertEqual(result["selection_rule"], "top_k")
        self.assertEqual(result["selected_count"], 2)
        self.assertEqual((result["tn"], result["fp"], result["fn"], result["tp"]), (2, 0, 1, 2))
        self.assertAlmostEqual(result["review_rate"], 0.4)

    def test_capacity_rejects_invalid_fraction(self):
        with self.assertRaises(ValueError):
            top_k_predictions([0.1, 0.2], fraction=0)


if __name__ == "__main__":
    unittest.main()
