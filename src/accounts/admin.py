from django.contrib import admin
from django.contrib.auth import get_user_model


@admin.register(get_user_model())
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'last_login', 'created')
    fieldsets = (
        ('Information', {'fields': ('email',)}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
        ('Dates', {'fields': ('last_login', 'created')}),
    )
    readonly_fields = ('last_login', 'created')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('email',)
        return self.readonly_fields

    def get_fieldsets(self, request, obj=None):
        if obj:
            return self.fieldsets
        self.fieldsets[0][1]['fields'] = ('email', 'password')
        return self.fieldsets

    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)
