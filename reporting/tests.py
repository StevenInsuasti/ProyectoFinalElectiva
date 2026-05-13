from django.test import TestCase


class ReportingSmokeTest(TestCase):
    def test_import_services(self):
        from reporting import services  # noqa: F401

        self.assertTrue(True)
