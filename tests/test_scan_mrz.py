import unittest
from unittest.mock import patch
from MRTD import scan_mrz


class TestScanMRZ(unittest.TestCase):
    """Tests for the scan_mrz stub and its mocked behavior."""

    # Test that the stub returns a tuple
    def test_scan_mrz_returns_tuple(self):
        result = scan_mrz()
        self.assertIsInstance(result, tuple)

    # Test that the stub returns two strings
    def test_scan_mrz_returns_two_strings(self):
        result = scan_mrz()
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], str)
        self.assertIsInstance(result[1], str)

    # Test mocking scan_mrz to return valid MRZ lines (UTO passport)
    @patch("MRTD.scan_mrz")
    def test_scan_mrz_mock_valid_data(self, mock_scan):
        mock_scan.return_value = (
            "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<",
            "L898902C34UTO7408122F1204153ZE184226B<<<<<70",
        )
        line1, line2 = mock_scan()
        self.assertEqual(len(line1), 44)
        self.assertEqual(len(line2), 44)
