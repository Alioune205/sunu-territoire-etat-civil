# 📋 Plan de Répartition des Tâches - Équipe DEV 1 (Backend Core)

Ce document détaille la suite du développement de l'architecture backend pour **SUNU CIVIL**. En tant que **DEV 1A (Lansana)**, vous avez mis en place la structure principale, la base de données, la sécurité JWT, les communes et la structure globale.

Voici les missions spécifiques et détaillées des trois autres membres de l'équipe **DEV 1 (DEV 1B, DEV 1C, DEV 1D)** pour finaliser le cœur du backend.

---

## 🧑‍💻 DEV 1B : Gestion des Dossiers, Workflow et Machine à États

**Mission principale** : Implémenter la logique métier stricte du cycle de vie des dossiers d'état civil, les transitions de statut sécurisées, l'affectation automatique et les commentaires.

### 📁 Fichiers cibles
* [backend/apps/dossiers/models.py](file:///c:/Users/HP/Documents/Institut_Supérieur_d'enseignement_professionnelle_%28ISEP%29/Hackathon/backend/apps/dossiers/models.py)
* [backend/apps/dossiers/views.py](file:///c:/Users/HP/Documents/Institut_Supérieur_d'enseignement_professionnelle_%28ISEP%29/Hackathon/backend/apps/dossiers/views.py)
* [backend/apps/dossiers/serializers.py](file:///c:/Users/HP/Documents/Institut_Supérieur_d'enseignement_professionnelle_%28ISEP%29/Hackathon/backend/apps/dossiers/serializers.py)

### ⚙️ Spécifications techniques à coder
1. **Machine à États (Workflow)** :
   Empêcher les changements de statut non autorisés en redéfinissant la méthode `save()` du modèle `Dossier` :
   * `draft` ne peut passer qu'à `submitted`.
   * `submitted` ne peut passer qu'à `in_review` (lorsqu'un agent de réception ou de vérification l'assigne).
   * `in_review` ne peut passer qu'à `approved` ou `rejected`.
   * `approved` ne peut passer qu'à `completed` (lorsque l'acte numérique est généré et signé par l'officier civil).

2. **Génération de Référence Unique** :
   * Créer une méthode utilitaire pour générer un numéro de référence unique et infalsifiable à la création du dossier (ex: `DOS-2026-XXXXX` avec `XXXXX` un numéro séquentiel ou hash).

3. **Endpoints d'Action Spécifiques** :
   Implémenter les routes d'actions dans `views.py` :
   * `/api/dossiers/{id}/submit/` : Seul le citoyen propriétaire du dossier peut le soumettre.
   * `/api/dossiers/{id}/assign/` : Permet d'assigner le dossier à un agent spécifique de la même commune.
   * `/api/dossiers/{id}/review/` : L'agent de vérification déclare qu'il examine le dossier.
   * `/api/dossiers/{id}/approve/` : Seul le `civil_admin` (Officier d'état civil) de la commune peut approuver.
   * `/api/dossiers/{id}/reject/` : L'officier rejette le dossier avec l'obligation de remplir le champ `rejection_reason`.

---

## 🧑‍💻 DEV 1C : Stockage Sécurisé et Gestion des Documents

**Mission principale** : Garantir la sécurité, l'intégrité et le stockage des pièces jointes téléversées par les citoyens (photos, scans de CNI, justificatifs).

### 📁 Fichiers cibles
* [backend/apps/documents/models.py](file:///c:/Users/HP/Documents/Institut_Supérieur_d'enseignement_professionnelle_%28ISEP%29/Hackathon/backend/apps/documents/models.py)
* [backend/apps/documents/views.py](file:///c:/Users/HP/Documents/Institut_Supérieur_d'enseignement_professionnelle_%28ISEP%29/Hackathon/backend/apps/documents/views.py)
* [backend/apps/shared/validators.py](file:///c:/Users/HP/Documents/Institut_Supérieur_d'enseignement_professionnelle_%28ISEP%29/Hackathon/backend/apps/shared/validators.py)

### ⚙️ Spécifications techniques à coder
1. **Validateur de Fichiers Strict** :
   * Écrire une fonction de validation de fichier dans `shared/validators.py` qui lit les premiers octets du fichier (magic bytes) pour vérifier que le type réel (ex. PDF, PNG, JPEG) correspond bien à l'extension, pour éviter que des scripts malveillants masqués en images soient stockés.
   * Valider la taille maximale du fichier (limite stricte à 10 Mo).

2. **Téléchargement et Accès Sécurisés** :
   * Sécuriser la vue de téléchargement des documents (`views.py`). Un fichier joint à un dossier ne doit être téléchargeable **que par** le citoyen qui l'a soumis ou par un agent de la commune associée à ce dossier.
   * Configurer des URLs signées temporaires si le stockage est migré vers le cloud.

3. **Préparation Cloud Storage** :
   * Ajouter la configuration optionnelle pour utiliser `django-storages` avec Amazon S3 ou un serveur MinIO local pour la phase de production.

---

## 🧑‍💻 DEV 1D : Audit Logs Avancés, Signaux et API Dashboard Core

**Mission principale** : Garantir la traçabilité complète de l'application à des fins de sécurité et fournir des données agrégées pour l'application statistique (Dashboard).

### 📁 Fichiers cibles
* [backend/apps/audit_logs/middleware.py](file:///c:/Users/HP/Documents/Institut_Supérieur_d'enseignement_professionnelle_%28ISEP%29/Hackathon/backend/apps/audit_logs/middleware.py)
* [backend/apps/users/signals.py](file:///c:/Users/HP/Documents/Institut_Supérieur_d'enseignement_professionnelle_%28ISEP%29/Hackathon/backend/apps/users/signals.py)
* [backend/apps/dashboard/views.py](file:///c:/Users/HP/Documents/Institut_Supérieur_d'enseignement_professionnelle_%28ISEP%29/Hackathon/backend/apps/dashboard/views.py)

### ⚙️ Spécifications techniques à coder
1. **Middleware d'Audit Log** :
   * Terminer l'implémentation du middleware pour capturer automatiquement l'adresse IP et l'identité de l'utilisateur effectuant des requêtes d'écriture (`POST`, `PUT`, `PATCH`, `DELETE`) et insérer une ligne dans la table `AuditLog`.

2. **Signaux Django pour Événements Sensibles** :
   * Connecter des signaux `post_save` et `post_delete` sur les modèles sensibles (`User`, `Commune`, `Dossier`) pour consigner automatiquement les actions dans l'audit (ex: Modification de rôle d'un utilisateur, désactivation d'une commune, etc.).

3. **Endpoints de Données Statistiques** :
   * Développer les endpoints dans `apps/dashboard/views.py` pour fournir au dashboard d'administration React :
     * Le nombre total de dossiers traités et en cours par commune.
     * Le temps moyen de traitement d'un dossier (différence entre `submitted_at` et `completed_at`).
     * Le nombre de demandes d'actes par type (naissance, mariage, décès, etc.).
