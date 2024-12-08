import unittest
from app.bpm_parser import parse_bpm, parseBPM


class TestBPMParser(unittest.TestCase):

    def test_parse_bpm_valid(self):
        self.assertEqual(parse_bpm("150"), 150)

    def test_parse_bpm_negative(self):
        with self.assertRaises(ValueError):
            parse_bpm("-150")

    def test_parse_bpm_invalid(self):
        with self.assertRaises(ValueError):
            parse_bpm("abc")

    def test_parseBPM_single_value(self):
        result = parseBPM("150")
        self.assertEqual(result["lower"], "150")
        self.assertEqual(result["higher"], "150")

    def test_parseBPM_range(self):
        result = parseBPM("120 - 150")
        self.assertEqual(result["lower"], "120")
        self.assertEqual(result["higher"], "150")

    def test_parseBPM_with_additional_text(self):
        result = parseBPM("150 beats")
        self.assertEqual(result["higher"], "150")

    def test_parseBPM_invalid_format(self):
        with self.assertRaises(ValueError):
            parseBPM("invalid format")


if __name__ == '__main__':
    unittest.main()
