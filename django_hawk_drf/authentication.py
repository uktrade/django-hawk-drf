import logging
from typing import Tuple

from django.contrib.auth.models import AnonymousUser
from django_hawk.utils import DjangoHawkAuthenticationFailed, authenticate_request
from mohawk import Receiver
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

logger = logging.getLogger(__name__)


class HawkAuthenticatedUser(AnonymousUser):
    """This is a user that is authenticated using Hawk"""

    @property
    def is_authenticated(self):
        return True


class HawkAuthentication(BaseAuthentication):
    def authenticate_header(self, request) -> str:
        """
        This is returned as the WWW-Authenticate header when
        AuthenticationFailed is raised. DRF also requires this
        to send a 401 (as opposed to 403)
        """

        return "Hawk"

    def authenticate(self, request: Request) -> Tuple[HawkAuthenticatedUser, Receiver]:
        """
        Authenticates a request using Hawk signature
        If either of these suggest we cannot authenticate, AuthenticationFailed
        is raised, as required in the DRF authentication flow
        """
        try:
            hawk_receiver = authenticate_request(request=request)
        except DjangoHawkAuthenticationFailed as e:
            raise AuthenticationFailed(str(e))

        return (HawkAuthenticatedUser(), hawk_receiver)
