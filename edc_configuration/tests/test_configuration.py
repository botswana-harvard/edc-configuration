from django.test.testcases import TestCase

from .test_app_configuration import TestAppConfiguration


class TestConfiguration(TestCase):

    def test_prepare(self):
        TestAppConfiguration(use_site_lab_profiles=False).prepare()
