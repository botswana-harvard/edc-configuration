from datetime import datetime

from django.test.testcases import TestCase

from edc_configuration.convert import localize
from edc_configuration.models import GlobalConfiguration
from edc_configuration.defaults import default_global_configuration

from .test_app_configuration import TestAppConfiguration


class TestConfiguration(TestCase):

    def test_reads_global_config(self):
        """Assert a value specified in the local app overwrites the default."""
        self.assertEqual(default_global_configuration.get('appointment').get('allowed_iso_weekdays'), '1234567')
        self.assertEqual(default_global_configuration.get('appointment').get('default_appt_type'), 'default')
        self.assertEqual(default_global_configuration.get('appointment').get('use_same_weekday'), True)
        TestAppConfiguration(use_site_lab_profiles=False).prepare()
        self.assertEqual(GlobalConfiguration.objects.get_attr_value('allowed_iso_weekdays'), '2345')
        self.assertEqual(GlobalConfiguration.objects.get_attr_value('default_appt_type'), 'clinic')
        self.assertEqual(GlobalConfiguration.objects.get_attr_value('use_same_weekday'), False)

    def test_prepare(self):
        TestAppConfiguration(use_site_lab_profiles=False).prepare()
        self.assertEqual(GlobalConfiguration.objects.get_attr_value('allowed_iso_weekdays'), '2345')
        self.assertEqual(GlobalConfiguration.objects.get_attr_value('default_appt_type'), 'clinic')
        self.assertEqual(GlobalConfiguration.objects.get_attr_value('use_same_weekday'), False)
        self.assertEqual(GlobalConfiguration.objects.get_attr_value('appointments_days_forward'), 8)
        self.assertEqual(GlobalConfiguration.objects.get_attr_value('allowed_iso_weekdays'), '2345')
        self.assertEqual(
            GlobalConfiguration.objects.get_attr_value('start_datetime'),
            localize(datetime(2013, 10, 18, 10, 30, 0)))
        self.assertEqual(
            GlobalConfiguration.objects.get_attr_value('end_datetime'),
            localize(datetime(2016, 10, 17, 16, 30, 0)))
