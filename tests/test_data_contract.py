import unittest
from pathlib import Path

from src.data_contract import EXPECTED_COLUMNS, load_raw_data, make_xy


class DataContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.frame = load_raw_data(cls.root / "data" / "raw" / "SouthGermanCredit.asc")

    def test_schema_is_exact(self):
        self.assertEqual(list(self.frame.columns), EXPECTED_COLUMNS)

    def test_target_has_expected_positive_mapping(self):
        _, y = make_xy(self.frame)
        self.assertEqual(int(y.sum()), 300)
        self.assertEqual(set(y.unique()), {0, 1})

    def test_no_missing_or_duplicates(self):
        self.assertEqual(int(self.frame.isna().sum().sum()), 0)
        self.assertEqual(int(self.frame.duplicated().sum()), 0)


if __name__ == "__main__":
    unittest.main()
