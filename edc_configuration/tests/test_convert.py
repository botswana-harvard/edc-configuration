from datetime import date, datetime

from django.test.testcases import TestCase
from django.utils import timezone

from edc_configuration.convert import Convert


class TestConvert(TestCase):

    def test_string_to_string(self):
        value = '11:00'
        string_value = Convert(value).to_string()
        self.assertEqual(string_value, '11:00')

    def test_string_back_to_string(self):
        string_value = '11:00'
        value = Convert(string_value).to_value()
        self.assertIsInstance(value, (str, basestring))

    def test_boolean_to_string1(self):
        value = True
        string_value = Convert(value).to_string()
        self.assertEqual(string_value, 'True')

    def test_boolean_to_string2(self):
        value = False
        string_value = Convert(value).to_string()
        self.assertEqual(string_value, 'False')

    def test_string_back_to_boolean(self):
        string_value = 'True'
        value = Convert(string_value).to_value()
        self.assertIsInstance(value, int)

    def test_string_back_to_boolean2(self):
        string_value = 'False'
        value = Convert(string_value).to_value()
        self.assertIsInstance(value, int)

    def test_string_back_to_none(self):
        string_value = 'None'
        value = Convert(string_value).to_value()
        self.assertIsNone(value)

    def test_datetime_to_string1(self):
        value = timezone.now()
        string_value = Convert(value).to_string()
        self.assertEqual(string_value, value.strftime('%Y-%m-%d %H:%M'))

    def test_string_to_datetime(self):
        string_value = '2016-01-05 09:35'
        value = Convert(string_value).to_value()
        self.assertEqual(value, datetime(2016, 1, 5, 9, 35))

    def test_datetime_to_string2(self):
        value = datetime.today()
        string_value = Convert(value).to_string()
        self.assertEqual(string_value, value.strftime('%Y-%m-%d %H:%M'))

    def test_date_to_string(self):
        value = date.today()
        string_value = Convert(value).to_string()
        self.assertEqual(string_value, value.strftime('%Y-%m-%d'))

    def test_string_to_date(self):
        string_value = '2016-01-05'
        value = Convert(string_value).to_value()
        self.assertEqual(value, date(2016, 1, 5))
