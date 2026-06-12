# Répartition des Tâches : Résidence & Décès (Exclusion du Mobile)

Conformément à vos consignes, l'équipe Flutter (Mobile) est totalement exclue de cette feuille de route et gérera ses formulaires en autonomie. Nos 5 développeurs se concentrent exclusivement sur le Backend, l'API et le Frontend Web de la mairie.

## 🧑‍💻 DEV 2A - PAPE ALIOUNE SENE
**Rôle** : Lead Backend PDF & Logique d'Expiration (Indépendant & Volume Max)
- **Tâche 1** : Créer le layout `_draw_residence_layout` dans `pdf_generator.py` en y intégrant la condition stricte : **"Validité : 3 mois à compter de la date de délivrance"**.
- **Tâche 2** : Créer les layouts `_draw_death_layout` (Certificat de décès) et `_draw_burial_permit` (Permis d'inhumation).
- **Tâche 3** : Modifier le routeur principal pour orienter la génération PDF en fonction du type d'acte.

## 🧑‍💻 DEV 1C - MAIMOUNA SALL
**Rôle** : Lead Frontend React (Sécurité Documentaire)
- **Tâche 4** : Développer le "Viewer Documentaire Avancé" dans l'interface Web des agents (`DossierDetail.jsx`). Son code React doit scanner les pièces jointes envoyées par le mobile. 
- **Tâche 5** : Implémenter des cases à cocher obligatoires. S'il s'agit d'un décès à domicile, l'agent ne pourra pas cliquer sur "Approuver" tant qu'il n'aura pas visualisé et coché "Conforme" pour les 4 pièces (Constat médecin, CNI défunt, CNI déclarant, CNI des 2 témoins).

## 🧑‍💻 DEV 1D - IBRAHIMA KHALILOU DIALLO
**Rôle** : Lead Backend API & Validations Métier (Garde-fou)
- **Tâche 6** : Implémenter le blocage de délai. Ajouter une règle dans les serializers Django pour refuser la création d'un certificat de décès si la `date_deces` remonte à plus d'un an (Renvoi d'une erreur 400 à l'équipe Mobile).
- **Tâche 7** : Créer le validateur de pièces jointes Backend. S'assurer que le payload JSON contient bien toutes les images/PDFs requis avant de sauvegarder en base.

## 🧑‍💻 DEV 1B - PATHE FALL
**Rôle** : Frontend React (Guichet Physique / Saisie sur place)
- **Tâche 8** : Étant donné qu'on ne touche pas au mobile, Pathé s'occupera d'intégrer le formulaire de création de "Certificat de Résidence" dans le module **Guichet Rapide** (Interface Web Interne). Cela permet à un agent d'enregistrer une demande pour un citoyen venu physiquement à la mairie, avec un uploader Web pour l'attestation du délégué de quartier.

## 🧑‍💻 DEV 2B - EL HADJI MASSOGUI DIOP
**Rôle** : Tests Backend QA & Configuration Django Admin
- **Tâche 9** : Écrire les Tests Unitaires complets pour valider les règles métiers d'Ibrahima (Tâches 6 et 7) et s'assurer que le générateur PDF de Pape (Tâches 1 et 2) ne plante jamais.
- **Tâche 10** : Mettre à jour l'interface native d'administration (Django Admin) pour qu'un Super Admin puisse consulter et forcer le statut de ces nouveaux types de certificats en cas de litige.
