import unittest
from MRTD import validate_mrz


class TestValidateMRZ(unittest.TestCase):
    """Tests for MRZ check digit validation."""

    # Valid Fletcher-16 MRZ lines (produced by encode_mrz)
    UTO_LINE1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
    UTO_LINE2 = "L898902C34UTO7408122F1204153ZE184226B<<<<<70"
    USA_LINE1 = "P<USASMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
    USA_LINE2 = "AB12345671USA9501014M2501015<<<<<<<<<<<<<<04"

    # Test that a valid UTO passport passes all check digit validations
    def test_validate_all_correct_uto(self):
        result = validate_mrz(self.UTO_LINE1, self.UTO_LINE2)
        self.assertTrue(result["overall_result"])
        for field in result["fields"]:
            self.assertTrue(field["match"], f"{field['field_name']} failed")

    # Test that a valid USA passport passes all check digit validations
    def test_validate_all_correct_usa(self):
        result = validate_mrz(self.USA_LINE1, self.USA_LINE2)
        self.assertTrue(result["overall_result"])
        for field in result["fields"]:
            self.assertTrue(field["match"], f"{field['field_name']} failed")

    # Test that tampering the passport check digit (pos 10) is detected
    def test_validate_wrong_passport_check(self):
        tampered = self.UTO_LINE2[:9] + "0" + self.UTO_LINE2[10:]
        result = validate_mrz(self.UTO_LINE1, tampered)
        self.assertFalse(result["overall_result"])
        passport_field = result["fields"][0]
        self.assertEqual(passport_field["field_name"], "passport_number")
        self.assertFalse(passport_field["match"])

    # Test that tampering the birth date check digit (pos 20) is detected
    def test_validate_wrong_birth_check(self):
        tampered = self.UTO_LINE2[:19] + "0" + self.UTO_LINE2[20:]
        result = validate_mrz(self.UTO_LINE1, tampered)
        self.assertFalse(result["overall_result"])
        birth_field = result["fields"][1]
        self.assertEqual(birth_field["field_name"], "birth_date")
        self.assertFalse(birth_field["match"])

    # Test that tampering the expiration check digit (pos 28) is detected
    def test_validate_wrong_expiration_check(self):
        tampered = self.UTO_LINE2[:27] + "0" + self.UTO_LINE2[28:]
        result = validate_mrz(self.UTO_LINE1, tampered)
        self.assertFalse(result["overall_result"])
        exp_field = result["fields"][2]
        self.assertEqual(exp_field["field_name"], "expiration_date")
        self.assertFalse(exp_field["match"])

    # Test that tampering the personal number check digit (pos 43) is detected
    def test_validate_wrong_personal_check(self):
        tampered = self.UTO_LINE2[:42] + "0" + self.UTO_LINE2[43:]
        result = validate_mrz(self.UTO_LINE1, tampered)
        self.assertFalse(result["overall_result"])
        pn_field = result["fields"][3]
        self.assertEqual(pn_field["field_name"], "personal_number")
        self.assertFalse(pn_field["match"])

    # Test that tampering the overall check digit (pos 44) is detected
    def test_validate_wrong_overall_check(self):
        tampered = self.UTO_LINE2[:43] + "9"
        result = validate_mrz(self.UTO_LINE1, tampered)
        self.assertFalse(result["overall_result"])
        overall_field = result["fields"][4]
        self.assertEqual(overall_field["field_name"], "overall")
        self.assertFalse(overall_field["match"])

    # Test that tampering all check digits reports all mismatches (no short-circuit)
    def test_validate_all_wrong(self):
        tampered = (
            self.UTO_LINE2[:9] + "0"
            + self.UTO_LINE2[10:19] + "0"
            + self.UTO_LINE2[20:27] + "0"
            + self.UTO_LINE2[28:42] + "0" + "9"
        )
        self.assertEqual(len(tampered), 44)
        result = validate_mrz(self.UTO_LINE1, tampered)
        self.assertFalse(result["overall_result"])
        # All 5 fields should be reported as mismatches
        mismatches = [f for f in result["fields"] if not f["match"]]
        self.assertEqual(len(mismatches), 5)

    # Test that the original ICAO reference passport fails Fletcher-16 validation
    def test_validate_icao_reference_fails(self):
        icao_line2 = "L898902C36UTO7408122F1204159ZE184226B<<<<<<1"
        result = validate_mrz(self.UTO_LINE1, icao_line2)
        self.assertFalse(result["overall_result"])

    # Test that the response dict has the correct structure with all 5 field entries
    def test_validate_returns_all_fields(self):
        result = validate_mrz(self.UTO_LINE1, self.UTO_LINE2)
        self.assertIn("overall_result", result)
        self.assertIn("fields", result)
        self.assertEqual(len(result["fields"]), 5)
        expected_names = [
            "passport_number", "birth_date", "expiration_date",
            "personal_number", "overall",
        ]
        actual_names = [f["field_name"] for f in result["fields"]]
        self.assertEqual(actual_names, expected_names)
        # Each field entry must have expected, actual, and match keys
        for field in result["fields"]:
            self.assertIn("expected", field)
            self.assertIn("actual", field)
            self.assertIn("match", field)
