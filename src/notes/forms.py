from django import forms

from notes import models


class BaseCreateForm(forms.ModelForm):
    """BaseCreateForm for models that has more to one relation with a worktable"""

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def save(self, commit=True):
        note = super().save(commit=False)
        if self.request.user.is_authenticated:
            note.worktable = self.request.user.worktable
        else:
            note.worktable = self.request.session.worktable
        note.save()
        return note


class CategoryCreateForm(BaseCreateForm):
    class Meta:
        model = models.Category
        fields = ('title', 'color')


class CategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Category
        fields = ('title', 'color')
