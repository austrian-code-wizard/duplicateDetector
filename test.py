from duplicateDetector.pairholder import PairHolder
from duplicateDetector import ROOT_PATH
import pandas as pd
import unittest

excel_sheet_path = "/Users/Moritz/Downloads/Customers.xlsx"
holder = PairHolder.get_holder_from_excel(excel_sheet_path)

class TestSum(unittest.TestCase):
	def test_run_levenshtein(self):
		result = holder.run_levenshtein(4, ["NAME1", "STRAS"], "_KNA1.KUNNR", data_limit=3000, filter_field="LAND1",
										filter_value="DE")
		self.assertIsInstance(result, pd.DataFrame)
		self.assertGreater(len(result), 0)
		for name in ["left_side", "right_side", "similarity"]:
			self.assertIn(name, result.columns)
		self.assertEqual(len(result.columns), 3)

	def test_run_jaro_winkler(self):
		result = holder.run_jaro_winkler(0.4, ["NAME1", "STRAS"], "_KNA1.KUNNR", data_limit=1000, filter_field="LAND1",
										filter_value="DE")
		self.assertIsInstance(result, pd.DataFrame)
		self.assertGreater(len(result), 0)
		for name in ["left_side", "right_side", "similarity"]:
			self.assertIn(name, result.columns)
		self.assertEqual(len(result.columns), 3)

	def test_run_cosine(self):
		result = holder.run_cosine(0.7, ["NAME1", "STRAS"], "_KNA1.KUNNR", filter_field="LAND1",
										filter_value="DE")
		self.assertIsInstance(result, pd.DataFrame)
		self.assertGreater(len(result), 0)
		for name in ["left_side", "right_side", "similarity"]:
			self.assertIn(name, result.columns)
		self.assertEqual(len(result.columns), 3)