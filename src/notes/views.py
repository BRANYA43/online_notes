from django import views
from django.http import JsonResponse
from django.urls import reverse
from django.views import generic

from accounts import forms as acc_forms
from notes import forms, models, filters, services


def filter_notes(request):
    filter_ = filters.NoteFilters(request.GET)
    data = services.serialize_filter_qs(filter_.qs)
    return JsonResponse(data=data, status=200, safe=False)


def retrieve_category(request, id):
    try:
        category = models.Category.objects.get(id=id)
        data = {
            'urls': {
                'update': reverse('update_category', args=[category.id]),
            },
            'category': {
                'id': category.id,
                'title': category.title,
                'color': category.color,
            },
        }
        return JsonResponse(data=data, status=200)

    except models.Category.DoesNotExist:
        return JsonResponse(data={'errors': [f'Not found such category by id={id}']}, status=404)


def delete_category(request, id):
    try:
        category = models.Category.objects.get(id=id)
        category.delete()
        return JsonResponse(data={'category': {'id': int(id)}}, status=200)
    except models.Category.DoesNotExist:
        return JsonResponse(data={'errors': [f'Not found such category by id={id}']}, status=404)


def update_category(request, id):
    try:
        category = models.Category.objects.get(id=id)
        form = forms.CategoryUpdateForm(instance=category, data=request.POST)
        if form.is_valid():
            category = form.save()
            data = {
                'category': {
                    'id': category.id,
                    'title': category.title,
                    'color': category.color,
                }
            }
            return JsonResponse(data=data, status=200)
        else:
            return JsonResponse(data={'errors': form.errors}, status=400)

    except models.Category.DoesNotExist:
        return JsonResponse(data={'errors': [f'Not found such category by id={id}']}, status=404)


def create_category(request):
    form = forms.CategoryCreateForm(request, request.POST)
    if form.is_valid():
        category = form.save()
        data = {
            'urls': {
                'update': reverse('update_category', args=[category.id]),
                'retrieve': reverse('retrieve_category', args=[category.id]),
                'delete': reverse('delete_category', args=[category.id]),
            },
            'category': {
                'id': category.id,
                'title': category.title,
                'color': category.color,
            },
        }
        return JsonResponse(data=data, status=201)
    else:
        return JsonResponse(data={'errors': form.errors}, status=400)


def delete_note(request, id):
    try:
        note = models.Note.objects.get(id=id)
        note.delete()
        return JsonResponse(data={'note': {'id': int(id)}}, status=200)
    except models.Note.DoesNotExist:
        return JsonResponse(data={'errors': [f'Not found such note by id={id}']}, status=404)


def archive_note(request, id):
    try:
        note = models.Note.objects.get(id=id)
        note.is_archived = not note.is_archived
        note.save()
        return JsonResponse(data={'note': {'id': int(id)}}, status=200)
    except models.Note.DoesNotExist:
        return JsonResponse(data={'errors': [f'Not found such note by id={id}']}, status=404)


def retrieve_note(request, id):
    try:
        note = models.Note.objects.get(id=id)
        data = {
            'urls': {
                'update': reverse('update_note', args=[note.id]),
            },
            'note': {
                'title': note.title,
                'text': note.text,
            },
        }
        if note.category:
            data['category'] = {
                'id': note.category.id,
                'title': note.category.title,
                'color': note.category.color,
            }
        return JsonResponse(data=data, status=200)

    except models.Note.DoesNotExist:
        return JsonResponse(data={'errors': [f'Not found such note by id={id}']}, status=404)


def update_note(request, id):
    note = models.Note.objects.get(id=id)
    form = forms.NoteUpdateForm(instance=note, data=request.POST)
    if form.is_valid():
        note = form.save()
        data = {
            'note': {
                'id': note.id,
                'title': note.title,
            }
        }
        if note.category:
            data['category'] = {
                'title': note.category.title,
                'color': note.category.color,
            }
        return JsonResponse(data=data, status=200)

    else:
        return JsonResponse(data={'errors': form.errors}, status=400)


def create_new_note(request):
    form = forms.NoteCreateForm(request=request, data=request.POST)
    if form.is_valid():
        note = form.save()
        data = {
            'urls': {
                'update': reverse('update_note', args=[note.id]),
                'retrieve': reverse('retrieve_note', args=[note.id]),
                'archive': reverse('archive_note', args=[note.id]),
                'delete': reverse('delete_note', args=[note.id]),
            },
            'note': {
                'id': note.id,
                'title': note.title,
                'date': note.created.strftime('%d.%m.%Y'),
            },
        }
        if note.category:
            data['category'] = {
                'title': note.category.title,
                'color': note.category.color,
            }

        return JsonResponse(data=data, status=201)
    else:
        return JsonResponse(data={'errors': form.errors}, status=400)


class BaseView(views.View, generic.base.ContextMixin, generic.base.TemplateResponseMixin):
    template_name = 'base.html'
    form_classes = {
        'login_form': acc_forms.UserLoginForm,
        'register_form': acc_forms.UserRegisterForm,
    }
    extra_form_classes: dict = {}

    def get_extra_forms(self) -> dict:
        return {form_key: form(self.request) for form_key, form in self.extra_form_classes.items()}

    def get_context_data(self, **kwargs):
        if self.extra_form_classes:
            kwargs.update(self.get_extra_forms())
        for form_key, form in self.form_classes.items():
            kwargs[form_key] = form(self.request)
        kwargs['worktable'] = self.get_worktable()
        return super().get_context_data(**kwargs)

    def get_worktable(self) -> models.Worktable:
        if self.request.user.is_authenticated:
            return self.request.user.worktable
        else:
            if self.request.session.session_key is None:
                self.request.session.save()
            return models.Worktable.objects.get_or_create(session_key=self.request.session.session_key)[0]

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())


class NotesView(BaseView):
    template_name = 'home.html'
    extra_form_classes = {
        'note_create_form': forms.NoteCreateForm,
    }


class CategoryView(BaseView):
    template_name = 'categories.html'
    extra_form_classes = {
        'category_create_form': forms.CategoryCreateForm,
    }
