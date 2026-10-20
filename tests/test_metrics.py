import unittest

from src.evaluation import binary_metrics


class MetricTests(unittest.TestCase):
    def test_binary_metrics_confusion_counts(self):
        result = binary_metrics([0, 0, 1, 1], [0.1, 0.8, 0.7, 0.2], threshold=0.5)
        self.assertEqual(result["tn"], 1)
        self.assertEqual(result["fp"], 1)
        self.assertEqual(result["fn"], 1)
        self.assertEqual(result["tp"], 1)
        self.assertAlmostEqual(result["precision"], 0.5)
        self.assertAlmostEqual(result["recall"], 0.5)
        self.assertAlmostEqual(result["f1"], 0.5)


if __name__ == "__main__":
    unittest.main()
