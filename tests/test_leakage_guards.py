import unittest

from src.data_contract import TARGET_COLUMN, make_xy, load_raw_data
from src.models import make_candidate_models


class LeakageGuardTests(unittest.TestCase):
    def test_target_is_not_in_predictors(self):
        frame = load_raw_data("data/raw/SouthGermanCredit.asc")
        X, y = make_xy(frame)
        self.assertNotIn(TARGET_COLUMN, X.columns)
        self.assertEqual(y.name, "bad_default_risk")

    def test_each_candidate_fits_preprocessing_inside_pipeline(self):
        for model in make_candidate_models().values():
            self.assertEqual(list(model.named_steps), ["preprocess", "model"])
            self.assertEqual(model.named_steps["preprocess"].remainder, "drop")


if __name__ == "__main__":
    unittest.main()
