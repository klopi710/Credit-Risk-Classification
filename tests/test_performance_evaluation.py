import unittest

import numpy as np

from src.performance_evaluation import capacity_metrics, top_k_predictions


class PerformanceEvaluationTests(unittest.TestCase):
    def test_top_k_selects_exact_capacity(self):
        selected = top_k_predictions(np.array([0.1, 0.2, 0.3, 0.4, 0.5]), fraction=0.2)
        self.assertEqual(int(selected.sum()), 1)
        self.assertEqual(int(selected[-1]), 1)

    def test_capacity_metrics_are_bounded(self):
        metrics = capacity_metrics([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.7], fraction=0.5)
        for key in ("accuracy_at_capacity", "precision_at_capacity", "recall_at_capacity", "f1_at_capacity"):
            self.assertGreaterEqual(metrics[key], 0.0)
            self.assertLessEqual(metrics[key], 1.0)


if __name__ == "__main__":
    unittest.main()
