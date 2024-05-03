from django.contrib import admin

from notes import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'color', 'worktable')
    fieldsets = (('Information', {'fields': ('worktable', 'title', 'color')}),)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('worktable',)
        return self.readonly_fields


@admin.register(models.Worktable)
class WorktableAdmin(admin.ModelAdmin):
    list_display = ('user',)
    fieldsets = (('Information', {'fields': ('user',)}),)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('user',)
        return self.readonly_fields
