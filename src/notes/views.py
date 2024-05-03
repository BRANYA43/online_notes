from django import views
from django.views import generic


from accounts import forms as acc_forms
from notes import forms, models


class HomeView(views.View, generic.base.ContextMixin, generic.base.TemplateResponseMixin):
    template_name = 'home.html'
    form_classes = {
        'login_form': acc_forms.UserLoginForm,
        'register_form': acc_forms.UserRegisterForm,
        'category_create_form': forms.CategoryCreateForm,
        'note_create_form': forms.NoteCreateForm,
    }

    def get_context_data(self, **kwargs):
        kwargs['login_form'] = self.form_classes['login_form'](self.request)
        kwargs['register_form'] = self.form_classes['register_form']()
        kwargs['category_create_form'] = self.form_classes['category_create_form'](self.request)
        kwargs['note_create_form'] = self.form_classes['note_create_form'](self.request)
        kwargs['worktable'] = self.get_worktable()
        return super().get_context_data(**kwargs)

    def get_worktable(self):
        if self.request.user.is_authenticated:
            return self.request.user.worktable
        else:
            return models.Worktable.objects.get_or_create(session_key=self.request.session.session_key)[0]

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())
