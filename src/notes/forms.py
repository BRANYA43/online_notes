from django import forms

from notes import models


class BaseCreateForm(forms.ModelForm):
    """BaseCreateForm for models that has more to one relation with a worktable"""

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.request.user.is_authenticated:
            obj.worktable = self.request.user.worktable
        else:
            obj.worktable = models.Worktable.objects.get(session_key=self.request.session.session_key)
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


class NoteUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Note
        fields = ('category', 'title', 'text')
