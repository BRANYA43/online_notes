from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest


def get_test_request(client, user=None) -> HttpRequest:
    request = HttpRequest()
    request.session = client.session
    request.user = user if user else AnonymousUser()
    return request
