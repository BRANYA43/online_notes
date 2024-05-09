from django.contrib import admin
from django.forms import HiddenInput

from notes import models


@admin.register(models.Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'worktable', 'category', 'is_archived', 'created')
    fieldsets = (
        ('Information', {'fields': ('worktable', 'category', 'title', 'text', 'is_archived')}),
        ('Dates', {'fields': ('created',)}),
    )
    readonly_fields = ('created',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('worktable',)
        return self.readonly_fields


class NoteInlineForCategory(admin.StackedInline):
    model = models.Note
    fields = ('worktable', 'title', 'text')
    extra = 1
    show_change_link = True

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            formset.form.base_fields['worktable'].widget = HiddenInput()
            formset.form.base_fields['worktable'].initial = obj.worktable
        return formset


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'color', 'worktable')
    fieldsets = (('Information', {'fields': ('worktable', 'title', 'color')}),)
    inlines = (NoteInlineForCategory,)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('worktable',)
        return self.readonly_fields


class CategoryInline(admin.TabularInline):
    model = models.Category
    fields = ('title', 'color')
    extra = 1
    show_change_link = True


class NoteInlineForWorktable(admin.StackedInline):
    model = models.Note
    fields = ('category', 'title', 'text')
    extra = 1
    show_change_link = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            worktable_id = request.resolver_match.kwargs['object_id']
            kwargs['queryset'] = models.Category.objects.filter(worktable_id=worktable_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(models.Worktable)
class WorktableAdmin(admin.ModelAdmin):
    fieldsets = (('Information', {'fields': ('user', 'session_key')}),)
    inlines = (CategoryInline, NoteInlineForWorktable)
