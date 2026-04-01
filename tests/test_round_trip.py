import unittest
from MRTD import decode_mrz, encode_mrz, validate_mrz


class TestRoundTrip(unittest.TestCase):
    """Tests verifying encode->decode and encode->validate round-trips."""

    # Test that encoding fields then decoding the result recovers the original data
    def test_encode_then_decode_uto(self):
        fields = {
            "document_type": "P",
            "issuing_country": "UTO",
            "surname": "ERIKSSON",
            "given_names": "ANNA MARIA",
            "passport_number": "L898902C3",
            "country_code": "UTO",
            "birth_date": "740812",
            "sex": "F",
            "expiration_date": "120415",
            "personal_number": "ZE184226B",
        }
        line1, line2 = encode_mrz(fields)
        decoded = decode_mrz(line1, line2)
        self.assertEqual(decoded["document_type"], "P")
        self.assertEqual(decoded["surname"], "ERIKSSON")
        self.assertEqual(decoded["given_names"], "ANNA MARIA")
        self.assertEqual(decoded["passport_number"], "L898902C3")
        self.assertEqual(decoded["birth_date"], "740812")
        self.assertEqual(decoded["sex"], "F")
        self.assertEqual(decoded["expiration_date"], "120415")
        self.assertEqual(decoded["personal_number"], "ZE184226B")

    # Test encode->decode round-trip for a USA passport
    def test_encode_then_decode_usa(self):
        fields = {
            "document_type": "P",
            "issuing_country": "USA",
            "surname": "SMITH",
            "given_names": "JOHN",
            "passport_number": "AB1234567",
            "country_code": "USA",
            "birth_date": "950101",
            "sex": "M",
            "expiration_date": "250101",
        }
        line1, line2 = encode_mrz(fields)
        decoded = decode_mrz(line1, line2)
        self.assertEqual(decoded["surname"], "SMITH")
        self.assertEqual(decoded["given_names"], "JOHN")
        self.assertEqual(decoded["country_code"], "USA")

    # Test that encoding then validating always passes all check digits
    def test_encode_then_validate_passes(self):
        fields = {
            "document_type": "P",
            "issuing_country": "GBR",
            "surname": "JONES",
            "given_names": "ELIZABETH MARY",
            "passport_number": "CD9876543",
            "country_code": "GBR",
            "birth_date": "880515",
            "sex": "F",
            "expiration_date": "280515",
            "personal_number": "12345",
        }
        line1, line2 = encode_mrz(fields)
        result = validate_mrz(line1, line2)
        self.assertTrue(result["overall_result"])
        for field in result["fields"]:
            self.assertTrue(field["match"], f"{field['field_name']} failed")

    # Test decode->encode round-trip reproduces the original MRZ lines
    def test_decode_then_encode_roundtrip(self):
        orig_line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
        orig_line2 = "L898902C34UTO7408122F1204153ZE184226B<<<<<70"
        decoded = decode_mrz(orig_line1, orig_line2)
        # Build fields dict from decoded output
        fields = {
            "document_type": decoded["document_type"],
            "issuing_country": decoded["issuing_country"],
            "surname": decoded["surname"],
            "given_names": decoded["given_names"],
            "passport_number": decoded["passport_number"],
            "country_code": decoded["country_code"],
            "birth_date": decoded["birth_date"],
            "sex": decoded["sex"],
            "expiration_date": decoded["expiration_date"],
            "personal_number": decoded["personal_number"],
        }
        line1, line2 = encode_mrz(fields)
        self.assertEqual(line1, orig_line1)
        self.assertEqual(line2, orig_line2)
