from django.test import TestCase

from django.urls import reverse
from django.views import generic

from accounts import forms as acc_forms
from notes import views, forms


class HomeViewTest(TestCase):
    def setUp(self) -> None:
        self.url = reverse('home')
        self.view_class = views.HomeView

    def test_view_inherit_expected_mixins(self):
        mixins = [generic.base.TemplateResponseMixin, generic.base.ContextMixin]
        for mixin in mixins:
            self.assertTrue(issubclass(self.view_class, mixin))

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'home.html')

    def test_view_context_has_expected_forms(self):
        expected_forms = {
            'login_form': acc_forms.UserLoginForm,
            'register_form': acc_forms.UserRegisterForm,
            'category_create_form': forms.CategoryCreateForm,
            'note_create_form': forms.NoteCreateForm,
        }
        response = self.client.get(self.url)

        for key, cls in expected_forms.items():
            if (form := response.context.get(key)) is not None:
                self.assertIsInstance(form, cls)
            else:
                self.fail(f'Missed <{cls.__name__}>.')
