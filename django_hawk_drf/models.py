from django.contrib.auth.models import AnonymousUser


class HawkAuthenticatedUser(AnonymousUser):
    """
    This is a user that is authenticated using Hawk
    """

    @property
    def is_authenticated(self):
        return True
