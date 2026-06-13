"""
Admin configuration for Commune.
"""
from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Commune


@admin.register(Commune)
class CommuneAdmin(ModelAdmin):
    list_display = ('name', 'region', 'department', 'code', 'is_active')
    list_filter = ('region', 'department', 'is_active')
    search_fields = ('name', 'region', 'department', 'code')
    ordering = ('name',)
