"""
Admin configuration for Dossier and DossierComment.
"""
from django.contrib import admin
from .models import Dossier, DossierComment


class DossierCommentInline(admin.TabularInline):
    model = DossierComment
    extra = 0
    readonly_fields = ('author', 'content', 'created_at')


@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = ('reference', 'type', 'status', 'citizen', 'commune', 'assigned_agent', 'created_at')
    list_filter = ('type', 'status', 'commune')
    search_fields = ('reference', 'citizen__email', 'citizen__first_name', 'citizen__last_name')
    readonly_fields = ('reference', 'created_at', 'updated_at')
    inlines = [DossierCommentInline]
    ordering = ('-created_at',)


@admin.register(DossierComment)
class DossierCommentAdmin(admin.ModelAdmin):
    list_display = ('dossier', 'author', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('dossier__reference', 'author__email', 'content')
