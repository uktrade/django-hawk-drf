from django.http import HttpResponse
from rest_framework.viewsets import ViewSet

from django_hawk_drf.authentication import HawkAuthentication


class ExampleViewSet(ViewSet):
    authentication_classes = (HawkAuthentication,)
    permission_classes = ()

    def list(self, request):
        return HttpResponse("This is a DRF view")
