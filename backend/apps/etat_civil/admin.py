from django.contrib import admin
from apps.etat_civil.models_attribution import ProfilAgent, AttributionDossier, JournalAttribution

@admin.register(ProfilAgent)
class ProfilAgentAdmin(admin.ModelAdmin):
    list_display = ('user', 'statut_actuel', 'charge_actuelle', 'capacite_maximale', 'score_performance_global', 'est_disponible')
    list_filter = ('statut_actuel',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('dossiers_traites_historique',)
    
    def est_disponible(self, obj):
        return obj.est_disponible
    est_disponible.boolean = True
    est_disponible.short_description = 'Disponible ?'

@admin.register(AttributionDossier)
class AttributionDossierAdmin(admin.ModelAdmin):
    list_display = ('dossier', 'agent', 'statut', 'niveau_priorite', 'date_limite_sla', 'est_en_retard')
    list_filter = ('statut', 'niveau_priorite')
    search_fields = ('dossier__reference', 'agent__user__email')
    readonly_fields = ('score_matching_initial', 'date_traitement_effectif')

    def est_en_retard(self, obj):
        return obj.est_en_retard
    est_en_retard.boolean = True
    est_en_retard.short_description = 'En retard ?'

@admin.register(JournalAttribution)
class JournalAttributionAdmin(admin.ModelAdmin):
    list_display = ('dossier', 'action', 'agent_concerne', 'created_at')
    list_filter = ('action',)
    search_fields = ('dossier__reference', 'motif_detaille')
    readonly_fields = ('dossier', 'agent_concerne', 'action', 'motif_detaille', 'anciennes_valeurs', 'created_at')
    
    def has_add_permission(self, request):
        return False  # Journal en lecture seule (Audit Trail)
