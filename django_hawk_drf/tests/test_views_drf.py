from django.test import TestCase
from django_hawk.tests.test_views import DjangoHawkViewTests


class DjangoRestFrameworkTests(DjangoHawkViewTests, TestCase):
    view_name = "test_view_set"
