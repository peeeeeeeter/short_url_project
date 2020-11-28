from django.test import TestCase

from ..configs import B62_ALPHABET
from ..utils import b62_decode, b62_encode


class B62EncoddeTest(TestCase):

    def test_number_is_string(self):
        number = '12345'
        with self.assertRaises(ValueError):
            b62_encode(number)

    def test_number_is_float(self):
        number = 123.0
        with self.assertRaises(ValueError):
            b62_encode(number)

    def test_not_positive_integer(self):
        number = 0
        with self.assertRaises(ValueError):
            b62_encode(number)

    def test_number_exceed_max_val(self):
        number = int(8 * 1e9 + 1)
        with self.assertRaises(ValueError):
            b62_encode(number)

    def test_success(self):
        number = 123456789
        result = b62_encode(number)

        self.assertEqual(result, '8m0Kx')


class B62DecodeTest(TestCase):

    def test_string_is_not_str(self):
        string = 12345
        with self.assertRaises(ValueError):
            b62_decode(string)

    def test_string_is_empty(self):
        string = ''
        with self.assertRaises(ValueError):
            b62_decode(string)

    def test_string_exceed_max_length(self):
        string = 'abcdefg'
        with self.assertRaises(ValueError):
            b62_decode(string)

    def test_success(self):
        string = '8m0Kx'
        decode = b62_decode(string)
        self.assertEqual(decode, 123456789)