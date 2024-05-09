import inspect

from django import views
from django.http import JsonResponse
from django.views import generic

from accounts import forms as acc_forms
from notes import forms, models, filters, services


def filter_notes(request):
    filter_ = filters.NoteFilter(request=request, data=request.GET)
    data = services.serialize_filter_qs(filter_.qs)
    return JsonResponse(data=data, status=200, safe=False)


def retrieve_category(request, id):
    try:
        category = models.Category.objects.get(id=id)
        data = services.serialize_model(
            category,
            ('id', 'title', 'color'),
            ('update',),
        )
        return JsonResponse(data=data, status=200)

    except models.Category.DoesNotExist:
        return JsonResponse(data={'errors': [f'Not found such category by id={id}']}, status=404)


def delete_category(request, id):
    try:
        category = models.Category.objects.get(id=id)
        data = services.serialize_model(category, ('id',))
        category.delete()
        return JsonResponse(data=data, status=200)
    except models.Category.DoesNotExist:
        return JsonResponse(data={'errors': [f'Not found such category by id={id}']}, status=404)


def update_category(request, id):
    try:
        category = models.Category.objects.get(id=id)
        form = forms.CategoryUpdateForm(instance=category, data=request.POST)
        if form.is_valid():
            category = form.save()
            data = services.serialize_model(
                category,
                ('id', 'title', 'color'),
            )
            return JsonResponse(data=data, status=200)
        else:
            return JsonResponse(data={'errors': form.errors}, status=400)

    except models.Category.DoesNotExist:
        return JsonResponse(data={'errors': [f'Not found such category by id={id}']}, status=404)


def create_category(request):
    form = forms.CategoryCreateForm(request, request.POST)
    if form.is_valid():
        category = form.save()
        data = services.serialize_model(
            category,
            ('id', 'title', 'color'),
            ('update', 'retrieve', 'delete'),
        )
        return JsonResponse(data=data, status=201)
    else:
        return JsonResponse(data={'errors': form.errors}, status=400)


def delete_note(request, id):
    try:
        note = models.Note.objects.get(id=id)
        data = services.serialize_model(note, ('id',))
        note.delete()
        return JsonResponse(data=data, status=200)
    except models.Note.DoesNotExist:
        return JsonResponse(data={'errors': [f'Not found such note by id={id}']}, status=404)


def archive_note(request, id):
    try:
        note = models.Note.objects.get(id=id)
        note.is_archived = not note.is_archived
        note.save()
        data = services.serialize_model(note, ('id',))
        return JsonResponse(data=data, status=200)
    except models.Note.DoesNotExist:
        return JsonResponse(data={'errors': [f'Not found such note by id={id}']}, status=404)


def retrieve_note(request, id):
    try:
        note = models.Note.objects.get(id=id)
        data = services.serialize_model(
            note,
            ('title', 'text'),
            ('update',),
        )
        if note.category:
            data.update(services.serialize_model(note.category, ('id', 'title', 'color')))
        return JsonResponse(data=data, status=200)

    except models.Note.DoesNotExist:
        return JsonResponse(data={'errors': [f'Not found such note by id={id}']}, status=404)


def update_note(request, id):
    note = models.Note.objects.get(id=id)
    form = forms.NoteUpdateForm(instance=note, data=request.POST)
    if form.is_valid():
        note = form.save()
        data = services.serialize_model(
            note,
            ('id', 'title'),
        )
        if note.category:
            data.update(services.serialize_model(note.category, ('title', 'color')))
        return JsonResponse(data=data, status=200)

    else:
        return JsonResponse(data={'errors': form.errors}, status=400)


def create_new_note(request):
    form = forms.NoteCreateForm(request=request, data=request.POST)
    if form.is_valid():
        note = form.save()
        data = services.serialize_model(
            note,
            ('id', 'title'),
            ('update', 'retrieve', 'archive', 'delete'),
        )
        data['note']['created'] = note.created.strftime('%d.%m.%Y')

        if note.category:
            data.update(services.serialize_model(note.category, ('title', 'color')))
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

    def get_extra_forms(self, **kwargs) -> dict:
        kwargs = {}
        for form_key, form in self.extra_form_classes.items():
            if 'request' in inspect.signature(form.__init__).parameters:
                kwargs[form_key] = form(self.request)
            else:
                kwargs[form_key] = form()

        return kwargs

    def get_context_data(self, **kwargs):
        kwargs['worktable'] = self.get_worktable()
        if self.extra_form_classes:
            kwargs.update(self.get_extra_forms())

        for form_key, form in self.form_classes.items():
            if 'request' in inspect.signature(form.__init__).parameters:
                kwargs[form_key] = form(self.request)
            else:
                kwargs[form_key] = form()

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
    filter_class = filters.NoteFilter

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        filter_form_class = self.filter_class(self.request).get_form_class()
        kwargs['filter_form'] = filter_form_class()
        return kwargs


class CategoryView(BaseView):
    template_name = 'categories.html'
    extra_form_classes = {
        'category_create_form': forms.CategoryCreateForm,
    }
