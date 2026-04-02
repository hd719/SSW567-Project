"""
Comprehensive unit tests for MRTD (Machine-Readable Travel Document) system.
Entry point — actual tests live in tests/ package.
"""

import unittest
from unittest.mock import patch
import MRTD


class TestCalculateCheckDigit(unittest.TestCase):

    def test_numeric_only(self):
        self.assertIsInstance(MRTD.calculate_check_digit("123456"), int)

    def test_alpha_only(self):
        self.assertIsInstance(MRTD.calculate_check_digit("ABCDEF"), int)

    def test_mixed_input(self):
        self.assertIn(MRTD.calculate_check_digit("A1B2C3"), range(10))

    def test_empty_input(self):
        self.assertEqual(MRTD.calculate_check_digit(""), 0)

    def test_invalid_char(self):
        with self.assertRaises(ValueError):
            MRTD.calculate_check_digit("abc!")


class TestScanMRZ(unittest.TestCase):

    @patch("MRTD.scan_mrz")
    def test_scan_returns_data(self, mock_scan):
        mock_scan.return_value = ("LINE1", "LINE2")
        self.assertEqual(MRTD.scan_mrz(), ("LINE1", "LINE2"))

    @patch("MRTD.scan_mrz")
    def test_scan_empty(self, mock_scan):
        mock_scan.return_value = ("", "")
        self.assertEqual(MRTD.scan_mrz(), ("", ""))


class TestQueryDatabase(unittest.TestCase):

    @patch("MRTD.query_database")
    def test_db_none(self, mock_db):
        mock_db.return_value = None
        self.assertIsNone(MRTD.query_database())

    @patch("MRTD.query_database")
    def test_db_found(self, mock_db):
        mock_db.return_value = {"status": "found"}
        self.assertEqual(MRTD.query_database(), {"status": "found"})


class TestDecodeMRZ(unittest.TestCase):
    def valid_lines(self):
        line1 = "P<UTOERIKSSON<<<<<<<<<<<<<<<<<<<<<<<<<<<".ljust(44, "<")
        line2 = "L898902C36UTO7408122F1204159<<<<<<<<<<<<<<".ljust(44, "<")
        return line1, line2

    def test_valid_decode(self):
        line1, line2 = self.valid_lines()
        result = MRTD.decode_mrz(line1, line2)
        self.assertEqual(result["document_type"], "P")

    def test_invalid_length(self):
        with self.assertRaises(ValueError):
            MRTD.decode_mrz("SHORT", "SHORT")

    def test_invalid_characters(self):
        bad = ("A" * 44)
        bad = bad[:-1] + "!"
        with self.assertRaises(ValueError):
            MRTD.decode_mrz(bad, bad)

    def test_missing_given_names(self):
        line1 = "P<UTOERIKSSON<<<<<<<<<<<<<<<<<<<<<<<<<<<".ljust(44, "<")
        line2 = "L898902C36UTO7408122F1204159<<<<<<<<<<<<<<".ljust(44, "<")
        result = MRTD.decode_mrz(line1, line2)
        self.assertIn("surname", result)


class TestEncodeMRZ(unittest.TestCase):
    def valid_fields(self):
        return {
            "document_type": "P",
            "issuing_country": "UTO",
            "surname": "ERIKSSON",
            "given_names": "ANNA MARIA",
            "passport_number": "123456789",
            "country_code": "UTO",
            "birth_date": "740812",
            "sex": "F",
            "expiration_date": "120415",
            "personal_number": "1234567890"}
    
    def test_valid_encode(self):
        line1, line2 = MRTD.encode_mrz(self.valid_fields())
        self.assertEqual(len(line1), 44)
        self.assertEqual(len(line2), 44)

    def test_missing_field(self):
        fields = self.valid_fields()
        del fields["surname"]
        with self.assertRaises(ValueError):
            MRTD.encode_mrz(fields)

    def test_invalid_passport_length(self):
        fields = self.valid_fields()
        fields["passport_number"] = "123"
        with self.assertRaises(ValueError):
            MRTD.encode_mrz(fields)


class TestValidateMRZ(unittest.TestCase):
    def test_all_valid(self):
        line1 = "P<UTOERIKSSON<<<<<<<<<<<<<<<<<<<<<<<<<<<".ljust(44, "<")
        line2 = "L898902C36UTO7408122F1204159<<<<<<<<<<<<<<0"
        line2 = line2.ljust(44, "<")
        result = MRTD.validate_mrz(line1, line2)
        self.assertIn("overall_result", result)

    def test_invalid_case(self):
        line1 = "P<UTOERIKSSON<<<<<<<<<<<<<<<<<<<<<<<<<<<".ljust(44, "<")
        line2 = "L898902C36UTO7408122F1204159<<<<<<<<<<<<<<9"
        line2 = line2.ljust(44, "<")
        result = MRTD.validate_mrz(line1, line2)
        self.assertFalse(result["overall_result"])



class TestRoundTrip(unittest.TestCase):
    def test_encode_decode_cycle(self):
        fields = {
            "document_type": "P",
            "issuing_country": "UTO",
            "surname": "SMITH",
            "given_names": "JOHN",
            "passport_number": "123456789",
            "country_code": "UTO",
            "birth_date": "900101",
            "sex": "M",
            "expiration_date": "300101",
            "personal_number": "111111111"}
        
        line1, line2 = MRTD.encode_mrz(fields)
        decoded = MRTD.decode_mrz(line1, line2)

        self.assertEqual(decoded["passport_number"], "123456789")
        self.assertEqual(decoded["country_code"], "UTO")


if __name__ == "__main__":
    unittest.main()