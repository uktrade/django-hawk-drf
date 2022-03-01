import datetime

import mohawk
from django.test import override_settings
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


def hawk_auth_sender(
    url: str,
    key_id: str = "some-id",
    secret_key: str = "some-secret",
    method: str = "GET",
    content: str = "",
    content_type: str = "",
):
    credentials = {
        "id": key_id,
        "key": secret_key,
        "algorithm": "sha256",
    }
    return mohawk.Sender(
        credentials,
        url,
        method,
        content=content,
        content_type=content_type,
    )


class DjangoHawkViewTests:
    view_name: str = ""

    def get_path(self) -> str:
        return reverse(self.view_name)

    def get_url(self) -> str:
        return "http://testserver" + self.get_path()

    @override_settings(
        DJANGO_HAWK={
            "HAWK_INCOMING_ACCESS_KEY": "some-id",
            "HAWK_INCOMING_SECRET_KEY": "some-secret",
        }
    )
    def test_empty_object_returned_with_authentication(self):
        """
        If the Authorization and X-Forwarded-For headers are correct, then
        the correct, and authentic, data is returned
        """

        url = self.get_url()
        sender = hawk_auth_sender(url=url)
        response = APIClient().get(
            url,
            content_type="",
            HTTP_AUTHORIZATION=sender.request_header,
            HTTP_X_FORWARDED_FOR="1.2.3.4, 123.123.123.123",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @override_settings(
        DJANGO_HAWK={
            "HAWK_INCOMING_ACCESS_KEY": "wrong-id",
            "HAWK_INCOMING_SECRET_KEY": "some-secret",
        }
    )
    def test_bad_credentials_mean_401_returned(self):
        """
        If the wrong credentials are used,
        then a 401 is returned
        """

        url = self.get_url()
        sender = hawk_auth_sender(url=url)
        response = APIClient().get(
            url,
            content_type="",
            HTTP_AUTHORIZATION=sender.request_header,
            HTTP_X_FORWARDED_FOR="1.2.3.4, 123.123.123.123",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.json(),
            {
                "detail": "Incorrect authentication credentials.",
            },
        )

    @override_settings(
        DJANGO_HAWK={
            "HAWK_INCOMING_ACCESS_KEY": "some-id",
            "HAWK_INCOMING_SECRET_KEY": "some-secret",
        }
    )
    def test_if_61_seconds_in_past_401_returned(self):
        """
        If the Authorization header is generated 61 seconds in the past, then a
        401 is returned
        """

        url = self.get_url()
        past = datetime.datetime.now() - datetime.timedelta(seconds=61)
        with freeze_time(past):
            auth = hawk_auth_sender(url).request_header
        response = APIClient().get(
            url,
            content_type="",
            HTTP_AUTHORIZATION=auth,
            HTTP_X_FORWARDED_FOR="1.2.3.4, 123.123.123.123",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.json(),
            {
                "detail": "Incorrect authentication credentials.",
            },
        )
