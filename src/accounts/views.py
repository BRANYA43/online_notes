from django.http import JsonResponse

from accounts import forms


def register_user(request, *args, **kwargs):
    data = request.POST
    form = forms.UserRegisterForm(data)
    if form.is_valid():
        form.save()
        return JsonResponse(data={}, status=201)
    else:
        data = {'errors': form.errors}
        return JsonResponse(data=data, status=400)
