from datetime import date, datetime

from django.test.testcases import TestCase
from django.utils import timezone

from edc_configuration.convert import Convert, localize
from decimal import Decimal
from edc_configuration.models import GlobalConfiguration
from django.test.utils import override_settings


class TestConvert(TestCase):

    def test_string_to_string(self):
        value = '11:00'
        string_value = Convert(value).to_string()
        self.assertEqual(string_value, '11:00')

    def test_string_back_to_time(self):
        string_value = '11:00'
        value = Convert(string_value).to_value()
        self.assertIsInstance(value, (str))

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

    @override_settings(USE_TZ=False)
    def test_datetime_to_string_notz(self):
        value = timezone.now()
        expected_value = value.strftime('%Y-%m-%dT%H:%M')
        string_value = Convert(value).to_string()
        self.assertTrue(string_value.startswith(expected_value))

    @override_settings(USE_TZ=True)
    def test_datetime_to_string_tz(self):
        value = timezone.now()
        expected_value = value.strftime('%Y-%m-%dT%H:%M')
        string_value = Convert(value).to_string()
        self.assertTrue(string_value.startswith(expected_value))

    @override_settings(USE_TZ=False)
    def test_string_to_datetime_notz(self):
        string_value = '2016-01-05 09:35'
        value = Convert(string_value).to_value()
        self.assertEqual(value, localize(datetime(2016, 1, 5, 9, 35)))

    @override_settings(USE_TZ=True)
    def test_string_with_tz_to_datetime_tz(self):
        string_value = '2016-01-05T09:35'
        value = Convert(string_value).to_value()
        self.assertEqual(value, localize(datetime(2016, 1, 5, 9, 35)))

    @override_settings(USE_TZ=True)
    def test_string_to_datetime_tz(self):
        string_value = '2016-01-05 09:35'
        value = Convert(string_value).to_value()
        self.assertEqual(value, localize(datetime(2016, 1, 5, 9, 35)))

    @override_settings(USE_TZ=False)
    def test_date_to_string_notz(self):
        value = date.today()
        string_value = Convert(value).to_string()
        self.assertEqual(string_value, value.strftime('%Y-%m-%d'))

    @override_settings(USE_TZ=True)
    def test_date_to_string_tz(self):
        value = date.today()
        string_value = Convert(value).to_string()
        self.assertEqual(string_value, value.strftime('%Y-%m-%d'))

    @override_settings(USE_TZ=False)
    def test_string_to_date_notz(self):
        string_value = '2016-01-05'
        value = Convert(string_value).to_value()
        self.assertEqual(value.date(), date(2016, 1, 5))

    @override_settings(USE_TZ=True)
    def test_string_to_date_tz(self):
        string_value = '2016-01-05'
        value = Convert(string_value).to_value()
        self.assertEqual(value.date(), date(2016, 1, 5))

    def test_string_to_int(self):
        string_value = '12345'
        value = Convert(string_value).to_value()
        self.assertEqual(value, 12345)
        self.assertFalse(isinstance(value, Decimal))

    def test_string_to_decimal(self):
        string_value = '12345.0'
        value = Convert(string_value).to_value()
        self.assertEqual(value, 12345.0)
        self.assertTrue(isinstance(value, Decimal))

    def test_string_to_string_int(self):
        string_value = '12345'
        value = Convert(string_value, convert=False).to_value()
        self.assertEqual(value, '12345')

    def test_string_global(self):
        string_value = '12345'
        convert = Convert(string_value, convert=False)
        self.assertFalse(convert.convert)
        value = convert.to_string()
        self.assertEqual(value, '12345')
        self.assertFalse(convert.convert)
        GlobalConfiguration.objects.create(
            category='test', attribute='attr', value=string_value, convert=convert.convert)
        self.assertEqual(GlobalConfiguration.objects.get_attr_value('attr'), string_value)
