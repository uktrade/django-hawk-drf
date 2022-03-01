from django.test import TestCase
from django_hawk_drf.tests.test_views import DjangoHawkViewTests


class DjangoRestFrameworkTests(DjangoHawkViewTests, TestCase):
    view_name = "test_view_set"
