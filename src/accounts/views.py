from django.contrib.auth import login, logout
from django.http import JsonResponse

from accounts import forms


def logout_user(request, *args, **kwargs):
    logout(request)
    return JsonResponse(data={}, status=200)


def login_user(request, *args, **kwargs):
    data = request.POST
    form = forms.UserLoginForm(request, data)
    if form.is_valid():
        login(request, form.cache_user)
        return JsonResponse(data={}, status=200)
    else:
        data = {'errors': form.errors}
        return JsonResponse(data=data, status=400)


def register_user(request, *args, **kwargs):
    data = request.POST
    form = forms.UserRegisterForm(data)
    if form.is_valid():
        form.save()
        return JsonResponse(data={}, status=201)
    else:
        data = {'errors': form.errors}
        return JsonResponse(data=data, status=400)
