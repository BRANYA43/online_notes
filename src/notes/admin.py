from django.contrib import admin

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
    fields = ('title', 'text')
    extra = 1
    show_change_link = True


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


@admin.register(models.Worktable)
class WorktableAdmin(admin.ModelAdmin):
    list_display = ('user',)
    fieldsets = (('Information', {'fields': ('user',)}),)
    inlines = (CategoryInline,)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('user',)
        return self.readonly_fields
