from django import forms

from notes import models, filters

NoteFiltersForm = filters.NoteFilter().get_form_class()


class BaseCreateForm(forms.ModelForm):
    """BaseCreateForm for models that has more to one relation with a worktable"""

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.worktable = self.get_worktable()
        obj.save()
        return obj

    def get_worktable(self):
        if self.request.user.is_authenticated:
            return self.request.user.worktable
        else:
            session = self.request.session
            if session.session_key is None:
                session.save()
            return models.Worktable.objects.get_or_create(session_key=session.session_key)[0]


class CategoryCreateForm(BaseCreateForm):
    class Meta:
        model = models.Category
        fields = ('title', 'color')


class CategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Category
        fields = ('title', 'color')


class NoteCreateForm(BaseCreateForm):
    class Meta:
        model = models.Note
        fields = ('category', 'title', 'text')


class NoteUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Note
        fields = ('category', 'title', 'text')
