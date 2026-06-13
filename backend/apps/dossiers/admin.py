"""
Admin configuration for Dossier and DossierComment.
"""
import json
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Dossier, DossierComment


class DossierCommentInline(admin.TabularInline):
    model = DossierComment
    extra = 0
    readonly_fields = ('author', 'content', 'created_at')


@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = ('reference', 'type', 'status', 'citizen', 'commune', 'assigned_agent', 'created_at')
    list_filter = ('type', 'status', 'commune')
    search_fields = ('reference', 'citizen__email', 'citizen__first_name', 'citizen__last_name', 'third_party_cni')
    readonly_fields = ('reference', 'created_at', 'updated_at', 'submitted_at', 'reviewed_at', 'completed_at', 'formatted_metadata')
    inlines = [DossierCommentInline]
    ordering = ('-created_at',)
    
    actions = ['mark_as_in_review']

    fieldsets = (
        ('Informations Générales', {
            'fields': ('reference', 'type', 'status', 'commune', 'assigned_agent')
        }),
        ('Demandeur & Tierce Personne', {
            'fields': ('citizen', 'is_for_third_party', 'third_party_cni', 'third_party_relation')
        }),
        ('Détails & Métadonnées (Registres)', {
            'fields': ('metadata', 'formatted_metadata', 'notes', 'rejection_reason'),
            'description': 'Les métadonnées contiennent les informations spécifiques (Mariage, Décès, Résidence, etc.)',
        }),
        ('Dates', {
            'fields': ('submitted_at', 'reviewed_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def formatted_metadata(self, obj):
        """Affiche les métadonnées JSON de manière esthétique."""
        if not obj.metadata:
            return "Aucune métadonnée"
        try:
            formatted_json = json.dumps(obj.metadata, indent=4, ensure_ascii=False)
            return format_html('<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px;">{}</pre>', formatted_json)
        except Exception:
            return str(obj.metadata)
    formatted_metadata.short_description = 'Métadonnées (Vue structurée)'

    @admin.action(description='Marquer les dossiers sélectionnés "En vérification"')
    def mark_as_in_review(self, request, queryset):
        updated = queryset.filter(status=Dossier.Status.SUBMITTED).update(
            status=Dossier.Status.IN_REVIEW, 
            reviewed_at=timezone.now(),
            assigned_agent=request.user
        )
        self.message_user(request, f"{updated} dossiers ont été marqués comme 'En vérification' et vous ont été assignés.")


@admin.register(DossierComment)
class DossierCommentAdmin(admin.ModelAdmin):
    list_display = ('dossier', 'author', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('dossier__reference', 'author__email', 'content')
