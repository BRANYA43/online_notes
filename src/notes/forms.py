from django import forms

from notes import models, services
from notes.services import get_worktable


class BaseCreateForm(forms.ModelForm):
    """BaseCreateForm for models that has more to one relation with a worktable"""

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.worktable = services.get_worktable(self.request)
        obj.save()
        return obj


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

    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['category'].queryset = get_worktable(self.request).get_all_categories()


class NoteUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Note
        fields = ('category', 'title', 'text')
